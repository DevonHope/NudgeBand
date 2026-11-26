"""Section views of the rev D hook latch (y = 107.5, through the tongue), closed and tipped open.
usage: python preview_rev_d.py OUT_DIR   (needs build123d, matplotlib)"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Polygon as MPoly  # noqa: E402
from build123d import Plane  # noqa: E402

import case_rev_d as D  # noqa: E402

A = D.A


def section(shape, y=107.5):
    sec = shape & A.box(80, 160, y - 0.001, y + 0.001, -20, 20)
    polys = []
    for f in sec.faces().filter_by(Plane.XZ):
        for w in f.wires():
            pts = []
            for e in w.order_edges():
                n = max(2, int(e.length / 0.05))
                pts += [(p.X, p.Z) for p in (e.position_at(i / n) for i in range(n))]
            polys.append((pts, w is f.outer_wire() or w.is_same(f.outer_wire())))
    return polys


def draw(ax, shape, color, alpha=1.0):
    for pts, outer in section(shape):
        ax.add_patch(MPoly(pts, closed=True, fc=color if outer else "white", ec="#222", lw=0.6, alpha=alpha if outer else 1, zorder=2 if outer else 3))


def main(out):
    shell, cover, board = D.make_shell(), D.make_cover(), D.board_box()
    fig, axs = plt.subplots(1, 3, figsize=(15, 5.2), dpi=160)
    views = (("1. Tip the cover in, hook first (15 deg)", 15, (93, 112, 1, 11.5)),
             ("2. Swing the motor end down", 6, (93, 112, 1, 11.5)),
             ("3. Closed: hook under the shell, screw in", 0, (95, 104, 4.5, 10.5)))
    for ax, (title, deg, (x0, x1, z0, z1)) in zip(axs, views):
        draw(ax, shell, "#3a4150")
        draw(ax, D.swung(cover, deg), "#cfd6c4")
        draw(ax, D.swung(board, deg), "#2e7d32")
        ax.set_xlim(x0, x1); ax.set_ylim(z0, z1); ax.set_aspect("equal")
        ax.set_title(title, fontsize=11); ax.set_xlabel("x (mm), antenna end on the left"); ax.set_ylabel("z (mm), wrist at 0")
        ax.grid(alpha=0.25)
    axs[2].annotate("hook 0.6 mm\n(45 deg underside)", xy=(98.45, 7.9), xytext=(100.8, 5.0), fontsize=9,
                    arrowprops=dict(arrowstyle="->"))
    axs[2].annotate("shell end wall\n(undercut)", xy=(97.2, 7.6), xytext=(100.4, 9.25), fontsize=9, color="#222",
                    bbox=dict(fc="white", ec="none", alpha=0.85),
                    arrowprops=dict(arrowstyle="->"))
    fig.suptitle("NudgeBand case rev D: hook latch at the antenna end (section through the tongue, y 107.5)  "
                 "dark = shell, light = wrist cover, green = board", fontsize=10)
    fig.tight_layout()
    fig.savefig(Path(out) / "wakeband-case-rev-d-latch-section.png")


if __name__ == "__main__":
    main(sys.argv[1])
