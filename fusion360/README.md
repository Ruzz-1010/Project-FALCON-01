# Project FALCON V2 — Final Fusion Script Set

This directory has been cleaned against the top-level component structure in
`exports/PROJECT FALCON -V2.fbx` dated 2026-08-27. Superseded prototype,
stabilizer, electronics-box, ventilation, solar-frame, and structural-cage
generators were removed on 2026-08-30. Their history remains recoverable in Git.

## Finalized FBX component generators

- `TOP_CAP`
- `BALLAST_SUSPENSION_CHAIN`
- `BALLAST`
- `MAIN_FLOAT_EDGE_FAIRING`
- `TOP_SENSOR_ARRAY`
- `NAVIGATION_LIGHT`
- `ANCHOR_MOORING_SYSTEM`
- `MAIN_FLOAT_TRADITIONAL_V2`
- `DUAL_30W_SOLAR_REPLACEMENT` — creates `DUAL_30W_SOLAR_ARRAY`
- `SEALED_POD_THERMAL_SYSTEM`
- `UPPER_POD_ELECTRONICS_LAYOUT`
- `POD_MARINE_PROTECTION_HARDWARE`
- `ADJUSTABLE_LOW_BALLAST_V2`
- `BALLAST_V2_ANCHOR_CONNECTOR`
- `REV5_MAIN_BUOY_FRAME_SUPPORT`
- `REV5_TAPERED_MARINE_MAST`
- `REV5_RECTANGULAR_MARINE_ELECTRONICS_POD`
- `REV5_LOWER_TO_MAIN_FRAME_SUPPORT_CAGE_V2`
- `REV5_TOWER_FRONT_MAINTENANCE_GATE`
- `WATER_PRESSURE_SENSOR_ASSEMBLY`

`MAIN_FLOAT` is retained only as the foundational dependency used when creating
`MAIN_FLOAT_TRADITIONAL_V2`. `REV5_FINAL_ASSEMBLY_CLEANUP` is retained as the
visibility and completeness checker for the finalized export set.

## Safety rules

- Never delete, move, hide, or edit unrelated existing components.
- Capture Position and save before running a generator.
- Each generator must stop if its target already exists unless it implements an
  explicitly documented repair of that same component.
- Validate waterline, ballast clearance, pressure-sensor submersion, enclosure
  sealing, and physical dimensions before fabrication or deployment.
- Preserve the finalized `.f3d`, `.fbx`, dashboard `.glb`, and Git history.
