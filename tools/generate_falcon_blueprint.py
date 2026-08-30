#!/usr/bin/env python3
"""Generate CAD-derived orthographic reference sheets from the FALCON GLB.

Only Python's standard library is used so the drawing can be regenerated on the
project workstation. The output is a technical reference, not a fabrication
release; final dimensions still require Fusion Drawing and physical validation.
"""

from __future__ import annotations

import json
import math
import struct
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "dashboard-next/public/models/PROJECT-FALCON-V2.glb"
OUT = ROOT / "docs/blueprints/FALCON-BP-001-cad-orthographic.svg"


def mat_mul(a, b):
    return [[sum(a[r][k] * b[k][c] for k in range(4)) for c in range(4)] for r in range(4)]


def node_matrix(node):
    if "matrix" in node:
        m = node["matrix"]
        return [[m[c * 4 + r] for c in range(4)] for r in range(4)]
    tx, ty, tz = node.get("translation", [0, 0, 0])
    sx, sy, sz = node.get("scale", [1, 1, 1])
    x, y, z, w = node.get("rotation", [0, 0, 0, 1])
    rot = [
        [1 - 2*y*y - 2*z*z, 2*x*y - 2*z*w, 2*x*z + 2*y*w, 0],
        [2*x*y + 2*z*w, 1 - 2*x*x - 2*z*z, 2*y*z - 2*x*w, 0],
        [2*x*z - 2*y*w, 2*y*z + 2*x*w, 1 - 2*x*x - 2*y*y, 0],
        [0, 0, 0, 1],
    ]
    scale = [[sx,0,0,0],[0,sy,0,0],[0,0,sz,0],[0,0,0,1]]
    trans = [[1,0,0,tx],[0,1,0,ty],[0,0,1,tz],[0,0,0,1]]
    return mat_mul(trans, mat_mul(rot, scale))


def transform(m, p):
    x, y, z = p
    q = [sum(m[r][k] * (x, y, z, 1)[k] for k in range(4)) for r in range(3)]
    return tuple(q)


def load_glb(path):
    raw = path.read_bytes()
    magic, version, _ = struct.unpack_from("<4sII", raw, 0)
    if magic != b"glTF" or version != 2:
        raise ValueError("Expected a GLB 2.0 file")
    offset, doc, binary = 12, None, None
    while offset < len(raw):
        length, kind = struct.unpack_from("<II", raw, offset)
        offset += 8
        chunk = raw[offset:offset + length]
        offset += length
        if kind == 0x4E4F534A:
            doc = json.loads(chunk.rstrip(b"\0 \t\r\n"))
        elif kind == 0x004E4942:
            binary = chunk
    return doc, binary


def accessor(doc, blob, index):
    acc = doc["accessors"][index]
    view = doc["bufferViews"][acc["bufferView"]]
    sizes = {5121:("B",1), 5123:("H",2), 5125:("I",4), 5126:("f",4)}
    widths = {"SCALAR":1, "VEC2":2, "VEC3":3, "VEC4":4}
    code, size = sizes[acc["componentType"]]
    count = widths[acc["type"]]
    stride = view.get("byteStride", size * count)
    start = view.get("byteOffset", 0) + acc.get("byteOffset", 0)
    fmt = "<" + code * count
    return [struct.unpack_from(fmt, blob, start + i * stride) for i in range(acc["count"])]


def normal(a, b, c):
    u = (b[0]-a[0], b[1]-a[1], b[2]-a[2])
    v = (c[0]-a[0], c[1]-a[1], c[2]-a[2])
    n = (u[1]*v[2]-u[2]*v[1], u[2]*v[0]-u[0]*v[2], u[0]*v[1]-u[1]*v[0])
    length = math.sqrt(sum(q*q for q in n)) or 1
    return tuple(q / length for q in n)


