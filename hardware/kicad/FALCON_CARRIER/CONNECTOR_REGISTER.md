# Connector Register


<!-- FALCON-DOST-REVISION-NOTE:START -->
> **Current revision note (2026-10-10):** Use the DOST major revision baseline in [`docs/REVISION_2026-10-10.md`](../../../docs/REVISION_2026-10-10.md) unless this file is explicitly archived. The active design is a compact single-tube / small-buoy, ESP32-based, event-driven, cloud-first system. LoRa, large Bay Station hardware, tall tower layouts, and continuous every-second uploads are legacy or optional fallback assumptions.
<!-- FALCON-DOST-REVISION-NOTE:END -->

Internal connector families now have a procurement baseline in
[`CONNECTOR_SELECTION_BASELINE.md`](CONNECTOR_SELECTION_BASELINE.md). Received
parts, contacts, wire gauges, tooling, and waterproof bulkhead transitions still
require validation before fabrication.

| Ref | Service | Pin assignment | Release note |
| --- | --- | --- | --- |
| J1 | Alternate regulated 5 V input | 1 `+5V_INPUT_RAW`, 2 `GND` | JST B2P-VH-FB-B / VHR-2N; passes through U6 and JP1; USB must be unplugged |
| J2 | Historical Bar02 R2 JST-GH | 1 `+3V3_SENSOR` (red), 2 `I2C_SCL` (green), 3 `I2C_SDA` (white), 4 `GND` (black) | OBSOLETE FOR DEPLOYMENT; HPT604 needs a separate 12 V 4–20 mA loop receiver and keyed two-wire termination |
| J3 | Socketed Ultimate GPS PID 746 | pad 2 `+3V3_SENSOR`, 3 `GND`, 4 `GPS_RX`, 5 `GPS_TX`; remaining pads open | Official module-header order; preserve antenna/u.FL clearance |
| J4 | INA260 battery logic | 1 `+3V3_SENSOR`, 2 `GND`, 3 `I2C_SCL`, 4 `I2C_SDA` | High current does not use this connector |
| J5 | INA260 solar logic | 1 `+3V3_SENSOR`, 2 `GND`, 3 `I2C_SCL`, 4 `I2C_SDA` | Module address must be `0x41`; high current stays off-carrier |
| J6 | MCP9808 | 1 `+3V3_SENSOR`, 2 `I2C_SCL`, 3 `I2C_SDA`, 4 `GND` | JST BM04B-GHS-TBT; place sensor away from heat |
| J7 | Anemometer | 1 `+3V3_SENSOR`, 2 `WIND_PULSE`, 3 `GND` | JST BM03B-GHS-TBT; reed harness may populate signal/GND only |
| J8 | Wind vane | 1 `+3V3_SENSOR`, 2 `WIND_VANE`, 3 `GND` | JST BM03B-GHS-TBT; input must remain within ADS1115 rails |
| J9 | DS18B20 | 1 `+3V3_SENSOR`, 2 `WATER_TEMP`, 3 `GND` | JST BM03B-GHS-TBT; confirm probe wires by continuity |
| J10 | Leak sensor | 1 `+3V3_SENSOR`, 2 `LEAK_SIGNAL`, 3 `GND` | JST BM03B-GHS-TBT; blocked by exact detector output |
| J11 | Fan 1 PWM | 1 GND, 2 `+5V_PROTECTED`, 3 `FAN1_TACH`, 4 `FAN1_PWM_OD` | Molex 470531000 / 470541000; verify received fan mating and key |
| J13 | Fan 2 PWM | 1 GND, 2 `+5V_PROTECTED`, 3 `FAN2_TACH`, 4 `FAN2_PWM_OD` | Molex 470531000 / 470541000; do not join tach outputs |
| J12 | Service I2C | 1 `+3V3_SENSOR`, 2 `I2C_SCL`, 3 `I2C_SDA`, 4 `GND` | JST BM04B-GHS-TBT; bench diagnostics only |

## Module headers

ESP32, BNO085, ADS1115, and any directly socketed breakout require footprints
made from measured purchased boards. Put module reference, pin 1, voltage, and
orientation on both silkscreen and assembly drawing. Prevent installation one
row or 180 degrees out where practical.
