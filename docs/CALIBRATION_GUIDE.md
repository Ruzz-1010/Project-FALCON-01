# Calibration Guide v6.1

> Current priorities are pressure baseline/depth/reference comparison, DS18B20 reference comparison, GPS geofence accuracy/persistence, wind/power calibration, and tamper false-alert testing. Conductivity/salinity is excluded from required Phase 1 work. IMU alignment is optional legacy work.

## Purpose
Define traceable calibration for future measurements.

## Scope
Environmental, motion, GPS, power, safety, and AI input quality.

## Current Status
No physical sensor exists; simulated values cannot be calibrated.

## Architecture
Reference -> repeated raw samples -> coefficient/model -> independent verification -> versioned record.

## Implementation
Future records must include sensor identity, firmware commit, reference instrument, environmental conditions, raw samples/timestamps, method, coefficients, uncertainty, acceptance limits, verification data, operator, date, and due date. Test range, repeatability, disconnect state, and recovery.

## Future Expansion
Add approved procedures for selected pressure and water-temperature sensors, GPS reference, wind, voltage/current, security inputs, and optional model normalization.

## Engineering Notes
Store coefficients outside code when persistent configuration exists. Never tune values only to improve appearance.

## Revision History
| Version | Date | Change |
| --- | --- | --- |
| 1.0 | 2026-08-05 | Initial calibration policy. |
