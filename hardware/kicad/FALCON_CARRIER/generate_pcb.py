#!/usr/bin/env python3
"""Generate the provisional FALCON-01 carrier placement board for KiCad 10."""

from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

from generate_schematic import MODULES, TEST_POINT_NETS


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
    "U3": (135, 88), "J3": (145, 45), "U2": (173, 90),
    # Bottom service and power section, separated from BNO085/GPS.
    "J12": (120, 150), "U1": (154, 160), "C1": (146, 160), "C2": (162, 160),
    "R3": (174, 124), "R4": (174, 132), "R5": (186, 124), "R6": (186, 132),
    "Q1": (198, 124), "Q2": (198, 132), "R7": (174, 140), "R8": (186, 140),
    "J11": (204, 146), "J13": (204, 158), "J1": (208, 170),
    "U6": (190, 158), "JP1": (175, 158),
}

for index, _net in enumerate(TEST_POINT_NETS, start=1):
    column = (index - 1) % 9
    row = (index - 1) // 9
    placements[f"TP{index}"] = (96 + column * 13.5, 108 + row * 12)

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


GH_CONNECTORS = {"J2": 4, "J6": 4, "J7": 3, "J8": 3, "J9": 3,
                 "J10": 3, "J12": 4}
VH_CONNECTORS = {"J1": 2}
FAN_CONNECTORS = {"J11", "J13"}


def jst_gh_top_footprint(
    ref: str, value: str, pins: list[tuple[str, str]], x: float, y: float
) -> str:
    """JST BMxxB-GHS-TBT top-entry SMT land pattern from the official GH catalog."""
    circuits = GH_CONNECTORS[ref]
    connected = dict(pins)
    contact_span = (circuits - 1) * 1.25
    body_width = contact_span + 4.50
    pads = []
    for index in range(circuits):
        number = str(index + 1)
        px = -contact_span / 2 + index * 1.25
        net = connected[number]
        pads.append(f'''    (pad "{number}" smd roundrect (at {px:.3f} -4.750)
      (size 0.60 1.70) (layers "F.Cu" "F.Paste" "F.Mask")
      (roundrect_rratio 0.20) (net {net_id[net]} "{net}")
      (uuid "{uid(ref + '/pad/' + number)}"))''')
    # Two soldered reinforcement tabs shown in JST's top-entry board layout.
    for side, px in (("L", -body_width / 2), ("R", body_width / 2)):
        pads.append(f'''    (pad "MP" smd roundrect (at {px:.3f} -1.550)
      (size 1.35 2.50) (layers "F.Cu" "F.Paste" "F.Mask")
      (roundrect_rratio 0.15) (uuid "{uid(ref + '/mount/' + side)}"))''')
    return f'''  (footprint "JST_GH_{circuits:02d}P_TOP_BM{circuits:02d}B-GHS-TBT"
    (layer "F.Cu") (uuid "{uid(ref)}") (at {x:.2f} {y:.2f})
    (descr "JST BM{circuits:02d}B-GHS-TBT official-catalog top-entry SMT land pattern")
    (tags "JST GH 1.25MM TOP ENTRY OFFICIAL CATALOG")
{property_block(ref, f"BM{circuits:02d}B-GHS-TBT", -7.5)}
    (path "/{uid(ref)}") (attr smd)
    (fp_rect (start {-body_width / 2:.3f} -4.250)
      (end {body_width / 2:.3f} 0)
      (stroke (width 0.15) (type solid)) (fill none) (layer "F.Fab")
      (uuid "{uid(ref + '/outline')}"))
    (fp_text user "1" (at {-contact_span / 2:.3f} -6.25 0) (layer "F.SilkS")
      (uuid "{uid(ref + '/pin1-label')}")
      (effects (font (size 0.75 0.75) (thickness 0.15))))
    (fp_text user "TOP MATE" (at 0 1.2 0) (layer "F.SilkS")
      (uuid "{uid(ref + '/cable-label')}")
      (effects (font (size 0.65 0.65) (thickness 0.12))))
{chr(10).join(pads)}
  )'''


