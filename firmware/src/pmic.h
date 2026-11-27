/* BQ25125 charger. Its power-up defaults already charge correctly (4.2 V, 30 mA set by R202). */
#ifndef NUDGEBAND_PMIC_H
#define NUDGEBAND_PMIC_H

#include <stdbool.h>
#include <stdint.h>

int pmic_init(void);

/* True while the dock supplies VIN (/PG low). */
bool pmic_docked(void);

/* Refresh the charging flag and (on battery) the VBMON battery reading. Call now and then. */
int pmic_update(void);

/* Battery percent (0-100) from the last VBMON reading, or 0xFF before the first one. */
uint8_t pmic_battery_pct(void);

/* Battery voltage in mV from the last VBMON reading (0 if none). */
uint16_t pmic_battery_mv(void);

/* True while docked and the charger reports a charge in progress. */
bool pmic_charging(void);

/* LED supply on/off (LS/LDO in load-switch mode). */
int pmic_led_supply(bool on);

#endif
