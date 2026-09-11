# Adviser Revision Documentation Audit

Date: 2026-09-08. Authority: `PROJECT_CONTEXT.md` v8.1.

## Current primary documents

- `README.md`
- `PROJECT_CONTEXT.md`
- `CURRENT_PROJECT_DOCUMENTATION.md`
- `HARDWARE.md`, `HARDWARE_BOM.md`, `PINOUT.md`, `ELECTRONICS_WIRING.md`
- `SENSOR_SPEC.md`, `SECURITY.md`, `SOFTWARE.md`, `API.md`, `DASHBOARD.md`, `AI.md`
- `THESIS DOCUMENTATION/PROJECT FALCON-01 - V3 Documentation.docx`
- `PROTOTYPE_REDESIGN_BASELINE.md` controls the physical/visual replacement; `BAY_STATION_ARCHITECTURE.md` controls LoRa-primary and Bay Station Internet-backhaul behavior.

## Historical/engineering records requiring a later physical-design revision

The following files preserve earlier BNO085/PCB/Wokwi work for traceability and are not the adviser-approved final wiring baseline: `WOKWI.md`, `CLEAR_WIRING_MAP.md`, `ELECTRONICS_LAYOUT.md`, `PCB_VALIDATION_REGISTER.md`, existing electronics-wiring SVG/PNG files, KiCad carrier files, and BNO085 chip definitions. They must not be used for final fabrication until revised against exact purchased parts and v6.1 pinout.

All Fusion 360 component READMEs, exported models, prototype images, dashboard 3D geometry, and video prompts describe earlier visual/mechanical revisions. They are under redesign hold and must not be used as the replacement prototype without review.

`CHANGELOG.md` and `VERSION_HISTORY.md` intentionally retain old terminology as historical records. Mechanical references to structural tension cables describe legacy CAD and are not anchor-chain load sensing.

## Legacy software retained for compatibility

The current dashboard retains `MotionPage.tsx` and `MotionScene.tsx` for its Buoy Motion page, plus forecast persistence and `/ai` compatibility. The unused standalone `WavePage.tsx` was removed from the archive during follow-up cleanup; it remains recoverable from Git commit `7fb489a`. Removing that disconnected page does not remove the active Overview prediction or change stored-data/API compatibility.

## Remaining release gates

Exact LoRa radio, barangay-hall gateway, Bay Station SIM/4G/5G backhaul, tamper, enclosure switch, GPS, wind, and health-monitor models remain TBD. Water temperature and conductivity/salinity are excluded from the required Phase 1 scope. Final schematics, PCB, diagrams, and BOM total must wait for datasheet/footprint/current/rating verification. Physical pressure calibration and security persistence validation are not complete.
