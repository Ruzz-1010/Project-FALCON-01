# Changelog

## 2026-08-23 - Post-approval upgrade roadmap documented

- Kept Orange Pi Zero 3 (4GB) as the Phase 1 edge baseline.
- Added gated future paths for an on-demand non-recording camera, calibrated
  environmental sensors, resilient communications, and Raspberry Pi 5 4GB.
- Added power, thermal, calibration, privacy, security, maintenance, and
  sustainability conditions across the core engineering documents.
- Added a concise thesis/presentation version of the upgrade plan.

## 2026-08-15 - Dashboard Next promoted to canonical production UI

- Made `dashboard-next/` the only full dashboard source.
- Configured Vite to bundle the production UI into `edge/static/dashboard/`.
- Updated the edge service to serve hashed assets, the 3D model, and SPA routes.
- Reduced ESP32 LittleFS content to a small sensor-node setup/diagnostics portal.
- Removed obsolete duplicated legacy dashboard libraries and assets from `data/`.
- Updated setup, architecture, firmware, and current-state documentation.

## 2026-08-13 - V2 digital-twin waterline correction

- Replaced the overall-assembly percentage waterline with a datum calculated
  from the `MAIN_FLOAT_TRADITIONAL_V2` bounds only.
- Raised the visible V2 buoy so the sea crosses the lower rounded hull instead
  of submerging the upper float and support frame.

## 2026-08-13 - Dashboard digital twin updated to FALCON V2

- Replaced the dashboard GLB asset with the Fusion-exported FALCON V2 assembly.
- Bumped the browser model cache key to `v=3` in both dashboard viewers.

## 2026-08-13 - Lower cage overhang correction

- Tapered the four lower support tubes inward from radius 365 mm to the existing
  frame-support attachment radius of 336 mm.
- Lowered the tube termination to Z=385 mm inside the main support clamp band,
  removing the visible radial and vertical overhang.

## 2026-08-13 - Lower-to-main-frame cage scope correction

- Limited the four external tubes to the lower buoy collar and
  `REV5_MAIN_BUOY_FRAME_SUPPORT`; they now stop at Z=480 mm.
- Removed any active cage connection to the upper mast, solar frame or antennas.
- Kept all earlier cage attempts hidden and recoverable.

## 2026-08-13 - Full-height cage top-connection correction

- Moved the four external cage origins from the mast feet to the top mast
  corners, then continued them through the upper ring to the lower collar.
- Retained the incorrect V1 cage as a hidden fallback instead of deleting it.

## 2026-08-13 - Full-height external buoy support cage

- Corrected the upper/lower load path to use four continuous external tubes
  from the mast feet down to the lower fairing elevation.
- Added a separate 760/696 mm EPDM-lined lower metal collar so the selected HDPE
  fairing is not incorrectly treated as a structural attachment.
- Retained the earlier short load cage as a hidden fallback.

## 2026-08-13 - Rectangular marine electronics pod

- Added a 300 x 280 x 400 mm chamfered UV-HDPE top-service cabinet with dual
  EPDM seals, weather hood, internal decks and sealed thermal interface.
- Retained the previous round pod as a hidden fallback instead of deleting it.

## 2026-08-13 - Upper-to-lower structural load cage

- Added four 32 mm primary struts from the tapered mast feet to the lower metal
  split-clamp frame, plus eight 20 mm anti-racking knee braces.
- Added isolated mounting pads and kept the HDPE shell free of new penetrations.

## 2026-08-13 - Tapered braced marine mast

- Replaced the tall open-post concept with a reference-inspired tapered mast.
- Added four two-stage 32 mm primary legs with a 420 mm deck footprint, 380 mm
  pod-clearance shoulder, 260 mm top, five rail levels, full-face X-bracing,
  two opposed solar cradles, and a compact top sensor platform.
- Marked the earlier fresh rectangular frame as superseded in final cleanup.

## 2026-08-13 - Main-buoy upper-frame support base

- Added an EPDM-lined non-penetrating clamp interface around the 650 mm body.
- Added four diagonal risers, eight gusset struts, an annular service deck, and
  four isolated mounting pads aligned with the Revision 5 upper frame.
- Preserved a 340 mm central service opening and prohibited drilling through
  the sealed HDPE shell in the design intent.

## 2026-08-13 - Fresh sealed-pod dual-solar frame

- Added a new frame independent of all deleted/superseded upper frames.
- Added two open East/West side structures, four deck feet, lower diagonal
  braces, three panel rails per side, and a compact central sensor bridge.
- Updated final assembly cleanup to treat this frame as active and the earlier
  two-side frame as legacy.

## 2026-08-13 - Revision 5 assembly cleanup

- Added reversible visibility-only cleanup for the final Revision 5 assembly.
- Added missing-active-system reporting and export-review metadata.
- Preserved all legacy geometry without moving or deleting components.

## 2026-08-13 - Ballast V2 anchor connector

- Added upper/lower shackles, load swivel, elastic snubber, and secondary
  lanyard between the adjustable ballast and existing anchor eye.

## 2026-08-13 - Adjustable low ballast V2

- Added a 500 mm central ballast rail below the rounded keel with four separate
  removable weight plates.
- Added upper/lower locking collars, secondary retention, and a lower
  anchor-chain clevis.
- Kept final ballast mass and depth dependent on loaded stability testing.

## 2026-08-13 - Pod marine protection hardware

- Added eight 316L lid clamps, four vibration isolators, and six downward IP68
  gland envelopes.
- Added external emergency isolation, solar surge protection, a dedicated
  lightning bonding lug, and secondary lid-retention cable.

## 2026-08-13 - Upper pod electronics packaging

- Added separate editable equipment envelopes for the LiFePO4 battery, BMS,
  MPPT, DC-DC, fused distribution, disconnect, Orange Pi, ESP32, LTE modem, and
  sensor distribution board.
- Organized the pod into battery, power/thermal, and control/communications
  service levels.
- Raised the internal recirculation-fan reference positions to preserve the
  battery and power-equipment packaging zones.

## 2026-08-13 - Sealed pod thermal system

- Added two 80 mm internal recirculation fans and airflow guides.
- Added a sealed aluminum thermal bridge and rear external eight-fin heat sink.
- Added a temperature/humidity sensor bracket with 40 C fan enable, 55 C
  derating, and 65 C shutdown design thresholds.
- Preserved pod ingress protection by providing no outside-air opening into the
  dry electronics volume.

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
