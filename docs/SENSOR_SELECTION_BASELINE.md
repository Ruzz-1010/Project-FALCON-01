# Project FALCON Sensor Selection and Architecture Baseline

<!-- FALCON-DOST-REVISION-NOTE:START -->
> **Current revision note (2026-10-10):** Use the DOST major revision baseline in [`docs/REVISION_2026-10-10.md`](REVISION_2026-10-10.md) unless this file is explicitly archived. The active proposal core is a compact ESP32-based buoy with **water pressure sensing, wind speed/direction sensing, GPS for exact position and security, battery + solar power, and Wi-Fi/LTE internet communication**. LoRa, large Bay Station hardware, tall tower layouts, and continuous every-second uploads are legacy or optional fallback assumptions.
<!-- FALCON-DOST-REVISION-NOTE:END -->

Revision: 2.2
Date: 2026-10-10
Status: event-driven cloud buoy baseline; not yet a fabrication or deployment release

## 1 Purpose

This document defines the approved proposal-stage sensor scope for the revised compact buoy. The system must remain simple, low-cost, and event-driven. The core measurement is water pressure for estimated wave behavior. Wind, GPS/security, battery/solar status, and internet communication are required supporting channels because they explain the sea condition, locate the buoy, protect the device, and make cloud upload possible.

## 2 System signal flow

```text
Marine environment
  -> water pressure sensor + wind speed/direction + GPS/security + power monitor
  -> protected interfaces
  -> ESP32 local sampling, filtering, validation, and event detection
  -> local flash/microSD buffer when offline
  -> Wi-Fi for lab/near-shore tests or 4G/LTE for remote field trial
  -> cloud API/database/dashboard
```

The ocean is never still. The ESP32 should sample locally, filter noise, and classify events. It should upload normal summaries every 1–5 minutes and send immediate packets only for material changes such as abnormal pressure trend, strong wind change, drift/geofence event, tamper/open enclosure, low battery, or communication recovery.

## 3 Required core channels

| Channel | Baseline choice | Alternate choices | Status | What must be proven |
| --- | --- | --- | --- | --- |
| Water pressure | Low-range 4–20 mA submersible pressure/level transmitter, 0–1 mH2O or 0–2 mH2O preferred | 0–5 V/0–10 V transmitter, RS485/Modbus transmitter, Blue Robotics Bar sensor for supervised tests | Core, highest priority | Correct range, continuous immersion, saltwater/wetted material evidence, sealed cable, calibration curve, wave-response test |
| Wind speed | Cup anemometer, pulse/analog/RS485 depending on chosen sensor | DIY reed-switch cup sensor for bench comparison | Core | Reference anemometer comparison, startup threshold, gust response, mounting vibration |
| Wind direction | Matched vane or combined wind sensor | Potentiometer vane | Core | Direction map, deadband, north alignment, mounting offset |
| GPS position/security | NEO-6M or equivalent GNSS board | LTE module with GNSS if available; bench simulation only for software | Core support | Fix quality, drift radius, geofence persistence, timestamp, antenna placement |
| Internet/cloud | Wi-Fi for lab; A7670E/SIM7600 LTE for field | LoRa fallback to shore receiver | Core path | Coverage, current peaks, reconnect, data use, secure API/MQTT behavior |
| Battery/solar state | INA219/INA260 or measured voltage divider + current test points | Manual meter readings during early bench work | Core support | Battery voltage accuracy, modem peak capture, charge/discharge trend |
| Local buffer | microSD or ESP32 flash ring buffer | Cloud-only for bench demo | Required for remote field trial | Timestamp preservation, retry behavior, no duplicate packets |

## 4 Optional or deferred sensors

| Sensor | Recommendation | Reason |
| --- | --- | --- |
| MPU6050/GY-521 accelerometer | Optional event/security input | Useful for tilt, motion, or tamper events, but not a replacement for pressure sensing. |
| SW-420 vibration module or reed switch | Optional low-cost tamper input | Simple trigger only; high false positives are possible in waves. |
| DS18B20 waterproof temperature probe | Optional context | Helpful context but not part of the minimum wave/wind claim. |
| Salinity, pH, dissolved oxygen, turbidity | Defer | These add calibration, cleaning, fouling, and maintenance requirements outside the low-cost Phase 1 scope. |
| Camera | Defer | Adds power, data, waterproofing, and privacy complexity. |
| Raspberry Pi or mini PC on buoy | Exclude from minimum build | Too much power and enclosure burden for the revised compact buoy. |

## 5 Water-pressure alternatives

### A 4–20 mA submersible transmitter

Recommended field candidate. The current loop is better suited to cable runs and noisy marine electronics than exposed I2C. It needs 12 V loop power, a precision shunt, ADC, input protection, and written confirmation of continuous immersion and materials.

### B 0–5 V or 0–10 V submersible transmitter

Potentially cheaper and easier to explain, but more sensitive to voltage drop and noise. It needs scaling and protection so the ADC cannot be overdriven.

### C RS485/Modbus transmitter

Strong for cable distance and digital integrity. It adds protocol work, addressing, waterproof connector decisions, and software validation.

### D Blue Robotics Bar02/Bar30 or MS5837 module

Useful for bench comparison and short supervised tests. It should not be the default unattended field baseline unless the exact model and deployment schedule satisfy its immersion requirements.

### E Non-pressure alternatives

Ultrasonic, radar, float, or camera-based wave measurement can be researched as future alternatives, but they change the mechanical design and validation method. They should not replace the pressure channel in the current low-cost proposal.

## 6 Release rule

No sensor is final until the exact model, datasheet, supplier, price, wiring, protection, calibration method, invalid/stale behavior, and physical test evidence are recorded. Low price is useful, but it is not proof of seawater suitability or measurement accuracy.

## 7 Source direction

- Shopee Philippines listing for 4–20 mA submersible water level transmitter, observed planning range ₱1,997–₱3,444: https://shopee.ph/Submersible-2-Liquid-Sensor-Tank-Pressure-4-20Ma-Hydrostatic-Water-River-Level-Transmitter-1-4-0M-i.1380515196.26470979857
- Shopee Philippines listing family for 1 m / 3 m / 5 m 4–20 mA hydrostatic level meter: https://shopee.ph/Water-Level-Transmitter-1m-3m-5m-Liquid-Water-Level-Sensor-4-20mA-Pool-Tank-Hydrostatic-Level-Meter-i.906740842.22061716970
- Holykell HPT604 Type A level sensor datasheet: https://www.holykell.com/wp-content/uploads/2023/08/HPT604A-Level-sensor-Datasheet-Holykell-V26-CS-1.pdf
- Blue Robotics Bar sensor guide: https://bluerobotics.com/learn/bar-sensors-guide/
- Makerlab PH wind speed sensor listing reference: https://makerlab.ph/products/anemometer-wind-speed-0-to-5v-analog
- SolarCalc PH catalog reference for local solar planning prices, including 100 W panel ₱2,200 as of 2026-03-15: https://solarcalcph.com/catalog/
- Spark Fruit PH 10 A solar charge controller listing: https://sparkfruit-ph.com/products/20a61c7d5de4e6d0f4c299f51d5bf970
- Shopee Philippines MPPT charge controller search reference, observed low-cost LiFePO4 MPPT listing around ₱847 in September 2026 crawl: https://shopee.ph/search?keyword=mppt+solar+charge+controller
