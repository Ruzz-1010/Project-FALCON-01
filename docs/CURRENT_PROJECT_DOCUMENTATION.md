# Project FALCON-01 — Consolidated Current-State Documentation

| Field | Value |
| --- | --- |
| Project | FALCON-01 — AI-powered Live Coastal Observation Network |
| Institution | Fullbright College |
| Phase | Phase 1 prototype |
| Documentation date | 2026-08-15 |
| Current mechanical baseline | Revision 5 single-body rounded-keel buoy |
| Embedded controller | ESP32 DevKit / ESP-WROOM-32 class |
| Selected edge computer | Orange Pi Zero 3, 4 GB; not yet physically installed |
| Current edge host | Development laptop |
| Data state | Simulator operational; physical-sensor integration incomplete |
| AI state | Presentation forecast; not field-trained or safety validated |

This document explains what Project FALCON is, what currently works in the
repository, what remains simulated or provisional, how to run the system on
Linux Mint, and what evidence is still required before field deployment.
[`PROJECT_CONTEXT.md`](PROJECT_CONTEXT.md) remains the engineering authority if
this summary conflicts with another project document.

## 1. Project Purpose

Project FALCON is a local-first coastal monitoring buoy prototype intended to:

1. collect near-real-time coastal measurements;
2. estimate wave height from synchronized water-pressure and motion data;
3. provide AI-assisted wave-height forecasts five to fifteen minutes ahead;
4. classify sea condition as Calm, Moderate, or Rough; and
5. present measurements, system health, history, alerts, and forecast evidence
   through a locally hosted dashboard.

Phase 1 does not claim autonomous navigation, official weather forecasting,
storm or typhoon prediction, water-quality analysis, cloud dependence, or a
field-certified safety system.

## 2. Current System Architecture

```text
Approved sensors
    |
    v
ESP32 acquisition and diagnostics
    |  USB/UART newline JSON (preferred prototype path)
    |  local Wi-Fi/HTTP (development alternate)
    v
Orange Pi Zero 3 target / development laptop today
    |-- validation and deterministic alerts
    |-- SQLite telemetry and event history
    |-- presentation wave forecast and backtesting
    |-- REST API on port 8765
    `-- bundled React dashboard on port 8765 (Vite port 5173 in development)
```

The ESP32 remains responsible for deterministic acquisition, basic validation,
sensor health, and telemetry framing. The edge host owns storage, API serving,
forecasting, alert aggregation, and dashboard hosting.

## 3. Implementation Status

| Subsystem | Current state | Evidence / limitation |
| --- | --- | --- |
| ESP32 build | Implemented and buildable | PlatformIO `esp32dev`, Arduino framework |
| Captive portal | Implemented | AP `FALCON-01`, DNS/HTTP dashboard and controls |
| Sensor diagnostics | Implemented foundation | I2C detection, SPI/UART setup, JSON health frames |
| Physical sensor values | Not complete | Dedicated production drivers and hardware validation pending |
| USB/UART telemetry | Protocol and edge reader implemented | Version 1 newline JSON; physical link test pending |
| Edge simulator | Implemented | Generates coherent presentation telemetry and fault scenarios |
| Edge storage | Implemented | SQLite telemetry, predictions, alerts, and events |
| REST API | Implemented prototype | `/status`, `/wave`, `/gps`, `/battery`, `/solar`, `/ai`, logs and controls |
| Dashboard Next | Implemented development UI | React/TypeScript/Vite; responsive multi-page dashboard |
| AI forecast | Implemented presentation model | Damped short-horizon trend; not a trained field model |
| Wokwi wiring | Implemented visual baseline | Custom unsupported parts are visual-only |
| Mechanical CAD | Extensive parametric concepts | Final manufactured assembly and physical verification pending |
| Power system | Calculated provisional baseline | No complete marine power system has been assembled/tested |
| Marine validation | Not started | Ingress, stability, mooring, endurance, calibration, and trials required |

## 4. Approved Phase 1 Hardware

### 4.1 Processing

- ESP32 DevKit / ESP-WROOM-32 class controller;
- Orange Pi Zero 3, 4 GB as the selected edge host;
- high-endurance microSD storage; and
- USB serial as the preferred initial ESP32-to-edge connection.

### 4.2 Sensors

| Function | Selected prototype device | Interface | Status |
| --- | --- | --- | --- |
| Motion/orientation | Adafruit BNO085 | SPI | Selected; physical validation pending |
| Water pressure | Blue Robotics Bar02 | I2C `0x76` | Selected; physical validation pending |
| Position/time | Adafruit Ultimate GPS class | UART2 | Selected; exact purchased revision pending |
| Battery monitoring | INA260 | I2C `0x40` | Selected |
| Solar monitoring | Second INA260 | I2C `0x41` | Selected; address jumper required |
| Enclosure temperature | MCP9808 | I2C `0x18` | Selected |
| Wind direction ADC | ADS1115 | I2C `0x48`, A0 | Selected |
| Wind speed/direction | SparkFun SEN-15901 prototype kit | Pulse + resistor ladder | Selected for prototype, not proven marine-durable |
| Water temperature | Sealed DS18B20 | OneWire | Optional |
| Leak/tamper | Exact detector TBD | Digital input | Planned |

BNO085 uses SPI because its documented I2C behavior is unreliable with ESP32.
Bar02 is preferred over Bar30 for shallow-wave work because its range and depth
resolution better fit the intended experiment. Bar02 still requires correct
bulkhead sealing and regular maintenance; it is not automatically suitable for
permanent immersion merely because its sensor face is water exposed.

### 4.3 ESP32 Pin Baseline

| Function | GPIO |
| --- | ---: |
| Shared I2C SDA / SCL | 21 / 22 |
| BNO085 SPI SCK / MISO / MOSI | 18 / 19 / 23 |
| BNO085 CS / INT / RST | 13 / 27 / 14 |
| GPS UART2 RX / TX | 16 / 17 |
| Anemometer pulse | 25 |
| Optional DS18B20 | 26 |
| Leak/tamper | 32 |
| Reserved fan PWM driver | 33 |

GPIO 0, 2, 5, 12, and 15 remain unused in the baseline because they are ESP32
strapping pins. GPIO 1 and 3 remain available for programming/logging. See
[`PINOUT.md`](PINOUT.md) before connecting physical hardware.

## 5. Electrical and Power Baseline

```text
Solar panel -> LiFePO4 MPPT -> 12.8 V 20 Ah LiFePO4 battery
                                   |
                                   +-> main fuse and disconnect
                                   +-> dedicated regulated 5 V / >=3 A Orange Pi branch
                                   `-> separate regulated 5 V ESP32/sensor branch
```

