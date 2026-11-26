"""WakeBand dock rev D: the rev C dock (../../rev-c/case/dock_rev_c.py) with the two printed locating pins
replaced by hook latches at the left end and one M2 screw at the right end.

Rev C held the top plate on the tray by friction on two Ø2 mm pins printed on the tray. Rev D:
  - a TONGUE rises from the tray's back-left end block (beside the strap channel, where rev C's back-left pin
    was), with a HOOK at its top pointing outward (-x); the top plate has a matching slot with an undercut (CLR
    all round, the band case's hook profile). It sits 1.9 mm in from the left face and stands 1.85 mm tall, so
    tipping the plate on its left edge swings the undercut clear of the hook. A second hook at the front-left
    would not work: that corner of the plate is a thin curved strip between the outline, the band recess and the
    strap channel, too far from the edge the plate rocks on to swing clear. Like rev C (two pins, both at the
    back), the front edge simply rests on the tray;
  - at the right-hand back corner one M2 x 8 countersunk screw goes up through the tray from underneath into an
    M2 hex nut pressed into a pocket in the plate underside. The plate is only 3.25 mm thick, too thin for a
    3 mm heat-set insert, so a nut gives metal threads instead (and survives any number of re-flashes).
  - the two right-hand rubber feet move inward so they don't cover the screw head; the left pair moves to match.
To fit the plate: tip it in left end first so both hooks go under the plate's undercuts, swing the right end down
onto the spring pins, then fit the screw from underneath.
Both parts still print with no supports, as rev C (plate underside down, tray floor down).
usage (needs build123d): python dock_rev_d.py OUT_DIR [DOCK_PCB_STEP]"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "rev-c" / "case"))
sys.path.insert(0, str(HERE.parents[2] / "band" / "rev-d" / "case"))
import dock_rev_c as C  # noqa: E402
import case_rev_d as band_d  # noqa: E402  (hook profile)
from build123d import Align, Color, Cone, Pos, Rot, RegularPolygon, export_step, export_stl  # noqa: E402

case = C.case
A = C.A
DOCK = C.DOCK

C.LOC_PINS = ()                                   # no printed locating pins
# rubber feet: 4 mm further in at each end (rev C x 96.35 / 140.95) so the right pair is clear of the screw head
C.FEET = [(x, y) for x in (DOCK[0] + 11.0, DOCK[1] - 11.0) for y in (DOCK[2] + 6.0, DOCK[3] - 6.0)]

# ------------------------------------------------------------------ hooks (left end)
HOOK, HOOK_FLAT, TIP_CH, CLR = band_d.HOOK, band_d.HOOK_FLAT, band_d.TIP_CH, band_d.CLR
TONGUE_X = (91.2, 92.2)                           # 1.0 mm thick; slot reaches x 90.45, 0.75 mm or more in from the outline
TONGUE_H = 1.85                                   # above the joint (-2.05); slot top -0.05: 1.25 mm of plate over it
TONGUES_Y = ((118.2, 120.4),)                     # back-left block, clear of the band recess (y <= 117.85) and the
                                                  # outline's corner round (centre 96.35, 118.6)
Z0 = C.PLATE_Z0                                   # joint plane (-2.05)

# ------------------------------------------------------------------ screw (right end)
SCREW = (143.8, 121.0)                            # back-right end block: 0.8 mm wall to the tray cavity, 3.3 mm to the outline
SCREW_CLEAR_D = 2.4
CSK_D, CSK_DEPTH = 4.4, 0.2                       # countersink (DIN 965 M2 head Ø3.8) and 0.2 mm below flush
NUT_AF, NUT_T = 4.0, 1.6                          # M2 hex nut (ISO 4032)
NUT_POCKET_AF, NUT_POCKET_T = 4.05, 1.7           # snug press, from the plate underside
TIP_HOLE_TOP = 0.2                                # screw-tip clearance above the nut (1.0 mm of plate left over it)


def tongues():
    out = None
    for y0, y1 in TONGUES_Y:
        t = band_d.prism(band_d.hook_face(*TONGUE_X, Z0 - 0.01, Z0 + TONGUE_H, HOOK, HOOK_FLAT, TIP_CH), y0, y1)
        out = t if out is None else out + t
    return out


def slots():
    out = None
    x_out, x_in = TONGUE_X
    for y0, y1 in TONGUES_Y:
        # inner side 0.6 mm wider: the plate moves outward over the tongue as it swings down
        s = band_d.prism(band_d.hook_face(x_out, x_in + 0.6, Z0 - 1, Z0 + TONGUE_H, HOOK, HOOK_FLAT, TIP_CH), y0, y1, grow=CLR)
        out = s if out is None else out + s
    return out


def make_top():
    t = C.make_top() - slots()
    x, y = SCREW
    t -= _hex_prism(x, y, NUT_POCKET_AF, Z0 - 1, Z0 + NUT_POCKET_T)
    t -= case.cyl(x, y, SCREW_CLEAR_D / 2 - 0.1, Z0, TIP_HOLE_TOP)
    return t


def _hex_prism(x, y, af, z0, z1):
    return case.slab(Pos(x, y) * Rot(0, 0, 30) * RegularPolygon(af / 2, 6, major_radius=False), z0, z1)


def make_tray():
    t = C.make_tray() + tongues()
    x, y = SCREW
    t -= case.cyl(x, y, SCREW_CLEAR_D / 2, C.TRAY_Z0 - 1, Z0 + 1)
    t -= case.cyl(x, y, CSK_D / 2, C.TRAY_Z0 - 1, C.TRAY_Z0 + CSK_DEPTH)
    t -= Pos(x, y, C.TRAY_Z0 + CSK_DEPTH) * Cone(CSK_D / 2, SCREW_CLEAR_D / 2, (CSK_D - SCREW_CLEAR_D) / 2,
                                                 align=(Align.CENTER, Align.CENTER, Align.MIN))
    return t


def make_screw_and_nut():
    x, y = SCREW
    z_head = C.TRAY_Z0 + CSK_DEPTH
    s = Pos(x, y, z_head) * Cone(3.8 / 2, 1.0, 1.2, align=(Align.CENTER, Align.CENTER, Align.MIN))
    s += case.cyl(x, y, 1.0, z_head + 1.19, z_head + 8.0)
    n = _hex_prism(x, y, NUT_AF, Z0 + 0.02, Z0 + 0.02 + NUT_T) - case.cyl(x, y, 1.0, Z0 - 1, Z0 + 3)
    return s, n


# ------------------------------------------------------------------ swing check
PIVOT = (DOCK[0] + C.SEAM_CH, Z0)                 # the plate rocks on the tray's left outer edge (0.35 mm seam chamfer)


def swung(shape, deg):
    """plate opened by deg: right end up, turning about a y axis through PIVOT"""
    px, pz = PIVOT
    return Pos(px, 0, pz) * Rot(0, -deg, 0) * Pos(-px, 0, -pz) * shape


if __name__ == "__main__":
    out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    top, tray = make_top(), make_tray()
    pcb, pins, mags = C.make_inside()
    screw, nut = make_screw_and_nut()
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
    for n, a in (("pcb envelope", pcb), ("spring pins", pins), ("magnets", mags), ("screw", screw), ("nut", nut)):
        for m, b in (("top", top), ("tray", tray), ("band cover", cover)):
            if m == "band cover" and n in ("pcb envelope", "screw", "nut"):
                continue
            if (n, m) in (("screw", "top"),):           # the screw tip runs into its clearance hole only
                pass
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
    print("swing (plate opened right end up, rocking on the tray's left outer edge):")
    fixed = tray + pcb + pins
    for deg in (1, 2, 4, 6, 8, 10, 15, 20, 30, 45, 60, 70):
        r = swung(top, deg) & fixed
        v = r.volume if r is not None else 0
        print(f"  {deg:>2} deg: overlap {v:.4f} mm3")
    t = tongues()
    for deg in (20, 30, 45, 50, 55, 60, 70):           # from which tilt the plate lifts straight up off the hook
        if all((r := (Pos(0, 0, 0.1 * i) * swung(top, deg)) & t) is None or r.volume < 1e-4 for i in range(1, 31)):
            print(f"hook engages / releases with the plate tilted {deg} deg or more (lifts straight off the tongue)")
            break
    print(f"screw: M2 x 8 countersunk, head {CSK_DEPTH} mm below the tray underside, tip at z {C.TRAY_Z0 + CSK_DEPTH + 8.0:.2f} "
          f"(nut {Z0 + 0.02:.2f} to {Z0 + 0.02 + NUT_T:.2f}, clearance hole to {TIP_HOLE_TOP})")
    print("feet", [tuple(round(v, 2) for v in f) for f in C.FEET])
    for name, s, col in (("top", top, Color(0.92, 0.92, 0.9)), ("tray", tray, Color(0.35, 0.36, 0.38))):
        p = C.out_frame(s); p.label, p.color = f"dock rev D {name}", col
        export_step(p, str(out / f"wakeband-dock-rev-d-{name}.step"))
        export_stl(p, str(out / f"wakeband-dock-rev-d-{name}.stl"), tolerance=0.01, angular_tolerance=0.1)
    for name, s, col in (("magnets", mags, Color(0.6, 0.6, 0.65)), ("spring-pins", pins, Color(0.85, 0.68, 0.3)),
                         ("screw-nut", screw + nut, Color(0.7, 0.7, 0.72)), ("strap-standin", C.strap_standin(), Color(0.2, 0.25, 0.35))):
        p = C.out_frame(s); p.label, p.color = f"dock rev D {name}", col
        export_step(p, str(out / f"wakeband-dock-rev-d-{name}.step"))
    sys.exit(0 if ok and not hits else 1)
