"""Bambu Lab X1C test plate (256 x 256 mm, PETG): one rev D band case (shell + cover) and one rev D dock
(top plate + tray), each turned to its print orientation from the case READMEs.
    python make_plate.py      (reads the STLs from ../../band/rev-d/case and ../../dock/rev-d/case)"""
import os
import sys

import numpy as np
import trimesh

HERE = os.path.dirname(os.path.abspath(__file__))
HW = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(HW, "strap", "tpu-rev-a", "print-plates"))
from make_plates import write_3mf  # noqa: E402

P, MARGIN, GAP = 256.0, 10.0, 12.0
PARTS = [  # name, stl, flip upside down?
    ("band-shell", "band/rev-d/case/wakeband-case-rev-d-shell.stl", True),     # top face down
    ("band-cover", "band/rev-d/case/wakeband-case-rev-d-cover.stl", False),    # wrist face down
    ("dock-top", "dock/rev-d/case/wakeband-dock-rev-d-top.stl", False),        # flat underside down
    ("dock-tray", "dock/rev-d/case/wakeband-dock-rev-d-tray.stl", False),      # floor down
]


def load(path, flip):
    m = trimesh.load(os.path.join(HW, path))
    m.merge_vertices()
    if flip:
        m.apply_transform(trimesh.transformations.rotation_matrix(np.pi, [1, 0, 0]))
    m.apply_translation(-m.bounds[0])
    return m


def layout():
    ms = [(n, load(p, f)) for n, p, f in PARTS]
    # 2 x 2 grid: band parts in the left column, dock parts in the right, centred on the plate
    cols = [ms[0:2], ms[2:4]]
    widths = [max(m.extents[0] for _, m in c) for c in cols]
    heights = [sum(m.extents[1] for _, m in c) + GAP for c in cols]
    W, H = sum(widths) + GAP, max(heights)
    x0, objs = (P - W) / 2, []
    for c, w, h in zip(cols, widths, heights):
        y = (P - h) / 2
        for n, m in c:
            m.apply_translation([x0 + (w - m.extents[0]) / 2, y, 0])
            objs.append((n, m))
            y += m.extents[1] + GAP
        x0 += w + GAP
    for n, m in objs:
        lo, hi = m.bounds
        assert lo[0] >= MARGIN and lo[1] >= MARGIN and hi[0] <= P - MARGIN and hi[1] <= P - MARGIN, (n, lo, hi)
        assert abs(lo[2]) < 1e-6 and m.is_watertight, n
    return objs


def preview(objs, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.collections import PolyCollection
    fig, ax = plt.subplots(figsize=(6, 6), dpi=150)
    ax.add_patch(plt.Rectangle((0, 0), P, P, fc="#eee", ec="#888"))
    for (n, m), col in zip(objs, ["#3b7dd8", "#5aa0f0", "#d8843b", "#f0a85a"]):
        up = m.face_normals[:, 2] > 0.1
        ax.add_collection(PolyCollection(m.vertices[m.faces[up]][:, :, :2], fc=col, ec="none"))
        c = m.bounds.mean(axis=0)
        ax.text(c[0], m.bounds[1][1] + 3, f"{n}  ({m.extents[2]:.1f} mm)", ha="center", fontsize=7)
    ax.set_xlim(-5, P + 5); ax.set_ylim(-5, P + 5); ax.set_aspect("equal"); ax.axis("off")
    ax.set_title("NudgeBand rev D test plate, X1C 256 x 256 mm", fontsize=9)
    fig.savefig(path, bbox_inches="tight"); plt.close(fig)


if __name__ == "__main__":
    objs = layout()
    write_3mf(os.path.join(HERE, "plate-rev-d-band-and-dock-petg.3mf"), objs)
    preview(objs, os.path.join(HERE, "preview-plate-rev-d.png"))
    for n, m in objs:
        lo, hi = m.bounds
        print(f"{n:11s} x {lo[0]:6.1f}-{hi[0]:6.1f}  y {lo[1]:6.1f}-{hi[1]:6.1f}  h {hi[2]:5.2f}")
