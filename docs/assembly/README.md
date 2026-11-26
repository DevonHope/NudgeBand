# NudgeBand assembly guide (band rev C, case rev C, dock rev C)

- **[nudgeband-assembly-guide-rev-c.pdf](nudgeband-assembly-guide-rev-c.pdf)**: 19-page colour, step-by-step build guide
  (parts list, print list and settings, dock, contact carrier, board wiring, closing the band, strap, first charge).
- **[band-rev-c-back-pads.png](band-rev-c-back-pads.png)**: which pads on the back of the band board take the battery
  (TP201 +, TP202 –) and the motor (TP501, TP502). Nets checked against `hardware/band/rev-c/pcb/rigid-rev-c.kicad_pcb`.

## Rebuilding the pictures and the PDF

Everything is generated from the KiCad boards and the case STLs, so it can be re-run after a design change.
From `docs/assembly/src/` (Python 3 with `sexpdata matplotlib pillow`, Node with Playwright and Chromium):

    python3 boardgeo.py ../../../hardware/band/rev-c/pcb/rigid-rev-c.kicad_pcb band.json
    python3 boardgeo.py ../../../hardware/dock/rev-c/pcb/dock-pcb-rev-c.kicad_pcb dock.json
    python3 padmap.py                      # band-rev-c-back-pads.png
    npm install three@0.160.0              # then copy three.module.min.js and examples/jsm/loaders/STLLoader.js (to jsm/) next to render.html
    python3 scenes.py                      # scene list -> r/scenes.json (scenes.py writes to r/; adjust as needed)
    node shoot.js r/scenes.json r/out      # renders every picture with three.js in headless Chromium
    python3 crop.py && python3 guide.py    # trims the renders, writes guide.html
    node pdf.js $PWD/guide.html $PWD/guide.pdf

The parts are drawn in board coordinates (x = KiCad x, y = −KiCad y, z = 0 at the wrist face), the same frame as the
case scripts, so the case STLs, board, cell, motor, pins and magnets line up without extra placement.
The cell, motor, pins, magnets, screw and insert are simple stand-in shapes at their design positions.
