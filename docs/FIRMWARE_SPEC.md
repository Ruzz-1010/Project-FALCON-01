# Firmware Specification


<!-- FALCON-DOST-REVISION-NOTE:START -->
> **Current revision note (2026-10-10):** Use the DOST major revision baseline in [`docs/REVISION_2026-10-10.md`](REVISION_2026-10-10.md) unless this file is explicitly archived. The active proposal core is a compact ESP32-based buoy with **water pressure sensing, wind speed/direction sensing, GPS for exact position and security, battery + solar power, and Wi-Fi/LTE internet communication**. LoRa, large Bay Station hardware, tall tower layouts, and continuous every-second uploads are legacy or optional fallback assumptions.
<!-- FALCON-DOST-REVISION-NOTE:END -->

> Event-driven cloud revision v9.0 governs: pressure input and local ESP32 event detection are required; Wi-Fi is the bench path and 4G/LTE is the remote field path. BNO085/load-cell/onboard-computer/LoRa-gateway logic is not required in the low-cost minimum build. Any prediction runs outside the buoy and cannot block ESP32 acquisition or buffering. Exact modules, buffering, authentication, cloud endpoint, and connector implementation remain pending approval.

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

Required assets: `/index.html`, `/style.css`, `/app.js`, `/falcon-logo.jpg`. These provide buoy-node setup and diagnostics; the full dashboard may be hosted by the cloud or development edge service. HTML and API are uncached; static assets use a one-hour cache. Monitoring state is volatile. Restart responds, waits 700 ms, then calls `ESP.restart()`.

## Future Expansion
Physical sensors, event-driven packet identity, short-outage buffer, acknowledgement/retry, LTE modem control, secure credential provisioning, cloud transport, structured errors, watchdog, and OTA require approved implementation.

## Engineering Notes
`LittleFS.begin(true)` may format after mount failure. Firmware and filesystem must be uploaded separately.

## Revision History
| Version | Date | Change |
| --- | --- | --- |
| 2.0 | 2026-08-15 | Reduced LittleFS UI to sensor-node setup/diagnostics; full dashboard moved to edge host. |
| 1.0 | 2026-08-05 | Initial firmware specification. |
