# Project FALCON System Test Plan v8.0


<!-- FALCON-DOST-REVISION-NOTE:START -->
> **Current revision note (2026-10-10):** Use the DOST major revision baseline in [`docs/REVISION_2026-10-10.md`](REVISION_2026-10-10.md) unless this file is explicitly archived. The active proposal core is a compact ESP32-based buoy with **water pressure sensing, wind speed/direction sensing, GPS for exact position and security, battery + solar power, and Wi-Fi/LTE internet communication**. LoRa, large Bay Station hardware, tall tower layouts, and continuous every-second uploads are legacy or optional fallback assumptions.
<!-- FALCON-DOST-REVISION-NOTE:END -->

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
- LTE coverage/peak-power, event-upload latency, outage, buffering, reconnect and endurance results;
- cloud synchronization, remote-access, data-usage, and Internet-outage results;
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
