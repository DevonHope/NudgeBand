/*
 * IS31FL3193 (Lumissil) RGB LED driver. The chip is write-only over I2C. Power-up state: software
 * shutdown (reg 0x00 = 0x01: SSD = 1, EN = 0). Enable = write 0x20 (EN = 1, SSD = 0).
 *
 * The LED's anode (VLED) is on the BQ25125 LS/LDO output, which powers up as a 1.8 V LDO: too low
 * for the green and blue dies. pmic_led_supply() switches it to load-switch mode (VLED = PMID).
 */
#include "led.h"

#include <zephyr/kernel.h>
#include <zephyr/logging/log.h>

#include "board_io.h"
#include "pmic.h"

LOG_MODULE_REGISTER(led, LOG_LEVEL_INF);

/* 0x68 with the address pin to GND (band README); the WLCSP "D" version is fixed at 0x6B. */
static const uint8_t addrs[] = {0x68, 0x6B};
static uint8_t addr;

#define REG_SHUTDOWN 0x00
#define REG_MODE     0x02
#define REG_CURRENT  0x03
#define REG_PWM1     0x04 /* OUT1 green */
#define REG_PWM2     0x05 /* OUT2 blue */
#define REG_PWM3     0x06 /* OUT3 red */
#define REG_UPDATE   0x07
#define REG_LED_CTRL 0x1D
#define REG_RESET    0x2F

#define SHUTDOWN_ON  0x20 /* EN = 1 (channels on), SSD = 0 (normal operation) */
#define MODE_PWM     0x00
#define CURRENT_5MA  (0x2 << 2) /* CS bits 4:2: 000 42 mA, 001 10 mA, 010 5 mA, 011 30 mA */
#define CTRL_ALL     0x07

static int wr(uint8_t reg, uint8_t val)
{
	return i2c_reg_write_byte(i2c_bus, addr, reg, val);
}

/* Wake the driver (SDB high) and find which address answers (the chip can't be read). */
static void probe(void)
{
	gpio_pin_set_dt(&io_led_en, 1);
	k_usleep(500);
	for (size_t i = 0; i < ARRAY_SIZE(addrs); i++) {
		if (i2c_reg_write_byte(i2c_bus, addrs[i], REG_RESET, 0x00) == 0) {
			addr = addrs[i];
			LOG_INF("IS31FL3193 at 0x%02x", addr);
			break;
		}
	}
	if (!addr) {
		LOG_ERR("IS31FL3193 not answering at 0x68 or 0x6B");
	}
	gpio_pin_set_dt(&io_led_en, 0);
}

int led_init(void)
{
	probe();
	return addr ? 0 : -ENODEV;
}

int led_set(uint8_t r, uint8_t g, uint8_t b)
{
	int err;

	if (!r && !g && !b) {
		gpio_pin_set_dt(&io_led_en, 0); /* hardware shutdown */
		return pmic_led_supply(false);
	}
	if (!addr) {
		probe();
		if (!addr) {
			return -ENODEV;
		}
	}
	err = pmic_led_supply(true);
	gpio_pin_set_dt(&io_led_en, 1);
	k_usleep(500);
	err = err ?: wr(REG_MODE, MODE_PWM);
	err = err ?: wr(REG_CURRENT, CURRENT_5MA);
	err = err ?: wr(REG_LED_CTRL, CTRL_ALL);
	err = err ?: wr(REG_PWM1, g);
	err = err ?: wr(REG_PWM2, b);
	err = err ?: wr(REG_PWM3, r);
	err = err ?: wr(REG_UPDATE, 0x00);
	err = err ?: wr(REG_SHUTDOWN, SHUTDOWN_ON);
	if (err) {
		LOG_WRN("LED write failed (%d)", err);
	}
	return err;
}
