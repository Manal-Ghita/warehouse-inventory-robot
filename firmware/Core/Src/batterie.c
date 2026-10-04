#include "batterie.h"
#include "board.h"

extern ADC_HandleTypeDef hadc1;

void batterie_init(void)
{
  // calibration de l'adc, une fois au demarrage
  HAL_ADCEx_Calibration_Start(&hadc1, ADC_SINGLE_ENDED);
}

float batterie_tension(void)
{
  HAL_ADC_Start(&hadc1);
  HAL_ADC_PollForConversion(&hadc1, 10);
  uint32_t brut = HAL_ADC_GetValue(&hadc1);
  HAL_ADC_Stop(&hadc1);

  // 12 bits sur 3,3 v, puis on remonte le pont diviseur
  return brut * 3.3f / 4095.0f * BATT_RAPPORT;
}

batterie_etat_t batterie_etat(void)
{
  float v = batterie_tension();
  if (v < BATT_SEUIL_CRITIQUE) return BATT_CRITIQUE;
  if (v < BATT_SEUIL_BAS) return BATT_BAS;
  return BATT_OK;
}
