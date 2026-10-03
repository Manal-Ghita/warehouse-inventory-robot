#ifndef BOARD_H
#define BOARD_H

#include "main.h"

#define TREUIL_DIR_PORT GPIOA
#define TREUIL_DIR_PIN GPIO_PIN_9
#define TREUIL_EN_PORT GPIOB
#define TREUIL_EN_PIN GPIO_PIN_5

#ifdef CIBLE_BANC_DE_TEST

#define TREUIL_EN_ACTIF GPIO_PIN_RESET
#define TREUIL_EN_INACTIF GPIO_PIN_SET
#else

#define TREUIL_EN_ACTIF GPIO_PIN_SET
#define TREUIL_EN_INACTIF GPIO_PIN_RESET
#endif

#endif
