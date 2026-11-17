#!/usr/bin/env python3
"""Build the FALCON-01 catamaran as real solids and export STEP + STL.

Dimensions are taken from the approved Option B preview
(`static website presentation/buoy-options/lite-buoy-spar.js`) and scaled up
in revision 2 to fit the final component list in the sensor approval list:
6x 3 W panel (3S2P), 12.8 V LiFePO4, LTE board, and a seabed anchor carrying
the 4-20 mA pressure transmitter. Revision 3 hollows the enclosure and models
the internals: 4x 10 Ah packs (40 Ah / 512 Wh), BMS, fuse, MPPT, tray with
ESP32 / ADS1115 / INA260 / LTE / SD logger, terminal block and desiccant.
The draft comes from the mass budget, so the hulls sit at the waterline the
budget actually predicts.

Requires build123d (not installed with the project). Use a throwaway venv:

    python3 -m venv /tmp/cadvenv
    /tmp/cadvenv/bin/pip install "build123d==0.9.1" "ocpsvg==0.5.0"
    python3 cad/catamaran/falcon_catamaran.py          # refresh hydrostatics.json
    /tmp/cadvenv/bin/python cad/catamaran/build_step.py

Outputs (in cad/catamaran/out/):
    falcon_catamaran.step     - import into Onshape / Fusion / FreeCAD
    falcon_catamaran_asm.stl  - quick visual check

First-pass geometry only, not a fabrication drawing.
"""

from __future__ import annotations

import json
import math
import re
from pathlib import Path

from build123d import (
    Box,
    Compound,
    Cylinder,
    Pos,
    RectangleRounded,
    Rot,
    Sphere,
    extrude,
)

try:
    from build123d import export_step, export_stl
except ImportError:  # older build123d layout
    from build123d.exporters3d import export_step, export_stl

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"

params = json.loads((HERE / "params.json").read_text())
geom = params["geometry"]
hydro = json.loads((OUT / "hydrostatics.json").read_text())
DRAFT = hydro["draft_m"] * 1000.0  # mm

# ---------------------------------------------------------------- hulls
PONTOON_D = geom["pontoon_diameter_m"] * 1000.0
PONTOON_L = geom["pontoon_length_m"] * 1000.0
BEAM = geom["pontoon_beam_m"] * 1000.0
PONTOON_R = PONTOON_D / 2.0
PONTOON_CY = PONTOON_R - DRAFT
PONTOON_TOP = PONTOON_D - DRAFT

# ---------------------------------------------------------------- deck
DECK_L = geom["deck_length_m"] * 1000.0
DECK_W = geom["deck_width_m"] * 1000.0
DECK_T = geom["deck_thickness_m"] * 1000.0
DECK_TOP = geom["deck_top_above_waterline_m"] * 1000.0
DECK_BOTTOM = DECK_TOP - DECK_T

# ------------------------------------------------------- electronics tube
CAB_R = geom["electronics_tube_diameter_m"] * 500.0
CAB_H = geom["electronics_tube_height_m"] * 1000.0
CAB_TOP = DECK_TOP + CAB_H
CAB_WALL = geom["enclosure_wall_m"] * 1000.0
CAB_IN_R = CAB_R - CAB_WALL

# ------------------------------------------------------------- solar array
PANEL_ROWS = geom["solar_panel_rows"]
PANEL_COLS = geom["solar_panel_cols"]
CELL_W = geom["solar_panel_cell_width_m"] * 1000.0
CELL_D = geom["solar_panel_cell_depth_m"] * 1000.0
CELL_GAP = geom["solar_panel_gap_m"] * 1000.0
PANEL_T = geom["solar_panel_thickness_m"] * 1000.0
PANEL_TILT = geom["solar_panel_tilt_deg"]
FRAME_Y = geom["solar_frame_height_above_waterline_m"] * 1000.0
FRAME_Z = -30.0
ARR_W = PANEL_COLS * CELL_W + (PANEL_COLS - 1) * CELL_GAP
ARR_D = PANEL_ROWS * CELL_D + (PANEL_ROWS - 1) * CELL_GAP
COLLAR_Y = CAB_TOP - 60.0

# --------------------------------------------------------------- sensors
MAST_H = geom["mast_height_m"] * 1000.0
MAST_X = geom["mast_x_offset_m"] * 1000.0
GPS_H = geom["gps_post_height_m"] * 1000.0

