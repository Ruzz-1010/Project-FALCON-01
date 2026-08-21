#!/usr/bin/env python3
"""Attach local FALCON VRML samples to a KiCad-saved PCB without regenerating it."""
import re
from pathlib import Path

BOARD = Path(__file__).with_name("FALCON_CARRIER.kicad_pcb")


def model_for(ref: str) -> tuple[str, tuple[float, float, float]] | None:
    fixed = {
        "J1": ("jst_vh_2", (0, 1.15, 0)), "U1": ("sot25", (0, 0, 0)),
        "U2": ("esp32_devkitc", (12.7, -22.86, 0)), "U3": ("bno085", (0, 0, 0)),
        "J2": ("jst_gh_4", (0, -2.125, 0)), "J3": ("gps", (0, 0, 0)),
        "J4": ("ina260", (0, 0, 0)), "J5": ("ina260", (0, 0, 0)),
        "J6": ("jst_gh_4", (0, -2.125, 0)), "U4": ("ads1115", (0, 0, 0)),
        "J7": ("jst_gh_3", (0, -2.125, 0)), "J8": ("jst_gh_3", (0, -2.125, 0)),
        "J9": ("jst_gh_3", (0, -2.125, 0)), "J10": ("jst_gh_3", (0, -2.125, 0)),
        "J11": ("fan_header", (0, 0, 0)), "J12": ("jst_gh_4", (0, -2.125, 0)),
        "J13": ("fan_header", (0, 0, 0)), "Q1": ("sot23", (0, 0, 0)),
        "Q2": ("sot23", (0, 0, 0)), "U6": ("module_generic", (0, 0, 0)),
        "JP1": ("module_generic", (0, 0, 0)),
    }
    if ref in fixed:
        return fixed[ref]
    if re.fullmatch(r"[CR][1-8]", ref):
        return "resistor_0603", (0, 0, 0)
    if ref.startswith("TP"):
        return "testpoint", (0, 0, 0)
    return None


text = BOARD.read_text(encoding="utf-8")
blocks = []
cursor = 0
while True:
    start = text.find("(footprint ", cursor)
    if start < 0:
        break
    depth = 0
    quoted = False
    escaped = False
    end = None
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
        if char == '"':
            quoted = True
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                end = index + 1
                break
    if end is None:
        raise RuntimeError(f"Unbalanced footprint starting at byte {start}")
    blocks.append((start, end))
    cursor = end

insertions = []
for start, end in blocks:
    block = text[start:end]
    match = re.search(r'\(property "Reference" "([^"]+)"', block)
    if not match or "(model " in block:
        continue
    ref = match.group(1)
    selected = model_for(ref)
    if not selected:
        continue
    name, (ox, oy, oz) = selected
    model = (f'\n\t(model "${{KIPRJMOD}}/models/{name}.wrl"\n'
             f'\t\t(offset (xyz {ox:.3f} {oy:.3f} {oz:.3f}))\n'
             '\t\t(scale (xyz 1 1 1))\n\t\t(rotate (xyz 0 0 0))\n\t)')
    insertions.append((end - 1, model, ref))

for position, model, _ref in reversed(insertions):
    text = text[:position] + model + text[position:]

BOARD.write_text(text, encoding="utf-8")
print(f"Attached {len(insertions)} local 3D models to {BOARD}")
