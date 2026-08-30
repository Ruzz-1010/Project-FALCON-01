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
OUT_POD = ROOT / "docs/blueprints/FALCON-BP-002-electronics-pod.svg"
OUT_FLOAT = ROOT / "docs/blueprints/FALCON-BP-003-metal-drum-dimensions.svg"


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
           '<defs><style>.border{fill:none;stroke:#253746;stroke-width:1}.object{fill:none;stroke:#526574;stroke-width:.58;stroke-linecap:round}.center{fill:none;stroke:#94a3b8;stroke-width:.65;stroke-dasharray:10 3 2 3}.dim{fill:none;stroke:#334155;stroke-width:.75}.title{font-family:Arial,sans-serif;font-size:24px;font-weight:700;fill:#172635}.head{font-family:Arial,sans-serif;font-size:13px;font-weight:700;fill:#243746}.txt{font-family:Arial,sans-serif;font-size:12px;fill:#334155}.small{font-family:Arial,sans-serif;font-size:10px;fill:#475569}.tiny{font-family:Arial,sans-serif;font-size:8px;fill:#64748b}.warn{font-family:Arial,sans-serif;font-size:14px;font-weight:700;fill:#9f1239}</style><marker id="arr" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto"><path d="M8 4 0 0v8z" fill="#334155"/></marker></defs>',
           '<rect width="1684" height="1191" fill="#f8fafc"/><rect x="20" y="20" width="1644" height="1151" class="border"/>',
           '<text x="45" y="60" class="title">PROJECT FALCON — CAD-DERIVED GENERAL ARRANGEMENT</text>',
           '<text x="45" y="86" class="txt">PROPOSED REPLACEMENT PROTOTYPE · V2 REFERENCE GEOMETRY · DIMENSIONS IN mm UNLESS NOTED</text>']

    for label, ax, ay, (x, y, w, h), predicate, limit in views:
        view_edges = [edge for edge in edges if predicate(edge)]
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
                f'<path d="M{x+w/2} {y+30}V{y+h-10} M{x+10} {y+h/2}H{x+w-10}" class="center"/>']
        projected = {}
        for a, b, _ in view_edges:
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
        selected = sorted(projected.values(), key=lambda item: item[4], reverse=True)[:limit]
        paths = [f'M{x1:.1f} {y1:.1f}L{x2:.1f} {y2:.1f}' for x1,y1,x2,y2,_ in selected]
        out.append(f'<path d="{" ".join(paths)}" class="object"/>')

    out += ['<path d="M210 575V596 M660 575V596 M210 590H660" class="dim" marker-start="url(#arr)" marker-end="url(#arr)"/>',
            '<text x="405" y="585" class="head">Ø650 CAD REF</text>',
            '<path d="M785 205H803 M785 530H803 M798 205V530" class="dim" marker-start="url(#arr)" marker-end="url(#arr)"/>',
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
    return "\n".join(out)


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
        pts = [p for e in pod_edges for p in e[:2]]
        mins = [min(p[i] for p in pts) for i in range(3)]
        maxs = [max(p[i] for p in pts) for i in range(3)]
        lowx, highx, lowy, highy = mins[ax], maxs[ax], mins[ay], maxs[ay]
        scale = min((w-50)/(highx-lowx), (h-55)/(highy-lowy))
        ox = x+w/2-(lowx+highx)/2*scale; oy = y+h/2+(lowy+highy)/2*scale
        out += [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" class="border"/>',
                f'<text x="{x+10}" y="{y+20}" class="head">{label}</text>',
                f'<path d="M{x+w/2} {y+30}V{y+h-10} M{x+10} {y+h/2}H{x+w-10}" class="center"/>']
        projected = {}
        for a,b,_ in pod_edges:
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
<path d="M170 205H630V228H170Z" class="obj"/><path d="M170 215H630M400 175V650" class="center"/>
<path d="M205 285H595M205 385H595" class="hidden"/>
<path d="M630 215H685M610 462H685M675 215V462" class="dim" marker-start="url(#darr)" marker-end="url(#darr)"/>
<text x="690" y="345" class="head" transform="rotate(-90 690 345)">380 CYLINDRICAL SECTION — CAD REF</text>
<path d="M610 462H735M400 618H735M725 462V618" class="dim" marker-start="url(#darr)" marker-end="url(#darr)"/>
<text x="740" y="570" class="head" transform="rotate(-90 740 570)">240 KEEL DEPTH — CAD REF</text>
<path d="M610 215H785M400 618H785M775 215V618" class="dim" marker-start="url(#darr)" marker-end="url(#darr)"/>
<text x="790" y="475" class="head" transform="rotate(-90 790 475)">620 OVERALL BODY — CAD REF</text>
<path d="M190 675V705M610 675V705M190 695H610" class="dim" marker-start="url(#darr)" marker-end="url(#darr)"/>
<text x="355" y="690" class="head">Ø650 O.D. — CAD REF</text>
<path d="M325 618V650M475 618V650M325 642H475" class="dim" marker-start="url(#darr)" marker-end="url(#darr)"/>
<text x="343" y="638" class="small">Ø200 KEEL ZONE — CAD REF</text>
<text x="90" y="755" class="small">SHELL THICKNESS: TBD FOR SELECTED METAL, LOADS, WELD PROCESS AND CORROSION SYSTEM.</text>

<rect x="845" y="130" width="785" height="410" class="border"/><text x="860" y="155" class="head">PLAN VIEW — STRUCTURAL INTERFACES</text>
<circle cx="1100" cy="335" r="175" class="obj"/><circle cx="1100" cy="335" r="165" class="hidden"/><circle cx="1100" cy="335" r="85" class="obj"/>
<path d="M880 335H1320M1100 115V555" class="center"/><path d="M925 525V555M1275 525V555M925 545H1275" class="dim" marker-start="url(#darr)" marker-end="url(#darr)"/>
<text x="1035" y="540" class="head">Ø690 SUPPORT CLAMP O.D.</text>
<path d="M935 495V520M1265 495V520M935 510H1265" class="dim" marker-start="url(#darr)" marker-end="url(#darr)"/>
<text x="1035" y="505" class="small">Ø654 LINED CLAMP I.D.</text>
<path d="M1015 450V480M1185 450V480M1015 470H1185" class="dim" marker-start="url(#darr)" marker-end="url(#darr)"/>
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


def main():
    doc, blob = load_glb(MODEL)
    edges = cad_edges(doc, blob)
    OUT.write_text(drawing(edges), encoding="utf-8")
    OUT_POD.write_text(pod_drawing(edges), encoding="utf-8")
    OUT_FLOAT.write_text(float_drawing(), encoding="utf-8")
    print(f"Generated {OUT.relative_to(ROOT)} from {len(edges):,} feature edges")
    print(f"Generated {OUT_POD.relative_to(ROOT)}")
    print(f"Generated {OUT_FLOAT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
