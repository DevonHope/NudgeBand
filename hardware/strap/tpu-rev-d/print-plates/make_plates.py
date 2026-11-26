"""Bambu Lab X1C test plate (256 x 256 mm): both rev D test straps (size L) side by side across the
diagonal, plus two keepers for the grip version.
    python make_plates.py      (reads the STLs one folder up)"""
import os
import sys

import numpy as np
import trimesh

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "tpu-rev-a", "print-plates"))
from make_plates import write_3mf  # noqa: E402

SRC = os.path.dirname(HERE)
P, MARGIN, OFF = 256.0, 6.0, 13.5        # OFF: each strap's centre line this far either side of the diagonal


def load(n):
    m = trimesh.load(os.path.join(SRC, f"nudgeband-strap-tpu-rev-d-{n}.stl"))
    m.merge_vertices()
    return m


def place(m, ang, cx, cy):
    m.apply_transform(trimesh.transformations.rotation_matrix(np.radians(ang), [0, 0, 1]))
    c = (m.bounds[0] + m.bounds[1]) / 2
    m.apply_translation([cx - c[0], cy - c[1], -m.bounds[0][2]])
    return m


if __name__ == "__main__":
    n = np.array([-1, 1]) / np.sqrt(2)           # normal to the 45 degree diagonal
    objs = []
    for name, sgn in (("lock-L", 1), ("grip-L", -1)):
        cx, cy = np.array([P / 2, P / 2]) + sgn * OFF * n
        objs.append((name, place(load(name), 45, cx, cy)))
    objs.append(("grip-keeper-1", place(load("grip-keeper"), 0, P - 34, 34)))
    objs.append(("grip-keeper-2", place(load("grip-keeper"), 0, P - 34, 50)))
    for name, m in objs:
        lo, hi = m.bounds
        assert lo[0] >= MARGIN and lo[1] >= MARGIN and hi[0] <= P - MARGIN and hi[1] <= P - MARGIN, (name, lo, hi)
    # straps must not touch each other: check the plan-view vertex gap
    a, b_ = objs[0][1], objs[1][1]
    from scipy.spatial import cKDTree
    d = cKDTree(a.vertices[:, :2]).query(b_.vertices[:, :2])[0].min()   # plan-view gap between vertex sets
    assert d > 3.0, d
    write_3mf(os.path.join(HERE, "plate-test-L-lock-and-grip.3mf"), objs)
    print(f"plate-test-L-lock-and-grip: {len(objs)} parts, straps {d:.1f} mm apart at the closest")
