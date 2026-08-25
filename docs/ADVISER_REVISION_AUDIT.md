# Adviser Revision Documentation Audit

Date: 2026-08-25. Authority: `PROJECT_CONTEXT.md` v6.0.

## Current primary documents

- `README.md`
- `PROJECT_CONTEXT.md`
- `CURRENT_PROJECT_DOCUMENTATION.md`
- `HARDWARE.md`, `HARDWARE_BOM.md`, `PINOUT.md`, `ELECTRONICS_WIRING.md`
- `SENSOR_SPEC.md`, `SECURITY.md`, `SOFTWARE.md`, `API.md`, `DASHBOARD.md`, `AI.md`
- `PROJECT FALCON-01 - V3 ADVISER REVISED.docx`

## Historical/engineering records requiring a later physical-design revision

The following files preserve earlier BNO085/PCB/Wokwi work for traceability and are not the adviser-approved final wiring baseline: `WOKWI.md`, `CLEAR_WIRING_MAP.md`, `ELECTRONICS_LAYOUT.md`, `PCB_VALIDATION_REGISTER.md`, existing electronics-wiring SVG/PNG files, KiCad carrier files, and BNO085 chip definitions. They must not be used for final fabrication until revised against exact purchased parts and v6.0 pinout.

`CHANGELOG.md` and `VERSION_HISTORY.md` intentionally retain old terminology as historical records. Mechanical references to structural tension cables describe legacy CAD and are not anchor-chain load sensing.

## Legacy software retained for compatibility

`MotionPage.tsx`, `MotionScene.tsx`, `WavePage.tsx`, forecast persistence, and `/ai` remain in source as deprecated/optional or backward-compatible modules. They are not primary dashboard navigation and do not define required Phase 1 sensors. Removing them immediately would discard user-authored work and could break stored-data/API compatibility.

## Remaining release gates

Exact conductivity, tamper, enclosure switch, GPS, wind, and health-monitor models remain TBD. Final schematics, PCB, diagrams, and BOM total must wait for datasheet/footprint/current/rating verification. Physical pressure calibration and security persistence validation are not complete.
