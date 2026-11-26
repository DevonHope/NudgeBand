# Test plate: Bambu Lab X1C, PETG (rev D band case + rev D dock)

| File | Parts |
| --- | --- |
| `plate-rev-d-band-and-dock-petg.3mf` | band case rev D shell + cover, dock rev D top plate + tray, each already turned to its print orientation |
| `preview-plate-rev-d.png` | the plate from above |
| `make_plate.py` | rebuilds the 3MF from the STLs in `../../band/rev-d/case` and `../../dock/rev-d/case` |

| Part | Orientation | Height |
| --- | --- | --- |
| Band shell | top face down | 6.5 mm |
| Band cover | wrist face down | 8.3 mm |
| Dock top plate | flat underside down | 3.25 mm |
| Dock tray | floor down | 8.0 mm |

The 3MF holds geometry only (no Bambu profile). Open it in Bambu Studio, answer **Yes** if it asks to load
geometry only, then set the following.

## Bambu Studio settings (X1C, 0.4 mm nozzle)

- **Filament:** PETG (Bambu PETG HF or Generic PETG) from the AMS.
- **Plate:** Textured PEI. Use glue stick on smooth PEI, because PETG can bond too hard to it.
- **Process:** **0.20 mm Standard @BBL X1C**, then wall loops **3**, supports **off**, brim **off**.
- **Magnet pause:** in the preview, right-click the layer slider at **z 1.4 mm** (the first layer above
  1.35 mm) and add a **pause**. When it stops, drop the 2 Ø3 x 1 mm magnets into the band cover pockets,
  facing so they attract the dock's magnets, and resume. The pause stops the whole plate, which doesn't hurt the other
  parts. The dock's magnet pockets open underneath, so its magnets go in after printing.

## What to check after printing

- Band: the cover's hook lip goes in at the antenna end, swings down flat, and the M2 x 6 screw closes the
  motor end. If the lip won't go in, set `CLR` to 0.2 in `case_rev_d.py` and reprint the shell only.
- Dock: the plate's left end hooks over the tray's back-left hook at about 50 degrees, and the right end
  snaps down on the clip. Pulling the right end up firmly should release it.
- The magnets sit snug in their 0.15 mm-clearance pockets, and the dock's LED sight holes line up with the LEDs.
