# FALCON-01 Local API

**Project:** Project FALCON

**Prototype:** FALCON-01

**Document Version:** API v3.0

**Status:** Phase 1 Development

---

# Overview

The FALCON-01 Local API provides a REST interface hosted directly on the ESP32.

The API is used by:

* Local Dashboard
* Mobile Devices
* Future Mobile Application
* AI Computer
* Maintenance Tools

All API endpoints are available only through the local Wi-Fi Access Point unless remote access is explicitly enabled in future versions.

---

# Base URL

```text
http://192.168.4.1/api/
```

---

# Response Format

All endpoints return JSON.

Example:

```json
{
    "success": true,
    "timestamp": 1722850000
}
```

---

# Authentication

Current Phase 1:

No authentication.

Future versions will support:

* User login
* Technician authentication
* API tokens
* Session management

---

# Cache Policy

All API responses disable browser caching to ensure the dashboard always displays the latest device information.

---

# System Endpoints

## GET `/api/status`

Returns the current system overview used by the dashboard.

### Example Response

```json
{
  "system": "ONLINE",
  "clients": 1,
  "uptime": 120,
  "monitoring": true,
  "battery": 94,
  "temperature": 28.6,
  "tilt": 2.4,
  "waveLevel": 0.3,
  "seaCondition": "CALM",
  "gps": "WAITING FOR GPS",
  "solar": "STANDBY",
  "security": "ARMED"
}
```

Current values are simulated until physical hardware is installed.

---

## GET `/api/info`

Returns firmware and device information.

### Planned Response

```json
{
    "device":"FALCON-01",
    "firmware":"1.0.0",
    "board":"ESP32 DevKit",
    "project":"Project FALCON",
    "status":"ONLINE"
}
```

---

## GET `/api/health`

Returns the buoy health summary.

### Planned Response

```json
{
    "healthScore":96,
    "status":"GOOD",
    "alerts":0,
    "maintenanceRequired":false
}
```

---

# Monitoring Endpoints

## POST `/api/monitoring/toggle`

Enable or disable local monitoring.

### Example Response

```json
{
    "monitoring": true
}
```

---

## POST `/api/restart`

Restarts the ESP32.

### Example Response

```json
{
    "restarting": true
}
```

---

# GPS Endpoints

## GET `/api/gps`

**Planned**

Example:

```json
{
    "status":"LOCKED",
    "latitude":0.0000,
    "longitude":0.0000,
    "satellites":12,
    "speed":0.0,
    "distanceFromAnchor":1.5
}
```

---

# Sensor Endpoints

## GET `/api/sensors`

Returns all available sensor readings.

Example:

```json
{
    "waterTemperature":28.3,
    "airTemperature":29.6,
    "humidity":82,
    "pressure":1012,
    "salinity":34.8,
    "waterLevel":1.25
}
```

---

## GET `/api/motion`

Returns IMU information.

Example:

```json
{
    "roll":1.8,
    "pitch":2.2,
    "tilt":2.4,
    "waveLevel":0.3
}
```

---

# Power Endpoints

## GET `/api/battery`

Example:

```json
{
    "percentage":94,
    "voltage":13.1,
    "current":1.8,
    "status":"NORMAL"
}
```

---

## GET `/api/solar`

Example:

```json
{
    "voltage":18.6,
    "current":3.5,
    "power":65.1,
    "status":"CHARGING"
}
```

---

# Safety Endpoints

## GET `/api/security`

Example:

```json
{
    "status":"ARMED",
    "tamper":false,
    "leak":false,
    "drift":false
}
```

---

## POST `/api/security/arm`

Future endpoint.

Example response:

```json
{
    "armed": true
}
```

---

## POST `/api/security/disarm`

Future endpoint.

Example response:

```json
{
    "armed": false
}
```

---

# History Endpoints

## GET `/api/history`

Returns historical sensor records.

Future implementation may support pagination and filtering.

---

# Settings Endpoints

## GET `/api/settings`

Returns device configuration.

Future example:

```json
{
    "device":"FALCON-01",
    "samplingInterval":5,
    "wifiSSID":"FALCON-01"
}
```

---

## POST `/api/settings`

Updates configuration parameters.

Future implementation will require authentication.

---

## POST `/api/calibrate`

Starts sensor calibration.

Future response:

```json
{
    "calibration":"STARTED"
}
```

---

# OTA Endpoints

## GET `/api/ota/status`

**Future**

Returns firmware update status.

---

## POST `/api/ota/update`

**Future**

Starts an OTA firmware update.

---

# Diagnostics Endpoints

## GET `/api/diagnostics`

Future endpoint.

Returns:

* CPU usage
* Memory usage
* LittleFS usage
* Wi-Fi clients
* Restart reason
* Internal temperature

---

## GET `/api/logs`

Future endpoint.

Returns recent system logs.

---

# AI Endpoints

## GET `/api/ai`

Future endpoint.

Example:

```json
{
    "seaCondition":"CALM",
    "confidence":97,
    "health":"GOOD"
}
```

---

# Error Responses

Example:

```json
{
    "success": false,
    "error": "NOT_FOUND"
}
```

Possible errors include:

* NOT_FOUND
* INVALID_REQUEST
* INTERNAL_ERROR
* SENSOR_OFFLINE
* GPS_UNAVAILABLE
* UNAUTHORIZED *(Future)*

---

# API Versioning

Current version:

```
v1 (Development)
```

Future major firmware releases may introduce versioned routes, for example:

```text
/api/v2/status
/api/v2/sensors
```

while maintaining backward compatibility whenever practical.

---

# Current Implementation

The following endpoints are currently implemented in `PortalServer` (`src/portal_server.cpp`):

* `GET /api/status`
* `POST /api/monitoring/toggle`
* `POST /api/restart`

All other endpoints described in this document are planned for future development and serve as the official API roadmap.

---

# Development Notes

* JSON is the standard response format.
* All responses include cache-control headers to prevent browser caching.
* The API is designed to remain lightweight for efficient operation on the ESP32.
* New endpoints should follow existing naming conventions and maintain backward compatibility whenever possible.

---

**Document:** API.md

**Version:** 3.0

**Status:** Phase 1 Development

This document defines the official local REST API for Project FALCON-01 and serves as the reference for dashboard, firmware, AI, and future mobile application development.
