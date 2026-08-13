# FALCON-01 3D Export Status

## Current mechanical baseline

Mechanical Revision 5.0 uses `MAIN_FLOAT_TRADITIONAL_V2`: a traditional Ø650 mm HDPE upper body with a 240 mm rounded tapered underwater keel. The four stabilizer buoys, arms, cradles, and radial cables are Legacy Revision 4.

## Existing exports

The existing `FALCON-01.f3d`, FBX files, and dashboard GLB were exported on 2026-08-09 before the Revision 5 body decision. They remain archived for comparison but must not be presented as final Revision 5 geometry.

## Required replacement package

When the verified Fusion assembly is ready, export and upload:

- `exports/source/FALCON-01-R5.f3d` — editable Fusion source;
- `exports/FALCON-01-R5.step` — neutral manufacturing exchange;
- `exports/FALCON-01-R5.fbx` — presentation exchange if required;
- `data/models/FALCON-01-R5.glb` — optimized dashboard model.

After visual and scale verification, replace the dashboard model reference with `FALCON-01-R5.glb`. Preserve older files as explicitly labelled legacy assets.
