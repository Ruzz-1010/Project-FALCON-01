# FALCON-01 Carrier Routing Plan

Status: **routing-preparation baseline; routing blocked by critical footprint
validation**.

## Net classes

| Class | Nets | Width | Clearance | Via |
| --- | --- | ---: | ---: | ---: |
| Power | `+5V_PROTECTED`, `+3V3_SENSOR`, `GND` | 0.75 mm | 0.30 mm | 1.0/0.5 mm |
| SensorBus | `I2C_*`, `BNO_*`, `GPS_*` | 0.30 mm | 0.25 mm | 0.8/0.4 mm |
| ExternalSensor | `WIND_*`, `WATER_TEMP`, `LEAK_SIGNAL` | 0.40 mm | 0.30 mm | 0.9/0.4 mm |
| FanLoad | `FAN_SWITCHED` | 0.75 mm | 0.30 mm | 1.0/0.5 mm |
| Default | Remaining low-current logic, including `FAN_PWM` | 0.20 mm | 0.20 mm | 0.6/0.3 mm |

Widths are conservative prototype defaults, not final current/thermal proof.
Recalculate the power and fan classes after measuring actual current, copper
weight, temperature rise, and connector ratings.

## Routing order

1. Freeze verified footprints, board outline, holes, connectors, and antenna
   keep-outs. Do not route around geometry still marked `PENDING`.
2. Route protected 5 V and regulated 3.3 V as short branches from the power
   section. Do not create a thin daisy-chain through sensor-module headers.
3. Establish a continuous bottom-layer ground plane. Avoid signal cuts that
   fragment return paths.
4. Route BNO085 SPI directly between U2 and U3. Keep it away from the fan driver,
   regulator, GPS antenna, and external field cables. Avoid unnecessary vias.
5. Route I2C as one controlled trunk with short branches. Do not create a star
   with long stubs. Verify the combined breakout pull-up resistance first.
6. Route GPS UART away from switcher/fan loops and preserve antenna clearance.
7. Route wind, water-temperature, and leak inputs from their service connectors
   to the controller/ADC. Keep the wind-vane analog path away from digital clocks.
8. Route fan PWM separately from the switched load current. Keep the fan current
   loop local to the power/driver zone.
9. Add ground stitching where it improves return continuity, not inside antenna
   keep-outs or beneath prohibited module areas.
10. Route the TP1–TP18 branches as short stubs from their monitored nets; do not
    force a sensitive bus or analog signal to detour through a test point.
11. Refill zones, run DRC, inspect every unrouted item, and review both copper
    layers visually before generating any fabrication output.

## Completion criteria

- Critical footprint rows in `footprint_measurements.csv` are `PASS`.
- No trace or copper pour enters the ESP32/GPS antenna keep-outs.
- BNO085 axis and mounting orientation are documented.
- ERC reports zero errors and warnings.
- DRC reports zero violations and zero unconnected items.
- A second reviewer verifies connector order, polarity, and both INA260 paths.
- A 1:1 print passes with actual modules and enclosure mounting hardware.
