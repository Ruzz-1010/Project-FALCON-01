#!/usr/bin/env python3
"""Refresh selected 3D model links while preserving the KiCad-saved PCB."""
import re
from pathlib import Path

BOARD = Path(__file__).with_name("FALCON_CARRIER.kicad_pcb")
ASSIGNMENTS = {
    "U6": "power_protection_preview.wrl",
    "JP1": "jumper_2pin.wrl",
    "C1": "capacitor_0603.wrl",
    "C2": "capacitor_0603.wrl",
}

text = BOARD.read_text(encoding="utf-8")
cursor = 0
changes = []
while True:
    start = text.find("(footprint ", cursor)
    if start < 0: break
    depth = 0
    for index in range(start, len(text)):
        if text[index] == "(": depth += 1
        elif text[index] == ")":
            depth -= 1
            if depth == 0:
                end = index + 1
                break
    block = text[start:end]
    ref = re.search(r'\(property "Reference" "([^"]+)"', block)
    if ref and ref.group(1) in ASSIGNMENTS:
        wanted = ASSIGNMENTS[ref.group(1)]
        updated = re.sub(r'(\$\{KIPRJMOD\}/models/)[^\"]+\.wrl', r'\g<1>' + wanted, block, count=1)
        changes.append((start, end, updated))
    cursor = end

for start, end, updated in reversed(changes):
    text = text[:start] + updated + text[end:]
BOARD.write_text(text, encoding="utf-8")
print(f"Refreshed {len(changes)} preview model links")
