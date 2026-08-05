# Network Protocol

## Purpose
Specify current local networking and constrain future links.

## Scope
AP, DNS, HTTP, captive routes, dashboard polling, and future edge/remote protocols.

## Current Status
Local Wi-Fi/DNS/HTTP are implemented; edge and remote links are not.

## Architecture
Client -> FALCON-01 AP -> wildcard DNS `192.168.4.1` -> HTTP dashboard/API.

## Implementation
Captive routes: `/generate_204`, `/gen_204`, `/connecttest.txt`, `/redirect`, `/ncsi.txt`, `/hotspot-detect.html`, `/library/test/success.html`, `/canonical.html`, `/success.txt`.

Static routes: `/`, `/index.html`, `/style.css`, `/app.js`, `/falcon-logo.jpg`. API routes are in [API.md](API.md). Dashboard status polling occurs every two seconds.

## Future Expansion
UART/USB edge protocol and LoRa/cellular telemetry need framing, checksum, retry, versioning, timestamps, authority, and authentication definitions.

## Engineering Notes
Captive popup behavior varies by client. Manual fallback is `http://192.168.4.1`.

## Revision History
| Version | Date | Change |
| --- | --- | --- |
| 1.0 | 2026-08-05 | Initial network protocol. |
