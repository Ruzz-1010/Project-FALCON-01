# Connector Register

All connector series, keying, current ratings, colors, and waterproof bulkhead
transitions are TBD. The pin numbers below define the intended logical order;
they do not authorize wiring an unverified purchased connector.

| Ref | Service | Pin assignment | Release note |
| --- | --- | --- | --- |
| J1 | Protected carrier input | 1 `+5V_PROTECTED`, 2 `GND` | Keyed 2-pin; rating based on measured load and fuse |
| J2 | Bar02 R2 JST-GH | 1 `+3V3_SENSOR` (red), 2 `I2C_SCL` (green), 3 `I2C_SDA` (white), 4 `GND` (black) | Blue Robotics official R2 order; verify plug-view orientation before energizing |
| J3 | GPS | 1 `+3V3_SENSOR`, 2 `GND`, 3 `GPS_TX`, 4 `GPS_RX` | Power selection must match purchased GPS revision |
| J4 | INA260 battery logic | 1 `+3V3_SENSOR`, 2 `GND`, 3 `I2C_SCL`, 4 `I2C_SDA` | High current does not use this connector |
| J5 | INA260 solar logic | 1 `+3V3_SENSOR`, 2 `GND`, 3 `I2C_SCL`, 4 `I2C_SDA` | Module address must be `0x41`; high current stays off-carrier |
| J6 | MCP9808 | 1 `+3V3_SENSOR`, 2 `GND`, 3 `I2C_SCL`, 4 `I2C_SDA` | Place sensor away from hot processors/regulator |
| J7 | Anemometer | 1 `+3V3_SENSOR`, 2 `WIND_PULSE`, 3 `GND` | Reed contact normally uses signal and ground; third pin reserved for keyed harness |
| J8 | Wind vane | 1 `+3V3_SENSOR`, 2 `WIND_VANE`, 3 `GND` | Input must remain within ADS1115 rails |
| J9 | DS18B20 | 1 `+3V3_SENSOR`, 2 `WATER_TEMP`, 3 `GND` | Confirm probe wire colors; never trust color alone |
| J10 | Leak sensor | 1 `+3V3_SENSOR`, 2 `LEAK_SIGNAL`, 3 `GND` | Placeholder until sensor output is known |
| J11 | Fan | 1 fan supply, 2 `FAN_SWITCHED` | Placeholder until fan voltage/current is known |
| J12 | Service I2C | 1 `+3V3_SENSOR`, 2 `GND`, 3 `I2C_SCL`, 4 `I2C_SDA` | Bench diagnostics only; keyed and labeled |

## Module headers

ESP32, BNO085, ADS1115, and any directly socketed breakout require footprints
made from measured purchased boards. Put module reference, pin 1, voltage, and
orientation on both silkscreen and assembly drawing. Prevent installation one
row or 180 degrees out where practical.
