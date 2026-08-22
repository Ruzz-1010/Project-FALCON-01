# Project FALCON Animated Demo

Format: 150 seconds, English on-screen text, background music only, 1920×1080 at 24 fps.

The V2 presentation uses continuous motion rather than static slides: the approved
buoy heaves and rolls with layered waves, wind crosses the mast, the wind sensor
spins, sensor values update live, and moving data pulses follow the complete path
from the sensors to ESP32, USB, Orange Pi, cloud, and dashboard.

| Time | Sequence |
| --- | --- |
| 0:00–0:12 | Approved prototype and project introduction |
| 0:12–0:30 | Ocean movement and environmental sensing |
| 0:30–0:48 | IMU, pressure, GPS, and wind acquisition |
| 0:48–1:07 | Sensor signals converge at the ESP32 |
| 1:07–1:23 | ESP32 transfers telemetry to Orange Pi through USB |
| 1:23–1:43 | Orange Pi validation, feature extraction, AI prediction, and alerts |
| 1:43–2:01 | Internet/cloud delivery with local buffering |
| 2:01–2:20 | Dashboard metrics and measured/predicted wave display |
| 2:20–2:27 | Complete connected data journey |
| 2:27–2:30 | Project closing frame |

The only exterior buoy representation is
`assets/falcon-approved-prototype.png`, supplied and approved by the project
owner. The electronics image is used strictly as an internal data-path diagram.
