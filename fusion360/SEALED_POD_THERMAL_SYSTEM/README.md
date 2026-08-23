# SEALED_POD_THERMAL_SYSTEM

Adds closed-loop cooling hardware directly to
`REV5_RECTANGULAR_MARINE_ELECTRONICS_POD`. It does not add a second enclosure.

- two 80 mm internal recirculation fans;
- rear 6 mm aluminum cold plate;
- sealed clamped thermal bridge through the rear interface;
- external 180 x 220 mm aluminum heat sink with eight fins; and
- top/rear splash hood that leaves the heat-sink sides and bottom open.

There is no outside-air intake or exhaust. No humidity or leak sensor is added.
The existing MCP9808 enclosure-temperature sensor is the only thermal-control
sensor in scope. Existing components are not moved, cut, joined, or deleted.

The script is repairable and non-duplicating. If its component already exists,
running it again reconnects the cooling hardware to the current rectangular-pod
transform and hides the obsolete second-box geometry without deleting it.

All dimensions are packaging geometry. Verify purchased-part dimensions, heat
load, thermal resistance, sealing, galvanic isolation, vibration, salt fog, and
service clearances before fabrication.
