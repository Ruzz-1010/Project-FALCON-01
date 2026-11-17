# FALCON-01 — Catamaran (Option B) design workspace

First-pass parametric design aid for the twin-hull buoy. **Not a fabrication
drawing, not a stability book, not a validated design.**

Revision 2 (2026-11-08) enlarges the hull so it carries the final component
list in `THESIS DOCUMENTATION/FALCON Sensor Approval List for Panel.docx`:
6× 3 W panel (3S2P), 12.8 V LiFePO4, ESP32 + ADS1115 + INA260 + LTE,
and a **seabed anchor carrying the 4–20 mA SS316 pressure transmitter**.
Revision 3 hollows the enclosure and adds the internals: a **40 Ah / 512 Wh
battery bank** (4 packs), BMS, fuse, MPPT, tray, ESP32 / ADS1115 / INA260 /
LTE / SD logger, terminal block and desiccant, closed by a top cover.
Revision 4 (2026-11-09) moves to **12-inch hulls** (Ø324 × 2200 mm uPVC
pipe), stretches the deck to 1700 × 1320 mm and switches it to a **moulded
GRP sandwich**. Mass is now 122.6 kg.

## What is in here

| File | Purpose |
| --- | --- |
| `params.json` | All geometry and the estimated mass budget. Edit this first. |
| `falcon_catamaran.py` | Hydrostatics (draft, freeboard, reserve buoyancy, GM) + reference STL. Pure Python, no dependencies. |
| `build_step.py` | Real solids via `build123d` → STEP for Onshape/Fusion/FreeCAD. Needs a separate venv. |
| `ONSHAPE_BUILD.md` | Click-by-click build sheet if you model it by hand. |
| `out/hydrostatics.json` | Latest computed numbers. |
| `out/falcon_catamaran.stl` | Reference assembly mesh (mm). Not watertight per part, not printable. |
| `out/falcon_catamaran.step` | Editable solids once `build_step.py` has run. |
| `out/preview.html` | three.js viewer for the STL, reads the numbers from `hydrostatics.json`. |

## Run

```bash
python3 cad/catamaran/falcon_catamaran.py          # numbers + reference STL
python3 cad/catamaran/falcon_catamaran.py --payload 25   # extra payload

# optional: real STEP export
python3 -m venv /tmp/cadvenv
/tmp/cadvenv/bin/pip install "build123d==0.9.1" "ocpsvg==0.5.0"
/tmp/cadvenv/bin/python cad/catamaran/build_step.py

# view the reference mesh
cd cad/catamaran/out && python3 -m http.server 8799
# then open http://127.0.0.1:8799/preview.html
```

`build123d` 0.10 pulls `ocp_gordon`, which needs an `OCP.collections` module that
the pinned `cadquery-ocp` build does not ship. Keep the pins above.

## Baseline numbers (revision 4)

Mass budget is an **estimate** (122.6 kg). Replace it with measured components
before using any of these numbers for procurement.

| Quantity | Value |
| --- | --- |
| Pontoons | 2 × Ø324 × 2200 mm (12-inch uPVC), beam 950 mm c/c |
| Deck | 1700 × 1320 × 6 mm, moulded GRP sandwich, slotted |
| Solar | 6 × 150 mm cells, 3S2P, 474 × 312 mm envelope, −10° tilt |
| Enclosure | Ø420 × 360 mm round tube, 8 mm wall, hollow |
| Battery bank | 4 × 12.8 V 10 Ah LiFePO4 packs = **40 Ah / 512 Wh** |
| Displacement capacity | 353.6 kg fully immersed |
| Draft at 122.6 kg | 120.5 mm |
| Hull freeboard | 203.5 mm |
| Submerged | 37.2 % |
| Reserve buoyancy | 65.3 % |
| Waterplane area | 1.331 m² |
| BM / KB / KG | 2.60 / 0.070 / 0.283 m |
| GM (small angle) | **2.39 m** |
| Roll period (crude) | **0.62 s** |

## Load check against the final component list

| Item | Est. mass |
| --- | --- |
| 2 × 12-inch uPVC hull, 324 × 2200 mm, capped | 71.7 kg |
| Deck, moulded GRP sandwich, 6 mm, 1700 × 1320 | 12.0 kg |
| 2 cross beams + 4 saddles | 6.0 kg |
| Enclosure tube, top cover, bulkhead, hatch, glands, desiccant | 4.8 kg |
| 4 × 12.8 V 10 Ah LiFePO4 pack + BMS + fuse | 4.5 kg |
| 6 × panel (3S2P) + frame | 2.6 kg |
| Mast, wind sensor, GNSS, LTE, beacon | 2.8 kg |
| ESP32 + ADS1115 + INA260 + LTE + SD + tray + terminal blocks | 1.2 kg |
| MPPT + regulators | 0.5 kg |
| Fasteners, glands, cable, misc | 1.5 kg |
| Trim ballast in the hull bilge | 3.0 kg |
| **Buoy subtotal** | **≈ 110.6 kg** |
| Mooring vertical load (taut worst case) | 12.0 kg |
| **All-up** | **122.6 kg** |

