# Coding Assistant Manual


<!-- FALCON-DOST-REVISION-NOTE:START -->
> **Current revision note (2026-10-10):** Use the DOST major revision baseline in [`docs/REVISION_2026-10-10.md`](REVISION_2026-10-10.md) unless this file is explicitly archived. The active design is a compact single-tube / small-buoy, ESP32-based, event-driven, cloud-first system. LoRa, large Bay Station hardware, tall tower layouts, and continuous every-second uploads are legacy or optional fallback assumptions.
<!-- FALCON-DOST-REVISION-NOTE:END -->

## Purpose
Permanent engineering instructions for AI coding assistants.

## Scope
Analysis, firmware, dashboard, documentation, hardware planning, tests, and Git.

## Current Status
Active for the Phase 1 prototype. Read `INDEX.md` and this file first.

## Architecture
Keep lifecycle in `main.cpp`, portal/API ownership in `portal_server.*`, constants in `include/`, the minimal LittleFS setup portal in `data/`, the canonical full dashboard in `dashboard-next/`, its bundled edge build in `edge/static/dashboard/`, tests in `test/`, and long-form documents in `docs/`.

## Implementation
Source priority: working code, `PROJECT_CONTEXT.md`, `HARDWARE.md`, `API.md`, `ROADMAP.md`, then remaining docs.

- Preserve AP, captive portal, offline operation, existing routes, and JSON fields.
- Use PlatformIO ESP32 Arduino and avoid unnecessary libraries.
- Do not fabricate sensors, GPIOs, credentials, endpoints, hardware, or AI.
- Mark unresolved details **Status: Not Yet Finalized**.
- Simulated values must remain explicit.
- Planned documentation examples do not count as implementation.
- Update affected specs, tests, changelog, and README after material changes.
- Run `git diff --check`, firmware build, LittleFS build, and link checks as applicable.
- Commit and push completed project changes unless the user explicitly opts out.

Naming: types `PascalCase`, members/methods `camelCase`, constants `kPascalCase`, private members with trailing underscore, JSON fields `camelCase`.

Status definitions: Implemented means source plus verification; In Progress means incomplete acceptance; Planned means approved but absent; Future Expansion means optional/long term.

## Future Expansion
Add repeatable rules when new toolchains or approved subsystems are introduced.

## Engineering Notes
Reliability, bounded resources, backward compatibility, evidence, and field safety take priority over novelty.

## Revision History
| Version | Date | Change |
| --- | --- | --- |
| 1.0 | 2026-08-05 | Initial assistant manual. |
