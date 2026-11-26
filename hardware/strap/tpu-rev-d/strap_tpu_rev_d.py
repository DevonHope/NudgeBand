"""NudgeBand TPU test strap, rev D: one piece, thread-through cinch clasp (two variants to test).

Like rev C, the strap goes up through one case loop slot, over the top of the case and down through
the other. The clasp now works like a regular strap. One end ends in a flat **cinch frame** with
a window. The other end (the tail) goes up through the window, gets pulled tight, folds back over
the frame's end bar and is locked onto itself:

  * ``lock``: the tail tip is rev B's split-arrow tongue. It weaves down and up through two slits in
    the tail's own lower run. Because the tail is doubled back, each 7 mm slit pitch gives a 3.5 mm
    adjustment step.
  * ``grip``: no slits. Low (0.8 mm) ratchet teeth on the tail's top face mesh with themselves once it is
    folded back (1.6 mm steps). They slip when you pull tighter and hold the other way. Two sliding
    keepers hold the layers together.

Everything is flat (bed face = skin side), so nothing loads across layer lines except the 0.8 mm
teeth. The clasp zone of the tail is thinned to 1.6 mm so the fold stays low on the wrist. The
frame sits on the side of the wrist, 25 mm from the case strap bar.

    python strap_tpu_rev_d.py OUT_DIR
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "tpu-rev-b"))
import strap_tpu_rev_b as b  # noqa: E402
from build123d import (Axis, Box, Plane, Polygon, Pos, export_step, export_stl, extrude,  # noqa: E402
                       fillet)

T, W = b.T, b.W
OVER_CASE = 67.0               # slot bottom to slot bottom over the rev D case (see rev C)
SLOT_TO_BAR = b.BAR_U

# cinch frame at u = 0 (strap end)
FRAME_W = W + 2 * 2.6          # 21.2: wider than the strap so the window passes it
BAR = 3.0                      # end bar the tail folds round
WIN_L, WIN_W = 3.0, W + 0.8    # window (along u, across)
WIN_C = BAR + WIN_L / 2        # 4.5
FRAME_L = BAR + WIN_L + 3.0    # frame body to u 9, then a taper to the strap width
TAPER_L = 4.0
A_W = 25.0                     # window centre to the case strap bar on the frame side

TAIL_T = 1.6                   # clasp zone thickness
FOLD_X0 = 3.6                  # fold path: window centre -> lying on the lower run, minus spatial x
                               # (up through the window, over the 3 mm bar, down 1.6 mm; 0.6 mm snug)
X_MIN = 10.0                   # nearest a slit/keeper may sit to the window centre (clears the frame)

# lock variant
L_TT = 1.6
L_WEAVE = b.PITCH + 2 * (TAIL_T + L_TT) - b.SNUG
# grip variant
TOOTH_P, TOOTH_H = 1.6, 0.8              # 0.8 tall (was 0.5; user test 2026-11-26)
G_FOLD_MIN = 30.0              # fold-back length at the loosest setting
KEEP_IN_H = 2 * (TAIL_T + TOOTH_H) - TOOTH_H + 0.1   # meshed stack + 0.1 (was +0.4)
KEEP_W, KEEP_L = 1.2, 6.0
KEEP_IN_W = W + 0.4             # inner width (was W + 0.8)

SIZES = b.SIZES                # (wrist, L between case bars, -)
BUILD = ("L",)                 # test straps: L only for now (others build by adding them here)


def frame():
    f = Pos(FRAME_L / 2, 0, T / 2) * Box(FRAME_L, FRAME_W, T)
    f = fillet(f.edges().filter_by(Axis.Z).group_by(Axis.X)[0], 3.0)    # round the strap-end corners
    tp = extrude(Polygon((FRAME_L - 0.01, FRAME_W / 2), (FRAME_L + TAPER_L, W / 2),
                         (FRAME_L + TAPER_L, -W / 2), (FRAME_L - 0.01, -FRAME_W / 2), align=None),
                 amount=T, dir=(0, 0, 1))
    win = Pos(WIN_C, 0, 0) * Box(WIN_L, WIN_W, 20)
    win = fillet(win.edges().filter_by(Axis.Z), 0.9)                  # round window corners (no tear start)
    return (f + tp) - win


def layout(size):
    """strap positions (u from the frame end) common to both variants"""
    _, (lmin, lmax), _ = SIZES[size]
    bar_a = WIN_C + A_W
    slot_a = bar_a + SLOT_TO_BAR
    slot_b = slot_a + OVER_CASE
    bar_b = slot_b + SLOT_TO_BAR
    # tail position that sits in the window, tightest .. loosest
    up_min, up_max = bar_b + (lmin - A_W), bar_b + (lmax - A_W)
    return bar_b, up_min, up_max


def tail_body(u0, u_thin, tip):
    s = b.body(FRAME_L + TAPER_L - 0.5, u_thin, T)
    s += b.body(u_thin - 0.5, tip, TAIL_T)
    return s


def strap_lock(size):
    bar_b, up_min, up_max = layout(size)
    entry = up_max + X_MIN + FOLD_X0          # tongue entry point (fixed on the strap)
    sh = entry + L_WEAVE
    tip = sh + b.ARROW_L
    # slit A for window position up: 2*up - entry + FOLD_X0; up steps 3.5 mm -> slits every 7 mm
    n = int(round((up_max - up_min) / (b.PITCH / 2)))
    slits_a = [2 * (up_min + i * b.PITCH / 2) - entry + FOLD_X0 for i in range(n + 1)]
    slits = sorted(set([round(s, 3) for s in slits_a] + [round(slits_a[0] - b.PITCH, 3)]))
    u_thin = slits[0] - 15
    s = frame() + tail_body(0, u_thin, entry - 3.0)
    s += b.taper(entry - 3.0, entry, L_TT) + b.tongue(entry - 0.5, sh, +1, L_TT)
    for u in slits:
        s -= b.slit(u)
    return s, dict(length=tip, settings=n + 1, step=b.PITCH / 2, slits=(slits[0], slits[-1]),
                   fold=(X_MIN, X_MIN + (up_max - up_min)))


def teeth(u0, u1, t):
    """ratchet teeth across the strap on the top face, u0..u1: steep face toward -u, ramp down toward +u
    (they mesh with themselves when the strap is folded back; tightening slides, loosening locks)"""
    n = int((u1 - u0) / TOOTH_P)
    prof = [(u0, t)]
    for i in range(n):
        x = u0 + i * TOOTH_P
        prof += [(x, t + TOOTH_H), (x + TOOTH_P, t)]
    prof += [(u0 + n * TOOTH_P, t - 0.3), (u0, t - 0.3)]
    face = Plane.XZ * Polygon(*prof, align=None)
    return extrude(face, amount=(W - 2.0) / 2, both=True)


def strap_grip(size):
    bar_b, up_min, up_max = layout(size)
    tip = up_max + FOLD_X0 + 7.5 + G_FOLD_MIN      # fold-back reaches 30 mm past the frame at the loosest
    tooth_from = up_min - (tip - up_min) + 2.0     # lower run under the longest fold-back
    u_thin = tooth_from - 15
    s = frame() + tail_body(0, u_thin, tip)
    s = b.round_end(s, tip, +1)
    s += teeth(tooth_from, tip - 9.0, TAIL_T)
    return s, dict(length=tip, teeth=(tooth_from, tip - 9), fold=(G_FOLD_MIN, G_FOLD_MIN + up_max - up_min))


def keeper_grip():
    ow, oh = KEEP_IN_W + 2 * KEEP_W, KEEP_IN_H + 2 * KEEP_W
    k = Pos(0, 0, KEEP_L / 2) * Box(ow, oh, KEEP_L) - Pos(0, 0, KEEP_L / 2) * Box(KEEP_IN_W, KEEP_IN_H, KEEP_L + 2)
    return fillet(k.edges().filter_by(Axis.Z), 0.5)


def main(out):
    os.makedirs(out, exist_ok=True)
    parts = {}
    for size in BUILD:
        sl, il = strap_lock(size)
        sg, ig = strap_grip(size)
        parts[f"nudgeband-strap-tpu-rev-d-lock-{size}"] = sl
        parts[f"nudgeband-strap-tpu-rev-d-grip-{size}"] = sg
        print(f"{size}: lock {il['length']:.1f} mm, {il['settings']} settings x {il['step']} mm, fold-back {il['fold']}; "
              f"grip {ig['length']:.1f} mm, fold-back {ig['fold']}")
    parts["nudgeband-strap-tpu-rev-d-grip-keeper"] = keeper_grip()
    for name, p in parts.items():
        export_stl(p, os.path.join(out, name + ".stl"), tolerance=0.01, angular_tolerance=0.15)
        export_step(p, os.path.join(out, name + ".step"))
        bb = p.bounding_box()
        print(f"  {name}: {bb.size.X:.1f} x {bb.size.Y:.1f} x {bb.size.Z:.1f} mm, solids {len(p.solids())}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
