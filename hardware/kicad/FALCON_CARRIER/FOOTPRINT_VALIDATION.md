# Footprint Validation Gate


<!-- FALCON-DOST-REVISION-NOTE:START -->
> **Current revision note (2026-10-10):** Use the DOST major revision baseline in [`docs/REVISION_2026-10-10.md`](../../../docs/REVISION_2026-10-10.md) unless this file is explicitly archived. The active design is a compact single-tube / small-buoy, ESP32-based, event-driven, cloud-first system. LoRa, large Bay Station hardware, tall tower layouts, and continuous every-second uploads are legacy or optional fallback assumptions.
<!-- FALCON-DOST-REVISION-NOTE:END -->

Status: **required before copper routing or fabrication**.

Print [`FOOTPRINT_MEASUREMENT_WORKSHEET.html`](FOOTPRINT_MEASUREMENT_WORKSHEET.html)
from a browser at 100% scale on A4 portrait paper. Use one page-one copy per
module, then transfer the signed results to `footprint_measurements.csv`.

The PCB now uses official CAD geometry for U2, U3, J3, J4, J5, and U4; all
remaining unselected module envelopes are provisional. JST GH/VH connector
geometry is captured from official catalogs, while manufacturer CAD is
not proof that the delivered revision or installed headers will fit. Validate every line in
`footprint_measurements.csv` using the actual item, a digital caliper, and clear
photos of both sides.

## How to measure

1. Identify the exact manufacturer, product number, and board revision.
2. Photograph the top and bottom beside a metric ruler.
3. Measure PCB width, length, and maximum assembled height in millimeters.
4. Measure header pitch, distance between header rows, pin count, and distance
   from pin 1 to the nearest two PCB edges.
5. Record mounting-hole diameter and center coordinates from the same datum.
6. Record connector body and cable insertion/removal clearance.
7. Mark pin 1 and copy the printed pin labels in physical order.
8. Print the KiCad board at 100% scale and place each module over its outline.
9. Sign only when the outline, pins, USB/antenna access, and connector clearance
   physically match.

Do not estimate from marketplace pictures. Boards sold under the same generic
name—especially `ESP32 DevKit V1`—often have different header-row spacing,
length, USB connector, and regulator placement.

## Highest-priority evidence

| Priority | Reference | Item | Required evidence |
| --- | --- | --- | --- |
| 1 | U2 | Espressif ESP32-DevKitC V4 with ESP32-WROOM-32E | Official 38-pin CAD is locked; verify delivered revision, USB overhang, antenna end, and header fit at 1:1 |
| 2 | U3 | Adafruit BNO085 PID 4754 | Board outline, full header order, holes, P0/P1 access, axis orientation |
| 3 | J2 | Historical Blue Robotics Bar02 R2 | Obsolete; replace with exact HPT604 loop connector and receiver components |
| 4 | J3 | GPS breakout | Exact product/revision, header order, antenna and keep-out |
| 5 | J4/J5 | INA260 breakouts | Logic header geometry plus high-current terminal orientation and cable clearance |
| 6 | U4/J6 | ADS1115/MCP9808 | Exact breakout revision, header/Qwiic geometry, address-jumper access |
| 7 | J7–J12 | External interfaces | Selected keyed connector family, pin numbering, mating direction, current/IP rating |
| 8 | U1/U5 | Regulator/fan driver | Selected topology, part numbers, thermal envelope, connector orientation |
| 9 | H1–H4 | Carrier mounting | Enclosure datum, hole coordinates, standoff diameter/height, tool clearance |

## Electrical cross-check during receiving

- Confirm there is no 5 V output connected to a 3.3 V-only ESP32 GPIO.
- Confirm all I2C breakout pull-ups and calculate their combined resistance.
- Confirm INA260 solar address configuration produces `0x41` after power cycle.
- Confirm BNO085 P0 and P1 can be held high for SPI mode.
- Confirm USB and external 5 V cannot back-feed one another.
- Confirm the exact HPT604 cable, vent, connector/gland, strain relief, probe guard, and dry-end desiccant/breather arrangement.
- Confirm fan voltage, running current, startup current, and whether it contains
  internal electronics that affect flyback protection or PWM.
- Confirm the leak detector's idle/output/fault voltages before connecting GPIO32.

## Release result

Routing may begin only after U2, U3, J2, J3, J4/J5, the power-input connector,
and mounting-hole coordinates are marked `PASS`. Optional interfaces may remain
`DNP/TBD` only when their pads are electrically isolated and clearly marked on
the board and schematic.
