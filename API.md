# FALCON-01 Local API

## GET `/api/status`

Returns current system and dashboard data.

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

Current sensor values are demo values until physical modules are connected.

## POST `/api/monitoring/toggle`

Toggles local monitoring.

Example response:

```json
{"monitoring": true}
```

## POST `/api/restart`

Restarts the ESP32.

Example response:

```json
{"restarting": true}
```

## Planned future endpoints

- `GET /api/gps`
- `GET /api/sensors`
- `GET /api/battery`
- `GET /api/solar`
- `GET /api/security`
- `GET /api/history`
- `GET /api/settings`
- `POST /api/settings`
- `POST /api/calibrate`
- `POST /api/security/arm`
- `POST /api/security/disarm`

These are proposals and may change.

## Implementation compatibility

The current handlers are implemented by `PortalServer` in
`src/portal_server.cpp`. This modularization does not change any endpoint,
method, response field, or response type documented above. API responses disable
browser caching so the local dashboard always receives current device state.
