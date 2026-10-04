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

#ifdef CIBLE_BANC_DE_TEST
// arret d'urgence simule par le bouton bleu b1, appuye = 0
#define AU_PORT   GPIOC
#define AU_PIN    GPIO_PIN_13
#define AU_ACTIF  GPIO_PIN_RESET
#else
// sortie de l'optocoupleur : arret d'urgence enfonce = 1
#define AU_PORT   GPIOC
#define AU_PIN    GPIO_PIN_8
#define AU_ACTIF  GPIO_PIN_SET
#endif

// pont r4 = 100k, r5 = 12k
#define BATT_RAPPORT        ((100.0f + 12.0f) / 12.0f)
// lifepo4 8s : 29,2 v pleine, ~20 v vide
#define BATT_SEUIL_BAS      24.0f
#define BATT_SEUIL_CRITIQUE 22.4f

#endif
