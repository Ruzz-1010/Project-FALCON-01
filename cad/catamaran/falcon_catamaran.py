#!/usr/bin/env python3
"""FALCON-01 Option B (catamaran) first-pass hydrostatics and mesh export.

Computes draft, freeboard, reserve buoyancy, waterplane properties and a
small-angle GM for the twin-pontoon buoy described in params.json, then
writes a binary STL of the assembly plus a JSON report.

This is a first-pass design aid. It is NOT a stability book, NOT a
fabrication drawing, and it is NOT a substitute for a loaded flotation
test in the intended water type.

Usage:
    python3 cad/catamaran/falcon_catamaran.py
    python3 cad/catamaran/falcon_catamaran.py --payload 45
"""

from __future__ import annotations

import argparse
import json
import math
import struct
from dataclasses import dataclass
from pathlib import Path

RHO_SEAWATER = 1025.0
G = 9.80665

HERE = Path(__file__).resolve().parent
DEFAULT_PARAMS = HERE / "params.json"


# --------------------------------------------------------------------------
# Geometry: submerged properties of a capsule (cylinder + two hemispheres)
# --------------------------------------------------------------------------

def _segment_area(radius: float, depth: float) -> float:
    """Area of the circular segment submerged to `depth` in a circle of `radius`."""
    if depth <= 0.0:
        return 0.0
    if depth >= 2.0 * radius:
        return math.pi * radius * radius
    a = radius - depth  # signed distance from centre to the waterline chord
    return radius * radius * math.acos(max(-1.0, min(1.0, a / radius))) - a * math.sqrt(
        max(0.0, radius * radius - a * a)
    )


def _segment_centroid_height(radius: float, depth: float) -> float:
    """Height of the submerged segment centroid above the lowest point."""
    if depth <= 0.0:
        return 0.0
    if depth >= 2.0 * radius:
        return radius
    # half-angle: chord sits at radius*cos(alpha) from the centre
    alpha = math.acos(max(-1.0, min(1.0, 1.0 - depth / radius)))
    denom = 3.0 * (2.0 * alpha - math.sin(2.0 * alpha))
    if denom <= 1e-12:
        return 0.5 * depth
    dist_from_centre = 4.0 * radius * math.sin(alpha) ** 3 / denom
    return radius - dist_from_centre


def _capsule_slices(length: float, radius: float, slices: int = 480):
    """Yield (dx, R(x)) for a capsule of total `length` and end `radius`."""
    cyl = max(0.0, length - 2.0 * radius)
    dx = length / slices
    for i in range(slices):
        x = -0.5 * length + (i + 0.5) * dx
        ax = abs(x)
        if ax <= 0.5 * cyl:
            r = radius
        else:
            s = min(radius, ax - 0.5 * cyl)
            r = math.sqrt(max(0.0, radius * radius - s * s))
        yield dx, r


def displaced_volume(length: float, radius: float, draft: float) -> float:
    """Submerged volume of one capsule at the given draft, in m^3."""
    return sum(dx * _segment_area(r, draft) for dx, r in _capsule_slices(length, radius))


def waterplane(length: float, radius: float, draft: float) -> tuple[float, float]:
    """Waterplane area and transverse second moment about the pontoon centreline."""
    area = 0.0
    inertia = 0.0
    for dx, r in _capsule_slices(length, radius):
        if draft <= 0.0 or draft >= 2.0 * r:
            continue
        chord = 2.0 * math.sqrt(max(0.0, 2.0 * r * draft - draft * draft))
        area += chord * dx
        inertia += chord ** 3 / 12.0 * dx
    return area, inertia


def vertical_centroid(length: float, radius: float, draft: float) -> float:
    """KB: height of the submerged volume centroid above the keel."""
    vol = 0.0
    moment = 0.0
    for dx, r in _capsule_slices(length, radius):
        a = _segment_area(r, draft)
        vol += a * dx
        moment += a * _segment_centroid_height(r, draft) * dx
    return moment / vol if vol > 0.0 else 0.0


