#include "treuil.h"
#include "board.h"

extern TIM_HandleTypeDef htim2;
extern TIM_HandleTypeDef htim5;

void treuil_stop(void){
	__HAL_TIM_SET_COMPARE(&htim2, TIM_CHANNEL_1, 0);
	HAL_GPIO_WritePin(TREUIL_EN_PORT, TREUIL_EN_PIN, TREUIL_EN_INACTIF);
}

void treuil_init(void){
  // moteur coupe avant tout
  treuil_stop();
  HAL_TIM_PWM_Start(&htim2, TIM_CHANNEL_1);
  HAL_TIM_Encoder_Start(&htim5, TIM_CHANNEL_ALL);
}

void treuil_commande(float consigne){
  // on borne entre -1 et 1
  if (consigne > 1.0f) consigne = 1.0f;
  if (consigne < -1.0f) consigne = -1.0f;

  GPIO_PinState sens = (consigne >= 0.0f) ? GPIO_PIN_SET : GPIO_PIN_RESET;
  HAL_GPIO_WritePin(TREUIL_DIR_PORT, TREUIL_DIR_PIN, sens);

  float abs_c = (consigne >= 0.0f) ? consigne : -consigne;
  uint32_t periode = __HAL_TIM_GET_AUTORELOAD(&htim2) + 1;
  __HAL_TIM_SET_COMPARE(&htim2, TIM_CHANNEL_1, (uint32_t)(abs_c * periode));

  HAL_GPIO_WritePin(TREUIL_EN_PORT, TREUIL_EN_PIN, TREUIL_EN_ACTIF);
}

int32_t treuil_position(void){
  return (int32_t)__HAL_TIM_GET_COUNTER(&htim5);
}

static int fdc_bas_atteint(void){
  return HAL_GPIO_ReadPin(FDC_BAS_PORT, FDC_BAS_PIN) == FDC_ACTIF;
}

int treuil_origine(uint32_t timeout_ms){
  uint32_t debut = HAL_GetTick();

  // descente lente jusqu'a la butee basse
  if (!fdc_bas_atteint()) treuil_commande(-0.25f);

  while (!fdc_bas_atteint()) {
    if (HAL_GetTick() - debut > timeout_ms) {
    	treuil_stop();
    	HAL_Delay(200);                    // on laisse le moteur s'immobiliser
    	__HAL_TIM_SET_COUNTER(&htim5, 0);  // position zero = mat en bas
    	return 1;
    }
  }

  treuil_stop();
  __HAL_TIM_SET_COUNTER(&htim5, 0);  // position zero = mat en bas
  return 1;
}