# --------------------------------------------------------------- mooring
DEPTH = geom["mooring_depth_m"] * 1000.0
LINE_R = geom["mooring_line_diameter_m"] * 500.0
# Midships, on the centre of flotation, so mooring tension trims the buoy
# evenly fore and aft instead of pulling the bow down.
ANCHOR_X = 0.0
BLOCK_L = geom["anchor_block_length_m"] * 1000.0
BLOCK_W = geom["anchor_block_width_m"] * 1000.0
BLOCK_H = geom["anchor_block_height_m"] * 1000.0
ANCHOR_TOP = -DEPTH
RISER_H = geom["transmitter_riser_height_m"] * 1000.0
TX_H = geom["transmitter_body_height_m"] * 1000.0
TX_R = geom["transmitter_body_diameter_m"] * 500.0
CABLE_R = geom["transmitter_cable_diameter_m"] * 500.0

parts = []


def add(shape, label: str):
    shape.label = label
    parts.append(shape)
    return shape


def vcyl(radius: float, height: float) -> object:
    """Cylinder with its axis vertical (Y up)."""
    return Rot(90, 0, 0) * Cylinder(radius=radius, height=height)


# ================================================================== hulls
half_cyl = (PONTOON_L - PONTOON_D) / 2.0


def hull_solid():
    """Capsule hull, built fresh per side so each keeps its own label."""
    return (
        Cylinder(radius=PONTOON_R, height=half_cyl * 2.0, rotation=(0, 90, 0))
        + Pos(half_cyl, 0, 0) * Sphere(PONTOON_R)
        + Pos(-half_cyl, 0, 0) * Sphere(PONTOON_R)
    )


add(Pos(0, PONTOON_CY, -BEAM / 2.0) * hull_solid(), "PONTOON_PORT")
add(Pos(0, PONTOON_CY, BEAM / 2.0) * hull_solid(), "PONTOON_STBD")

# ================================================================== deck
deck = Pos(0, DECK_BOTTOM + DECK_T / 2.0, 0) * Box(DECK_L, DECK_T, DECK_W)

SLOT_X, SLOT_Z, SLOT_R = 90.0, 78.0, 14.0
PITCH_X, PITCH_Z = 128.0, 124.0
CLEAR_RADIUS = CAB_R + 30.0
BEAM_X = DECK_L * 0.32

tools = []
LAND_SPOTS = (
    (geom["mast_x_offset_m"] * 1000.0, 0.0, 110.0),   # mast foot
    (-380.0, 300.0, 90.0),                            # GPS post
    (520.0, -480.0, 100.0),                           # antenna whip foot
)
ix = int(DECK_L / PITCH_X) + 1
iz = int(DECK_W / PITCH_Z) + 1
for i in range(-ix, ix + 1):
    x = i * PITCH_X
    if abs(x) > DECK_L / 2.0 - 90.0:
        continue
    if abs(abs(x) - BEAM_X) < 80.0:      # solid land over the cross beams
        continue
    for j in range(-iz, iz + 1):
        z = j * PITCH_Z
        if abs(z) > DECK_W / 2.0 - 80.0:
            continue
        if (x * x + z * z) ** 0.5 < CLEAR_RADIUS:
            continue
        if any(((x - lx) ** 2 + (z - lz) ** 2) ** 0.5 < lr for lx, lz, lr in LAND_SPOTS):
            continue
        tools.append(
            Pos(x, DECK_BOTTOM - 40.0, z)
            * Rot(-90, 0, 0)
            * extrude(RectangleRounded(SLOT_X, SLOT_Z, SLOT_R), amount=80.0)
        )

if tools:
    cutter = tools[0]
    for t in tools[1:]:
        cutter = cutter + t
    deck = deck - cutter
add(deck, "DECK_THROUGH_SLOTTED")

# ============================================ cross beams and hull saddles
MEMBER_H = 55.0
MEMBER_BOTTOM = DECK_BOTTOM - MEMBER_H
SADDLE_H = MEMBER_BOTTOM - PONTOON_TOP

for i, sx in enumerate((-BEAM_X, BEAM_X)):
    add(
        Pos(sx, DECK_BOTTOM - MEMBER_H / 2.0, 0) * Box(90.0, MEMBER_H, BEAM + 260.0),
        f"DECK_CROSS_BEAM_{i + 1}",
    )

