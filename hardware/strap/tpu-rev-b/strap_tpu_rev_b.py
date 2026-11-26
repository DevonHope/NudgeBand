"""NudgeBand TPU test strap, rev B: slit lock (no upright features).

Rev A held with mushroom studs and pegs that stand up off the bed, so the load on their necks
pulls across layer lines, TPU's weakest direction. Rev B keeps every part flat: each lock is a
tongue with a split arrowhead that weaves down through one slit and back up through the next.
The barbs flex sideways (in the print plane), and the load runs along the printed walls.

Both ends use the same lock:
  * case end: the tab goes through the case strap slot, folds back over the bar and weaves
    through two slits in its own strap.
  * clasp: the short strap's tongue weaves through two adjacent slits of the long strap's row.

    python strap_tpu_rev_b.py OUT_DIR

Everything prints flat (bed face = skin side), no supports, TPU 95A.
Coordinates as rev A: u along the strap, 0 = fold point (middle of the case slot once fitted).
"""
import os
import sys

from build123d import Axis, Box, Cylinder, Polygon, Pos, export_step, export_stl, extrude, fillet

W, T = 16.0, 2.0          # strap width / thickness
EDGE_R = 0.6
BAR_U = 2.3               # case bar centre from the fold point

# lock geometry (same at both ends)
NECK_W = 11.0             # tongue width (fits the slits and the case slot)
ARROW_W = 15.6            # barbs, open
ARROW_L = 8.0             # shoulder to tip
BARB_HOOK = 0.8           # barb back edge swept back this much (positive lock)
RELIEF_W = 3.0            # split down the arrowhead: halves squeeze to ARROW_W - RELIEF_W
RELIEF_BACK = 3.0         # split runs this far behind the shoulder ...
RELIEF_HOLE = 3.6         # ... and ends in a round stress-relief hole
SLIT_L, SLIT_W = 13.0, 2.0       # slit across the strap / along it
SLIT_END_D = 2.8                 # dog-bone relief holes at the slit ends
PITCH = 7.0               # slit pitch (adjustment step at the clasp)

TONGUE_T = 1.6            # clasp tongue thickness (slit 2.0 + flex)
TAB_T = 1.2               # case-end tab thickness (case slot is 2.2)
CASE_SLIT_U = (12.0, 19.0)       # case-end slits A, B in the strap body (from the fold)
CASE_PATH = 5.7           # fold -> round the bar -> back onto the body (centre line, rev A)
SNUG = 0.6                # make each lock this much short so it sits tight
# a lock lies on top of the strap, dives down through slit A, runs under the bridge and comes up
# through slit B: its centre line drops (T + its own thickness) twice
CLASP_WEAVE_EXTRA = PITCH + 2 * (T + TONGUE_T) - SNUG     # flat tongue from slit A to the shoulder
CASE_WEAVE_EXTRA = (CASE_SLIT_U[1] - CASE_SLIT_U[0]) + 2 * (T + TAB_T) - SNUG

KEEP_WALL, KEEP_L = 1.2, 6.0
KEEP_IN_W, KEEP_IN_H = W + 0.8, 2 * T + 0.4

SIZES = {
    #     wrist mm      L range        A: short strap length from bar to where it enters slit A
    "S": ((140, 162), (90, 112), 58.0),
    "M": ((158, 180), (108, 130), 62.0),
    "L": ((176, 200), (126, 150), 68.0),
    "XL": ((194, 220), (144, 170), 74.0),
}
N_SET = 5                 # clasp settings (slit pairs)


def slab(face, t):
    return extrude(face, amount=t, dir=(0, 0, 1))


def arrow_face(u_sh, sign):
    """2D arrowhead + split, shoulder at u_sh, pointing +u (sign 1) or -u (sign -1)"""
    h, a = ARROW_W / 2, ARROW_L
    pts = [(-BARB_HOOK, NECK_W / 2 - 0.01), (-BARB_HOOK, h), (0, h), (a, 3.0), (a, -3.0),
           (0, -h), (-BARB_HOOK, -h), (-BARB_HOOK, -NECK_W / 2 + 0.01), (-2, -NECK_W / 2 + 0.01),
           (-2, NECK_W / 2 - 0.01)]
    return Polygon(*[(u_sh + sign * x, y) for x, y in pts], align=None)


def lock_cut(u_sh, sign):
    """the split down the middle of the arrowhead, ending in a round relief hole"""
    c = u_sh - sign * RELIEF_BACK
    tip = u_sh + sign * (ARROW_L + 1)
    s = Pos((c + tip) / 2, 0, 0) * Box(abs(tip - c), RELIEF_W, 20)
    s += Pos(c, 0, 0) * Cylinder(RELIEF_HOLE / 2, 20)
    return s


def tongue(u_from, u_sh, sign, t):
    """neck from u_from to the shoulder at u_sh, plus arrowhead; t thick, bed flush"""
    u0, u1 = sorted((u_from, u_sh))
    neck = Pos((u0 + u1) / 2, 0, t / 2) * Box(u1 - u0, NECK_W, t)
    head = slab(arrow_face(u_sh, sign), t)
    s = neck + head
    s -= lock_cut(u_sh, sign)
    return s


