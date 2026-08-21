#!/usr/bin/env python3
"""Export an A4, millimetre-scale footprint fit sheet from the KiCad PCB."""
from __future__ import annotations

import html
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BOARD = ROOT / "FALCON_CARRIER.kicad_pcb"
OUTPUT = ROOT / "FALCON_CARRIER_PHYSICAL_FIT_A4.svg"
BOARD_LEFT, BOARD_TOP, BOARD_W, BOARD_H = 20.0, 20.0, 165.0, 125.0
PAGE_W, PAGE_H = 210.0, 297.0
DRAW_X, DRAW_Y = (PAGE_W - BOARD_W) / 2, 55.0


def blocks(source: str, token: str) -> list[str]:
    """Return balanced S-expression blocks beginning with token."""
    found: list[str] = []
    cursor = 0
    while True:
        start = source.find(token, cursor)
        if start < 0:
            return found
        depth = 0
        quoted = False
        escaped = False
        for end in range(start, len(source)):
            char = source[end]
            if quoted:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == '"':
                    quoted = False
            elif char == '"':
                quoted = True
            elif char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
                if depth == 0:
                    found.append(source[start : end + 1])
                    cursor = end + 1
                    break
        else:
            raise ValueError(f"Unbalanced block beginning at {start}: {token}")


def nums(expression: str, name: str) -> tuple[float, ...] | None:
    match = re.search(rf"\({name}\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)(?:\s+([-+0-9.eE]+))?\)", expression)
    return tuple(float(value) for value in match.groups() if value is not None) if match else None


def line(x1: float, y1: float, x2: float, y2: float, css: str) -> str:
    return f'<line x1="{x1:g}" y1="{y1:g}" x2="{x2:g}" y2="{y2:g}" class="{css}"/>'


source = BOARD.read_text(encoding="utf-8")
art: list[str] = []
references: list[str] = []

for footprint in blocks(source, "(footprint "):
    reference_match = re.search(r'\(property "Reference" "([^"]+)"', footprint)
    at = nums(footprint, "at")
    if not reference_match or not at:
        continue
    ref = reference_match.group(1)
    fx, fy = at[0] - BOARD_LEFT, at[1] - BOARD_TOP
    angle = at[2] if len(at) == 3 else 0.0
    body: list[str] = []

    for shape in blocks(footprint, "(fp_rect"):
        start, end = nums(shape, "start"), nums(shape, "end")
        if start and end:
            x, y = min(start[0], end[0]), min(start[1], end[1])
            body.append(f'<rect x="{x:g}" y="{y:g}" width="{abs(end[0]-start[0]):g}" height="{abs(end[1]-start[1]):g}" class="outline"/>')
    for shape in blocks(footprint, "(fp_circle"):
        center, end = nums(shape, "center"), nums(shape, "end")
        if center and end:
            radius = math.hypot(end[0] - center[0], end[1] - center[1])
            body.append(f'<circle cx="{center[0]:g}" cy="{center[1]:g}" r="{radius:g}" class="outline"/>')
    for pad in blocks(footprint, "(pad "):
        pad_match = re.match(r'\(pad\s+"([^"]*)"\s+([a-z_]+)\s+([a-z_]+)', pad)
        position, size = nums(pad, "at"), nums(pad, "size")
        if not pad_match or not position or not size:
            continue
        number, kind, shape = pad_match.groups()
        px, py = position[:2]
        pa = position[2] if len(position) == 3 else 0.0
        klass = "hole" if kind in {"thru_hole", "np_thru_hole"} else "smd"
        if shape == "circle":
            body.append(f'<circle cx="{px:g}" cy="{py:g}" r="{size[0]/2:g}" class="{klass}"/>')
        else:
            body.append(f'<rect x="{px-size[0]/2:g}" y="{py-size[1]/2:g}" width="{size[0]:g}" height="{size[1]:g}" rx="{min(size)/5:g}" class="{klass}" transform="rotate({pa:g} {px:g} {py:g})"/>')
        if number == "1":
            body.append(f'<circle cx="{px:g}" cy="{py:g}" r="0.45" class="pin1"/>')

    body.append(f'<text x="0" y="-1.5" class="ref">{html.escape(ref)}</text>')
    references.append(ref)
    art.append(f'<g transform="translate({fx:g} {fy:g}) rotate({angle:g})">{"".join(body)}</g>')

svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="210mm" height="297mm" viewBox="0 0 210 297">
  <title>FALCON-01 Carrier PCB physical fit sheet</title>
  <style>
    .title {{ font-family: Arial, sans-serif; font-size: 6pt; font-weight: bold; fill: #111; }}
    .note {{ font-family: Arial, sans-serif; font-size: 3.2pt; fill: #222; }}
    .small {{ font-family: Arial, sans-serif; font-size: 2.5pt; fill: #333; }}
    .board {{ fill: none; stroke: #111; stroke-width: .35; }}
    .outline {{ fill: none; stroke: #555; stroke-width: .18; }}
    .smd {{ fill: #ddd; stroke: #111; stroke-width: .12; }}
    .hole {{ fill: white; stroke: #111; stroke-width: .2; }}
    .pin1 {{ fill: #111; }}
    .ref {{ font-family: Arial, sans-serif; font-size: 2.5pt; font-weight: bold; text-anchor: middle; fill: #111; }}
    .dim {{ stroke: #111; stroke-width: .18; }}
  </style>
  <text x="22.5" y="14" class="title">FALCON-01 CARRIER — 1:1 PHYSICAL FIT SHEET</text>
  <text x="22.5" y="20" class="note">Print on A4 portrait at 100% / Actual size. Disable Fit, Shrink, and Scale to page.</text>
  <text x="22.5" y="25" class="note">Measure the 50 mm calibration bar before placing any component. Black dot marks pad 1.</text>
  <g transform="translate(22.5 34)">
    {line(0, 0, 50, 0, 'dim')}
    {line(0, -2, 0, 2, 'dim')}{line(10, -1, 10, 1, 'dim')}{line(20, -1, 20, 1, 'dim')}
    {line(30, -1, 30, 1, 'dim')}{line(40, -1, 40, 1, 'dim')}{line(50, -2, 50, 2, 'dim')}
    <text x="0" y="6" class="small">0</text><text x="47" y="6" class="small">50 mm</text>
  </g>
  <g transform="translate({DRAW_X:g} {DRAW_Y:g})">
    <rect x="0" y="0" width="{BOARD_W:g}" height="{BOARD_H:g}" class="board"/>
    {''.join(art)}
    <text x="82.5" y="131" class="note" text-anchor="middle">BOARD OUTLINE: 165.00 × 125.00 mm</text>
  </g>
  <text x="22.5" y="194" class="note">FIT RESULT: ☐ PASS  ☐ FAIL     Scale measured: __________ mm / 50.00 mm</text>
  <text x="22.5" y="201" class="note">Checked by: ____________________  Date: ______________  Second reviewer: ____________________</text>
  <text x="22.5" y="210" class="small">Do not drill, fabricate, or route final copper from this sheet until every critical footprint is physically verified.</text>
  <text x="22.5" y="216" class="small">Source: FALCON_CARRIER.kicad_pcb · Footprints rendered: {len(references)}</text>
</svg>
'''
OUTPUT.write_text(svg, encoding="utf-8")
print(f"Exported {OUTPUT.name}: {len(references)} footprints, {BOARD_W:g} x {BOARD_H:g} mm board")
