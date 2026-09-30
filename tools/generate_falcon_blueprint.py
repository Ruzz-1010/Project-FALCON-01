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
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "dashboard-next/public/models/PROJECT-FALCON-V2.glb"
OUT = ROOT / "docs/blueprints/FALCON-BP-001-cad-orthographic.svg"
OUT_POD = ROOT / "docs/blueprints/FALCON-BP-002-electronics-pod.svg"
OUT_FLOAT = ROOT / "docs/blueprints/FALCON-BP-003-metal-drum-dimensions.svg"
OUT_STRUCTURE = ROOT / "docs/blueprints/FALCON-BP-004-tower-structural-dimensions.svg"
OUT_HARDWARE = ROOT / "docs/blueprints/FALCON-BP-005-external-hardware-dimensions.svg"
OUT_EQUIPMENT = ROOT / "docs/blueprints/FALCON-BP-006-electronics-equipment-layout.svg"


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
                boundary = len(normals) == 1
                hard = boundary
                silhouette_axes = set()
                if len(normals) > 1:
                    dot = sum(normals[0][k] * normals[1][k] for k in range(3))
                    # Preserve moderately curved manufactured features in the
                    # general arrangement (sensor cups, guards, fairings and
                    # tube transitions) instead of retaining only sharp 28°+
                    # edges. View-specific silhouette filtering below prevents
                    # unrelated triangle clutter from leaking into each view.
                    hard = dot < 0.96
                    silhouette_axes = {
                        k for k in range(3)
                        if normals[0][k] * normals[1][k] <= 0
                    }
                if hard or silhouette_axes:
                    # Store why an edge was retained. A silhouette is valid
                    # only for its matching viewing axis; drawing every axis'
                    # silhouette in every view caused radial/triangulation
                    # clutter in the earlier detail sheets.
                    result.append((vertices[a], vertices[b], name, hard, silhouette_axes))
    return result


def esc(value):
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def clip_segment(x1, y1, x2, y2, left, top, right, bottom):
    """Clip a projected feature instead of dropping a partly visible line."""
    dx, dy = x2 - x1, y2 - y1
    p = (-dx, dx, -dy, dy)
    q = (x1 - left, right - x1, y1 - top, bottom - y1)
    u1, u2 = 0.0, 1.0
    for pi, qi in zip(p, q):
        if abs(pi) < 1e-12:
            if qi < 0:
                return None
            continue
        t = qi / pi
        if pi < 0:
            u1 = max(u1, t)
        else:
            u2 = min(u2, t)
        if u1 > u2:
            return None
    return x1 + u1 * dx, y1 + u1 * dy, x1 + u2 * dx, y1 + u2 * dy


def finish_svg(svg):
    """Apply consistent print-safe line rendering to every blueprint sheet."""
    common = ("svg{shape-rendering:geometricPrecision}"
              "path,line,polyline,polygon,rect,circle,ellipse{"
              "vector-effect:non-scaling-stroke;stroke-linejoin:round;"
              "stroke-linecap:round}")
    return svg.replace("<style>", f"<style>{common}", 1)


def cad_detail_sheet(edges, title, drawing_no, panels, register):
    """Create a real CAD-projected detail sheet from selected Fusion geometry."""
    width, height = 1684, 1191
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
           '<defs><style>.b{fill:none;stroke:#263746;stroke-width:1}.o{fill:none;stroke:#3f5362;stroke-width:.9}.c{fill:none;stroke:#94a3b8;stroke-width:.7;stroke-dasharray:10 3 2 3}.d{fill:none;stroke:#475569;stroke-width:.9}.title{font-family:Arial,sans-serif;font-size:24px;font-weight:700;fill:#172635}.h{font-family:Arial,sans-serif;font-size:13px;font-weight:700;fill:#243746}.t{font-family:Arial,sans-serif;font-size:11px;fill:#334155}.s{font-family:Arial,sans-serif;font-size:9px;fill:#475569}.w{font-family:Arial,sans-serif;font-size:13px;font-weight:700;fill:#9f1239}</style><marker id="cadarr" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto"><path d="M8 4 0 0v8z" fill="#475569"/></marker></defs>',
           '<rect width="1684" height="1191" fill="#f8fafc"/><rect x="20" y="20" width="1644" height="1151" class="b"/>',
           f'<text x="45" y="58" class="title">{esc(title)}</text>',
           '<text x="45" y="84" class="t">FUSION V2 CAD-PROJECTED FEATURE LINEWORK · ORTHOGRAPHIC REFERENCE · DIMENSIONS IN metres (m)</text>']

    for panel in panels:
        label, terms, ax, ay, box = panel
        x, y, w, h = box
        view_axis = ({0, 1, 2} - {ax, ay}).pop()
        selected_edges = [
            e for e in edges
            if any(term in e[2].upper() for term in terms)
            and (e[3] or view_axis in e[4])
        ]
        out += [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" class="b"/>',
                f'<text x="{x+12}" y="{y+24}" class="h">{esc(label)}</text>']
        if not selected_edges:
            out.append(f'<text x="{x+20}" y="{y+60}" class="w">NO MATCHING CAD GEOMETRY</text>')
            continue
        points = [p for e in selected_edges for p in e[:2]]
        lo = [min(p[i] for p in points) for i in range(3)]
        hi = [max(p[i] for p in points) for i in range(3)]
        # GLB coordinates are metres. Use a millimetre-scale epsilon; using
        # `1` here incorrectly forced every sub-metre component into a 1 m
        # envelope and made its projected linework look tiny/incomplete.
        spanx, spany = max(hi[ax]-lo[ax], .001), max(hi[ay]-lo[ay], .001)
        scale = min((w-90)/spanx, (h-105)/spany)
        ox = x+w/2-(lo[ax]+hi[ax])*scale/2
        oy = y+h/2+(lo[ay]+hi[ay])*scale/2+8
        out += [f'<line x1="{x+w/2}" y1="{y+38}" x2="{x+w/2}" y2="{y+h-30}" class="c"/>',
                f'<line x1="{x+20}" y1="{y+h/2}" x2="{x+w-20}" y2="{y+h/2}" class="c"/>']
        unique = {}
        for a, b, _, _, _ in selected_edges:
            segment = clip_segment(ox+a[ax]*scale, oy-a[ay]*scale,
                                   ox+b[ax]*scale, oy-b[ay]*scale,
                                   x+8, y+35, x+w-8, y+h-32)
            if not segment:
                continue
            x1,y1,x2,y2 = segment
            q1,q2=(round(x1,1),round(y1,1)),(round(x2,1),round(y2,1))
            if q1 != q2:
                unique[tuple(sorted((q1,q2)))] = segment
        # Discard sub-pixel tessellation remnants that do not survive print.
        clean = [segment for segment in unique.values()
                 if math.hypot(segment[2]-segment[0], segment[3]-segment[1]) >= 1.25]
        paths = [f'M{x1:.1f} {y1:.1f}L{x2:.1f} {y2:.1f}' for x1,y1,x2,y2 in clean]
        out.append(f'<path d="{" ".join(paths)}" class="o"/>')
        out.append(f'<text x="{x+12}" y="{y+h-10}" class="s">CAD ENVELOPE: {spanx:.3f} × {spany:.3f} m · DO NOT SCALE</text>')

    out += ['<rect x="40" y="790" width="1010" height="305" class="b"/>',
            '<text x="55" y="817" class="h">CONTROLLED COMPONENT / DIMENSION REGISTER</text>',
            '<line x1="40" y1="835" x2="1050" y2="835" class="b"/>']
    yy = 864
    for code, item, dimension, note in register:
        out += [f'<text x="55" y="{yy}" class="h">{esc(code)}</text>',
                f'<text x="105" y="{yy}" class="t">{esc(item)}</text>',
                f'<text x="390" y="{yy}" class="t">{esc(dimension)}</text>',
                f'<text x="610" y="{yy}" class="s">{esc(note)}</text>',
                f'<line x1="40" y1="{yy+11}" x2="1050" y2="{yy+11}" class="b"/>']
        yy += 36
    out += ['<rect x="1080" y="790" width="560" height="305" class="b"/>',
            '<text x="1095" y="817" class="h">ENGINEERING / RELEASE NOTES</text>',
            '<text x="1095" y="852" class="t">1. LINEWORK IS PROJECTED FROM THE CURRENT FUSION V2 GLB.</text>',
            '<text x="1095" y="882" class="t">2. VERIFY ALL DIMENSIONS IN THE NATIVE PARAMETRIC MODEL.</text>',
            '<text x="1095" y="912" class="t">3. COMPLETE MATERIAL, LOAD, SEAL AND INTERFERENCE REVIEWS.</text>',
            '<text x="1095" y="942" class="t">4. PURCHASED-PART HOLES REQUIRE APPROVED DATASHEETS.</text>',
            '<text x="1095" y="982" class="w">REFERENCE — NOT FOR FABRICATION</text>',
            '<line x1="1080" y1="1010" x2="1640" y2="1010" class="b"/>',
            f'<text x="1095" y="1040" class="s">DRAWING</text><text x="1180" y="1040" class="h">{esc(drawing_no)}</text>',
            '<text x="1370" y="1040" class="s">REV.</text><text x="1430" y="1040" class="h">P4</text>',
            '<text x="1095" y="1075" class="s">PROJECT</text><text x="1180" y="1075" class="h">FALCON-01</text>',
            '<text x="1370" y="1075" class="s">STATUS</text><text x="1430" y="1075" class="w">REFERENCE</text>',
            '</svg>']
    return finish_svg("\n".join(out))


