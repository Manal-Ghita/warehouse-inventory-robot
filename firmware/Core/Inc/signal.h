#ifndef SIGNAL_H
#define SIGNAL_H

void signal_init(void);
void signal_buzzer(int actif);
void signal_feu(int actif);
void signal_led(float niveau);   // 0 a 1

#endif
