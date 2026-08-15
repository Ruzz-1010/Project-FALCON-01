# FALCON-01 Prototype Pinout Register

## Status

**Prototype baseline v0.1 — for 3.3 V bench assembly only.** Verify the printed
pin labels and exact breakout revision before power. Marine power wiring remains
subject to physical load, fuse, cable, connector, and waterproofing review.

Controller: ESP32 DevKit / ESP-WROOM-32.

## ESP32 Assignments

| Function | GPIO | Interface | Device pin / note |
| --- | ---: | --- | --- |
| Shared SDA | 21 | I2C | All SDA pins; 3.3 V bus |
| Shared SCL | 22 | I2C | All SCL pins; 3.3 V bus |
| BNO085 clock | 18 | SPI | SCL/SCK |
| BNO085 data out | 19 | SPI | SDA/MISO |
| BNO085 data in | 23 | SPI | DI/MOSI |
| BNO085 select | 13 | SPI | CS, active low |
| BNO085 interrupt | 27 | Input | INT, required |
| BNO085 reset | 14 | Output | RST, required |
| GPS receive | 16 | UART2 RX | GPS TX -> ESP RX |
| GPS transmit | 17 | UART2 TX | GPS RX <- ESP TX |
| Anemometer | 25 | Input | Reed to GND; external 10 kOhm pull-up |
| Optional DS18B20 | 26 | OneWire | DQ; external 4.7 kOhm pull-up |
| Leak/tamper | 32 | Input | Exact sensor TBD |
| Reserved fan | 33 | PWM output | MOSFET driver only; never direct fan |
| Edge link | USB | USB serial | Preferred prototype link to Orange Pi |

GPIO 0, 2, 5, 12, and 15 remain unused because they are strapping pins. GPIO 1
and 3 remain reserved for programming and logs.

## Shared I2C Bus

| Device | Address | Supply | Purpose |
| --- | --- | --- | --- |
| Blue Robotics Bar02 | Module default | 3.3 V | Pressure/wave input |
| INA260 battery | `0x40` | 3.3 V | Battery branch monitor |
| INA260 solar | `0x41` | 3.3 V | Solar/charger monitor |
| MCP9808 | `0x18` | 3.3 V | Enclosure temperature |
| ADS1115 | `0x48` | 3.3 V | Wind-vane analog input on A0 |

Set the second INA260 address to `0x41`. Inspect breakout pull-ups before adding
any. Wire the wind vane as a 3.3 V divider with an external 10 kOhm resistor and
calibrate its ADC bands after physical north alignment.

## BNO085

Use SPI, not I2C: the BNO085 I2C implementation has a documented ESP32
compatibility problem. Connect VIN to 3.3 V, common GND, and P0/P1 to 3.3 V for
SPI mode. Do not omit INT or RST.

## Power Rules

- ESP32 GPIO and sensor logic are 3.3 V; never apply a 5 V GPIO signal.
- Never connect raw 12.8 V to ESP32, Orange Pi, or sensor logic.
- Give Orange Pi a dedicated regulated 5 V / 3 A branch.
- Use a separate regulated branch for ESP32 and its peripherals.
- Join logic grounds at protected low-voltage distribution.
- INA260 high-current terminals are not interchangeable with logic pins.

See [ELECTRONICS_WIRING.md](ELECTRONICS_WIRING.md) and the
[visual wiring diagram](diagrams/FALCON-01-electronics-wiring.svg).

## Revision History

| Version | Date | Change |
| --- | --- | --- |
| 1.1 | 2026-08-15 | Added reviewed prototype GPIO and bus allocation. |
| 1.0 | 2026-08-05 | Unassigned pin register. |