def drawing(edges):
    width, height = 1684, 1191
    internal_terms = (
        "BATTERY", "BMS", "MPPT", "DC_DC", "FUSED", "DISCONNECT",
        "ORANGE_PI", "ESP32", "MODEM_ENVELOPE", "DISTRIBUTION_BOARD",
        "FAN_", "AIR_GUIDE", "HEAT_SINK", "THERMAL_BRIDGE", "LEAK_TRAY",
        "GASKET", "HINGE", "LATCH", "FASTENER", "MEMBRANE_VENT",
    )
    mooring_terms = ("ANCHOR", "CHAIN", "BALLAST", "SHACKLE", "LANYARD", "CLEVIS")

    def exterior(edge):
        name = edge[2].upper()
        return (not any(term in name for term in internal_terms + mooring_terms)
                and max(edge[0][2], edge[1][2]) > 1.8)

    def mooring(edge):
        name = edge[2].upper()
        return any(term in name for term in mooring_terms)

    views = [
        ("FRONT ELEVATION — BUOY ASSEMBLY", 0, 2, (55, 145, 760, 465), exterior, 7000),
        ("MOORING / BALLAST ELEVATION", 0, 2, (55, 625, 760, 240), mooring, 4500),
        ("RIGHT ELEVATION", 1, 2, (845, 145, 380, 345), exterior, 4500),
        ("PLAN VIEW", 0, 1, (1250, 145, 380, 345), exterior, 4500),
    ]
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
           '<defs><style>.border{fill:none;stroke:#253746;stroke-width:1}.object{fill:none;stroke:#3f5362;stroke-width:.82}.center{fill:none;stroke:#94a3b8;stroke-width:.65;stroke-dasharray:10 3 2 3}.dim{fill:none;stroke:#334155;stroke-width:.75}.title{font-family:Arial,sans-serif;font-size:24px;font-weight:700;fill:#172635}.head{font-family:Arial,sans-serif;font-size:13px;font-weight:700;fill:#243746}.txt{font-family:Arial,sans-serif;font-size:12px;fill:#334155}.small{font-family:Arial,sans-serif;font-size:10px;fill:#475569}.tiny{font-family:Arial,sans-serif;font-size:8px;fill:#64748b}.warn{font-family:Arial,sans-serif;font-size:14px;font-weight:700;fill:#9f1239}</style><marker id="arr" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto"><path d="M8 4 0 0v8z" fill="#334155"/></marker></defs>',
           '<rect width="1684" height="1191" fill="#f8fafc"/><rect x="20" y="20" width="1644" height="1151" class="border"/>',
           '<text x="45" y="60" class="title">PROJECT FALCON — CAD-DERIVED GENERAL ARRANGEMENT</text>',
           '<text x="45" y="86" class="txt">PROPOSED REPLACEMENT PROTOTYPE · V2 REFERENCE GEOMETRY · DIMENSIONS IN mm UNLESS NOTED</text>']

    for label, ax, ay, (x, y, w, h), predicate, limit in views:
        view_axis = ({0, 1, 2} - {ax, ay}).pop()
        view_edges = [edge for edge in edges
                      if predicate(edge) and (edge[3] or view_axis in edge[4])]
        all_points = [p for edge in view_edges for p in edge[:2]]
        mins = [min(p[i] for p in all_points) for i in range(3)]
        maxs = [max(p[i] for p in all_points) for i in range(3)]
        lowx, highx = mins[ax], maxs[ax]
        lowy, highy = mins[ay], maxs[ay]
        scale = min((w-40)/(highx-lowx), (h-55)/(highy-lowy))
        ox = x + w/2 - (lowx+highx)/2*scale
        oy = y + h/2 + (lowy+highy)/2*scale
        out += [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" class="border"/>',
                f'<text x="{x+10}" y="{y+20}" class="head">{label}</text>',
                f'<line x1="{x+w/2}" y1="{y+30}" x2="{x+w/2}" y2="{y+h-10}" class="center"/><line x1="{x+10}" y1="{y+h/2}" x2="{x+w-10}" y2="{y+h/2}" class="center"/>']
        projected = {}
        for a, b, _, _, _ in view_edges:
            x1, y1 = ox+a[ax]*scale, oy-a[ay]*scale
            x2, y2 = ox+b[ax]*scale, oy-b[ay]*scale
            clipped = clip_segment(x1, y1, x2, y2, x+2, y+32, x+w-2, y+h-2)
            if clipped:
                x1, y1, x2, y2 = clipped
                q1, q2 = (round(x1), round(y1)), (round(x2), round(y2))
                if q1 == q2:
                    continue
                key = tuple(sorted((q1, q2)))
                projected[key] = (x1, y1, x2, y2, math.hypot(x2-x1, y2-y1))
        # GLB tessellation can duplicate coincident triangle boundaries. Keep a
        # bounded set of the longest unique projected features for readable,
        # performant engineering linework.
        selected = sorted(projected.values(), key=lambda item: item[4], reverse=True)[:max(limit, 20000)]
        paths = [f'M{x1:.1f} {y1:.1f}L{x2:.1f} {y2:.1f}' for x1,y1,x2,y2,_ in selected]
        out.append(f'<path d="{" ".join(paths)}" class="object"/>')

    out += ['<line x1="210" y1="575" x2="210" y2="596" class="dim"/><line x1="660" y1="575" x2="660" y2="596" class="dim"/><line x1="210" y1="590" x2="660" y2="590" class="dim" marker-start="url(#arr)" marker-end="url(#arr)"/>',
            '<text x="405" y="585" class="head">Ø650 CAD REF</text>',
            '<line x1="785" y1="205" x2="803" y2="205" class="dim"/><line x1="785" y1="530" x2="803" y2="530" class="dim"/><line x1="798" y1="205" x2="798" y2="530" class="dim" marker-start="url(#arr)" marker-end="url(#arr)"/>',
            '<text x="790" y="385" class="head" transform="rotate(-90 790 385)">800 MAST CAD REF</text>']

    # Reference dimension register and release notes.
    out += ['<rect x="845" y="515" width="785" height="350" class="border"/>',
            '<text x="860" y="540" class="head">COMPONENT / DIMENSION SCHEDULE — CAD REFERENCE ONLY</text>']
    rows = [
        ("A", "MAIN FLOAT", "Ø650 × 620 O/A", "6 mm HDPE wall; upper cylinder 380; keel 240"),
        ("B", "MAST / FRAME", "800 high", "420 base / 380 shoulder / 260 top"),
        ("C", "ELECTRONICS POD", "300 × 280 × 400", "8 mm UV-HDPE wall; 18 mm service lid"),
        ("D", "SOLAR MODULES", "2 × 450 × 300 × 20", "30 W each; 20° outward tilt"),
        ("E", "PRESSURE GUARD", "Ø64 × 72", "Sensor envelope Ø24 × 42; offset 125"),
        ("F", "BALLAST RAIL", "Ø40 × 500", "4 × Ø220 × 25 removable plates"),
        ("G", "ANCHOR", "650 / 450 × 500", "Nominal 367 kg — calculation/approval required"),
        ("H", "TOP SENSOR ARRAY", "LOCATION TBD", "Wind + GNSS + LTE + navigation light"),
        ("I", "CONTROL SYSTEM", "INTERNAL FIT TBD", "ESP32 + LTE modem + protected sensor I/O"),
    ]
    yy = 566
    for code, item, dim, note in rows:
        out += [f'<line x1="845" y1="{yy+10}" x2="1630" y2="{yy+10}" class="border"/>',
                f'<text x="860" y="{yy}" class="head">{code}</text>', f'<text x="900" y="{yy}" class="txt">{esc(item)}</text>',
                f'<text x="1100" y="{yy}" class="txt">{esc(dim)}</text>', f'<text x="1280" y="{yy}" class="small">{esc(note)}</text>']
        yy += 34
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
    return finish_svg("\n".join(out))


def pod_drawing(edges):
    """Create a dedicated electronics-pod mechanical arrangement sheet."""
    pod_terms = (
        "RECT_POD", "LIFEPO4", "BATTERY_BMS", "MPPT", "DC_DC",
        "FUSED_POWER", "MAIN_BATTERY", "ESP32", "LTE_4G_MODEM",
        "SENSOR_DISTRIBUTION", "SOLAR_SURGE", "FAN_", "THERMAL_BRIDGE",
        "HEAT_SINK", "AIR_GUIDE", "AIRFLOW_BAFFLE",
    )
    pod_edges = [e for e in edges if any(t in e[2].upper() for t in pod_terms)
                 and "ORANGE_PI" not in e[2].upper()]
    views = [
        ("FRONT INTERNAL ARRANGEMENT", 0, 2, (55, 145, 760, 545), 7500),
        ("PLAN / DECK ARRANGEMENT", 0, 1, (845, 145, 785, 330), 6500),
        ("RIGHT ELEVATION", 1, 2, (845, 500, 380, 300), 4500),
    ]
    out = ['<svg xmlns="http://www.w3.org/2000/svg" width="1684" height="1191" viewBox="0 0 1684 1191">',
           '<defs><style>.border{fill:none;stroke:#253746;stroke-width:1}.object{fill:none;stroke:#526574;stroke-width:.62;stroke-linecap:round}.center{fill:none;stroke:#94a3b8;stroke-width:.65;stroke-dasharray:10 3 2 3}.dim{fill:none;stroke:#334155;stroke-width:.75}.call{fill:#f8fafc;stroke:#334155;stroke-width:1}.title{font-family:Arial,sans-serif;font-size:24px;font-weight:700;fill:#172635}.head{font-family:Arial,sans-serif;font-size:13px;font-weight:700;fill:#243746}.txt{font-family:Arial,sans-serif;font-size:12px;fill:#334155}.small{font-family:Arial,sans-serif;font-size:10px;fill:#475569}.tiny{font-family:Arial,sans-serif;font-size:8px;fill:#64748b}.warn{font-family:Arial,sans-serif;font-size:14px;font-weight:700;fill:#9f1239}</style><marker id="arr2" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto"><path d="M8 4 0 0v8z" fill="#334155"/></marker></defs>',
           '<rect width="1684" height="1191" fill="#f8fafc"/><rect x="20" y="20" width="1644" height="1151" class="border"/>',
           '<text x="45" y="60" class="title">PROJECT FALCON — SEALED ELECTRONICS POD ARRANGEMENT</text>',
           '<text x="45" y="86" class="txt">MECHANICAL PLACEMENT REFERENCE · 300 × 280 × 400 mm POD · ORANGE PI EXCLUDED</text>']
    for label, ax, ay, (x, y, w, h), limit in views:
        view_axis = ({0, 1, 2} - {ax, ay}).pop()
        visible_edges = [e for e in pod_edges if e[3] or view_axis in e[4]]
        pts = [p for e in visible_edges for p in e[:2]]
        mins = [min(p[i] for p in pts) for i in range(3)]
        maxs = [max(p[i] for p in pts) for i in range(3)]
        lowx, highx, lowy, highy = mins[ax], maxs[ax], mins[ay], maxs[ay]
        scale = min((w-50)/(highx-lowx), (h-55)/(highy-lowy))
        ox = x+w/2-(lowx+highx)/2*scale; oy = y+h/2+(lowy+highy)/2*scale
        out += [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" class="border"/>',
                f'<text x="{x+10}" y="{y+20}" class="head">{label}</text>',
                f'<line x1="{x+w/2}" y1="{y+30}" x2="{x+w/2}" y2="{y+h-10}" class="center"/><line x1="{x+10}" y1="{y+h/2}" x2="{x+w-10}" y2="{y+h/2}" class="center"/>']
        projected = {}
        for a,b,_,_,_ in visible_edges:
            x1,y1,x2,y2=ox+a[ax]*scale,oy-a[ay]*scale,ox+b[ax]*scale,oy-b[ay]*scale
            if x-2<=x1<=x+w+2 and y-2<=y1<=y+h+2 and x-2<=x2<=x+w+2 and y-2<=y2<=y+h+2:
                q1,q2=(round(x1),round(y1)),(round(x2),round(y2))
                if q1!=q2: projected[tuple(sorted((q1,q2)))]=(x1,y1,x2,y2,math.hypot(x2-x1,y2-y1))
        selected=sorted(projected.values(),key=lambda q:q[4],reverse=True)[:limit]
        out.append('<path d="'+' '.join(f'M{a:.1f} {b:.1f}L{c:.1f} {d:.1f}' for a,b,c,d,_ in selected)+'" class="object"/>')

    out += ['<path d="M275 670V696 M595 670V696 M275 690H595" class="dim" marker-start="url(#arr2)" marker-end="url(#arr2)"/>',
            '<text x="418" y="685" class="head">300</text>',
            '<path d="M600 172H632 M600 598H632 M625 172V598" class="dim" marker-start="url(#arr2)" marker-end="url(#arr2)"/>',
            '<text x="618" y="400" class="head" transform="rotate(-90 618 400)">400</text>',
            '<path d="M1110 455V480 M1390 455V480 M1110 472H1390" class="dim" marker-start="url(#arr2)" marker-end="url(#arr2)"/>',
            '<text x="1238" y="467" class="head">280</text>',
            '<path d="M180 520H300" class="dim"/><circle cx="170" cy="520" r="13" class="call"/><text x="163" y="525" class="head">01</text>',
            '<path d="M180 450H330" class="dim"/><circle cx="170" cy="450" r="13" class="call"/><text x="163" y="455" class="head">02</text>',
            '<path d="M690 450H545" class="dim"/><circle cx="700" cy="450" r="13" class="call"/><text x="693" y="455" class="head">03</text>',
            '<path d="M180 418H330" class="dim"/><circle cx="170" cy="418" r="13" class="call"/><text x="163" y="423" class="head">04</text>',
            '<path d="M690 418H545" class="dim"/><circle cx="700" cy="418" r="13" class="call"/><text x="693" y="423" class="head">05</text>',
            '<path d="M180 385H330" class="dim"/><circle cx="170" cy="385" r="13" class="call"/><text x="163" y="390" class="head">06</text>',
            '<path d="M690 385H545" class="dim"/><circle cx="700" cy="385" r="13" class="call"/><text x="693" y="390" class="head">07</text>',
            '<path d="M180 310H350" class="dim"/><circle cx="170" cy="310" r="13" class="call"/><text x="163" y="315" class="head">08</text>',
            '<path d="M690 310H545" class="dim"/><circle cx="700" cy="310" r="13" class="call"/><text x="693" y="315" class="head">09</text>',
            '<text x="285" y="245" class="head">UPPER CONTROL / COMMUNICATION DECK</text>',
            '<text x="310" y="625" class="head">LOWER POWER / BATTERY DECK</text>']

    out += ['<rect x="55" y="715" width="760" height="350" class="border"/>',
            '<text x="70" y="740" class="head">CONTROLLED COMPONENT PLACEMENT SCHEDULE</text>']
    rows = [
        ("01", "12 V LiFePO₄ BATTERY + BMS", "LOWER DECK", "Retained; strapped; terminal cover"),
        ("02", "MPPT SOLAR CONTROLLER", "LOWER DECK", "Heat/service clearance TBD"),
        ("03", "DC–DC REGULATOR", "LOWER DECK", "Protected regulated supply"),
        ("04", "FUSED POWER DISTRIBUTION", "LOWER DECK", "Accessible after door opening"),
        ("05", "MAIN BATTERY DISCONNECT", "LOWER DECK", "Service-accessible isolation"),
        ("06", "ESP32 CONTROLLER", "UPPER DECK", "Sensor acquisition controller"),
        ("07", "LTE/4G MODEM", "UPPER DECK", "Antenna/coax bend radius TBD"),
        ("08", "SENSOR DISTRIBUTION BOARD", "UPPER DECK", "Protected field connectors"),
        ("09", "THERMAL INTERFACE / FANS", "REAR/INTERNAL", "Final need based on heat test"),
    ]
    yy=768
    for no,item,zone,note in rows:
        out += [f'<line x1="55" y1="{yy+9}" x2="815" y2="{yy+9}" class="border"/>',
                f'<text x="70" y="{yy}" class="head">{no}</text>',f'<text x="110" y="{yy}" class="txt">{esc(item)}</text>',
                f'<text x="365" y="{yy}" class="small">{esc(zone)}</text>',f'<text x="485" y="{yy}" class="small">{esc(note)}</text>']
        yy+=32
    out += ['<rect x="845" y="825" width="785" height="240" class="border"/>',
            '<text x="860" y="850" class="head">ENCLOSURE / INSTALLATION NOTES</text>',
            '<text x="860" y="878" class="txt">1. OUTER ENVELOPE: 300 W × 280 D × 400 H; 8 mm UV-HDPE; 18 mm LID.</text>',
            '<text x="860" y="904" class="txt">2. MAINTAIN PHYSICAL SEPARATION BETWEEN POWER AND SENSOR/DATA HARNESS.</text>',
            '<text x="860" y="930" class="txt">3. USE DOWNWARD-FACING IP68 GLANDS, STRAIN RELIEF, DRIP LOOPS AND LABELS.</text>',
            '<text x="860" y="956" class="txt">4. KEEP BATTERY LOW; VERIFY DECK LOAD, C.G., CONNECTOR AND TOOL CLEARANCE.</text>',
            '<text x="860" y="982" class="txt">5. VALIDATE GASKETS, VENT, CONDENSATION CONTROL AND THERMAL PERFORMANCE.</text>',
            '<text x="860" y="1008" class="txt">6. ORANGE PI / BAY-STATION COMPUTER SHALL NOT BE INSTALLED IN THIS POD.</text>',
            '<text x="860" y="1042" class="warn">REFERENCE / NOT FOR FABRICATION</text>',
            '<rect x="845" y="1080" width="785" height="70" class="border"/>',
            '<line x1="1180" y1="1080" x2="1180" y2="1150" class="border"/>',
            '<text x="860" y="1105" class="small">DRAWING NO.</text><text x="950" y="1105" class="head">FALCON-BP-002</text>',
            '<text x="860" y="1135" class="small">SOURCE</text><text x="950" y="1135" class="txt">FUSION V2 / GLB</text>',
            '<text x="1195" y="1105" class="small">TITLE</text><text x="1260" y="1105" class="head">ELECTRONICS POD ARRANGEMENT</text>',
            '<text x="1195" y="1135" class="small">REV / STATUS</text><text x="1290" y="1135" class="warn">P1 / REFERENCE</text>',
            '</svg>']
    return "\n".join(out)