def cad_edges(doc, blob):
    identity = [[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]]
    parents = {c:i for i,n in enumerate(doc["nodes"]) for c in n.get("children", [])}
    roots = [i for i in range(len(doc["nodes"])) if i not in parents]
    instances = []

    def walk(index, parent):
        node = doc["nodes"][index]
        world = mat_mul(parent, node_matrix(node))
        if "mesh" in node:
            instances.append((node.get("name", ""), doc["meshes"][node["mesh"]], world))
        for child in node.get("children", []):
            walk(child, world)

    for root in roots:
        walk(root, identity)

    result = []
    for name, mesh, world in instances:
        for primitive in mesh.get("primitives", []):
            if primitive.get("mode", 4) != 4 or "POSITION" not in primitive.get("attributes", {}):
                continue
            vertices = [transform(world, p) for p in accessor(doc, blob, primitive["attributes"]["POSITION"])]
            if "indices" in primitive:
                indices = [x[0] for x in accessor(doc, blob, primitive["indices"])]
            else:
                indices = list(range(len(vertices)))
            adjacency = defaultdict(list)
            for i in range(0, len(indices) - 2, 3):
                tri = indices[i:i+3]
                n = normal(vertices[tri[0]], vertices[tri[1]], vertices[tri[2]])
                for a, b in ((tri[0],tri[1]), (tri[1],tri[2]), (tri[2],tri[0])):
                    adjacency[tuple(sorted((a,b)))].append(n)
            for (a, b), normals in adjacency.items():
                keep = len(normals) == 1
                if len(normals) > 1:
                    dot = sum(normals[0][k] * normals[1][k] for k in range(3))
                    keep = dot < 0.88
                if keep:
                    result.append((vertices[a], vertices[b], name))
    return result


