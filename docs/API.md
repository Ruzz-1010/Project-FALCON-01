# Project FALCON Local API v6.1

Authority: [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md). Host: Orange Pi Zero 3 or development laptop. Format: UTF-8 JSON with ISO 8601 timestamps.

## Primary grouped endpoint

`GET /api/telemetry/current` returns the complete adviser-approved dashboard state. `GET /api/dashboard` is an equivalent compatibility alias.

```json
{
  "system": {
    "state": "ONLINE",
    "source": "simulator",
    "recordedAt": "2026-08-25T12:00:00+00:00",
    "labels": ["SIMULATED"]
  },
  "wave": {
    "rawPressure": 115.31,
    "filteredPressure": 115.28,
    "pressureBaseline": 114.90,
    "pressureUnit": "kPa",
    "depth": 1.49,
    "waveHeight": 0.53,
    "waveHeightState": "SIMULATED",
    "estimationMethod": "pressure-calibration-v1",
    "calibration": "CALIBRATION REQUIRED",
    "valid": true
  },
  "environment": {
    "windSpeed": 11.2,
    "windDirection": "NE",
    "waterTemperature": 28.2,
    "enclosureTemperature": 34.0
  },
  "gps": {},
  "power": {"battery": {}, "solar": {}},
  "security": {
    "state": "SECURE",
    "geofenceState": "SECURE",
    "geofenceRadiusMeters": 10,
    "distanceMeters": 2.4,
    "vibrationDetected": false,
    "enclosureOpen": false,
    "buzzerActive": false,
    "persistence": "DEBOUNCED"
  },
  "health": {},
  "assistant": {
    "state": "NORMAL",
    "message": "Station readings are within configured monitoring limits.",
    "mode": "RULE_BASED",
    "optional": true
  },
  "alerts": []
}
```

## Data-state rules

- `LIVE`: produced from connected physical hardware.
- `SIMULATED`: produced by the presentation simulator.
- `ESTIMATED`: derived from sensor data; not directly measured.
- `CALIBRATION REQUIRED`: no validated field calibration supports an accuracy claim.
- `STALE`: older than the configured update threshold.
- `OFFLINE`: source is unavailable.
- `OPTIONAL`: failure cannot interrupt the monitoring baseline.

Unavailable readings are `null`, never a fabricated zero. Units and source must remain explicit.

## Compatibility endpoints

| Route | Purpose | Status |
| --- | --- | --- |
| `GET /status` | service and sensor health | Supported |
| `GET /wave` | pressure and estimated wave details | Supported |
| `GET /gps` | position and geofence details | Supported |
| `GET /battery` | battery state | Supported |
| `GET /solar` | solar state | Supported |
| `GET /logs` | telemetry, optional predictions, alerts, and events | Supported |
| `GET /ai?horizon=10` | optional research prediction | Optional compatibility route |
| `GET/POST /api/scenario` | simulator scenarios | Development only |
| `POST /calibrate` | audited calibration request | Supported |
| `POST /restart` | audited maintenance request | Supported |

## Calibration channels

Accepted Phase 1 calibration targets are `water-pressure`, `water-temperature`, `wind`, `gps`, `battery`, `solar`, and `security`. The legacy `salinity` field/target may remain temporarily for backward compatibility but is excluded from the required dashboard, hardware baseline, and evaluation. BNO085 and mooring-tension channels are not part of the approved primary contract.

## Errors

Use `400` for invalid input, `404` for unknown routes, `409` for unavailable operations, `503` for required unavailable data, and `500` for unexpected service errors. Current-data responses use `Cache-Control: no-store`.
