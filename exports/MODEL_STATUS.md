# FALCON-01 3D Export Status

## Redesign status

The physical/visual prototype is under redesign. No export is the approved replacement model. Mechanical Revision 5.0 and its `MAIN_FLOAT_TRADITIONAL_V2` body are retained only as historical references.

## Existing exports

The existing `FALCON-01.f3d`, FBX files, and dashboard GLB were exported on 2026-08-09 before the Revision 5 body decision. They remain archived for comparison but must not be presented as final Revision 5 geometry.

## Current dashboard working preview

`exports/PROJECT FALCON -V2.fbx`, updated on 2026-08-27, is converted to
`dashboard-next/public/models/PROJECT-FALCON-V2.glb` for the Buoy Motion page.
This is the current working prototype preview requested by the project team; it
is not yet a fabrication-approved or field-validated mechanical baseline.

The dashboard hides the anchor, ballast, and their chain/connector groups before
fitting the floating model. Its presentation waterline is calculated from the
main-float bounds at 35% of hull height above the rounded bottom. The pressure
sensor assembly is used for the Pressure Offline diagnostic highlight.

## Required new-revision package

After the proposed replacement passes `docs/PROTOTYPE_REDESIGN_BASELINE.md`, assign its new revision identifier and export:

- `exports/source/FALCON-01-<REV>.f3d` — editable Fusion source;
- `exports/FALCON-01-<REV>.step` — neutral manufacturing exchange;
- `exports/FALCON-01-<REV>.fbx` — presentation exchange if required;
- `dashboard-next/public/models/FALCON-01-<REV>.glb` — optimized dashboard model.

After scale, orientation, appearance, and source-revision verification, replace the dashboard model reference. Preserve older files as explicitly labeled legacy/reference assets.
