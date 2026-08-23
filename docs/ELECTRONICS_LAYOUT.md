# Electronics Pod Layout Baseline

This layout coordinates the existing 485 × 325 mm removable-tray concept with
electrical segregation. Purchased-part dimensions remain required before holes
are drilled or CAD envelopes are released.

## Three Levels

| Level | Equipment | Placement rule |
| --- | --- | --- |
| Lower | 12.8 V battery and BMS | Centered low, restrained in every axis, isolated from leak path |
| Power | MPPT, disconnect, fuse block, two buck converters, INA260 high-current paths | Short high-current loops on thermal plate |
| Control | Orange Pi, ESP32, sensor distribution, ADS1115, MCP9808 | Removable service tray, separated from power switching |

## Control-Tray Zones

```text
FRONT / SERVICE SIDE
+-------------------------------------------------------------+
| Orange Pi + heatsink | 50 mm cable channel | ESP32 + USB    |
|----------------------+---------------------+----------------|
| GPS interface        | Sensor distribution | ADS1115/I2C    |
|----------------------+---------------------+----------------|
| Dry-loop service     | strain relief       | external glands|
+-------------------------------------------------------------+
REAR / BULKHEAD SIDE
```

- Keep the BNO085 on the rigid central structure, not beside fans, buck inductors,
  high-current conductors, magnets, or loose cable bundles.
- Put MCP9808 in representative enclosure airflow, away from Orange Pi heatsink.
- Route SPI and I2C separately from power wiring; cross at 90 degrees if needed.
- Terminate external sensor cables at labeled locking connectors before the ESP32.
- Provide drip loops, gland strain relief, service slack, and a lowest-point leak sensor.
- Keep the GPS antenna above switching electronics with a documented ground/clearance plan.

## Release Checklist

- [ ] Exact component envelopes entered in Fusion 360.
- [ ] Connector insertion/removal clearance checked with lid installed.
- [ ] Battery cannot contact electronics under shock or inversion.
- [ ] Main disconnect and every fuse remain service-accessible.
- [ ] Power and signal harnesses have independent tie points.
- [ ] Thermal path tested at sealed-pod ambient worst case.
- [ ] Condensation path cannot drip onto exposed terminals.
- [ ] Every cable and both ends carry the same circuit identifier.

## Future Layout Reservations

Reserve no unverified holes, cutouts, or power capacity as if future equipment
were already selected. After approval, layout studies may consider an isolated
camera connector/power switch, extra sensor termination area, modem clearance,
and a Raspberry Pi 5 tray with active-cooler airflow. Exact purchased dimensions
and sealed-pod thermal tests are required. See
[`FUTURE_UPGRADES.md`](FUTURE_UPGRADES.md).