def float_drawing():
    """Create a controlled dimensional sheet for the proposed metal adaptation."""
    return '''<svg xmlns="http://www.w3.org/2000/svg" width="1684" height="1191" viewBox="0 0 1684 1191">
<defs>
 <style>.border{fill:none;stroke:#253746;stroke-width:1}.obj{fill:none;stroke:#334155;stroke-width:2}.cut{fill:#e2e8f0;stroke:#334155;stroke-width:1.4}.hidden{fill:none;stroke:#94a3b8;stroke-width:1;stroke-dasharray:7 5}.center{fill:none;stroke:#94a3b8;stroke-width:.8;stroke-dasharray:12 3 2 3}.dim{fill:none;stroke:#475569;stroke-width:1}.title{font-family:Arial,sans-serif;font-size:24px;font-weight:700;fill:#172635}.head{font-family:Arial,sans-serif;font-size:13px;font-weight:700;fill:#243746}.txt{font-family:Arial,sans-serif;font-size:12px;fill:#334155}.small{font-family:Arial,sans-serif;font-size:10px;fill:#475569}.warn{font-family:Arial,sans-serif;font-size:14px;font-weight:700;fill:#9f1239}</style>
 <marker id="darr" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto"><path d="M8 4 0 0v8z" fill="#475569"/></marker>
</defs>
<rect width="1684" height="1191" fill="#f8fafc"/><rect x="20" y="20" width="1644" height="1151" class="border"/>
<text x="45" y="60" class="title">PROJECT FALCON — METAL DRUM / FLOAT DIMENSIONAL CONTROL</text>
<text x="45" y="86" class="txt">PRELIMINARY METAL ADAPTATION OF V2 FLOAT GEOMETRY · ALL DIMENSIONS IN mm · DO NOT SCALE</text>

<rect x="55" y="130" width="760" height="660" class="border"/><text x="70" y="155" class="head">SECTION A–A — PRINCIPAL FLOAT BODY</text>
<path d="M190 215H610V462 C610 535 540 618 400 618 C260 618 190 535 190 462Z" class="cut"/>
<path d="M200 225H600V457 C600 522 532 606 400 606 C268 606 200 522 200 457Z" class="hidden"/>
<rect x="170" y="205" width="460" height="23" class="obj"/><line x1="170" y1="215" x2="630" y2="215" class="center"/><line x1="400" y1="175" x2="400" y2="650" class="center"/>
<path d="M205 285H595M205 385H595" class="hidden"/>
<line x1="630" y1="215" x2="685" y2="215" class="dim"/><line x1="610" y1="462" x2="685" y2="462" class="dim"/><line x1="675" y1="215" x2="675" y2="462" class="dim" marker-start="url(#darr)" marker-end="url(#darr)"/>
<text x="690" y="345" class="head" transform="rotate(-90 690 345)">380 CYLINDRICAL SECTION — CAD REF</text>
<line x1="610" y1="462" x2="735" y2="462" class="dim"/><line x1="400" y1="618" x2="735" y2="618" class="dim"/><line x1="725" y1="462" x2="725" y2="618" class="dim" marker-start="url(#darr)" marker-end="url(#darr)"/>
<text x="740" y="570" class="head" transform="rotate(-90 740 570)">240 KEEL DEPTH — CAD REF</text>
<line x1="610" y1="215" x2="785" y2="215" class="dim"/><line x1="400" y1="618" x2="785" y2="618" class="dim"/><line x1="775" y1="215" x2="775" y2="618" class="dim" marker-start="url(#darr)" marker-end="url(#darr)"/>
<text x="790" y="475" class="head" transform="rotate(-90 790 475)">620 OVERALL BODY — CAD REF</text>
<line x1="190" y1="675" x2="190" y2="705" class="dim"/><line x1="610" y1="675" x2="610" y2="705" class="dim"/><line x1="190" y1="695" x2="610" y2="695" class="dim" marker-start="url(#darr)" marker-end="url(#darr)"/>
<text x="355" y="690" class="head">Ø650 O.D. — CAD REF</text>
<line x1="325" y1="618" x2="325" y2="650" class="dim"/><line x1="475" y1="618" x2="475" y2="650" class="dim"/><line x1="325" y1="642" x2="475" y2="642" class="dim" marker-start="url(#darr)" marker-end="url(#darr)"/>
<text x="343" y="638" class="small">Ø200 KEEL ZONE — CAD REF</text>
<text x="90" y="755" class="small">SHELL THICKNESS: TBD FOR SELECTED METAL, LOADS, WELD PROCESS AND CORROSION SYSTEM.</text>

<rect x="845" y="130" width="785" height="410" class="border"/><text x="860" y="155" class="head">PLAN VIEW — STRUCTURAL INTERFACES</text>
<circle cx="1100" cy="335" r="175" class="obj"/><circle cx="1100" cy="335" r="165" class="hidden"/><circle cx="1100" cy="335" r="85" class="obj"/>
<line x1="880" y1="335" x2="1320" y2="335" class="center"/><line x1="1100" y1="115" x2="1100" y2="555" class="center"/><line x1="925" y1="525" x2="925" y2="555" class="dim"/><line x1="1275" y1="525" x2="1275" y2="555" class="dim"/><line x1="925" y1="545" x2="1275" y2="545" class="dim" marker-start="url(#darr)" marker-end="url(#darr)"/>
<text x="1035" y="540" class="head">Ø690 SUPPORT CLAMP O.D.</text>
<line x1="935" y1="495" x2="935" y2="520" class="dim"/><line x1="1265" y1="495" x2="1265" y2="520" class="dim"/><line x1="935" y1="510" x2="1265" y2="510" class="dim" marker-start="url(#darr)" marker-end="url(#darr)"/>
<text x="1035" y="505" class="small">Ø654 LINED CLAMP I.D.</text>
<line x1="1015" y1="450" x2="1015" y2="480" class="dim"/><line x1="1185" y1="450" x2="1185" y2="480" class="dim"/><line x1="1015" y1="470" x2="1185" y2="470" class="dim" marker-start="url(#darr)" marker-end="url(#darr)"/>
<text x="1040" y="465" class="small">Ø340 SERVICE OPENING</text>
<text x="1350" y="210" class="head">INTERFACE REGISTER</text><text x="1350" y="240" class="txt">Support deck O.D.  Ø620</text><text x="1350" y="268" class="txt">Support clamp I.D. Ø654</text><text x="1350" y="296" class="txt">Support clamp O.D. Ø690</text><text x="1350" y="324" class="txt">Clamp height       70</text><text x="1350" y="352" class="txt">Drain holes        8 × Ø10</text><text x="1350" y="380" class="txt">Drain-hole PCD     Ø672</text><text x="1350" y="420" class="small">Values are V2 CAD references.</text>

<rect x="845" y="565" width="785" height="225" class="border"/><text x="860" y="590" class="head">ENGINEERING VALUES REQUIRED BEFORE METAL FABRICATION</text>
<text x="860" y="620" class="txt">□ Selected alloy/steel grade and certified mechanical properties</text><text x="860" y="648" class="txt">□ Calculated shell, top, bottom and local reinforcement thicknesses</text><text x="860" y="676" class="txt">□ Weld joint details, process, inspection and leak-test requirements</text><text x="860" y="704" class="txt">□ Coating/anode/isolation system for marine corrosion and mixed metals</text><text x="860" y="732" class="txt">□ Loaded displacement, design waterline, freeboard, C.G. and stability</text><text x="860" y="760" class="txt">□ Lifting, frame, ballast and mooring design loads with safety factors</text>

<rect x="55" y="820" width="1020" height="280" class="border"/><text x="70" y="845" class="head">FABRICATION / DESIGN NOTES</text>
<text x="70" y="875" class="txt">1. CURRENT FUSION V2 SOURCE DEFINES A 6 mm HDPE BODY; IT DOES NOT VALIDATE A METAL SHELL.</text>
<text x="70" y="903" class="txt">2. DO NOT COPY THE 6 mm HDPE WALL VALUE INTO A METAL FABRICATION DRAWING.</text>
<text x="70" y="931" class="txt">3. FINAL PLATE THICKNESS AND REINFORCEMENT REQUIRE STRUCTURAL, BUOYANCY AND FATIGUE REVIEW.</text>
<text x="70" y="959" class="txt">4. PROVIDE CONTINUOUS WATERTIGHT JOINTS; WELD SYMBOLS AND NDT ACCEPTANCE REMAIN TBD.</text>
<text x="70" y="987" class="txt">5. ISOLATE DISSIMILAR METALS; INCLUDE DRAINAGE, SEALED PENETRATIONS AND SERVICE ACCESS.</text>
<text x="70" y="1015" class="txt">6. VERIFY DIMENSIONS AGAINST THE SELECTED PHYSICAL DRUM/SHELL BEFORE DETAIL DESIGN.</text>
<text x="70" y="1055" class="warn">PRELIMINARY ENGINEERING REFERENCE / NOT FOR FABRICATION</text>

<rect x="1100" y="820" width="530" height="280" class="border"/><line x1="1100" y1="900" x2="1630" y2="900" class="border"/><line x1="1360" y1="820" x2="1360" y2="1100" class="border"/>
<text x="1115" y="850" class="small">PROJECT</text><text x="1115" y="880" class="title">FALCON-01</text><text x="1375" y="850" class="small">DRAWING TITLE</text><text x="1375" y="875" class="head">METAL DRUM DIMENSIONAL CONTROL</text>
<text x="1115" y="935" class="small">DRAWING NO.</text><text x="1210" y="935" class="head">FALCON-BP-003</text><text x="1375" y="935" class="small">REVISION</text><text x="1455" y="935" class="head">P0</text>
<text x="1115" y="975" class="small">SCALE</text><text x="1210" y="975" class="head">NTS</text><text x="1375" y="975" class="small">DATE</text><text x="1455" y="975" class="head">2026-08-30</text>
<text x="1115" y="1015" class="small">SOURCE</text><text x="1210" y="1015" class="txt">FUSION V2 REF.</text><text x="1375" y="1015" class="small">STATUS</text><text x="1455" y="1015" class="warn">PRELIMINARY</text>
<text x="1115" y="1060" class="small">ENGINEER</text><text x="1210" y="1060" class="txt">________________</text><text x="1375" y="1060" class="small">APPROVAL</text><text x="1455" y="1060" class="txt">________________</text>
</svg>'''


