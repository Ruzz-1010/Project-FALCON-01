# Security

## Purpose
Document current security posture and required future controls.

## Scope
Wi-Fi, HTTP/API, credentials, physical access, updates, and remote links.

## Current Status
Prototype only: WPA2 AP password exists, but HTTP/API have no authentication or TLS. The shared password is hard-coded and documented.

## Architecture
Any nearby user who knows the AP password can access dashboard controls, including restart.

## Implementation
Current controls are AP password protection, local-only operation, and absence of cloud credentials/remote commands. Missing controls include roles, sessions, CSRF defense, rate limits, audit logs, signed updates, and secure provisioning.

## Future Expansion
Per-device credentials, authenticated technician access, encrypted edge/remote links, secure storage, signed updates, and threat modeling.

## Engineering Notes
Do not present the current prototype as secure for unattended public deployment.

## Revision History
| Version | Date | Change |
| --- | --- | --- |
| 1.0 | 2026-08-05 | Initial security assessment. |
