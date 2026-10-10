# FALCON-01 3D Export Status


<!-- FALCON-DOST-REVISION-NOTE:START -->
> **Current revision note (2026-10-10):** Use the DOST major revision baseline in [`docs/REVISION_2026-10-10.md`](../docs/REVISION_2026-10-10.md) unless this file is explicitly archived. The active proposal core is a compact ESP32-based buoy with **water pressure sensing, wind speed/direction sensing, GPS for exact position and security, battery + solar power, and Wi-Fi/LTE internet communication**. LoRa, large Bay Station hardware, tall tower layouts, and continuous every-second uploads are legacy or optional fallback assumptions.
<!-- FALCON-DOST-REVISION-NOTE:END -->

## Redesign status

The physical/visual prototype is under redesign. No export is the approved replacement model. Mechanical Revision 5.0 and its `MAIN_FLOAT_TRADITIONAL_V2` body are retained only as historical references.

## Existing exports

Older FBX/GLB exports now live in `archive/exports/` at the repository root. Their contents are unchanged. The duplicate root-level tilt FBX was moved to Trash; the retained tilt model is `archive/exports/FALCON-01-tilt.fbx`. Editable Fusion sources and the current V2 working exports remain in this directory.

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
