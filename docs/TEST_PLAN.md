# Project FALCON System Test Plan v7.1

> The detailed sensor procedures, proposed acceptance limits, recording sheets, integrated scenarios and deployment gates are authoritative in [SENSOR_VALIDATION_AND_CALIBRATION_PLAN.md](SENSOR_VALIDATION_AND_CALIBRATION_PLAN.md). The DS18B20 is bench-only; Celsius R2 is the recommended marine water-temperature candidate. Mandatory IMU testing remains removed.

## Purpose
Define repeatable acceptance evidence.

## Scope
Repository, builds, filesystem, device startup, AP, portal, API, UI, controls, and future hardware.

## Current Status
Firmware and LittleFS builds have passed previously. Automated unit/browser tests and physical sensor validation remain incomplete. No simulated result may be recorded as physical calibration evidence.

## Architecture
Static checks -> build -> bench -> client matrix -> endurance -> future field tests.

## Implementation
- Run `git diff --check` and Markdown link validation.
- Run `platformio run` and `platformio run --target buildfs`.
- Verify asset startup message, AP visibility, address assignment, portal/manual URL, all assets, JSON fields, toggle, restart, reconnect, and a 30-minute polling soak.
- Test at least Android and laptop clients; record OS/browser, automatic/manual portal, responsive layout, and caching.

## Required Evidence

- repository/build checks and automated unit/API/browser tests;
- per-sensor identity, disconnect, recovery, reference-comparison and calibration records;
- pressure-to-wave controlled scenarios and independent reference comparison;
- GPS scatter/geofence persistence and security false-alarm trials;
- LTE peak-power, outage, buffering, reconnect and endurance results;
- required AI persistence baseline, chronological held-out evaluation and failure isolation;
- ingress, thermal, power-autonomy, stability and supervised field evidence;
- dashboard usability testing with representative older/non-technical operators.

Future camera, communications, sensor, or Raspberry Pi upgrades require their own
regression, bandwidth, privacy/security, calibration, thermal, power, endurance,
and supervised field evidence. See [`FUTURE_UPGRADES.md`](FUTURE_UPGRADES.md).

## Engineering Notes
A compile is not device validation. Record date, hardware revision, commit, operator, environment, and result.

## Revision History
| Version | Date | Change |
| --- | --- | --- |
| 7.1 | 2026-08-31 | Linked the formal sensor validation/calibration protocol and corrected the water-temperature baseline. |
| 1.0 | 2026-08-05 | Initial test plan. |
