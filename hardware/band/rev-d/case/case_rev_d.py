"""WakeBand case rev D: the rev C case (../../rev-c/case/case_rev_c.py) with the two printed press-fit
pins at the antenna end replaced by a hook latch.

Rev A to C located the antenna end of the wrist cover with two Ø1.4 mm pins printed on the shell skirt,
pressed into holes in the cover. Small printed pins wear loose and snap, so rev D drops them:
  - the wrist cover gets a TONGUE at its antenna end (a 10 mm wide wall rising 1.6 mm above the cover
    lip, just outside the board's end edge) with a HOOK at its top pointing outward (-x) by HOOK mm;
  - the shell end wall gets a matching slot with an undercut over the hook (CLR all round).
To close the case, tip the cover in antenna end first so the hook tucks under the shell's undercut, then
swing the motor end down onto the screw boss and fit the M2 screw. The hook moves into the undercut along
the swing, so nothing slides. The screw holds the motor end; the hook holds the antenna end.
Both hook faces under an overhang are 45 degrees, so both parts still print with no supports in the same
orientation as before (shell top face down, cover wrist face down).
Everything else (antenna pocket, dock land, LED skin, screw boss, carrier pocket, magnets) is rev C's.
usage (needs build123d): python case_rev_d.py OUT_DIR [CELL_STEP LRA_STEP]
"""
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "rev-c" / "case"))
import case_rev_c as C  # noqa: E402  (also imports rev A as C.A and applies rev C's dock-land change)
from build123d import (Axis, Color, Kind, Plane, Polygon, Pos, Rot, export_step, export_stl,  # noqa: E402
                       extrude, import_step, mirror, offset)

A = C.A
A.PIN_Y = ()                        # no press-fit pins (rev A-C had two at y 102.5 and 112.5)

# ------------------------------------------------------------------ hook latch
TONGUE_X = (A.CAV[0] - A.LIP_W, A.CAV[0])  # 98.90 .. 99.85: the cover lip's own width, 0.15 mm off the board end
TONGUE_Y = (102.5, 112.5)                  # 10 mm wide, on the straight part of the end wall
TONGUE_TOP = 8.3                           # 1.6 mm above the lip top (B.Cu, 6.7); shell roof inside is 8.8
HOOK = 0.6                                 # overhang toward the outside of the case (-x)
HOOK_FLAT = 0.4                            # vertical face at the hook tip
TIP_CH = 0.2                               # lead-in chamfer on the hook's top outer corner
CLR = 0.15                                 # gap round the tongue and hook in the shell slot


def hook_face(x_out, x_in, z_base, z_top, hook=HOOK, flat=HOOK_FLAT, tip=TIP_CH):
    """Tongue + hook section in the xz plane (as 2D points x, z): a wall from x_out to x_in rising from z_base
    to z_top, with a hook at the top pointing toward x_out (outward) by `hook`. The hook has a `flat` vertical
    tip face, a 45 deg underside back to the tongue and a `tip` lead-in chamfer on its top outer corner."""
    xt = x_out - hook
    return [(x_in, z_base), (x_in, z_top), (xt + tip, z_top), (xt, z_top - tip),
            (xt, z_top - flat), (x_out, z_top - flat - hook), (x_out, z_base)]


def prism(pts, y0, y1, grow=0.0):
    """extrude an xz section from y0 to y1; grow > 0 offsets the section (sharp, mitred corners) and the y ends"""
    face = Polygon(*pts, align=None)
    if grow:
        face = offset(face, grow, kind=Kind.INTERSECTION)
    face = Plane.XZ * face
    return Pos(0, y1 + grow, 0) * extrude(face, y1 - y0 + 2 * grow)


def make_tongue():
    return prism(hook_face(*TONGUE_X, A.BOARD_B - 0.01, TONGUE_TOP), *TONGUE_Y)


def make_slot():
    """the tongue's slot in the shell: CLR all round, run down out of the shell and into the board pocket"""
    x_out, x_in = TONGUE_X
    return prism(hook_face(x_out, x_in + 0.6, A.Z_SKIRT - 1, TONGUE_TOP), *TONGUE_Y, grow=CLR)


def make_shell():
    return C.make_shell() - make_slot()


def make_cover():
    return A.make_cover() + make_tongue()


# ------------------------------------------------------------------ swing check
PIVOT = (A.X_A + 0.3, A.Z_SKIRT)   # where the cover rocks on the shell: the outer edge of the joint at the antenna end
                                   # (both parts have a 0.3 mm chamfer there)


def swung(shape, deg, pivot=PIVOT):
    """the cover side opened by deg: motor end down, turning about a y axis through pivot (x, z)"""
    px, pz = pivot
    return Pos(px, 0, pz) * Rot(0, deg, 0) * Pos(-px, 0, -pz) * shape


def board_box():
    b = A.BOARD
    return A.slab(A.rrect(*b, A.BOARD_R), A.BOARD_B, A.BOARD_F)


if __name__ == "__main__":
    out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    shell, cover = make_shell(), make_cover()
    for part, name in ((shell, "shell"), (cover, "cover")):
        assert len(part.solids()) == 1 and part.is_valid, f"{name}: {len(part.solids())} solids"
        bb = part.bounding_box()
        print(f"{name}: valid, volume {part.volume:.0f} mm3, bbox {[round(v, 2) for v in bb.min]} .. {[round(v, 2) for v in bb.max]}")
    ov = shell & cover
    print("shell vs cover overlap (closed):", round(ov.volume if ov is not None else 0, 4), "(rev C: 0.77, the press-fit pins)")
    tb = make_tongue() & board_box()
    print("tongue vs board:", round(tb.volume if tb is not None else 0, 4))
    pull = shell & (Pos(0, 0, -0.3) * make_tongue())
    print(f"hook holds: tongue pulled 0.3 mm toward the wrist hits the shell by {pull.volume if pull is not None else 0:.3f} mm3 (> 0)")
    wall = TONGUE_X[0] - HOOK - CLR - A.X_A
    print(f"end wall left outside the undercut: {wall:.2f} mm; roof over the slot: {A.TOP - TONGUE_TOP - CLR:.2f} mm")
    moving = cover + board_box()
    print("swing (cover + board opened rocking on the outer edge of the joint at the antenna end):")
    for deg in (1, 2, 3, 4, 6, 8, 10, 12, 15, 20, 25, 30):
        r = shell & swung(moving, deg)
        v = r.volume if r is not None else 0
        print(f"  {deg:>2} deg: overlap {v:.4f} mm3")
    t = make_tongue()
    for deg in (10, 12, 15, 18, 20, 25, 30):           # from which tilt the cover drops straight off the hook
        if all((r := shell & (Pos(0, 0, -0.1 * i) * swung(t, deg))) is None or r.volume < 1e-4 for i in range(1, 31)):
            print(f"hook engages / releases with the cover tilted {deg} deg or more (drops straight off the shell)")
            break
    p = A.to_step_frame(shell); p.label, p.color = "case shell rev D", Color(0.20, 0.22, 0.25)
    export_step(p, str(out / "wakeband-case-rev-d-shell.step"))
    export_stl(p, str(out / "wakeband-case-rev-d-shell.stl"), tolerance=0.01, angular_tolerance=0.1)
    c = A.to_step_frame(cover); c.label, c.color = "case wrist cover rev D", Color(0.85, 0.85, 0.82)
    export_step(c, str(out / "wakeband-case-rev-d-cover.step"))
    export_stl(c, str(out / "wakeband-case-rev-d-cover.stl"), tolerance=0.01, angular_tolerance=0.1)