def solve_draft(length: float, radius: float, mass: float, rho: float) -> float:
    """Bisection for the draft where displaced mass equals `mass`."""
    target = mass / rho
    lo, hi = 0.0, 2.0 * radius
    if displaced_volume(length, radius, hi) < target:
        return hi
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if displaced_volume(length, radius, mid) < target:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


# --------------------------------------------------------------------------
# Hydrostatics
# --------------------------------------------------------------------------

@dataclass
class Hydrostatics:
    total_mass_kg: float
    capacity_kg: float
    draft_m: float
    freeboard_m: float
    submerged_fraction: float
    reserve_buoyancy_fraction: float
    waterplane_area_m2: float
    waterplane_inertia_m4: float
    bm_m: float
    kb_m: float
    kg_m: float
    gm_m: float
    roll_period_s: float

    def as_dict(self) -> dict:
        return {
            "total_mass_kg": round(self.total_mass_kg, 2),
            "capacity_kg": round(self.capacity_kg, 2),
            "draft_m": round(self.draft_m, 4),
            "draft_mm": round(self.draft_m * 1000.0, 1),
            "freeboard_m": round(self.freeboard_m, 4),
            "freeboard_mm": round(self.freeboard_m * 1000.0, 1),
            "submerged_fraction": round(self.submerged_fraction, 4),
            "reserve_buoyancy_fraction": round(self.reserve_buoyancy_fraction, 4),
            "waterplane_area_m2": round(self.waterplane_area_m2, 4),
            "waterplane_inertia_m4": round(self.waterplane_inertia_m4, 5),
            "bm_m": round(self.bm_m, 3),
            "kb_m": round(self.kb_m, 3),
            "kg_m": round(self.kg_m, 3),
            "gm_m": round(self.gm_m, 3),
            "roll_period_s": round(self.roll_period_s, 2),
        }


def analyse(geom: dict, budget: list[dict], rho: float, extra_payload: float = 0.0) -> Hydrostatics:
    diameter = geom["pontoon_diameter_m"]
    length = geom["pontoon_length_m"]
    radius = diameter / 2.0
    beam = geom["pontoon_beam_m"]

    mass = sum(item["mass_kg"] for item in budget) + extra_payload
    capacity = 2.0 * displaced_volume(length, radius, diameter) * rho

    draft = solve_draft(length, radius, mass / 2.0, rho)
    submerged = 2.0 * displaced_volume(length, radius, draft)

    wp_area_one, wp_inertia_one = waterplane(length, radius, draft)
    # parallel-axis transfer to the vessel centreline, then mirror for the pair
    wp_inertia_pair = 2.0 * (wp_inertia_one + wp_area_one * (beam / 2.0) ** 2)

    bm = wp_inertia_pair / submerged if submerged > 0.0 else float("inf")
    kb = vertical_centroid(length, radius, draft)

    # KG: weighted mean of item heights above the keel
    wl_moment = sum(item["mass_kg"] * item["height_above_waterline_m"] for item in budget)
    if extra_payload:
        wl_moment += extra_payload * geom.get("payload_height_m", 0.10)
    kg = draft + wl_moment / mass

    gm = bm + kb - kg
    # roll period of the whole catamaran about its longitudinal axis
    inertia_vessel = 2.0 * mass / 2.0 * (beam / 2.0) ** 2  # crude radius-of-gyration
    k_roll = mass * G * gm
    period = 2.0 * math.pi * math.sqrt(inertia_vessel / k_roll) if k_roll > 0 else float("nan")

    return Hydrostatics(
        total_mass_kg=mass,
        capacity_kg=capacity,
        draft_m=draft,
        freeboard_m=diameter - draft,
        submerged_fraction=draft / diameter,
        reserve_buoyancy_fraction=1.0 - mass / capacity if capacity > 0 else 0.0,
        waterplane_area_m2=2.0 * wp_area_one,
        waterplane_inertia_m4=wp_inertia_pair,
        bm_m=bm,
        kb_m=kb,
        kg_m=kg,
        gm_m=gm,
        roll_period_s=period,
    )


