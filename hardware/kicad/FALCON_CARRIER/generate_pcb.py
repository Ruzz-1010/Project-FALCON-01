#!/usr/bin/env python3
"""Generate the provisional FALCON-01 carrier placement board for KiCad 10."""

from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

from generate_schematic import MODULES


OUT = Path(__file__).with_name("FALCON_CARRIER.kicad_pcb")


def uid(key: str) -> str:
    return str(uuid5(NAMESPACE_URL, f"falcon-carrier-pcb/{key}"))


placements = {
    # Left edge: field-service connectors in physical cable order.
    "J2": (32, 45), "J7": (32, 75), "J8": (32, 105),
    "J9": (32, 135), "J10": (32, 160),
    # I2C distribution column; short shared-bus paths and clear addressing order.
    "J4": (78, 48), "J5": (78, 78), "J6": (78, 108),
    "U4": (78, 138),
    # Pull-ups remain physically close to the associated field inputs.
    "R1": (51, 75), "R2": (51, 135),
    # Center/right: rigid motion sensor, GPS, controller, and antenna edge.
    "U3": (135, 88), "J3": (145, 45), "U2": (165, 65),
    # Bottom service and power section, separated from BNO085/GPS.
    "J12": (120, 150), "U1": (160, 152), "U5": (180, 130),
    "J11": (208, 130), "J1": (208, 158),
}

nets = []
for _, _, pins, _, _ in MODULES:
    for _, net in pins:
        if net not in nets:
            nets.append(net)
net_id = {name: index + 1 for index, name in enumerate(nets)}


def property_block(ref: str, value: str, ref_y: float) -> str:
    return f'''    (property "Reference" "{ref}" (at 0 {ref_y:.2f} 0) (layer "F.SilkS")
      (uuid "{uid(ref + '/ref')}") (effects (font (size 1 1) (thickness 0.15))))
    (property "Value" "{value}" (at 0 5 0) (layer "F.Fab")
      (uuid "{uid(ref + '/value')}") (effects (font (size 1 1) (thickness 0.15))))
    (property "Datasheet" "" (at 0 0 0) (layer "F.Fab") (hide yes)
      (uuid "{uid(ref + '/datasheet')}") (effects (font (size 1.27 1.27))))
    (property "Description" "PROVISIONAL FOOTPRINT — VERIFY PHYSICAL MODULE" (at 0 0 0)
      (layer "F.Fab") (hide yes) (uuid "{uid(ref + '/description')}")
      (effects (font (size 1.27 1.27))))'''


def footprint(ref: str, value: str, pins: list[tuple[str, str]], x: float, y: float) -> str:
    count = len(pins)
    two_rows = count > 6
    columns = 2 if two_rows else 1
    rows = (count + columns - 1) // columns
    body_w = 27.94 if two_rows else 10.16
    body_h = max(10.16, (rows - 1) * 2.54 + 7.62)
    pads = []
    for index, (number, net) in enumerate(pins):
        if two_rows:
            col = index % 2
            row = index // 2
            px = -12.7 if col == 0 else 12.7
            py = (row - (rows - 1) / 2) * 2.54
        else:
            px = 0
            py = (index - (rows - 1) / 2) * 2.54
        shape = "rect" if index == 0 else "circle"
        pads.append(
            f'''    (pad "{number}" thru_hole {shape} (at {px:.2f} {py:.2f})
      (size 2.2 2.2) (drill 1) (layers "*.Cu" "*.Mask")
      (net {net_id[net]} "{net}") (uuid "{uid(ref + '/pad/' + number)}"))'''
        )
    return f'''  (footprint "FALCON_PROVISIONAL_{value}"
    (layer "F.Cu") (uuid "{uid(ref)}") (at {x:.2f} {y:.2f})
    (descr "PROVISIONAL Project FALCON module envelope")
    (tags "FALCON PROVISIONAL VERIFY")
{property_block(ref, value, -body_h / 2 - 2.0)}
    (path "/{uid(ref)}")
    (attr through_hole)
    (fp_rect (start {-body_w / 2:.2f} {-body_h / 2:.2f}) (end {body_w / 2:.2f} {body_h / 2:.2f})
      (stroke (width 0.3) (type dash)) (fill none) (layer "F.SilkS")
      (uuid "{uid(ref + '/outline')}"))
{chr(10).join(pads)}
  )'''


