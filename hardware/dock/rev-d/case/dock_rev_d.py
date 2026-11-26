"""WakeBand dock rev D: the rev C dock (../../rev-c/case/dock_rev_c.py) with the two printed locating pins
replaced by a hook lip at the left end and a snap clip at the right end (no screw).

Rev C held the top plate on the tray by friction on two Ø2 mm pins printed on the tray. Rev D:
  - a TONGUE (hook lip) rises from the tray's back-left end block and follows the corner, with a HOOK at its top
    pointing outward (-x); the top plate has a matching slot with an undercut (CLR all round, the band case's hook
    profile). Tipping the plate on its left edge swings the undercut clear of the hook. A second hook at the
    front-left would not work (that corner is a thin curved strip between the outline, recess and strap channel);
    the front edge rests on the tray;
  - at the right-hand back corner a SNAP CLIP (2026-11-26, replacing an M2 screw and nut): a flexible wall printed
    inside a pocket in the plate (joined only at its back end, so it bends sideways with the stress along the
    layers) carries a small hook that snaps under the lip of a post on the tray;
  - status-LED sight holes through the tray's back wall, and strap channels 0.45 mm narrower each side so the plate
    rims at the corners print one line thicker (2026-11-26).
To fit the plate: tip it in left end first so the lip goes under the plate's undercut, then press the right end
down until the clip snaps. To open: pull the right end up firmly, then lift the plate off the lip.
Both parts still print with no supports, as rev C (plate underside down, tray floor down).
usage (needs build123d): python dock_rev_d.py OUT_DIR [DOCK_PCB_STEP]"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "rev-c" / "case"))
sys.path.insert(0, str(HERE.parents[2] / "band" / "rev-d" / "case"))
import dock_rev_c as C  # noqa: E402
import case_rev_d as band_d  # noqa: E402  (hook profile)
from build123d import (Axis, Color, Plane, Polygon, Pos, Rot, export_step,  # noqa: E402
                       export_stl, extrude, revolve)

case = C.case
A = C.A
DOCK = C.DOCK

C.LOC_PINS = ()                                   # no printed locating pins
C.MAG_POCKET_D = C.MAG_D + 2 * band_d.MAG_FIT  # 4.3: 0.15 mm round the 4 x 1.5 mm magnets (rev C 4.1);
# the pocket is open below (magnets glued in from underneath), so the magnet still sits against the 0.2 mm skin
# rubber feet: back at rev C's positions (the 2026-11-26 screw that pushed them 4 mm inward is gone)
# strap channels 0.45 mm narrower each side (one extrusion line, 2026-11-26): the plate rims beside the channels at
# the four corners printed too thin. 17.7 mm still leaves 0.85 mm each side of the 16 mm strap.
C.STRAP_W = 18.6 - 2 * 0.45

# ------------------------------------------------------------------ hooks (left end)
HOOK, HOOK_FLAT, TIP_CH, CLR = band_d.HOOK, band_d.HOOK_FLAT, band_d.TIP_CH, band_d.CLR
# The hook is a lip that follows the back-left corner of the outline (centre CORNER, radius 7): a short straight run
# on the left face (y 117.95 to 118.6, between the strap channel's rounded lip and the corner) and then WRAP degrees
# round the corner, at a constant inset, so the plate keeps at least 0.8 mm outside the slot everywhere.
CORNER = (DOCK[0] + C.DOCK_R, DOCK[3] - C.DOCK_R)  # (96.35, 118.6)
R_IN, R_OUT = 3.9, 5.15                           # lip 1.25 mm thick; hook tip at r 5.75, slot to r 5.9 (outline r 7)
STRAIGHT_Y0 = 117.95                              # start of the straight run (clear of the channel's lip round)
WRAP = 52                                         # degrees round the corner (as on the band)
TONGUE_H = 1.85                                   # above the joint (-2.05); slot top -0.05: 1.25 mm of plate over it
ROOT = 0.6                                        # 45 deg gusset on the lip's inner root
Z0 = C.PLATE_Z0                                   # joint plane (-2.05)
SWEEP = range(0, 72, 2)                           # the slot is the lip's path as the plate swings open, 0 to 70 deg


def _profile(root=True):
    """lip section (x, z) on the line y = CORNER[1], hook pointing to -x (outward)"""
    cx = CORNER[0]
    p = band_d.hook_face(cx - R_OUT, cx - R_IN, Z0 - 0.01, Z0 + TONGUE_H, HOOK, HOOK_FLAT, TIP_CH)
    if root:
        p = [(cx - R_IN + ROOT, Z0 - 0.01), (cx - R_IN, Z0 + ROOT)] + p[1:]
    return Polygon(*p, align=None)


def _lip(root=True, profile=None):
    cx, cy = CORNER
    prof = profile if profile is not None else _profile(root)
    face = Pos(0, cy, 0) * (Plane.XZ * prof)
    arc = revolve(face, Axis((cx, cy, 0), (0, 0, 1)), WRAP)
    if arc.bounding_box().max.Y < cy + 0.5:                  # revolve the other way if it went toward -y
        arc = revolve(face, Axis((cx, cy, 0), (0, 0, 1)), -WRAP)
    straight = Pos(0, cy, 0) * extrude(Plane.XZ * prof, cy - STRAIGHT_Y0)
    if straight.bounding_box().min.Y > cy - 0.1:
        straight = Pos(0, cy, 0) * extrude(Plane.XZ * prof, -(cy - STRAIGHT_Y0))
    return arc + straight


def tongues():
    return _lip()


_SLOT = None


def slots():
    """the lip grown by CLR (union of shifted copies), swept along the plate's swing"""
    global _SLOT
    if _SLOT is None:
        body = _lip()
        c, d = CLR, CLR * 0.7071
        grown = None
        for v in ((c, 0, 0), (-c, 0, 0), (0, c, 0), (0, -c, 0), (d, d, 0), (d, -d, 0), (-d, d, 0), (-d, -d, 0),
                  (0, 0, c), (d, 0, d), (-d, 0, d), (0, d, d), (0, -d, d), (0, 0, 0)):
            g = Pos(*v) * body
            grown = g if grown is None else grown + g
        slot = grown
        for th in SWEEP:
            slot += swung(grown, -th)                # the plate turns, so the lip moves the other way relative to it
        # square up the slot's inner side (a vertical wall at r 2.9) so the swept surface leaves no overhang in the
        # plate, which prints underside down
        cx = CORNER[0]
        r0, z1 = R_IN - ROOT - 0.4, Z0 + TONGUE_H + CLR
        box = Polygon((cx - R_IN, Z0 - 1), (cx - R_IN, z1), (cx - r0, z1), (cx - r0, Z0 - 1), align=None)
        slot += _lip(profile=box) + Pos(0, CLR, 0) * _lip(profile=box) + Pos(0, -CLR, 0) * _lip(profile=box)
        _SLOT = slot
    return _SLOT


