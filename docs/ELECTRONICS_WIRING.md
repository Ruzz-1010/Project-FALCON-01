# FALCON-01 Electronics Wiring Baseline

This is the recommended Phase 1 **bench prototype**. It gives us a real shopping
and wiring baseline without inventing final marine fuse sizes or cable gauges.

Open [the SVG wiring diagram](diagrams/FALCON-01-electronics-wiring.svg) directly
in VS Code. Exact GPIO connections are in [PINOUT.md](PINOUT.md).

For an easier spatial overview, open the
[3D-style assembly guide](diagrams/FALCON-01-electronics-wiring-3d.png). The 3D
image is illustrative: use `PINOUT.md`, not the generated board markings, when
connecting individual pins.

## Recommended Parts

| Qty | Part | Reason |
| ---: | --- | --- |
| 1 | Espressif ESP32-DevKitC V4 with ESP32-WROOM-32E, 38-pin | Exact carrier reference; preserves GPIO16/17 |
| 1 | Adafruit BNO085 breakout | Fused orientation; use documented SPI mode |
| 1 | Blue Robotics Bar02 | Shallow-water range and 0.16 mm depth resolution |
| 1 | Adafruit Ultimate GPS or equivalent 3.3 V UART GPS | Simple UART integration |
| 2 | INA260 breakouts | Separate battery and solar monitoring |
| 1 | MCP9808 breakout | Enclosure temperature |
| 1 | ADS1115 breakout | Stable 16-bit wind-vane measurement |
| 1 | SparkFun Weather Meter Kit | Prototype wind speed/direction |
| 1 | Orange Pi Zero 3, 4 GB | Edge service and dashboard host |
| 1 | 12.8 V LiFePO4 battery | Storage baseline; capacity needs load testing |
| 1 | LiFePO4-compatible MPPT | Must match exact panel and battery |
| 1 | 12 V to regulated 5 V / 3 A minimum buck | Dedicated Orange Pi supply |
| 1 | Separate regulated 12 V to 5 V buck | ESP32/peripheral supply |
| 1 | Fused distribution and disconnect | Branch isolation/service |

Bar02 is preferred over Bar30 for surface-wave measurement because its range and
resolution fit shallow water better. The rear is not waterproof by itself: use a
proper bulkhead seal and follow the maker's drying/maintenance requirements.

## Signal Wiring Order

Disconnect every power source first.

1. Connect ESP32 by USB only; upload a serial or blink test.
2. Build the 3.3 V I2C bus on GPIO21 SDA and GPIO22 SCL.
3. Add one I2C module at a time and scan its address after each addition.
4. Wire BNO085 through SPI per `PINOUT.md`; P0/P1 go high. Include INT and RST.
5. Cross GPS TX to GPIO16 RX2 and GPS RX to GPIO17 TX2.
6. Connect the anemometer reed between GPIO25 and GND, with an external 10 kOhm
   pull-up from GPIO25 to 3.3 V. Debounce pulses in firmware.
7. Make the vane's resistor divider from 3.3 V and send its midpoint to ADS1115
   A0. Calibrate every direction; do not copy generic thresholds blindly.
8. For the prototype, connect Orange Pi to the ESP32 USB port. This avoids direct
   Orange Pi header mistakes and leaves ESP32 UART0 available for debugging.

## Power Architecture

```text
Solar -> LiFePO4 MPPT -> 12.8 V battery -> main fuse -> disconnect -> distribution
                                                               |-> 5 V/3 A buck -> Orange Pi
                                                               `-> separate 5 V buck -> ESP32
                                                                                      `-> 3V3 sensors
```

Do not guess fuse ratings or wire sizes. Before marine assembly, record exact
part numbers, continuous/startup current, cable length and voltage drop,
connector/IP ratings, fuse calculations, and corrosion/condensation controls.
INA260 high-current paths must remain inside the exact board's ratings.

## Bench Checklist

- [ ] Photograph both sides of each board and record its exact revision.
- [ ] Meter every buck output before connecting electronics.
- [ ] Check that positive and ground rails are not shorted.
- [ ] Power ESP32 alone and verify its 3.3 V rail.
- [ ] Scan I2C after every added module.
- [ ] Verify BNO085 quaternion output over SPI.
- [ ] Verify GPS sentences/fix over UART2.
- [ ] Calibrate all vane positions and test anemometer pulses.
- [ ] Compare pressure against a known reference at rest.
- [ ] Verify ESP32 USB telemetry and Orange Pi brownout behavior.
- [ ] Only then assemble the fused low-voltage branches.

## Reference Datasheets and Guides

- [Espressif ESP32 datasheet](https://www.espressif.com/sites/default/files/documentation/esp32_datasheet_en.pdf)
- [Adafruit BNO085 guide](https://learn.adafruit.com/adafruit-9-dof-orientation-imu-fusion-breakout-bno085?view=all)
- [Blue Robotics Bar02/Bar30 specifications](https://bluerobotics.com/store/sensors-cameras/sensors/bar-depth-pressure-sensor/)
- [Adafruit ADS1115 guide](https://learn.adafruit.com/adafruit-4-channel-adc-breakouts?view=all)
- [SparkFun Weather Meter guide](https://learn.sparkfun.com/tutorials/weather-meter-hookup-guide/all?print=1)

This becomes a final marine harness only after the purchased modules, connector
pinouts, load measurements, fusing, cable sizing, and waterproofing are reviewed.
