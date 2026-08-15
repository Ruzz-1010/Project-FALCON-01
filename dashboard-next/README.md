# FALCON Dashboard Next

Canonical React + TypeScript dashboard for Project FALCON. The production build is served by the Python edge service; the ESP32 hosts only a small setup and diagnostics portal.

## Migrated pages

- responsive application shell and standard navigation;
- live Overview page;
- two-second polling of the existing Python edge API;
- dark/light themes; and
- typed telemetry contracts.

Phase 2 adds the Wave AI page with current-versus-predicted results, selectable
5/10/15-minute horizons, live history and forecast plotting, model confidence,
calculation evidence, and reversible presentation scenarios. A simulated sensor
failure is contained to the affected wave feed instead of taking down the shell.

Phase 3 adds the Motion page using the actual Fusion-exported FALCON GLB. The
lazy-loaded digital twin follows live roll, pitch, heading, and wave telemetry;
floats on an animated sea; supports orbit and zoom controls; shows navigation
lights; and highlights affected components during sensor, thermal, or power alerts.

Phase 4 adds the GPS page with a lazy-loaded OpenStreetMap view centered on the
Puerto Princesa City, Palawan coastal reference. It updates the live buoy marker,
deployment marker, 10 m geofence, drift line, coordinates, accuracy, heading,
surface speed, satellites, and map-tile connection status.

Phase 5 adds the Power page with battery reserve and runtime, voltage/current/load,
solar charging input, battery and enclosure temperatures, live intake/exhaust fan
RPM, thermal states, and realistic recent-history charts. Low-battery and thermal
presentation scenarios use the same verified edge telemetry and alert pipeline.

Phase 6 adds System Health with explicit ESP32, Orange Pi edge host, UART/Wi-Fi, and API states;
sensor-channel availability; uptime and monitoring state; CPU, memory, storage,
and Wi-Fi metrics; active diagnostics; and firmware/dashboard version context.
Simulator-backed services remain clearly labeled instead of appearing physical.

Phase 7 adds Alerts and Events with a live top-bar badge, in-app warning toast,
active-alert panel, severity filters, persisted SQLite alert history, and local
acknowledgement states. Acknowledging an item never removes the edge evidence.

Phase 8 adds Operational Logs with separate telemetry, AI prediction, alert, and
system-event archives; record search; timestamped tables; source/model context;
and CSV/JSON export of the currently filtered local records.

Phase 9 adds Settings for persistent theme and polling preferences, Wave AI
horizon, demo scenario selection, browser notification permission, approved
sensor calibration, and confirmed ESP32 restart requests. Maintenance actions
are accepted by the edge API and written to the auditable local event archive.

## Run

Start the existing edge service on port `8765`, then:

cd "C:\Users\Admin\Documents\PlatformIO\Projects\Project FALCON-01\dashboard-next"
npm.cmd run dev


```powershell
cd dashboard-next
npm install
npm run dev
```

Open `http://127.0.0.1:5173`. All planned migration pages are available: Overview,
Wave AI, Motion, GPS, Power, System Health, Alerts, Logs, and Settings.

## Production build

```bash
cd dashboard-next
npm install
npm run build
cd ../edge
python3 -m falcon_edge.service
```

The build is written to `edge/static/dashboard/`. Open `http://127.0.0.1:8765/`.
This is the normal dashboard URL on the development laptop and target Orange Pi.
