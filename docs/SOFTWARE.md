# Project FALCON Software Architecture v4.0

## Authority

This document implements the software boundaries defined by PROJECT_CONTEXT.md v4.0.

Status: Phase 1 Prototype.

Updated: 2026-08-09.

## Software Objective

The software shall support real-time coastal monitoring and AI-assisted wave-height prediction 5–15 minutes ahead.

No other Phase 1 AI product is approved.

## Layered Architecture

```text
Sensor Drivers
     |
ESP32 Acquisition Firmware
     |
UART Protocol
     |
Mini-PC Edge Services
     |
REST API
     |
Local Dashboard
```

Cloud software is Future Expansion.

## Current Repository Implementation

### ESP32

Implemented:

- Arduino/PlatformIO firmware;
- Wi-Fi access point;
- captive portal;
- lightweight LittleFS setup/diagnostic portal;
- simulated system state;
- status response;
- monitoring toggle;
- and restart control.

### Edge Prototype

Implemented on the laptop:

- Python service;
- simulated telemetry source;
- ESP32 HTTP-source adapter;
- local SQLite storage;
- deterministic alerts;
- presentation forecast;
- rolling backtest;
- scenario control;
- and static dashboard hosting.

### Known Migration Work

- replace broad simulated channels with approved sensor schema;
- implement UART ingestion;
- implement calibrated wave estimator;
- limit AI outputs to wave prediction and three-class sea condition;
- remove 30-minute Phase 1 prediction;
- migrate to the approved eight REST endpoints;
- and add prediction-history persistence.

## ESP32 Firmware Modules

Required modules:

```text
firmware/
├── sensors/
├── power/
├── gps/
├── dashboard/
├── storage/
├── wifi/
├── api/
├── ai_bridge/
├── diagnostics/
├── communication/
├── config/
└── main.cpp
```

### sensors

- initialize BNO085, pressure, wind, internal-temperature, and optional water-temperature devices;
- apply calibration;
- validate readings;
- timestamp samples;
- and expose health.

### power

- acquire battery voltage/current/percentage;
- acquire solar voltage/current/charging state;
- apply power thresholds;
- and publish power health.

### gps

- parse fixes;
- expose coordinates and accuracy;
- manage reference position;
- calculate anchor distance;
- and report sustained drift state.

### dashboard

- serve only the lightweight ESP32 fallback interface when used;
- clearly label reduced functionality;
- and avoid loading full 3D assets into insufficient flash.

### storage

- retain configuration;
- retain calibration metadata;
- retain essential logs;
- enforce bounded writes;
- and recover from incomplete writes.

### wifi

- manage local access;
- report connection state;
- use field-safe credentials;
- and avoid undocumented services.

### api

- provide approved endpoints when hosted on the ESP32;
- validate requests;
- bound payload sizes;
- and return structured errors.

### ai_bridge

- send validated telemetry to the Orange Pi;
- expose AI availability;
- and never fabricate predictions.

### diagnostics

- monitor task health;
- monitor sensor availability;
- record restart reason;
- and feed the watchdog.

### communication

- encode/decode UART frames;
- maintain sequence numbers;
- verify checksum or CRC;
- and report link statistics.

## Firmware Runtime Rules

- avoid long blocking calls;
- use periodic tasks or a scheduler;
- prioritize acquisition;
- isolate sensor failures;
- continue with remaining valid sensors;
- never convert unavailable data to zero;
- feed watchdog explicitly;
- and record controlled restarts.

## UART Message Model

Each frame should contain:

- protocol version;
- message type;
- payload length;
- sequence number;
- timestamp;
- payload;
- and checksum/CRC.

Approved message families:

- HEARTBEAT;
- STATUS;
- WAVE;
- MOTION;
- GPS;
- BATTERY;
- SOLAR;
- TEMPERATURE;
- ALERT;
- and CALIBRATION.

## Mini-PC Services

```text
orange_pi/
├── ingestion/
├── validation/
├── wave_processing/
├── ai/
├── storage/
├── alerts/
├── api/
├── dashboard_host/
├── config/
└── service/
```

### ingestion

- read UART without blocking other services;
- reassemble frames;
- track sequence gaps;
- and publish link state.

### validation

- validate schema;
- validate types;
- validate units/ranges;
- identify stale data;
- and preserve error reasons.

### wave_processing

- synchronize pressure and IMU data;
- apply approved preprocessing;
- calculate current wave-height estimate;
- calculate quality;
- and produce AI features.

### ai

- load one approved operational model;
- predict wave height 5–15 minutes ahead;
- classify Calm/Moderate/Rough;
- expose confidence/quality;
- and refuse inference on invalid input.

### storage

- persist telemetry;
- persist wave estimates;
- persist predictions;
- attach later actual values;
- persist alerts;
- and enforce retention.

### alerts

- apply deterministic thresholds;
- deduplicate repeated alerts;
- retain severity/code/subsystem;
- and expose active/history states.

### api

- implement the approved eight endpoints;
- use explicit units/timestamps;
- return unavailable reason;
- and protect mutating operations.

### dashboard_host

- serve local static assets;
- avoid external CDN dependencies;
- set cache policy intentionally;
- and report missing assets.

## Data States

Every relevant value shall be identifiable as one of:

- measured;
- estimated;
- predicted;
- simulated;
- stale;
- invalid;
- or unavailable.

## Storage Entities

- sensor samples;
- wave estimates;
- AI predictions;
- prediction evaluations;
- GPS records;
- power records;
- alerts;
- calibration events;
- and system logs.

## Configuration

Configuration includes:

- device ID;
- sampling intervals;
- sensor calibration;
- UART settings;
- reference GPS;
- anchor radius;
- alert thresholds;
- sea-condition thresholds;
- model version/path;
- and retention limits.

Configuration shall be validated and versioned.

## Error Handling

- log recoverable errors;
- return structured API errors;
- reconnect UART automatically;
- preserve acquisition during Orange Pi outages;
- mark AI unavailable when inputs fail;
- and avoid restart loops.

## Security

- no committed production secrets;
- strong local credentials for field deployment;
- bounded API input;
- POST for mutation;
- configuration validation;
- and audit logs for restart/calibration.

## Testing

Required software tests:

- sensor-driver unit tests where feasible;
- protocol codec tests;
- CRC/checksum tests;
- malformed-frame tests;
- database tests;
- forecast tests;
- API contract tests;
- alert-rule tests;
- reconnect tests;
- and dashboard integration tests.

## Future Expansion

Cloud services, fleet management, mobile applications, additional AI services, computer vision, and remote updates are outside Phase 1.

## Database Implementation

The Orange Pi Zero 3 (4GB) uses SQLite for local-first persistence. The v4 schema contains:

- `telemetry` for timestamped source payloads;
- `alerts` linked to their telemetry record;
- `wave_predictions` for auditable 5- and 15-minute model outputs;
- and `system_events` for restart and calibration command auditing.

Schema creation is additive through `CREATE TABLE IF NOT EXISTS`. Existing presentation databases are upgraded when the edge service starts, without removing earlier telemetry or alert records.

## Revision History

| Version | Date | Change |
| --- | --- | --- |
| 4.1 | 2026-08-12 | Selected Orange Pi Zero 3 (4GB) as the edge host; UART remains primary and Wi-Fi is an alternate validated transport. |
| 4.0 | 2026-08-09 | Created focused ESP32, UART, edge-host, REST API, and local-dashboard software architecture. |
| 4.1 | 2026-08-09 | Recorded the implemented v4 SQLite schema, approved endpoints, and dashboard migration. |
