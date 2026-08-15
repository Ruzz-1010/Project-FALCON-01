# PROJECT FALCON Documentation Index

## Authority

[`PROJECT_CONTEXT.md`](PROJECT_CONTEXT.md) is the single source of truth for approved project scope, architecture, terminology, and implementation priorities. If another document conflicts with it, the project context takes precedence.

Current authoritative mechanical revision: **5.0**, using the traditional single-body rounded-keel buoy. Existing August 9 dashboard/CAD exports remain Legacy Revision 4 until replaced by a verified Revision 5 export.

## Core v5.0 Documentation

Read these documents in order:

1. [`PROJECT_CONTEXT.md`](PROJECT_CONTEXT.md) — master engineering context and scope
2. [`README.md`](../README.md) — repository entry point and quick start
3. [`ROADMAP.md`](ROADMAP.md) — gated delivery plan
4. [`HARDWARE.md`](HARDWARE.md) — Phase 1 electronics and sensor baseline
5. [`SOFTWARE.md`](SOFTWARE.md) — ESP32 and Orange Pi software responsibilities
6. [`ORANGE_PI_EDGE.md`](ORANGE_PI_EDGE.md) — selected Orange Pi Zero 3 architecture and responsibility boundary
7. [`AI.md`](AI.md) — 5- and 15-minute wave-height prediction contract
8. [`DASHBOARD.md`](DASHBOARD.md) — local dashboard information architecture
9. [`API.md`](API.md) — approved local REST API contract
10. [`MECHANICAL.md`](MECHANICAL.md) — approved buoy mechanical baseline

These core documents were aligned to Project FALCON v5.0 and the single-body mechanical baseline on 2026-08-13.

## Supporting Documentation

- [`SYSTEM_ARCHITECTURE.md`](SYSTEM_ARCHITECTURE.md)
- [`FIRMWARE_SPEC.md`](FIRMWARE_SPEC.md)
- [`PINOUT.md`](PINOUT.md)
- [`SENSOR_SPEC.md`](SENSOR_SPEC.md)
- [`POWER_SYSTEM.md`](POWER_SYSTEM.md)
- [`POWER_CALCULATIONS.md`](POWER_CALCULATIONS.md)
- [`HARDWARE_BOM.md`](HARDWARE_BOM.md)
- [`ELECTRONICS_WIRING.md`](ELECTRONICS_WIRING.md)
- [`ELECTRONICS_LAYOUT.md`](ELECTRONICS_LAYOUT.md)
- [`WOKWI.md`](WOKWI.md)
- [`NETWORK_PROTOCOL.md`](NETWORK_PROTOCOL.md)
- [`SECURITY.md`](SECURITY.md)
- [`TEST_PLAN.md`](TEST_PLAN.md)
- [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md)
- [`USER_MANUAL.md`](USER_MANUAL.md)
- [`ASSEMBLY_GUIDE.md`](ASSEMBLY_GUIDE.md)
- [`DEPLOYMENT_GUIDE.md`](DEPLOYMENT_GUIDE.md)
- [`CALIBRATION_GUIDE.md`](CALIBRATION_GUIDE.md)
- [`CHANGELOG.md`](CHANGELOG.md)
- [`VERSION_HISTORY.md`](VERSION_HISTORY.md)

Supporting documents describe implementation details and historical work. They must not expand Phase 1 scope or override the core v5.0 documents. Future updates should migrate them to the same terminology as the master context.

Future assistants must also read [`CODEX.md`](CODEX.md) before changing the project.

## Phase 1 Boundary

Project FALCON v5.0 is limited to real-time coastal monitoring and AI-assisted wave-height prediction at 5- and 15-minute horizons. The AI classifies sea state as Calm, Moderate, or Rough. Cloud services, camera vision, water-quality analytics, and autonomous control remain future expansion.

## Revision History

| Version | Date | Change |
| --- | --- | --- |
| 1.0 | 2026-08-05 | Initial documentation index. |
| 4.0 | 2026-08-09 | Reordered documentation around the v4.0 source of truth and added all core subsystem documents. |
