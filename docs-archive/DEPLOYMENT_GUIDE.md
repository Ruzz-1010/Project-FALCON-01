# Deployment Guide


<!-- FALCON-DOST-REVISION-NOTE:START -->
> **Current revision note (2026-10-10):** Use the DOST major revision baseline in [`docs/REVISION_2026-10-10.md`](REVISION_2026-10-10.md) unless this file is explicitly archived. The active proposal core is a compact ESP32-based buoy with **water pressure sensing, wind speed/direction sensing, GPS for exact position and security, battery + solar power, and Wi-Fi/LTE internet communication**. LoRa, large Bay Station hardware, tall tower layouts, and continuous every-second uploads are legacy or optional fallback assumptions.
<!-- FALCON-DOST-REVISION-NOTE:END -->

> **No deployment is authorized from the current reference geometry.** Revalidate this guide against the approved replacement prototype, exact hardware, risk assessment, and controlled-test evidence before field use.

> Phase 1 uses passive mooring with adequate line scope. Set the surveyed geofence, calibrate pressure at measured depth, test security debounce, and verify data labels. No load-cell connection is used.

## Purpose
Define software deployment and future field gates.

## Scope
Build, firmware/filesystem flash, bench acceptance, and marine readiness.

## Current Status
Bench deployment is supported; marine deployment is not approved.

## Architecture
Source -> firmware/LittleFS builds -> both flashes -> bench acceptance -> client matrix -> future field gate.

## Implementation
Close serial monitor; run `platformio run`, `platformio run --target buildfs`, `platformio run --target upload`, and `platformio run --target uploadfs`. Use BOOT when required, then release it and press EN. Verify serial, AP, portal, API, controls, and record the Git commit.

Marine use additionally requires mechanical calculations, power/protection review, ingress testing, sensor calibration, mooring/stability tests, endurance tests, and emergency/maintenance plans.

## Future Expansion
Add signed artifacts, rollback, provisioning, deployment coordinates, and maintenance schedules.

Future camera, modem, additional-sensor, or Raspberry Pi deployments must repeat
the relevant power, thermal, ingress, calibration, privacy/security, recovery,
and supervised sea-trial gates. See
[`FUTURE_UPGRADES.md`](FUTURE_UPGRADES.md).

## Engineering Notes
The maintenance dashboard does not prove marine readiness.

## Revision History
| Version | Date | Change |
| --- | --- | --- |
| 1.0 | 2026-08-05 | Initial deployment gates. |