Preferred prototype solar capacity is 80 W; 60 W is the supervised-test
minimum. The 20 Ah battery stores approximately 256 Wh nominal and about
205 Wh at an 80% usable assumption. Estimated no-solar runtime is about 34 hours
at 6 W average load, 26 hours at 8 W, or 20 hours at 10 W. These figures are
calculations, not measured endurance results.

The current raw procurement estimate is PHP 36,600–60,550. A practical landed
budget is PHP 42,000–79,000. See [`HARDWARE_BOM.md`](HARDWARE_BOM.md) and
[`POWER_CALCULATIONS.md`](POWER_CALCULATIONS.md). Final fuse values, conductor
sizes, connector ratings, and solar protection require exact purchased products
and measured current.

## 6. ESP32 Firmware

Relevant source files:

- `src/main.cpp` — firmware entry point;
- `src/portal_server.cpp/.h` — AP, captive portal, local HTTP API and controls;
- `src/system_state.cpp/.h` — current ESP32 portal status state;
- `src/sensor_diagnostics.cpp/.h` — hardware probes and telemetry frames; and
- `include/config.h` — network settings, pins, addresses, and timing.

At startup, diagnostics:

- initialize I2C on GPIO21/22;
- initialize BNO085 SPI wiring;
- start GPS UART2 at 9600 baud;
- configure anemometer, optional temperature, leak, and fan pins;
- probe Bar02, both INA260 devices, MCP9808, and ADS1115 addresses; and
- emit a versioned diagnostic telemetry frame every two seconds.

The diagnostics report devices as detected, not detected, untested, or waiting.
They deliberately leave `measurements` empty until actual drivers produce valid
values. Detection is not equivalent to calibration or measurement validation.

## 7. Telemetry Contract

The ESP32 prototype uses UTF-8 newline-delimited JSON at 115200 baud:

```json
{"protocol":"falcon.telemetry","version":1,"sequence":7,"uptimeMs":4200,"source":"hardware-diagnostic","monitoring":true,"sensors":{"bar02":"DETECTED","bno085":"UNTESTED"},"measurements":{}}
```

The edge reader validates protocol name, version, sequence, and measurement
shape. Unsupported or malformed frames are rejected. Sequence gaps expose lost
frames. Physical serial testing, reconnect policy, clock synchronization, and
field error-rate characterization remain pending.

## 8. Edge Service

The Python service under `edge/falcon_edge/` provides:

- simulator, ESP32 HTTP, and ESP32 serial data sources;
- deterministic health and alert rules;
- SQLite persistence;
- short-horizon wave forecast and forecast-versus-actual history;
- static dashboard serving; and
- local REST endpoints.

