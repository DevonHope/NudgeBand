"""WakeBand open test shell: the band shell with its roof cut open, so the band board can be probed with a
meter or scope while it sits on the dock.

It is the normal shell (rev D, or rev C with --rev c) with every interface kept: the skirt that meets the
wrist cover, the antenna-end joint (rev D hook slot or rev C press-fit pins), the M2 screw boss with its
heat-set insert hole, and the three things that press the board down onto the cover against the four
spring pins (the dock land over the top pin pair, the post over the bottom pair, the two posts on the antenna
keep-out strip). Only the roof between them is removed, so the board sits exactly where it sits in the real
case and the cover, carrier, magnets, cell, LRA and dock are all the real ones.

Two changes besides the window:
  - the dock land starts at x LAND_X0 (128.4) instead of 127.6, so the PMID test pad TP705 (127.1, 101.6) is
    in the window; the land still covers the top spring-pin pair at x 131.5 (+/- 2.9 mm of land round it);
  - the top edge of the window is chamfered where the wall is wide enough, so probe tips slide in.

usage (needs build123d): python test_shell.py OUT_DIR [--rev c|d]
Run one revision per process: importing case_rev_d changes rev C's settings (it drops the press-fit pins).
"""
import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CASE = HERE.parents[1]                       # hardware/band

ap = argparse.ArgumentParser()
ap.add_argument("out")
ap.add_argument("--rev", choices=("c", "d"), default="d")
ap.add_argument("--map-only", action="store_true", help="only write the probe map SVG")
args = ap.parse_args()

if args.rev == "d":
    sys.path.insert(0, str(CASE / "rev-d" / "case"))
    import case_rev_d as R                   # noqa: E402
    A = R.A
else:
    sys.path.insert(0, str(CASE / "rev-c" / "case"))
    import case_rev_c as R                   # noqa: E402
    A = R.A
sys.path.insert(0, str(CASE.parent / "tools"))
from build123d import Axis, Color, chamfer, export_step, export_stl  # noqa: E402

LAND_X0 = 128.4
A.LAND = (LAND_X0, A.CAV[1], A.CAV[2], 103.2)
POST = (131.75, A.CAV[1], 110.8, A.CAV[3])   # rev A's post over the bottom pin pair (case_rev_a.make_shell)
KEEP = 0.3                                   # roof kept round the land and post beyond their own footprint
WIN_X0 = A.BOARD[0] + 0.95 + KEEP            # 101.25: just past the antenna-strip posts (x <= 100.95)
WIN_Z0 = A.ROOF_IN - 0.2                     # cut from just under the roof's inside face to above the top
EDGE_CH = 0.5                                # 45 degree lead-in on the window's top edge


def window_face():
    win = A.rrect(WIN_X0, A.CAV[1] + 5, A.CAV[2], A.CAV[3], 0.5) & A.POCKET
    win -= A.rrect(A.LAND[0] - KEEP, A.CAV[1] + 5, A.CAV[2] - 5, A.LAND[3] + KEEP, 0.3)
    win -= A.rrect(POST[0] - KEEP, A.CAV[1] + 5, POST[2] - KEEP, A.CAV[3] + 5, 0.3)
    return win


def make_test_shell():
    s = R.make_shell()
    s -= A.slab(window_face(), WIN_Z0, A.TOP + 1)
    top = [e for e in s.edges().filter_by_position(Axis.Z, A.TOP - 1e-3, A.TOP + 1e-3)
           if WIN_X0 - 0.05 <= e.center().X <= A.CAV[1] + 0.05
           and A.CAV[2] - 0.05 <= e.center().Y <= A.CAV[3] + 0.05]
    try:
        s = chamfer(top, EDGE_CH)
    except Exception as exc:                 # the walls' rounded top edge leaves little flat: skip quietly
        print(f"window lead-in chamfer skipped ({exc})")
    return s


