#!/usr/bin/env python3
"""Compact the placement-only carrier while preserving KiCad-saved content."""
import re
from pathlib import Path

BOARD = Path(__file__).with_name("FALCON_CARRIER.kicad_pcb")

PLACEMENTS = {
    "J2": (27, 40, 0), "J7": (27, 58, 0), "J8": (27, 76, 0),
    "J9": (27, 94, 0), "J10": (27, 112, 0),
    "R1": (39, 58, 0), "R2": (39, 94, 0),
    "J4": (56, 40, 0), "J5": (56, 65, 0), "J6": (56, 90, 0),
    "U4": (56, 116, 0), "J3": (87, 43, 0), "U3": (89, 79, 0),
    "U2": (136, 70, -90), "J12": (107, 94, 0),
    "R3": (145, 83, 0), "R4": (145, 91, 0), "R5": (155, 83, 0),
    "R6": (155, 91, 0), "Q1": (166, 83, 0), "Q2": (166, 91, 0),
    "R7": (145, 99, 0), "R8": (155, 99, 0),
    "C1": (76, 132, 0), "U1": (82, 132, 0), "C2": (88, 132, 0),
    "JP1": (103, 132, 0), "U6": (116, 132, 0), "J1": (132, 132, 0),
    "J11": (151, 132, 0), "J13": (172, 132, 0),
    "H1": (25, 25, 0), "H2": (180, 25, 0),
    "H3": (25, 140, 0), "H4": (180, 140, 0),
}
for index in range(1, 21):
    column = (index - 1) % 11
    row = (index - 1) // 11
    PLACEMENTS[f"TP{index}"] = (75 + column * 8.2, 108 + row * 9, 0)


def footprint_blocks(text):
    cursor = 0
    while True:
        start = text.find("(footprint ", cursor)
        if start < 0:
            return
        depth, quoted, escaped = 0, False, False
        for index in range(start, len(text)):
            char = text[index]
            if quoted:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == '"':
                    quoted = False
                continue
            if char == '"': quoted = True
            elif char == "(": depth += 1
            elif char == ")":
                depth -= 1
                if depth == 0:
                    yield start, index + 1
                    cursor = index + 1
                    break


text = BOARD.read_text(encoding="utf-8")
changes = []
for start, end in footprint_blocks(text):
    block = text[start:end]
    ref_match = re.search(r'\(property "Reference" "([^"]+)"', block)
    if not ref_match or ref_match.group(1) not in PLACEMENTS:
        continue
    ref = ref_match.group(1)
    at_match = re.search(r'\(at\s+[-.\d]+\s+[-.\d]+(?:\s+[-.\d]+)?\)', block)
    if not at_match:
        continue
    x, y, angle = PLACEMENTS[ref]
    replacement = f"(at {x:g} {y:g}" + (f" {angle:g}" if angle else "") + ")"
    changes.append((start + at_match.start(), start + at_match.end(), replacement))

for start, end, replacement in reversed(changes):
    text = text[:start] + replacement + text[end:]

# Compact outline, antenna keep-out, and zone labels. These exact strings are
# stable UUID-owned graphics from the generated carrier.
text = text.replace('(start 20 20)\n\t\t(end 220 180)',
                    '(start 20 20)\n\t\t(end 185 145)')
text = text.replace('(start 205 62)\n\t\t(end 219 95)', '(start 174 42)\n\t\t(end 184 72)')
text = text.replace('FALCON-01 CARRIER — SENSOR-POWER PLACEMENT V0.9',
                    'FALCON-01 CARRIER — COMPACT PREVIEW V1.0')
text = text.replace('(rev "PLACEMENT V0.9")', '(rev "COMPACT PREVIEW V1.0")')
for old, new in {
    '(at 120 25 0)': '(at 102.5 25 0)', '(at 42 29 0)': '(at 30 29 0)',
    '(at 78 29 0)': '(at 56 29 0)', '(at 160 29 0)': '(at 136 29 0)',
    '(at 150 101 0)': '(at 116 103 0)', '(at 180 174 0)': '(at 145 142 0)',
    '(at 120 176 0)': '(at 102.5 143 0)', '(at 190 168 0)': '(at 116 139 0)',
    '(at 213 78.5 90)': '(at 179 57 90)',
}.items():
    text = text.replace(old, new)

BOARD.write_text(text, encoding="utf-8")
print(f"Compacted {len(changes)} footprints to a 165 x 125 mm preview board")