122.6 kg against 353.6 kg capacity, so the platform floats at 37 % of its
displacement. The 12-inch pipe is heavy (16.3 kg/m), but it buys a lot of
volume: capacity grew 1.9× while mass only grew 2.1×.

Draft at higher all-up masses:

| All-up mass | Draft | Freeboard | Reserve |
| --- | --- | --- | --- |
| 123 kg | 120 mm | 204 mm | 65 % |
| 140 kg | 133 mm | 191 mm | 60 % |
| 160 kg | 147 mm | 177 mm | 55 % |
| 200 kg | 176 mm | 148 mm | 43 % |
| 250 kg | 213 mm | 111 mm | 29 % |
| 300 kg | 254 mm | 70 mm | 15 % |

## What is inside the enclosure

Revision 3 hollows the tube (8 mm wall, Ø404 internal) and models the whole
electrical fit-out in the STEP, so Onshape shows the real stack:

| Part | Size | Position |
| --- | --- | --- |
| Bulkhead | Ø408 × 10 mm | tube floor, `Y = 345` |
| Top cover | Ø420 × 5 mm | closes the tube at `Y = 705` |
| Battery pack ×4 | 150 × 65 × 100 mm | `X = ±85`, `Z = ±60`, on the bulkhead |
| BMS | 120 × 20 × 40 mm | above the packs, `Z = −120` |
| Main fuse block | 60 × 30 × 40 mm | `X = +150` |
| MPPT charge controller | 110 × 30 × 70 mm | above the packs, `Z = +120` |
| Electronics tray | Ø280 × 6 mm | `Y = 470` |
| ESP32 board | 70 × 12 × 55 mm | on the tray |
| ADS1115 / INA260 | 30 × 8 × 22 / 25 × 8 × 18 mm | on the tray |
| LTE modem + SD logger | 90 × 12 × 60 / 45 × 8 × 35 mm | on the tray |
| Terminal block | 60 × 25 × 30 mm | on the tray |
| Desiccant box | 70 mm cube | next to the tray |
| Cable glands ×2 | Ø24 × 34 mm | through the top hatch |

Every internal part stays inside the Ø404 cavity (worst corner radius 198 mm
against 202 mm available). Hide `ROUND_ELECTRONICS_TUBE` in Onshape to see the
fit-out; it is opaque by design.

Battery margin: 512 Wh against a load of roughly 0.4–0.6 W average (sensor
sampling + LTE burst) gives several weeks of autonomy without sun; the 18 W
panel array normally covers it in a few hours. Check the real duty cycle before
trusting that.

## Two things the numbers say

1. **The platform is still stiff, but better.** GM of 2.39 m on a 122.6 kg
   buoy gives a roll period of 0.62 s — still quick, but a real roll instead of
   a snap. The 12-inch hulls and the heavier deck did most of the work.
2. **204 mm of freeboard on a 324 mm float is a lot of windage.** Wind load
   will push this platform more than the mooring drawing suggests. The GRP deck
   is also 12 kg of the mass, high up.

Both are first-pass results. The roll-period figure is crude — it ignores added
mass of entrained water and assumes a uniform mass radius of gyration. Treat it
as a direction, not a value.

## The anchor and the pressure sensor

`FALCON Sensor Approval List for Panel.docx` states that the pressure
transmitter is fixed to the seabed or an independent mooring reference and is
**not** suspended at a constant distance below the heaving buoy. Revision 2
therefore removed the deck-mounted stilling tube and puts the transmitter on a
riser on the anchor block, 2000 mm below the waterline (schematic depth, set to
the real site depth before mooring design).

Only the mooring line tension reaches the buoy. That is budgeted as 12 kg in
`params.json`; confirm it against the actual chain and anchor before cutting
material.

## Known limitations

- Masses are estimates, not measurements.
- The hydrostatic model assumes an intact, sealed capsule with no heel.
- No torsional check on the cross-beam joints — the real weak point of a
  catamaran, and the one that decides whether the deck survives a mooring
  shock load.
- No wave-response or added-mass model.
- The STL is a visual assembly, not a printable single body.
- Anchor depth and mooring scope are placeholders.

## Before fabrication release

1. Measured mass of every component.
2. Confirm the panel split and the actual solar array footprint.
3. Loaded flotation test in a tank, then in seawater.
4. Heel/righting test with secured ballast.
5. Torsion test on the frame with the mooring load applied at the bridle.
6. Leak test on every sealed joint.
