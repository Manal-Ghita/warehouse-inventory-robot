#include "plafond.h"
#include "main.h"

extern IWDG_HandleTypeDef hiwdg;
static volatile uint16_t distance_mm = 0;

#ifdef CIBLE_BANC_DE_TEST
// banc : vl53l1x en i2c, mesure lue a chaque interruption
#include "vl53l1_api.h"

extern I2C_HandleTypeDef hi2c1;
static VL53L1_Dev_t dev;
// diagnostic
volatile int plafond_err_init = 0;
volatile uint32_t plafond_nb_irq = 0;
volatile int plafond_statut = -1;

void plafond_init(void)
{
  // reset puis reveil du capteur
  HAL_GPIO_WritePin(GPIOH, GPIO_PIN_0, GPIO_PIN_RESET);
  HAL_Delay(10);
  HAL_GPIO_WritePin(GPIOH, GPIO_PIN_0, GPIO_PIN_SET);
  HAL_Delay(5);

  dev.I2cHandle = &hi2c1;
  dev.I2cDevAddr = 0x52;  // adresse d'usine
  dev.comms_type = 1;
  dev.comms_speed_khz = 400;

  plafond_err_init = VL53L1_WaitDeviceBooted(&dev);
  HAL_IWDG_Refresh(&hiwdg);
  if (plafond_err_init == 0) plafond_err_init = VL53L1_DataInit(&dev);
  HAL_IWDG_Refresh(&hiwdg);
  VL53L1_StaticInit(&dev);
  HAL_IWDG_Refresh(&hiwdg);
  VL53L1_SetDistanceMode(&dev, VL53L1_DISTANCEMODE_LONG);
  VL53L1_SetMeasurementTimingBudgetMicroSeconds(&dev, 40000);
  VL53L1_SetInterMeasurementPeriodMilliSeconds(&dev, 50);
  VL53L1_StartMeasurement(&dev);
}

// front descendant sur intof1 : une mesure est prete
void HAL_GPIO_EXTI_Callback(uint16_t pin)
{
  if (pin != GPIO_PIN_11) return;
  VL53L1_RangingMeasurementData_t m;
  VL53L1_GetRangingMeasurementData(&dev, &m);
  plafond_nb_irq++;
  plafond_statut = m.RangeStatus;
  if (m.RangeStatus == 0) distance_mm = m.RangeMilliMeter;
  VL53L1_ClearInterruptAndStartMeasurement(&dev);
}

#else
// robot : tfmini-s en uart, trames de 9 octets
extern UART_HandleTypeDef huart3;
static uint8_t octet;
static uint8_t trame[9];
static uint8_t idx = 0;

void plafond_init(void)
{
  HAL_UART_Receive_IT(&huart3, &octet, 1);
}

void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart)
{
  if (huart->Instance != USART3) return;

  // en-tete 0x59 0x59 puis 7 octets
  if (idx < 2 && octet != 0x59) {
    idx = 0;
  } else {
    trame[idx++] = octet;
    if (idx == 9) {
      uint8_t somme = 0;
      for (int i = 0; i < 8; i++) somme += trame[i];
      // distance envoyee en cm
      if (somme == trame[8]) distance_mm = (trame[2] | (trame[3] << 8)) * 10;
      idx = 0;
    }
  }
  HAL_UART_Receive_IT(&huart3, &octet, 1);
}
#endif

uint16_t plafond_distance_mm(void)
{
  return distance_mm;
}
