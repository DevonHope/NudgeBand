"""Bambu Lab X1C plates (256 x 256 mm) for the one-piece TPU strap, as 3MF files.
The strap is up to 290 mm long, so it is laid across the plate diagonally (45 degrees).
    python make_plates.py      (reads the STLs one folder up)"""
import os
import sys

import numpy as np
import trimesh

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "tpu-rev-a", "print-plates"))
from make_plates import write_3mf  # noqa: E402  (plain 3MF writer, shared with rev A/B)

SRC = os.path.dirname(HERE)
P, MARGIN = 256.0, 8.0


def load(n):
    m = trimesh.load(os.path.join(SRC, f"nudgeband-strap-tpu-rev-c-{n}.stl"))
    m.merge_vertices()
    return m


def centre(m, x, y):
    c = (m.bounds[0] + m.bounds[1]) / 2
    m.apply_translation([x - c[0], y - c[1], -m.bounds[0][2]])
    return m


def size_plate(size):
    s = load(size)
    s.apply_transform(trimesh.transformations.rotation_matrix(np.radians(45), [0, 0, 1]))
    centre(s, P / 2, P / 2)
    k = centre(load("keeper"), P - 40, 40)          # keeper in a free corner
    objs = [(f"strap-{size}", s), ("keeper", k)]
    for _, m in objs:
        assert m.bounds[0][0] >= MARGIN and m.bounds[1][0] <= P - MARGIN, size
        assert m.bounds[0][1] >= MARGIN and m.bounds[1][1] <= P - MARGIN, size
    kx, ky = k.centroid[:2]
    assert abs(kx - ky) / np.sqrt(2) > 8 + 15, size     # keeper well clear of the strap on the diagonal
    write_3mf(os.path.join(HERE, f"plate-2-{size}.3mf"), objs)
    print(f"plate-2-{size}: strap {s.extents[0]:.0f} x {s.extents[1]:.0f} mm across the diagonal + keeper")


def coupon_plate():
    c = centre(load("lock-coupon"), P / 2, P / 2 + 10)
    k = centre(load("keeper"), P / 2, P / 2 - 30)
    write_3mf(os.path.join(HERE, "plate-1-lock-coupon.3mf"), [("lock-coupon", c), ("keeper", k)])
    print("plate-1-lock-coupon")


if __name__ == "__main__":
    coupon_plate()
    for s in ("S", "M", "L", "XL"):
        size_plate(s)