The simulator includes Normal, Rough Sea, Low Battery, Overheating, and Sensor
Fault scenarios. Transitions are gradual to avoid unrealistic graph steps.
Simulator results must always remain labeled as simulated.

### REST endpoints

```text
GET  /status
GET  /wave
GET  /gps
GET  /battery
GET  /solar
GET  /ai?horizon=5
GET  /ai?horizon=15
GET  /prediction?horizon=10   development presentation extension
GET  /logs?limit=60
POST /restart
POST /calibrate
```

Legacy `/api/...` compatibility routes still exist for the presentation UI.

## 9. Dashboard

`dashboard-next/` is the canonical React + TypeScript dashboard. It has:

- Overview mission control;
- Wave AI measured/history/forecast presentation;
- Motion digital twin and animated sea;
- GPS map, reference point, geofence and drift status;
- Battery, solar, temperature and fan views;
- System Health and sensor availability;
- Alerts and browser notifications;
- searchable Logs with CSV/JSON export; and
- local Settings and presentation scenarios.

The UI is responsive and supports light/dark themes. Its values currently come
primarily from the edge simulator. `dashboard-next/` is the only full dashboard;
its bundled build is served by the edge host from `edge/static/dashboard/`.
`data/` contains only the lightweight ESP32 setup/diagnostic portal because the
React/3D application is not intended to fit in the ESP32 LittleFS partition.

## 10. AI and Wave Forecast

The current model is a transparent presentation forecast derived from recent
wave-height history. It supports short horizons and stores predictions for
later comparison. It is useful for dashboard and pipeline development, but it
is not evidence that a field AI model is accurate.

A final model requires synchronized pressure and IMU trials, raw-data retention,
calibration, train/validation/test separation, baseline comparison, error metrics,
confidence behavior, drift monitoring, and documented failure limits. The only
approved AI target is wave height; operational sensors are context, not separate
prediction targets.

## 11. Mechanical Baseline

Revision 5 uses a compact traditional single-body concept:

- approximately 650 mm main HDPE body;
- rounded tapered underwater keel;
- central low ballast;
- single-anchor mooring;
- upper marine electronics pod;
- sensor mast/array; and
- solar-panel support structure.

Fusion 360 scripts provide parametric concepts for the body, frame, mast, pod,
trays, electronics envelopes, protection hardware, cooling, solar structures,
ballast, and mooring components. These scripts and envelopes are design aids,
not manufacturing certification. The older four-stabilizer arrangement is
legacy Revision 4 and must not be mixed into current claims.

## 12. Wiring and Visualization

Available artifacts:

- `diagram.all.json` — complete Wokwi overview;
- `diagram.json` — core BNO085, Bar02 and GPS view;
- `diagram.environment.json` — environmental/wind view;
- `diagram.power.json` — power-monitor/edge view;
- `docs/diagrams/FALCON-01-electronics-wiring.svg` — technical overview; and
- `docs/diagrams/FALCON-01-electronics-wiring-3d.png` — illustrative 3D guide.

Custom Wokwi sensors are visual-only unless a behavior model exists. The 3D PNG
is also illustrative. `PINOUT.md` and purchased-board datasheets remain the
authority for physical connections.

## 13. Linux Mint Development Guide

### 13.1 Run the edge simulator

```bash
cd "/home/ruzz/Documents/PlatformIO/Projects/Project FALCON-01/edge"
python3 -m falcon_edge.service
```

Open `http://127.0.0.1:8765/`.

### 13.2 Run Dashboard Next

Open a second terminal:

```bash
cd "/home/ruzz/Documents/PlatformIO/Projects/Project FALCON-01/dashboard-next"
source "$HOME/.nvm/nvm.sh"
nvm use 22
npm install
npm run dev
```

Open `http://127.0.0.1:5173/`. Keep the edge service running on port 8765 so
Vite can proxy API requests. For the normal production-style workflow, run
`npm run build`, start the edge service, and open `http://127.0.0.1:8765/`.

### 13.3 Build ESP32 firmware

```bash
cd "/home/ruzz/Documents/PlatformIO/Projects/Project FALCON-01"
"$HOME/.platformio/penv/bin/platformio" run
```

Upload only after setting the correct Linux serial port for the actual board.
Windows values such as `COM3` do not work on Linux. Typical Linux devices are
`/dev/ttyUSB0` or `/dev/ttyACM0`, but detect the actual device rather than guess.

### 13.4 Read ESP32 serial telemetry on the edge service

```bash
cd "/home/ruzz/Documents/PlatformIO/Projects/Project FALCON-01"
python3 -m pip install -r edge/requirements-hardware.txt
cd edge
python3 -m falcon_edge.service --source serial --serial-port /dev/ttyUSB0
```

