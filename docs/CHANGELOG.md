# Changelog

## Purpose
Record material repository changes.

## Scope
Firmware, dashboard, documentation, APIs, hardware specifications, and tooling.

## Current Status
Reconstructed from Git history and repository evidence.

## Architecture
This is a change record; source and dedicated specifications remain authoritative.

## Implementation
### 2026-08-13 - Mechanical Revision 5 direction
- Adopted `MAIN_FLOAT_TRADITIONAL_V2` as the current CAD body direction.
- Replaced the production four-stabilizer arrangement with a compact Ø650 mm single body and 240 mm rounded tapered keel.
- Retained stabilizer scripts and components as Legacy Revision 4 for traceability and rollback.
- Required ballast relocation and renewed flotation/stability validation.
- Marked existing August 9 F3D/FBX/GLB exports as pre-Revision-5 until a new verified assembly export is supplied.

### 2026-08-05 - Documentation baseline
- Moved four engineering documents into `docs/`.
- Added index, assistant rules, specifications, test/operations guides, changelog, and version register.
- Added verified status notices separating source-backed implementation from plans.

### 2026-08-04 - Dashboard 2.1
- Modernized responsive UI, offline state, demo labels, and falcon logo.

### 2026-08-04 - Portal baseline
- Added modular portal, AP/DNS/HTTP, LittleFS validation, and three API routes.

## Future Expansion
Use tagged releases and linked test evidence after stable versioning exists.

## Engineering Notes
Changelog statements are not proof of physical hardware validation.

## Revision History
| Version | Date | Change |
| --- | --- | --- |
| 1.0 | 2026-08-05 | Initial changelog. |
