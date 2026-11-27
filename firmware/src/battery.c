#include "battery.h"

#include <stddef.h>

uint16_t battery_vbmon_to_mv(uint8_t vbmon_reg, uint16_t vbatreg_mv)
{
	/* Bits 6:5 range (60/70/80/90 % of VBATREG), bits 4:2 threshold above the range floor. */
	static const uint8_t th_pct[8] = {0, 0, 2, 4, 4, 6, 6, 8};
	uint8_t range = (vbmon_reg >> 5) & 0x3;
	uint8_t th = (vbmon_reg >> 2) & 0x7;
	uint32_t pct_x10;

	if (th == 0) {
		/* Nothing found in this range. In the lowest range that means below 60 % of
		 * VBATREG (about 2.5 V): call it empty. Elsewhere the reading is incomplete. */
		return range == 0 ? (uint16_t)(vbatreg_mv * 60u / 100u) : 0;
	}
	/* Middle of the 2 % step the reading falls in. */
	pct_x10 = (60u + 10u * range + th_pct[th]) * 10u + 10u;
	return (uint16_t)(vbatreg_mv * pct_x10 / 1000u);
}

uint16_t battery_vbreg_to_mv(uint8_t reg05)
{
	uint16_t mv = 3600u + 10u * (reg05 >> 1);

	return mv > 4650u ? 4650u : mv;
}

uint8_t battery_mv_to_pct(uint16_t mv)
{
	/* Typical small LiPo discharge curve at light load. */
	static const struct {
		uint16_t mv;
		uint8_t pct;
	} curve[] = {
		{3300, 0}, {3500, 5}, {3600, 10}, {3700, 25}, {3750, 40}, {3800, 52},
		{3850, 62}, {3900, 70}, {4000, 82}, {4100, 92}, {4180, 100},
	};
	size_t n = sizeof(curve) / sizeof(curve[0]);

	if (mv <= curve[0].mv) {
		return 0;
	}
	for (size_t i = 1; i < n; i++) {
		if (mv <= curve[i].mv) {
			uint32_t span = curve[i].mv - curve[i - 1].mv;
			uint32_t pos = mv - curve[i - 1].mv;

			return (uint8_t)(curve[i - 1].pct +
					 (curve[i].pct - curve[i - 1].pct) * pos / span);
		}
	}
	return 100;
}
