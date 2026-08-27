# Fusion 360 CAD Scripts

> **REDESIGN HOLD — 26 August 2026:** None of the assemblies or component positions below is the approved replacement prototype. All scripts are preserved as editable historical/reference geometry. Do not call any entry current, final, fabrication-ready, or deployment-ready until a new revision passes `docs/PROTOTYPE_REDESIGN_BASELINE.md`.

## Previous CAD development sequence

`WATER_PRESSURE_SENSOR_ASSEMBLY` is a new proposed integration study for the
replacement prototype. It adds a separate Bar02-compatible sensor envelope,
downward pressure port, open protective guard, mounting plate, and cable-gland
envelope on the submerged lower shoulder. Placement remains editable and must
be checked against the approved waterline, ballast, mooring, and cable route.

`COMPACT_ELEVATED_UPPER_TOWER` was a historical correction. It retains the four
panels at +150 mm, raises the sensor array and navigation light by the same
amount, and replaces the visible 560 mm frame with a compact 460 mm low-drag
frame. `SOLAR_PANEL_ELEVATION_UPGRADE` is retained only as the earlier
panel-only revision.

`DUAL_30W_SOLAR_REPLACEMENT` was the latest historical solar configuration: two separate
30 W panels on opposite East and West sides, mounted at Z1170 mm with a
20-degree outward tilt. The former four-panel array is legacy geometry.

`TWO_SIDE_SOLAR_FRAME_V3` was the matching historical frame. It has only two open
flat support sides, East and West, for the two 30 W panels. There are no North
or South panel frames and no circular rings. `DUAL_SOLAR_COMPACT_FRAME_V2` is
retained as a superseded intermediate revision.

`UPPER_ALL_ELECTRONICS_POD` was a historical serviceability concept: a sealed
320 mm OD upper pod containing the battery and serviceable electronics, with a
double-gasket lid, sun/rain shield, leak tray, thermal plate, control rack,
membrane vent, and downward IP68 connector panel.

`SEALED_POD_THERMAL_SYSTEM` adds two internal recirculation fans, airflow
baffles, a sealed thermal bridge, a rear external eight-fin heat sink, and a
temperature/humidity sensor bracket. It introduces no outside-air path into the
dry electronics compartment.

`UPPER_POD_ELECTRONICS_LAYOUT` populates the pod with separate editable
packaging envelopes: battery/BMS below, MPPT and protected power equipment in
the middle, and Orange Pi, ESP32, LTE, and sensor distribution on top.

`POD_MARINE_PROTECTION_HARDWARE` adds lid clamps, vibration isolators,
downward IP68 glands, emergency isolation, solar surge protection, an external
lightning bond, and secondary lid retention.

`ADJUSTABLE_LOW_BALLAST_V2` compensates for the upper electronics payload with
a low central rail, four removable plates, dual lock collars, secondary
retention, and an anchor-chain clevis. Final mass remains test-controlled.

`BALLAST_V2_ANCHOR_CONNECTOR` connects the new ballast clevis to the existing
anchor eye with dual shackles, a swivel, compact snubber, and safety lanyard.

`REV5_FINAL_ASSEMBLY_CLEANUP` applies the reversible final visibility state,
shows active Revision 5 systems, hides superseded geometry, and reports missing
required systems before export.

`REV5_POD_DUAL_SOLAR_FRAME` was a later historical structural frame for the
sealed-pod layout: two open solar side frames, four deck feet, lower diagonal
braces, and a compact sensor bridge. It does not depend on any deleted frame.

`REV5_MAIN_BUOY_FRAME_SUPPORT` supplies its missing primary load path using an
EPDM-lined split clamp, four gusseted diagonal risers, an annular service deck,
and four isolated upper-frame mounting pads without drilling the HDPE shell.

`REV5_TAPERED_MARINE_MAST` was the reference-inspired upper structure:
a 420-to-380-to-260 mm two-stage four-leg mast. Its lower bay preserves sealed
pod clearance while the upper bay tapers to the sensor platform. Horizontal
rails, full-face X-bracing, and two opposed solar cradles complete the frame.

`REV5_UPPER_TO_LOWER_LOAD_CAGE` adds four direct load-transfer struts and eight
knee braces between the tapered mast feet and the existing lower split-clamp
frame, keeping mast loads out of the HDPE shell.

`REV5_FULL_HEIGHT_EXTERNAL_SUPPORT_CAGE` supersedes that short cage with four
continuous tubes outside the complete float body, joining the upper mast/deck
to a new EPDM-lined structural collar around the lower fairing.

`REV5_FULL_HEIGHT_EXTERNAL_SUPPORT_CAGE_V2` corrects the upper connection: each
continuous load path begins at a top mast corner rather than at a mast foot,
slopes to the upper buoy ring, then runs vertically to the lower collar.

`REV5_LOWER_TO_MAIN_FRAME_SUPPORT_CAGE` was a corrected historical version: four
external tubes connect the lower buoy collar only to
`REV5_MAIN_BUOY_FRAME_SUPPORT` and terminate at its Z=480 mm support ring.

`REV5_LOWER_TO_MAIN_FRAME_SUPPORT_CAGE_V2` removes the visible overhang: its
tubes taper inward from radius 365 mm at the lower collar to radius 336 mm and
terminate inside the main support clamp band at Z=385 mm.

`REV5_RECTANGULAR_MARINE_ELECTRONICS_POD` replaces the visible round pod with a
300 x 280 x 400 mm chamfered UV-HDPE cabinet containing separate leak, power,
control, sealing, weather-protection, thermal and cable-interface components.

`REV5_INNER_SEALED_BOX_COOLING` adds a front-access 270 x 220 x 330 mm secondary
sealed box, dual EPDM door seals, internal power/control decks, two recirculation
fans, a cold plate, solid thermal bridge, rear finned sink, and splash hood. It
uses the existing MCP9808 only and adds no humidity or leak sensor.

`REV5_TOWER_FRONT_MAINTENANCE_GATE` replaces only the obstructing front-face
rails/braces with a separate tapered X-braced gate, left removable hinge pin,
right captive locks, and EPDM stops. Side/rear mast members remain unchanged.

## Previous Mechanical Revision: 5.0

Revision 5 used `MAIN_FLOAT_TRADITIONAL_V2`, a traditional Ø650 mm HDPE single-body buoy with a 240 mm rounded tapered underwater keel. These values are not automatically valid for the replacement design.

Historical Revision 5 scripts include the V2 main float, top cap, electronics/cooling system, structural frames, solar array, upper sensors, central ballast, and single-anchor mooring system. They are not the replacement prototype baseline.

## Legacy Revision 4

The following are retained only for traceability and rollback and are not part of a new Revision 5 assembly:

- `STABILIZER_ARM` and `STABILIZER_ARM_REINFORCEMENT`;
- `STABILIZER_ARM_UNIT_02`, `_03`, and `_04`;
- `STABILIZER_BUOY_01`, `STABILIZER_BUOY_SYSTEM`, and `STABILIZER_BUOY_UPSIZE_320`;
- `STABILIZER_TENSION_CABLE_SYSTEM`;
- the original `MAIN_FLOAT` body when the V2 body is active.

Do not delete these from the master CAD archive. Hide/suppress their occurrences in the Revision 5 representation.

## Safety Rule

All generators must preserve existing user geometry and positions unless the user explicitly approves a named component revision. Always Capture Position and save before running a generator.