def pod_equipment_drawing():
    """Detailed three-deck pod layout using the controlled Fusion envelopes."""
    return '''<svg xmlns="http://www.w3.org/2000/svg" width="1684" height="1191" viewBox="0 0 1684 1191">
<defs><style>.b{fill:none;stroke:#263746;stroke-width:1}.o{fill:#f8fafc;stroke:#334155;stroke-width:1.4}.pcb{fill:#e5eef3;stroke:#334155;stroke-width:1.3}.metal{fill:#e2e8f0;stroke:#334155;stroke-width:1.2}.keep{fill:none;stroke:#94a3b8;stroke-width:1;stroke-dasharray:7 5}.wire{fill:none;stroke:#64748b;stroke-width:1}.ctr{fill:none;stroke:#94a3b8;stroke-width:.8;stroke-dasharray:10 3 2 3}.title{font-family:Arial,sans-serif;font-size:24px;font-weight:700;fill:#172635}.h{font-family:Arial,sans-serif;font-size:13px;font-weight:700;fill:#243746}.t{font-family:Arial,sans-serif;font-size:11px;fill:#334155}.s{font-family:Arial,sans-serif;font-size:9px;fill:#475569}.xs{font-family:Arial,sans-serif;font-size:7px;fill:#475569}.w{font-family:Arial,sans-serif;font-size:13px;font-weight:700;fill:#9f1239}</style></defs>
<rect width="1684" height="1191" fill="#f8fafc"/><rect x="20" y="20" width="1644" height="1151" class="b"/>
<text x="45" y="58" class="title">PROJECT FALCON — ELECTRONICS POD EQUIPMENT LAYOUT</text><text x="45" y="84" class="t">THREE REMOVABLE DECKS · CONTROLLED PACKAGING ENVELOPES · POD 300 W × 280 D × 400 H mm</text>

<!-- LEVEL 1 -->
<rect x="40" y="115" width="505" height="350" class="b"/><text x="55" y="140" class="h">LEVEL 1 — BATTERY / LOWEST DECK</text><rect x="105" y="158" width="360" height="270" rx="18" class="o"/><line x1="285" y1="145" x2="285" y2="440" class="ctr"/><line x1="90" y1="293" x2="480" y2="293" class="ctr"/>
<rect x="142" y="185" width="288" height="216" rx="8" class="metal"/><text x="213" y="282" class="h">12.8 V 20 Ah LiFePO₄</text><text x="230" y="302" class="s">240 × 180 × 105 envelope</text><circle cx="176" cy="215" r="10" class="o"/><text x="172" y="219" class="h">+</text><circle cx="396" cy="215" r="10" class="o"/><text x="392" y="219" class="h">−</text><rect x="214" y="370" width="144" height="24" class="pcb"/><text x="260" y="386" class="s">BMS 120×40×50</text><line x1="176" y1="225" x2="214" y2="375" class="wire"/><line x1="396" y1="225" x2="358" y2="375" class="wire"/><rect x="126" y="172" width="320" height="242" rx="12" class="keep"/><text x="112" y="449" class="s">25 mm minimum provisional service/restraint clearance · retain battery in all axes</text>

<!-- LEVEL 2 -->
<rect x="565" y="115" width="505" height="350" class="b"/><text x="580" y="140" class="h">LEVEL 2 — POWER CONVERSION / PROTECTION</text><rect x="630" y="158" width="360" height="270" rx="18" class="o"/><line x1="810" y1="145" x2="810" y2="440" class="ctr"/><line x1="615" y1="293" x2="1005" y2="293" class="ctr"/>
<rect x="652" y="185" width="132" height="96" rx="5" class="metal"/><text x="697" y="211" class="h">MPPT</text><text x="670" y="228" class="s">110×80×45</text><rect x="665" y="245" width="105" height="22" class="o"/><line x1="700" y1="245" x2="700" y2="267" class="b"/><line x1="735" y1="245" x2="735" y2="267" class="b"/><text x="671" y="260" class="xs">PV</text><text x="705" y="260" class="xs">BAT</text><text x="740" y="260" class="xs">LOAD</text>
<rect x="842" y="185" width="108" height="84" class="pcb"/><text x="879" y="205" class="h">DC–DC</text><text x="870" y="222" class="s">90×70×35</text><circle cx="872" cy="245" r="13" class="o"/><rect x="912" y="235" width="22" height="20" class="metal"/><text x="866" y="249" class="xs">L1</text>
<rect x="652" y="322" width="108" height="48" class="o"/><text x="677" y="341" class="h">FUSE BLOCK</text><text x="681" y="357" class="s">90×40×30</text><rect x="660" y="328" width="13" height="32" class="metal"/><rect x="678" y="328" width="13" height="32" class="metal"/><rect x="696" y="328" width="13" height="32" class="metal"/><rect x="714" y="328" width="13" height="32" class="metal"/>
<rect x="862" y="322" width="72" height="48" rx="5" class="o"/><circle cx="898" cy="346" r="15" class="metal"/><line x1="898" y1="346" x2="909" y2="335" class="b"/><text x="867" y="388" class="s">DISCONNECT 60×40×40</text><text x="630" y="449" class="s">High-current wiring kept short; fuse and isolation controls remain service-accessible</text>

<!-- LEVEL 3 -->
<rect x="1090" y="115" width="550" height="350" class="b"/><text x="1105" y="140" class="h">LEVEL 3 — CONTROL / CELLULAR / SENSOR I/O</text><rect x="1155" y="158" width="360" height="270" rx="18" class="o"/><line x1="1335" y1="145" x2="1335" y2="440" class="ctr"/><line x1="1140" y1="293" x2="1530" y2="293" class="ctr"/>
<rect x="1180" y="185" width="96" height="66" rx="4" class="pcb"/><text x="1202" y="205" class="h">ESP32</text><text x="1192" y="220" class="s">80×55×22 env.</text><rect x="1203" y="225" width="49" height="18" class="metal"/><text x="1213" y="238" class="xs">WROOM-32E</text><rect x="1180" y="213" width="12" height="18" class="o"/><line x1="1263" y1="190" x2="1263" y2="246" class="b"/><text x="1177" y="264" class="s">USB / EN / BOOT accessible</text>
<rect x="1382" y="185" width="108" height="60" rx="4" class="pcb"/><text x="1410" y="204" class="h">LTE/4G</text><text x="1401" y="219" class="s">90×50×25 env.</text><rect x="1392" y="225" width="35" height="14" class="o"/><text x="1398" y="236" class="xs">SIM</text><circle cx="1474" cy="230" r="6" class="o"/><text x="1455" y="258" class="s">u.FL/SMA → gland</text>
<rect x="1180" y="320" width="108" height="60" rx="4" class="pcb"/><text x="1192" y="338" class="h">SENSOR I/O PCB</text><text x="1196" y="353" class="s">90×50×20 env.</text><rect x="1186" y="360" width="15" height="12" class="o"/><rect x="1205" y="360" width="15" height="12" class="o"/><rect x="1224" y="360" width="15" height="12" class="o"/><rect x="1243" y="360" width="15" height="12" class="o"/><rect x="1262" y="360" width="15" height="12" class="o"/>
<rect x="1370" y="310" width="125" height="82" rx="4" class="pcb"/><text x="1390" y="327" class="h">INTERFACE DEVICES</text><rect x="1380" y="338" width="30" height="20" class="metal"/><text x="1384" y="351" class="xs">ADS1115</text><rect x="1416" y="338" width="30" height="20" class="metal"/><text x="1422" y="351" class="xs">INA260</text><rect x="1452" y="338" width="30" height="20" class="metal"/><text x="1458" y="351" class="xs">INA260</text><rect x="1380" y="365" width="45" height="18" class="o"/><text x="1386" y="377" class="xs">GPS UART</text><rect x="1433" y="365" width="49" height="18" class="o"/><text x="1437" y="377" class="xs">SECURITY</text><text x="1160" y="449" class="s">Former Orange Pi zone retained as service/cable space — no Bay Station computer onboard</text>

<!-- SIDE SECTION -->
<rect x="40" y="495" width="650" height="330" class="b"/><text x="55" y="520" class="h">SECTION B–B — DECK HEIGHTS / CABLE ENTRY</text><rect x="185" y="545" width="300" height="245" rx="16" class="o"/><line x1="195" y1="715" x2="475" y2="715" class="b"/><line x1="195" y1="640" x2="475" y2="640" class="b"/><line x1="195" y1="570" x2="475" y2="570" class="b"/><text x="500" y="575" class="h">LEVEL 3 — CONTROL</text><text x="500" y="645" class="h">LEVEL 2 — POWER</text><text x="500" y="720" class="h">LEVEL 1 — BATTERY</text><rect x="235" y="720" width="200" height="55" class="metal"/><text x="278" y="752" class="t">BATTERY + BMS</text><rect x="220" y="652" width="95" height="45" class="metal"/><text x="247" y="679" class="s">MPPT</text><rect x="350" y="660" width="80" height="35" class="pcb"/><text x="372" y="681" class="s">DC–DC</text><rect x="220" y="582" width="90" height="34" class="pcb"/><text x="242" y="603" class="s">ESP32</text><rect x="350" y="582" width="90" height="34" class="pcb"/><text x="369" y="603" class="s">LTE/SENSORS</text><rect x="250" y="790" width="18" height="20" class="o"/><rect x="282" y="790" width="18" height="20" class="o"/><rect x="314" y="790" width="18" height="20" class="o"/><rect x="346" y="790" width="18" height="20" class="o"/><rect x="378" y="790" width="18" height="20" class="o"/><text x="215" y="815" class="s">DOWNWARD IP68 GLANDS: SOLAR · PRESSURE · WIND · TEMP · SECURITY</text><line x1="170" y1="545" x2="170" y2="790" class="b"/><text x="145" y="690" class="h" transform="rotate(-90 145 690)">400 POD HEIGHT</text>

<!-- SCHEDULE -->
<rect x="710" y="495" width="930" height="330" class="b"/><text x="725" y="520" class="h">EQUIPMENT / ENVELOPE / INTERFACE SCHEDULE</text>
<line x1="710" y1="540" x2="1640" y2="540" class="b"/><line x1="755" y1="495" x2="755" y2="825" class="b"/><line x1="1030" y1="495" x2="1030" y2="825" class="b"/><line x1="1170" y1="495" x2="1170" y2="825" class="b"/><line x1="1320" y1="495" x2="1320" y2="825" class="b"/>
<text x="720" y="536" class="s">ID</text><text x="770" y="536" class="s">EQUIPMENT</text><text x="1040" y="536" class="s">ENVELOPE mm</text><text x="1180" y="536" class="s">DECK</text><text x="1330" y="536" class="s">PRIMARY INTERFACE / STATUS</text>
<text x="720" y="568" class="t">01</text><text x="770" y="568" class="t">12.8 V 20 Ah LiFePO₄</text><text x="1040" y="568" class="t">240×180×105</text><text x="1180" y="568" class="t">L1</text><text x="1330" y="568" class="t">VBAT · selected rating; physical size verify</text>
<text x="720" y="596" class="t">02</text><text x="770" y="596" class="t">LiFePO₄ MPPT controller</text><text x="1040" y="596" class="t">110×80×45</text><text x="1180" y="596" class="t">L2</text><text x="1330" y="596" class="t">PV/BAT/LOAD · exact product TBD</text>
<text x="720" y="624" class="t">03</text><text x="770" y="624" class="t">DC–DC regulated branch</text><text x="1040" y="624" class="t">90×70×35</text><text x="1180" y="624" class="t">L2</text><text x="1330" y="624" class="t">5 V/3V3 rails · rating TBD by load test</text>
<text x="720" y="652" class="t">04</text><text x="770" y="652" class="t">Fused distribution</text><text x="1040" y="652" class="t">90×40×30</text><text x="1180" y="652" class="t">L2</text><text x="1330" y="652" class="t">Branch fuses · service accessible</text>
<text x="720" y="680" class="t">05</text><text x="770" y="680" class="t">Battery disconnect</text><text x="1040" y="680" class="t">60×40×40</text><text x="1180" y="680" class="t">L2</text><text x="1330" y="680" class="t">Main isolation · lockable/guarded TBD</text>
<text x="720" y="708" class="t">06</text><text x="770" y="708" class="t">ESP32-DevKitC V4</text><text x="1040" y="708" class="t">80×55×22 env.</text><text x="1180" y="708" class="t">L3</text><text x="1330" y="708" class="t">USB/UART/I2C/GPIO · exact selected controller</text>
<text x="720" y="736" class="t">07</text><text x="770" y="736" class="t">LTE/4G modem</text><text x="1040" y="736" class="t">90×50×25</text><text x="1180" y="736" class="t">L3</text><text x="1330" y="736" class="t">UART/USB + antenna · exact model TBD</text>
<text x="720" y="764" class="t">08</text><text x="770" y="764" class="t">Sensor distribution PCB</text><text x="1040" y="764" class="t">90×50×20</text><text x="1180" y="764" class="t">L3</text><text x="1330" y="764" class="t">Bar02/GPS/wind/temp/security terminations</text>
<text x="720" y="792" class="t">09</text><text x="770" y="792" class="t">Thermal interface / fan</text><text x="1040" y="792" class="t">TBD</text><text x="1180" y="792" class="t">REAR</text><text x="1330" y="792" class="t">Install only if sealed thermal test requires</text>

<rect x="40" y="850" width="1050" height="245" class="b"/><text x="55" y="875" class="h">INSTALLATION / DRAWING NOTES</text><text x="55" y="905" class="t">1. POD: 300×280×400; 35 CORNERS; 8 UV-HDPE WALL; 18 LID. VERIFY SEALS, DOOR AND 25 SERVICE CLEARANCE.</text><text x="55" y="933" class="t">2. EQUIPMENT DIMENSIONS ARE CONTROLLED ENVELOPES; MEASURE PARTS, CONNECTORS, BEND RADII AND TOOL CLEARANCE.</text><text x="55" y="961" class="t">3. ROUTE POWER AND SENSOR/DATA HARNESSES SEPARATELY; CROSS ONLY AT 90° AND PROVIDE LABELED TIE POINTS.</text><text x="55" y="989" class="t">4. TERMINATE EXTERNAL SENSOR CABLES AT LOCKING CONNECTORS; USE DRIP LOOPS AND DOWNWARD IP68 GLANDS.</text><text x="55" y="1017" class="t">5. BATTERY SHALL NOT CONTACT ELECTRONICS UNDER SHOCK/INVERSION; KEEP EXPOSED TERMINALS ABOVE LEAK TRAY.</text><text x="55" y="1045" class="t">6. ORANGE PI / BAY-STATION COMPUTER IS EXCLUDED. FORMER ENVELOPE IS SERVICE AND CABLE-ROUTING SPACE.</text><text x="55" y="1078" class="w">REFERENCE / VERIFY PHYSICAL PARTS / NOT FOR FABRICATION</text>
<rect x="1110" y="850" width="530" height="245" class="b"/><line x1="1110" y1="925" x2="1640" y2="925" class="b"/><line x1="1360" y1="850" x2="1360" y2="1095" class="b"/><text x="1125" y="877" class="s">PROJECT</text><text x="1125" y="910" class="title">FALCON-01</text><text x="1375" y="877" class="s">TITLE</text><text x="1375" y="903" class="h">ELECTRONICS POD EQUIPMENT LAYOUT</text><text x="1125" y="960" class="s">DRAWING NO.</text><text x="1220" y="960" class="h">FALCON-BP-002</text><text x="1375" y="960" class="s">REVISION</text><text x="1455" y="960" class="h">P2</text><text x="1125" y="1000" class="s">SCALE</text><text x="1220" y="1000" class="h">NTS</text><text x="1375" y="1000" class="s">DATE</text><text x="1455" y="1000" class="h">2026-08-30</text><text x="1125" y="1040" class="s">SOURCE</text><text x="1220" y="1040" class="t">FUSION ENVELOPES + BOM</text><text x="1375" y="1040" class="s">STATUS</text><text x="1455" y="1040" class="w">REFERENCE</text><text x="1125" y="1075" class="s">APPROVAL</text><text x="1220" y="1075" class="t">________________________</text>
</svg>'''