# top-side probe points that the window exposes (rev C board, rigid-rev-c.kicad_pcb), with what to expect
PROBES = (
    ("TP707", 131.6, 108.2, "GND", "meter black lead here"),
    ("C201", 124.0, 105.0, "VIN", "dock 5 V (about 4.7-5.0 V)"),
    ("TP705", 127.1, 101.6, "PMID", "charger output, about VIN"),
    ("TP706", 125.65, 109.0, "VBAT", "cell voltage (0 V if no cell)"),
    ("C10", 113.31, 108.905, "VDD_2V0", "nRF supply, 1.97-2.03 V"),
    ("C3", 114.475, 109.9, "VDD_2V0", "same rail, bigger pad"),
    ("R602", 115.8, 112.5, "SWDIO", "100R: dock side / chip side"),
    ("R601", 117.8, 112.5, "SWDCLK", "100R: dock side / chip side"),
    ("TP701", 105.215, 103.2, "nRESET", "about 2.0 V when running"),
    ("TP203", 131.6, 106.6, "/MR", "charger wake (do not short)"),
)


def write_probe_map(path):
    """Top view (looking down on F.Cu through the window), KiCad coordinates (y down), as a PNG."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle, FancyBboxPatch

    fig, ax = plt.subplots(figsize=(11, 6.4), dpi=130)

    def rect(x0, x1, y0, y1, fc, ec="none", r=0.0, z=1):
        ax.add_patch(FancyBboxPatch((x0 + r, y0 + r), x1 - x0 - 2 * r, y1 - y0 - 2 * r,
                                    boxstyle=f"round,pad={r}", fc=fc, ec=ec, lw=1.5, zorder=z))
    rect(A.X_A, A.X_E, A.Y0, A.Y1, "#f2a65a", "#a0581a", A.CORNER)              # shell, from above
    rect(*A.BOARD, "#2f6b3a", "#173d20", A.BOARD_R, z=2)                          # board through the window
    # what stays over the board: antenna strip, land, post
    rect(A.CAV[0], WIN_X0, A.CAV[2], A.CAV[3], "#f2a65a", z=3)
    rect(A.LAND[0] - KEEP, A.CAV[1], A.CAV[2], A.LAND[3] + KEEP, "#f2a65a", z=3)
    rect(POST[0] - KEEP, A.CAV[1], POST[2] - KEEP, A.CAV[3], "#f2a65a", z=3)
    for x, y in ((131.5, 101.1), (131.5, 103.3), (131.5, 111.7), (131.5, 113.9)):
        ax.add_patch(Circle((x, y), 0.7, fc="none", ec="#7a3d0c", ls="--", lw=1.2, zorder=4))
    ax.add_patch(Circle(A.SCREW, 1.1, fc="#d9d9d9", ec="#555", zorder=4))
    ax.text(A.SCREW[0], A.SCREW[1] + 2.2, "M2 screw", ha="center", fontsize=8, color="#555", zorder=5)
    ax.text(130.5, 98.6, "land / post: hold the board over the spring pins (dashed)", ha="center", fontsize=8,
            color="#7a3d0c")
    ax.text(98.4, 107.5, "antenna end", rotation=90, va="center", ha="center", fontsize=8, color="#7a3d0c")
    for i, (ref, x, y, net, note) in enumerate(PROBES, 1):
        ax.add_patch(Circle((x, y), 0.55, fc="#ffd400" if net != "GND" else "#ffffff", ec="k", lw=1.2, zorder=6))
        ax.text(x, y, str(i), ha="center", va="center", fontsize=7, weight="bold", zorder=7)
        col, row = (i - 1) // 5, (i - 1) % 5
        ax.text(A.X_A + col * 23, A.Y1 + 2.2 + row * 1.6, f"{i}  {ref}  {net}", fontsize=9, weight="bold", va="center")
        ax.text(A.X_A + col * 23 + 9.5, A.Y1 + 2.2 + row * 1.6, note, fontsize=9, va="center")
    ax.set_xlim(A.X_A - 1.5, A.X_E + 1.5)
    ax.set_ylim(A.Y1 + 2.2 + 5 * 1.6, A.Y0 - 2.5)                                  # y down, as in KiCad
    ax.set_aspect("equal"); ax.axis("off")
    ax.set_title("NudgeBand open test shell: top view and probe points (rev C board, parts side up)", fontsize=11)
    fig.savefig(path, bbox_inches="tight"); plt.close(fig)


def write_preview(shell, path):
    """Isometric picture of the test shell with the board (green slab) in place."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection

    def tris(shape, tol=0.05):
        v, f = shape.tessellate(tol, 0.3)
        p = [(q.X, q.Y, q.Z) for q in v]
        return [[p[a], p[b], p[c]] for a, b, c in f]
    fig = plt.figure(figsize=(9, 5.5), dpi=130)
    ax = fig.add_subplot(projection="3d")
    board = A.slab(A.rrect(*A.BOARD, A.BOARD_R), A.BOARD_B, A.BOARD_F)
    ax.add_collection3d(Poly3DCollection(tris(board), facecolors="#2f6b3a", shade=True))
    ax.add_collection3d(Poly3DCollection(tris(shell), facecolors="#f2a65a", shade=True))
    ax.set_xlim(96, 142); ax.set_ylim(119.5, 95.5); ax.set_zlim(-10, 20)
    ax.set_box_aspect((46, 24, 30)); ax.view_init(elev=38, azim=-62); ax.axis("off")
    fig.savefig(path, bbox_inches="tight"); plt.close(fig)


