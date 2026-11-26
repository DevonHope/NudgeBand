# WakeBand case rev D (for the rigid rev C board)

> **Rev D = the rev C case with the two printed press-fit pins at the antenna end replaced by a hook latch.**
> Small printed pins wear loose and snap after a few openings, so rev D has none. Everything else (antenna
> pocket, dock land, 0.4 mm LED skin, screw boss, contact-carrier pocket, magnets, strap loops) is rev C's,
> and so is the outside: the hook is hidden inside the joint. Rev C is kept unchanged in
> [`../../rev-c/case`](../../rev-c/case). The board is rev C's ([`../pcb`](../pcb) is a copy).

**Update 2026-11-26 (not printed yet):**
- **Magnet pockets** in the wrist cover are now Ø3.3 x 1.15 mm for the Ø3 x 1 mm magnets: 0.15 mm clearance all round
  and on top (rev C: 0.05 mm). The 0.2 mm skin under them is unchanged; the dome over each pocket rises 0.1 mm more
  (top at z 1.6), so the print pause moves to **z 1.35 mm** and the foam under the cell is 0.35 mm thinner over the domes.
- **LED side window:** the one-piece TPU strap now runs over the top of the shell and hides the top LED window, so the
  long side wall next to the charge LED is hollowed from inside (x 128.9 to 131.4, z 7.5 to 8.3) down to a 0.4 mm skin
  on the outside face. The LED shows through the side as well as the top. The top, end walls and strap slots are
  unchanged. Print check: no new bridges or overhangs; the only new thin spot is that 0.4 mm skin.


![hook lip: tip in, swing down, closed](wakeband-case-rev-d-latch-section.png)

## The hook latch

- **Cover:** the ridge round the cover's edge rises 1.6 mm higher **across the whole antenna end and round both
  corners** (52 degrees round each corner arc, about 18 mm of lip in all), just outside the board's end edge. Above
  the ridge it is **1.25 mm thick**, and its top carries a continuous **0.6 mm hook lip** pointing outward: 0.4 mm
  vertical tip face, 45 degree underside, 0.2 mm lead-in chamfer on top. A 0.6 mm 45 degree gusset fills the inside
  root, so there is no sharp inner corner where it meets the cover. The inner top edge is chamfered 0.35 x 0.8 mm
  so the lip clears the shell's two antenna-strip posts as it swings.
- **Shell:** a matching slot with an undercut over the lip, **0.15 mm clearance** all round. The slot is the lip's
  own path as the cover swings (0 to 60 degrees), so it swings in freely but can't be pulled straight off. The end
  wall keeps 1.6 mm outside the undercut and 1.55 mm of roof over the slot; the corners stop where the side wall
  would get thinner than 0.8 mm.
- **Why this shape** (strengthened 2026-11-26): the cover prints wrist face down, so the hook bends across its
  layer lines, the weakest direction for FDM. Compared with the first rev D hook (one 10 mm x 0.95 mm tongue, sharp
  root), the lip is about 1.8x longer and 1.3x thicker, with no sharp root corner. The engaged volume when the cover
  is pulled 0.3 mm toward the wrist went from 0.40 to 0.97 mm3 (2.4x).
- **Motor end:** unchanged, the M2 x 6 countersunk screw into the heat-set insert in the shell boss.

### Closing the case

1. Lay the board in the cover as before (cell, motor and contact carrier already fitted).
2. Hold the shell top face down. Tip the cover in **antenna end first**, steeply tilted (about 40 degrees), so the
   hook lip goes in under the shell's end wall.
3. Swing the motor end down. The cover rocks on its antenna-end edge and the hook moves in under the undercut by
   itself; nothing slides.
4. Fit the M2 screw from the wrist face.

To open, take the screw out and lift the motor end: the cover swings out and comes free once it is tilted about
40 degrees.

## Checks (2026-11-26, `case_rev_d.py`)

| Check | Result |
| --- | --- |
| Shell, cover | one valid solid each |
| Shell vs cover, closed | 0 overlap (rev C had 0.77 mm3: the press fit of the two pins) |
| Tongue vs board | 0 overlap |
| Swing: cover and board rocking on the outer edge of the joint at the antenna end, 1 to 60 degrees | 0 overlap at every step |
| Hook engages / releases | from 40 degrees of tilt; below that the cover can't drop off the shell |
| Hook holds | pulling the closed tongue 0.3 mm toward the wrist runs into the shell |
| Print check (`../../../tools/printcheck.py`) | one solid each, no overhang past 45 degrees, no new bridges; the only thin spots are rev C's own (0.4 mm LED skin, 0.2 mm magnet skins, the 0.75 mm wall at the insert, the carrier pocket floor). The shell has a few knife-edge slivers under 0.1 mm long where the lip's slot ends at the two corners (below a nozzle width, so they don't print) |

The cell and motor sit well inside the board outline and the tongue and slot are outside it, so rev C's clash
check against the board, cell and LRA (0 overlaps) still holds; only the two press-fit pins and their holes were
removed.

## Printing

As rev C: **shell top face down**, **cover wrist face down** with a pause at z 1.35 mm for the magnets, PETG, no
supports. The hook's underside and the undercut's lower face are both 45 degrees, so they print as ordinary
chamfers in these orientations. If your printer runs tight and the hook won't go in, open `CLR` in
`case_rev_d.py` to 0.2 and reprint the shell only.

## Files

| File | What |
| --- | --- |
| `wakeband-case-rev-d-shell.step` / `.stl` | outer shell (print this) |
| `wakeband-case-rev-d-cover.step` / `.stl` | wrist cover with the hook tongue (print this) |
| `wakeband-case-rev-d-latch-section.png` | section through the hook: tip in, swing, closed |
| `case_rev_d.py` | builds both parts from rev C's script and runs the checks above (about 3 minutes: the slot is swept along the swing) |
| `preview_rev_d.py` | draws the section picture (needs matplotlib) |

    python case_rev_d.py OUT_DIR

Hardware is unchanged from rev C: M2 x 6 countersunk screw, M2 x 3 heat-set insert (see `../../rev-a/case/README.md`,
"Hardware").