# --------------------------------------------------------------------------
# Binary STL writer
# --------------------------------------------------------------------------

class Mesh:
    def __init__(self) -> None:
        self.tris: list[tuple[tuple[float, float, float], ...]] = []

    def add(self, a, b, c) -> None:
        self.tris.append((a, b, c))

    def quad(self, a, b, c, d) -> None:
        self.add(a, b, c)
        self.add(a, c, d)

    def merge(self, other: "Mesh") -> None:
        self.tris.extend(other.tris)


def cylinder(mesh: Mesh, r: float, h: float, seg: int, y0: float, x: float = 0.0, z: float = 0.0) -> None:
    """Vertical cylinder, base at y0."""
    for i in range(seg):
        a0 = 2.0 * math.pi * i / seg
        a1 = 2.0 * math.pi * (i + 1) / seg
        p0 = (x + r * math.cos(a0), y0, z + r * math.sin(a0))
        p1 = (x + r * math.cos(a1), y0, z + r * math.sin(a1))
        p2 = (p1[0], y0 + h, p1[2])
        p3 = (p0[0], y0 + h, p0[2])
        mesh.quad(p0, p1, p2, p3)
        mesh.add((x, y0, z), p1, p0)
        mesh.add((x, y0 + h, z), p3, p2)


def capsule_x(mesh: Mesh, r: float, length: float, cx: float, cy: float, rz: float, seg: int = 40) -> None:
    """Capsule of radius r and total length along the X axis."""
    cyl = length - 2.0 * r
    rings = max(4, seg // 2)

    def ring(ax: float, rad: float, phase: float = 0.0):
        return [
            (cx + ax, cy + rad * math.sin(2 * math.pi * i / seg + phase), rz + rad * math.cos(2 * math.pi * i / seg + phase))
            for i in range(seg)
        ]

    body = [ring(-cyl / 2.0, r), ring(cyl / 2.0, r)]
    for i in range(seg):
        j = (i + 1) % seg
        mesh.quad(body[0][i], body[0][j], body[1][j], body[1][i])

    for sign, base_x in ((-1.0, -cyl / 2.0), (1.0, cyl / 2.0)):
        prev = None
        for k in range(1, rings + 1):
            ang = math.pi / 2.0 * k / rings
            rad = r * math.cos(ang)
            ax = base_x + sign * r * math.sin(ang)
            cur = ring(ax, rad)
            if prev is None:
                for i in range(seg):
                    mesh.add((cx + base_x, cy, rz), cur[i], cur[(i + 1) % seg])
            else:
                for i in range(seg):
                    j = (i + 1) % seg
                    if sign > 0:
                        mesh.quad(prev[i], prev[j], cur[j], cur[i])
                    else:
                        mesh.quad(prev[j], prev[i], cur[i], cur[j])
            prev = cur


def box(mesh: Mesh, sx: float, sy: float, sz: float, cx: float, cy: float, cz: float) -> None:
    x0, x1 = cx - sx / 2, cx + sx / 2
    y0, y1 = cy - sy / 2, cy + sy / 2
    z0, z1 = cz - sz / 2, cz + sz / 2
    v = [
        (x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
        (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1),
    ]
    for face in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
        a, b, c, d = (v[i] for i in face)
        mesh.quad(a, b, c, d)


def tilted_box(mesh: Mesh, sx: float, sy: float, sz: float, cx: float, cy: float, cz: float, angle: float) -> None:
    """Box rotated about the X axis around its own centre."""
    ca, sa = math.cos(angle), math.sin(angle)
    tmp = Mesh()
    box(tmp, sx, sy, sz, 0.0, 0.0, 0.0)
    out = []
    for tri in tmp.tris:
        rot = []
        for px, py, pz in tri:
            rot.append((cx + px, cy + py * ca - pz * sa, cz + py * sa + pz * ca))
        out.append(tuple(rot))
    mesh.tris.extend(out)


def build_assembly(geom: dict, h: Hydrostatics, scale: float = 1000.0) -> Mesh:
    """Assembly mesh in millimetres, waterline at y = 0, keel at y = -draft."""
    mesh = Mesh()
    r = geom["pontoon_diameter_m"] / 2.0
    length = geom["pontoon_length_m"]
    beam = geom["pontoon_beam_m"]
    cy = -h.draft_m + r

    for x in (-beam / 2.0, beam / 2.0):
        capsule_x(mesh, r, length, x, cy, 0.0)

    # Height chain, all derived so the deck can never intersect the hulls.
    pontoon_top = -h.draft_m + 2.0 * r
    deck_top = geom["deck_top_above_waterline_m"]
    deck_t = geom["deck_thickness_m"]
    deck_bottom = deck_top - deck_t

    box(mesh, geom["deck_length_m"], deck_t, geom["deck_width_m"], 0.0, deck_bottom + deck_t / 2.0, 0.0)

    # Two cross beams across the beam, on saddles that sit on each hull.
    member_h = 0.055
    member_bottom = deck_bottom - member_h
    beam_x = geom["deck_length_m"] * 0.32
    saddle_h = member_bottom - pontoon_top
    for sx in (-beam_x, beam_x):
        box(mesh, 0.09, member_h, beam + 0.16, sx, deck_bottom - member_h / 2.0, 0.0)
        if saddle_h > 0.0:
            for sz in (-beam / 2.0, beam / 2.0):
                box(mesh, 0.16, saddle_h, 0.19, sx, pontoon_top + saddle_h / 2.0, sz)

    # Round electronics tube, foot flange and bolted hatch.
    tube_r = geom["electronics_tube_diameter_m"] / 2.0
    tube_h = geom["electronics_tube_height_m"]
    cylinder(mesh, tube_r, tube_h, 48, deck_top, 0.0, 0.0)
    cylinder(mesh, tube_r + 0.030, 0.026, 48, deck_top, 0.0, 0.0)
    cylinder(mesh, tube_r - 0.012, 0.022, 48, deck_top + tube_h, 0.0, 0.0)

    # 3S2P solar array: 2 rows x 3 columns of 150 mm cells on a tilted frame.
    rows = geom["solar_panel_rows"]
    cols = geom["solar_panel_cols"]
    cw = geom["solar_panel_cell_width_m"]
    cd = geom["solar_panel_cell_depth_m"]
    gap = geom["solar_panel_gap_m"]
    panel_t = geom["solar_panel_thickness_m"]
    arr_w = cols * cw + (cols - 1) * gap
    arr_d = rows * cd + (rows - 1) * gap
    frame_y = geom["solar_frame_height_above_waterline_m"]
    tilt = math.radians(geom["solar_panel_tilt_deg"])
    collar_y = deck_top + tube_h - 0.06
    frame_z = -0.03

    post_h = (frame_y - 0.02) - collar_y
    for sx in (-(arr_w / 2.0 - 0.05), arr_w / 2.0 - 0.05):
        box(mesh, 0.030, post_h, 0.030, sx, collar_y + post_h / 2.0, frame_z)
    box(mesh, arr_w * 0.8, 0.022, 0.028, 0.0, frame_y - 0.024, frame_z)

    # Frame rails, then the cells, all placed in the tilted frame.
    def tilted(sx, sy, sz, cx, cy, cz):
        tmp = Mesh()
        box(tmp, sx, sy, sz, 0.0, 0.0, 0.0)
        ca, sa = math.cos(tilt), math.sin(tilt)
        out = []
        for tri in tmp.tris:
            rot = [(cx + px, cy + py * ca - pz * sa, cz + py * sa + pz * ca) for px, py, pz in tri]
            out.append(tuple(rot))
        mesh.tris.extend(out)

    rail = 0.030
    for sz in (-(arr_d / 2.0 + 0.02), arr_d / 2.0 + 0.02):
        tilted(arr_w + 0.06, rail, rail, 0.0, frame_y, frame_z + sz)
    for sx in (-(arr_w / 2.0 + 0.02), arr_w / 2.0 + 0.02):
        tilted(rail, rail, arr_d, 0.0, frame_y, frame_z + sx)

    for i in range(cols):
        for j in range(rows):
            px = (i - (cols - 1) / 2.0) * (cw + gap)
            pz = (j - (rows - 1) / 2.0) * (cd + gap)
            tilted(cw, panel_t, cd, px, frame_y + 0.004, frame_z + pz)

    # GPS post + puck at the deck aft/port corner.
    gps_h = geom["gps_post_height_m"]
    cylinder(mesh, 0.015, gps_h, 12, deck_top, -0.38, 0.30)
    cylinder(mesh, 0.050, 0.030, 24, deck_top + gps_h, -0.38, 0.30)

    # Wind mast at the deck rear, with beacon.
    mast_h = geom["mast_height_m"]
    mast_x = geom["mast_x_offset_m"]
    cylinder(mesh, 0.018, mast_h, 14, deck_top, mast_x, 0.0)
    cylinder(mesh, 0.045, 0.060, 14, deck_top, mast_x, 0.0)
    cylinder(mesh, 0.026, 0.065, 16, deck_top + mast_h - 0.12, mast_x, 0.0)

    # Wi-Fi / LTE whip on the aft starboard corner.
    box(mesh, 0.06, 0.03, 0.06, 0.52, deck_top + 0.015, -0.48)
    cylinder(mesh, 0.009, 0.35, 10, deck_top + 0.03, 0.52, -0.48)

    # ---------------------------------------------------------------- mooring
    # Seabed anchor with the pressure transmitter mounted on it. The
    # transmitter is a seabed reference, not a buoy-mounted sensor.
    depth = geom["mooring_depth_m"]
    # Midships, on the centre of flotation, so the line trims the buoy evenly.
    anchor_x = 0.0
    bl = geom["anchor_block_length_m"]
    bw = geom["anchor_block_width_m"]
    bh = geom["anchor_block_height_m"]
    anchor_top = -depth

    box(mesh, bl, bh, bw, anchor_x, anchor_top - bh / 2.0, 0.0)
    cylinder(mesh, 0.035, 0.060, 16, anchor_top, anchor_x, 0.0)

    riser_h = geom["transmitter_riser_height_m"]
    tx_h = geom["transmitter_body_height_m"]
    tx_r = geom["transmitter_body_diameter_m"] / 2.0
    cylinder(mesh, 0.025, riser_h, 12, anchor_top, anchor_x, 0.10)
    cylinder(mesh, tx_r, tx_h, 24, anchor_top + riser_h, anchor_x, 0.10)

    # Cable from the transmitter head up to the deck bridle.
    cable_r = geom["transmitter_cable_diameter_m"] / 2.0
    cable_top = deck_bottom
    cable_base = anchor_top + riser_h + tx_h
    cylinder(mesh, cable_r, cable_top - cable_base, 8, cable_base, anchor_x + 0.07, 0.10)

    # Bridle plate on the deck and the mooring line down to the anchor eye.
    box(mesh, 0.20, 0.020, 0.20, anchor_x, deck_bottom - 0.010, 0.0)
    cylinder(mesh, 0.030, 0.050, 12, deck_bottom - 0.070, anchor_x, 0.0)
    line_r = geom["mooring_line_diameter_m"] / 2.0
    line_base = anchor_top + 0.030
    line_top = deck_bottom - 0.060
    cylinder(mesh, line_r, line_top - line_base, 10, line_base, anchor_x, 0.0)

    if scale != 1.0:
        mesh.tris = [
            tuple((px * scale, py * scale, pz * scale) for px, py, pz in tri) for tri in mesh.tris
        ]
    return mesh


def write_stl(mesh: Mesh, path: Path) -> None:
    with path.open("wb") as fh:
        fh.write(b"FALCON-01 catamaran first-pass assembly".ljust(80, b" "))
        fh.write(struct.pack("<I", len(mesh.tris)))
        for a, b, c in mesh.tris:
            ux, uy, uz = (b[i] - a[i] for i in range(3))
            vx, vy, vz = (c[i] - a[i] for i in range(3))
            nx, ny, nz = (uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx)
            norm = math.sqrt(nx * nx + ny * ny + nz * nz) or 1.0
            fh.write(struct.pack("<3f", nx / norm, ny / norm, nz / norm))
            fh.write(struct.pack("<9f", *a, *b, *c))
            fh.write(struct.pack("<H", 0))


# --------------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--params", type=Path, default=DEFAULT_PARAMS)
    ap.add_argument("--payload", type=float, default=0.0, help="extra payload mass in kg")
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    data = json.loads(args.params.read_text())
    geom = data["geometry"]
    rho = data["environment"]["water_density_kg_m3"]

    h = analyse(geom, data["mass_budget"], rho, extra_payload=args.payload)

    print("FALCON-01  OPTION B - CATAMARAN  (first pass, not validated)")
    print("-" * 58)
    print(f"Pontoon            : 2 x {geom['pontoon_diameter_m']*1000:.0f} x {geom['pontoon_length_m']*1000:.0f} mm")
    print(f"Beam (c/c)         : {geom['pontoon_beam_m']*1000:.0f} mm")
    print(f"Total mass         : {h.total_mass_kg:6.2f} kg")
    print(f"Displacement cap.  : {h.capacity_kg:6.2f} kg  (fully immersed)")
    print(f"Draft              : {h.draft_m*1000:6.1f} mm")
    print(f"Freeboard (hull)   : {h.freeboard_m*1000:6.1f} mm")
    print(f"Submerged          : {h.submerged_fraction*100:6.1f} %")
    print(f"Reserve buoyancy   : {h.reserve_buoyancy_fraction*100:6.1f} %")
    print(f"Waterplane area    : {h.waterplane_area_m2:6.3f} m2")
    print(f"BM                 : {h.bm_m:6.2f} m")
    print(f"KB / KG            : {h.kb_m:6.3f} / {h.kg_m:6.3f} m")
    print(f"GM (small angle)   : {h.gm_m:6.2f} m")
    print(f"Roll period (est.) : {h.roll_period_s:6.2f} s")
    print("-" * 58)
    print("First-pass estimate only. Requires measured masses, a loaded")
    print("flotation test, and a heel/righting test before fabrication.")

    out_dir = args.out or HERE / "out"
    out_dir.mkdir(parents=True, exist_ok=True)

    report = h.as_dict()
    report["payload_extra_kg"] = args.payload
    report["geometry"] = {
        key: geom[key]
        for key in (
            "pontoon_diameter_m",
            "pontoon_length_m",
            "pontoon_beam_m",
            "deck_length_m",
            "deck_width_m",
        )
    }
    (out_dir / "hydrostatics.json").write_text(json.dumps(report, indent=2) + "\n")

    mesh = build_assembly(geom, h)
    stl_path = out_dir / "falcon_catamaran.stl"
    write_stl(mesh, stl_path)

    print()
    print(f"Wrote {stl_path.relative_to(HERE.parent.parent)}  ({len(mesh.tris)} triangles, mm)")
    print(f"Wrote {(out_dir / 'hydrostatics.json').relative_to(HERE.parent.parent)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