def jst_vh_footprint(
    ref: str, value: str, pins: list[tuple[str, str]], x: float, y: float
) -> str:
    """JST BxP-VH-FB-B 3.96 mm THT geometry from the official VH catalog."""
    circuits = VH_CONNECTORS[ref]
    connected = dict(pins)
    span = (circuits - 1) * 3.96
    body_width = span + 5.84
    pads = []
    for index in range(circuits):
        number = str(index + 1)
        px = -span / 2 + index * 3.96
        net_clause = ""
        if number in connected:
            net = connected[number]
            net_clause = f' (net {net_id[net]} "{net}")'
        shape = "rect" if number == "1" else "circle"
        pads.append(f'''    (pad "{number}" thru_hole {shape} (at {px:.3f} 0)
      (size 2.40 2.40) (drill 1.30) (layers "*.Cu" "*.Mask"){net_clause}
      (uuid "{uid(ref + '/pad/' + number)}"))''')
    return f'''  (footprint "JST_VH_{circuits:02d}P_B{circuits}P-VH-FB-B"
    (layer "F.Cu") (uuid "{uid(ref)}") (at {x:.2f} {y:.2f})
    (descr "JST B{circuits}P-VH-FB-B official-catalog 3.96 mm THT geometry")
    (tags "JST VH 3.96MM SHROUDED OFFICIAL CATALOG")
{property_block(ref, f"B{circuits}P-VH-FB-B", -7.5)}
    (path "/{uid(ref)}") (attr through_hole)
    (fp_rect (start {-body_width / 2:.3f} -3.70)
      (end {body_width / 2:.3f} 6.00)
      (stroke (width 0.25) (type solid)) (fill none) (layer "F.SilkS")
      (uuid "{uid(ref + '/outline')}"))
    (fp_text user "1" (at {-span / 2:.3f} -5.0 0) (layer "F.SilkS")
      (uuid "{uid(ref + '/pin1-label')}")
      (effects (font (size 0.9 0.9) (thickness 0.18))))
    (fp_text user "CABLE" (at 0 7.1 0) (layer "F.SilkS")
      (uuid "{uid(ref + '/cable-label')}")
      (effects (font (size 0.75 0.75) (thickness 0.14))))
{chr(10).join(pads)}
  )'''


def fan_header_footprint(
    ref: str, value: str, pins: list[tuple[str, str]], x: float, y: float
) -> str:
    """Four-pin 2.54 mm fan header pin pattern for Molex 470531000."""
    connected = dict(pins)
    pads = []
    for index in range(4):
        number = str(index + 1)
        px = (index - 1.5) * 2.54
        net = connected[number]
        shape = "rect" if number == "1" else "circle"
        pads.append(f'''    (pad "{number}" thru_hole {shape} (at {px:.2f} 0)
      (size 2.0 2.0) (drill 1.0) (layers "*.Cu" "*.Mask")
      (net {net_id[net]} "{net}") (uuid "{uid(ref + '/pad/' + number)}"))''')
    return f'''  (footprint "MOLEX_470531000_4PIN_FAN_HEADER"
    (layer "F.Cu") (uuid "{uid(ref)}") (at {x:.2f} {y:.2f})
    (descr "Molex 470531000 4-circuit 2.54 mm vertical fan header; outline verify on receipt")
    (tags "MOLEX 47053 FAN PWM 2.54MM")
{property_block(ref, "470531000", -4.0)}
    (path "/{uid(ref)}") (attr through_hole)
    (fp_rect (start -5.2 -2.4) (end 5.2 2.4)
      (stroke (width 0.2) (type solid)) (fill none) (layer "F.SilkS")
      (uuid "{uid(ref + '/outline')}"))
    (fp_text user "1 GND" (at -3.81 3.5 0) (layer "F.SilkS")
      (uuid "{uid(ref + '/pin1-label')}")
      (effects (font (size 0.7 0.7) (thickness 0.13))))
    (fp_text user "5V TACH PWM" (at 1.3 3.5 0) (layer "F.SilkS")
      (uuid "{uid(ref + '/signals-label')}")
      (effects (font (size 0.65 0.65) (thickness 0.12))))
{chr(10).join(pads)}
  )'''


