"""Section views of the dock rev D hook latch (y 119.3) and snap clip (y 119.8).
usage: python preview_rev_d.py OUT_DIR   (needs build123d, matplotlib)"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "band" / "rev-d" / "case"))
import preview_rev_d as band_preview  # noqa: E402  (band's section drawing helpers)
import dock_rev_d as D  # noqa: E402


def draw(ax, shape, color, y):
    from matplotlib.patches import Polygon as MPoly
    for pts, outer in band_preview.section(shape, y):
        ax.add_patch(MPoly(pts, closed=True, fc=color if outer else "white", ec="#222", lw=0.6, zorder=2 if outer else 3))


def main(out):
    top, tray = D.make_top(), D.make_tray()
    pcb, pins, _ = D.C.make_inside()
    fig, axs = plt.subplots(1, 4, figsize=(18, 4.8), dpi=150, gridspec_kw=dict(width_ratios=[1.3, 1.3, 1, 1]))
    y_hook = D.CORNER[1] - 0.3                           # through the straight run of the hook lip
    views = (("1. Hook the left end in (plate tilted 50 deg)", 50, (86, 104, -9, 9)),
             ("2. Swing the right end down", 12, (86, 104, -9, 4)),
             ("3. Closed: hook under the plate", 0, (88, 95, -3.5, 1.6)))
    for ax, (title, deg, (x0, x1, z0, z1)) in zip(axs, views):
        draw(ax, tray, "#5a5e66", y_hook)
        draw(ax, D.swung(top, deg), "#e7e6df", y_hook)
        ax.set_xlim(x0, x1); ax.set_ylim(z0, z1); ax.set_aspect("equal")
        ax.set_title(title, fontsize=10); ax.set_xlabel("x (mm), left end"); ax.grid(alpha=0.25)
    ax = axs[3]
    y = (D.CLIP_Y0 + D.CLIP_HOOK_Y1) / 2
    draw(ax, tray, "#5a5e66", y); draw(ax, top, "#e7e6df", y)
    ax.set_xlim(140.5, 147.5); ax.set_ylim(-3.2, 1.6); ax.set_aspect("equal"); ax.grid(alpha=0.25)
    ax.set_title("4. Clip: plate wall hooks under tray post", fontsize=10)
    ax.set_xlabel("x (mm), right end")
    axs[0].set_ylabel("z (mm)")
    fig.suptitle("NudgeBand dock rev D: hook at the back-left, snap clip at the back-right (sections; light = top plate, "
                 "grey = tray)", fontsize=10)
    fig.tight_layout()
    fig.savefig(Path(out) / "wakeband-dock-rev-d-latch-section.png")


if __name__ == "__main__":
    main(sys.argv[1])