def pod_fabrication_drawing():
    return '''<svg xmlns="http://www.w3.org/2000/svg" width="1684" height="1191" viewBox="0 0 1684 1191"><defs><style>.b{fill:none;stroke:#263746;stroke-width:1}.o{fill:none;stroke:#334155;stroke-width:2}.x{fill:#e2e8f0;stroke:#334155;stroke-width:1.2}.hln{fill:none;stroke:#94a3b8;stroke-width:1;stroke-dasharray:7 5}.ctr{fill:none;stroke:#94a3b8;stroke-width:.8;stroke-dasharray:10 3 2 3}.d{fill:none;stroke:#475569;stroke-width:1}.title{font-family:Arial,sans-serif;font-size:24px;font-weight:700;fill:#172635}.h{font-family:Arial,sans-serif;font-size:13px;font-weight:700;fill:#243746}.t{font-family:Arial,sans-serif;font-size:11px;fill:#334155}.s{font-family:Arial,sans-serif;font-size:9px;fill:#475569}.w{font-family:Arial,sans-serif;font-size:13px;font-weight:700;fill:#9f1239}</style><marker id="p2" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto"><path d="M8 4 0 0v8z" fill="#475569"/></marker></defs><rect width="1684" height="1191" fill="#f8fafc"/><rect x="20" y="20" width="1644" height="1151" class="b"/><text x="45" y="58" class="title">PROJECT FALCON — MARINE ELECTRONICS POD FABRICATION CONTROL</text><text x="45" y="84" class="t">ENCLOSURE / DOOR / LID / DECK / CABLE INTERFACES · V2 CAD REFERENCE · ALL DIMENSIONS IN mm</text>
<rect x="40" y="115" width="600" height="575" class="b"/><text x="55" y="140" class="h">FRONT ELEVATION — SERVICE DOOR</text><polygon points="185,185 220,150 460,150 495,185 495,550 460,585 220,585 185,550" class="o"/><rect x="215" y="190" width="250" height="340" class="x"/><rect x="230" y="200" width="220" height="320" class="hln"/><rect x="221" y="196" width="238" height="328" class="hln"/><line x1="185" y1="150" x2="185" y2="585" class="ctr"/><line x1="340" y1="125" x2="340" y2="610" class="ctr"/>
<circle cx="205" cy="240" r="12" class="o"/><circle cx="205" cy="340" r="12" class="o"/><circle cx="205" cy="440" r="12" class="o"/><circle cx="205" cy="520" r="12" class="o"/><rect x="457" y="260" width="40" height="25" class="x"/><rect x="457" y="450" width="40" height="25" class="x"/><text x="68" y="240" class="t">4 × HINGE BARREL Ø24 × 45</text><text x="68" y="265" class="t">Z = 70 / 170 / 270 / 350</text><text x="505" y="275" class="t">LATCH 01 Z100</text><text x="505" y="465" class="t">LATCH 02 Z290</text><line x1="185" y1="620" x2="495" y2="620" class="d" marker-start="url(#p2)" marker-end="url(#p2)"/><line x1="185" y1="585" x2="185" y2="630" class="d"/><line x1="495" y1="585" x2="495" y2="630" class="d"/><text x="313" y="615" class="h">300 O/A</text><line x1="540" y1="150" x2="540" y2="585" class="d" marker-start="url(#p2)" marker-end="url(#p2)"/><line x1="495" y1="150" x2="550" y2="150" class="d"/><line x1="495" y1="585" x2="550" y2="585" class="d"/><text x="550" y="375" class="h">400 O/A</text><text x="215" y="555" class="t">DOOR 250×340×10 · OPENING 220×320</text><text x="215" y="575" class="s">RAISED LIP 250×350×6 · DUAL EPDM GASKET PATHS</text>
<rect x="670" y="115" width="470" height="330" class="b"/><text x="685" y="140" class="h">TOP PLAN — LID / RAIN HOOD</text><polygon points="735,190 770,155 1040,155 1075,190 1075,390 1040,425 770,425 735,390" class="o"/><polygon points="748,200 780,168 1030,168 1062,200 1062,380 1030,412 780,412 748,380" class="hln"/><line x1="905" y1="140" x2="905" y2="435" class="ctr"/><line x1="720" y1="290" x2="1090" y2="290" class="ctr"/><text x="760" y="405" class="t">POD 300×280 · CORNER CHAMFER 35</text><text x="760" y="425" class="t">LID 316×296×18 · HOOD 330×310×5</text>
<rect x="1170" y="115" width="470" height="575" class="b"/><text x="1185" y="140" class="h">SECTION A–A — WALL / DECK ELEVATIONS</text><rect x="1270" y="170" width="280" height="400" class="o"/><rect x="1278" y="178" width="264" height="384" class="hln"/><rect x="1262" y="150" width="296" height="18" class="x"/><rect x="1255" y="128" width="310" height="5" class="x"/><rect x="1295" y="515" width="250" height="6" class="x"/><rect x="1295" y="292" width="250" height="5" class="x"/><rect x="1290" y="542" width="256" height="6" class="hln"/><line x1="1245" y1="170" x2="1245" y2="570" class="d" marker-start="url(#p2)" marker-end="url(#p2)"/><text x="1190" y="375" class="h">400</text><text x="1320" y="535" class="t">LOWER DECK 250×200×6 @ Z45</text><text x="1320" y="285" class="t">UPPER DECK 250×210×5 @ Z270</text><text x="1320" y="595" class="t">BASE 8 · WALL 8 · LEAK TRAY 276×256×6</text><text x="1320" y="620" class="t">LID 18 · DUAL 6 EPDM SEAL PATHS</text><text x="1320" y="645" class="t">REAR THERMAL INTERFACE 180×6×220</text><text x="1320" y="670" class="t">MEMBRANE VENT BOSS 24×24×12</text>
<rect x="670" y="475" width="470" height="215" class="b"/><text x="685" y="500" class="h">BOTTOM / CABLE INTERFACE</text><rect x="765" y="535" width="216" height="72" class="x"/><circle cx="795" cy="571" r="12" class="o"/><circle cx="835" cy="571" r="12" class="o"/><circle cx="875" cy="571" r="12" class="o"/><circle cx="915" cy="571" r="12" class="o"/><circle cx="955" cy="571" r="12" class="o"/><text x="740" y="635" class="t">GLAND PLATE 180×60×8 · HOLE DIAMETERS / SPACING TBD BY SELECTED GLANDS</text><text x="740" y="660" class="t">ALL CABLE ENTRIES DOWNWARD-FACING WITH STRAIN RELIEF AND DRIP LOOPS</text>
<rect x="40" y="720" width="965" height="375" class="b"/><text x="55" y="745" class="h">ENCLOSURE PART / DETAIL SCHEDULE</text><line x1="40" y1="765" x2="1005" y2="765" class="b"/><line x1="95" y1="720" x2="95" y2="1095" class="b"/><line x1="390" y1="720" x2="390" y2="1095" class="b"/><line x1="600" y1="720" x2="600" y2="1095" class="b"/><text x="55" y="790" class="t">P01</text><text x="110" y="790" class="t">UV-HDPE SHELL</text><text x="405" y="790" class="t">300×280×400 / WALL 8</text><text x="615" y="790" class="t">CHAMFER 35; BASE 8</text><text x="55" y="820" class="t">P02</text><text x="110" y="820" class="t">TOP SERVICE LID</text><text x="405" y="820" class="t">316×296×18</text><text x="615" y="820" class="t">DUAL EPDM PATHS</text><text x="55" y="850" class="t">P03</text><text x="110" y="850" class="t">RAIN / SUN HOOD</text><text x="405" y="850" class="t">330×310×5</text><text x="615" y="850" class="t">VENTILATED OVERHANG</text><text x="55" y="880" class="t">P04</text><text x="110" y="880" class="t">FRONT SERVICE OPENING</text><text x="405" y="880" class="t">220×320</text><text x="615" y="880" class="t">ONLY SHELL CUT</text><text x="55" y="910" class="t">P05</text><text x="110" y="910" class="t">FRONT SERVICE DOOR</text><text x="405" y="910" class="t">250×340×10</text><text x="615" y="910" class="t">OPEN ≥100°</text><text x="55" y="940" class="t">P06</text><text x="110" y="940" class="t">HINGE BARRELS / PIN</text><text x="405" y="940" class="t">4× Ø24×45 / PIN Ø9×340</text><text x="615" y="940" class="t">316L</text><text x="55" y="970" class="t">P07</text><text x="110" y="970" class="t">COMPRESSION LATCHES</text><text x="405" y="970" class="t">2× 40×25×45 ENV.</text><text x="615" y="970" class="t">316L; FINAL SKU TBD</text><text x="55" y="1000" class="t">P08</text><text x="110" y="1000" class="t">LOWER / UPPER DECKS</text><text x="405" y="1000" class="t">250×200×6 / 250×210×5</text><text x="615" y="1000" class="t">ALUMINUM; LOAD VERIFY</text><text x="55" y="1030" class="t">P09</text><text x="110" y="1030" class="t">GLAND PLATE</text><text x="405" y="1030" class="t">180×60×8</text><text x="615" y="1030" class="t">HOLES TBD</text><text x="55" y="1060" class="t">P10</text><text x="110" y="1060" class="t">THERMAL INTERFACE</text><text x="405" y="1060" class="t">180×6×220</text><text x="615" y="1060" class="t">SEALED REAR BRIDGE</text><text x="55" y="1085" class="w">REFERENCE DIMENSIONS / COMPLETE SEAL, LOAD AND IP TESTS BEFORE FABRICATION</text>
<rect x="1035" y="720" width="605" height="375" class="b"/><text x="1050" y="745" class="h">FABRICATION / VALIDATION NOTES</text><text x="1050" y="780" class="t">1. DO NOT SCALE. VERIFY ALL NATIVE FUSION DIMENSIONS.</text><text x="1050" y="810" class="t">2. HOLE PATTERNS REQUIRE PURCHASED HARDWARE.</text><text x="1050" y="840" class="t">3. SPECIFY FASTENERS, TORQUE AND THREAD INSERTS.</text><text x="1050" y="870" class="t">4. VALIDATE DUAL SEALS, DOOR COMPRESSION AND VENT.</text><text x="1050" y="900" class="t">5. PERFORM IP, THERMAL, SALT, VIBRATION AND EMC TESTS.</text><line x1="1035" y1="930" x2="1640" y2="930" class="b"/><line x1="1325" y1="930" x2="1325" y2="1095" class="b"/><text x="1050" y="960" class="s">PROJECT</text><text x="1050" y="995" class="title">FALCON-01</text><text x="1340" y="960" class="s">TITLE</text><text x="1340" y="985" class="h">POD FABRICATION CONTROL</text><text x="1050" y="1030" class="s">DRAWING</text><text x="1140" y="1030" class="h">FALCON-BP-002</text><text x="1340" y="1030" class="s">REV.</text><text x="1410" y="1030" class="h">P3</text><text x="1050" y="1070" class="s">STATUS</text><text x="1140" y="1070" class="w">REFERENCE</text><text x="1340" y="1070" class="s">APPROVAL</text><text x="1430" y="1070" class="t">____________</text></svg>'''


