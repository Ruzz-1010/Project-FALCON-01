# Project FALCON Blueprint Package

Status: **PROPOSED REPLACEMENT PROTOTYPE — REFERENCE / NOT FOR FABRICATION**  
Source model: `exports/PROJECT FALCON -V2.f3d` and dashboard conversion `dashboard-next/public/models/PROJECT-FALCON-V2.glb`  
Drawing basis date: 2026-08-30

## Current drawing

1. [`FALCON-BP-001-cad-orthographic.svg`](FALCON-BP-001-cad-orthographic.svg) — professional CAD-derived front elevation, right elevation, plan view, controlled dimension register, engineering notes, and title block.
2. [`FALCON-BP-002-electronics-pod.svg`](FALCON-BP-002-electronics-pod.svg) — true enclosure fabrication-control sheet with orthographic views, section, door/opening, lid/hood, gasket, hinge/latch, deck, gland-plate, and part dimensions.
3. [`FALCON-BP-003-metal-drum-dimensions.svg`](FALCON-BP-003-metal-drum-dimensions.svg) — separate engineering dimensional-control sheet for a proposed metal drum/float adaptation, including body geometry, clamp/service interfaces, required calculations, fabrication notes, and approval fields.
4. [`FALCON-BP-004-tower-structural-dimensions.svg`](FALCON-BP-004-tower-structural-dimensions.svg) — tower, main support, lower cage, maintenance gate, and controlled structural-member dimension schedule.
5. [`FALCON-BP-005-external-hardware-dimensions.svg`](FALCON-BP-005-external-hardware-dimensions.svg) — solar, top sensors, pressure guard, ballast, chain/connector, and concrete-anchor dimension register.
6. [`FALCON-BP-006-electronics-equipment-layout.svg`](FALCON-BP-006-electronics-equipment-layout.svg) — separate three-deck internal equipment packaging layout; this is not the enclosure fabrication drawing.

The earlier concept-style infographic sheets were withdrawn. The current sheet
uses projected feature linework extracted directly from the V2 GLB geometry.
Regenerate it with:

```bash
python3 tools/generate_falcon_blueprint.py
```

Open either SVG directly in VS Code and select **Open Preview**, or open it in Firefox.

## Dimension authority

Dimensions marked **CAD REF** were recovered from the existing Fusion generator parameters. They describe the V2 reference geometry only. Dimensions marked **TBD** require physical component measurement, engineering calculation, controlled testing, and adviser approval before fabrication.

| Item | V2 CAD reference |
| --- | --- |
| Main float | Ø650 mm × 620 mm overall; 380 mm cylindrical upper body; 240 mm tapered keel; 6 mm HDPE wall |
| Mast | 800 mm structural height; 420 mm base; 380 mm shoulder; 260 mm top; Ø32 mm legs; Ø20 mm braces |
| Electronics pod | 300 × 280 × 400 mm; 8 mm UV-HDPE wall; 18 mm lid |
| Solar array | 2 × 30 W; each panel 450 × 300 × 20 mm; 20° outward tilt |
| Pressure sensor | Ø24 × 42 mm envelope; Ø64 × 72 mm guard; 125 mm radial offset |
| Adjustable ballast reference | Ø40 × 500 mm rail; 4 × Ø220 × 25 mm plates |
| Mooring anchor reference | 650 mm bottom / 450 mm top × 500 mm high; nominal 367 kg |

## Architecture correction

The old Fusion electronics layout contains an `ORANGE_PI_MINI_PC_ENVELOPE`. It is explicitly excluded from these drawings. The Orange Pi is located at the shore-based Bay Station and communicates with the buoy through LTE/cellular infrastructure. USB/UART is for bench servicing only.

## Release gates

Before changing these sheets to **FOR PROTOTYPE FABRICATION**, record and approve:

- actual part manufacturer/model and measured envelope;
- loaded mass, displacement, waterline, freeboard, center of gravity, and stability;
- structural loads, fasteners, corrosion isolation, and mooring rating;
- cable-gland count and positions, bend radius, drainage, and service clearance;
- battery and solar sizing based on measured consumption;
- CAD interference check and controlled leak/flotation tests;
- adviser/team design approval and a new mechanical revision identifier.
