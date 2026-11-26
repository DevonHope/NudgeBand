"""WakeBand case rev D: the rev C case (../../rev-c/case/case_rev_c.py) with the two printed press-fit
pins at the antenna end replaced by a hook latch.

Rev A to C located the antenna end of the wrist cover with two Ø1.4 mm pins printed on the shell skirt,
pressed into holes in the cover. Small printed pins wear loose and snap, so rev D drops them:
  - the wrist cover's ridge rises 1.6 mm higher across the whole antenna end and round both corners, 1.25 mm
    thick, with a continuous HOOK lip along its top pointing outward by HOOK mm (a 0.6 mm gusset at its root);
  - the shell gets a matching slot with an undercut over the lip: the lip grown by CLR and swept along the
    swing, so the cover swings in and out freely but can't be pulled straight off.
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
                       extrude, import_step, loft, mirror, offset)

A = C.A
A.PIN_Y = ()                        # no press-fit pins (rev A-C had two at y 102.5 and 112.5)

# ------------------------------------------------------------------ hook latch
# The hook is a continuous lip: it follows the cover's ridge across the whole antenna end and wraps round both
# corners (to 52 degrees past the end, where the shell's side wall would get thinner than 0.8 mm outside it).
# Its cross-section, measured outward from the board pocket's edge (offset) and up from the wrist face (z):
#   ridge 0 .. 0.95 from the joint (z 6.0) up; +0.3 mm thicker above the ridge top (45 deg start);
#   hook 0.6 mm further out between z 7.3 and 8.3 (45 deg underside, 0.4 mm tip face, 0.2 mm lead-in);
#   top at z 8.3; inner top edge chamfered 0.35 x 0.8 (clears the shell's antenna-strip posts on the swing);
#   a 0.6 mm 45 deg gusset at the root on the inside (no sharp inner corner).
LIP_T = A.LIP_W + 0.3                      # 1.25 mm thick above the ridge
TONGUE_TOP = 8.3                           # 1.6 mm above the ridge top (B.Cu, 6.7); shell roof inside is 8.8
HOOK = 0.6                                 # overhang outward
HOOK_FLAT = 0.4                            # vertical face at the hook tip
TIP_CH = 0.2                               # lead-in chamfer on the hook's top outer corner
INNER_CH = (0.35, 0.8)                     # inner top chamfer (sideways, down)
ROOT = 0.6                                 # root gusset (45 deg) on the inner face
WRAP = 52                                  # degrees round each corner past the end (the corner arcs' centres are at
CORNER_C = ((101.0, 101.0), (101.0, 114.0))  # the pocket's corner centres)
CLR = 0.15                                 # gap round the lip in the shell's slot
SWEEP = range(0, 62, 2)                    # the slot is the lip's path as the cover swings open, 0 to 60 degrees


def _off(o):
    return A.POCKET if o == 0 else offset(A.POCKET, o, kind=Kind.ARC)


def _loft(o0, z0, o1, z1):
    return loft([Pos(0, 0, z0) * _off(o0), Pos(0, 0, z1) * _off(o1)])


def _window(extra=0.0):
    """plan region of the lip: the antenna end, plus WRAP (+extra) degrees round each corner"""
    (x1, y1), (x2, y2) = CORNER_C
    a1, a2, r = math.radians(180 + WRAP + extra), math.radians(180 - WRAP - extra), 12.0
    p1 = (x1 + r * math.cos(a1), y1 + r * math.sin(a1))
    p2 = (x2 + r * math.cos(a2), y2 + r * math.sin(a2))
    return A.slab(Polygon((x2, y2), p2, (80, p2[1]), (80, p1[1]), p1, (x1, y1), align=None), 0, 12)


def _lip_body():
    zs, zb, zt = A.Z_SKIRT, A.BOARD_B, TONGUE_TOP
    zh = zt - HOOK_FLAT - HOOK                 # hook underside starts (7.3)
    s = (A.slab(_off(A.LIP_W), zs - 0.01, zb + 0.01) + _loft(A.LIP_W, zb, LIP_T, zb + 0.3)
         + A.slab(_off(LIP_T), zb + 0.3, zh) + _loft(LIP_T, zh, LIP_T + HOOK, zh + HOOK)
         + A.slab(_off(LIP_T + HOOK), zh + HOOK, zt - TIP_CH) + _loft(LIP_T + HOOK, zt - TIP_CH, LIP_T + HOOK - TIP_CH, zt))
    s -= A.slab(A.POCKET, 0, 12)
    s -= _loft(0, zt - INNER_CH[1], INNER_CH[0], zt + 0.01)
    return s


def make_tongue():
    """the hook lip on the cover"""
    zs = A.Z_SKIRT
    gusset = A.slab(A.POCKET, zs - 0.01, zs + ROOT) - _loft(-ROOT, zs - 0.02, 0, zs + ROOT + 0.01)
    return (_lip_body() & _window()) + (gusset & _window())


_SLOT = None


def make_slot():
    """the lip's slot in the shell: the lip grown by CLR (union of shifted copies), swept along the swing"""
    global _SLOT
    if _SLOT is None:
        body = _lip_body() & _window(3)
        c, d = CLR, CLR * 0.7071
        grown = None
        for v in ((c, 0, 0), (-c, 0, 0), (0, c, 0), (0, -c, 0), (d, d, 0), (d, -d, 0), (-d, d, 0), (-d, -d, 0),
                  (0, 0, c), (d, 0, d), (-d, 0, d), (0, d, d), (0, -d, d), (0, 0, 0)):
            g = Pos(*v) * body
            grown = g if grown is None else grown + g
        slot = grown
        for th in SWEEP:
            slot += swung(grown, th)
        # square up the slot's inner side (to x 100.15 at the end) so no thin sliver of shell is left between
        # the swept slot and the board pocket
        slot += (A.slab(_off(LIP_T - 0.9), A.Z_SKIRT - 1, TONGUE_TOP + CLR) - A.slab(_off(-0.31), A.Z_SKIRT - 2, 12)) & _window(3)
        _SLOT = slot
    return _SLOT


