# FALCON-01 Carrier PCB Validation Register

## Status

**Pre-schematic review only — not approved for fabrication.** The recommended
Phase 1 board is a removable carrier PCB for purchased modules, not a new
ESP32 radio design and not a board that directly carries the complete marine
power path. Exact purchased revisions and measurements remain release gates.

## Validated Baseline

| Area | Result | Basis |
| --- | --- | --- |
| Controller | Espressif ESP32-DevKitC V4 with ESP32-WROOM-32E | Official 38-pad pinout and Espressif KiCad footprint locked; physical 1:1 receiving check remains open |
| I2C bus | GPIO21 SDA, GPIO22 SCL, 3.3 V logic | Firmware, pinout, and wiring documents agree |
| BNO085 SPI | SCK 18, MISO 19, MOSI 23, CS 13, INT 27, RST 14 | Firmware and documents agree; P0 and P1 high select SPI |
| GPS UART2 | GPS TX to GPIO16; GPS RX from GPIO17; 9600 baud baseline | Firmware and documents agree |
| Wind speed | GPIO25, reed switch to ground, external 10 kOhm pull-up | Valid prototype input arrangement; debounce/calibration still required |
| Water temperature | GPIO26 with external 4.7 kOhm OneWire pull-up | Valid optional interface; exact probe still required |
| I2C addresses | Bar02 `0x76`, battery INA260 `0x40`, solar INA260 `0x41`, MCP9808 `0x18`, ADS1115 `0x48` | No address collision in the selected baseline |
| Avoided pins | GPIO0, 2, 5, 12, 15; UART0 GPIO1/3 | Prevents baseline boot-strap and programming conflicts |
| Fan control | GPIO33 through a MOSFET driver only | GPIO must never directly power a fan |
| Edge link | ESP32 USB serial to Orange Pi | Preferred prototype connection; avoids an unvalidated direct SBC header link |

GPIO16 and GPIO17 are accepted only for the selected **ESP-WROOM-32 class**
board. Some ESP32 variants use these pins for PSRAM, so changing controller
variant requires another pin review.

## Electrical Architecture Decision

The carrier board shall accept only regulated low voltage:

```text
12.8 V battery / MPPT domain
        |
        +-- protected dedicated 5 V buck --> Orange Pi
        |
        `-- protected separate 5 V buck --> carrier PCB / ESP32
                                              `-- regulated 3.3 V sensor rail
```

- Raw battery or panel voltage shall not enter an ESP32 header or logic connector.
- USB and external 5 V must not back-feed each other. Placement v0.6 uses a
  manual `JP1 EXT POWER ENABLE` interlock: normal Orange Pi/USB operation keeps
  JP1 open; alternate regulated J1 power requires USB to be physically
  unplugged before JP1 is fitted. U6 is a TPS25947-family protection candidate,
  but its values and suffix remain blocked by load/transient measurements.
- Add input fuse coordination, reverse-polarity protection, transient/ESD
  protection, bulk capacitance, and local decoupling after exact loads and
  connectors are selected.
- Use a continuous ground reference for logic while keeping switcher and
  high-current return loops away from sensor paths.
- Keep the ESP32 module antenna at the PCB edge with copper, components, and
  enclosure metal outside its antenna keep-out.

## High-Current Measurement Boundary

The INA260 supports the planned DC voltage range, but the carrier PCB shall not
automatically route battery or solar current through ordinary 0.1-inch module
headers. Use the breakout's rated high-current terminals or a separately
reviewed high-current section. Confirm continuous current, terminal rating,
trace width, copper weight, temperature rise, fuse rating, and fault current
before routing `VIN+` and `VIN-`.

Keep these two measurement paths physically and electrically distinct:

- `INA260 BAT` at address `0x40` for the defined battery/load branch; and
- `INA260 SOLAR` at address `0x41` for the defined panel/charger branch.

The exact locations relative to the MPPT must be marked on the final schematic,
because moving either sensor changes what its voltage, current, and power values
mean.

## Open Items That Block Schematic Release

| Priority | Required decision or evidence | Why it blocks release |
| --- | --- | --- |
| High | Receive and 1:1-check Espressif ESP32-DevKitC V4 with ESP32-WROOM-32E | Exact official reference is locked, but delivered board/revision and headers still require physical confirmation |
| Critical | Exact 5 V buck models and output-current/ripple test | Defines input connector, protection, thermal area, and power quality |
| Critical | Exact MPPT, battery BMS, panel Voc/Isc, and load-current measurements | Required for correct fusing and current-monitor topology |
| Critical | Connector family, pin count, current rating, waterproofing method, and keying | Prevents reversed sensors and unsafe power connections |
| Critical | Receive and bench-test two NF-A8 5V PWM candidates: startup current, rail transient, 25 kHz PWM, independent tach, and enclosure environment | Required to release the open-drain PWM/load-enable stages and dual four-pin connectors |
| Critical | Leak/tamper sensor electrical output | GPIO32 interface and protection cannot be designed from a placeholder |
| High | Photos/revisions and dimensions for every breakout | Required to create or verify module footprints |
| High | BNO085 physical mounting location and axis convention | Orientation is invalid if the board can flex or its axes are undocumented |
| High | Bar02 cable/connector and bulkhead implementation | Sensor rear and electronics require correct sealing and strain relief |
| High | Enclosure tray dimensions, mounting holes, lid clearance, and cable-gland positions | Defines board outline and connector placement |
| High | Total 3.3 V sensor current and ESP32 radio peak measurements | Determines whether an independent 3.3 V regulator is required |
| Medium | Test-point and status-LED policy | Needed for serviceability without creating unnecessary power draw |

## Required PCB Features

- Socketed ESP32 DevKit with accessible USB, EN, and BOOT controls.
- Labeled, keyed connectors with signal, voltage, and ground marked on silkscreen.
- Test points for 5 V, 3.3 V, GND, SDA, SCL, SPI signals, UART2, and protected inputs.
- External pull-ups for anemometer and DS18B20, with values shown on schematic.
- Address configuration that guarantees the second INA260 is `0x41`.
- MOSFET fan stage with a defined power-up-off state and load-appropriate protection.
- Sensor-line ESD/transient provisions selected for actual cable lengths and environment.
- Mounting holes and keep-outs that do not interfere with module undersides or antennas.
- No high-current path beneath the BNO085, ESP32 antenna, GPS antenna, or pressure-sensor interface.

## KiCad Release Sequence

1. Create the block schematic using module connectors and named power domains.
2. Enter exact manufacturer part numbers and connector pinouts.
3. Photograph and measure every purchased module; verify each footprint at 1:1 scale.
4. Complete electrical-rules checking with no unexplained errors.
5. Place connectors from the mechanical cable-gland plan, then sensitive sensors,
   controller, protection, and power stages.
6. Route low-voltage signals over a continuous ground reference; review antenna
   and high-current keep-outs.
7. Complete design-rule, clearance, polarity, address, and connector-keying reviews.
8. Print the board at 1:1 and physically place all modules before generating Gerbers.
9. Fabricate only a small bench revision first; do not deploy the first PCB at sea.

## Release Rule

The design may move from **pre-schematic** to **schematic draft** now, using
clearly marked placeholders. It may move to **fabrication candidate** only after
every Critical item is closed and the High items affecting footprints,
connectors, safety, and mechanical fit are verified.
