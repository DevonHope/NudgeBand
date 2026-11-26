"""NudgeBand TPU test strap, rev A: double stud and tuck clasp.

Builds the two strap halves for sizes S/M/L, the sliding keeper and a stud
fit coupon, and writes STEP + STL files:

    python strap_tpu.py OUT_DIR

Everything is printed flat, outer face up, no supports (TPU 95A).

Coordinates (flat strap): u runs along the strap, 0 = the fold point, which
sits in the middle of the case strap slot once fitted. The case end (tab,
negative u) wraps round the case strap bar; the clasp end is at positive u.
Width along Y, thickness along Z (bed face z = 0 is the skin side).

Case interface: the strap loops of the band case cover (case rev A/B/C):
16.6 x 2.2 mm slots through a 3.0 mm tall loop, 2.4 mm bar outside the slot,
bar centres about 50.8 mm apart.
"""
import os
import sys

from build123d import (Align, Axis, Box, Cone, Cylinder, Kind, Pos, Rot,
                       export_step, export_stl, fillet, chamfer)

# ------------------------------------------------------------------ strap
W = 16.0          # strap width (slot is 16.6)
T = 2.0           # strap thickness
EDGE_R = 0.6      # long-edge round

# case end: tab folds round the case strap bar and snaps over two pegs
TAB_W = 15.6      # through the 16.6 x 2.2 slot (round slot ends)
TAB_T = 1.2
PEG_U = (12.5, 18.5)          # pegs on the strap body, from the fold point
TAB_EXTRA = 5.0               # path from the fold round the bar back to the body
                              # (centre line ~5.6 mm; 0.6 mm short so the loop is snug)
TAB_HOLE_U = tuple(-(u + TAB_EXTRA) for u in PEG_U)
TAB_TIP = TAB_HOLE_U[1] - 4.0
PEG_D, PEG_HEAD_D, PEG_HOLE_D = 2.4, 3.6, 2.4
BAR_U = 2.3                   # case bar centre from the fold point (slot centre)

# clasp: two mushroom studs on the short strap, hole row on the long strap
PITCH = 6.0                   # hole pitch = adjustment step
STUD_D, STUD_HEAD_D = 3.0, 4.4
HOLE_D = 3.0                  # see the fit coupon: 2.6 / 2.8 / 3.0 / 3.2
TIP_R = W / 2

# keeper: separate sliding ring that holds the long strap's tail
KEEP_WALL, KEEP_L = 1.2, 6.0
KEEP_IN_W, KEEP_IN_H = W + 0.8, 2 * T + 0.4

# Sizes. L = strap length needed round the wrist between the two case bars
# (wrist circumference minus about 50 mm for the case). S1 = short strap's
# tip-side stud, measured from the case bar centre.
SIZES = {
    #     wrist mm      L range        S1
    "S": ((140, 162), (90, 112), 58.0),
    "M": ((158, 180), (108, 130), 62.0),
    "L": ((176, 200), (126, 150), 68.0),
    "XL": ((194, 220), (144, 170), 74.0),
}


def bar(u0, u1, w, t, z0=0.0):
    return Pos((u0 + u1) / 2, 0, z0 + t / 2) * Box(u1 - u0, w, t)


def round_end(s, u_tip, sign, r):
    """trim the end at u_tip into a semicircle of radius r (sign: +1 tip at +u)"""
    c = u_tip - sign * r
    keep = Pos(c - sign * 500, 0, 0) * Box(1000, 2 * r + 4, 50) + Pos(c, 0, 0) * Cylinder(r, 50)
    return s & keep


def mushroom(u, z, neck_d, neck_h, head_d, head_h):
    """neck plus a double-cone head: 45 deg underside (prints without support),
    tapered top so it pushes through the hole"""
    a = (Align.CENTER, Align.CENTER, Align.MIN)
    rn, rh = neck_d / 2, head_d / 2
    under = rh - rn                              # 45 deg underside
    top = max(head_h - under - 0.3, 0.4)
    s = Pos(u, 0, z) * Cylinder(rn, neck_h + 0.01, align=a)
    s += Pos(u, 0, z + neck_h) * Cone(rn, rh, under, align=a)
    s += Pos(u, 0, z + neck_h + under) * Cylinder(rh, 0.3, align=a)
    s += Pos(u, 0, z + neck_h + under + 0.3) * Cone(rh, rn * 0.9, top, align=a)
    return s


def holes(s, us, d):
    for u in us:
        s -= Pos(u, 0, 0) * Cylinder(d / 2, 40)
    return s


