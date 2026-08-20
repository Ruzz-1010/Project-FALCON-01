# FALCON-01 Low-Voltage Carrier PCB

Status: **native KiCad pre-schematic and placement-zone draft; not approved for
fabrication**.

This KiCad project will implement a serviceable low-voltage carrier for the
ESP32 DevKit and selected sensor breakouts. It intentionally excludes the raw
12.8 V battery, solar-panel, MPPT, and high-current distribution paths.

## Board boundary

The board receives protected, regulated 5 V from the dedicated ESP32 buck
branch. It distributes 5 V, regulated 3.3 V, logic ground, and the validated
sensor buses. The Orange Pi retains its own 5 V supply and connects to the
ESP32 through USB during Phase 1.

High-current battery and solar conductors connect directly to the appropriately
rated INA260 breakout terminals outside the carrier copper path. Only INA260
logic power and I2C reach the carrier.

## Draft modules

- Socketed ESP32 DevKit / ESP-WROOM-32 class controller.
- Socketed Adafruit BNO085 SPI breakout.
- Bar02 I2C connector.
- GPS UART connector.
- Separate battery and solar INA260 logic connectors.
- MCP9808 and ADS1115 module connectors.
- Wind-speed, wind-vane, optional DS18B20, and leak-sensor connectors.
- Fan MOSFET driver placeholder; component values remain TBD.
- Protected 5 V input and 3.3 V sensor-regulator placeholder.

## Mechanical starting envelope

The current control deck is documented as 250 x 210 mm inside the latest
rectangular-pod concept. The first carrier outline shall be no larger than
200 x 160 mm, leaving service and connector clearance. This is a planning
envelope only: mounting-hole coordinates and final outline remain TBD until the
enclosure and modules are physically measured.

## Native KiCad files

Native KiCad 10 `.kicad_pro`, `.kicad_sch`, and `.kicad_pcb` files are present.
The board contains a 200 x 160 mm planning outline and labeled placement zones,
not final footprints or routing. Do not manufacture from placeholder geometry
or exported pictures.

Schematic v0.1 contains the ESP32 carrier interface, BNO085 SPI, shared I2C
modules, GPS UART, wind inputs, optional DS18B20, leak placeholder, fan-driver
placeholder, protected 5 V input, 3.3 V regulator placeholder, and required
wind/OneWire pull-ups. Connections use validated named nets and pass KiCad 10
ERC with zero errors and warnings. `generate_schematic.py` reproducibly rebuilds
the native schematic and its project symbol library; do not hand-edit generated
symbol geometry without updating the generator.

PCB placement v0.2 contains provisional through-hole module/socket envelopes,
named-net pads, four provisional M3 mounting holes, and an ESP32 antenna
keep-out. `generate_pcb.py` reproducibly builds this placement. The current DRC
result is **zero geometry/rule violations and 64 expected unconnected ratsnest
items**. Those connections must remain visible until deliberate copper routing;
they are not to be suppressed or described as a finished PCB.

Placement v0.3 reorganizes the same validated nets into professional functional
zones: field connectors on the left service edge, I2C modules in an addressable
distribution column, pull-ups beside their inputs, BNO085/GPS in the quiet
control area, ESP32 at the antenna edge, and power/fan/service components at the
bottom right. This reduces ratsnest crossing before routing without pretending
that the provisional footprints are final.

Reference map:

| Reference | Function |
| --- | --- |
| U1 | 5 V to 3.3 V regulator placeholder |
| U2 | ESP32 DevKit carrier interface |
| U3 | BNO085 SPI breakout |
| U4 | ADS1115 wind-vane ADC |
| U5 | Fan MOSFET-driver placeholder |
| J1 | Protected 5 V input |
| J2–J6 | Bar02, GPS, two INA260 logic links, MCP9808 |
| J7–J10 | Anemometer, wind vane, DS18B20, leak sensor |
| J11–J12 | Fan and service I2C |
| R1–R2 | Wind-pulse 10 kOhm and OneWire 4.7 kOhm pull-ups |
| H1–H4 | Provisional M3 mounting holes |

Every footprint outline, header spacing, mounting hole, and connector remains
provisional until checked against the purchased hardware on a 1:1 print.

The next release gate is [FOOTPRINT_VALIDATION.md](FOOTPRINT_VALIDATION.md).
Record measurements in `footprint_measurements.csv`; do not start final copper
routing while the critical rows remain `PENDING`.

Use these source registers during capture:

- [NET_REGISTER.csv](NET_REGISTER.csv)
- [CONNECTOR_REGISTER.md](CONNECTOR_REGISTER.md)
- [DESIGN_RULES.md](DESIGN_RULES.md)
- [`docs/PCB_VALIDATION_REGISTER.md`](../../../docs/PCB_VALIDATION_REGISTER.md)

## Release gates

1. Record exact board revisions, dimensions, and pin labels.
2. Close every Critical item in `docs/PCB_VALIDATION_REGISTER.md`.
3. Verify source selection prevents USB/external-5V backfeed.
4. Pass ERC with every exception documented.
5. Print footprints at 1:1 and place the actual modules on the print.
6. Pass DRC and an independent connector/polarity review.
7. Assemble and test one protected bench prototype before any marine trial.