# ------------------------------------------------------------------ snap clip (right end, 2026-11-26)
# Replaces rev D's M2 screw and nut. A flexible WALL is printed inside a pocket in the plate's back-right block:
# it stands on the plate underside (on the bed), is joined to the pocket only at its back end (y CLIP_Y1) and is free
# on every other side, so it bends sideways (in x) like a leaf, with the bending stress running along the printed
# layers rather than across them. A small HOOK on its free end points +x. A rigid POST on the tray's end block rises
# into the same pocket with a LIP pointing -x that sits over the hook when closed. Swing the plate down and the hook's
# chamfer rides over the lip's chamfer, bends the wall 0.5 mm in and snaps under the lip; pull the right end up
# firmly and the two 45 deg faces push the wall in again and let go.
CLIP_Y0, CLIP_Y1 = 118.6, 123.8                   # wall free end / root (5.2 mm free length)
CLIP_HOOK_Y1 = 121.0                              # hook and post along y 118.6 to 121.0
WALL_X0, WALL_X1 = 142.6, 143.6                   # 1.0 mm wall (two lines plus)
HOOK_X = WALL_X1 + 0.5                            # hook tip 144.1
POCKET = (142.0, 145.6, 118.3, CLIP_Y1, 0.4)      # x0, x1, y0, y1, roof (0.8 mm of plate over it)
POCKET_NECK = (CLIP_HOOK_Y1 + 0.3, WALL_X1 + 0.3)  # behind the post the pocket narrows to x 143.9 (keeps 1.7 mm to the round corner)
POST_X0, POST_X1 = HOOK_X + CLR, 145.4             # tray post (gap 0.15 to the hook tip, 0.2 to the pocket wall)
LIP_X0 = WALL_X1 + CLR                             # lip reaches in to 143.75: 0.35 mm over the hook
CLIP_TOP = -0.6                                   # top of the post


