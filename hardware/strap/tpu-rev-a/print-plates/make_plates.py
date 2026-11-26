"""Lay the TPU strap parts out on Bambu Lab X1C plates (256 x 256 mm) as 3MF files.
    python make_plates.py      (run from this folder; reads the STLs one level up)"""
import os, zipfile
import numpy as np
import trimesh

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
P, GAP, MARGIN = 256.0, 7.0, 10.0


def load(n):
    m = trimesh.load(os.path.join(SRC, f"nudgeband-strap-tpu-rev-a-{n}.stl"))
    m.merge_vertices()
    m.apply_translation(-m.bounds[0])
    return m


def write_3mf(path, objs):
    res, items = [], []
    for i, (name, m) in enumerate(objs, 1):
        v = "".join(f'<vertex x="{a:.4f}" y="{b:.4f}" z="{c:.4f}"/>' for a, b, c in m.vertices)
        t = "".join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in m.faces)
        res.append(f'<object id="{i}" name="{name}" type="model"><mesh><vertices>{v}</vertices>'
                   f'<triangles>{t}</triangles></mesh></object>')
        items.append(f'<item objectid="{i}"/>')
    model = ('<?xml version="1.0" encoding="UTF-8"?>\n<model unit="millimeter" xml:lang="en-US" '
             'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">'
             '<metadata name="Title">NudgeBand TPU strap rev A</metadata>'
             f'<resources>{"".join(res)}</resources><build>{"".join(items)}</build></model>')
    ct = ('<?xml version="1.0" encoding="UTF-8"?>\n<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
          '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
          '<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
    rels = ('<?xml version="1.0" encoding="UTF-8"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Target="/3D/3dmodel.model" Id="rel0" '
            'Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", ct)
        z.writestr("_rels/.rels", rels)
        z.writestr("3D/3dmodel.model", model)


def plate(name, rows):
    """rows of part names, laid left to right, rows stacked; the whole layout is centred on the plate"""
    placed, y, W = [], 0.0, 0.0
    for row in rows:
        x, h = 0.0, 0.0
        for n in row:
            m = load(n)
            m.apply_translation([x, y, 0])
            placed.append((n, m))
            x += m.extents[0] + GAP
            h = max(h, m.extents[1])
        W, y = max(W, x - GAP), y + h + GAP
    H = y - GAP
    assert W <= P - 2 * MARGIN and H <= P - 2 * MARGIN, (name, W, H)
    objs = []
    for i, (n, m) in enumerate(placed, 1):
        m.apply_translation([(P - W) / 2, (P - H) / 2, 0])
        objs.append((f"{n}-{i}", m))
    write_3mf(os.path.join(HERE, name + ".3mf"), objs)
    print(f"{name}: {W:.0f} x {H:.0f} mm, {len(objs)} parts")


if __name__ == "__main__":
    plate("plate-1-fit-coupon", [["fit-coupon"], ["keeper"]])
    for s in ("S", "M", "L", "XL"):
        plate(f"plate-2-{s}", [[f"{s}-long"], [f"{s}-short", "keeper"]])
    plate("plate-3-all-sizes", [["XL-long"], ["L-long"], ["M-long"], ["S-long"], ["XL-short", "keeper"], ["L-short", "keeper"],
                                ["M-short", "keeper"], ["S-short", "keeper"]])
