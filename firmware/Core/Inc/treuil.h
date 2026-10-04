#ifndef TREUIL_H
#define TREUIL_H

#include <stdint.h>

void treuil_init(void);
void treuil_commande(float consigne);  // entre -1 et 1
void treuil_stop(void);
int32_t treuil_position(void);       // en impultions
int treuil_origine(uint32_t timeout_ms);  // 1 si ok, 0 si delai depasse

#endif
