#include "signal.h"
#include "main.h"

extern TIM_HandleTypeDef htim8;
extern TIM_HandleTypeDef htim3;

void signal_init(void)
{
  // tout eteint au demarrage
  HAL_TIM_PWM_Start(&htim8, TIM_CHANNEL_4);
  signal_buzzer(0);
  signal_feu(0);
  HAL_TIM_PWM_Start(&htim3, TIM_CHANNEL_4);
  signal_led(0.0f);
}

void signal_buzzer(int actif)
{
  uint32_t moitie = (__HAL_TIM_GET_AUTORELOAD(&htim8) + 1) / 2;
  __HAL_TIM_SET_COMPARE(&htim8, TIM_CHANNEL_4, actif ? moitie : 0);
}

void signal_feu(int actif)
{
  HAL_GPIO_WritePin(GPIOA, GPIO_PIN_7, actif ? GPIO_PIN_SET : GPIO_PIN_RESET);
}

void signal_led(float niveau)
{
  if (niveau < 0.0f) niveau = 0.0f;
  if (niveau > 1.0f) niveau = 1.0f;
  uint32_t periode = __HAL_TIM_GET_AUTORELOAD(&htim3) + 1;
  __HAL_TIM_SET_COMPARE(&htim3, TIM_CHANNEL_4, (uint32_t)(niveau * periode));
}
