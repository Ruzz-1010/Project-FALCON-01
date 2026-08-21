#!/usr/bin/env python3
"""Apply the reviewed industrial placement without changing pads or nets."""
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5
import re

BOARD = Path(__file__).with_name("FALCON_CARRIER.kicad_pcb")

# 165 x 125 mm board: (20,20) to (185,145). H1-H4 remain fixed.
PLACEMENTS = {
    # Sensor/service edge, left-to-right in requested functional order.
    "J3": (40, 50, 0),       # GPS
    "U3": (68, 47, 0),       # BNO085 IMU
    "J2": (88, 33, 0),       # Pressure
    "J7": (100, 33, 0),      # Wind speed
    "J8": (112, 33, 0),      # Wind direction
    "J9": (124, 33, 0),      # Water temperature
    "J4": (143, 43, 0),      # Battery monitor
    "J5": (167, 43, 0),      # Solar monitor
    # Sensor support kept below its corresponding connector.
    "J10": (88, 60, 0), "R1": (45, 75, 0), "R2": (60, 75, 0),
    "U4": (112, 46, 0), "J6": (170, 68, 0),
    # Controller is visually centered; antenna/USB end remains unobstructed.
    "U2": (109, 84, -90),
    # Communication/service edge.
    "J12": (43, 108, 0),
    # Power flow: input -> protection/interlock -> regulator -> decoupling.
    "J1": (40, 132, 0), "U6": (57, 132, 0), "JP1": (72, 132, 0),
    "C1": (84, 132, 0), "U1": (92, 132, 0), "C2": (100, 132, 0),
    # Cooling driver and edge-facing fan connectors.
    "R3": (164, 84, 0), "R5": (172, 84, 0), "Q1": (180, 84, 0),
    "R4": (164, 93, 0), "R6": (172, 93, 0), "Q2": (180, 93, 0),
    "R7": (164, 102, 0), "R8": (172, 102, 0),
    "J11": (150, 132, 0), "J13": (169, 132, 0),
    "H1": (25, 25, 0), "H2": (180, 25, 0),
    "H3": (25, 140, 0), "H4": (180, 140, 0),
}

# One accessible, consistently spaced service bank below the controller.
for index in range(1, 21):
    column = (index - 1) % 10
    row = (index - 1) // 10
    PLACEMENTS[f"TP{index}"] = (68 + column * 7.4, 109 + row * 9, 0)


def footprint_blocks(text: str):
    cursor = 0
    while True:
        start = text.find("(footprint ", cursor)
        if start < 0:
            return
        depth = 0
        quoted = escaped = False
        for index in range(start, len(text)):
            char = text[index]
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
                    yield start, index + 1
                    cursor = index + 1
                    break


text = BOARD.read_text(encoding="utf-8")
changes = []
found = set()
for start, end in footprint_blocks(text):
    block = text[start:end]
    match = re.search(r'\(property "Reference" "([^"]+)"', block)
    if not match or match.group(1) not in PLACEMENTS:
        continue
    ref = match.group(1)
    at = re.search(r'\(at\s+[-.\d]+\s+[-.\d]+(?:\s+[-.\d]+)?\)', block)
    if not at:
        continue
    x, y, angle = PLACEMENTS[ref]
    replacement = f"(at {x:g} {y:g}" + (f" {angle:g}" if angle else "") + ")"
    changes.append((start + at.start(), start + at.end(), replacement))
    found.add(ref)

missing = sorted(set(PLACEMENTS) - found)
if missing:
    raise RuntimeError(f"Placement references missing from PCB: {missing}")
for start, end, replacement in reversed(changes):
    text = text[:start] + replacement + text[end:]

# Reposition the ESP32 antenna keep-out beside the centered controller.
text = text.replace('(start 174 42)\n\t\t(end 184 72)',
                    '(start 127 69)\n\t\t(end 143 99)')
text = text.replace('(at 179 57 90)', '(at 139 84 90)')

# Remove outdated layout labels and connector legends before adding the v2 set.
obsolete = {
    "FIELD SENSORS", "I2C DISTRIBUTION", "MOTION / CONTROL",
    "POWER / SERVICE", "SERVICE TEST POINTS",
    "1:+  2:SCL  3:SDA  4:G", "1:+  2:PULSE  3:G",
    "1:+  2:VANE  3:G", "1:+  2:TEMP  3:G", "1:+  2:LEAK  3:G",
    "SENSOR INTERFACES", "GPS", "IMU", "PRESSURE", "WIND SPD",
    "WIND DIR", "TEMP", "BAT MON", "SOLAR MON", "ESP32 CONTROLLER",
    "COMM / SERVICE", "POWER MANAGEMENT", "FAN CONTROL",
}
for label in obsolete:
    pattern = re.compile(r'\n\t\(gr_text "' + re.escape(label) + r'".*?\n\t\)', re.S)
    text = pattern.sub('', text)

labels = [
    ("SENSOR INTERFACES", 102.5, 23, 1.25),
    ("GPS", 40, 27.5, 0.75), ("IMU", 68, 27.5, 0.75),
    ("PRESSURE", 88, 27.5, 0.65), ("WIND SPD", 100, 27.5, 0.65),
    ("WIND DIR", 112, 27.5, 0.65), ("TEMP", 124, 27.5, 0.65),
    ("BAT MON", 143, 27.5, 0.65), ("SOLAR MON", 167, 27.5, 0.65),
    ("ESP32 CONTROLLER", 109, 65, 1.0),
    ("COMM / SERVICE", 93, 104, 0.9),
    ("POWER MANAGEMENT", 69, 142, 0.9),
    ("FAN CONTROL", 157, 78, 0.8),
]
blocks = []
for label, x, y, size in labels:
    key = f"industrial-placement/{label}"
    blocks.append(f'''\t(gr_text "{label}"
\t\t(at {x:g} {y:g} 0) (layer "F.SilkS")
\t\t(uuid "{uuid5(NAMESPACE_URL, key)}")
\t\t(effects (font (size {size:g} {size:g}) (thickness 0.16)) (justify bottom))
\t)''')

text = text.replace('FALCON-01 CARRIER — COMPACT PREVIEW V1.0',
                    'FALCON-01 CARRIER — INDUSTRIAL PLACEMENT V2.0')
text = text.replace('(rev "COMPACT PREVIEW V1.0")',
                    '(rev "INDUSTRIAL PLACEMENT V2.0")')
insert = text.rfind("\n\t(embedded_fonts no)\n)")
if insert < 0:
    raise RuntimeError("PCB terminator not found")
text = text[:insert] + "\n" + "\n".join(blocks) + text[insert:]
BOARD.write_text(text, encoding="utf-8")
print(f"Applied professional placement to {len(changes)} footprints")
