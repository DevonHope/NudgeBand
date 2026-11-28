# NudgeBand

**A small, open-source wristband that wakes you up gently.**

Set a wake-up time, and NudgeBand watches how you move in your sleep. During the 30 minutes before
your alarm, it waits for a moment of light sleep and wakes you with a soft vibration on your wrist,
with no sound and no phone needed. If you never reach light sleep, it still wakes you at your set time.

Everything is open: the circuit boards, the 3D-printed case, the charging dock and the strap pattern.
You can build one yourself.

> **Status (November 2026):** prototype boards received. The dock is up and running its programmer
> firmware; the band board has not been powered up with firmware yet. See [Current status](#current-status)
> and the [assembly guide](docs/assembly/nudgeband-assembly-guide-rev-e.pdf).

---

## How it works

1. **You wear it to bed.** A low-power motion sensor (accelerometer) measures how much you move.
2. **It estimates your sleep stage.** Less movement usually means deeper sleep, and small movements
   usually mean light sleep.
3. **It picks the best moment.** In the 30-minute window before your alarm, it waits for light sleep,
   because waking from light sleep feels easier than waking from deep sleep.
4. **It nudges you awake.** A tiny vibration motor ramps up gently instead of buzzing suddenly.
5. **You put it on the dock.** The dock charges the band and is also used to load new firmware.

The band has no screen and no USB port. It is sealed except for four small gold contacts on the
underside that touch spring pins in the dock.

## What's in it

| Part | What it does |
| --- | --- |
| Nordic nRF54L10 | The main chip, with Bluetooth Low Energy built in |
| Motion sensor (accelerometer) | Tracks movement through the night |
| DRV2605L + 8 mm vibration motor | Gentle, ramped vibration |
| TI BQ25125 | Charges the battery |
| 60 mAh LiPo battery | Expected to last about a month per charge (estimate, not yet measured) |
| RGB LED | Shows status through a thin window in the case, with no hole |

- **Board:** 33 x 15 mm, 4-layer, assembled by JLCPCB
- **Case:** about 45 x 19 x 10 mm, 3D-printed in PETG. The cover hooks in at one end and is held by one M2 screw at the other
- **Dock:** USB-C, magnets to hold the band in place, and a built-in programmer (RP2040 running Raspberry Pi's `debugprobe`)
- **Strap:** 16 mm wide. Either 3D-print a TPU strap (no sewing) or sew one from a free pattern (Velcro, or elastic with a buckle)

## Current status

*Last updated: 26 November 2026*

| Area | Status |
| --- | --- |
| Hardware design | ✅ **Build rev D.** Band and dock boards are **rev C** (reviewed, DRC/ERC clean); rev D adds new printed parts only |
| PCBs | ✅ **Received** from JLCPCB (band rev C, dock rev C, contact carrier) |
| Dock | ✅ **Brought up.** Passed all 6 checks of the [LED self-test](firmware/dock-selftest/README.md) (flash ID, flash write, 12 MHz crystal, SWDIO loopback, 1.8 V level shifter, SWCLK pull-down) and now runs Raspberry Pi's [debugprobe](https://github.com/raspberrypi/debugprobe) firmware. Firmware testing on the dock has gone well so far |
| Band | ⏳ **Next.** Not yet assembled or flashed, so the dock has not been tested with a band yet |
| Case and dock housing | ✅ **Rev D designed.** The band cover and the dock top now hook in at one end and swing down onto a single M2 screw, instead of relying on printed alignment pins that wear out. Not yet test-printed |
| Strap | ✅ Printable **TPU strap** in four sizes (S to XL, no sewing; [`tpu-rev-b`](hardware/strap/tpu-rev-b) recommended) plus two **sewn strap** patterns |
| Assembly guide | ✅ **20-page colour guide** for band rev C / case rev D / dock rev D (see [below](#assembly-guide)) |
| Band firmware | 🛠️ **Started.** Plan in [`firmware/TODO.md`](firmware/TODO.md); smart-wake logic written and unit-tested, drivers drafted, builds in CI, not yet run on a band |
| Android app | 🧪 **First version** in [`android/`](android/). Works with a simulated band; Bluetooth spec in [`docs/ble-protocol.md`](docs/ble-protocol.md) |
| Phone-only alarm | 🧪 Until the band works, a fork of the open-source Somn sleep app ([DevonHope/somn](https://github.com/DevonHope/somn)) does smart wake with the phone's own motion sensor. It is also where the band's Bluetooth link will be tried first |
| Security | ✅ Every pull request is checked for leaked secrets, personal details, unsafe workflows, vulnerable dependencies and code issues (CodeQL). See [`SECURITY.md`](SECURITY.md) |

**Up next:** assemble the first band following the guide, flash it through the dock, then bring up the
firmware (charger setup, motion sensor, vibration) and test smart-wake on real nights. Test-print the
rev D latches (if they are tight, the clearance can be opened up from 0.15 to 0.2 mm in the case scripts).

**Known limitations:**
- The radio and antenna are not certified (FCC, IC or CE). Treat it as a personal project, not a product.
- The antenna may need tuning on the first boards.
- Battery life is a datasheet estimate until it is measured.

## Assembly guide

[**nudgeband-assembly-guide-rev-e.pdf**](docs/assembly/nudgeband-assembly-guide-rev-e.pdf) is a 20-page,
picture-by-picture build guide in colour. It covers:

- the parts list, what to print and the print settings
- building the dock and loading debugprobe onto it
- the contact carrier with its four spring pins
- wiring the battery and motor to the band board. The pads on the back of the board are shown in
  [`band-rev-c-back-pads.png`](docs/assembly/band-rev-c-back-pads.png): battery + to TP201 and – to TP202,
  motor to TP501 and TP502 (either way round)
- getting the magnets the right way round in the cover and the dock
- closing the band: tuck the hooked end of the cover in first, swing it down, fit the screw
- fitting the strap and the first charge

All the pictures are generated from the KiCad boards and the case models, so the guide can be rebuilt
after a design change. See [`docs/assembly/README.md`](docs/assembly/README.md).

## Repository layout

```
hardware/
├── band/      the wristband: PCB, case and contact carrier for each revision (build rev D)
├── dock/      the charging and programming dock: PCB and housing for each revision (build rev D)
├── strap/     printable TPU straps (STL/3MF) and strap sewing patterns (PDF)
├── reviews/   design reviews of the boards
└── tools/     helper scripts (e.g. printability check)
android/       the Android companion app (and a simulated band for testing)
firmware/      band firmware (Zephyr): plan in TODO.md, source, unit tests; dock-selftest/ for the dock
docs/          assembly guide, roadmap, parts research, design notes and the Bluetooth protocol
```

Older revisions (A to C) are kept for reference. Each folder has its own README with details.
[`hardware/README.md`](hardware/README.md) lists exactly what to order and what to print.

## Building one

Follow the [assembly guide](#assembly-guide). In short:

1. **Order the boards.** Rev D uses the rev C boards: fab files in `hardware/band/rev-c/pcb/fab/` and
   `hardware/dock/rev-c/pcb/fab/` (JLCPCB with assembly), plus the small contact-carrier board.
2. **Buy the extras.** Spring pins, magnets, battery and motor are listed in
   [`BUY-LIST.md`](hardware/band/rev-a/contact-carrier/BUY-LIST.md).
3. **Print the case and dock** in PETG from `hardware/band/rev-d/case/` and `hardware/dock/rev-d/case/`.
   Print notes are in each folder's README.
4. **Make the strap.** Print a TPU strap from `hardware/strap/tpu-rev-b/`, or sew one from the patterns in `hardware/strap/`.
5. **Set up the dock.** Flash the [self-test](firmware/dock-selftest/README.md), check the LEDs, then load debugprobe.
6. **Flash the band firmware** through the dock (see [`firmware/README.md`](firmware/README.md); not ready yet).

Design tools: KiCad 10 for the PCBs, Python scripts for the case models.

## License

[MIT](LICENSE). Use it, change it and share it.
