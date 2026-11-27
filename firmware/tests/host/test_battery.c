/* Battery level from VBMON (src/battery.c). */
#include "battery.h"
#include "test.h"

void test_battery(void)
{
	/* VBATREG */
	CHECK(battery_vbreg_to_mv(0x78) == 4200); /* BQ25125 default */
	CHECK(battery_vbreg_to_mv(0x96) == 4350);

	/* Datasheet example: range 10, threshold 011 = 84-86 % of VBATREG. */
	uint8_t r84 = (0x2 << 5) | (0x3 << 2);
	CHECK(battery_vbmon_to_mv(r84, 4200) == 4200u * 85u / 100u);
	/* Range 11, threshold 111 = 98-100 %: about 4.16 V. */
	CHECK(battery_vbmon_to_mv((0x3 << 5) | (0x7 << 2), 4200) == 4158);
	/* VBMON_READ bit and unused bits are ignored. */
	CHECK(battery_vbmon_to_mv(0x80 | r84 | 0x3, 4200) == battery_vbmon_to_mv(r84, 4200));
	/* Empty reading in a high range: unknown. Lowest range: empty cell. */
	CHECK(battery_vbmon_to_mv(0x3 << 5, 4200) == 0);
	CHECK(battery_vbmon_to_mv(0x00, 4200) == 2520);

	/* Voltage to percent: monotonic, clamped, never above 100 (the old firmware sent 0xFF). */
	CHECK(battery_mv_to_pct(0) == 0);
	CHECK(battery_mv_to_pct(3300) == 0);
	CHECK(battery_mv_to_pct(4180) == 100);
	CHECK(battery_mv_to_pct(4350) == 100);
	CHECK(battery_mv_to_pct(3800) == 52);
	uint8_t prev = 0;
	for (uint16_t mv = 3000; mv <= 4400; mv += 5) {
		uint8_t p = battery_mv_to_pct(mv);

		CHECK(p >= prev && p <= 100);
		prev = p;
	}
	for (int reg = 0; reg < 256; reg++) {
		uint16_t mv = battery_vbmon_to_mv((uint8_t)reg, 4200);

		CHECK(mv == 0 || (mv >= 2520 && mv <= 4200));
	}
}
