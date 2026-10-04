#ifndef BATTERIE_H
#define BATTERIE_H

typedef enum {
  BATT_OK = 0,
  BATT_BAS,
  BATT_CRITIQUE,
} batterie_etat_t;

void batterie_init(void);
float batterie_tension(void);   // en volts
batterie_etat_t batterie_etat(void);

#endif
