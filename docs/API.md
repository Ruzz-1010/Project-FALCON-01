# Project FALCON Local REST API v4.0

## Document Control

| Field | Value |
| --- | --- |
| Authority | PROJECT_CONTEXT.md v4.0 |
| Target host | Mini PC local edge service |
| Representation | JSON |
| Status | Approved contract implemented by the Mini PC edge service |
| Updated | 2026-08-09 |

## Approved Endpoint Set

```text
GET  /status
GET  /wave
GET  /gps
GET  /battery
GET  /solar
GET  /ai
POST /restart
POST /calibrate
```

No other endpoint is part of the final Phase 1 contract.

Dashboard v5 presentation extensions are `GET /prediction` and `GET /logs`. They support the requested 10-minute demonstration and local history/export interface without replacing the eight approved Phase 1 contract endpoints.

## Current Compatibility Status

The Mini PC edge service implements all eight approved endpoints. Legacy/prototype routes remain temporarily available for ESP32 portal and presentation-scenario compatibility.

### ESP32 Portal

- `GET /api/status` — implemented;
- `POST /api/monitoring/toggle` — implemented prototype control;
- `POST /api/restart` — implemented.

### Laptop Edge Prototype

- `GET /health` — implemented;
- `GET /api/latest` — implemented;
- `GET /api/history` — implemented;
- `GET /api/alerts` — implemented;
- `GET /api/scenario` — implemented for demonstration;
- `POST /api/scenario` — implemented for demonstration;
- `GET /api/forecast` — implemented presentation forecast;
- and `GET /api/forecast/validation` — implemented presentation backtest.

These routes are not the final v4 public contract. The v4 dashboard no longer depends on legacy telemetry or forecast routes; only its explicitly labeled simulator control uses `/api/scenario`.

Migration shall preserve demonstrations while the dashboard and services adopt the approved paths.

## General Conventions

- JSON responses;
- UTF-8 encoding;
- ISO 8601 timestamps with timezone;
- explicit engineering units;
- no-cache policy for current operational data;
- meaningful HTTP status codes;
- structured error objects;
- no mutation through GET;
- and unavailable values represented explicitly, not as false zeros.

## Data-State Conventions

Values may include a state such as:

- `MEASURED`;
- `ESTIMATED`;
- `PREDICTED`;
- `SIMULATED`;
- `STALE`;
- `INVALID`;
- or `UNAVAILABLE`.

## Common Error Shape

```json
{
  "error": {
    "code": "SENSOR_UNAVAILABLE",
    "message": "Water-pressure sensor is unavailable.",
    "recordedAt": "2026-08-09T10:00:00+00:00",
    "details": {}
  }
}
```

Recommended status mapping:

- `200` successful read or completed command;
- `202` accepted asynchronous command;
- `400` malformed request;
- `404` unknown route/resource;
- `409` command conflicts with current state;
- `422` structurally valid but unacceptable calibration input;
- `503` required subsystem unavailable;
- and `500` unexpected internal failure.

## GET /status

Purpose: overall local-system readiness.

### Response

```json
{
  "system": "ONLINE",
  "monitoring": true,
  "uptimeSeconds": 42672,
  "esp32": "ONLINE",
  "miniPc": "ONLINE",
  "uart": "CONNECTED",
  "api": "ONLINE",
  "sensorsOnline": 8,
  "sensorsExpected": 8,
  "lastUpdate": "2026-08-09T10:00:00+00:00",
  "dataSource": "simulator",
  "activeAlertCount": 0,
  "version": "4.0"
}
```

### Rules

- `dataSource` is required;
- simulator mode shall be explicit;
- sensor counts shall reflect approved installed sensors;
- and stale ESP32 telemetry shall degrade `system` or `uart` state.

## GET /wave

Purpose: current wave, pressure, and motion state.

### Response

```json
{
  "recordedAt": "2026-08-09T10:00:00+00:00",
  "waveHeight": 0.42,
  "waveHeightUnit": "m",
  "waveHeightState": "ESTIMATED",
  "estimationMethod": "pressure-imu-v1",
  "pressure": 115.2,
  "pressureUnit": "kPa",
  "pitch": 0.9,
  "roll": 1.8,
  "yaw": 41.6,
  "angleUnit": "deg",
  "waveMotion": 0.37,
  "quality": 0.91,
  "valid": true
}
```

### Rules

- wave-height definition shall match `estimationMethod`;
- quality meaning shall be documented;
- missing pressure/IMU input shall not produce fabricated wave height;
- and simulator data shall use `waveHeightState: SIMULATED` or equivalent source metadata.

## GET /gps

Purpose: current position and deployment-reference state.

### Response

```json
{
  "recordedAt": "2026-08-09T10:00:00+00:00",
  "latitude": 9.742112,
  "longitude": 118.735322,
  "fix": "3D",
  "satellites": 12,
  "horizontalAccuracyMeters": 1.8,
  "referenceLatitude": 9.7421,
  "referenceLongitude": 118.7353,
  "deploymentName": "Puerto Princesa City, Palawan Coast",
  "deploymentReferenceState": "DEMO_REFERENCE",
  "anchorDistanceMeters": 3.4,
  "driftStatus": "SECURE",
  "valid": true
}
```

### Rules

