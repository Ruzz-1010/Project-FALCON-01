# Sensor Specification

## Purpose
Define selection, validation, calibration, and reporting rules for sensors.

## Scope
Environmental, motion, GPS, power, and safety measurements.

## Current Status
No sensor is implemented; dashboard sensor-facing values are simulated.

## Architecture
Driver -> validation -> calibration/unit conversion -> canonical state -> API/logging/future AI.

## Implementation
| Measurement | Current state | Candidate direction |
| --- | --- | --- |
| Water temperature | Simulated | Waterproof DS18B20-class probe |
| Tilt/motion | Simulated | Suitable IMU; model not finalized |
| GPS | Placeholder | Suitable receiver; model not finalized |
| Battery/solar | Simulated/placeholder | Voltage/current monitor |
| Security | Placeholder | GPS/IMU/leak/tamper fusion |

Selection requires marine suitability, range, accuracy, calibration, voltage, power, bus, cabling, maintenance, and detectable fault states.

## Future Expansion
pH, salinity, turbidity, dissolved oxygen, weather, and waterline sensing require scope approval.

## Engineering Notes
IMU-derived activity is not validated wave height. AI requires time-aligned labeled data.

## Revision History
| Version | Date | Change |
| --- | --- | --- |
| 1.0 | 2026-08-05 | Initial sensor requirements. |
