# Project FALCON Sensor Selection and Architecture Baseline

Revision: 2.0  
Date: 2026-10-09  
Status: event-driven cloud buoy baseline; not yet a fabrication or deployment release

## 1 Purpose

This document defines a low-cost sensor scope for a smaller single-tube buoy. The ESP32 samples locally, calculates short-window summaries and event states, and transmits through Wi-Fi for laboratory work or 4G/LTE for a remote field trial. The core research signal is pressure-derived wave estimation. Wind, GPS, temperature, and security channels are supporting or optional channels and require adviser confirmation.

## 2 System signal flow

```text
Marine environment
  -> pressure sensor and optional wind sensor
  -> protected interface
  -> ESP32 local sampling and event detection
  -> local flash/microSD buffer
  -> Wi-Fi (lab) or 4G/LTE (field)
  -> cloud API/database/dashboard
```

The ocean is always moving, so the system must not treat every individual wave as a network event. The ESP32 samples continuously, sends one-minute summaries every 1–5 minutes, and sends immediate packets only for material changes or system faults.

## 3 Selection status

- **Recommended field candidate** — technically appropriate but procurement and field validation remain pending.
- **Low-cost alternative** — may reduce cost but must pass the same range, sealing, seawater, and calibration gates.
- **Bench only** — acceptable for software or short supervised tests, not unattended deployment.
- **Optional** — not required for the minimum pressure-monitoring claim.
- **TBD** — no exact product is approved.

## 4 Sensor and interface decisions

| Function | Preferred | Lower-cost or alternate option | Required validation |
| --- | --- | --- | --- |
| Submerged pressure / wave input | Low-range 4–20 mA submersible transmitter; Holykell HPT604 Type A remains a candidate | 0–5 V/0–10 V transmitter, RS485/Modbus transmitter, Blue Robotics Bar sensor, or Bar02 bench sensor | Range versus depth/tide, wetted material, cable sealing, continuous seawater suitability, five-point calibration, dynamic reference comparison |
| Movement and tilt event input | MPU6050/GY-521 | SW-420 vibration module or ball tilt switch | Baseline motion, threshold, debounce, false-event behavior |
| Wind speed | Pulse-output cup anemometer | DIY reed-switch cup anemometer | Reference anemometer comparison and local calibration |
| Wind direction | Combined vane/anemometer | Potentiometer wind vane | Direction reference and deadband testing |
| Position and time | NEO-6M GPS | Omit from bench prototype | Fix quality, scatter, geofence persistence, privacy |
| Power state | INA219 voltage/current monitor | Voltage divider plus measured load test | Calibrated meter comparison and modem peak capture |
| Water temperature | DS18B20 waterproof probe | NTC waterproof probe | Optional context only; not a primary research result |
| Enclosure security | Reed switch | SW-420 vibration input | Lid-open detection, debounce, and ordinary-wave false positives |
| Local buffer | microSD | ESP32 flash ring buffer | Outage duration, wear behavior, timestamp preservation |
| Cloud link | 4G/LTE modem with antenna and SIM | Wi-Fi for laboratory/near-shore testing | Coverage, registration, data use, reconnect, TLS/API or MQTT behavior |

## 5 Water-pressure alternatives

### A 4–20 mA submersible transmitter

Preferred field interface because it tolerates long cables and electrical noise. It requires protected loop power, a precision shunt, ADC, and a confirmed vented or sealed installation.

### B 0–5 V or 0–10 V transmitter

Simpler wiring but more sensitive to cable voltage drop and noise. It requires voltage scaling and input protection so the signal cannot exceed the ESP32/ADC limit.

### C RS485/Modbus transmitter

Digital and useful for long cable runs. It requires an RS485 transceiver, protocol handling, device addressing, and stronger integration effort.

### D Marine digital pressure sensor

A marine-oriented digital sensor may improve documentation and integration. It is typically more expensive and must still be checked for the actual depth range and continuous deployment conditions.

### E Bar02

Useful for bench comparison and short supervised water tests. It must not be treated as the unattended field baseline unless its immersion and drying requirements are satisfied.

### F Protective stilling tube or chamber

A stilling tube can reduce turbulence and mechanical impact around a pressure sensor. It does not replace a suitable pressure sensor and may attenuate fast wave changes, so its response must be tested.

## 6 Release rule

No sensor is final until the exact model, datasheet, supplier, price, wiring, protection, calibration method, invalid/stale behavior, and physical test evidence are recorded. A low marketplace price is not evidence of continuous marine suitability.

