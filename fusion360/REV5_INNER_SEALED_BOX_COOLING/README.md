# REV5_INNER_SEALED_BOX_COOLING

Adds a second sealed enclosure and closed-loop cooling system inside
`REV5_RECTANGULAR_MARINE_ELECTRONICS_POD`.

- 270 x 220 x 330 mm inner UV-resistant polymer box;
- front removable door with raised sealing frame and dual EPDM gasket paths;
- lower power/battery deck and upper control deck;
- two 80 mm internal recirculation fans;
- rear 6 mm aluminum cold plate;
- sealed clamped thermal bridge through the rear interface;
- external 180 x 220 mm aluminum heat sink with eight fins; and
- top/rear splash hood that leaves the heat-sink sides and bottom open.

There is no outside-air intake or exhaust. No humidity or leak sensor is added.
The existing MCP9808 enclosure-temperature sensor is the only thermal-control
sensor in scope. Existing components are not moved, cut, joined, or deleted.

The script is repairable and non-duplicating: if its component already exists,
running it again reconnects that occurrence to the current rectangular-pod
transform. This corrects assemblies moved away from the global origin without
deleting or rebuilding any body.

All dimensions are packaging geometry. Verify purchased-part dimensions, heat
load, thermal resistance, sealing, galvanic isolation, vibration, salt fog, and
service clearances before fabrication.
