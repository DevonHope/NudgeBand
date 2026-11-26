# WakeBand dock rev D

> **Rev D = the rev C dock with the two printed locating pins replaced by a hook latch and one screw.** Rev C's top
> plate sat on two Ø2 mm pins printed on the tray, held by friction; printed pins that small wear loose. Rev D has a
> hook at the left end and an **M2 screw from underneath** at the right end. The outside, the strap channels, LEDs,
> magnets, spring-pin bores and PCB are all rev C's. Rev C is kept unchanged in [`../../rev-c/case`](../../rev-c/case);
> the dock PCB is rev C's ([`../pcb`](../pcb) is a copy). For everything not about the joint (strap, magnets,
> BOOTSEL, printing colour) see the rev C README.

![hook and screw sections](wakeband-dock-rev-d-latch-section.png)

## The joint

- **Hook (back-left):** a tongue 2.2 mm wide (y 118.2 to 120.4) and 1.0 mm thick rises 1.85 mm from the tray's
  solid back-left end block, 1.9 mm in from the left face, where rev C's back-left pin was. A **0.6 mm hook** at its
  top points outward (to the left), with the band case's profile: 0.4 mm tip face, 45 degree underside, 0.2 mm
  lead-in. The top plate has a matching slot from underneath, 0.15 mm clearance, 0.6 mm extra on the inner side
  for the swing, 1.25 mm of plate left over it.
- **Screw (back-right):** **M2 x 8 countersunk** (DIN 965 / ISO 7046 or ISO 10642) up through the tray's back-right
  end block at (143.8, 121.0), head 0.2 mm below the tray's underside, into an **M2 hex nut** (ISO 4032, 4 mm
  across flats, 1.6 mm thick) pressed into a hex pocket in the plate underside (4.05 mm across flats, 1.7 mm deep).
  The plate is only 3.25 mm thick, too thin for a 3 mm heat-set insert, so a nut gives metal threads instead; it
  needs no heat tool and takes any number of re-flashes.
- **Front edge:** rests on the tray, as in rev C (whose two pins were both at the back). A second hook at the
  front-left can't work: that corner of the plate is a thin curved strip between the outline, the band recess and
  the strap channel, too far from the edge the plate rocks on for a hook to swing clear.
- **Rubber feet:** both pairs moved 4 mm toward the middle (x 100.35 and 136.95) so the right-hand foot doesn't cover
  the screw head.

## Assembly (replaces rev C's steps 3 and 4)

1. Solder the spring pins, flash the dock and lay the PCB in the tray (as rev C).
2. Press the magnets into the plate (as rev C), and press the **M2 nut** into the hex pocket in the plate underside
   (a drop of CA glue keeps it there when the plate is off).
3. Hold the plate **steeply tilted, about 50 degrees, left end down**, and hook its left end over the tray's hook
   at the back-left corner.
4. Swing the right end down, guiding the spring-pin plungers into their bores.
5. Fit the M2 x 8 screw from underneath, then stick on the rubber feet inside their rings.

To re-flash, take the screw out and swing the right end up; the plate comes off the hook at about 50 degrees.

## Checks (2026-11-26, `dock_rev_d.py`)

| Check | Result |
| --- | --- |
| Top plate, tray | one valid solid each |
| Top vs tray, closed | 0 overlap |
| Clash, closed: PCB envelope, spring pins, magnets, screw, nut, against plate, tray and the band's wrist cover | 0 overlaps |
| Swing: plate rocking on the tray's left outer edge, 1 to 70 degrees, against the tray, PCB envelope and spring pins | 0 overlap at every step |
| Hook engages / releases | from 50 degrees of tilt |
| Hook holds | pulling the closed tongue 0.3 mm down runs into the plate |
| Print check (`../../../tools/printcheck.py`) | one solid each, no overhang past 45 degrees, no knife edges; the only bridge over 5 mm is still rev C's USB-C pocket (the nut pocket roof is a 4 mm bridge); the only thin spots are rev C's 0.4 mm LED skins and 0.2 mm magnet skins |

## Files

| File | What |
| --- | --- |
| `wakeband-dock-rev-d-top.step` / `.stl` | top plate (print this, underside down) |
| `wakeband-dock-rev-d-tray.step` / `.stl` | tray (print this, floor down) |
| `wakeband-dock-rev-d-magnets.step`, `-spring-pins.step`, `-screw-nut.step`, `-strap-standin.step` | fit-check models |
| `wakeband-dock-rev-d-latch-section.png` | sections through the hook and the screw |
| `dock_rev_d.py`, `preview_rev_d.py` | build the parts and run the checks; draw the sections |

    python dock_rev_d.py OUT_DIR

## To buy (in addition to rev C's list)

- 1 x M2 x 8 countersunk screw, A2 stainless
- 1 x M2 hex nut, ISO 4032, A2 stainless
