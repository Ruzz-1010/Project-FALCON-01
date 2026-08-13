# Fusion 360 CAD Scripts

## Current Solar Elevation Upgrade

`COMPACT_ELEVATED_UPPER_TOWER` is the active correction. It retains the four
panels at +150 mm, raises the sensor array and navigation light by the same
amount, and replaces the visible 560 mm frame with a compact 460 mm low-drag
frame. `SOLAR_PANEL_ELEVATION_UPGRADE` is retained only as the earlier
panel-only revision.

`DUAL_30W_SOLAR_REPLACEMENT` is the current solar configuration: two separate
30 W panels on opposite East and West sides, mounted at Z1170 mm with a
20-degree outward tilt. The former four-panel array is legacy geometry.

`TWO_SIDE_SOLAR_FRAME_V3` is the active matching frame. It has only two open
flat support sides, East and West, for the two 30 W panels. There are no North
or South panel frames and no circular rings. `DUAL_SOLAR_COMPACT_FRAME_V2` is
retained as a superseded intermediate revision.

`UPPER_ALL_ELECTRONICS_POD` is the active serviceability concept: a sealed
320 mm OD upper pod containing the battery and serviceable electronics, with a
double-gasket lid, sun/rain shield, leak tray, thermal plate, control rack,
membrane vent, and downward IP68 connector panel.

## Current Mechanical Revision: 5.0

The current production direction uses `MAIN_FLOAT_TRADITIONAL_V2`, a traditional Ø650 mm HDPE single-body buoy with a 240 mm rounded tapered underwater keel.

Current Revision 5 scripts include the V2 main float, top cap, electronics/cooling system, structural frames, solar array, upper sensors, central ballast, and single-anchor mooring system. The ballast position must be revised below the deeper V2 keel before the assembly is considered interference-free.

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