def _xz_prism(pts, y0, y1):
    """polygon in the xz plane (x, z points) extruded along y from y0 to y1"""
    poly = Polygon(*pts, align=None)
    f = Pos(0, y1, 0) * (Plane.XZ * poly)
    e = extrude(f, y1 - y0)
    if e.bounding_box().min.Y > y0 + 0.01:
        e = extrude(f, -(y1 - y0))
    return e


def hook_profile():
    # hook on the wall: 45 deg chamfer on its bed-side outer edge (lead-in) and a 45 deg top face (retention)
    return [(WALL_X1 - 0.01, Z0), (WALL_X1 + 0.2, Z0), (HOOK_X, Z0 + 0.3), (WALL_X1 - 0.01, Z0 + 0.3 + HOOK_X - WALL_X1 + 0.01)]


def post_profile():
    # post with a lip over the hook: 45 deg underside parallel to the hook's top face, CLR above it; 45 deg lead-in on top
    zr = Z0 + 0.3 + CLR * 1.4142                  # lip underside at the hook tip's x
    return [(POST_X0, Z0 - 0.01), (POST_X1, Z0 - 0.01), (POST_X1, CLIP_TOP), (LIP_X0 + 0.15, CLIP_TOP),
            (LIP_X0, CLIP_TOP - 0.15), (LIP_X0, zr + (HOOK_X - LIP_X0)), (POST_X0, zr - (POST_X0 - HOOK_X))]


def clip_wall():
    w = case.box(WALL_X0, WALL_X1, CLIP_Y0, CLIP_Y1 + 0.01, Z0, POCKET[4] - 0.3)
    return w + _xz_prism(hook_profile(), CLIP_Y0, CLIP_HOOK_Y1)


def clip_pocket():
    x0, x1, y0, y1, zr = POCKET
    yn, xn = POCKET_NECK
    return case.box(x0, x1, y0, yn, Z0 - 1, zr) + case.box(x0, xn, y0, y1, Z0 - 1, zr)


def clip_post():
    return _xz_prism(post_profile(), CLIP_Y0, CLIP_HOOK_Y1)


LED_HOLE_D, LED_HOLE_Z = 1.6, -4.0                # status-LED sight holes through the tray's back wall (LED top ~ -4.1)


def make_top():
    return C.make_top() - slots() - clip_pocket() + clip_wall()


def make_tray():
    t = C.make_tray() + tongues() + clip_post()
    for x, y in A.LEDS:                                   # sight holes: look straight at the LEDs from the back
        t -= C.ycyl(x, LED_HOLE_Z, LED_HOLE_D / 2, y, DOCK[3] + 1)
    return t

# ------------------------------------------------------------------ swing check
PIVOT = (DOCK[0] + C.SEAM_CH, Z0)                 # the plate rocks on the tray's left outer edge (0.35 mm seam chamfer)


def swung(shape, deg):
    """plate opened by deg: right end up, turning about a y axis through PIVOT"""
    px, pz = PIVOT
    return Pos(px, 0, pz) * Rot(0, -deg, 0) * Pos(-px, 0, -pz) * shape


def make_top_deflected(dx=-0.4):
    """the plate with its clip wall bent dx in x (as it is while the hook rides over the lip)"""
    return C.make_top() - slots() - clip_pocket() + Pos(dx, 0, 0) * clip_wall()