- drift calculation shall account for expected mooring swing;
- the packaged Puerto Princesa coordinate is a presentation reference until replaced by a surveyed field coordinate;
- no fix shall return `valid: false` and nullable coordinates;
- and GPS is not an autonomous-navigation interface.

## GET /battery

Purpose: battery state and power warning context.

### Response

```json
{
  "recordedAt": "2026-08-09T10:00:00+00:00",
  "voltage": 12.7,
  "voltageUnit": "V",
  "current": -0.82,
  "currentUnit": "A",
  "percentage": 87.0,
  "direction": "DISCHARGING",
  "status": "NORMAL",
  "valid": true
}
```

### Rules

- sign convention shall be documented;
- percentage is an estimate;
- and low/critical thresholds belong in configuration.

## GET /solar

Purpose: solar input and charging state.

### Response

```json
{
  "recordedAt": "2026-08-09T10:00:00+00:00",
  "voltage": 18.4,
  "voltageUnit": "V",
  "current": 2.16,
  "currentUnit": "A",
  "power": 39.7,
  "powerUnit": "W",
  "charging": true,
  "status": "CHARGING",
  "valid": true
}
```

### Rules

- power shall be calculated only from compatible simultaneous readings;
- unavailable current shall make power unavailable;
- and nighttime standby is not automatically a fault.

## GET /ai

Purpose: focused wave prediction and sea-condition classification.

### Successful Response

```json
{
  "generatedAt": "2026-08-09T10:00:00+00:00",
  "targetAt": "2026-08-09T10:15:00+00:00",
  "horizonMinutes": 15,
  "currentWaveHeight": 0.42,
  "predictedWaveHeight": 0.58,
  "unit": "m",
  "change": 0.16,
  "direction": "up",
  "confidence": 82,
  "confidenceMeaning": "model quality indicator",
  "seaCondition": "MODERATE",
  "model": "wave-short-term",
  "modelVersion": "1.0.0",
  "sampleCount": 120,
  "status": "READY",
  "dataSource": "sensor",
  "unavailableReason": null
}
```

### Unavailable Response

```json
{
  "generatedAt": "2026-08-09T10:00:00+00:00",
  "targetAt": null,
  "horizonMinutes": 15,
  "currentWaveHeight": null,
  "predictedWaveHeight": null,
  "unit": "m",
  "change": null,
  "direction": null,
  "confidence": null,
  "seaCondition": null,
  "model": "wave-short-term",
  "modelVersion": "1.0.0",
  "sampleCount": 3,
  "status": "UNAVAILABLE",
  "dataSource": "sensor",
  "unavailableReason": "INSUFFICIENT_HISTORY"
}
```

### Rules

- supported horizon is 5–15 minutes;
- Phase 1 audit baselines use 5 and 15 minutes; Dashboard v5 may request 10 minutes as an in-range presentation extension;
- current and predicted values shall both be returned;
- sea condition shall be Calm, Moderate, or Rough when valid;
- unavailable is a state, not a sea-condition class;
- and weather/current/maintenance/water-quality predictions shall not be added.

## POST /restart

Purpose: authorized controlled restart.

### Request

```json
{
  "target": "esp32",
  "reason": "authorized maintenance"
}
```

Allowed target values:

- `esp32`;
- `mini-pc` when implemented;
- or `service` when implemented.

### Accepted Response

```json
{
  "accepted": true,
  "target": "esp32",
  "status": "RESTARTING"
}
```

Restart requests shall be logged.

## POST /calibrate

Purpose: authorized sensor calibration request.

### Request

```json
{
  "sensor": "bno085",
  "operation": "start",
  "reference": null
}
```

### Response

```json
{
  "accepted": true,
  "sensor": "bno085",
  "operation": "start",
  "status": "IN_PROGRESS",
  "calibrationId": "cal-20260809-001"
}
```

Calibration requests shall validate the installed sensor and supported operation.

Calibration completion/failure shall be recorded in system logs.

## Security

- local access does not eliminate authorization needs;
- mutating endpoints shall reject oversized payloads;
- request input shall be validated;
- field credentials shall not use prototype defaults;
- and restart/calibration events shall be auditable.

## Contract Testing

Each endpoint requires tests for:

- successful response;
- schema/type validity;
- explicit units;
- unavailable state;
- stale source;
- malformed request where applicable;
- service failure;
- and no-cache behavior for current state.

## Migration Plan

1. define shared v4 response models;
2. implement approved endpoints alongside legacy routes;
3. migrate dashboard consumers;
4. add contract tests;
5. mark legacy routes deprecated;
6. remove legacy routes only after demonstration compatibility is confirmed;
7. update all examples and supporting documents.

## Future Expansion

Cloud APIs, authentication services, fleet endpoints, water-quality endpoints, camera endpoints, mobile APIs, and multi-buoy endpoints are outside Phase 1.

## Revision History

| Version | Date | Change |
| --- | --- | --- |
| 3.1 | 2026-08-05 | Recorded three implemented ESP32 prototype endpoints. |
| 4.0 | 2026-08-09 | Replaced broad API roadmap with eight approved local endpoints and explicit legacy-migration status. |
| 4.1 | 2026-08-09 | Recorded implementation of all approved endpoints and dashboard migration. |