def structural_drawing():
    return '''<svg xmlns="http://www.w3.org/2000/svg" width="1684" height="1191" viewBox="0 0 1684 1191"><defs><style>.b{fill:none;stroke:#263746;stroke-width:1}.o{fill:none;stroke:#334155;stroke-width:2}.x{fill:none;stroke:#526574;stroke-width:1.4}.c{fill:none;stroke:#94a3b8;stroke-width:.8;stroke-dasharray:10 3 2 3}.d{fill:none;stroke:#475569;stroke-width:1}.title{font-family:Arial,sans-serif;font-size:24px;font-weight:700;fill:#172635}.h{font-family:Arial,sans-serif;font-size:13px;font-weight:700;fill:#243746}.t{font-family:Arial,sans-serif;font-size:11px;fill:#334155}.s{font-family:Arial,sans-serif;font-size:9px;fill:#475569}.w{font-family:Arial,sans-serif;font-size:13px;font-weight:700;fill:#9f1239}</style><marker id="a4" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto"><path d="M8 4 0 0v8z" fill="#475569"/></marker></defs><rect width="1684" height="1191" fill="#f8fafc"/><rect x="20" y="20" width="1644" height="1151" class="b"/><text x="45" y="58" class="title">PROJECT FALCON — TOWER / FRAME STRUCTURAL DIMENSION CONTROL</text><text x="45" y="84" class="t">V2 CAD REFERENCE · 6061-T6 STRUCTURAL MEMBERS + 316L SERVICE HARDWARE · ALL DIMENSIONS IN mm</text>
<rect x="40" y="115" width="650" height="650" class="b"/><text x="55" y="140" class="h">FRONT ELEVATION — TAPERED MARINE MAST</text><line x1="205" y1="675" x2="485" y2="675" class="o"/><line x1="205" y1="675" x2="285" y2="175" class="o"/><line x1="485" y1="675" x2="405" y2="175" class="o"/><line x1="285" y1="175" x2="405" y2="175" class="o"/><line x1="225" y1="550" x2="465" y2="550" class="x"/><line x1="245" y1="425" x2="445" y2="425" class="x"/><line x1="265" y1="300" x2="425" y2="300" class="x"/><line x1="225" y1="550" x2="445" y2="425" class="x"/><line x1="465" y1="550" x2="245" y2="425" class="x"/><line x1="245" y1="425" x2="425" y2="300" class="x"/><line x1="445" y1="425" x2="265" y2="300" class="x"/><line x1="265" y1="300" x2="405" y2="175" class="x"/><line x1="425" y1="300" x2="285" y2="175" class="x"/><line x1="345" y1="145" x2="345" y2="705" class="c"/><line x1="205" y1="705" x2="485" y2="705" class="d" marker-start="url(#a4)" marker-end="url(#a4)"/><line x1="205" y1="675" x2="205" y2="715" class="d"/><line x1="485" y1="675" x2="485" y2="715" class="d"/><text x="315" y="700" class="h">420 BASE</text><line x1="285" y1="155" x2="405" y2="155" class="d" marker-start="url(#a4)" marker-end="url(#a4)"/><text x="315" y="150" class="h">260 TOP</text><line x1="515" y1="175" x2="515" y2="675" class="d" marker-start="url(#a4)" marker-end="url(#a4)"/><line x1="485" y1="175" x2="525" y2="175" class="d"/><line x1="485" y1="675" x2="525" y2="675" class="d"/><text x="530" y="455" class="h" transform="rotate(-90 530 455)">800 STRUCTURAL HEIGHT</text><text x="75" y="735" class="t">PRIMARY LEGS Ø32 · HORIZONTAL/X BRACES Ø20 · POD-CLEARANCE SHOULDER 380</text>
<rect x="720" y="115" width="430" height="310" class="b"/><text x="735" y="140" class="h">PLAN — SUPPORT DECK / CLAMP</text><circle cx="935" cy="270" r="135" class="o"/><circle cx="935" cy="270" r="128" class="x"/><circle cx="935" cy="270" r="66" class="o"/><line x1="770" y1="270" x2="1100" y2="270" class="c"/><line x1="935" y1="105" x2="935" y2="435" class="c"/><text x="770" y="390" class="t">CLAMP O.D. Ø690 / I.D. Ø654 / HEIGHT 70</text><text x="770" y="410" class="t">SERVICE DECK O.D. Ø620 / OPENING Ø340</text>
<rect x="1180" y="115" width="450" height="310" class="b"/><text x="1195" y="140" class="h">LOWER SUPPORT CAGE</text><line x1="1270" y1="360" x2="1315" y2="175" class="o"/><line x1="1540" y1="360" x2="1495" y2="175" class="o"/><line x1="1270" y1="360" x2="1540" y2="360" class="x"/><line x1="1315" y1="175" x2="1495" y2="175" class="x"/><line x1="1405" y1="150" x2="1405" y2="390" class="c"/><text x="1210" y="390" class="t">4 × Ø32 TUBES · BOTTOM RADIUS 365 · TOP RADIUS 336</text><text x="1210" y="410" class="t">TOP ATTACHMENT Z = 385 CAD REFERENCE</text>
<rect x="720" y="455" width="430" height="310" class="b"/><text x="735" y="480" class="h">FRONT MAINTENANCE GATE</text><line x1="790" y1="700" x2="820" y2="515" class="o"/><line x1="1070" y1="700" x2="1040" y2="515" class="o"/><line x1="790" y1="700" x2="1070" y2="700" class="o"/><line x1="820" y1="515" x2="1040" y2="515" class="o"/><line x1="790" y1="700" x2="1040" y2="515" class="x"/><line x1="1070" y1="700" x2="820" y2="515" class="x"/><text x="750" y="735" class="t">LOWER 340 · UPPER 310 · HEIGHT 390</text><text x="750" y="755" class="t">FRAME Ø25 · X-BRACE Ø20 · HINGE PIN Ø10 · OPEN ≥100°</text>
<rect x="1180" y="455" width="450" height="310" class="b"/><text x="1195" y="480" class="h">STRUCTURAL MEMBER SCHEDULE</text><text x="1200" y="515" class="t">M01  Mast legs                 4 × Ø32 6061-T6</text><text x="1200" y="545" class="t">M02  Rails / X-braces          Ø20 6061-T6</text><text x="1200" y="575" class="t">M03  Main support risers       Ø30 6061-T6</text><text x="1200" y="605" class="t">M04  Lower support tubes       4 × Ø32 6061-T6</text><text x="1200" y="635" class="t">M05  Gate perimeter            Ø25 6061-T6</text><text x="1200" y="665" class="t">M06  Gate X-brace              Ø20 6061-T6</text><text x="1200" y="695" class="t">M07  Gate hinge pin            Ø10 316L</text><text x="1200" y="725" class="t">M08  EPDM isolation liners     THICKNESS TBD</text><text x="1200" y="750" class="s">CUT LENGTHS, WALL THICKNESS, JOINTS AND FASTENERS TBD.</text>
<rect x="40" y="795" width="1040" height="300" class="b"/><text x="55" y="820" class="h">STRUCTURAL ENGINEERING / FABRICATION NOTES</text><text x="55" y="850" class="t">1. OUTSIDE DIAMETERS AND ENVELOPES ARE CAD REFERENCES; TUBE WALL THICKNESS IS NOT YET ENGINEER-APPROVED.</text><text x="55" y="878" class="t">2. COMPLETE WIND, WAVE, SHOCK, FATIGUE, SOLAR-BRACKET AND LIFTING LOAD CASES BEFORE MEMBER RELEASE.</text><text x="55" y="906" class="t">3. ISSUE A CONTROLLED CUT LIST ONLY AFTER NATIVE-FUSION JOINT COORDINATES AND END CUTS ARE VERIFIED.</text><text x="55" y="934" class="t">4. SPECIFY WELD/BOLT JOINTS, GUSSETS, FASTENER GRADES, TORQUE, DRAIN HOLES AND INSPECTION.</text><text x="55" y="962" class="t">5. ELECTRICALLY ISOLATE DISSIMILAR METALS AND DOCUMENT MARINE COATING / ANODE REQUIREMENTS.</text><text x="55" y="990" class="t">6. PERFORM INTERFERENCE, DEFLECTION AND SERVICE-ACCESS CHECKS WITH THE ACTUAL POD AND PANELS.</text><text x="55" y="1030" class="w">PRELIMINARY DIMENSION CONTROL / NOT A FABRICATION CUT LIST</text>
<rect x="1110" y="795" width="520" height="300" class="b"/><line x1="1110" y1="875" x2="1630" y2="875" class="b"/><line x1="1360" y1="795" x2="1360" y2="1095" class="b"/><text x="1125" y="825" class="s">PROJECT</text><text x="1125" y="858" class="title">FALCON-01</text><text x="1375" y="825" class="s">TITLE</text><text x="1375" y="850" class="h">TOWER / FRAME DIMENSIONS</text><text x="1125" y="915" class="s">DRAWING</text><text x="1210" y="915" class="h">FALCON-BP-004</text><text x="1375" y="915" class="s">REV.</text><text x="1450" y="915" class="h">P0</text><text x="1125" y="955" class="s">SCALE</text><text x="1210" y="955" class="h">NTS</text><text x="1375" y="955" class="s">DATE</text><text x="1450" y="955" class="h">2026-08-30</text><text x="1125" y="995" class="s">SOURCE</text><text x="1210" y="995" class="t">FUSION V2 PARAMS</text><text x="1375" y="995" class="s">STATUS</text><text x="1450" y="995" class="w">REFERENCE</text><text x="1125" y="1045" class="s">ENGINEER</text><text x="1210" y="1045" class="t">____________</text><text x="1375" y="1045" class="s">APPROVAL</text><text x="1450" y="1045" class="t">____________</text></svg>'''


def external_hardware_drawing():
    return '''<svg xmlns="http://www.w3.org/2000/svg" width="1684" height="1191" viewBox="0 0 1684 1191"><defs><style>.b{fill:none;stroke:#263746;stroke-width:1}.o{fill:none;stroke:#334155;stroke-width:2}.x{fill:#e2e8f0;stroke:#334155;stroke-width:1.3}.c{fill:none;stroke:#94a3b8;stroke-width:.8;stroke-dasharray:9 4}.title{font-family:Arial,sans-serif;font-size:24px;font-weight:700;fill:#172635}.h{font-family:Arial,sans-serif;font-size:13px;font-weight:700;fill:#243746}.t{font-family:Arial,sans-serif;font-size:11px;fill:#334155}.s{font-family:Arial,sans-serif;font-size:9px;fill:#475569}.w{font-family:Arial,sans-serif;font-size:13px;font-weight:700;fill:#9f1239}</style></defs><rect width="1684" height="1191" fill="#f8fafc"/><rect x="20" y="20" width="1644" height="1151" class="b"/><text x="45" y="58" class="title">PROJECT FALCON — EXTERNAL HARDWARE DIMENSION REGISTER</text><text x="45" y="84" class="t">SOLAR · SENSOR ARRAY · PRESSURE GUARD · BALLAST · MOORING / ANCHOR · V2 CAD REFERENCE</text>
<rect x="40" y="115" width="515" height="370" class="b"/><text x="55" y="140" class="h">DUAL SOLAR ARRAY</text><rect x="100" y="185" width="270" height="180" class="x"/><line x1="145" y1="185" x2="145" y2="365" class="c"/><line x1="190" y1="185" x2="190" y2="365" class="c"/><line x1="235" y1="185" x2="235" y2="365" class="c"/><line x1="280" y1="185" x2="280" y2="365" class="c"/><line x1="325" y1="185" x2="325" y2="365" class="c"/><text x="105" y="395" class="t">EACH PANEL 450 W × 300 H × 20 T</text><text x="105" y="420" class="t">2 × 30 W = 60 W NOMINAL · 20° OUTWARD TILT</text><text x="105" y="445" class="t">PANEL CENTER Z = 1170 · LAMINATE 3</text>
<rect x="580" y="115" width="500" height="370" class="b"/><text x="595" y="140" class="h">TOP SENSOR / ANTENNA ARRAY</text><line x1="640" y1="385" x2="1020" y2="385" class="o"/><line x1="675" y1="385" x2="675" y2="205" class="o"/><line x1="780" y1="385" x2="780" y2="165" class="o"/><line x1="890" y1="385" x2="890" y2="135" class="o"/><line x1="985" y1="385" x2="985" y2="87" class="o"/><circle cx="780" cy="165" r="22" class="x"/><circle cx="890" cy="135" r="20" class="x"/><text x="620" y="420" class="t">DECK Z 882 · GNSS TOTAL H 250 · LTE WHIP H 220</text><text x="620" y="445" class="t">WI-FI REF. H 180 · WIND SENSOR H 219 · AIR TERMINAL H 298</text>
<rect x="1105" y="115" width="535" height="370" class="b"/><text x="1120" y="140" class="h">PRESSURE SENSOR GUARD</text><ellipse cx="1285" cy="210" rx="64" ry="18" class="o"/><ellipse cx="1285" cy="350" rx="64" ry="18" class="o"/><line x1="1221" y1="210" x2="1221" y2="350" class="o"/><line x1="1349" y1="210" x2="1349" y2="350" class="o"/><rect x="1261" y="245" width="48" height="84" rx="18" class="x"/><text x="1380" y="220" class="t">GUARD Ø64 × 72</text><text x="1380" y="250" class="t">RODS Ø6</text><text x="1380" y="280" class="t">SENSOR Ø24 × 42</text><text x="1380" y="310" class="t">RADIAL OFFSET 125</text><text x="1380" y="340" class="t">MOUNT Z 198</text><text x="1380" y="370" class="t">DOWNWARD OPEN PORT</text>
<rect x="40" y="515" width="515" height="350" class="b"/><text x="55" y="540" class="h">ADJUSTABLE LOW BALLAST</text><line x1="250" y1="575" x2="250" y2="800" class="o"/><ellipse cx="250" cy="630" rx="105" ry="18" class="x"/><ellipse cx="250" cy="675" rx="105" ry="18" class="x"/><ellipse cx="250" cy="720" rx="105" ry="18" class="x"/><ellipse cx="250" cy="765" rx="105" ry="18" class="x"/><text x="375" y="620" class="t">RAIL Ø40 × 500</text><text x="375" y="650" class="t">4 PLATES</text><text x="375" y="680" class="t">EACH Ø220 × 25</text><text x="375" y="710" class="t">TOP Z −300</text><text x="375" y="740" class="t">BOTTOM Z −800</text><text x="75" y="835" class="s">MASS / MATERIAL / RETENTION LOAD REQUIRE CALCULATION AND TEST.</text>
<rect x="580" y="515" width="500" height="350" class="b"/><text x="595" y="540" class="h">CHAIN / CONNECTOR REFERENCE</text><ellipse cx="745" cy="620" rx="30" ry="50" class="o"/><ellipse cx="745" cy="710" rx="30" ry="50" class="o"/><ellipse cx="745" cy="800" rx="30" ry="50" class="o"/><text x="830" y="610" class="t">CHAIN WIRE Ø12</text><text x="830" y="640" class="t">LINK OUTSIDE Ø52</text><text x="830" y="670" class="t">VERTICAL PITCH 45</text><text x="830" y="700" class="t">13 LINKS IN CAD REFERENCE</text><text x="830" y="730" class="t">SHACKLE / CLEVIS RATINGS TBD</text><text x="830" y="760" class="t">SECONDARY SAFETY LANYARD TBD</text>
<rect x="1105" y="515" width="535" height="350" class="b"/><text x="1120" y="540" class="h">CONCRETE MOORING ANCHOR</text><path d="M1200 790L1245 600H1455L1500 790Z" class="x"/><text x="1180" y="830" class="t">BOTTOM 650 × 650 · TOP 450 × 450 · HEIGHT 500</text><text x="1180" y="855" class="t">NOMINAL CAD MASS 367 kg — VERIFY BY DESIGN CALCULATION</text>
<rect x="40" y="895" width="1040" height="220" class="b"/><text x="55" y="920" class="h">RELEASE NOTES</text><text x="55" y="950" class="t">1. VERIFY EVERY PURCHASED SENSOR, PANEL, CONNECTOR, SHACKLE AND CHAIN AGAINST ITS DATASHEET AND RECEIVING MEASUREMENT.</text><text x="55" y="978" class="t">2. SOLAR BRACKETS REQUIRE WIND/SLAM LOADS; SENSOR POSITIONS REQUIRE CLEAR VIEW, SEPARATION, DRAINAGE AND CABLE SERVICE.</text><text x="55" y="1006" class="t">3. PRESSURE PORT DEPTH AND HYDRODYNAMIC LOCATION REQUIRE CONTROLLED CALIBRATION AND WAVE-ESTIMATION VALIDATION.</text><text x="55" y="1034" class="t">4. BALLAST, CHAIN, SHACKLE, ANCHOR AND ATTACHMENTS REQUIRE WORKING-LOAD, SAFETY-FACTOR AND CORROSION REVIEW.</text><text x="55" y="1080" class="w">REFERENCE DIMENSIONS / NOT FOR PROCUREMENT OR FABRICATION</text>
<rect x="1110" y="895" width="530" height="220" class="b"/><line x1="1110" y1="965" x2="1640" y2="965" class="b"/><line x1="1360" y1="895" x2="1360" y2="1115" class="b"/><text x="1125" y="925" class="s">PROJECT</text><text x="1125" y="955" class="title">FALCON-01</text><text x="1375" y="925" class="s">TITLE</text><text x="1375" y="950" class="h">EXTERNAL HARDWARE REGISTER</text><text x="1125" y="1000" class="s">DRAWING</text><text x="1210" y="1000" class="h">FALCON-BP-005</text><text x="1375" y="1000" class="s">REV.</text><text x="1450" y="1000" class="h">P0</text><text x="1125" y="1040" class="s">SCALE</text><text x="1210" y="1040" class="h">NTS</text><text x="1375" y="1040" class="s">STATUS</text><text x="1450" y="1040" class="w">REFERENCE</text><text x="1125" y="1080" class="s">APPROVAL</text><text x="1210" y="1080" class="t">________________</text></svg>'''