if __name__ == "__main__":
    out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    top, tray = make_top(), make_tray()
    pcb, pins, mags = C.make_inside()
    ok = True
    for name, s in (("top", top), ("tray", tray)):
        good = len(s.solids()) == 1 and s.is_valid
        ok &= good
        bb = s.bounding_box()
        print(f"{name}: solids {len(s.solids())} valid {s.is_valid} volume {s.volume:.0f} mm3 "
              f"bbox {[round(v, 2) for v in bb.min]} {[round(v, 2) for v in bb.max]}")
    r = top & tray
    print("top vs tray overlap (closed):", round(r.volume if r is not None else 0, 4))
    cover = case.make_cover()
    hits = []
    for n, a in (("pcb envelope", pcb), ("spring pins", pins), ("magnets", mags)):
        for m, b in (("top", top), ("tray", tray), ("band cover", cover)):
            if m == "band cover" and n == "pcb envelope":
                continue
            v = (a & b)
            v = v.volume if v is not None else 0
            if v > 1e-4:
                hits.append((n, m, round(v, 4)))
    print(f"clash check (closed): {len(hits)} overlaps", hits)
    for m, b in (("top", top), ("tray", tray)):
        r = b & cover
        print(f"band cover vs {m}:", round(r.volume if r is not None else 0, 4))
    pull = top & (Pos(0, 0, -0.3) * tongues())
    print(f"hook holds: tongue 0.3 mm further down hit the plate by {pull.volume if pull is not None else 0:.3f} mm3 (> 0)")
    post = clip_post()
    pull = (Pos(0, 0, 0.3) * clip_wall()) & post
    print(f"clip holds: wall lifted 0.3 mm hits the post by {pull.volume if pull is not None else 0:.3f} mm3 (> 0)")
    for dx in (-0.3, -0.4, -0.5):
        r = (Pos(0, 0, 0.3) * Pos(dx, 0, 0) * clip_wall()) & post
        print(f"  wall bent {dx} mm: lifted 0.3 overlap {r.volume if r is not None else 0:.4f} mm3")
    print("swing (plate opened right end up, rocking on the tray's left outer edge):")
    fixed = (tray - post) + pcb + pins
    bent = make_top_deflected(-0.4)
    for deg in (1, 2, 4, 6, 8, 10, 15, 20, 30, 45, 60, 70):
        r = swung(top, deg) & fixed
        v = r.volume if r is not None else 0
        r2 = swung(bent, deg) & post
        v2 = r2.volume if r2 is not None else 0
        print(f"  {deg:>2} deg: plate vs tray {v:.4f} mm3, plate (clip wall bent 0.4 mm) vs clip post {v2:.4f} mm3")
    t = tongues()
    for deg in (20, 30, 40, 45, 50, 55, 60, 70):           # from which tilt the plate lifts straight up off the hook
        if all((r := (Pos(0, 0, 0.1 * i) * swung(top, deg)) & t) is None or r.volume < 1e-4 for i in range(1, 31)):
            print(f"hook engages / releases with the plate tilted {deg} deg or more (lifts straight off the tongue)")
            break
    strain = 1.5 * (WALL_X1 - WALL_X0) * (HOOK_X - LIP_X0 + 0.05) / (CLIP_Y1 - CLIP_Y0) ** 2
    print(f"clip wall: {WALL_X1 - WALL_X0:.1f} mm thick, {CLIP_Y1 - CLIP_Y0:.1f} mm free, bends {HOOK_X - LIP_X0:.2f} mm: "
          f"peak strain {strain * 100:.1f} % (PETG yield about 4 %)")
    print("feet", [tuple(round(v, 2) for v in f) for f in C.FEET], "strap channel", C.STRAP_W)
    for name, s, col in (("top", top, Color(0.92, 0.92, 0.9)), ("tray", tray, Color(0.35, 0.36, 0.38))):
        p = C.out_frame(s); p.label, p.color = f"dock rev D {name}", col
        export_step(p, str(out / f"wakeband-dock-rev-d-{name}.step"))
        export_stl(p, str(out / f"wakeband-dock-rev-d-{name}.stl"), tolerance=0.01, angular_tolerance=0.1)
    for name, s, col in (("magnets", mags, Color(0.6, 0.6, 0.65)), ("spring-pins", pins, Color(0.85, 0.68, 0.3)),
                         ("strap-standin", C.strap_standin(), Color(0.2, 0.25, 0.35))):
        p = C.out_frame(s); p.label, p.color = f"dock rev D {name}", col
        export_step(p, str(out / f"wakeband-dock-rev-d-{name}.step"))
    sys.exit(0 if ok and not hits else 1)
