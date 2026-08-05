# Project FALCON-01

> **Fullbright College's AI-powered Live Coastal Observation Network**

Project FALCON-01 is the Phase 1 prototype of **Project FALCON**, an AI-assisted, solar-powered smart coastal observation buoy designed for long-term autonomous deployment in Philippine coastal waters.

The system combines embedded systems, IoT, renewable energy, edge AI, and environmental sensing to provide real-time coastal monitoring, buoy self-diagnostics, and future AI-assisted environmental prediction.

---

# Project Goals

Project FALCON aims to provide an affordable, research-grade coastal monitoring platform capable of:

* Real-time environmental monitoring
* AI-assisted sea-state classification
* Autonomous solar-powered operation
* Local maintenance dashboard
* Remote cloud synchronization
* GPS tracking and drift detection
* Tidal-aware buoy health monitoring
* Anti-theft monitoring
* Future multi-buoy networking

---

# Project Information

| Item                  | Value                 |
| --------------------- | --------------------- |
| Project               | Project FALCON        |
| Prototype             | FALCON-01             |
| Current Stage         | Phase 1 Prototype     |
| Firmware Version      | Development           |
| Documentation Version | PROJECT_CONTEXT.md v3 |
| IDE                   | Visual Studio Code    |
| Extension             | PlatformIO            |
| Framework             | Arduino (ESP32)       |

---

# Development Environment

## Software

* Visual Studio Code
* PlatformIO
* ESP32 Arduino Framework
* LittleFS
* Git

## Core Libraries

* WiFi
* WebServer
* DNSServer
* LittleFS
* ArduinoJson
* Preferences
* Update (OTA)

Additional libraries will be introduced as new hardware modules are integrated.

---

# ESP32 Features

The ESP32 is the primary embedded controller responsible for:

* Sensor acquisition
* Local Wi-Fi Access Point
* Captive Portal
* Local Dashboard
* REST API
* Power monitoring
* GPS communication
* Health monitoring
* Data logging
* OTA firmware updates
* Communication with the AI computer

The ESP32 continues operating even if the AI computer becomes unavailable.

---

# Local Wi-Fi

The firmware automatically creates a maintenance Wi-Fi network.

## Default Configuration

**SSID**

```text
FALCON-01
```

**Password**

```text
falcon123
```

**Dashboard**

```text
http://192.168.4.1
```

---

# Captive Portal

When a technician connects to the buoy's Wi-Fi network:

1. Connect to **FALCON-01**
2. Captive Portal automatically opens
3. Dashboard loads
4. Live system information becomes available

No Internet connection is required.

---

# Current Development Status

## Completed

* ESP32 development environment
* CH340 USB driver installation
* COM3 upload verified
* Blink test
* Wi-Fi Access Point
* Captive Portal
* Basic project structure
* LittleFS integration
* Local dashboard framework

---

## Current Focus

Development is currently focused on:

* Professional responsive marine dashboard
* LittleFS web assets
* REST API development
* Modular firmware architecture
* Health monitoring system
* Dashboard optimization

---

## Planned Features

* Live sensor monitoring
* GPS display
* Battery monitoring
* Solar monitoring
* IMU visualization
* Drift detection
* Alert system
* OTA firmware updates
* Configuration interface
* Data export
* Diagnostic logs

---

# Project Structure

```text
Project-FALCON/
│
├── include/
│   ├── config.h
│   └── ...
│
├── src/
│   ├── main.cpp
│   ├── portal_server.cpp
│   ├── portal_server.h
│   └── ...
│
├── data/
│   ├── index.html
│   ├── style.css
│   ├── app.js
│   └── assets/
│
├── lib/
│
├── test/
│
├── documentation/
│
├── hardware/
│
├── mechanical/
│
├── PROJECT_CONTEXT.md
│
└── README.md
```

---

# Firmware Structure

## `src/main.cpp`

Responsibilities:

* System initialization
* Main scheduler
* Service execution
* Watchdog feeding

---

## `src/portal_server.*`

Responsible for:

* Wi-Fi Access Point
* Captive Portal
* DNS Server
* HTTP Server
* LittleFS file serving
* REST API
* Dashboard routing

---

## `include/config.h`

Contains shared project configuration such as:

* Wi-Fi settings
* Dashboard configuration
* API constants
* System constants
* Pin assignments
* Feature flags

---

## `data/`

Contains all web assets.

Examples:

* HTML
* CSS
* JavaScript
* Images
* Icons
* Fonts

These files are uploaded separately to LittleFS.

---

# Upload Procedure

## Firmware

After modifying firmware:

1. Save changes.
2. Close the Serial Monitor.
3. Run:

```text
PlatformIO → Upload
```

---

## Dashboard Files

After modifying anything inside the `data/` directory:

1. Save changes.
2. Close the Serial Monitor.
3. Run:

```text
PlatformIO → Upload Filesystem Image
```

This uploads the LittleFS partition independently of the firmware.

---

# Coding Guidelines

Project FALCON follows these engineering principles:

* Modular architecture
* Non-blocking code
* Event-driven design
* Extensive documentation
* Clean code practices
* Version control with Git
* Consistent formatting
* Hardware abstraction
* Reusable modules

---

# Documentation

Before making significant code or hardware changes, review the following documents:

1. `PROJECT_CONTEXT.md` *(Master Source of Truth)*
2. `Hardware_Documentation.md`
3. `SYSTEM_ARCHITECTURE.md` *(when available)*
4. `FIRMWARE_SPEC.md` *(when available)*

All development should remain consistent with the approved Phase 1 baseline.

---

# Phase 1 Hardware Overview

Current prototype hardware includes:

* ESP32 DevKit
* AI Computer (development platform)
* 12V 60Ah LiFePO₄ Battery
* 150W Solar Panel
* MPPT Charge Controller
* GPS Module
* LTE Module
* BNO085 IMU
* Environmental Sensors
* Modified HDPE Drum
* Four HDPE Stabilizer Buoys
* Central Ballast
* Marine Anchor

---

# Future Development

Planned enhancements include:

* AI-powered sea-state prediction
* Multi-buoy fleet management
* LoRa networking
* Satellite communication
* Camera integration
* Oil spill detection
* Predictive maintenance
* Mobile application
* Cloud analytics dashboard
* Remote configuration management

---

# License

This repository is part of the **Project FALCON** research and development initiative.

Unless otherwise specified, all project files, documentation, firmware, and designs are intended solely for educational, research, and prototype development purposes.

---

# Important

**Always read `PROJECT_CONTEXT.md` before making significant changes.**

`PROJECT_CONTEXT.md` is the authoritative engineering reference for Project FALCON and defines the approved hardware, firmware, software architecture, and development roadmap.
