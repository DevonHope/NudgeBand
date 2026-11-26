# Print plate: Bambu Lab X1C, TPU from the external spool (rev D test, size L)

| File | Parts |
| --- | --- |
| `plate-test-L-lock-and-grip.3mf` | rev D lock strap L + grip strap L side by side across the diagonal, plus 2 grip keepers |
| `preview-plate-test-L.png` | the plate |
| `make_plates.py` | rebuilds the 3MF from the STLs one folder up |

The 3MF holds geometry only (no Bambu profile). Open it in Bambu Studio, answer **Yes** if it asks to
load geometry only, then pick the settings below. One plate prints everything.

## Bambu Studio settings (X1C, 0.4 mm nozzle)

- **Filament:** TPU can't go through the AMS. Load it on the **external spool** holder and feed it
  straight into the toolhead. In Studio, set the filament slot to **External** with the
  **Bambu TPU 95A HF** (or **Generic TPU**) profile. 95A works best, and the lock sizes assume it.
- **Plate:** Textured PEI, no glue. Bed 35 to 45 °C, as the profile sets.
- **Process:** start from **0.20 mm Standard @BBL X1C**, then change:
  - Wall loops **4**
  - Sparse infill **100 %**, pattern **concentric**
  - Supports **off**, brim **off**. Add a 3 mm brim only if a tip lifts.
  - Keep the TPU profile's max volumetric speed. Don't raise it.
- **Before printing:** dry the TPU if the spool has been open a while. Wipe the whole plate, because
  the straps run nearly corner to corner. Watch until the first layer is down along their full length.

Peel the parts off slowly. TPU stretches if you yank it.
