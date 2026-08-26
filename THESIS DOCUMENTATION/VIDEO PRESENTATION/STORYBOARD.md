# Project FALCON Animated Demo

> **ON HOLD:** This storyboard describes the previous prototype and data story. Replace its exterior reference and placement only after the new prototype is approved. It must not be rendered as the current design.

Format: 150 seconds, English on-screen text, background music only, 1920×1080 at 24 fps.

The previous V2 presentation concept used continuous motion rather than static slides: the reference
buoy heaves and rolls with layered waves, wind crosses the mast, the wind sensor
spins, sensor values update live, and moving data pulses follow the complete path
from the sensors to ESP32, USB, Orange Pi, cloud, and dashboard.

| Time | Sequence |
| --- | --- |
| 0:00–0:12 | Approved replacement prototype and project introduction (create only after approval) |
| 0:12–0:30 | Ocean movement and environmental sensing |
| 0:30–0:48 | Pressure, GPS, wind, water-temperature, power, and security acquisition |
| 0:48–1:07 | Sensor signals converge at the ESP32 |
| 1:07–1:23 | ESP32 transfers telemetry to Orange Pi through USB |
| 1:23–1:43 | Orange Pi validation, local storage, estimated-wave processing, and alerts |
| 1:43–2:01 | Local API and dashboard delivery; optional Internet synchronization is secondary |
| 2:01–2:20 | Dashboard metrics and pressure-based estimated-wave display |
| 2:20–2:27 | Complete connected data journey |
| 2:27–2:30 | Project closing frame |

The old `assets/falcon-approved-prototype.png` is retained only as a reference and must be replaced. The new video must show no required BNO085, no required AI forecast, and no mandatory cloud dependency.
