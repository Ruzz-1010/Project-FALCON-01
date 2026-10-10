# Connector Selection Baseline


<!-- FALCON-DOST-REVISION-NOTE:START -->
> **Current revision note (2026-10-10):** Use the DOST major revision baseline in [`docs/REVISION_2026-10-10.md`](../../../docs/REVISION_2026-10-10.md) unless this file is explicitly archived. The active design is a compact single-tube / small-buoy, ESP32-based, event-driven, cloud-first system. LoRa, large Bay Station hardware, tall tower layouts, and continuous every-second uploads are legacy or optional fallback assumptions.
<!-- FALCON-DOST-REVISION-NOTE:END -->

Status: **engineering baseline for footprint capture; receiving and harness
validation still required**. Updated 2026-08-21.

PCB footprint status: JST GH and VH geometries are now generated from the
official catalog board-layout and dimensional drawings. They remain subject to
a printed 1:1 overlay and physical receiving inspection before fabrication.

## Selection rules

- PCB connectors stay inside the dry electronics enclosure; they are not the
  external waterproof boundary.
- Low-current sensor connectors use one pin order per circuit count so an
  accidental swap does not put supply voltage on a signal pin.
- Protected power and fan connectors use a larger family and different circuit
  counts to prevent cross-mating.
- External cables transition through separately selected sealed bulkhead
  pigtails or cable glands with strain relief.

## Locked internal families

| Service | PCB header baseline | Mating housing | Rating basis | Pin decision |
| --- | --- | --- | --- | --- |
| J1 protected 5 V | JST `B2P-VH-FB-B`, 2-pos., 3.96 mm, THT | `VHR-2N` | VH shrouded header: 7 A with AWG18 | 1 `+5V_PROTECTED`, 2 GND |
| J2 historical Bar02 R2 | JST `BM04B-GHS-TBT`, 4-pos., 1.25 mm, SMT | `GHR-04V-S` | OBSOLETE FOR DEPLOYMENT | Replace with keyed HPT604 two-wire loop termination after marine connector, cable vent, current-loop and enclosure review |
| J6 MCP9808 / J12 service I2C | JST `BM04B-GHS-TBT` | `GHR-04V-S` | GH: 1 A with AWG26 | 1 3V3, 2 SCL, 3 SDA, 4 GND |
| J7–J10 sensor inputs | JST `BM03B-GHS-TBT`, 3-pos. | `GHR-03V-S` | GH: 1 A with AWG26 | 1 3V3, 2 signal, 3 GND |
| J11/J13 fans | Molex `470531000`, 4-pos., 2.54 mm, THT | `470541000` baseline | 4-wire fan interface | 1 GND, 2 5 V, 3 independent tach, 4 independent open-drain PWM |

J1 and the fan outputs use different families/circuit counts. Silkscreen must
show reference, pin 1, voltage, signal names, and mating direction. See
`FAN_SELECTION_BASELINE.md` for the current dual-fan interface decision.

## External enclosure boundary

An M8 A-coded sealed pigtail is a candidate for three- or four-wire field
sensors. TE Connectivity offers keyed panel-mount M8 IP67 variants. IP67 is only
a splash-exposure starting point, not approval for continuous submersion. Final
selection must match cable diameter, panel thickness, salt/UV exposure, mating
cycles, and required IP rating. The former Bar02 M10×1.5 arrangement is historical; the exact HPT604 probe/cable and dry vent termination control the revised mechanical interface.

## Official references

- [JST GH family](https://www.jst-mfg.com/product/index.php?lang=2&series=105)
- [JST GH catalog](https://www.jst-mfg.com/product/pdf/eng/eGH.pdf)
- [JST VH family](https://www.jst-mfg.com/product/index.php?lang=2&series=262)
- [JST VH catalog](https://www.jst-mfg.com/product/pdf/eng/eVH.pdf)
- [TE M8 panel-mount family](https://www.te.com/en/product-CAT-C73765-M1B.html)

## Gates before footprint release

1. Confirm authorized-source availability of headers, housings, and contacts.
2. Match contact crimp range to the selected wire gauge and tooling.
3. Crimp sample harnesses and perform continuity and pull tests.
4. Check header height, cable bend radius, and unplugging space against the lid.
5. Perform deliberate wrong-connector trials before applying power.
6. Record photos and 1:1 results in `footprint_measurements.csv`.
