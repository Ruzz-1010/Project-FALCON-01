# Changelog

## 2026-08-13 - Upper all-electronics service pod

- Added a separate 320 mm OD x 400 mm UV-HDPE upper pod for the battery,
  computing, communications, power management, and sensor-control electronics.
- Added a removable double-gasket lid, ventilated sun/rain shield, leak tray,
  battery restraint, thermal spreader, control rack, downward connector panel,
  and hydrophobic membrane-vent boss.
- Specified sealed internal air recirculation instead of salt-air fan intake.
- Kept final acceptance dependent on thermal, ingress, salt-fog, vibration,
  flotation, freeboard, and righting-moment validation.

## 2026-08-13 - Two-side solar frame V3

- Replaced the circular dual-solar cage with two open flat frames only: East
  and West, matching the two opposed 30 W panels.
- Removed North/South frame geometry and circular rings from the active view.
- Used 20 x 2 mm round aluminum tubing and a minimal top sensor crossbar to
  reduce exposed wind area.

## 2026-08-13 - Dual-solar compact frame V2

- Added the missing visible frame for the dual 30 W configuration.
- Reduced tower outside diameter to 360 mm and used four 20 mm posts.
- Added East/West solar ties and a compact top sensor cross.
- Hid the former 560 mm and 460 mm frames without deleting them.

## 2026-08-13 - Dual 30 W solar replacement

- Replaced the active four-panel solar arrangement with two opposed 30 W
  panels for 60 W nominal total output.
- Positioned the new panels on the East and West sides at Z1170 mm with a
  20-degree outward tilt and compact triangulated brackets.
- Hid rather than deleted the former four-panel array and its brackets.

## 2026-08-13 - Compact elevated upper tower correction

- Corrected the earlier panel-only elevation upgrade by raising the top sensor
  array and navigation light to the same +150 mm level.
- Replaced the active visible 560 mm frame with a 460 mm OD frame using four
  20 mm posts and slim rings to reduce wind area.
- Preserved the old frame and temporary supports as hidden, recoverable legacy
  geometry rather than deleting them.

## 2026-08-13 - Elevated solar-panel support upgrade

- Added a Fusion 360 upgrade that raises all four existing solar panels by 150 mm.
- Added eight 12 mm 6061-T6 extension struts from the upper-frame rail.
- Preserved the buoy body, electronics, ballast, and sensor positions.

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
