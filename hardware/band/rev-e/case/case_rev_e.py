"""WakeBand case rev E: the rev D case (../../rev-d/case/case_rev_d.py) re-sized for the cell actually fitted,
measured 2026-11-26 at 17.25 x 10.0 x 5.05 mm (rev A to D were drawn for a 17 x 13.5 x 5.0 mm envelope), plus
an open DEV shell for bring-up on the dock.

Changes (z = 0 at the wrist face):
  - Magnets: the dock's Ø4 x 1.5 mm discs (rev D: Ø3 x 1) at the same two places, in OPEN-TOP pockets (Ø4.3, 0.2 mm
    skin under them), glued in flush after printing: no print pause. Pocket rims and magnet tops at z 1.7.
  - The cell rests on the magnets and their rims (no foam): cell 1.7 to 6.75. Over it 0.45 mm of room to B.Cu, for
    the extras a real build adds (rev D had 0.05 to 0.2 and didn't close): thin double-sided tape under the cell
    (~0.1), kapton on the board's B side (~0.06), pouch swell / thickness spread (~0.1) and print growth (~0.1).
    So the split (B.Cu) moves from z 6.70 to 7.20.
  - Roof 0.9 mm (rev D 1.2), so the case is only 0.2 mm taller than rev D overall (top 10.2).
  - Contact carrier 0.3 mm higher (floor step z 1.0): band-side pins 0.40 mm compression (rev D 0.60), pin tails
    0.3 mm deeper in the cover (z 0.85), so the dock's pins compress 0.40 mm (rev D 0.70): much less push lifting
    the band off the dock. The dock (rev D) is unchanged.
  - Pin windows in the wrist face Ø2.6 at the face (rev D 2.0) narrowing to Ø1.6 at the carrier (rev D 1.2), so the
    dock plungers find the tails without pressing the band down. Each pair's windows merge at the face.
Cell seat: the side ribs close in to the 10 mm cell (y 102.5 to 112.5) and the end stop moves 0.2 mm toward the
antenna end so the 17.25 mm cell (x 106.75 to 124.0) keeps 0.5 mm from the motor's envelope.

DEV shell (make_dev_shell): the rev E shell with the roof opened over the board so the F-side test pads can be
probed with the band seated and charging on the dock. It keeps everything that holds the board down onto the
spring pins (the dock land over the top pin pair, the post over the bottom pair, the two antenna-strip posts),
the walls, the hook slot and the screw boss, so it fits the cover and the dock exactly like the real shell.

usage (needs build123d): python case_rev_e.py OUT_DIR
"""
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REV_A = HERE.parents[1] / "rev-a" / "case" / "case_rev_a.py"

# ---- rev A's module with rev E's cell numbers, registered before rev C / rev D import it
CELL = (17.25, 10.0, 5.05)                     # measured cell, PCM and tape included (L x W x T)
_PATCH = {
    "CELL_MAX, FOAM, GAP = 5.0, 0.5, 0.2": "CELL_MAX, FOAM, GAP = 5.05, 0.7, 0.45   # rev E: cell on the magnets (top z 1.7); 0.45 mm room over it",
    "ROOF = 1.2": "ROOF = 0.9   # rev E: thinner roof keeps the case 10.2 mm tall",
    "MAG_D, MAG_T = 3.0, 1.0": "MAG_D, MAG_T = 4.0, 1.5   # rev E: the dock's Ø4 x 1.5 mm magnets",
    "CARRIER_Z = 0.7  ": "CARRIER_Z = 1.0  ",
    "WIN_D0, WIN_D1 = 2.0, 1.2": "WIN_D0, WIN_D1 = 2.6, 1.6   # rev E: wider pin windows",
    "c += cyl(x, y, MAG_POCKET_D / 2 + 0.6, FLOOR - 0.01, MAG_SKIN + MAG_POCKET_T + 0.25)\n        c -= cyl(x, y, MAG_POCKET_D / 2, MAG_SKIN, MAG_SKIN + MAG_POCKET_T)":
        "c += cyl(x, y, MAG_POCKET_D / 2 + 0.6, FLOOR - 0.01, MAG_SKIN + MAG_T)\n        c -= cyl(x, y, MAG_POCKET_D / 2, MAG_SKIN, MAG_SKIN + MAG_T + 1)   # rev E: open-top pocket, magnet glued in flush",
    "CELL_ENV = (107.0, 124.0, 100.75, 114.25)": "CELL_ENV = (106.75, 124.0, 102.5, 112.5)   # rev E: 17.25 x 10 cell",
    "c += box(105.6, 106.8, 102.0, 113.0, FLOOR, FLOOR + 1.5)": "c += box(105.4, CELL_ENV[0] - CLR, 102.0, 113.0, FLOOR, FLOOR + 1.5)",
}
_src = REV_A.read_text()
for old, new in _PATCH.items():
    assert _src.count(old) == 1, old
    _src = _src.replace(old, new)
_spec = importlib.util.spec_from_loader("case_rev_a", loader=None, origin=str(REV_A))
A = importlib.util.module_from_spec(_spec)
A.__file__ = str(REV_A)
exec(compile(_src, str(REV_A), "exec"), A.__dict__)
sys.modules["case_rev_a"] = A