if SADDLE_H > 0:
    n = 0
    for sx in (-BEAM_X, BEAM_X):
        for sz in (-BEAM / 2.0, BEAM / 2.0):
            n += 1
            add(
                Pos(sx, PONTOON_TOP + SADDLE_H / 2.0, sz) * Box(160.0, SADDLE_H, 190.0),
                f"PONTOON_SADDLE_{n}",
            )

# ==================================================== round electronics tube
# Hollow shell: 8 mm wall, so the electronics and battery bank have a real
# cavity instead of sitting inside a solid block.
add(
    Pos(0, DECK_TOP + CAB_H / 2.0, 0) * (vcyl(CAB_R, CAB_H) - vcyl(CAB_IN_R, CAB_H)),
    "ROUND_ELECTRONICS_TUBE",
)
add(Pos(0, DECK_TOP + 13.0, 0) * vcyl(CAB_R + 30.0, 26.0), "ROUND_CABINET_FOOT_FLANGE")
# Full cover closes the open end of the tube; the bolted hatch sits on it.
COVER_T = 5.0
add(Pos(0, CAB_TOP + COVER_T / 2.0, 0) * vcyl(CAB_R, COVER_T), "ENCLOSURE_TOP_COVER")
add(Pos(0, CAB_TOP + COVER_T + 11.0, 0) * vcyl(CAB_R - 12.0, 22.0), "BOLTED_TOP_HATCH")

# ------------------------------------------------------------- internals
# Everything below sits on the enclosure bulkhead, inside the Ø404 cavity.
BULK_T = 10.0
BULK_Y = DECK_TOP + BULK_T / 2.0
add(Pos(0, BULK_Y, 0) * vcyl(CAB_IN_R + 2.0, BULK_T), "ENCLOSURE_BULKHEAD")
FLOOR = DECK_TOP + BULK_T

# 4x 12.8 V 10 Ah LiFePO4 packs = 40 Ah / 512 Wh, wired in parallel.
BATT_L = geom["battery_pack_length_m"] * 1000.0
BATT_W = geom["battery_pack_width_m"] * 1000.0
BATT_H = geom["battery_pack_height_m"] * 1000.0
BATT_Y = FLOOR + 5.0 + BATT_H / 2.0
n = 0
for sx in (-85.0, 85.0):
    for sz in (-60.0, 60.0):
        n += 1
        add(
            Pos(sx, BATT_Y, sz) * Box(BATT_L, BATT_H, BATT_W),
            f"BATTERY_PACK_{n}",
        )
BATT_TOP = BATT_Y + BATT_H / 2.0

# BMS, main fuse and the MPPT charger sit on top of the pack.
add(Pos(0, BATT_TOP + 13.0, -120.0) * Box(120.0, 20.0, 40.0), "BATTERY_BMS")
add(Pos(150.0, BATT_TOP + 15.0, 0) * Box(60.0, 30.0, 40.0), "MAIN_FUSE_BLOCK")
add(Pos(0, BATT_TOP + 15.0, 120.0) * Box(110.0, 30.0, 70.0), "MPPT_CHARGE_CONTROLLER")

# Electronics tray and the boards that ride on it.
TRAY_Y = BATT_TOP + 45.0
add(Pos(0, TRAY_Y, 0) * vcyl(140.0, 6.0), "ELECTRONICS_TRAY")
BOARD = TRAY_Y + 3.0
add(Pos(-60.0, BOARD + 6.0, 60.0) * Box(70.0, 12.0, 55.0), "ESP32_BOARD")
add(Pos(10.0, BOARD + 4.0, 95.0) * Box(30.0, 8.0, 22.0), "ADS1115_BOARD")
add(Pos(45.0, BOARD + 4.0, 95.0) * Box(25.0, 8.0, 18.0), "INA260_BOARD")
add(Pos(65.0, BOARD + 6.0, -50.0) * Box(90.0, 12.0, 60.0), "LTE_MODEM_BOARD")
add(Pos(-40.0, BOARD + 4.0, -95.0) * Box(45.0, 8.0, 35.0), "SD_LOGGER_BOARD")
add(Pos(105.0, BOARD + 12.0, 60.0) * Box(60.0, 25.0, 30.0), "TERMINAL_BLOCK")

