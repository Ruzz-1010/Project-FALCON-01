# SEALED_POD_THERMAL_SYSTEM


<!-- FALCON-DOST-REVISION-NOTE:START -->
> **Current revision note (2026-10-10):** Use the DOST major revision baseline in [`docs/REVISION_2026-10-10.md`](../../docs/REVISION_2026-10-10.md) unless this file is explicitly archived. The active design is a compact single-tube / small-buoy, ESP32-based, event-driven, cloud-first system. LoRa, large Bay Station hardware, tall tower layouts, and continuous every-second uploads are legacy or optional fallback assumptions.
<!-- FALCON-DOST-REVISION-NOTE:END -->

Adds closed-loop cooling hardware directly to
`REV5_RECTANGULAR_MARINE_ELECTRONICS_POD`. It does not add a second enclosure.

- two horizontal 80 mm internal recirculation fans;
- lower and upper horizontal airflow guides;
- sealed clamped thermal bridge through the rear interface;
- external vertical 180 x 220 mm aluminum heat-sink base with eight projecting
  fins.

The service door is on the negative-Y front side. The thermal bridge and finned
heat sink are mounted on the opposite positive-Y rear side and rotated so the
bridge clamps inward while the fins project outward. This keeps the front door
and its service swing clear.

There is no outside-air intake or exhaust. No humidity or leak sensor is added.
The existing MCP9808 enclosure-temperature sensor is the only thermal-control
sensor in scope. Existing components are not moved, cut, joined, or deleted.

The script is repairable and non-duplicating. If its component already exists,
running it again reconnects the cooling hardware to the current rectangular-pod
transform, hides the obsolete humidity bracket and hides any later misplaced
cooling duplicate without deleting it. The authoritative arrangement matches
the installed geometry shown in Screenshot 693.

All dimensions are packaging geometry. Verify purchased-part dimensions, heat
load, thermal resistance, sealing, galvanic isolation, vibration, salt fog, and
service clearances before fabrication.