def smd_resistor_0603_footprint(
    ref: str, value: str, pins: list[tuple[str, str]], x: float, y: float
) -> str:
    pads = []
    for number, px in (("1", -0.8), ("2", 0.8)):
        net = dict(pins)[number]
        pads.append(f'''    (pad "{number}" smd roundrect (at {px} 0)
      (size 0.9 0.95) (layers "F.Cu" "F.Paste" "F.Mask")
      (roundrect_rratio 0.2) (net {net_id[net]} "{net}")
      (uuid "{uid(ref + '/pad/' + number)}"))''')
    return f'''  (footprint "R_0603_1608Metric"
    (layer "F.Cu") (uuid "{uid(ref)}") (at {x:.2f} {y:.2f})
{property_block(ref, value, -1.8)} (path "/{uid(ref)}") (attr smd)
    (fp_rect (start -1.1 -0.6) (end 1.1 0.6)
      (stroke (width 0.15) (type solid)) (fill none) (layer "F.SilkS")
      (uuid "{uid(ref + '/outline')}"))
{chr(10).join(pads)}
  )'''


def sot23_2n7002_footprint(
    ref: str, value: str, pins: list[tuple[str, str]], x: float, y: float
) -> str:
    positions = {"1": (-1.0, 0.95), "2": (1.0, 0.95), "3": (0.0, -0.95)}
    pads = []
    for number, net in pins:
        px, py = positions[number]
        pads.append(f'''    (pad "{number}" smd roundrect (at {px} {py})
      (size 0.9 1.0) (layers "F.Cu" "F.Paste" "F.Mask")
      (roundrect_rratio 0.2) (net {net_id[net]} "{net}")
      (uuid "{uid(ref + '/pad/' + number)}"))''')
    return f'''  (footprint "SOT-23_2N7002"
    (layer "F.Cu") (uuid "{uid(ref)}") (at {x:.2f} {y:.2f})
{property_block(ref, value, -2.5)} (path "/{uid(ref)}") (attr smd)
    (fp_rect (start -1.5 -1.45) (end 1.5 1.45)
      (stroke (width 0.15) (type solid)) (fill none) (layer "F.SilkS")
      (uuid "{uid(ref + '/outline')}"))
{chr(10).join(pads)}
  )'''