# Desiccant box and two cable glands through the top hatch.
add(Pos(-100.0, BOARD + 35.0, -70.0) * Box(70.0, 70.0, 70.0), "DESICCANT_BOX")
add(Pos(-100.0, CAB_TOP + COVER_T + 11.0, 40.0) * vcyl(12.0, 34.0), "CABLE_GLAND_1")
add(Pos(100.0, CAB_TOP + COVER_T + 11.0, -40.0) * vcyl(12.0, 34.0), "CABLE_GLAND_2")

# ============================================== 3S2P solar array on a frame
add(Pos(0, COLLAR_Y, 0) * Rot(90, 0, 0) * Cylinder(radius=CAB_R + 16.0, height=24.0), "PANEL_COLLAR_BAND")

post_top = FRAME_Y - 20.0
post_h = post_top - COLLAR_Y
for i, sx in enumerate((-(ARR_W / 2.0 - 50.0), ARR_W / 2.0 - 50.0)):
    add(
        Pos(sx, COLLAR_Y + post_h / 2.0, FRAME_Z) * Box(30.0, post_h, 30.0),
        f"PANEL_SUPPORT_POST_{i + 1}",
    )

add(Pos(0, FRAME_Y - 24.0, FRAME_Z) * Box(ARR_W * 0.8, 22.0, 28.0), "PANEL_CROSS_MEMBER")

RAIL = 30.0
for i, sz in enumerate((-(ARR_D / 2.0 + 20.0), ARR_D / 2.0 + 20.0)):
    add(
        Pos(0, FRAME_Y, FRAME_Z + sz) * Rot(PANEL_TILT, 0, 0) * Box(ARR_W + 60.0, RAIL, RAIL),
        f"PANEL_END_RAIL_{i + 1}",
    )
for i, sx in enumerate((-(ARR_W / 2.0 + 20.0), ARR_W / 2.0 + 20.0)):
    add(
        Pos(sx, FRAME_Y, FRAME_Z) * Rot(PANEL_TILT, 0, 0) * Box(RAIL, RAIL, ARR_D),
        f"PANEL_SIDE_RAIL_{i + 1}",
    )

cell = 0
for i in range(PANEL_COLS):
    for j in range(PANEL_ROWS):
        cell += 1
        px = (i - (PANEL_COLS - 1) / 2.0) * (CELL_W + CELL_GAP)
        pz = (j - (PANEL_ROWS - 1) / 2.0) * (CELL_D + CELL_GAP)
        add(
            Pos(px, FRAME_Y + 4.0, FRAME_Z + pz) * Rot(PANEL_TILT, 0, 0) * Box(CELL_W, PANEL_T, CELL_D),
            f"SOLAR_PANEL_{cell}",
        )

# ================================================================ GPS puck
GPS_X, GPS_Z = -380.0, 300.0
add(Pos(GPS_X, DECK_TOP + GPS_H / 2.0, GPS_Z) * vcyl(15.0, GPS_H), "GPS_POST")
add(Pos(GPS_X, DECK_TOP + GPS_H + 15.0, GPS_Z) * vcyl(50.0, 30.0), "REQUIRED_GPS_POSITION_SECURITY_PUCK")

# =============================================================== wind mast
add(Pos(MAST_X, DECK_TOP + MAST_H / 2.0, 0) * vcyl(18.0, MAST_H), "WIND_MAST")
add(Pos(MAST_X, DECK_TOP + 30.0, 0) * vcyl(45.0, 60.0), "MAST_FOOT")
add(Pos(MAST_X, DECK_TOP + MAST_H - 120.0, 0) * vcyl(26.0, 65.0), "TOPMARK_BEACON")
add(Pos(MAST_X, DECK_TOP + MAST_H - 87.5, 0) * Sphere(26.0), "BEACON_DOME")

# ============================================================ antenna whip
add(Pos(520.0, DECK_TOP + 15.0, -480.0) * Box(60.0, 30.0, 60.0), "WHIP_FOOT")
add(Pos(520.0, DECK_TOP + 190.0, -480.0) * vcyl(9.0, 350.0), "WIFI_LTE_WHIP_ANTENNA")

# =================================== seabed anchor + pressure transmitter
add(Pos(ANCHOR_X, ANCHOR_TOP - BLOCK_H / 2.0, 0) * Box(BLOCK_L, BLOCK_H, BLOCK_W), "ANCHOR_CONCRETE_BLOCK")
add(Pos(ANCHOR_X, ANCHOR_TOP + 30.0, 0) * vcyl(35.0, 60.0), "ANCHOR_LIFTING_EYE")

