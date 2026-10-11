# Project FALCON Pressure Sensor Baseline and Alternatives

<!-- FALCON-DOST-REVISION-NOTE:START -->
> **Current revision note (2026-10-10):** Use the DOST major revision baseline in [`docs/REVISION_2026-10-10.md`](REVISION_2026-10-10.md) unless this file is explicitly archived. The active proposal core is a compact ESP32-based buoy with **water pressure sensing, wind speed/direction sensing, GPS for exact position and security, battery + solar power, and Wi-Fi/LTE internet communication**. LoRa, large Bay Station hardware, tall tower layouts, and continuous every-second uploads are legacy or optional fallback assumptions.
<!-- FALCON-DOST-REVISION-NOTE:END -->

Revision: 2.2
Date: 2026-10-10
Status: recommended field candidate with lower-cost alternatives; procurement, supplier confirmation, integration, and validation pending

## Decision

The recommended Phase 1 pressure sensor is a **low-range submersible water-level or pressure transmitter with 4–20 mA output**. For the revised compact buoy, the target range should be **0–1 mH2O** or **0–2 mH2O**, because shallow coastal wave work needs resolution. A high-range pump or automotive transducer may look cheaper but can waste resolution and may not solve underwater cable sealing.

The preferred procurement target remains a Holykell HPT604 Type A or equivalent continuous-submersion transmitter with:

- 4–20 mA two-wire output;
- 0–1 mH2O or 0–2 mH2O range after depth review;
- 316L stainless or confirmed marine-compatible wetted material;
- fixed waterproof cable, preferably vented gauge cable when using gauge measurement;
- IP68 or equivalent continuous-immersion statement;
- 7–30 V or 12 V-compatible loop supply;
- accuracy around ±0.5 percent full scale or better if budget allows.

This is a procurement target, not installed hardware. Before payment, the seller must confirm exact range, output, supply voltage, wetted materials, cable jacket, cable length, venting requirement, response time, overload, saltwater/continuous immersion suitability, and calibration certificate or test record.

## Current option matrix

| Option | Interface | Planning range | Recommended use | Decision rule |
| --- | --- | ---: | --- | --- |
| Generic low-range submersible transmitter | 4–20 mA | ₱1,997–₱3,444 | First low-cost field candidate | Accept only if range, wetted material, cable sealing, and continuous immersion are documented. |
| Holykell HPT604 Type A or equivalent quoted unit | 4–20 mA | Supplier quotation required; target below ₱10,000 sensor-only | Preferred documented industrial candidate | Accept if exact configuration and saltwater/material evidence fit the project budget. |
| Analog submersible transmitter | 0–5 V or 0–10 V | ₱1,500–₱4,500 | Backup if current-loop option is unavailable | Requires cable-noise test, input protection, and ADC scaling. |
| RS485/Modbus transmitter | RS485 digital | ₱2,500–₱6,000 | Backup for longer cable/digital integrity | Requires RS485 transceiver, protocol test, waterproof connector plan. |
| Blue Robotics Bar02/Bar30 or MS5837 board | I2C/digital | Higher-cost imported or bench module | Bench comparison and short supervised testing | Do not use as unattended baseline unless immersion limits and sealing are satisfied. |
| Ultrasonic/radar/float/camera | Non-pressure | TBD | Future research only | Changes the thesis method and requires a separate validation plan. |

## Why 4–20 mA is preferred

A 4–20 mA loop is practical for a buoy because it can tolerate longer cable runs and electrical noise better than a raw voltage or I2C line. It also gives a live-zero fault clue: around 4 mA means the sensor is alive at the low end; near 0 mA suggests broken wiring or power loss. The trade-off is that the buoy must include loop power, shunt resistor, ADC, protection, and calibration.

## Required ESP32 interface

```text
12 V protected supply
  -> fuse / reverse protection / surge protection
  -> 4–20 mA pressure transmitter loop
  -> 150 ohm 0.1 percent shunt resistor
  -> RC filter and clamp protection
  -> ADS1115 ADC at 3.3 V
  -> ESP32 I2C
```

With a 150 ohm shunt, 4 mA is about 0.60 V and 20 mA is about 3.00 V, which fits a 3.3 V ADC path when protected. The resistor should be at least 0.25 W after tolerance and fault review. The interface must be bench-tested with simulated 4 mA, 12 mA, and 20 mA signals before the real probe is connected.

## Validation tests

1. Static water-column test at 0, 25, 50, 75, and 100 cm or the selected range equivalent.
2. Increasing and decreasing depth run to check hysteresis.
3. Noise test while ESP32, LTE, GPS, wind sensor, and power system are active.
4. Small-wave/stilling-tube test to confirm the tube does not hide the signal needed for event detection.
5. Leak, cable strain, vent/desiccant, and saltwater exposure inspection.
6. Supervised 24-hour wet bench test before any field trial.
7. Controlled comparison against a reference water-level or pressure measurement before reporting estimated wave-height performance.

## Dashboard rule

The dashboard must show pressure-derived output as **Estimated wave height**, not measured wave height. It must keep raw loop current or pressure, calibration version, quality state, installation depth, and timestamp. Sensor failure must be `INVALID`, `STALE`, or `OFFLINE`, never zero.

## Source direction

- Shopee Philippines listing for 4–20 mA submersible water level transmitter, observed planning range ₱1,997–₱3,444: https://shopee.ph/Submersible-2-Liquid-Sensor-Tank-Pressure-4-20Ma-Hydrostatic-Water-River-Level-Transmitter-1-4-0M-i.1380515196.26470979857
- Shopee Philippines listing family for 1 m / 3 m / 5 m 4–20 mA hydrostatic level meter: https://shopee.ph/Water-Level-Transmitter-1m-3m-5m-Liquid-Water-Level-Sensor-4-20mA-Pool-Tank-Hydrostatic-Level-Meter-i.906740842.22061716970
- Holykell HPT604 Type A level sensor datasheet: https://www.holykell.com/wp-content/uploads/2023/08/HPT604A-Level-sensor-Datasheet-Holykell-V26-CS-1.pdf
- Blue Robotics Bar sensor guide: https://bluerobotics.com/learn/bar-sensors-guide/
- Makerlab PH wind speed sensor listing reference: https://makerlab.ph/products/anemometer-wind-speed-0-to-5v-analog
- SolarCalc PH catalog reference for local solar planning prices, including 100 W panel ₱2,200 as of 2026-03-15: https://solarcalcph.com/catalog/
- Spark Fruit PH 10 A solar charge controller listing: https://sparkfruit-ph.com/products/20a61c7d5de4e6d0f4c299f51d5bf970
- Shopee Philippines MPPT charge controller search reference, observed low-cost LiFePO4 MPPT listing around ₱847 in September 2026 crawl: https://shopee.ph/search?keyword=mppt+solar+charge+controller
