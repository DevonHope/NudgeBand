/*
 * Battery level from the BQ25125's VBMON reading (hardware-independent, host-tested).
 * VBMON gives the battery voltage as a fraction of VBATREG in 2 % steps from 60 % to 100 %.
 */
#ifndef NUDGEBAND_BATTERY_H
#define NUDGEBAND_BATTERY_H

#include <stdint.h>

#define BATTERY_PCT_UNKNOWN 0xFF

/* Battery voltage in mV from VBMON register 0x0A and VBATREG (mV); 0 if the reading is empty. */
uint16_t battery_vbmon_to_mv(uint8_t vbmon_reg, uint16_t vbatreg_mv);

/* VBATREG in mV from register 0x05 (3.6 V + 10 mV per step in bits 7:1). */
uint16_t battery_vbreg_to_mv(uint8_t reg05);

/* Rough state of charge (0-100) of a 4.2 V LiPo cell at rest. */
uint8_t battery_mv_to_pct(uint16_t mv);

#endif