TX_X = ANCHOR_X
TX_Z = 100.0
add(Pos(TX_X, ANCHOR_TOP + RISER_H / 2.0, TX_Z) * vcyl(25.0, RISER_H), "TRANSMITTER_RISER_POST")
add(Pos(TX_X, ANCHOR_TOP + RISER_H + TX_H / 2.0, TX_Z) * vcyl(TX_R, TX_H), "SS316_PRESSURE_TRANSMITTER")

CABLE_BASE = ANCHOR_TOP + RISER_H + TX_H
add(
    Pos(TX_X + 70.0, CABLE_BASE + (DECK_BOTTOM - CABLE_BASE) / 2.0, TX_Z)
    * vcyl(CABLE_R, DECK_BOTTOM - CABLE_BASE),
    "TRANSMITTER_CABLE",
)

add(Pos(ANCHOR_X, DECK_BOTTOM - 10.0, 0) * Box(200.0, 20.0, 200.0), "MOORING_BRIDLE_PLATE")
add(Pos(ANCHOR_X, DECK_BOTTOM - 45.0, 0) * vcyl(30.0, 50.0), "MOORING_SHACKLE")
LINE_BASE = ANCHOR_TOP + 30.0
LINE_TOP = DECK_BOTTOM - 60.0
add(
    Pos(ANCHOR_X, LINE_BASE + (LINE_TOP - LINE_BASE) / 2.0, 0)
    * vcyl(LINE_R, LINE_TOP - LINE_BASE),
    "MOORING_LINE",
)

# ================================================================== export
try:
    assembly = Compound(children=parts)
except Exception:  # build123d < 0.10
    assembly = Compound.make_compound(parts)

OUT.mkdir(exist_ok=True)
step_path = OUT / "falcon_catamaran.step"
stl_path = OUT / "falcon_catamaran_asm.stl"
export_step(assembly, str(step_path))
export_stl(assembly, str(stl_path))


def name_inner_solids(path: Path) -> int:
    """Give each exported body the name of the part it belongs to.

    build123d writes one component per child named after its label, but wraps
    the actual solid in an anonymous PRODUCT('SOLID'). Importers (Onshape,
    Fusion) take the leaf name, so every body would arrive called "SOLID".
    """
    text = path.read_text()
    pattern = re.compile(r"PRODUCT\('([^']*)'")
    edits = []
    current, seen = None, {}
    for m in pattern.finditer(text):
        name = m.group(1)
        if name != "SOLID":
            current = name
            continue
        if not current:
            continue
        seen[current] = seen.get(current, 0) + 1
        unique = current if seen[current] == 1 else f"{current}_{seen[current]}"
        start, end = m.span(1)
        edits.append((start, end, unique))
    if not edits:
        return 0
    for start, end, unique in reversed(edits):
        text = text[:start] + unique + text[end:]
    path.write_text(text)
    return len(edits)


renamed = name_inner_solids(step_path)

print(f"parts      : {len(parts)}")
print(f"pontoons   : 2 x D{PONTOON_D:.0f} x {PONTOON_L:.0f} mm, beam {BEAM:.0f} mm c/c")
print(f"draft      : {DRAFT:.1f} mm   (from mass budget)")
print(f"hull top   : {PONTOON_TOP:.1f} mm above waterline")
print(f"deck top   : {DECK_TOP:.1f} mm above waterline")
print(f"tube       : D{CAB_R*2:.0f} x {CAB_H:.0f} mm, top at {CAB_TOP:.1f} mm")
print(f"battery    : {geom['battery_pack_count']} x {BATT_L:.0f} x {BATT_W:.0f} x {BATT_H:.0f} mm packs (40 Ah / 512 Wh)")
print(f"array      : {PANEL_COLS}x{PANEL_ROWS} cells, {ARR_W:.0f} x {ARR_D:.0f} mm, top at ~{FRAME_Y:.0f} mm")
print(f"mast head  : {DECK_TOP + MAST_H:.1f} mm above waterline")
print(f"anchor     : {BLOCK_L:.0f} x {BLOCK_W:.0f} x {BLOCK_H:.0f} mm at {DEPTH:.0f} mm depth")
print(f"named      : {renamed} inner solids")
print(f"wrote      : {step_path}")
print(f"wrote      : {stl_path}")
