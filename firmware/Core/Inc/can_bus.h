#ifndef CAN_BUS_H
#define CAN_BUS_H

#include <stdint.h>

void can_init(void);
int can_envoyer(uint16_t id, const uint8_t *data, uint8_t len);  // 1 si ok
int can_recu(uint16_t *id, uint8_t *data, uint8_t *len);         // 1 si nouvelle trame

#endif
