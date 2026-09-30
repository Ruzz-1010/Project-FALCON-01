# Calibration Guide v7.0

> Use the exact procedures, proposed acceptance limits and recording sheets in [SENSOR_VALIDATION_AND_CALIBRATION_PLAN.md](SENSOR_VALIDATION_AND_CALIBRATION_PLAN.md). Water temperature, conductivity/salinity, and required IMU alignment are excluded from the Phase 1 measurement scope; calibration focuses on pressure-derived wave estimation, wind, supporting telemetry, and security behavior.

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

## Required Calibration Set

- Bar02 static air/depth points, independent verification and controlled dynamic wave scenarios;
- Celsius R2 three-point temperature comparison and installation leak test;
- MCP9808 enclosure reference comparison and placement-bias test;
- wind-speed reference comparison and wind-direction code/alignment map;
- GPS stationary scatter and evidence-based geofence/persistence values;
- battery and solar INA260 comparison at idle, normal and near-maximum project load;
- enclosure-contact and optional tamper false-alarm trials;
- separate AI model evaluation using chronological held-out data.

## Engineering Notes
Store coefficients outside code when persistent configuration exists. Never tune values only to improve appearance.

## Revision History
| Version | Date | Change |
| --- | --- | --- |
| 7.0 | 2026-08-31 | Adopted the formal sensor validation plan and corrected marine water-temperature scope. |
| 1.0 | 2026-08-05 | Initial calibration policy. |
