# Fusion 360 CAD Scripts

## Current Solar Elevation Upgrade

`SOLAR_PANEL_ELEVATION_UPGRADE` raises the four panels by 150 mm and adds
eight upper-frame extension struts. It does not move the buoy, electronics,
ballast, or sensor components.

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
