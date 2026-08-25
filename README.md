# Project FALCON-01

Project FALCON is a solar-powered smart coastal observation buoy for near-real-time local monitoring. Its Phase 1 baseline uses an ESP32 for sensor acquisition and an Orange Pi Zero 3 (4 GB) for local logging, API hosting, and the web dashboard.

The current adviser-approved direction is documented in [PROJECT_CONTEXT.md](docs/PROJECT_CONTEXT.md). It supersedes older mandatory-IMU, anchor-tension, and AI-first descriptions.

## Phase 1 focus

- pressure-based **estimated** wave height using Bar02 or a compatible sensor;
- GPS position and persistent geofence monitoring;
- wind speed and direction;
- sealed water temperature and a calibration-required salinity/conductivity indicator;
- battery, solar, and enclosure health;
- simple vibration/tamper and enclosure-access detection;
- local SQLite records and responsive dashboard;
- optional supporting AI only.

BNO085 is not required in the primary baseline. Load cell/HX711 anchor-chain sensing is removed. The buoy uses passive mooring with sufficient line scope for tides and ordinary movement.

## Current truth

The repository contains working firmware, simulator, local edge API, database, and dashboard prototypes. Most physical sensors and the Orange Pi have not yet been integrated or field-validated. Simulator readings are labeled `SIMULATED`; wave values are labeled `ESTIMATED`; uncalibrated channels say `CALIBRATION REQUIRED`.

## Run the full local dashboard on Linux Mint

The simplest normal workflow runs the bundled production dashboard from the Python edge service:

```bash
cd "/home/ruzz/Documents/PlatformIO/Projects/Project FALCON-01/edge"
python3 -m falcon_edge.service
```

Open <http://127.0.0.1:8765/>.

For frontend development, Node.js 20.19 or newer is required:

```bash
cd "/home/ruzz/Documents/PlatformIO/Projects/Project FALCON-01/dashboard-next"
npm install
npm run dev
```

Open <http://127.0.0.1:5173/> while the edge service runs on port 8765.

## Tests and builds

```bash
cd "/home/ruzz/Documents/PlatformIO/Projects/Project FALCON-01"
PYTHONPATH=edge python3 -m unittest discover -s edge/tests -v
cd dashboard-next
npm run build
```

ESP32 firmware:

```bash
cd "/home/ruzz/Documents/PlatformIO/Projects/Project FALCON-01"
pio run
```

## Dashboard

The canonical dashboard has four primary pages:

1. Overview
2. Buoy Motion (optional visualization, not a required IMU reading)
3. Sensors
4. Logs & Alerts

Settings are opened using the header icon. Optional AI is hidden by default and cannot interrupt the monitoring baseline.
The Sensors page presents six operator-friendly groups—Wave & Pressure, GPS & Security, Wind, Water, Power, and System—with technical device diagnostics available through **View Details**.

## API

The primary grouped route is:

```text
GET /api/telemetry/current
```

Compatibility alias: `GET /api/dashboard`. Legacy sensor endpoints remain temporarily available to avoid breaking existing code. See [API.md](docs/API.md).

## Repository map

```text
dashboard-next/   React/TypeScript dashboard source
data/             small ESP32 setup/diagnostic portal
docs/             current engineering documentation
edge/             Python service, tests, database, bundled dashboard
src/              ESP32 firmware
THESIS DOCUMENTATION/ thesis and presentation files
```

## Safety and research limits

FALCON is a research prototype. It is not an official weather, storm, tsunami, navigation, or emergency-warning system and must not replace PAGASA or authorized coastal agencies.
