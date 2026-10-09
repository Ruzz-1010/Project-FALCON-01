# Network Protocol

## Purpose
Specify current local networking and constrain future links.

## Scope
AP, DNS, HTTP, captive routes, dashboard polling, and future edge/remote protocols.

## Current Status
Local Wi-Fi/DNS/HTTP are implemented; event-driven LTE cloud upload, endpoint authentication, and remote links are not yet implemented.

## Architecture
Client -> FALCON-01 AP -> wildcard DNS `192.168.4.1` -> HTTP dashboard/API.

## Implementation
Captive routes: `/generate_204`, `/gen_204`, `/connecttest.txt`, `/redirect`, `/ncsi.txt`, `/hotspot-detect.html`, `/library/test/success.html`, `/canonical.html`, `/success.txt`.

Static routes: `/`, `/index.html`, `/style.css`, `/app.js`, `/falcon-logo.jpg`. API routes are in [API.md](API.md). Dashboard status polling occurs every two seconds.

## ESP32 USB/UART Telemetry v1

The prototype emits one UTF-8 JSON object per line at 115200 baud. Diagnostic
frames never fabricate measurements; absent driver values leave `measurements`
empty and report sensor state explicitly.

```json
{"protocol":"falcon.telemetry","version":1,"sequence":7,"uptimeMs":4200,"source":"hardware-diagnostic","monitoring":true,"sensors":{"bar02":"DETECTED","gps":"DETECTED","tamper":"UNTESTED"},"measurements":{}}
```

Required envelope fields are `protocol`, `version`, integer `sequence`,
`uptimeMs`, `source`, `sensors`, and `measurements`. Receivers reject unsupported
versions and malformed frames. Sequence gaps indicate dropped frames. Phase 1
USB serial relies on its physical/local trust boundary; remote transport will
require authentication, integrity protection, replay handling, and clock sync.

Run the edge serial source with:

```bash
python3 -m falcon_edge.service --source serial --serial-port /dev/ttyUSB0
```

Install `pyserial` in the edge environment first. HTTP ESP32 input remains an
alternate development transport.

## Event Driven Cloud Telemetry

The ESP32 samples sensors locally, calculates one-minute summaries, and uploads a summary every 1–5 minutes. It uploads an immediate event for significant pressure or movement changes, displacement, tamper, low battery, sensor failure, or connection recovery. Records are buffered locally while offline. HTTPS or MQTT over TLS remains a selection gate.

## Future Expansion
Add checksum/framing beyond newline JSON if field error testing demonstrates the
need, plus authenticated HTTPS or MQTT over TLS, explicit modem/recovery status,
cloud synchronization, and time synchronization. Wi-Fi is the bench path and
4G/LTE is the remote field path. If the cloud link is unavailable, the buoy
continues local acquisition and buffers telemetry for later retransmission.

An optional camera requires a separate authenticated streaming path and must not
delay or congest safety-relevant telemetry. See
[`FUTURE_UPGRADES.md`](FUTURE_UPGRADES.md).

## Engineering Notes
Captive popup behavior varies by client. Manual fallback is `http://192.168.4.1`.

## Revision History
| Version | Date | Change |
| --- | --- | --- |
| 1.1 | 2026-08-15 | Added versioned USB/UART newline-JSON telemetry contract. |
| 1.0 | 2026-08-05 | Initial network protocol. |