def sot25_ap2112_footprint(
    ref: str, value: str, pins: list[tuple[str, str]], x: float, y: float
) -> str:
    """Diodes AP2112 SOT25 pin pattern: 1 VIN, 2 GND, 3 EN, 4 NC, 5 VOUT."""
    connected = dict(pins)
    positions = {"1": (-0.95, 1.10), "2": (0.0, 1.10), "3": (0.95, 1.10),
                 "4": (0.95, -1.10), "5": (-0.95, -1.10)}
    pads = []
    for number, (px, py) in positions.items():
        net_clause = ""
        if number in connected:
            net = connected[number]
            net_clause = f' (net {net_id[net]} "{net}")'
        pads.append(f'''    (pad "{number}" smd roundrect (at {px} {py})
      (size 0.65 1.05) (layers "F.Cu" "F.Paste" "F.Mask")
      (roundrect_rratio 0.18){net_clause}
      (uuid "{uid(ref + '/pad/' + number)}"))''')
    return f'''  (footprint "SOT-25_AP2112K"
    (layer "F.Cu") (uuid "{uid(ref)}") (at {x:.2f} {y:.2f})
    (descr "Diodes AP2112K SOT25; official pin assignment and package geometry")
    (tags "AP2112K SOT25 LDO 3V3")
{property_block(ref, "AP2112K-3.3TRG1", -2.7)} (path "/{uid(ref)}") (attr smd)
    (fp_rect (start -1.55 -1.45) (end 1.55 1.45)
      (stroke (width 0.15) (type solid)) (fill none) (layer "F.SilkS")
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
    (layer "F.Cu") (uuid "{uid(ref)}") (at {x:.2f} {y:.2f} 270)
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


OFFICIAL_MODULE_GEOMETRY = {
    # Coordinates are from the manufacturers' Eagle board datum, in mm.
    "U3": {
        "size": (25.4, 22.86),
        "pads": [(f"A{i}", 6.35 + (i - 1) * 2.54, 2.54) for i in range(1, 7)]
                + [(f"B{i}", 6.35 + (i - 1) * 2.54, 20.32) for i in range(1, 7)],
        "holes": [(2.54, 2.54), (22.86, 2.54), (2.54, 20.32), (22.86, 20.32)],
        "source": "Adafruit BNO08x Rev C official Eagle CAD",
    },
    "J3": {
        "size": (25.4, 34.29),
        "pads": [(str(i), 22.86 - (i - 1) * 2.54, 2.032) for i in range(1, 10)],
        "holes": [(2.54, 31.75), (22.86, 31.75)],
        "source": "Adafruit Ultimate GPS PID 746 official Eagle CAD",
    },
    "J4": {
        "size": (22.86, 22.86),
        "pads": [(str(i), 2.54 + (i - 1) * 2.54, 2.54) for i in range(1, 9)],
        "holes": [(2.54, 20.32), (20.32, 20.32)],
        "source": "Adafruit INA260 PID 4226 official Eagle CAD",
    },
    "J5": {
        "size": (22.86, 22.86),
        "pads": [(str(i), 2.54 + (i - 1) * 2.54, 2.54) for i in range(1, 9)],
        "holes": [(2.54, 20.32), (20.32, 20.32)],
        "source": "Adafruit INA260 PID 4226 official Eagle CAD",
    },
    "U4": {
        "size": (25.4, 17.78),
        "pads": [(f"B{i}", 6.35 + (i - 1) * 2.54, 2.54) for i in range(1, 7)]
                + [(f"A{i}", 6.35 + (i - 1) * 2.54, 15.24) for i in range(1, 7)],
        "holes": [(2.54, 2.54), (22.86, 2.54), (2.54, 15.24), (22.86, 15.24)],
        "source": "Adafruit ADS1115 PID 1085 STEMMA QT official Eagle CAD",
    },
}


def official_module_footprint(
    ref: str, value: str, pins: list[tuple[str, str]], x: float, y: float
) -> str:
    """Create a carrier socket from a manufacturer board datum."""
    spec = OFFICIAL_MODULE_GEOMETRY[ref]
    width, height = spec["size"]
    connected = dict(pins)
    pads = []
    for index, (number, px, py) in enumerate(spec["pads"]):
        net_clause = ""
        if number in connected:
            net = connected[number]
            net_clause = f' (net {net_id[net]} "{net}")'
        shape = "rect" if index == 0 else "circle"
        pads.append(f'''    (pad "{number}" thru_hole {shape}
      (at {px - width / 2:.3f} {py - height / 2:.3f})
      (size 2.0 2.0) (drill 1.0) (layers "*.Cu" "*.Mask"){net_clause}
      (uuid "{uid(ref + '/pad/' + number)}"))''')
    holes = []
    for index, (hx, hy) in enumerate(spec["holes"], start=1):
        holes.append(f'''    (pad "" np_thru_hole circle
      (at {hx - width / 2:.3f} {hy - height / 2:.3f})
      (size 2.5 2.5) (drill 2.5) (layers "*.Cu" "*.Mask")
      (uuid "{uid(ref + '/mount/' + str(index))}"))''')
    return f'''  (footprint "FALCON_LOCKED_{value}"
    (layer "F.Cu") (uuid "{uid(ref)}") (at {x:.2f} {y:.2f})
    (descr "{spec['source']}; receiving check still required")
    (tags "FALCON MANUFACTURER CAD SOCKET")
{property_block(ref, value, -height / 2 - 2.0)}
    (path "/{uid(ref)}") (attr through_hole)
    (fp_rect (start {-width / 2:.3f} {-height / 2:.3f})
      (end {width / 2:.3f} {height / 2:.3f})
      (stroke (width 0.25) (type solid)) (fill none) (layer "F.SilkS")
      (uuid "{uid(ref + '/outline')}"))
    (fp_text user "CAD LOCKED · VERIFY 1:1" (at 0 0 0) (layer "F.Fab")
      (uuid "{uid(ref + '/cad-label')}")
      (effects (font (size 0.8 0.8) (thickness 0.14))))
{chr(10).join(pads)}
{chr(10).join(holes)}
  )'''


def test_point_footprint(ref: str, net: str, x: float, y: float) -> str:
    """Create a labeled 1.0 mm drilled pad for bench probing."""
    short_label = net.replace("+", "")
    return f'''  (footprint "FALCON_TEST_POINT_THT"
    (layer "F.Cu") (uuid "{uid(ref)}") (at {x:.2f} {y:.2f})
    (descr "FALCON labeled through-hole service test point")
    (tags "TEST POINT SERVICE")
    (property "Reference" "{ref}" (at 0 -2.8 0) (layer "F.SilkS")
      (uuid "{uid(ref + '/ref')}") (effects (font (size 0.75 0.75) (thickness 0.13))))
    (property "Value" "{short_label}" (at 0 2.8 0) (layer "F.SilkS")
      (uuid "{uid(ref + '/value')}") (effects (font (size 0.65 0.65) (thickness 0.12))))
    (property "Datasheet" "" (at 0 0 0) (layer "F.Fab") (hide yes)
      (uuid "{uid(ref + '/datasheet')}") (effects (font (size 1.27 1.27))))
    (property "Description" "Accessible service test point" (at 0 0 0)
      (layer "F.Fab") (hide yes) (uuid "{uid(ref + '/description')}")
      (effects (font (size 1.27 1.27))))
    (path "/{uid(ref)}") (attr through_hole exclude_from_bom)
    (fp_circle (center 0 0) (end 1.8 0) (stroke (width 0.2) (type solid))
      (fill none) (layer "F.SilkS") (uuid "{uid(ref + '/outline')}"))
    (pad "1" thru_hole circle (at 0 0) (size 2.4 2.4) (drill 1.0)
      (layers "*.Cu" "*.Mask") (net {net_id[net]} "{net}")
      (uuid "{uid(ref + '/pad/1')}"))
  )'''


footprints = []
for ref, value, pins, _, _ in MODULES:
    x, y = placements[ref]
    if ref == "U2":
        footprints.append(esp32_devkitc_footprint(ref, value, pins, x, y))
    elif ref in GH_CONNECTORS:
        footprints.append(jst_gh_top_footprint(ref, value, pins, x, y))
    elif ref in VH_CONNECTORS:
        footprints.append(jst_vh_footprint(ref, value, pins, x, y))
    elif ref in FAN_CONNECTORS:
        footprints.append(fan_header_footprint(ref, value, pins, x, y))
    elif ref in {"R3", "R4", "R5", "R6", "R7", "R8"}:
        footprints.append(smd_resistor_0603_footprint(ref, value, pins, x, y))
    elif ref in {"Q1", "Q2"}:
        footprints.append(sot23_2n7002_footprint(ref, value, pins, x, y))
    elif ref == "U1":
        footprints.append(sot25_ap2112_footprint(ref, value, pins, x, y))
    elif ref in {"C1", "C2"}:
        footprints.append(smd_resistor_0603_footprint(ref, value, pins, x, y))
    elif ref in OFFICIAL_MODULE_GEOMETRY:
        footprints.append(official_module_footprint(ref, value, pins, x, y))
    elif ref.startswith("TP"):
        footprints.append(test_point_footprint(ref, pins[0][1], x, y))
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
    (rev "PLACEMENT V0.9") (company "PROJECT FALCON-01")
    (comment 1 "MODULE AND CONNECTOR GEOMETRY — VERIFY AT 1:1")
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
  (gr_text "FALCON-01 CARRIER — SENSOR-POWER PLACEMENT V0.9" (at 120 25 0)
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
  (gr_text "EXT 5V — REMOVE USB FIRST" (at 190 168 0) (layer "F.SilkS")
    (uuid "{uid('external-power-warning')}")
    (effects (font (size 0.9 0.9) (thickness 0.18)) (justify bottom)))
  (gr_text "SERVICE TEST POINTS" (at 150 101 0) (layer "F.SilkS")
    (uuid "{uid('zone-test-points')}")
    (effects (font (size 1.0 1.0) (thickness 0.20)) (justify bottom)))
  (gr_rect (start 205 62) (end 219 95)
    (stroke (width 0.5) (type dash_dot)) (fill none) (layer "Dwgs.User")
    (uuid "{uid('antenna-keepout')}"))
  (gr_text "ESP32 ANTENNA KEEP-OUT" (at 213 78.5 90) (layer "Dwgs.User")
    (uuid "{uid('antenna-text')}")
    (effects (font (size 1 1) (thickness 0.2)) (justify bottom)))
)
'''

OUT.write_text(board, encoding="utf-8")
print(f"Generated {OUT}")
