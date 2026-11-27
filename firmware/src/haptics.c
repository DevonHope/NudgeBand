/*
 * DRV2605L register-level driver (TI SLOS854). The motor is driven in real-time playback (RTP)
 * mode so the firmware can ramp the strength itself. EN is held low between buzzes (shutdown).
 * Motor: Vybronics VG0832012 LRA (1.8 Vrms, 235 Hz). Auto-calibrated once at boot.
 */
#include "haptics.h"

#include <zephyr/kernel.h>
#include <zephyr/logging/log.h>

#include "board_io.h"

LOG_MODULE_REGISTER(haptics, LOG_LEVEL_INF);

#define ADDR 0x5A

#define REG_STATUS    0x00
#define REG_MODE      0x01
#define REG_RTP       0x02
#define REG_LIBRARY   0x03
#define REG_GO        0x0C
#define REG_RATED_V   0x16
#define REG_OD_CLAMP  0x17
#define REG_CAL_COMP  0x18
#define REG_CAL_BEMF  0x19
#define REG_FEEDBACK  0x1A
#define REG_CONTROL1  0x1B
#define REG_CONTROL3  0x1D
#define REG_CONTROL4  0x1E
#define REG_OL_PERIOD 0x20

#define MODE_RTP          0x05
#define MODE_AUTOCAL      0x07
#define MODE_STANDBY      BIT(6)
#define LIBRARY_LRA       0x06
#define STATUS_DIAG_FAIL  BIT(3)

/*
 * VG0832012 LRA: 1.8 Vrms rated (1.85 max), 235 Hz. With SAMPLE_TIME 300 us:
 * RATED_VOLTAGE = 1.8 * sqrt(1 - (4 * 300 us + 300 us) * 235 Hz) / 20.58 mV = 70.
 * OD_CLAMP 0x7A is about 2.6 V peak (the motor's 1.85 Vrms max as a sine peak).
 * DRIVE_TIME: half a period (2.13 ms) = 0.5 ms + 0.1 ms * 16.
 * Open-loop fallback period: 1 / (235 Hz * 98.46 us) = 43.
 */
#define LRA_RATED_V   70
#define LRA_OD_CLAMP  0x7A
#define LRA_CONTROL1  (0x80 | 16)     /* STARTUP_BOOST, DRIVE_TIME 16 */
#define LRA_FEEDBACK  0xAA            /* LRA, brake factor 2, loop gain 2, BEMF gain 2 */
#define LRA_CONTROL4  0x30            /* AUTO_CAL_TIME 3 (longest) */
#define LRA_OL_PERIOD 43
/* Control3: NG_THRESH and ERM_OPEN_LOOP at their defaults (0xA0), RTP data unsigned (bit 3),
 * bit 0 LRA_OPEN_LOOP when calibration failed. */
#define CONTROL3_BASE 0xA8
#define CONTROL3_LRA_OPEN_LOOP BIT(0)

#define STEP_MS 50

static struct k_work_delayable step_work;
static uint32_t elapsed_ms;
static uint32_t ramp_ms;
static uint32_t total_ms;
static uint8_t target;
static uint8_t pat;
static bool running;

static int wr(uint8_t reg, uint8_t val)
{
	return i2c_reg_write_byte(i2c_bus, ADDR, reg, val);
}

static bool calibrated;
static uint8_t cal_comp, cal_bemf, cal_feedback = LRA_FEEDBACK;

/* Write the motor settings (and calibration results, if any). EN must be high. */
static int configure(bool open_loop)
{
	int err;

	err = wr(REG_FEEDBACK, cal_feedback);
	err = err ?: wr(REG_RATED_V, LRA_RATED_V);
	err = err ?: wr(REG_OD_CLAMP, LRA_OD_CLAMP);
	err = err ?: wr(REG_CONTROL1, LRA_CONTROL1);
	err = err ?: wr(REG_CONTROL4, LRA_CONTROL4);
	err = err ?: wr(REG_OL_PERIOD, LRA_OL_PERIOD);
	err = err ?: wr(REG_LIBRARY, LIBRARY_LRA);
	if (calibrated) {
		err = err ?: wr(REG_CAL_COMP, cal_comp);
		err = err ?: wr(REG_CAL_BEMF, cal_bemf);
	}
	err = err ?: wr(REG_CONTROL3, CONTROL3_BASE | (open_loop ? CONTROL3_LRA_OPEN_LOOP : 0));
	return err;
}

/* Auto-calibration (a short buzz at boot). Without it the closed loop has no back-EMF gain to
 * work with, so on failure the driver runs the motor open loop at its 235 Hz instead. */
