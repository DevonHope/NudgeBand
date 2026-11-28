"""Fit check: band case rev E (wrist cover) seated on the UNCHANGED dock rev D.
Reads the exported STEPs (both in the same output frame: y = -KiCad y, z = 0 at the band's wrist face) and builds
the dock's four spring pins (Mill-Max 0906-4-15-20-75-14-11-0) and its magnets from the dock scripts' numbers.
usage (needs build123d): python fit_dock_rev_e.py   (run from this folder)
"""
from pathlib import Path
from build123d import Pos, Cylinder, Cone, Align, import_step

HERE = Path(__file__).resolve().parent
DOCK = HERE.parents[2] / "dock" / "rev-d" / "case"

# band rev E (from case_rev_e.py)
SP_X, SP_Y = 131.5, (101.1, 103.3, 111.7, 113.9)
TAIL_E = 0.9 + 1.6 - 1.75             # band pin tails, rev E (rev D 0.55)
WIN_D0, WIN_D1, WIN_Z1 = 2.6, 1.6, 0.9
MAG_E = (0.2, 1.7)                    # band magnets z (Ø4 x 1.5)
MAG_XY = ((112.5, 107.5), (120.5, 107.5))
# dock rev D (dock_rev_a / dock_rev_c numbers; unchanged)
D_SP_A, D_BODY_L, D_STROKE, D_PLUNGER_D, D_BODY_D = 5.99, 2.69, 1.40, 1.07, 1.50
D_PCB_TOP = 0.55 + 0.70 - D_SP_A      # designed for mid-stroke on rev D's tails at z 0.55
D_MAG = (-0.2 - 1.5 - 0.02, -0.2 - 0.02)
REC_CLR = 0.15


def cyl(x, y, d, z0, z1):
    return Pos(x, -y, z0) * Cylinder(d / 2, z1 - z0, align=(Align.CENTER, Align.CENTER, Align.MIN))


def vol(s):
    return round(s.volume, 4) if s is not None else 0


cover = import_step(str(HERE / "wakeband-case-rev-e-cover.step"))
top = import_step(str(DOCK / "wakeband-dock-rev-d-top.step"))
tray = import_step(str(DOCK / "wakeband-dock-rev-d-tray.step"))
for n, s in (("cover", cover), ("dock top", top), ("dock tray", tray)):
    bb = s.bounding_box()
    print(f"{n}: bbox {[round(v, 2) for v in bb.min]} .. {[round(v, 2) for v in bb.max]}")

free_tip = D_PCB_TOP + D_SP_A
comp = free_tip - TAIL_E
print(f"\ndock pin: seat z {D_PCB_TOP:.2f}, free tip z {free_tip:.2f}; band tail z {TAIL_E:.2f} (rev D 0.55)")
print(f"dock pin compression seated: {comp:.2f} of {D_STROKE} (rev D 0.70); left before bottoming {D_STROKE - comp:.2f}")
print(f"band reaches the pins (first contact) when its wrist face is {free_tip - TAIL_E:.2f} mm above its seat")

# window clearance round the plunger at the depth it reaches
for z in (0.0, TAIL_E):
    d = WIN_D0 + (WIN_D1 - WIN_D0) * min(z, WIN_Z1) / WIN_Z1
    print(f"window at z {z:.2f}: dia {d:.2f}, radial clearance round the Ø{D_PLUNGER_D} plunger {(d - D_PLUNGER_D) / 2:.2f} "
          f"(band can sit off-centre by up to the recess clearance {REC_CLR})")
d_d = 2.0 + (1.2 - 2.0) * 0.55 / 0.7
print(f"  rev D for comparison: window at its tail z 0.55 dia {d_d:.2f}, clearance {(d_d - D_PLUNGER_D) / 2:.2f}")

pins = None
for y in SP_Y:   # compressed: body from the seat, plunger up to the tail
    p = cyl(SP_X, y, D_BODY_D, D_PCB_TOP, D_PCB_TOP + D_BODY_L) + cyl(SP_X, y, D_PLUNGER_D, D_PCB_TOP + D_BODY_L - 0.01, TAIL_E)
    pins = p if pins is None else pins + p
pins_off = None  # same, with the band shifted by the full recess clearance in x and y
for y in SP_Y:
    p = cyl(SP_X + REC_CLR, y + REC_CLR, D_PLUNGER_D, 0.0, TAIL_E)
    pins_off = p if pins_off is None else pins_off + p
dmag = None
bmag = None
for x, y in MAG_XY:
    m = cyl(x, y, 4.0, *D_MAG); dmag = m if dmag is None else dmag + m
    b = cyl(x, y, 4.0, *MAG_E); bmag = b if bmag is None else bmag + b

print("\nclashes, band seated (want 0):")
for n, a in (("dock spring pins", pins), ("dock pins, band 0.15 mm off-centre", pins_off), ("dock magnets", dmag),
             ("dock top", top), ("dock tray", tray)):
    print(f"  {n} vs band cover: {vol(a & cover)}")
print(f"  band magnets vs cover: {vol(bmag & cover)}  (glued into open pockets)")
print(f"magnet faces: band {MAG_E[0]:.2f}, dock {D_MAG[1]:.2f}: gap {MAG_E[0] - D_MAG[1]:.2f} mm (0.2 + 0.2 skins + 0.02)")

if __name__ == "__main__":
    import sys
    from build123d import export_step
    if len(sys.argv) > 1:   # write the stand-in parts for a CAD fit check (SolidCraft etc.)
        out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
        export_step(pins, str(out / "fit-dock-rev-d-spring-pins-on-rev-e.step"))
        export_step(dmag, str(out / "fit-dock-rev-d-magnets.step"))
        export_step(bmag, str(out / "fit-band-rev-e-magnets.step"))
        print("wrote fit-check STEPs to", out)
