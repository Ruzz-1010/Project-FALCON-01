# FALCON-01 Clear Wiring Map — Historical Prototype


<!-- FALCON-DOST-REVISION-NOTE:START -->
> **Current revision note (2026-10-10):** Use the DOST major revision baseline in [`docs/REVISION_2026-10-10.md`](REVISION_2026-10-10.md) unless this file is explicitly archived. The active proposal core is a compact ESP32-based buoy with **water pressure sensing, wind speed/direction sensing, GPS for exact position and security, battery + solar power, and Wi-Fi/LTE internet communication**. LoRa, large Bay Station hardware, tall tower layouts, and continuous every-second uploads are legacy or optional fallback assumptions.
<!-- FALCON-DOST-REVISION-NOTE:END -->

> Do not fabricate from this older BNO085/Orange-Pi-centered map. Use `PINOUT.md` and `BAY_STATION_ARCHITECTURE.md`; the final harness awaits exact purchased parts and an approved LTE modem. No Bay Station computer belongs in the buoy harness.

Status: **bench-wiring reference; not a final marine harness**.

Open the [color-coded wiring sheet](diagrams/FALCON-01-clear-wiring.svg) for the
visual layout. Disconnect USB, battery, and solar power before changing wiring.

## BNO085 SPI

| Adafruit PID 4754 carrier pad | Breakout label | ESP32 connection |
| --- | --- | --- |
| A1 | VIN | 3.3 V sensor rail |
| A3 | GND | GND |
| A4 | SCL/SCK/RX | GPIO18 SCK |
| A5 | SDA/MISO/TX | GPIO19 MISO |
| A6 | INT | GPIO27 |
| B2 | PS0 | 3.3 V for SPI mode |
| B3 | PS1 | 3.3 V for SPI mode |
| B4 | RST | GPIO14 |
| B5 | MOSI | GPIO23 |
| B6 | CS | GPIO13 |

A2 `3Vo` and B1 `BOOT` remain physically socketed but electrically open.

## Shared I2C

Every installed I2C module uses `SDA → GPIO21`, `SCL → GPIO22`, 3.3 V logic,
and common GND.

| Device | Address | Special rule |
| --- | --- | --- |
| Blue Robotics Bar02 R2 | `0x76` | JST-GH: 1 Vin/red, 2 SCL/green, 3 SDA/white, 4 GND/black |
| INA260 battery | `0x40` | Logic header only; load current stays off-carrier |
| INA260 solar | `0x41` | Set address and verify after power cycle |
| MCP9808 | `0x18` | Keep away from regulator, processors, and fan exhaust |
| ADS1115 | `0x48` | Wind-vane divider midpoint connects to A0 |

## GPS UART2

| Ultimate GPS PID 746 pin | Connection |
| --- | --- |
| 2 VIN | 3.3 V sensor rail |
| 3 GND | GND |
| 5 TX | ESP32 GPIO16 RX2 |
| 4 RX | ESP32 GPIO17 TX2 |

TX and RX cross because one device's transmitter connects to the other's
receiver. GPS pins 1, 6, 7, 8, and 9 remain unconnected in the baseline.

## External inputs

- Anemometer reed: GPIO25 to GND; 10 kOhm pull-up from GPIO25 to 3.3 V.
- Wind vane: 3.3 V divider; midpoint to ADS1115 A0; calibrate after installation.
- Optional DS18B20: DQ to GPIO26; 4.7 kOhm pull-up from GPIO26 to 3.3 V.
- Leak input GPIO32 and fan driver GPIO33 remain provisional until exact parts
  and electrical characteristics are selected.

## Power boundary

The carrier receives protected regulated 5 V only. Raw panel, battery, MPPT,
and branch load current do not enter ordinary carrier headers. The selected LTE modem
uses a separate regulated 5 V / at least 3 A branch. INA260 high-current
terminals remain in their separately fused external paths.

The Bar02 entry above is retained only to interpret the historical drawing. The deployment candidate is an HPT604 4–20 mA probe and requires a protected 12 V loop, 150 ohm precision shunt, ADS1115 receiver, and dry vent termination as specified in [PRESSURE_SENSOR_BASELINE.md](PRESSURE_SENSOR_BASELINE.md). Do not fabricate the old J2 pressure connection.
