# Test Plan

> Apply v6.2 gates: pressure reference accuracy, DS18B20 water-temperature reference comparison, geofence/tamper persistence and false alerts, five-page dashboard usability, required AI prediction output and failure isolation, and replacement-prototype fit/stability validation supersede mandatory IMU tests.

## Purpose
Define repeatable acceptance evidence.

## Scope
Repository, builds, filesystem, device startup, AP, portal, API, UI, controls, and future hardware.

## Current Status
Firmware and LittleFS builds pass. Automated unit/browser tests are absent.

## Architecture
Static checks -> build -> bench -> client matrix -> endurance -> future field tests.

## Implementation
- Run `git diff --check` and Markdown link validation.
- Run `platformio run` and `platformio run --target buildfs`.
- Verify asset startup message, AP visibility, address assignment, portal/manual URL, all assets, JSON fields, toggle, restart, reconnect, and a 30-minute polling soak.
- Test at least Android and laptop clients; record OS/browser, automatic/manual portal, responsive layout, and caching.

## Future Expansion
Add unit/API/browser tests, sensor faults, calibration, power endurance, GPS false-alert analysis, storage limits, AI metrics, ingress, stability, and marine trials.

Future camera, communications, sensor, or Raspberry Pi upgrades require their own
regression, bandwidth, privacy/security, calibration, thermal, power, endurance,
and supervised field evidence. See [`FUTURE_UPGRADES.md`](FUTURE_UPGRADES.md).

## Engineering Notes
A compile is not device validation. Record date, hardware revision, commit, operator, environment, and result.

## Revision History
| Version | Date | Change |
| --- | --- | --- |
| 1.0 | 2026-08-05 | Initial test plan. |
