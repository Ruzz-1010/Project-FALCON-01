# Project FALCON Documentation Index v9.0


<!-- FALCON-DOST-REVISION-NOTE:START -->
> **Current revision note (2026-10-10):** Use the DOST major revision baseline in [`docs/REVISION_2026-10-10.md`](REVISION_2026-10-10.md) unless this file is explicitly archived. The active design is a compact single-tube / small-buoy, ESP32-based, event-driven, cloud-first system. LoRa, large Bay Station hardware, tall tower layouts, and continuous every-second uploads are legacy or optional fallback assumptions.
<!-- FALCON-DOST-REVISION-NOTE:END -->

Start with [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md), the current source of truth, then [REVISION_2026-10-10.md](REVISION_2026-10-10.md), [REVISION_2026-10-09.md](REVISION_2026-10-09.md), and [CURRENT_PROJECT_DOCUMENTATION.md](CURRENT_PROJECT_DOCUMENTATION.md). For the new compact can-buoy body and component placement, use [PROTOTYPE_REDESIGN_BASELINE.md](PROTOTYPE_REDESIGN_BASELINE.md).

## Current adviser-approved specifications

- [HARDWARE.md](HARDWARE.md), [HARDWARE_BOM.md](HARDWARE_BOM.md), [PINOUT.md](PINOUT.md), [ELECTRONICS_WIRING.md](ELECTRONICS_WIRING.md)
- [SENSOR_SPEC.md](SENSOR_SPEC.md), [SECURITY.md](SECURITY.md), [POWER_SYSTEM.md](POWER_SYSTEM.md)
- [SOFTWARE.md](SOFTWARE.md), [API.md](API.md), [DASHBOARD.md](DASHBOARD.md), [AI.md](AI.md)
- [TEST_PLAN.md](TEST_PLAN.md), [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md), [FUTURE_UPGRADES.md](FUTURE_UPGRADES.md)
- [ADVISER_REVISION_AUDIT.md](ADVISER_REVISION_AUDIT.md) explains current, legacy, and pending records.
- [DOCUMENTATION_CLEANUP_AUDIT.md](DOCUMENTATION_CLEANUP_AUDIT.md) records the pre-redesign Markdown cleanup and document authority order.
- [IMPLEMENTATION_REPORT_V6.md](IMPLEMENTATION_REPORT_V6.md) records delivered code, verification, commands, and remaining work.
- [Adviser architecture diagram](diagrams/FALCON-01-adviser-architecture.svg) is a historical visual until it is redrawn for the event-driven Wi-Fi/LTE cloud flow.

The current equipment and alternatives file is `THESIS DOCUMENTATION/FALCON Revised Event Driven BOM and Sensor Options.docx`. `THESIS DOCUMENTATION/BayStation.docx` and the V3 filename remain earlier thesis records until regenerated against v9.0.

## Design records on hold

All `fusion360/` component notes, `exports/MODEL_STATUS.md`, existing prototype renders, dashboard 3D models, video prompts, and prototype-specific mechanical dimensions are retained for traceability only. They are not the approved replacement design. Older Wokwi, PCB, motion, IMU, and wiring visuals likewise remain historical until explicitly revised against v6.1 and the selected physical parts.

- [Proposed blueprint package](blueprints/README.md) documents reference geometry and component layout. Every sheet is marked **REFERENCE / NOT FOR FABRICATION** until the compact can-buoy redesign acceptance gates are completed.
