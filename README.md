# Project FALCON-01

**Fullbright College's AI-powered Live Coastal Observation Network**

## Purpose
Repository entry point for the Phase 1 ESP32 local-dashboard prototype.

## Scope
Current firmware/dashboard and links to planned hardware, sensors, AI, communications, testing, and deployment documentation.

## Current Status
Implemented: PlatformIO ESP32 Arduino firmware, `FALCON-01` AP, captive portal, LittleFS dashboard/logo, and three API endpoints. Sensor values are simulated. Sensors, GPIOs, logging, OTA, edge AI, remote services, power autonomy, and marine assembly are not implemented.

## Architecture
The ESP32 independently owns the offline AP, wildcard DNS, HTTP server, local API, and LittleFS dashboard. Future sensor, edge, and cloud layers must remain optional.

## Implementation
Build and upload firmware and filesystem separately:

```powershell
platformio run
platformio run --target buildfs
platformio run --target upload
platformio run --target uploadfs
```

Close serial monitor before upload. Hold BOOT if required; after flashing, release BOOT and press EN/RESET.

| Setting | Value |
| --- | --- |
| SSID | `FALCON-01` |
| Password | `falcon123` |
| Dashboard | `http://192.168.4.1` |

The credential is for prototype use only.

Repository structure:

```text
Project FALCON-01/
|-- README.md
|-- platformio.ini
|-- docs/
|-- include/
|-- src/
|-- data/
|-- lib/
`-- test/
```

## Documentation
Start with [INDEX.md](docs/INDEX.md) and [CODEX.md](docs/CODEX.md).

- [PROJECT_CONTEXT.md](docs/PROJECT_CONTEXT.md)
- [HARDWARE.md](docs/HARDWARE.md)
- [ROADMAP.md](docs/ROADMAP.md)
- [API.md](docs/API.md)
- [SYSTEM_ARCHITECTURE.md](docs/SYSTEM_ARCHITECTURE.md)
- [FIRMWARE_SPEC.md](docs/FIRMWARE_SPEC.md)
- [PINOUT.md](docs/PINOUT.md)
- [SENSOR_SPEC.md](docs/SENSOR_SPEC.md)
- [POWER_SYSTEM.md](docs/POWER_SYSTEM.md)
- [NETWORK_PROTOCOL.md](docs/NETWORK_PROTOCOL.md)
- [SECURITY.md](docs/SECURITY.md)
- [TEST_PLAN.md](docs/TEST_PLAN.md)
- [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
- [USER_MANUAL.md](docs/USER_MANUAL.md)
- [ASSEMBLY_GUIDE.md](docs/ASSEMBLY_GUIDE.md)
- [DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md)
- [CALIBRATION_GUIDE.md](docs/CALIBRATION_GUIDE.md)
- [CHANGELOG.md](docs/CHANGELOG.md)
- [VERSION_HISTORY.md](docs/VERSION_HISTORY.md)

## Future Expansion
Verified sensor integration, power/GPS systems, bounded logging, labeled datasets, trained AI, remote telemetry, and marine field testing.

## Engineering Notes
Working source is authoritative for implementation. `docs/PROJECT_CONTEXT.md` is the master planning context. Demo readings must not be used for decisions.

## Revision History
| Version | Date | Change |
| --- | --- | --- |
| 3.1 | 2026-08-05 | Verified root overview and documentation links. |