sys.path.insert(0, str(HERE.parents[1] / "rev-d" / "case"))
import case_rev_d as D  # noqa: E402  (imports rev C, which picks up the patched rev A above)
from build123d import Color, Pos, export_step, export_stl  # noqa: E402

assert D.A is A and abs(A.BOARD_B - 7.20) < 1e-9, A.BOARD_B
assert abs(A.MAG_POCKET_D - 4.3) < 1e-9
# rev D wrote two heights as numbers for its B.Cu at 6.7: keep them 1.6 / 0.8 mm above the new split
D.TONGUE_TOP = A.BOARD_B + 1.6                 # hook lip top (rev D 8.3), roof over its slot stays 1.55 mm
D.LED_SIDE_Z = (A.BOARD_F, A.BOARD_F + 0.8)    # LED side window (rev D 7.5 to 8.3)

make_shell, make_cover, make_tongue = D.make_shell, D.make_cover, D.make_tongue

# ---- dev shell: probe windows in the roof
# Main window over the board from just past the antenna-strip posts to the dock land (which starts at x 127.6),
# then a second window between the land (y <= 103.2) and the post (y >= 110.8) reaching TP203 / TP707 at x 131.6.
DEV_WIN = (101.3, 127.3, 100.45, 114.55)        # x0, x1, y0, y1 (rounded corners)
DEV_WIN2 = (126.8, 132.55, 103.65, 110.35)      # beside the end wall, between the land and the post
DEV_WIN3 = (126.8, 131.4, 103.65, 114.55)       # over the charge LED (x 129 to 131.4), clear of the post at x 131.75
DEV_R = 1.0


def make_dev_shell():
    s = make_shell()
    z0, z1 = A.BOARD_F + A.F_PARTS + 0.05, A.TOP + 1      # cut from just over the parts, so the land / posts stay whole
    s -= A.slab(A.rrect(*DEV_WIN, DEV_R), z0, z1)
    s -= A.slab(A.rrect(*DEV_WIN2, 0.5), z0, z1)
    s -= A.slab(A.rrect(*DEV_WIN3, 0.5), z0, z1)
    return s


def cell_box():
    x0, x1, y0, y1 = A.CELL_ENV
    z = A.MAG_SKIN + A.MAG_T
    return A.box(x0, x1, y0, y1, z, z + CELL[2])


def lra_cyl():
    return A.cyl(*A.LRA_C, A.LRA_ENV_R, A.PART_FACE - A.LRA_H, A.PART_FACE)


def _v(x):
    return round(x.volume, 4) if x is not None else 0


if __name__ == "__main__":
    out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    shell, cover, dev = make_shell(), make_cover(), make_dev_shell()
    for part, name in ((shell, "shell"), (cover, "cover"), (dev, "dev shell")):
        assert len(part.solids()) == 1 and part.is_valid, f"{name}: {len(part.solids())} solids"
        bb = part.bounding_box()
        print(f"{name}: valid, volume {part.volume:.0f} mm3, bbox {[round(v, 2) for v in bb.min]} .. {[round(v, 2) for v in bb.max]}")
    cell, lra, board = cell_box(), lra_cyl(), D.board_box()
    print(f"stack: magnets / domes top {A.MAG_SKIN + A.MAG_T:.2f}, cell top {cell.bounding_box().max.Z:.2f}, "
          f"B.Cu {A.BOARD_B:.2f}, F.Cu {A.BOARD_F:.2f}, roof inside {A.ROOF_IN:.2f}, top {A.TOP:.2f}")
    zf = A.CARRIER_Z + A.CARRIER_T
    print(f"band spring pins: free tip {zf + A.SP_A:.2f}, compression {zf + A.SP_A - A.BOARD_B:.2f} of {A.SP_STROKE}; "
          f"tails at z {zf - A.SP_TAIL:.2f} (rev D 0.55): dock pins compress {0.70 - (zf - A.SP_TAIL - 0.55):.2f} of 1.40 (rev D 0.70)")
    for n, a in (("cell", cell), ("LRA", lra), ("board", board)):
        for m, b in (("shell", shell), ("cover", cover), ("dev shell", dev)):
            print(f"  {n} vs {m}: {_v(a & b)}")
    print("cell vs LRA:", _v(cell & lra), " cell vs board:", _v(cell & board))
    print("shell vs cover:", _v(shell & cover), " dev shell vs cover:", _v(dev & cover))
    pull = dev & (Pos(0, 0, -0.3) * make_tongue())
    print(f"dev shell hook holds (tongue pulled 0.3 mm): {_v(pull)} mm3 (> 0)")
    moving = cover + board
    worst = max(_v(dev & D.swung(moving, d)) for d in (1, 4, 10, 20, 30, 40, 60))
    print("dev shell swing check, worst overlap 1-60 deg:", worst)
    names = (("shell", shell, Color(0.20, 0.22, 0.25), "case shell rev E"),
             ("cover", cover, Color(0.85, 0.85, 0.82), "case wrist cover rev E"),
             ("dev-shell", dev, Color(0.95, 0.55, 0.10), "dev shell rev E (open, for probing)"))
    for name, part, col, label in names:
        p = A.to_step_frame(part); p.label, p.color = label, col
        export_step(p, str(out / f"wakeband-case-rev-e-{name}.step"))
        export_stl(p, str(out / f"wakeband-case-rev-e-{name}.stl"), tolerance=0.01, angular_tolerance=0.1)