### 13.5 Run automated checks

```bash
cd "/home/ruzz/Documents/PlatformIO/Projects/Project FALCON-01"
"$HOME/.platformio/penv/bin/platformio" run
PYTHONPATH=edge python3 -m unittest discover -s edge/tests -v
cd dashboard-next
source "$HOME/.nvm/nvm.sh"
nvm use 22
npm run build
```

## 14. Current Verification Evidence

At the time of this documentation update:

- ESP32 firmware builds successfully for `esp32dev`;
- firmware usage is approximately 14.1% RAM and 65.0% flash;
- all four Wokwi diagram files pass connection/pin linting, with only the
  informational legacy-part notice for the Wokwi ESP32 visual type;
- the edge test suite contains 18 passing tests; and
- recent Dashboard Next production builds pass with a non-fatal large-chunk
  warning related to the Three.js motion page.

These software results do not replace physical electrical or marine testing.

## 15. Safety, Security, and Deployment Limits

- Never connect raw 12.8 V or a 5 V signal to ESP32 GPIO.
- Orange Pi must use its own stable regulated 5 V supply.
- Do not drive fans or other loads directly from ESP32 pins.
- Validate buck outputs with a meter before connecting electronics.
- Fuse the battery close to its positive terminal with DC-rated protection.
- Change the prototype Wi-Fi password before deployment.
- Do not expose maintenance endpoints to an untrusted network.
- Do not deploy unattended until waterproofing, thermal, electrical, mooring,
  stability, calibration, endurance, and fault tests pass.
- Do not use simulator or presentation-AI output for safety decisions.

## 16. Remaining Work and Recommended Order

1. Purchase and photograph exact boards/components.
2. Bench-test ESP32 alone and record its Linux serial device.
3. Integrate BNO085 SPI driver and validate quaternion/roll/pitch/yaw.
4. Integrate Bar02 driver, establish pressure baseline, and calibrate depth.
5. Add GPS parsing, INA260, MCP9808, ADS1115, wind pulse, and optional DS18B20
   drivers one at a time.
6. Populate real `measurements` fields while preserving validity/status metadata.
7. Validate serial reconnects, sequence gaps, stale data, and Orange Pi startup.
8. Freeze exact power products, recalculate fuses/wires, and complete 24/72-hour
   endurance testing.
9. Update Fusion envelopes using measured purchased-part dimensions.
10. Perform controlled tank/coastal calibration and synchronized pressure/IMU trials.
11. Train and evaluate the field model only after sufficient validated data exists.
12. Complete ingress, thermal, stability, mooring, recovery, and supervised sea trials.

## 17. Documentation Map

| Topic | Detailed document |
| --- | --- |
| Engineering authority | [`PROJECT_CONTEXT.md`](PROJECT_CONTEXT.md) |
| Roadmap | [`ROADMAP.md`](ROADMAP.md) |
| Hardware | [`HARDWARE.md`](HARDWARE.md) |
| Procurement | [`HARDWARE_BOM.md`](HARDWARE_BOM.md) |
| Pin assignments | [`PINOUT.md`](PINOUT.md) |
| Wiring | [`ELECTRONICS_WIRING.md`](ELECTRONICS_WIRING.md) |
| Pod layout | [`ELECTRONICS_LAYOUT.md`](ELECTRONICS_LAYOUT.md) |
| Power | [`POWER_SYSTEM.md`](POWER_SYSTEM.md), [`POWER_CALCULATIONS.md`](POWER_CALCULATIONS.md) |
| Firmware/software | [`FIRMWARE_SPEC.md`](FIRMWARE_SPEC.md), [`SOFTWARE.md`](SOFTWARE.md) |
| Telemetry | [`NETWORK_PROTOCOL.md`](NETWORK_PROTOCOL.md) |
| Edge host | [`ORANGE_PI_EDGE.md`](ORANGE_PI_EDGE.md) |
| API | [`API.md`](API.md) |
| Dashboard | [`DASHBOARD.md`](DASHBOARD.md) |
| AI | [`AI.md`](AI.md) |
| Mechanical | [`MECHANICAL.md`](MECHANICAL.md) |
| Calibration/tests | [`CALIBRATION_GUIDE.md`](CALIBRATION_GUIDE.md), [`TEST_PLAN.md`](TEST_PLAN.md) |
| Deployment and safety | [`DEPLOYMENT_GUIDE.md`](DEPLOYMENT_GUIDE.md), [`SECURITY.md`](SECURITY.md) |

## Revision History

| Version | Date | Change |
| --- | --- | --- |
| 1.0 | 2026-08-15 | Consolidated actual repository state, setup, evidence, limitations, and next gates. |
