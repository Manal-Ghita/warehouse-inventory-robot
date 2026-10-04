#define FDC_HAUT_PORT  GPIOA
#define FDC_HAUT_PIN   GPIO_PIN_15

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

#ifdef CIBLE_BANC_DE_TEST
// fin de course bas simulee par sw2, appuye = 0
#define FDC_BAS_PORT   GPIOB
#define FDC_BAS_PIN    GPIO_PIN_11
#define FDC_ACTIF      GPIO_PIN_RESET
#else
// contact nf : butee atteinte = 1
#define FDC_BAS_PORT   GPIOB
#define FDC_BAS_PIN    GPIO_PIN_10
#define FDC_ACTIF      GPIO_PIN_SET
#endif

#ifdef CIBLE_BANC_DE_TEST
#define TREUIL_POS_MAX  20000   // arbitraire sur le banc
#else
#define TREUIL_POS_MAX  20000   // a recalculer avec le vrai treuil
#endif

#endif
