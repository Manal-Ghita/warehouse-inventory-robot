#include "treuil.h"
#include "board.h"

extern TIM_HandleTypeDef htim2;
extern TIM_HandleTypeDef htim5;

#define KP         0.0005f
#define KI         0.0f
#define KD         0.0f
#define DT         0.01f   // 100 hz
#define U_MAX      0.5f    // puissance max en asservissement
#define U_MIN      0.2f    // en dessous le moteur cale
#define TOLERANCE  20      // impulsions

static volatile int32_t cible = 0;
static volatile int actif = 0;
static float integrale = 0.0f;
static int32_t erreur_prec = 0;
static volatile treuil_erreur_t erreur = TREUIL_OK;
static int32_t pos_controle = 0;   // position au dernier controle de blocage
static uint32_t nb_appels = 0;

void treuil_stop(void){
  __HAL_TIM_SET_COMPARE(&htim2, TIM_CHANNEL_1, 0);
  HAL_GPIO_WritePin(TREUIL_EN_PORT, TREUIL_EN_PIN, TREUIL_EN_INACTIF);
}

void treuil_init(void){
  // moteur coupe avant tout
  treuil_stop();
  HAL_TIM_PWM_Start(&htim2, TIM_CHANNEL_1);
  HAL_TIM_Encoder_Start(&htim5, TIM_CHANNEL_ALL);
}

void treuil_commande(float consigne){
  // on borne entre -1 et 1
  if (consigne > 1.0f) consigne = 1.0f;
  if (consigne < -1.0f) consigne = -1.0f;

  GPIO_PinState sens = (consigne >= 0.0f) ? GPIO_PIN_SET : GPIO_PIN_RESET;
  HAL_GPIO_WritePin(TREUIL_DIR_PORT, TREUIL_DIR_PIN, sens);

  float abs_c = (consigne >= 0.0f) ? consigne : -consigne;
  uint32_t periode = __HAL_TIM_GET_AUTORELOAD(&htim2) + 1;
  __HAL_TIM_SET_COMPARE(&htim2, TIM_CHANNEL_1, (uint32_t)(abs_c * periode));

  HAL_GPIO_WritePin(TREUIL_EN_PORT, TREUIL_EN_PIN, TREUIL_EN_ACTIF);
}

int32_t treuil_position(void){
  return (int32_t)__HAL_TIM_GET_COUNTER(&htim5);
}

static int fdc_bas_atteint(void){
  return HAL_GPIO_ReadPin(FDC_BAS_PORT, FDC_BAS_PIN) == FDC_ACTIF;
}

static int fdc_haut_atteint(void){
  return HAL_GPIO_ReadPin(FDC_HAUT_PORT, FDC_HAUT_PIN) == FDC_ACTIF;
}

int treuil_origine(uint32_t timeout_ms)
{
  uint32_t debut = HAL_GetTick();

  // descente lente jusqu'a la butee basse
  if (!fdc_bas_atteint()) treuil_commande(-0.25f);

  while (!fdc_bas_atteint()) {
    if (HAL_GetTick() - debut > timeout_ms) {
      // butee jamais vue : on coupe et on signale
      treuil_stop();
      return 0;
    }
  }

  treuil_stop();
  HAL_Delay(200);                    // on laisse le moteur s'immobiliser
  __HAL_TIM_SET_COUNTER(&htim5, 0);  // position zero = mat en bas
  return 1;
}

int treuil_aller_a(int32_t c){
  // pas de mouvement tant qu'une erreur n'est pas acquittee
  if (erreur != TREUIL_OK) return 0;
  // cible hors course : refusee
  if (c < 0 || c > TREUIL_POS_MAX) return 0;

  cible = c;
  integrale = 0.0f;
  erreur_prec = c - treuil_position();
  pos_controle = treuil_position();
  nb_appels = 0;
  actif = 1;
  return 1;
}


static int au_actif(void){
  return HAL_GPIO_ReadPin(AU_PORT, AU_PIN) == AU_ACTIF;
}


void treuil_maj(void){
  // arret d'urgence : on coupe et on memorise, meme a l'arret
  if (au_actif()) {
    treuil_stop();
    actif = 0;
    erreur = TREUIL_ARRET_URGENCE;
    return;
  }
  if (!actif) return;

  int32_t pos = treuil_position();
  int32_t err = cible - pos;

  if (err > -TOLERANCE && err < TOLERANCE) {
    treuil_stop();
    integrale = 0.0f;
    erreur_prec = err;
    pos_controle = pos;
    nb_appels = 0;
    return;
  }

  integrale += err * DT;
  float deriv = (err - erreur_prec) / DT;
  erreur_prec = err;

  float u = KP * err + KI * integrale + KD * deriv;
  if (u > U_MAX) u = U_MAX;
  if (u < -U_MAX) u = -U_MAX;
  if (u > 0.0f && u < U_MIN) u = U_MIN;
  if (u < 0.0f && u > -U_MIN) u = -U_MIN;

  // butee haute en montee : arret immediat
  if (u > 0.0f && fdc_haut_atteint()) {
    treuil_stop();
    actif = 0;
    erreur = TREUIL_FDC_HAUT;
    return;
  }

  // butee basse en descente : on s'arrete sans erreur
  if (u < 0.0f && fdc_bas_atteint()) {
    treuil_stop();
    actif = 0;
    return;
  }

  // toutes les 0,5 s : le codeur doit avoir bouge
  if (++nb_appels >= 50) {
    int32_t deplacement = pos - pos_controle;
    if (deplacement < 0) deplacement = -deplacement;
    if (deplacement < 50) {
      treuil_stop();
      actif = 0;
      erreur = TREUIL_BLOCAGE;
      return;
    }
    pos_controle = pos;
    nb_appels = 0;
  }

  treuil_commande(u);
}

treuil_erreur_t treuil_erreur(void){
  return erreur;
}

void treuil_acquitter(void){
  erreur = TREUIL_OK;
}

