# Troubleshooting

## Purpose
Provide safe recovery for observed prototype failures.

## Scope
PlatformIO, COM3, boot mode, LittleFS, AP, portal, API, and caching.

## Current Status
Based on the Windows CH340/ESP32 development setup.

## Architecture
Diagnose USB/serial -> boot -> firmware -> LittleFS -> AP/DNS -> HTTP/assets -> API/UI.

## Implementation
- `pio` missing: use VS Code tasks or `%USERPROFILE%\.platformio\penv\Scripts\platformio.exe`.
- COM3 busy: close all serial monitors; only one process may own the port.
- Wrong boot mode `0x13`: hold BOOT during connection, release after writing starts, then press EN after upload if needed.
- `File not found`: upload the LittleFS image separately.
- AP absent: release BOOT, press EN, wait 5-10 seconds, inspect serial startup, and verify USB power.
- Portal not automatic: stay connected despite no internet and open `http://192.168.4.1`.
- Old UI/logo: refresh or clear site cache; static assets cache for one hour.
- Connection lost: test `/api/status` and check serial for resets.

## Future Expansion
Add fault trees for sensors, power, edge compute, remote links, and field servicing.

## Engineering Notes
Collect logs before erasing flash, changing partitions, or clearing tool caches.

## Revision History
| Version | Date | Change |
| --- | --- | --- |
| 1.0 | 2026-08-05 | Initial observed-failure guide. |
