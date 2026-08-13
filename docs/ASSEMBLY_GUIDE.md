# Assembly Guide

## Purpose
Define safe current setup and gates for future assembly.

## Scope
USB-powered ESP32 bench setup and future electronics/marine assembly.

## Current Status
Only the ESP32 bench setup is confirmed. Mechanical Revision 5.0 is the approved CAD direction but remains subject to fabrication, flotation, leak, ballast-clearance, and stability validation.

## Architecture
Controller bench -> individual modules -> protected power -> enclosure -> mechanical structure -> integrated validation.

## Implementation
Place ESP32 on a non-conductive surface, inspect it, use a data-capable USB cable, confirm CH340 port, flash firmware and LittleFS separately, then verify startup and portal.

Do not guess GPIOs, connect unadjusted LM2596 output, energize an unprotected battery/solar system, or claim an IP rating without assembly testing.

## Future Expansion
Add approved schematics, wiring, connectors, torque/seal procedures, photographs, BOM revisions, and inspection forms.

## Engineering Notes
Disconnect power before wiring. Marine energy storage requires proper supervision and protective equipment.

## Mechanical Revision 5 Assembly Order

1. Generate and inspect `MAIN_FLOAT_TRADITIONAL_V2` without deleting the original CAD body.
2. Hide the Legacy Revision 4 main-body representation and all outrigger/stabilizer components in the Revision 5 representation.
3. Verify the existing top cap, electronics enclosure, vent penetrations, and upper frame against the V2 body.
4. Relocate/redesign the central ballast below the 240 mm keel with adequate motion clearance.
5. Connect the ballast to the single-anchor mooring system.
6. Perform dry interference, leak, loaded-waterline, heel, and roll/pitch recovery tests before deployment.

Do not physically remove stabilizers from a prototype and deploy the modified buoy without repeating stability validation.

## Revision History
| Version | Date | Change |
| --- | --- | --- |
| 1.0 | 2026-08-05 | Initial bench-only guide. |
| 2.0 | 2026-08-13 | Added controlled assembly transition to the single-body rounded-keel mechanical baseline. |
