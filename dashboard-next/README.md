# FALCON Dashboard Next

Canonical React + TypeScript operator dashboard for Project FALCON. The production build is hosted by the Python edge service; the ESP32 hosts only the compact setup/diagnostic portal.

## Current interface

The primary navigation contains five pages:

1. **Overview** — pressure-based estimated-wave chart and station summary.
2. **Sensors** — Wave & Pressure, GPS & Security, Wind, Water, Power, and System groups with expandable diagnostics.
3. **Buoy Motion** — optional pressure-driven 3D visualization. It uses no required IMU, roll, or pitch channel. Current Data uses telemetry; Calm, Moderate, Rough, and Pressure Offline are local labeled demo presets that never alter telemetry.
4. **GPS** — position, fix, geofence/security state, and distance from the anchor reference.
5. **Logs & Alerts** — active warnings, stored records, search, acknowledgement, and export. This is the final sidebar item.

Settings is a compact header action. Optional prediction is hidden by default and cannot block acquisition, logging, alerts, or the operator view. The saved FALCON Assistant assets are not currently mounted.

The external buoy model shown on Buoy Motion is a **reference model under redesign**. Replace it only after the new prototype passes `docs/PROTOTYPE_REDESIGN_BASELINE.md` and is exported from the same approved CAD revision.

## Data truthfulness

The interface preserves explicit states such as `LIVE`, `SIMULATED`, `ESTIMATED`, `CALIBRATION REQUIRED`, `STALE`, `OFFLINE`, and `OPTIONAL`. Pressure is measured; wave height is estimated from pressure and must be reference-calibrated before accuracy claims.

## Development on Linux Mint

Node.js 20.19 or newer is required.

```bash
cd "/home/ruzz/Documents/PlatformIO/Projects/Project FALCON-01/dashboard-next"
npm install
npm run dev
```

Open <http://127.0.0.1:5173/>. Run the edge service on port `8765` for live API data.

## Production build

```bash
cd "/home/ruzz/Documents/PlatformIO/Projects/Project FALCON-01/dashboard-next"
npm run build
cd ../edge
python3 -m falcon_edge.service
```

The build is written to `edge/static/dashboard/`. Open <http://127.0.0.1:8765/>.
