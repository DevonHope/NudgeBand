# WakeBand hardware

Everything is grouped by **what it is** (band or dock), then **revision**, then **PCB or printed case**:
every revision folder carries its own `pcb/` and its own `case/` (the models to print).
Build **rev D**: the rev C boards (rev B plus the 2026-11-08 review fixes; every part assembled by JLCPCB) with
printed parts that close with a hook latch instead of printed alignment pins. Rev A to rev C are kept unchanged
for reference: a new revision always gets its own folder.

```
hardware/
├── band/                    the wristband
│   ├── rev-a/
│   │   ├── pcb/             rigid band board, ISP2454 module (rigid-rev-a.kicad_pro)
│   │   ├── case/            shell + wrist cover (print)
│   │   └── contact-carrier/ small PCB holding the 4 spring pins in the cover, + BUY-LIST.md
│   ├── rev-b/               superseded by rev C (as reviewed on 2026-11-08)
│   │   ├── pcb/             rigid band board, nRF54L10 bare chip (rigid-rev-b.kicad_pro)
│   │   ├── case/            rev B shell + wrist cover
│   │   └── contact-carrier/ same carrier as rev A
│   ├── rev-c/               rev B + 2026-11-08 review fixes
│   │   ├── pcb/             rigid band board (rigid-rev-c.kicad_pro)
│   │   ├── case/            shell + wrist cover, same geometry as rev B
│   │   └── contact-carrier/ same carrier as rev A and rev B
│   ├── rev-d/               build this: rev C board, case with a hook latch instead of press-fit pins
│   │   ├── pcb/             copy of rev C's board (unchanged)
│   │   ├── case/            shell + wrist cover rev D (print)
│   │   └── contact-carrier/ same carrier as rev A to C
│   └── archive/flex-rev-a/  early flex-PCB design (not built)
├── dock/                    the charging / programming dock
│   ├── rev-a/
│   │   ├── pcb/             dock PCB (dock-pcb-rev-a.kicad_pro)
│   │   └── case/            dock housing rev A (superseded)
│   ├── rev-b/               superseded by rev C (as reviewed on 2026-11-08)
│   │   ├── pcb/             dock PCB, rev A circuit, stocked pins (dock-pcb-rev-b.kicad_pro)
│   │   └── case/            dock housing rev B
│   ├── rev-c/               rev B + 2026-11-08 review fixes
│   │   ├── pcb/             dock PCB with pin ESD, decoupling, no vias under paste (dock-pcb-rev-c.kicad_pro)
│   │   └── case/            dock housing rev C (plate held by two printed pins)
│   └── rev-d/               build this: rev C PCB, housing with a hook lip + snap clip
│       ├── pcb/             copy of rev C's dock PCB (unchanged)
│       └── case/            dock housing rev D (print)
├── reviews/                 design reviews (latest: 2026-11-08, two advisors per board)
├── print-plates/x1c-rev-d/ X1C test plate: rev D band case + dock in one PETG 3MF
├── strap/                   strap sewing patterns + printable TPU strap (tpu-rev-a)
└── tools/                   printcheck.py (printability check for the printed parts)
```

## What to order and print (rev D)

| What | Where | How |
| --- | --- | --- |
| Band PCB, assembled | [`band/rev-c/pcb/fab/jlcpcb/`](band/rev-c/pcb/fab/jlcpcb) | JLCPCB Standard PCBA (rev D uses the rev C boards), 2 panels of 2 x 2 (see its README, "Ordering") |
| Contact carrier PCB | [`band/rev-c/contact-carrier/fab/`](band/rev-c/contact-carrier/fab) | bare PCB, panel of 6, 1.6 mm |
| Dock PCB, assembled | [`dock/rev-c/pcb/fab/dock-pcb-rev-c-fab.zip`](dock/rev-c/pcb/fab) | JLCPCB, top side (BOM + CPL inside the zip) |
| Spring pins, magnets, feet, glue | [`band/rev-a/contact-carrier/BUY-LIST.md`](band/rev-a/contact-carrier/BUY-LIST.md) | Mouser, Indigo |
| Band shell | [`band/rev-d/case/wakeband-case-rev-d-shell.stl`](band/rev-d/case) | PETG, top face down, no supports |
| Wrist cover | [`band/rev-d/case/wakeband-case-rev-d-cover.stl`](band/rev-d/case) | PETG, wrist face down, pause at z 1.35 mm for the magnets |
| Dock top plate and tray | [`dock/rev-d/case/`](dock/rev-d/case) (`-top.stl`, `-tray.stl`) | PETG, flat faces down, no supports; no screws |
| All four on one X1C plate | [`print-plates/x1c-rev-d/`](print-plates/x1c-rev-d) | PETG 3MF, parts already oriented; same pause at z 1.35 mm |
| Strap | [`strap/`](strap) | sewing pattern PDFs; TPU printed strap STLs in `strap/tpu-rev-a` |

Each folder's README has the details: firmware notes and antenna tuning (band PCB), assembly (case),
flashing the dock and programming the band (dock PCB).