def esp32_devkitc_footprint(ref: str, value: str, pins: list[tuple[str, str]], x: float, y: float) -> str:
    """38-pad geometry from Espressif's official ESP32-DevKitC footprint."""
    used = {number: net for number, net in pins}
    pads = []
    for number in range(1, 39):
        if number <= 19:
            px, py = 0.0, (number - 1) * 2.54
        else:
            px, py = 25.4, (38 - number) * 2.54
        shape = "rect" if number == 1 else "oval"
        net_clause = ""
        if str(number) in used:
            net = used[str(number)]
            net_clause = f' (net {net_id[net]} "{net}")'
        pads.append(
            f'''    (pad "{number}" thru_hole {shape} (at {px:.2f} {py:.2f} 270)
      (size 1.2 2.0) (drill 0.8) (layers "*.Cu" "*.Mask"){net_clause}
      (uuid "{uid(ref + '/pad/' + str(number))}"))'''
        )
    return f'''  (footprint "FALCON_LOCKED_ESP32_DEVKITC_V4"
    (layer "F.Cu") (uuid "{uid(ref)}") (at {x:.2f} {y:.2f} 90)
    (descr "ESP32-DevKitC V4 geometry locked from official Espressif KiCad library")
    (tags "ESP32 DevKitC V4 WROOM-32E OFFICIAL GEOMETRY")
{property_block(ref, "ESP32-DevKitC_V4_WROOM-32E", -3.1)}
    (path "/{uid(ref)}") (attr through_hole)
    (fp_rect (start -1.5 -1.1) (end 26.9 46.82)
      (stroke (width 0.2) (type solid)) (fill none) (layer "F.Fab")
      (uuid "{uid(ref + '/outline')}"))
    (fp_rect (start 3.73 -7.01) (end 21.71 -1.12)
      (stroke (width 0.25) (type solid)) (fill none) (layer "F.SilkS")
      (uuid "{uid(ref + '/usb')}"))
    (fp_text user "USB / POWER END" (at 12.7 -4.1 0) (layer "F.SilkS")
      (uuid "{uid(ref + '/usb-label')}")
      (effects (font (size 0.8 0.8) (thickness 0.15))))
    (fp_text user "ANTENNA END" (at 12.7 44.45 0) (layer "F.SilkS")
      (uuid "{uid(ref + '/antenna-label')}")
      (effects (font (size 0.8 0.8) (thickness 0.15))))
{chr(10).join(pads)}
  )'''


footprints = []
for ref, value, pins, _, _ in MODULES:
    x, y = placements[ref]
    if ref == "U2":
        footprints.append(esp32_devkitc_footprint(ref, value, pins, x, y))
    else:
        footprints.append(footprint(ref, value, pins, x, y))

holes = []
for index, (x, y) in enumerate(((26, 26), (214, 26), (26, 174), (214, 174)), start=1):
    holes.append(f'''  (footprint "FALCON_PROVISIONAL_M3_HOLE" (layer "F.Cu")
    (uuid "{uid('H' + str(index))}") (at {x} {y})
    (property "Reference" "H{index}" (at 0 -4 0) (layer "F.SilkS")
      (uuid "{uid('H' + str(index) + '/ref')}") (effects (font (size 1 1) (thickness 0.15))))
    (property "Value" "M3 PROVISIONAL" (at 0 4 0) (layer "F.Fab")
      (uuid "{uid('H' + str(index) + '/value')}") (effects (font (size 1 1) (thickness 0.15))))
    (attr exclude_from_pos_files exclude_from_bom)
    (fp_circle (center 0 0) (end 3.2 0) (stroke (width 0.3) (type solid))
      (fill none) (layer "F.SilkS") (uuid "{uid('H' + str(index) + '/circle')}"))
    (pad "" np_thru_hole circle (at 0 0) (size 3.2 3.2) (drill 3.2)
      (layers "*.Cu" "*.Mask") (uuid "{uid('H' + str(index) + '/pad')}"))
  )''')

