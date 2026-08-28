# Documentation Cleanup Audit — Prototype Redesign Baseline

Date: 26 August 2026  
Authority: `PROJECT_CONTEXT.md` v6.1

## Result

The repository Markdown set was audited before replacement of the physical/visual prototype. A local-link scan covered 119 Markdown files and found zero missing local links.

The cleanup does not delete earlier engineering work. Instead, documents now follow this authority order:

1. `PROJECT_CONTEXT.md` — approved system function and truthful claims.
2. `PROTOTYPE_REDESIGN_BASELINE.md` — physical/visual redesign status and acceptance gates.
3. Current engineering specifications in `docs/` — software, sensors, API, power, security, wiring requirements, tests, and operation.
4. Historical/reference records — old Fusion components, exports, KiCad carrier, Wokwi, renders, video prompts, changelogs, and previous mechanical revisions.

## Corrections applied

- Reset the current physical/visual prototype status to `UNDER REDESIGN`.
- Removed old “current/approved production prototype” authority from Revision 5 CAD and export notes.
- Preserved system requirements that do not depend on external shape or component placement.
- Kept BNO085, salinity, anchor-load sensing, AI-first operation, and cloud dependency outside the required Phase 1 baseline.
- Aligned dashboard documentation to Overview, Sensors, Buoy Motion, GPS, and Logs & Alerts.
- Documented Current Data, Calm, Moderate, Rough, and Pressure Offline motion scenarios as non-telemetry presentation presets.
- Corrected Linux Mint run instructions and the current thesis DOCX filename.
- Marked old deployment-video prompts and visual assets as references awaiting replacement.
- Marked the old carrier PCB and enclosure/component layout as non-fabrication historical drafts.
- Replaced outdated ESP32-only operator instructions with the current ESP32-to-Orange-Pi workflow.

## Items intentionally preserved

Historical part names, dimensions, IMU wiring, old simulator behavior, and prior design decisions may still appear inside explicitly archived records. They preserve traceability and are not requirements for the replacement prototype.

## Next documentation update

When the replacement design is selected, update its revision, dimensions, calculations, verified placements, figures, BOM effects, assembly steps, dashboard GLB, and presentation assets as one controlled change. Do not remove the redesign hold until the acceptance checklist is complete.
