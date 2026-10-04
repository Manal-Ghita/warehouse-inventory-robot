#include "can_bus.h"
#include "main.h"
#include <string.h>

extern CAN_HandleTypeDef hcan1;

static volatile int nouvelle = 0;
static uint16_t rx_id;
static uint8_t rx_data[8];
static uint8_t rx_len;

void can_init(void)
{
  // filtre ouvert : on accepte toutes les trames
  CAN_FilterTypeDef f = {0};
  f.FilterBank = 0;
  f.FilterMode = CAN_FILTERMODE_IDMASK;
  f.FilterScale = CAN_FILTERSCALE_32BIT;
  f.FilterFIFOAssignment = CAN_RX_FIFO0;
  f.FilterActivation = ENABLE;
  HAL_CAN_ConfigFilter(&hcan1, &f);

  HAL_CAN_Start(&hcan1);
  HAL_CAN_ActivateNotification(&hcan1, CAN_IT_RX_FIFO0_MSG_PENDING);
}

int can_envoyer(uint16_t id, const uint8_t *data, uint8_t len)
{
  CAN_TxHeaderTypeDef h = {0};
  uint32_t boite;
  h.StdId = id;
  h.IDE = CAN_ID_STD;
  h.RTR = CAN_RTR_DATA;
  h.DLC = len;
  return HAL_CAN_AddTxMessage(&hcan1, &h, (uint8_t *)data, &boite) == HAL_OK;
}

int can_recu(uint16_t *id, uint8_t *data, uint8_t *len)
{
  if (!nouvelle) return 0;
  *id = rx_id;
  *len = rx_len;
  memcpy(data, rx_data, rx_len);
  nouvelle = 0;
  return 1;
}

// appelee par la hal a chaque trame recue
void HAL_CAN_RxFifo0MsgPendingCallback(CAN_HandleTypeDef *hcan)
{
  CAN_RxHeaderTypeDef h;
  HAL_CAN_GetRxMessage(hcan, CAN_RX_FIFO0, &h, rx_data);
  rx_id = h.StdId;
  rx_len = h.DLC;
  nouvelle = 1;
}