net_lines = ['  (net 0 "")'] + [f'  (net {net_id[name]} "{name}")' for name in nets]

board = f'''(kicad_pcb
  (version 20260206) (generator "pcbnew") (generator_version "10.0")
  (general (thickness 1.6) (legacy_teardrops no))
  (paper "A4")
  (title_block (title "FALCON-01 LOW-VOLTAGE CARRIER") (date "2026-08-20")
    (rev "PLACEMENT V0.3") (company "PROJECT FALCON-01")
    (comment 1 "ALL FOOTPRINTS PROVISIONAL — VERIFY AT 1:1")
    (comment 2 "NOT APPROVED FOR FABRICATION"))
  (layers
    (0 "F.Cu" signal) (31 "B.Cu" signal)
    (36 "B.SilkS" user "b.silkscreen") (37 "F.SilkS" user "f.silkscreen")
    (39 "Dwgs.User" user "User.Drawings")
    (44 "Edge.Cuts" user))
  (setup (pad_to_mask_clearance 0) (allow_soldermask_bridges_in_footprints no)
    (tenting front back))
{chr(10).join(net_lines)}
{chr(10).join(footprints)}
{chr(10).join(holes)}
  (gr_rect (start 20 20) (end 220 180)
    (stroke (width 0.5) (type default)) (fill none) (layer "Edge.Cuts")
    (uuid "{uid('outline')}"))
  (gr_text "FALCON-01 CARRIER — PROVISIONAL PLACEMENT V0.3" (at 120 25 0)
    (layer "F.SilkS") (uuid "{uid('title')}")
    (effects (font (size 2.2 2.2) (thickness 0.4)) (justify bottom)))
  (gr_text "VERIFY EVERY MODULE, CONNECTOR AND HOLE AT 1:1 BEFORE FABRICATION" (at 120 176 0)
    (layer "F.SilkS") (uuid "{uid('warning')}")
    (effects (font (size 1.2 1.2) (thickness 0.25)) (justify bottom)))
  (gr_text "FIELD SENSORS" (at 42 29 0) (layer "F.SilkS")
    (uuid "{uid('zone-field')}")
    (effects (font (size 1.1 1.1) (thickness 0.22)) (justify bottom)))
  (gr_text "I2C DISTRIBUTION" (at 78 29 0) (layer "F.SilkS")
    (uuid "{uid('zone-i2c')}")
    (effects (font (size 1.1 1.1) (thickness 0.22)) (justify bottom)))
  (gr_text "MOTION / CONTROL" (at 160 29 0) (layer "F.SilkS")
    (uuid "{uid('zone-control')}")
    (effects (font (size 1.1 1.1) (thickness 0.22)) (justify bottom)))
  (gr_text "POWER / SERVICE" (at 180 174 0) (layer "F.SilkS")
    (uuid "{uid('zone-power')}")
    (effects (font (size 1.1 1.1) (thickness 0.22)) (justify bottom)))
  (gr_rect (start 205 50) (end 218 80)
    (stroke (width 0.5) (type dash_dot)) (fill none) (layer "Dwgs.User")
    (uuid "{uid('antenna-keepout')}"))
  (gr_text "ESP32 ANTENNA KEEP-OUT" (at 213 65 90) (layer "Dwgs.User")
    (uuid "{uid('antenna-text')}")
    (effects (font (size 1 1) (thickness 0.2)) (justify bottom)))
)
'''

OUT.write_text(board, encoding="utf-8")
print(f"Generated {OUT}")