def slit(u):
    s = Pos(u, 0, 0) * Box(SLIT_W, SLIT_L - SLIT_END_D / 2, 20)
    for y in (-1, 1):
        s += Pos(u, y * (SLIT_L - SLIT_END_D) / 2, 0) * Cylinder(SLIT_END_D / 2, 20)
    return s


def body(u0, u1, t=T, w=W):
    b = Pos((u0 + u1) / 2, 0, t / 2) * Box(u1 - u0, w, t)
    return fillet(b.edges().filter_by(Axis.X), EDGE_R)


def round_end(s, u_tip, sign, r=W / 2):
    c = u_tip - sign * r
    keep = Pos(c - sign * 500, 0, 0) * Box(1000, 2 * r + 4, 50) + Pos(c, 0, 0) * Cylinder(r, 50)
    return s & keep


def taper(u_wide, u_narrow, t):
    """16 -> 11 mm transition between the strap and a tongue"""
    pts = [(u_wide, W / 2), (u_narrow, NECK_W / 2), (u_narrow, -NECK_W / 2), (u_wide, -W / 2)]
    return slab(Polygon(*pts, align=None), t)


def case_end():
    """fold-back tab (negative u) and its two slits; returns (tab solid, slit u list)"""
    sh = -(CASE_SLIT_U[0] + CASE_PATH + CASE_WEAVE_EXTRA)
    tab = tongue(-1.0, sh, -1, TAB_T) + taper(1.0, -2.0, TAB_T)
    return tab, list(CASE_SLIT_U)


def strap_half(tip_u):
    s = body(0.5, tip_u)
    s = round_end(s, tip_u, +1)
    tab, slits = case_end()
    s += tab
    for u in slits:
        s -= slit(u)
    return s


def short_strap(size):
    _, _, a = SIZES[size]
    ua = a + BAR_U                         # where the tongue dives into slit A
    sh = ua + CLASP_WEAVE_EXTRA            # shoulder (flat)
    s = body(0.5, ua - 3.0)
    tab, slits = case_end()
    s += tab
    for u in slits:
        s -= slit(u)
    s += taper(ua - 3.0, ua, TONGUE_T) + tongue(ua - 0.5, sh, +1, TONGUE_T)
    return s, dict(enter_from_bar=a, shoulder_from_bar=sh - BAR_U, tip_from_bar=sh + ARROW_L - BAR_U)


def long_strap(size):
    _, (lmin, lmax), a = SIZES[size]
    h0 = lmin - a                          # slit A of the tightest setting, from the bar
    hs = [h0 + PITCH * i for i in range(N_SET + 1)]
    tip = hs[-1] + 17.0
    s = strap_half(tip + BAR_U)
    for h in hs:
        s -= slit(h + BAR_U)
    return s, dict(slits_from_bar=hs, tip_from_bar=tip, range=(a + hs[0], a + hs[N_SET - 1]))


def keeper():
    ow, oh = KEEP_IN_W + 2 * KEEP_WALL, KEEP_IN_H + 2 * KEEP_WALL
    k = Pos(0, 0, KEEP_L / 2) * Box(ow, oh, KEEP_L) - Pos(0, 0, KEEP_L / 2) * Box(KEEP_IN_W, KEEP_IN_H, KEEP_L + 2)
    return fillet(k.edges().filter_by(Axis.Z), 0.5)


def coupon():
    """lock test: a tongue strip and a strip with two slits (plus a pair at 12.6 / 13.4 mm)"""
    t = body(0, 14) + taper(14, 17, TONGUE_T) + tongue(16.5, 17 + CLASP_WEAVE_EXTRA, +1, TONGUE_T)
    strip = body(0, 70)
    for u0, L in ((10, SLIT_L - 0.4), (32, SLIT_L), (54, SLIT_L + 0.4)):
        for u in (u0, u0 + PITCH):
            c = Pos(u, 0, 0) * Box(SLIT_W, L - SLIT_END_D / 2, 20)
            for y in (-1, 1):
                c += Pos(u, y * (L - SLIT_END_D) / 2, 0) * Cylinder(SLIT_END_D / 2, 20)
            strip -= c
    return t + Pos(0, W + 4, 0) * strip


def main(out):
    os.makedirs(out, exist_ok=True)
    parts, rep = {}, []
    for size in SIZES:
        sh, i_s = short_strap(size)
        lo, i_l = long_strap(size)
        parts[f"nudgeband-strap-tpu-rev-b-{size}-short"] = sh
        parts[f"nudgeband-strap-tpu-rev-b-{size}-long"] = lo
        rep.append(f"{size}: wrist {SIZES[size][0]}; fits L {i_l['range']} mm in {PITCH} mm steps; "
                   f"slits {i_l['slits_from_bar']}; short tip {i_s['tip_from_bar']:.1f}, long tip {i_l['tip_from_bar']:.1f}")
    parts["nudgeband-strap-tpu-rev-b-keeper"] = keeper()
    parts["nudgeband-strap-tpu-rev-b-lock-coupon"] = coupon()
    for name, p in parts.items():
        export_stl(p, os.path.join(out, name + ".stl"), tolerance=0.01, angular_tolerance=0.15)
        export_step(p, os.path.join(out, name + ".step"))
        bb = p.bounding_box()
        print(f"{name}: {bb.size.X:.1f} x {bb.size.Y:.1f} x {bb.size.Z:.1f} mm, solids {len(p.solids())}")
    print("\n".join(rep))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