def equipment_actual_drawing():
    """Detailed proposed actual-part layout for BP-006.

    Confirmed boards use their named product geometry. Power/cellular parts
    that are not yet frozen in the BOM remain explicitly marked PROPOSED so
    the drawing cannot be mistaken for a procurement release.
    """
    return '''<svg xmlns="http://www.w3.org/2000/svg" width="1684" height="1191" viewBox="0 0 1684 1191"><defs><style>svg{shape-rendering:geometricPrecision}path,line,polyline,polygon,rect,circle,ellipse{vector-effect:non-scaling-stroke;stroke-linejoin:round;stroke-linecap:round}.b{fill:none;stroke:#263746;stroke-width:1}.o{fill:#f8fafc;stroke:#334155;stroke-width:1.7}.pcb{fill:#e8f0f3;stroke:#334155;stroke-width:1.5}.metal{fill:#dbe4e8;stroke:#334155;stroke-width:1.2}.pin{fill:#334155;stroke:none}.wire{fill:none;stroke:#64748b;stroke-width:1;stroke-dasharray:7 4}.ctr{fill:none;stroke:#94a3b8;stroke-width:.8;stroke-dasharray:10 3 2 3}.title{font-family:Arial,sans-serif;font-size:24px;font-weight:700;fill:#172635}.h{font-family:Arial,sans-serif;font-size:13px;font-weight:700;fill:#243746}.t{font-family:Arial,sans-serif;font-size:11px;fill:#334155}.s{font-family:Arial,sans-serif;font-size:9px;fill:#475569}.xs{font-family:Arial,sans-serif;font-size:7px;fill:#475569}.w{font-family:Arial,sans-serif;font-size:13px;font-weight:700;fill:#9f1239}.ok{font-family:Arial,sans-serif;font-size:10px;font-weight:700;fill:#166534}.prop{font-family:Arial,sans-serif;font-size:10px;font-weight:700;fill:#9a3412}</style></defs>
<rect width="1684" height="1191" fill="#f8fafc"/><rect x="20" y="20" width="1644" height="1151" class="b"/><text x="45" y="58" class="title">PROJECT FALCON — ELECTRONICS POD ACTUAL-PART LAYOUT</text><text x="45" y="84" class="t">RECOGNIZABLE COMPONENT FOOTPRINTS · THREE SERVICE LEVELS · DIMENSIONS IN metres (m) · VERIFY PURCHASED SKU</text>

<!-- LEVEL 1: battery -->
<rect x="40" y="115" width="500" height="315" class="b"/><text x="55" y="140" class="h">LEVEL 1 — BATTERY / LOWEST DECK</text><rect x="120" y="175" width="320" height="190" rx="12" class="o"/><rect x="143" y="195" width="274" height="130" rx="8" class="metal"/><circle cx="175" cy="190" r="10" class="o"/><text x="170" y="194" class="h">+</text><circle cx="385" cy="190" r="10" class="o"/><text x="381" y="194" class="h">−</text><rect x="220" y="325" width="120" height="22" class="pcb"/><text x="246" y="340" class="xs">INTERNAL BMS</text><text x="200" y="255" class="h">12.8 V · 20 Ah LiFePO4</text><text x="195" y="280" class="t">selected marine battery</text><text x="55" y="395" class="prop">PROPOSED PHYSICAL SKU — VERIFY CASE, POSTS AND BMS</text>

<!-- LEVEL 2: MPPT/DC protection -->
<rect x="560" y="115" width="520" height="315" class="b"/><text x="575" y="140" class="h">LEVEL 2 — CHARGING / REGULATION / PROTECTION</text><rect x="595" y="175" width="190" height="185" rx="8" class="pcb"/><rect x="625" y="195" width="130" height="72" class="metal"/><text x="643" y="225" class="h">Victron</text><text x="632" y="245" class="t">SmartSolar 75/10</text><rect x="615" y="292" width="32" height="35" class="o"/><rect x="655" y="292" width="32" height="35" class="o"/><rect x="695" y="292" width="32" height="35" class="o"/><rect x="735" y="292" width="32" height="35" class="o"/><text x="619" y="344" class="xs">PV+ PV− BAT+ BAT−</text><text x="607" y="380" class="prop">PROPOSED MPPT · 0.100×0.113×0.040 m</text>
<rect x="815" y="175" width="105" height="185" class="pcb"/><rect x="840" y="195" width="55" height="120" class="metal"/><line x1="850" y1="205" x2="850" y2="305" class="wire"/><line x1="865" y1="205" x2="865" y2="305" class="wire"/><line x1="880" y1="205" x2="880" y2="305" class="wire"/><text x="828" y="335" class="xs">5 V DC-DC</text><text x="815" y="380" class="prop">SKU TBD</text>
<rect x="945" y="175" width="100" height="85" class="pcb"/><rect x="957" y="192" width="14" height="45" class="o"/><rect x="978" y="192" width="14" height="45" class="o"/><rect x="999" y="192" width="14" height="45" class="o"/><rect x="1020" y="192" width="14" height="45" class="o"/><text x="960" y="280" class="xs">FUSED DISTRIBUTION</text><circle cx="995" cy="325" r="33" class="o"/><circle cx="995" cy="325" r="13" class="metal"/><text x="957" y="375" class="t">MAIN DISCONNECT</text>

<!-- LEVEL 3: control -->
<rect x="1100" y="115" width="540" height="315" class="b"/><text x="1115" y="140" class="h">LEVEL 3 — CONTROL / TELEMETRY / SENSOR I/O</text>
<!-- ESP32 --> <rect x="1125" y="175" width="145" height="205" rx="5" class="pcb"/><rect x="1150" y="193" width="95" height="82" class="metal"/><path d="M1160 205h75v55h-75zM1170 215h55v35h-55z" class="wire"/><text x="1166" y="238" class="t">ESP32-WROOM</text><rect x="1175" y="333" width="45" height="35" class="o"/><text x="1184" y="355" class="xs">USB</text>''' + ''.join(f'<rect x="{1132 if side==0 else 1254}" y="{190+i*9}" width="9" height="5" class="pin"/>' for side in range(2) for i in range(19)) + '''<text x="1130" y="402" class="ok">CONFIRMED: ESP32-DevKitC V4</text>
<!-- LTE --> <rect x="1290" y="175" width="205" height="205" rx="5" class="pcb"/><rect x="1320" y="205" width="120" height="82" class="metal"/><text x="1340" y="240" class="h">SIM7600G-H</text><text x="1345" y="260" class="xs">LTE / GNSS</text><circle cx="1310" cy="200" r="12" class="o"/><circle cx="1475" cy="200" r="12" class="o"/><rect x="1310" y="320" width="45" height="28" class="o"/><rect x="1365" y="320" width="45" height="28" class="o"/><rect x="1420" y="320" width="45" height="28" class="o"/><text x="1310" y="402" class="prop">PROPOSED: SIM7600G-H</text>
<!-- INA260 pair --> <rect x="1515" y="175" width="100" height="90" class="pcb"/><rect x="1530" y="188" width="70" height="27" class="o"/><text x="1535" y="207" class="xs">VIN+ / VIN−</text><rect x="1545" y="225" width="42" height="24" class="metal"/><text x="1530" y="280" class="xs">INA260 BAT · 0x40</text><rect x="1515" y="300" width="100" height="90" class="pcb"/><rect x="1530" y="313" width="70" height="27" class="o"/><text x="1535" y="332" class="xs">VIN+ / VIN−</text><rect x="1545" y="350" width="42" height="24" class="metal"/><text x="1530" y="405" class="xs">INA260 SOLAR · 0x41</text><text x="1518" y="420" class="ok">CONFIRMED: INA260 ×2</text>

<!-- Pod integration plan -->
<rect x="40" y="455" width="1000" height="335" class="b"/><text x="55" y="480" class="h">POD PLAN — SERVICEABLE ACTUAL-PART ARRANGEMENT</text><polygon points="235,525 265,495 815,495 845,525 845,740 815,770 265,770 235,740" class="o"/><rect x="270" y="535" width="260" height="185" rx="8" class="metal"/><text x="315" y="625" class="h">E01 · LiFePO4 BATTERY</text><circle cx="300" cy="555" r="8" class="o"/><circle cx="500" cy="555" r="8" class="o"/><rect x="555" y="525" width="135" height="145" class="pcb"/><text x="570" y="585" class="t">E02 · MPPT</text><rect x="710" y="525" width="80" height="145" class="pcb"/><text x="721" y="585" class="xs">E03</text><text x="718" y="602" class="xs">DC-DC</text><rect x="555" y="690" width="110" height="50" class="pcb"/><text x="570" y="720" class="xs">FUSE / SPD</text><circle cx="745" cy="715" r="25" class="o"/><text x="704" y="758" class="xs">DISCONNECT</text><line x1="530" y1="625" x2="555" y2="600" class="wire"/><line x1="690" y1="600" x2="710" y2="600" class="wire"/><text x="865" y="535" class="h">SERVICE RULES</text><text x="865" y="565" class="t">• Battery retained on lowest deck</text><text x="865" y="593" class="t">• Power and data harnesses separated</text><text x="865" y="621" class="t">• Terminals face service door</text><text x="865" y="649" class="t">• Drip loop before every gland</text><text x="865" y="677" class="t">• Maintain connector/tool clearance</text><text x="865" y="705" class="t">• Verify heat rise in sealed pod</text><text x="865" y="748" class="w">PLACEMENT TO BE VERIFIED WITH PURCHASED PARTS</text>

<!-- Schedule and title block -->
<rect x="40" y="820" width="1040" height="275" class="b"/><text x="55" y="847" class="h">ACTUAL / PROPOSED PART REGISTER</text><line x1="40" y1="865" x2="1080" y2="865" class="b"/><text x="55" y="892" class="t">E01  12.8 V 20 Ah LiFePO4 battery + BMS</text><text x="535" y="892" class="prop">PROPOSED · EXACT SKU/CASE TBD</text><text x="55" y="925" class="t">E02  Victron SmartSolar MPPT 75/10 · 0.100×0.113×0.040 m</text><text x="535" y="925" class="prop">PROPOSED</text><text x="55" y="958" class="t">E03  12 V to regulated 5 V DC-DC branch</text><text x="535" y="958" class="prop">EXACT SKU TBD</text><text x="55" y="991" class="t">E04  Espressif ESP32-DevKitC V4 / ESP32-WROOM-32E</text><text x="535" y="991" class="ok">CONFIRMED BOM</text><text x="55" y="1024" class="t">E05  Waveshare SIM7600G-H 4G HAT</text><text x="535" y="1024" class="prop">PROPOSED · NETWORK APPROVAL REQUIRED</text><text x="55" y="1057" class="t">E06/E07  Adafruit INA260 PID 4226 ×2 · 0.0229×0.0228×0.0027 m</text><text x="535" y="1057" class="ok">CONFIRMED BOM</text><text x="55" y="1084" class="s">Do not drill mounting holes until each purchased unit and connector clearance is physically measured.</text>
<rect x="1100" y="455" width="540" height="640" class="b"/><text x="1115" y="483" class="h">DRAWING STATUS / NOTES</text><text x="1115" y="520" class="t">1. Detailed outlines improve identification and maintenance.</text><text x="1115" y="550" class="t">2. Green items are already named in the controlled BOM.</text><text x="1115" y="580" class="t">3. Orange items are proposed candidates, not purchases.</text><text x="1115" y="610" class="t">4. Replace proposed geometry after SKU freeze.</text><text x="1115" y="640" class="t">5. Orange Pi remains at the shore Bay Station.</text><text x="1115" y="690" class="w">REFERENCE / NOT FOR FABRICATION</text><line x1="1100" y1="730" x2="1640" y2="730" class="b"/><text x="1115" y="770" class="s">PROJECT</text><text x="1115" y="805" class="title">FALCON-01</text><text x="1375" y="770" class="s">TITLE</text><text x="1375" y="800" class="h">POD ACTUAL-PART LAYOUT</text><text x="1115" y="850" class="s">DRAWING</text><text x="1210" y="850" class="h">FALCON-BP-006</text><text x="1375" y="850" class="s">REV.</text><text x="1450" y="850" class="h">P5</text><text x="1115" y="895" class="s">SCALE</text><text x="1210" y="895" class="h">NTS</text><text x="1375" y="895" class="s">UNITS</text><text x="1450" y="895" class="h">m</text><text x="1115" y="940" class="s">SOURCE</text><text x="1210" y="940" class="t">FUSION V2 + BOM</text><text x="1375" y="940" class="s">STATUS</text><text x="1450" y="940" class="w">REFERENCE</text><text x="1115" y="990" class="s">APPROVAL</text><text x="1210" y="990" class="t">________________________</text></svg>'''