def make_shell():
    s = C.make_shell() - make_slot()
    for y0, y1 in ((101.1, 103.2), (111.8, 113.9)):          # antenna-strip posts onto F.Cu: kept whole
        s += A.box(A.CAV[0] + 0.3, A.BOARD[0] + 0.95, y0, y1, A.BOARD_F, A.ROOF_IN + 0.1)
    return s


def make_cover():
    return A.make_cover() + make_tongue()


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
    return Pos(0, y1 + grow, 0) * extrude(face, y1 - y0 + 2 * grow, dir=(0, -1, 0))


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
    wall = A.CAV[0] - LIP_T - HOOK - CLR - A.X_A
    print(f"end wall left outside the undercut: {wall:.2f} mm; roof over the slot: {A.TOP - TONGUE_TOP - CLR:.2f} mm")
    moving = cover + board_box()
    print("swing (cover + board opened rocking on the outer edge of the joint at the antenna end):")
    for deg in (1, 2, 4, 6, 8, 10, 15, 20, 25, 30, 40, 50, 60):
        r = shell & swung(moving, deg)
        v = r.volume if r is not None else 0
        print(f"  {deg:>2} deg: overlap {v:.4f} mm3")
    t = make_tongue()
    for deg in (10, 12, 15, 18, 20, 25, 30, 40):           # from which tilt the cover drops straight off the hook
        if all((r := shell & (Pos(0, 0, -0.1 * i) * swung(t, deg))) is None or r.volume < 1e-4 for i in range(1, 31)):
            print(f"hook engages / releases with the cover tilted {deg} deg or more (drops straight off the shell)")
            break
    p = A.to_step_frame(shell); p.label, p.color = "case shell rev D", Color(0.20, 0.22, 0.25)
    export_step(p, str(out / "wakeband-case-rev-d-shell.step"))
    export_stl(p, str(out / "wakeband-case-rev-d-shell.stl"), tolerance=0.01, angular_tolerance=0.1)
    c = A.to_step_frame(cover); c.label, c.color = "case wrist cover rev D", Color(0.85, 0.85, 0.82)
    export_step(c, str(out / "wakeband-case-rev-d-cover.step"))
    export_stl(c, str(out / "wakeband-case-rev-d-cover.stl"), tolerance=0.01, angular_tolerance=0.1)