static void calibrate(void)
{
	uint8_t go = 1, st = 0;
	int err;

	calibrated = false;
	err = configure(false);
	err = err ?: wr(REG_MODE, MODE_AUTOCAL);
	err = err ?: wr(REG_GO, 1);
	for (int i = 0; !err && go && i < 300; i++) {
		k_msleep(10);
		err = i2c_reg_read_byte(i2c_bus, ADDR, REG_GO, &go);
		go &= 1;
	}
	err = err ?: i2c_reg_read_byte(i2c_bus, ADDR, REG_STATUS, &st);
	if (err || go || (st & STATUS_DIAG_FAIL)) {
		LOG_WRN("auto-calibration failed (err %d, go %u, status 0x%02x): open loop", err, go,
			st);
		(void)wr(REG_GO, 0);
		return;
	}
	(void)i2c_reg_read_byte(i2c_bus, ADDR, REG_CAL_COMP, &cal_comp);
	(void)i2c_reg_read_byte(i2c_bus, ADDR, REG_CAL_BEMF, &cal_bemf);
	(void)i2c_reg_read_byte(i2c_bus, ADDR, REG_FEEDBACK, &cal_feedback);
	calibrated = true;
	LOG_INF("calibrated: comp 0x%02x, bemf 0x%02x, feedback 0x%02x", cal_comp, cal_bemf,
		cal_feedback);
}

/* Strength at this moment of the pattern, 0-255. */
static uint8_t level_now(void)
{
	uint32_t lvl = target;

	if (elapsed_ms < ramp_ms) {
		lvl = lvl * elapsed_ms / ramp_ms;
	}
	switch (pat) {
	case 1: /* slow pulses: 1 s on, 1 s off */
		return (elapsed_ms / 1000) % 2 ? 0 : (uint8_t)lvl;
	case 2: /* heartbeat: two short beats every 1.2 s */
	{
		uint32_t t = elapsed_ms % 1200;

		return (t < 150 || (t >= 300 && t < 450)) ? (uint8_t)lvl : 0;
	}
	default:
		return (uint8_t)lvl;
	}
}

static void power_down(void)
{
	(void)wr(REG_RTP, 0);
	(void)wr(REG_MODE, MODE_STANDBY);
	gpio_pin_set_dt(&io_hapt_en, 0);
	running = false;
}

static void step(struct k_work *work)
{
	ARG_UNUSED(work);
	if (!running) {
		return;
	}
	if (elapsed_ms >= total_ms) {
		power_down();
		return;
	}
	int err = wr(REG_RTP, level_now());

	if (err) {
		LOG_WRN("RTP write failed (%d)", err);
	}
	elapsed_ms += STEP_MS;
	k_work_reschedule(&step_work, K_MSEC(STEP_MS));
}

int haptics_init(void)
{
	uint8_t st;
	int err;

	k_work_init_delayable(&step_work, step);

	gpio_pin_set_dt(&io_hapt_en, 1);
	k_msleep(1);
	err = i2c_reg_read_byte(i2c_bus, ADDR, REG_STATUS, &st);
	if (err) {
		LOG_ERR("no answer at 0x%02x (%d)", ADDR, err);
		gpio_pin_set_dt(&io_hapt_en, 0);
		return err;
	}
	LOG_INF("DRV2605L status 0x%02x (device id %u)", st, st >> 5);
	/* TODO(TODO.md 2.3): keep the calibration in settings instead of redoing it every boot. */
	calibrate();
	power_down();
	return 0;
}

int haptics_start(uint8_t intensity, uint8_t pattern, uint8_t ramp_s, uint8_t buzz_s)
{
	int err;

	gpio_pin_set_dt(&io_hapt_en, 1);
	k_msleep(1);
	/* Registers are rewritten every time: EN low (shutdown) between buzzes. */
	err = configure(!calibrated);
	err = err ?: wr(REG_RTP, 0);
	err = err ?: wr(REG_MODE, MODE_RTP);
	if (err) {
		LOG_ERR("motor driver setup failed (%d)", err);
		gpio_pin_set_dt(&io_hapt_en, 0);
		return err;
	}
	LOG_INF("buzz: drive %u, pattern %u, %u s (%s loop)", intensity, pattern, buzz_s,
		calibrated ? "closed" : "open");
	target = intensity;
	pat = pattern;
	ramp_ms = (uint32_t)ramp_s * 1000;
	total_ms = (uint32_t)buzz_s * 1000;
	elapsed_ms = 0;
	running = true;
	k_work_reschedule(&step_work, K_NO_WAIT);
	return 0;
}

void haptics_stop(void)
{
	running = false;
	k_work_cancel_delayable(&step_work);
	power_down();
}

bool haptics_busy(void)
{
	return running;
}
