# Draft PCB Design Rules


<!-- FALCON-DOST-REVISION-NOTE:START -->
> **Current revision note (2026-10-10):** Use the DOST major revision baseline in [`docs/REVISION_2026-10-10.md`](../../../docs/REVISION_2026-10-10.md) unless this file is explicitly archived. The active design is a compact single-tube / small-buoy, ESP32-based, event-driven, cloud-first system. LoRa, large Bay Station hardware, tall tower layouts, and continuous every-second uploads are legacy or optional fallback assumptions.
<!-- FALCON-DOST-REVISION-NOTE:END -->

These constraints are conservative starting points for the low-voltage carrier,
not substitutes for the selected PCB manufacturer's capabilities.

## Stack-up and geometry

- Two-layer FR-4 prototype, 1.6 mm nominal thickness, 1 oz copper minimum.
- Continuous ground pour on the bottom layer; avoid fragmenting return paths.
- Default signal trace: 0.25 mm minimum.
- 3.3 V and low-current 5 V distribution: begin at 0.50 mm and recalculate from
  measured current, temperature rise, copper weight, and length.
- Default clearance: 0.25 mm minimum; increase around external connectors and
  contaminated/moisture-prone regions.
- No raw battery, panel, or MPPT high-current routing on this carrier revision.

## Placement

- ESP32 antenna at the board edge. No copper, traces, components, fasteners, or
  enclosure metal inside the module manufacturer's antenna keep-out.
- BNO085 on a rigid area, with X/Y axes printed, away from fans, magnets,
  inductors, high-current loops, and loose cables.
- GPS antenna and receiver kept away from switching regulators and the ESP32 antenna.
- MCP9808 kept away from the ESP32, Orange Pi airflow, regulator, MOSFET, and fan exhaust.
- External connectors grouped at an accessible service edge with strain relief.
- Put protection close to the connector it protects.

## Interfaces and protection

- Audit parallel I2C pull-ups fitted on every breakout before choosing carrier pull-ups.
- Reserve optional series damping footprints on off-board SPI/I2C/UART signals.
- Add connector-side ESD/TVS only after its capacitance, clamping behavior, and
  cable exposure are checked for the relevant bus.
- Fan gate needs a series resistor and pull-down so the fan remains off during boot.
- Fit load-appropriate flyback protection for an inductive two-wire fan unless
  the selected fan/driver topology proves it unnecessary.
- USB and external 5 V are mutually exclusive for the DevKitC V4. Keep JP1
  `EXT POWER ENABLE` open during normal USB operation; fit it only with USB
  physically unplugged. An input eFuse does not by itself prevent external 5 V
  from backfeeding the DevKit USB connector.

## Review requirements

- ERC: no unexplained power, output-to-output, or unconnected-pin warnings.
- DRC: zero unresolved clearance, courtyard, hole, and board-edge violations.
- Verify every connector pin from source datasheet to schematic, footprint,
  harness drawing, and silkscreen.
- Verify all footprints on a 1:1 paper print using the actual modules.
- Add test points for both rails, ground, I2C, SPI, UART2, and external inputs.
