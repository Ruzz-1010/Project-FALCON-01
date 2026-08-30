# Firmware Specification

> Bay Station revision v7.0 governs: pressure and security inputs plus LTE/cellular telemetry are required; BNO085/load-cell/onboard-computer logic is not. Required AI prediction runs at the shore Bay Station and cannot block ESP32 acquisition/security. Exact modem, buffering, authentication, and connector implementation remain pending approval.

## Purpose
Specify current observable ESP32 firmware behavior.

## Scope
Startup, LittleFS setup portal, AP, DNS, HTTP, API, captive routes, diagnostics, and loop behavior.

## Current Status
Implemented and buildable; sensor behavior is simulated.

## Architecture
One `PortalServer` service owns `DNSServer`, `WebServer`, startup state, and monitoring state.

## Implementation
Startup mounts LittleFS, verifies four assets, configures `192.168.4.1/24`, starts `FALCON-01` on channel 6 for up to four clients, starts wildcard DNS port 53, and HTTP port 80. The loop services DNS/HTTP and delays 2 ms.

Required assets: `/index.html`, `/style.css`, `/app.js`, `/falcon-logo.jpg`. These provide buoy-node setup and diagnostics only; the full dashboard is hosted by the shore Bay Station service. HTML and API are uncached; static assets use a one-hour cache. Monitoring state is volatile. Restart responds, waits 700 ms, then calls `ESP.restart()`.

## Future Expansion
Physical sensors, LTE modem driver, packet identity, short-outage buffer, acknowledgement/retry, secure credential provisioning, structured errors, watchdog, and OTA require approved implementation.

## Engineering Notes
`LittleFS.begin(true)` may format after mount failure. Firmware and filesystem must be uploaded separately.

## Revision History
| Version | Date | Change |
| --- | --- | --- |
| 2.0 | 2026-08-15 | Reduced LittleFS UI to sensor-node setup/diagnostics; full dashboard moved to edge host. |
| 1.0 | 2026-08-05 | Initial firmware specification. |
