/*
 * BQ25125 (TI SLUSDL9; register map as the pin-compatible BQ25120A, SLUSD08). Plan, from the band
 * README:
 * - Leave it in default mode as much as possible: no I2C writes means no host-mode watchdog.
 * - /CD high only while talking to it on battery; low the rest of the time (Hi-Z, 0.7 uA) and
 *   always while docked (/CD high stops charging). I2C is off in Hi-Z.
 * - I2C writes only for: a VBMON battery reading (on battery), the LS/LDO output setting for the
 *   LED supply, ship mode (later).
 */
#include "pmic.h"

#include <zephyr/kernel.h>
#include <zephyr/logging/log.h>

#include "battery.h"
#include "board_io.h"

LOG_MODULE_REGISTER(pmic, LOG_LEVEL_INF);

#define ADDR 0x6A

#define REG_STATUS 0x00
#define REG_FAULT  0x01 /* 7 VIN_OV, 6 VIN_UV, 5 BAT_UVLO, 4 BAT_OCP (clear on read) */
#define REG_TS     0x02 /* TS control and status: TS fault bits (NTC hot/cold) */
#define REG_VBREG  0x05
#define REG_LS_LDO 0x07
#define REG_VBMON  0x0A

#define STATUS_STAT(st)  (((st) >> 6) & 0x3) /* 0 ready, 1 charging, 2 done, 3 fault */
#define VBMON_READ       BIT(7)
/*
 * LS/LDO: bit 7 EN_LS_LDO, bits 6:2 voltage code (0.8 V + 0.1 V per step). Codes above 3.3 V
 * (26-31) make it a load switch: VLED follows PMID. Leave EN_LS_LDO at 0 and switch the output
 * with LSCTRL (output on when either is set). The code may only change while the output is off.
 */
#define LS_LDO_SWITCH    (31u << 2)

static K_MUTEX_DEFINE(pmic_lock);
static uint8_t battery_pct = BATTERY_PCT_UNKNOWN;
static uint16_t battery_mv;
static bool charging;
static bool ls_mode_set;

static bool cd_high(void)
{
	if (pmic_docked()) {
		return false; /* never stop charging to talk to it; I2C works anyway with VIN */
	}
	gpio_pin_set_dt(&io_chg_cd, 1);
	k_msleep(2); /* Hi-Z to active battery takes about 1 ms */
	return true;
}

static void cd_low(void)
{
	gpio_pin_set_dt(&io_chg_cd, 0);
}

static int rd(uint8_t reg, uint8_t *val)
{
	return i2c_reg_read_byte(i2c_bus, ADDR, reg, val);
}

static int wr(uint8_t reg, uint8_t val)
{
	return i2c_reg_write_byte(i2c_bus, ADDR, reg, val);
}

int pmic_init(void)
{
	uint8_t st;
	int err;
	bool cd = cd_high();

	/* On the dock the BQ talks I2C anyway (VIN present), so this works either way. */
	uint8_t fault = 0, ts = 0;

	err = rd(REG_STATUS, &st);
	err = err ?: rd(REG_FAULT, &fault);
	err = err ?: rd(REG_TS, &ts);
	if (cd) {
		cd_low();
	}
	if (err) {
		LOG_ERR("no answer at 0x%02x (%d)", ADDR, err);
		return err;
	}
	/* /PG (DOCK_PG) is low only while VIN is good. STAT: 0 ready, 1 charging, 2 done, 3 fault. */
	LOG_INF("BQ25125 status 0x%02x (STAT %u), faults 0x%02x, TS reg 0x%02x, /PG pin %s -> %s",
		st, STATUS_STAT(st), fault, ts, pmic_docked() ? "low" : "high",
		pmic_docked() ? "docked" : "on battery");
	(void)pmic_update();
	return 0;
}

bool pmic_docked(void)
{
	return gpio_pin_get_dt(&io_dock_pg) == 1; /* active low in the devicetree */
}

int pmic_update(void)
{
	uint8_t st = 0, vbreg = 0x78, vbmon = 0;
	bool docked = pmic_docked();
	bool cd;
	int err;

	k_mutex_lock(&pmic_lock, K_FOREVER);
	cd = cd_high();
	err = rd(REG_STATUS, &st);
	charging = !err && docked && STATUS_STAT(st) == 1;
	if (!err && docked) {
		uint8_t fault = 0;

		(void)rd(REG_FAULT, &fault);
		LOG_INF("docked: status 0x%02x (STAT %u), faults 0x%02x", st, STATUS_STAT(st), fault);
	}
	/*
	 * VBMON only on battery: a reading while charging is high (the datasheet suggests pausing
	 * the charge), and on the dock we stay off I2C writes so the charger keeps its default mode.
	 * Keep the last battery reading while docked.
	 */
	if (!err && !docked) {
		(void)rd(REG_VBREG, &vbreg);
		err = wr(REG_VBMON, VBMON_READ);
		k_msleep(3); /* the reading takes 2 ms */
		err = err ?: rd(REG_VBMON, &vbmon);
	}
	if (cd) {
		cd_low();
	}
	if (!err && !docked) {
		uint16_t mv = battery_vbmon_to_mv(vbmon, battery_vbreg_to_mv(vbreg));

		if (mv) {
			battery_mv = mv;
			battery_pct = battery_mv_to_pct(mv);
		}
		LOG_INF("battery: VBMON 0x%02x, VBATREG reg 0x%02x -> %u mV, %u %%", vbmon, vbreg, mv,
			battery_pct);
	} else if (err) {
		LOG_WRN("battery read failed (%d)", err);
	}
	k_mutex_unlock(&pmic_lock);
	return err;
}

uint8_t pmic_battery_pct(void)
{
	return battery_pct;
}

uint16_t pmic_battery_mv(void)
{
	return battery_mv;
}

bool pmic_charging(void)
{
	return charging;
}

int pmic_led_supply(bool on)
{
	int err = 0;

	k_mutex_lock(&pmic_lock, K_FOREVER);
	if (!on) {
		gpio_pin_set_dt(&io_ls_ctrl, 0);
		k_mutex_unlock(&pmic_lock);
		return 0;
	}
	/*
	 * The LS/LDO output powers up as a 1.8 V LDO, too low for the LED (blue and green need about
	 * 3 V). Set the load-switch code once with the output off, then switch it with LSCTRL. In Hi-Z
	 * (/CD low) the watchdog is off and the setting stays. On the dock the write puts the charger
	 * in host mode; its watchdog returns it to defaults 50 s later, so write again each time.
	 */
	if (!ls_mode_set || pmic_docked()) {
		uint8_t back = 0;
		bool cd;

		gpio_pin_set_dt(&io_ls_ctrl, 0);
		cd = cd_high();
		err = wr(REG_LS_LDO, LS_LDO_SWITCH);
		err = err ?: rd(REG_LS_LDO, &back);
		if (cd) {
			cd_low();
		}
		if (err || (back & 0xFC) != LS_LDO_SWITCH) {
			LOG_WRN("LS/LDO setup failed (err %d, reg 0x%02x)", err, back);
		} else {
			ls_mode_set = !pmic_docked();
			LOG_INF("LED supply in load-switch mode (reg 0x07 = 0x%02x)", back);
		}
	}
	gpio_pin_set_dt(&io_ls_ctrl, 1);
	k_mutex_unlock(&pmic_lock);
	return err;
}
