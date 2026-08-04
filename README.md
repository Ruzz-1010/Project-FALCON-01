# Project FALCON-01

**FALCON** means **Fullbright College's AI-powered Live Coastal Observation Network**.

FALCON-01 is an AI-assisted, solar-powered smart ocean buoy concept for local coastal monitoring, future short-term environmental prediction, and anti-theft protection.

## Current working feature

The ESP32 creates a local Wi-Fi access point:

- SSID: `FALCON-01`
- Password: `falcon123`
- Dashboard: `http://192.168.4.1`

A captive portal automatically displays the dashboard after a phone connects.

## Development environment

- VS Code
- PlatformIO
- ESP32 Arduino framework
- LittleFS
- Built-in `WiFi`, `WebServer`, and `DNSServer`

## Current status

Completed:
- ESP32 blink test
- CH340 driver setup
- COM3 upload
- Wi-Fi AP
- Captive portal

Current focus:
- LittleFS-based local dashboard
- Professional responsive marine UI
- Stable local APIs

Read `PROJECT_CONTEXT.md` before editing the project.

## Firmware structure

- `src/main.cpp` starts and services the local portal.
- `src/portal_server.*` owns the Wi-Fi AP, captive DNS, HTTP routes, LittleFS
  file serving, and current local API handlers.
- `include/config.h` contains shared network and website-path constants.
- `data/` contains the separate HTML, CSS, and JavaScript dashboard assets.

After firmware changes, run PlatformIO **Upload**. After any `data/` change, run
PlatformIO **Upload Filesystem Image** as a separate step. Close the serial
monitor first because it can lock the configured COM port.