def main():
    doc, blob = load_glb(MODEL)
    edges = cad_edges(doc, blob)
    details_only = "--details-only" in sys.argv
    general_only = "--general-only" in sys.argv
    if not details_only:
        OUT.write_text(drawing(edges), encoding="utf-8")
    if general_only:
        print(f"Generated {OUT.relative_to(ROOT)} from {len(edges):,} feature edges")
        return
    pod = ("RECT_POD", "TOP_SERVICE_LID", "FRONT_DOOR_",
           "FRONT_EPDM_", "FRONT_RAISED_", "IP68_DOWNWARD_",
           "IP67_MEMBRANE_", "SEALED_REAR_", "INTERNAL_LEAK_")
    OUT_POD.write_text(cad_detail_sheet(edges,
        "PROJECT FALCON — ELECTRONICS POD CAD FABRICATION REFERENCE", "FALCON-BP-002",
        [("FRONT ELEVATION", pod, 0, 2, (40,115,520,300)),
         ("RIGHT ELEVATION", pod, 1, 2, (580,115,500,300)),
         ("PLAN VIEW", pod, 0, 1, (1100,115,540,300)),
         ("FRONT DOOR / SEAL DETAIL", ("FRONT_DOOR_","FRONT_EPDM_","FRONT_RAISED_"), 0, 2, (40,435,780,325)),
         ("DECK / CABLE INTERFACE", ("BATTERY_MINIPC_MPPT_DECK","ESP32_MODEM_SENSOR_DECK","IP68_DOWNWARD_"), 0, 2, (840,435,800,325))],
        [("P01","Pod shell","0.300 × 0.280 × 0.400 m / wall 0.008 m","UV-HDPE; chamfer 0.035 m; base 0.008 m"),
         ("P02","Service lid / hood","0.316×0.296×0.018 m / 0.330×0.310×0.005 m","Dual EPDM paths"),
         ("P03","Door / opening","0.250×0.340×0.010 m / 0.220×0.320 m","Open ≥100°"),
         ("P04","Hinges / latches","4×Ø0.024×0.045 m / 2×0.040×0.025×0.045 m","Final 316L SKU TBD"),
         ("P05","Internal decks","0.250×0.200×0.006 m / 0.250×0.210×0.005 m","Load and isolation TBD"),
         ("P06","Gland plate","0.180 × 0.060 × 0.008 m","Hole pattern by selected glands")]), encoding="utf-8")

    float_terms = ("MAIN_FLOAT_TRADITIONAL", "MAIN_FLOAT_EDGE", "MAIN_FLOAT_UPPER", "MAIN_FLOAT_LOWER")
    OUT_FLOAT.write_text(cad_detail_sheet(edges,
        "PROJECT FALCON — MAIN FLOAT / DRUM CAD DIMENSION CONTROL", "FALCON-BP-003",
        [("FRONT ELEVATION", float_terms, 0, 2, (40,115,520,300)),
         ("RIGHT ELEVATION", float_terms, 1, 2, (580,115,500,300)),
         ("PLAN VIEW", float_terms, 0, 1, (1100,115,540,300)),
         ("UPPER FAIRING DETAIL", ("MAIN_FLOAT_UPPER",), 0, 2, (40,435,780,325)),
         ("LOWER FAIRING / KEEL DETAIL", ("MAIN_FLOAT_LOWER",), 0, 2, (840,435,800,325))],
        [("F01","Main float overall","Ø0.650 × 0.620 m","Final material and displacement TBD"),
         ("F02","Upper cylindrical body","Ø0.650 × 0.380 m","Wall thickness design-required"),
         ("F03","Lower rounded keel","Ø0.650 × 0.240 m","Hydrodynamic fairing"),
         ("F04","Service opening","Ø0.340 m CAD reference","Seal and clamp TBD"),
         ("F05","Support interface","Ø0.620 m / clamp Ø0.690 m","Verify frame fit"),
         ("F06","Drain pattern","8 × Ø0.010 m CAD reference","Final placement TBD")]), encoding="utf-8")

    frame = ("MAST_", "BAY_", "LEVEL_", "FRAME_PAD_", "DIAGONAL_FRAME",
             "LOWER_TO_MAIN_FRAME_", "GATE_", "RISER_GUSSET_")
    OUT_STRUCTURE.write_text(cad_detail_sheet(edges,
        "PROJECT FALCON — TOWER / FRAME CAD STRUCTURAL CONTROL", "FALCON-BP-004",
        [("FRONT ELEVATION", frame, 0, 2, (40,115,520,300)),
         ("RIGHT ELEVATION", frame, 1, 2, (580,115,500,300)),
         ("PLAN VIEW", frame, 0, 1, (1100,115,540,300)),
         ("MAST / X-BRACING DETAIL", ("MAST_","BAY_","LEVEL_"), 0, 2, (40,435,780,325)),
         ("LOWER CAGE / GATE DETAIL", ("LOWER_TO_MAIN_FRAME_","GATE_"), 0, 2, (840,435,800,325))],
        [("M01","Mast legs","4 × Ø0.032 m / 0.800 m high","6061-T6; wall TBD"),
         ("M02","Rails / X-braces","Ø0.020 m","Joint design TBD"),
         ("M03","Main support risers","Ø0.030 m","CAD envelope"),
         ("M04","Lower support tubes","4 × Ø0.032 m","Bottom radius 0.365 m"),
         ("M05","Maintenance gate","0.340 / 0.310 × 0.390 m","Hinge/latch hardware TBD"),
         ("M06","Deck / clamp","Ø0.620 / Ø0.690 m","Opening Ø0.340 m")]), encoding="utf-8")

    OUT_HARDWARE.write_text(cad_detail_sheet(edges,
        "PROJECT FALCON — EXTERNAL HARDWARE CAD DETAIL REGISTER", "FALCON-BP-005",
        [("DUAL SOLAR ARRAY", ("DUAL_SOLAR",), 0, 2, (40,115,520,300)),
         ("TOP SENSOR ARRAY", ("WIND_","GNSS_","NAVIGATION_LIGHT"), 0, 2, (580,115,500,300)),
         ("PRESSURE SENSOR ASSEMBLY", ("PRESSURE_","BAR02_","SENSOR_GUARD"), 0, 2, (1100,115,540,300)),
         ("BALLAST / CONNECTOR", ("BALLAST_V2",), 0, 2, (40,435,780,325)),
         ("ANCHOR / MOORING CHAIN", ("ANCHOR_",), 0, 2, (840,435,800,325))],
        [("H01","Solar panels","2 × 0.450 × 0.300 × 0.020 m","30 W each; verify purchased panel"),
         ("H02","Sensor platform","Top deck Z = 0.882 m","GNSS, wind, light and antennas"),
         ("H03","Pressure guard","Ø0.064 × 0.072 m","Sensor Ø0.024 × 0.042 m"),
         ("H04","Ballast rail / plates","Ø0.040×0.500 m / 4×Ø0.220×0.025 m","Mass and retention TBD"),
         ("H05","Mooring chain","Wire Ø0.012 m / link Ø0.052 m","WLL and corrosion review"),
         ("H06","Concrete anchor","0.650/0.450 × 0.500 m","Mass calculation and approval required")]), encoding="utf-8")

    equipment = ("LIFEPO4_BATTERY_12V_ENVELOPE_BODY", "BATTERY_BMS_ENVELOPE_BODY",
                 "MPPT_CONTROLLER_ENVELOPE_BODY", "DC_DC_CONVERTER_ENVELOPE_BODY",
                 "FUSED_POWER_DISTRIBUTION_BODY", "MAIN_BATTERY_DISCONNECT_BODY",
                 "ESP32_CONTROLLER_ENVELOPE_BODY", "LTE_4G_MODEM_ENVELOPE_BODY",
                 "SENSOR_DISTRIBUTION_BOARD_BODY")
    OUT_EQUIPMENT.write_text(cad_detail_sheet(edges,
        "PROJECT FALCON — POD EQUIPMENT CAD PACKAGING LAYOUT", "FALCON-BP-006",
        [("FRONT PACKAGING ELEVATION", equipment, 0, 2, (40,115,520,300)),
         ("RIGHT PACKAGING ELEVATION", equipment, 1, 2, (580,115,500,300)),
         ("PLAN PACKAGING VIEW", equipment, 0, 1, (1100,115,540,300)),
         ("POWER EQUIPMENT DETAIL", ("LIFEPO4_BATTERY_12V_ENVELOPE_BODY","BATTERY_BMS_ENVELOPE_BODY","MPPT_CONTROLLER_ENVELOPE_BODY","DC_DC_CONVERTER_ENVELOPE_BODY","FUSED_POWER_DISTRIBUTION_BODY","MAIN_BATTERY_DISCONNECT_BODY"), 0, 2, (40,435,780,325)),
         ("CONTROL / COMMUNICATION DETAIL", ("ESP32_CONTROLLER_ENVELOPE_BODY","LTE_4G_MODEM_ENVELOPE_BODY","SENSOR_DISTRIBUTION_BOARD_BODY"), 0, 2, (840,435,800,325))],
        [("E01","LiFePO4 battery","0.240 × 0.180 × 0.105 m envelope","Selected physical size TBD"),
         ("E02","MPPT controller","0.110 × 0.080 × 0.045 m","PV/BAT/LOAD"),
         ("E03","DC-DC regulator","0.090 × 0.070 × 0.035 m","5 V rail"),
         ("E04","ESP32 controller","0.080 × 0.055 × 0.022 m envelope","Exact DevKit footprint TBD"),
         ("E05","LTE/4G modem","0.090 × 0.050 × 0.025 m","Antenna and bend clearance"),
         ("E06","Sensor distribution PCB","0.090 × 0.050 × 0.020 m","Connector access required")]), encoding="utf-8")
    # BP-006 uses recognizable actual/candidate part representations instead
    # of anonymous CAD envelopes so the maintenance layout is understandable.
    OUT_EQUIPMENT.write_text(equipment_actual_drawing(), encoding="utf-8")
    if not details_only:
        print(f"Generated {OUT.relative_to(ROOT)} from {len(edges):,} feature edges")
    print(f"Generated {OUT_POD.relative_to(ROOT)}")
    print(f"Generated {OUT_FLOAT.relative_to(ROOT)}")
    print(f"Generated {OUT_STRUCTURE.relative_to(ROOT)}")
    print(f"Generated {OUT_HARDWARE.relative_to(ROOT)}")
    print(f"Generated {OUT_EQUIPMENT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
