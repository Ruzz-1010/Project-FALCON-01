# WATER_PRESSURE_SENSOR_ASSEMBLY


<!-- FALCON-DOST-REVISION-NOTE:START -->
> **Current revision note (2026-10-10):** Use the DOST major revision baseline in [`docs/REVISION_2026-10-10.md`](../../docs/REVISION_2026-10-10.md) unless this file is explicitly archived. The active design is a compact single-tube / small-buoy, ESP32-based, event-driven, cloud-first system. LoRa, large Bay Station hardware, tall tower layouts, and continuous every-second uploads are legacy or optional fallback assumptions.
<!-- FALCON-DOST-REVISION-NOTE:END -->

Adds one separate editable component named
`WATER_PRESSURE_SENSOR_ASSEMBLY_REV6_PROPOSED` to the current Fusion assembly.

The proposed location is on the permanently submerged underside of the rounded
keel. It is offset 125 mm from the centerline so the pressure port remains clear
of the ballast and anchor-chain load path. A 316L stainless saddle assembly uses
an underside plate, four standoffs, a carrier plate, and four M8 fastener
envelopes to support the historical Bar02-compatible sensor, downward pressure port, open
six-rod protective guard, and IP68 cable-gland envelope.

This is proposed integration geometry, not an installed or calibrated sensor.
Its radial offset, height, sensor size, and guard dimensions are user parameters.
Final placement requires a waterline check, cable-routing review, and controlled
pressure calibration. Report wave height as **ESTIMATED** and **CALIBRATION
REQUIRED** until validation is complete.

> Superseded pressure package: the recommended deployment candidate is now a vented-cable HPT604 4–20 mA probe. This CAD remains a reference only and must be redimensioned from the physically received exact HPT604 configuration, its cable bend radius, strain relief, guard, and dry vent termination before fabrication.

The generator stops before changes when positions are uncaptured. On rerun, it
repairs only an existing pressure-sensor occurrence by applying the underside
orientation; it does not rebuild or duplicate it. No other part is moved,
hidden, edited, or deleted.