if __name__ == "__main__":
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    write_probe_map(out / "nudgeband-test-shell-probe-map.png")
    if args.map_only:
        sys.exit(0)
    tag = f"rev-{args.rev}"
    shell, cover = make_test_shell(), R.make_cover() if args.rev == "d" else A.make_cover()
    assert len(shell.solids()) == 1 and shell.is_valid, f"{len(shell.solids())} solids"
    bb = shell.bounding_box()
    print(f"test shell {tag}: valid, volume {shell.volume:.0f} mm3, bbox "
          f"{[round(v, 2) for v in bb.min]} .. {[round(v, 2) for v in bb.max]}")
    ov = shell & cover
    print("test shell vs cover overlap (closed):", round(ov.volume if ov is not None else 0, 4))
    # the three hold-downs still reach F.Cu: probe just below their faces
    for name, (x, y) in (("land", (131.5, 102.0)), ("post", (132.5, 112.5)), ("antenna post", (100.5, 102.0))):
        hit = shell & A.box(x - 0.1, x + 0.1, y - 0.1, y + 0.1, A.BOARD_F - 0.04, A.BOARD_F + 0.2)
        print(f"  {name} at ({x}, {y}) presses on F.Cu: {hit is not None and hit.volume > 1e-4}")
    # nothing left over the window between z F.Cu and the top
    over = shell & A.slab(window_face(), A.BOARD_F, A.TOP + 1)
    print("material over the window:", round(over.volume if over is not None else 0, 4), "mm3")
    if args.rev == "d":
        moving = cover + R.board_box()
        worst = 0.0
        for d in (1, 5, 10, 20, 30, 40, 60):
            r = shell & R.swung(moving, d)
            worst = max(worst, r.volume if r is not None else 0.0)
        print(f"swing 1-60 deg (rev D hook): worst overlap {worst:.4f} mm3")
    try:
        from printcheck import check, show
        show(check(f"test shell {tag} (top face down)", shell, flip=True,
              allow=[(A.CAV[0] - 1, A.CAV[1] + 1, A.Y1 - 1, A.Y1 + 1, 7.0, 8.6)]))
    except Exception as exc:
        print(f"print check not run ({exc})")
    p = A.to_step_frame(shell); p.label, p.color = f"band test shell {tag}", Color(0.95, 0.55, 0.10)
    export_step(p, str(out / f"nudgeband-test-shell-{tag}.step"))
    export_stl(p, str(out / f"nudgeband-test-shell-{tag}.stl"), tolerance=0.01, angular_tolerance=0.1)
    write_preview(shell, out / f"nudgeband-test-shell-{tag}-preview.png")
    print("written", out / f"nudgeband-test-shell-{tag}.stl")