def esc(value):
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def drawing(edges):
    width, height = 1684, 1191
    all_points = [p for edge in edges for p in edge[:2]]
    mins = [min(p[i] for p in all_points) for i in range(3)]
    maxs = [max(p[i] for p in all_points) for i in range(3)]

    views = [
        ("FRONT ELEVATION", 0, 2, (55, 145, 760, 720)),
        ("RIGHT ELEVATION", 1, 2, (845, 145, 380, 345)),
        ("PLAN VIEW", 0, 1, (1250, 145, 380, 345)),
    ]
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
           '<defs><style>.border{fill:none;stroke:#111;stroke-width:1}.object{fill:none;stroke:#111;stroke-width:.72;stroke-linecap:round}.center{fill:none;stroke:#555;stroke-width:.7;stroke-dasharray:10 3 2 3}.dim{fill:none;stroke:#222;stroke-width:.75}.title{font-family:Arial,sans-serif;font-size:24px;font-weight:700}.head{font-family:Arial,sans-serif;font-size:13px;font-weight:700}.txt{font-family:Arial,sans-serif;font-size:12px}.small{font-family:Arial,sans-serif;font-size:10px}.tiny{font-family:Arial,sans-serif;font-size:8px}.warn{font-family:Arial,sans-serif;font-size:14px;font-weight:700;fill:#b00020}</style><marker id="arr" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto"><path d="M8 4 0 0v8z" fill="#222"/></marker></defs>',
           '<rect width="1684" height="1191" fill="#fff"/><rect x="20" y="20" width="1644" height="1151" class="border"/>',
           '<text x="45" y="60" class="title">PROJECT FALCON — CAD-DERIVED GENERAL ARRANGEMENT</text>',
           '<text x="45" y="86" class="txt">PROPOSED REPLACEMENT PROTOTYPE · V2 REFERENCE GEOMETRY · DIMENSIONS IN mm UNLESS NOTED</text>']

    for label, ax, ay, (x, y, w, h) in views:
        lowx, highx = mins[ax], maxs[ax]
        lowy, highy = mins[ay], maxs[ay]
        scale = min((w-40)/(highx-lowx), (h-55)/(highy-lowy))
        ox = x + w/2 - (lowx+highx)/2*scale
        oy = y + h/2 + (lowy+highy)/2*scale
        out += [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" class="border"/>',
                f'<text x="{x+10}" y="{y+20}" class="head">{label}</text>',
                f'<path d="M{x+w/2} {y+30}V{y+h-10} M{x+10} {y+h/2}H{x+w-10}" class="center"/>']
        projected = {}
        for a, b, _ in edges:
            x1, y1 = ox+a[ax]*scale, oy-a[ay]*scale
            x2, y2 = ox+b[ax]*scale, oy-b[ay]*scale
            if x-2 <= x1 <= x+w+2 and y-2 <= y1 <= y+h+2 and x-2 <= x2 <= x+w+2 and y-2 <= y2 <= y+h+2:
                q1, q2 = (round(x1), round(y1)), (round(x2), round(y2))
                if q1 == q2:
                    continue
                key = tuple(sorted((q1, q2)))
                projected[key] = (x1, y1, x2, y2, math.hypot(x2-x1, y2-y1))
        # GLB tessellation can duplicate coincident triangle boundaries. Keep a
        # bounded set of the longest unique projected features for readable,
        # performant engineering linework.
        selected = sorted(projected.values(), key=lambda item: item[4], reverse=True)[:10000]
        paths = [f'M{x1:.1f} {y1:.1f}L{x2:.1f} {y2:.1f}' for x1,y1,x2,y2,_ in selected]
        out.append(f'<path d="{" ".join(paths)}" class="object"/>')

    # Reference dimension register and release notes.
    out += ['<rect x="845" y="515" width="785" height="350" class="border"/>',
            '<text x="860" y="540" class="head">PRINCIPAL DIMENSION REGISTER — CAD REFERENCE ONLY</text>']
    rows = [
        ("A", "MAIN FLOAT", "Ø650 × 620 O/A", "6 mm HDPE wall; upper cylinder 380; keel 240"),
        ("B", "MAST / FRAME", "800 high", "420 base / 380 shoulder / 260 top"),
        ("C", "ELECTRONICS POD", "300 × 280 × 400", "8 mm UV-HDPE wall; 18 mm service lid"),
        ("D", "SOLAR MODULES", "2 × 450 × 300 × 20", "30 W each; 20° outward tilt"),
        ("E", "PRESSURE GUARD", "Ø64 × 72", "Sensor envelope Ø24 × 42; offset 125"),
        ("F", "BALLAST RAIL", "Ø40 × 500", "4 × Ø220 × 25 removable plates"),
        ("G", "ANCHOR", "650 / 450 × 500", "Nominal 367 kg — calculation/approval required"),
    ]
    yy = 570
    for code, item, dim, note in rows:
        out += [f'<line x1="845" y1="{yy+12}" x2="1630" y2="{yy+12}" class="border"/>',
                f'<text x="860" y="{yy}" class="head">{code}</text>', f'<text x="900" y="{yy}" class="txt">{esc(item)}</text>',
                f'<text x="1100" y="{yy}" class="txt">{esc(dim)}</text>', f'<text x="1280" y="{yy}" class="small">{esc(note)}</text>']
        yy += 40
    out += ['<rect x="55" y="895" width="780" height="205" class="border"/>',
            '<text x="70" y="920" class="head">GENERAL NOTES</text>',
            '<text x="70" y="947" class="txt">1. LINEWORK IS PROJECTED DIRECTLY FROM PROJECT-FALCON-V2.GLB.</text>',
            '<text x="70" y="973" class="txt">2. DO NOT SCALE DRAWING. VERIFY ALL DIMENSIONS IN NATIVE FUSION SOURCE.</text>',
            '<text x="70" y="999" class="txt">3. ORANGE PI IS EXCLUDED FROM BUOY; COMPUTE IS AT THE SHORE BAY STATION.</text>',
            '<text x="70" y="1025" class="txt">4. WATERLINE, FREEBOARD, C.G., DISPLACEMENT AND RIGHTING MOMENT ARE TBD.</text>',
            '<text x="70" y="1051" class="txt">5. COMPLETE INTERFERENCE, STRUCTURAL, INGRESS AND FLOTATION REVIEWS BEFORE BUILD.</text>',
            '<text x="70" y="1080" class="warn">REFERENCE / NOT FOR FABRICATION</text>']
    out += ['<rect x="845" y="895" width="785" height="205" class="border"/>',
            '<line x1="845" y1="965" x2="1630" y2="965" class="border"/><line x1="1180" y1="895" x2="1180" y2="1100" class="border"/>',
            '<text x="860" y="923" class="head">PROJECT</text><text x="860" y="950" class="title">FALCON-01</text>',
            '<text x="1195" y="923" class="head">DRAWING TITLE</text><text x="1195" y="949" class="txt">GENERAL ARRANGEMENT</text>',
            '<text x="860" y="990" class="small">DRAWING NO.</text><text x="950" y="990" class="head">FALCON-BP-001</text>',
            '<text x="1195" y="990" class="small">REVISION</text><text x="1270" y="990" class="head">P1</text>',
            '<text x="860" y="1025" class="small">SCALE</text><text x="950" y="1025" class="head">NTS</text>',
            '<text x="1195" y="1025" class="small">DATE</text><text x="1270" y="1025" class="head">2026-08-30</text>',
            '<text x="860" y="1060" class="small">SOURCE</text><text x="950" y="1060" class="txt">FUSION V2 / GLB</text>',
            '<text x="1195" y="1060" class="small">STATUS</text><text x="1270" y="1060" class="warn">REFERENCE</text>',
            '<text x="860" y="1087" class="tiny">UNCONTROLLED WHEN PRINTED · APPROVAL SIGNATURES REQUIRED FOR RELEASE</text>',
            '</svg>']
    return "\n".join(out)


def main():
    doc, blob = load_glb(MODEL)
    edges = cad_edges(doc, blob)
    OUT.write_text(drawing(edges), encoding="utf-8")
    print(f"Generated {OUT.relative_to(ROOT)} from {len(edges):,} feature edges")


if __name__ == "__main__":
    main()
