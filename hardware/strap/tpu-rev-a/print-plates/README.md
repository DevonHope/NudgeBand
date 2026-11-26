# Print plates: Bambu Lab X1C, TPU from the external spool

The 3MF files hold the parts already laid out on a 256 x 256 mm plate, centred, flat side down.
They hold geometry only (no Bambu profile). Open one in Bambu Studio, answer **Yes** if it asks to
load geometry only, then pick the settings below.

| File | Parts | Size on plate |
| --- | --- | --- |
| `plate-1-fit-coupon.3mf` | fit coupon (stud strip + hole strip) + 1 keeper | 68 x 50 mm |
| `plate-2-S.3mf` / `-M` / `-L` / `-XL` | one strap in that size: long half, short half, keeper | 121 to 147 x 39 mm |
| `plate-3-all-sizes.3mf` | S, M, L and XL straps + 4 keepers | 147 x 177 mm |
| `make_plates.py` | rebuilds the 3MFs from the STLs one folder up | |

Print the fit coupon first (about 10 min). Then print your size, or all sizes if you're not sure.

## Bambu Studio settings (X1C, 0.4 mm nozzle)

- **Filament:** TPU can't go through the AMS. Load it on the **external spool** holder and feed it
  straight into the toolhead, then in Studio set the filament slot to **External** with the
  **Bambu TPU 95A HF** (or **Generic TPU**) profile. 95A works best; it's what the stud sizes assume.
- **Plate:** Textured PEI. No glue needed. Bed 35 to 45 °C, as the profile sets.
- **Process:** start from **0.20 mm Standard @BBL X1C**, then:
  - Wall loops **3** (the straps are only 2 mm thick, so this makes them nearly all wall)
  - Sparse infill **100 %**, pattern rectilinear (or concentric for a softer strap)
  - Top / bottom shells: leave at the profile's default
  - Supports **off**, brim **off** (the straps are long and flat; add a 3 mm brim only if a tip lifts)
  - Keep the TPU profile's max volumetric speed (about 3.5 to 4 mm³/s for 95A HF). Don't raise it.
- **Before printing:** dry the TPU if it's been open a while (it strings and bubbles when damp).
  Leave flow dynamics calibration on.

After printing, peel the parts off slowly. TPU stretches if you yank it, which would move the holes.
