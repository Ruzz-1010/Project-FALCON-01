# FALCON-01 Plug-and-Play Sensor Harness Plan

Status: **presentation and prototype assembly baseline; verify every received
cable by continuity before power**. Updated 2026-08-21.

## Service concept

All field-sensor cables terminate in removable keyed plugs inside the dry
electronics enclosure. The PCB headers are soldered once during assembly; no
sensor cable should be soldered directly to the carrier. Disconnect power,
release the latch, and pull the housing—not the wires—during maintenance.

J2 and J7–J10 are grouped on the left service edge as top-entry JST GH headers.
This permits removal after opening the enclosure lid while keeping cable bends
away from the BNO085, GPS antenna, fan PWM section, and power protection block.

## Connector schedule

| Ref | Service | PCB header | Plug housing | Circuits | Cable label |
| --- | --- | --- | --- | ---: | --- |
| J2 | Historical Bar02 pressure | `BM04B-GHS-TBT` | `GHR-04V-S` | 4 | OBSOLETE; replace with HPT604 4–20 mA loop termination |
| J7 | Anemometer | `BM03B-GHS-TBT` | `GHR-03V-S` | 3 | `WIND-SPD` |
| J8 | Wind vane | `BM03B-GHS-TBT` | `GHR-03V-S` | 3 | `WIND-DIR` |
| J9 | DS18B20 water temperature | `BM03B-GHS-TBT` | `GHR-03V-S` | 3 | `WATER-T` |
| J10 | Leak detector | `BM03B-GHS-TBT` | `GHR-03V-S` | 3 | `LEAK-01` |

Use genuine compatible crimp contacts for the selected conductor size. JST GH
is a small 1.25 mm family; use an approved production crimp tool or purchase
pre-crimped leads. Do not crush contacts using ordinary pliers.

## Pin and wire schedule

| Ref | Pin 1 | Pin 2 | Pin 3 | Pin 4 |
| --- | --- | --- | --- | --- |
| J2 historical Bar02 | Red — `3V3/VIN` | Green — `SCL` | White — `SDA` | Black — `GND`; DO NOT USE FOR HPT604 |
| J7 wind speed | Red — `3V3` reserved | Yellow — `WIND_PULSE` | Black — `GND` | — |
| J8 wind direction | Red — `3V3` | Blue — `WIND_VANE` | Black — `GND` | — |
| J9 water temperature | Red — `3V3` | Yellow — `WATER_TEMP/DQ` | Black — `GND` | — |
| J10 leak | Red — `3V3` | White — `LEAK_SIGNAL` | Black — `GND` | — |

Bar02 colors document the historical cable only. HPT604 conductor colors and polarity must come from the exact delivered datasheet and receiving inspection. Colors for J7–J10 are the
carrier harness convention, not proof of a sensor's delivered wire function.
The exact leak sensor remains TBD; do not energize J10 until its output type and
voltage have been verified.

The SparkFun anemometer reed switch may use only pulse and ground. In that case,
leave J7 pin 1 unpopulated in the cable housing; never short it to another pin.

## Physical construction

- Use adhesive heat-shrink labels at both ends with reference and function.
- Keep exposed conductor outside the crimp wings to the contact specification.
- Add strain relief before each enclosure gland; the PCB header carries no cable load.
- Route pressure/I2C and pulse/signal harnesses away from fan and power loops.
- Provide a service loop without exceeding the enclosure bend radius.
- Use one gland/sealed bulkhead strategy per external cable; JST GH is an
  internal connector and is not the marine waterproof boundary.
- Add a mating-view drawing to every fabricated harness traveler.

## Mandatory tests

1. Inspect contact lock, housing latch, pin 1, and wire color.
2. Continuity-test every pin end-to-end with both ends disconnected.
3. Confirm no shorts between adjacent pins or any pin and shield/enclosure.
4. Perform a gentle pull test on every crimp and strain relief.
5. Energize first using a current-limited bench supply.
6. Record a photo of the connector mating face and completed cable label.

## Primary reference

- [JST GH connector family](https://www.jst-mfg.com/product/pdf/eng/eGH.pdf)
