# WakeBand dock rev D

> **Rev D = the rev C dock with the two printed locating pins replaced by a hook latch and one screw.** Rev C's top
> plate sat on two Ø2 mm pins printed on the tray, held by friction; printed pins that small wear loose. Rev D has a
> hook at the left end and an **M2 screw from underneath** at the right end. The outside, the strap channels, LEDs,
> magnets, spring-pin bores and PCB are all rev C's. Rev C is kept unchanged in [`../../rev-c/case`](../../rev-c/case);
> the dock PCB is rev C's ([`../pcb`](../pcb) is a copy). For everything not about the joint (strap, magnets,
> BOOTSEL, printing colour) see the rev C README.

**Update 2026-11-26 (not printed yet):** the magnet pockets are now Ø4.3 mm for the Ø4 x 1.5 mm magnets, 0.15 mm
clearance all round (rev C: Ø4.1). They are open below (the magnets go in from underneath with a drop of CA glue), so
the magnet still sits against the 0.2 mm skin on top: a 0.15 mm gap there would only weaken the pull on the band.

![hook and screw sections](wakeband-dock-rev-d-latch-section.png)

## The joint

- **Hook (back-left):** a lip rising 1.85 mm from the tray's solid back-left end block, where rev C's back-left pin
  was. It follows the outline's back-left corner at a constant inset: a short straight run on the left face (y 117.95
  to 118.6) and then 52 degrees round the corner arc, about 6 mm long in all. It is **1.25 mm thick** with a 0.6 mm 45
  degree gusset at its inside root, and carries a **0.6 mm hook** pointing outward with the band case's profile (0.4 mm
  tip face, 45 degree underside, 0.2 mm lead-in). The top plate's slot is the lip grown by 0.15 mm and swept along the
  plate's swing (0 to 70 degrees), with its inner side squared up so the plate still prints without overhangs; 1.25
  mm of plate stays over it and at least 0.8 mm outside it. Strengthened 2026-11-26: the first version was a straight
  2.2 mm x 1.0 mm tongue; the engaged volume when pulled 0.3 mm went from 0.09 to 0.18 mm3 (2x).
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
| Print check (`../../../tools/printcheck.py`) | one solid each, no overhang past 45 degrees, no knife edges; the only bridge over 5 mm is still rev C's USB-C pocket (the nut pocket roof is a 4 mm bridge); the only thin spots are rev C's 0.4 mm LED skins and 0.2 mm magnet skins; the plate has a few overhang slivers under 0.1 mm2 at the curved end of the hook slot (below a nozzle width) |

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
