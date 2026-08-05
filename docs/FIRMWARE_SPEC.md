# Firmware Specification

## Purpose
Specify current observable ESP32 firmware behavior.

## Scope
Startup, LittleFS, AP, DNS, HTTP, API, captive routes, and loop behavior.

## Current Status
Implemented and buildable; sensor behavior is simulated.

## Architecture
One `PortalServer` service owns `DNSServer`, `WebServer`, startup state, and monitoring state.

## Implementation
Startup mounts LittleFS, verifies four assets, configures `192.168.4.1/24`, starts `FALCON-01` on channel 6 for up to four clients, starts wildcard DNS port 53, and HTTP port 80. The loop services DNS/HTTP and delays 2 ms.

Required assets: `/index.html`, `/style.css`, `/app.js`, `/falcon-logo.jpg`. HTML and API are uncached; static assets use a one-hour cache. Monitoring state is volatile. Restart responds, waits 700 ms, then calls `ESP.restart()`.

## Future Expansion
Sensors, storage, structured errors, secure settings, watchdog, and OTA require approved implementation.

## Engineering Notes
`LittleFS.begin(true)` may format after mount failure. Firmware and filesystem must be uploaded separately.

## Revision History
| Version | Date | Change |
| --- | --- | --- |
| 1.0 | 2026-08-05 | Initial firmware specification. |
