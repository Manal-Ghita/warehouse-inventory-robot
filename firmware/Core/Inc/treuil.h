#ifndef TREUIL_H
#define TREUIL_H

#include <stdint.h>

typedef enum {
  TREUIL_OK = 0,
  TREUIL_BLOCAGE,
  TREUIL_FDC_HAUT,
  TREUIL_ARRET_URGENCE,
} treuil_erreur_t;

void treuil_init(void);
void treuil_commande(float consigne);     // entre -1 et 1
void treuil_stop(void);
int32_t treuil_position(void);            // en impulsions codeur
int treuil_origine(uint32_t timeout_ms);  // 1 si ok, 0 si delai depasse
int treuil_aller_a(int32_t cible);        // 1 si acceptee, 0 si refusee
void treuil_maj(void);                    // appelee a 100 hz
treuil_erreur_t treuil_erreur(void);
void treuil_acquitter(void);

#endif
