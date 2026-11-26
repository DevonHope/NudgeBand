# NudgeBand assembly guide (band board rev C, case rev D, dock rev D)

- **[nudgeband-assembly-guide-rev-d.pdf](nudgeband-assembly-guide-rev-d.pdf)**: 20-page colour, step-by-step build guide
  (parts list, print list and settings, dock, contact carrier, board wiring, closing the band, strap, first charge).
  Rev D: the band cover and the dock top hook in at one end and swing down onto the screw (no printed alignment pins).
- **[dock-pinout.png](dock-pinout.png)**: the four dock contacts (band wrist side and dock spring pins P1-P4) and the
  bring-up probe points on top of the band, with expected voltages. Also the guide's last page (Debugging).
  Made by `src/pinout.py` from the band and dock KiCad files.
- **[band-rev-c-back-pads.png](band-rev-c-back-pads.png)**: which pads on the back of the band board take the battery
  (TP201 +, TP202 –) and the motor (TP501, TP502). Nets checked against `hardware/band/rev-c/pcb/rigid-rev-c.kicad_pcb`.

## Rebuilding the pictures and the PDF

Everything is generated from the KiCad boards and the case STLs, so it can be re-run after a design change.
From `docs/assembly/src/` (Python 3 with `sexpdata matplotlib pillow`, Node with Playwright and Chromium):

    python3 boardgeo.py ../../../hardware/band/rev-c/pcb/rigid-rev-c.kicad_pcb band.json
    python3 boardgeo.py ../../../hardware/dock/rev-c/pcb/dock-pcb-rev-c.kicad_pcb dock.json
    python3 padmap.py                      # band-rev-c-back-pads.png
    npm install three@0.160.0              # then copy three.module.min.js and examples/jsm/loaders/STLLoader.js (to jsm/) next to render.html
    python3 tilt.py                        # tilted cover / dock top for the closing steps (needs build123d)
    python3 scenes.py                      # scene list -> r/scenes.json (scenes.py writes to r/; adjust as needed)
    node shoot.js r/scenes.json r/out      # renders every picture with three.js in headless Chromium
    python3 pinout.py ../../../hardware/band/rev-c/pcb/rigid-rev-c.kicad_pcb ../dock-pinout.png
    python3 crop.py && cp ../band-rev-c-back-pads.png ../dock-pinout.png img/ && python3 guide.py    # trims the renders, writes guide.html
    node pdf.js $PWD/guide.html $PWD/guide.pdf

The parts are drawn in board coordinates (x = KiCad x, y = −KiCad y, z = 0 at the wrist face), the same frame as the
case scripts, so the case STLs, board, cell, motor, pins and magnets line up without extra placement.
The cell, motor, pins, magnets, screw and insert are simple stand-in shapes at their design positions.
