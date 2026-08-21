#!/usr/bin/env python3
"""Add compact field-connector pin legends without regenerating the PCB."""
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

BOARD = Path(__file__).with_name("FALCON_CARRIER.kicad_pcb")
LEGENDS = [
    ("J2", "1:+  2:SCL  3:SDA  4:G", 34.5, 44.5),
    ("J7", "1:+  2:PULSE  3:G", 34.5, 62.5),
    ("J8", "1:+  2:VANE  3:G", 34.5, 80.5),
    ("J9", "1:+  2:TEMP  3:G", 34.5, 98.5),
    ("J10", "1:+  2:LEAK  3:G", 34.5, 116.5),
]

text = BOARD.read_text(encoding="utf-8")
blocks = []
for ref, label, x, y in LEGENDS:
    marker = f"PIN LEGEND {ref}"
    if f'(gr_text "{label}"' in text:
        continue
    uid = uuid5(NAMESPACE_URL, f"falcon-carrier/{marker}")
    blocks.append(f'''\t(gr_text "{label}"
\t\t(at {x} {y} 0)
\t\t(layer "F.SilkS")
\t\t(uuid "{uid}")
\t\t(effects (font (size 0.58 0.58) (thickness 0.11)) (justify left bottom))
\t)''')

if blocks:
    insertion = text.rfind("\n\t(embedded_fonts no)\n)")
    if insertion < 0:
        raise RuntimeError("Final board terminator not found")
    text = text[:insertion] + "\n" + "\n".join(blocks) + text[insertion:]
    BOARD.write_text(text, encoding="utf-8")
print(f"Added {len(blocks)} connector legend groups")