def strap_half(clasp_tip_u):
    """common body: case-end tab, two pegs, strap out to clasp_tip_u"""
    body = bar(0.5, clasp_tip_u, W, T)
    body = fillet(body.edges().filter_by(Axis.X), EDGE_R)
    # thin tab (bed face flush with the body's) and a 45 deg step between them
    tab = bar(TAB_TIP, 1.3, TAB_W, TAB_T)
    tab = fillet(tab.edges().filter_by(Axis.Z), 1.0)
    tab = fillet(tab.edges().filter_by(Axis.X), 0.4)
    s = body + tab
    s = round_end(s, clasp_tip_u, +1, TIP_R)
    s = holes(s, TAB_HOLE_U, PEG_HOLE_D)
    for u in PEG_U:
        s += mushroom(u, T, PEG_D, TAB_T + 0.1, PEG_HEAD_D, 1.4)
    return s


def short_strap(size):
    _, _, s1 = SIZES[size]
    u1 = s1 + BAR_U                    # tip-side stud
    tip = u1 + 7.0
    s = strap_half(tip)
    for u in (u1, u1 - PITCH):
        s += mushroom(u, T, STUD_D, T + 0.2, STUD_HEAD_D, 2.0)
    return s, dict(studs_from_bar=(s1 - PITCH, s1), tip_from_bar=tip - BAR_U)


def long_strap(size):
    _, (lmin, lmax), s1 = SIZES[size]
    h0, h1 = lmin - s1, lmax - s1 + PITCH          # hole range from the bar
    n = int(round((h1 - h0) / PITCH)) + 1
    hs = [h0 + PITCH * i for i in range(n)]
    tip = hs[-1] + 17.0                            # tail long enough to reach the keeper
    s = strap_half(tip + BAR_U)
    s = holes(s, [h + BAR_U for h in hs], HOLE_D)
    return s, dict(holes_from_bar=hs, tip_from_bar=tip, settings=n - 1)


def keeper():
    """rectangular ring, printed standing (axis vertical)"""
    ow, oh = KEEP_IN_W + 2 * KEEP_WALL, KEEP_IN_H + 2 * KEEP_WALL
    k = Pos(0, 0, KEEP_L / 2) * Box(ow, oh, KEEP_L) - Pos(0, 0, KEEP_L / 2) * Box(KEEP_IN_W, KEEP_IN_H, KEEP_L + 2)
    k = fillet(k.edges().filter_by(Axis.Z), 0.5)
    return k


def coupon():
    """fit test: a stud strip (two studs) and a hole strip with pairs of
    2.6 / 2.8 / 3.0 / 3.2 mm holes (notches on the edge count 1..4)"""
    studs = bar(0, 22, W, T)
    studs = fillet(studs.edges().filter_by(Axis.X), EDGE_R)
    for u in (8, 8 + PITCH):
        studs += mushroom(u, T, STUD_D, T + 0.2, STUD_HEAD_D, 2.0)
    strip = bar(0, 4 * 16 + 4, W, T)
    strip = fillet(strip.edges().filter_by(Axis.X), EDGE_R)
    for i, d in enumerate((2.6, 2.8, 3.0, 3.2)):
        u0 = 5 + 16 * i
        strip = holes(strip, (u0, u0 + PITCH), d)
        for j in range(i + 1):
            strip -= Pos(u0 + PITCH / 2 - i * 0.9 + j * 1.8, W / 2, T / 2) * Box(0.8, 1.6, 10)
    strip = Pos(0, W + 4, 0) * strip
    return studs + strip


def main(out):
    os.makedirs(out, exist_ok=True)
    report = []
    parts = {}
    for size in SIZES:
        sh, i_s = short_strap(size)
        lo, i_l = long_strap(size)
        parts[f"nudgeband-strap-tpu-rev-a-{size}-short"] = sh
        parts[f"nudgeband-strap-tpu-rev-a-{size}-long"] = lo
        wr, lr, _ = SIZES[size]
        report.append(f"{size}: wrist {wr[0]}-{wr[1]} mm; short studs {i_s['studs_from_bar']} mm from bar, "
                      f"tip {i_s['tip_from_bar']:.1f}; long holes {i_l['holes_from_bar'][0]:.0f}..{i_l['holes_from_bar'][-1]:.0f} "
                      f"({len(i_l['holes_from_bar'])} holes, {i_l['settings']} settings), tip {i_l['tip_from_bar']:.1f}; "
                      f"flat length short {i_s['tip_from_bar'] + BAR_U - TAB_TIP:.1f}, long {i_l['tip_from_bar'] + BAR_U - TAB_TIP:.1f}")
    parts["nudgeband-strap-tpu-rev-a-keeper"] = keeper()
    parts["nudgeband-strap-tpu-rev-a-fit-coupon"] = coupon()
    for name, p in parts.items():
        export_stl(p, os.path.join(out, name + ".stl"), tolerance=0.01, angular_tolerance=0.15)
        export_step(p, os.path.join(out, name + ".step"))
        bb = p.bounding_box()
        print(f"{name}: {bb.size.X:.1f} x {bb.size.Y:.1f} x {bb.size.Z:.1f} mm, {p.volume / 1000:.2f} cm3, solids {len(p.solids())}")
    print("\n".join(report))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
