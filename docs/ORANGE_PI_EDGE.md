# Historical Orange Pi Edge Architecture — Superseded

> **Do not use for current design or procurement.** The adviser-approved Bay Station baseline removes the Orange Pi from the buoy. See [BAY_STATION_ARCHITECTURE.md](BAY_STATION_ARCHITECTURE.md). The content below is retained only for historical traceability.

## Decision

Project FALCON Phase 1 selects the **Orange Pi Zero 3 (4GB)** as the target edge computer. Procurement, enclosure integration, and endurance validation remain pending. Until the board arrives, the development laptop performs the same edge role.

## Approved data flow

```text
Marine Sensors
       |
       v
     ESP32
 (Data Acquisition)
       |
  UART / Wi-Fi
       |
       v
Orange Pi Zero 3 (4GB)
       |
       +-- AI Prediction Engine
       +-- Explainable AI (XAI)
       +-- SQLite Database
       +-- REST API
       +-- Local Dashboard
       +-- Historical Data
       +-- Web Server
       |
       v
Laptop / Tablet / Phone
```

UART is the primary deterministic telemetry transport. Local Wi-Fi may be used during development, maintenance, or as a validated fallback. Both transports require framing, validation, reconnect behavior, stale-data detection, and explicit link status.

## Responsibility boundary

The ESP32 owns deterministic sensor acquisition, calibration application, range checks, basic filtering, watchdog behavior, and telemetry framing. It shall continue acquisition if the Orange Pi is unavailable.

The Orange Pi owns telemetry ingestion, secondary validation, wave processing, AI inference, XAI output, SQLite persistence, historical data, alerts, REST API, dashboard assets, and the local web server. It does not replace ESP32 time-critical acquisition.

The laptop, tablet, or phone is a browser client. Internet and cloud services are not required for Phase 1 operation.

## Hardware notes

The Orange Pi Zero 3 provides a USB Type-C power input, 4GB LPDDR4 in the selected variant, onboard Wi-Fi, Ethernet, and UART-capable headers. Use a stable regulated 5 V rail designed for a 3 A transient envelope. UART electrical levels, ground strategy, connector locking, isolation, and ESD protection require review before marine installation.

## Status

- Architecture selection: approved, 2026-08-12.
- Physical Orange Pi integration: planned.
- Current executable edge prototype: laptop-hosted Python service.
- Cloud synchronization: Future Expansion.

## Conditional Edge Upgrade

Orange Pi Zero 3 (4GB) remains the Phase 1 selection. A Raspberry Pi 5 4GB may
replace it only after measured CPU, memory, inference, storage, temperature, or
camera-streaming results prove that optimization is insufficient. Migration
requires a new protected power branch, active cooling, mounting and enclosure
review, and full regression/endurance testing. See
[`FUTURE_UPGRADES.md`](FUTURE_UPGRADES.md).
