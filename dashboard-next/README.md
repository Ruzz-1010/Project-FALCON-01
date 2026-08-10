# FALCON Dashboard Next

Safe, page-by-page React + TypeScript migration of the FALCON dashboard. The existing dashboard remains the production fallback while this directory is developed and validated.

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

## Run

Start the existing edge service on port `8765`, then:

```powershell
cd dashboard-next
npm install
npm run dev
```

Open `http://127.0.0.1:5173`. Overview, Wave AI, Motion, GPS, and Power are available. Other pages are
intentionally marked as pending until migrated and verified.
