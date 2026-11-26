"""NudgeBand TPU test strap, rev C: one piece, over the top of the case.

One continuous strap printed as a single part. From the wrist it goes up through one of the
case cover's strap-loop slots, across the top of the case, down through the other slot and on
round the wrist. The ends close under the wrist with rev B's slit lock: a split-arrow tongue
weaves down through one slit of a row and up through the next. Nothing stands up off the bed.
There are no case-end tabs: the strap just passes through the loops.

    python strap_tpu_rev_c.py OUT_DIR

Flat coordinates: u along the strap, 0 = where the strap leaves the bottom of the first case
slot. The tongue end is at negative u, the slit row at the far end. Bed face (z = 0) is the skin
side under the wrist; over the case that face lies on the case.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "tpu-rev-b"))
import strap_tpu_rev_b as b  # noqa: E402  (lock, slit, keeper and coupon geometry from rev B)
from build123d import export_step, export_stl  # noqa: E402

T, W = b.T, b.W
# centre line of a 2.0 mm strap hugging the rev D band case (0.15 mm clearance), from the bottom of
# one cover slot, up the end wall, across the shell top and down to the bottom of the other slot.
# Measured on the rev D shell + cover section through the strap centre (y -107.5): 67.1 mm.
OVER_CASE = 67.0
SLOT_TO_BAR = b.BAR_U          # rev A/B sizes count from the bar centres, 2.3 mm outside the slots

SIZES = b.SIZES                # same wrist ranges as rev B: (wrist, L between bars, a)
N_SET = b.N_SET
TAIL = 17.0                    # past the last slit, so the tail reaches the keeper


def strap(size):
    _, (lmin, lmax), a = SIZES[size]
    ua = -(a + SLOT_TO_BAR)                       # where the tongue enters slit A (flat u)
    sh = ua - b.CLASP_WEAVE_EXTRA                 # arrow shoulder
    h0 = lmin - a
    hs = [h0 + b.PITCH * i for i in range(N_SET + 1)]
    u_slot_b = OVER_CASE
    slits = [u_slot_b + SLOT_TO_BAR + h for h in hs]
    tip = slits[-1] + TAIL
    s = b.body(ua + 3.0, tip)
    s = b.round_end(s, tip, +1)
    s += b.taper(ua + 3.0, ua, b.TONGUE_T) + b.tongue(ua + 0.5, sh, -1, b.TONGUE_T)
    for u in slits:
        s -= b.slit(u)
    info = dict(length=tip - (sh - b.ARROW_L), tongue_tip=sh - b.ARROW_L, slits=slits, tip=tip,
                fits=(a + hs[0], a + hs[N_SET - 1]))
    return s, info


def main(out):
    os.makedirs(out, exist_ok=True)
    parts = {}
    for size in SIZES:
        s, i = strap(size)
        parts[f"nudgeband-strap-tpu-rev-c-{size}"] = s
        wr = SIZES[size][0]
        print(f"{size}: wrist {wr[0]}-{wr[1]} mm, flat length {i['length']:.1f} mm, between-bar range "
              f"{i['fits'][0]:.0f}-{i['fits'][1]:.0f} mm in {b.PITCH:.0f} mm steps")
    parts["nudgeband-strap-tpu-rev-c-keeper"] = b.keeper()
    parts["nudgeband-strap-tpu-rev-c-lock-coupon"] = b.coupon()
    for name, p in parts.items():
        export_stl(p, os.path.join(out, name + ".stl"), tolerance=0.01, angular_tolerance=0.15)
        export_step(p, os.path.join(out, name + ".step"))
        bb = p.bounding_box()
        print(f"  {name}: {bb.size.X:.1f} x {bb.size.Y:.1f} x {bb.size.Z:.1f} mm, solids {len(p.solids())}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
