# User Manual

## Purpose
Explain current offline dashboard operation.

## Scope
Wi-Fi connection, portal access, readings, controls, and limitations.

## Current Status
Applies to dashboard v2.1 with simulated sensor values.

## Architecture
Phone/laptop connects directly to ESP32; no router, internet, cloud, account, or app is required.

## Implementation
1. Power ESP32 and wait 5-10 seconds.
2. Join `FALCON-01` using `falcon123` and accept no-internet mode.
3. Use captive portal or `http://192.168.4.1`.
4. Read online state, clients, uptime, and clearly labeled demo values.
5. Monitoring toggle changes temporary state only; restart temporarily disconnects Wi-Fi.

## Future Expansion
Add settings, history, export, alerts, calibration, and real sensor interpretation when implemented.

## Engineering Notes
Never use demo values for environmental, navigation, power, or safety decisions.

## Revision History
| Version | Date | Change |
| --- | --- | --- |
| 1.0 | 2026-08-05 | Initial dashboard manual. |
