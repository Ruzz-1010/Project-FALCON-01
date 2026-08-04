# PROJECT FALCON-01 — MASTER PROJECT CONTEXT

## 1. Official Project Identity

**Project Name:** Project FALCON  
**Prototype Name:** FALCON-01  
**Meaning:** **Fullbright College's AI-powered Live Coastal Observation Network**

**Current working thesis direction:**  
Design and development of an AI-assisted, solar-powered smart ocean buoy for real-time coastal monitoring, short-term environmental prediction, and anti-theft protection.

**Primary branding line:**  
**Project FALCON-01 — AI-Powered Smart Ocean Buoy**

**Core purpose:**  
To build a practical smart ocean buoy that collects coastal and environmental data, performs local monitoring, supports future AI-based sea-condition classification or short-term prediction, and provides anti-theft protection through location and movement monitoring.

---

## 2. Current Development Strategy

The project will be developed in stages.

### Local-first development
The first working system is the **local ESP32-based dashboard**.

When a user is near the buoy:

1. The ESP32 creates its own Wi-Fi access point.
2. The user connects to the Wi-Fi network named `FALCON-01`.
3. A captive portal automatically opens.
4. The browser displays the local FALCON dashboard.
5. No internet connection and no mobile app are required.

### Future remote access
A separate mobile application may be developed later for remote monitoring.

The intended future flow is:

```text
Sensors → ESP32 / onboard controller → LoRa or cellular communication
       → cloud/database → FALCON mobile application
```

The local website and future mobile app should use similar data structures and API naming so both systems remain consistent.

---

## 3. Confirmed Hardware and Development Setup

### Current confirmed controller
- ESP32 DevKit / ESP-WROOM-32
- USB-to-serial chip detected as CH340
- Windows driver: CH340/CH341
- Current serial port used during testing: COM3
- The ESP32 has already passed the built-in LED blink test.
- Uploading may require holding the BOOT button when the uploader shows `Connecting...`.

### Current available parts
- ESP32 development board
- Jumper wires
- LM2596 adjustable DC-DC buck converter
- Relay module
- USB/DC power modules
- Adjustable DC power module
- Extra ESP8266/NodeMCU or other development boards may be available, but the ESP32 remains the main controller.

### Recommended future sensor and communication modules
These are planned and not yet physically available:

- Waterproof DS18B20 water-temperature sensor
- MPU6050 or preferably BNO055/another suitable IMU for tilt and motion
- GPS module such as NEO-6M or NEO-M8N
- INA219 or similar voltage/current sensor
- Solar charging and battery-monitoring hardware
- LoRa module such as SX1278, or a cellular module where coverage is available
- Optional pH, TDS, salinity, turbidity, dissolved oxygen, or other water-quality sensors depending on final thesis scope

### Power concept
- Solar-powered buoy
- Rechargeable battery
- Charge controller
- DC regulation for ESP32 and sensors
- The LM2596 may be used to step down a higher battery voltage to a suitable regulated voltage.
- Final battery chemistry, capacity, solar-panel wattage, and marine-grade protection must still be finalized.

### Protection requirements
All electronics must be protected from seawater, salt air, condensation, corrosion, and mechanical shock.

Planned protection includes:
- IP67/IP68 enclosure where practical
- Proper cable glands
- Corrosion-resistant connectors
- Conformal coating where appropriate
- Desiccant or condensation-management strategy
- Separate sensor openings or probes without exposing the main electronics
- Secure mounting inside the buoy body

---

## 4. Software Development Environment

### Preferred environment
- Visual Studio Code
- PlatformIO extension
- Arduino framework for ESP32

### Current PlatformIO configuration

```ini
[env:esp32dev]
platform = espressif32
board = esp32dev
framework = arduino

monitor_speed = 115200
upload_speed = 115200
upload_port = COM3
monitor_port = COM3

board_build.filesystem = littlefs
```

The COM port may change on another computer or after reconnecting the board.

### Core libraries currently used
These are available with the ESP32 Arduino framework:
- `Arduino.h`
- `WiFi.h`
- `WebServer.h`
- `DNSServer.h`
- `LittleFS.h`

No external library is required for the current local captive-portal version.

---

## 5. Current Local Network Design

### Wi-Fi access point
- **SSID:** `FALCON-01`
- **Password:** `falcon123`
- **Default ESP32 AP address:** `192.168.4.1`

The password is temporary and should later be configurable.

### Captive portal behavior
The ESP32 runs a DNS server that redirects domain requests to its local IP address.

The firmware supports common captive-portal detection paths for:
- Android
- Windows
- Apple devices
- Firefox and other browsers

Examples of handled paths:
- `/generate_204`
- `/gen_204`
- `/connecttest.txt`
- `/redirect`
- `/ncsi.txt`
- `/hotspot-detect.html`
- `/library/test/success.html`
- `/canonical.html`
- `/success.txt`

The portal already works automatically during local testing.

### Known limitation
Automatic browser pop-up depends on the phone or operating system. The portal should still be reachable through:

```text
http://192.168.4.1
```

or by opening an ordinary HTTP page while connected to the FALCON Wi-Fi.

---

## 6. Current Web Dashboard Direction

### Dashboard name
**FALCON Local Dashboard**

### Current version direction
**FALCON Local Dashboard v2**

### Design style
- Dark ocean theme
- Marine-tech appearance
- Glassmorphism-inspired panels
- Responsive layout for Android phones and laptops
- Professional thesis/demo presentation
- Clean, modern, commercial-looking interface
- FALCON branding visible in the header

### Current dashboard sections
- System status
- Connected devices
- System uptime
- Monitoring status
- Battery status
- Water temperature
- GPS status/location
- Sea condition
- Tilt
- Wave level
- Solar status
- Anti-theft status
- Wi-Fi network information
- Last update timestamp
- Start/Stop Monitoring button
- Restart ESP32 button

### Temporary demo data
Until sensors are connected, sample values may be shown for:
- Battery percentage
- Water temperature
- Tilt
- Wave level
- Sea condition
- Solar status
- Security status

Demo values must be clearly treated as simulated data and replaced with real sensor readings later.

---

## 7. Current API Design

The local dashboard communicates with the ESP32 using HTTP endpoints.

### Existing/confirmed endpoints

#### `GET /api/status`
Returns current dashboard data.

Example:

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

#### `POST /api/monitoring/toggle`
Starts or stops monitoring.

#### `POST /api/restart`
Restarts the ESP32.

### Planned future endpoints
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

These endpoints are proposals and may change as hardware is finalized.

---

## 8. Current Project Folder Structure

```text
FALCON-01/
├── PROJECT_CONTEXT.md
├── README.md
├── HARDWARE.md
├── API.md
├── ROADMAP.md
├── platformio.ini
├── src/
│   └── main.cpp
├── data/
│   ├── index.html
│   ├── style.css
│   └── app.js
├── include/
├── lib/
└── docs/
```

### Current responsibility of each file
- `PROJECT_CONTEXT.md` — master source of truth for Codex, ChatGPT, and developers
- `README.md` — quick project overview and setup
- `HARDWARE.md` — components, wiring, power, enclosure, and sensor planning
- `API.md` — current and planned local API definitions
- `ROADMAP.md` — development phases and milestones
- `src/main.cpp` — ESP32 firmware, Wi-Fi AP, captive portal, API routes
- `data/index.html` — dashboard HTML structure
- `data/style.css` — dashboard visual design
- `data/app.js` — live API polling and interface controls

---

## 9. Firmware Architecture Direction

The first version may remain simple, but the long-term firmware should become modular.

Proposed future structure:

```text
src/
├── main.cpp
├── config.h
├── wifi_manager.cpp
├── wifi_manager.h
├── captive_portal.cpp
├── captive_portal.h
├── api_server.cpp
├── api_server.h
├── sensor_manager.cpp
├── sensor_manager.h
├── gps_manager.cpp
├── gps_manager.h
├── imu_manager.cpp
├── imu_manager.h
├── power_manager.cpp
├── power_manager.h
├── security_manager.cpp
├── security_manager.h
├── storage_manager.cpp
├── storage_manager.h
├── ai_engine.cpp
└── ai_engine.h
```

The code should:
- Avoid unnecessary blocking delays
- Use clear constants and configuration files
- Validate sensor readings
- Handle missing sensors without crashing
- Use JSON responses consistently
- Keep the dashboard responsive
- Allow future addition of OTA updates
- Support low-power operation later
- Log important events and errors

---

## 10. Planned Sensor Functions

### Water temperature
- Read using a waterproof temperature probe
- Display in degrees Celsius
- Validate disconnected-sensor and out-of-range conditions

### Motion, tilt, and sea condition
- Read acceleration and orientation from an IMU
- Calculate tilt
- Detect abnormal movement
- Estimate a simple wave/motion level
- Support future sea-condition classification

Important: a low-cost IMU does not directly and accurately measure true ocean wave height without calibration and signal processing. Early values should be labeled as motion level or estimated wave activity until validated.

### GPS
- Display latitude and longitude
- Record the buoy’s reference/home position
- Support geofencing
- Detect suspicious displacement
- Support future map display in the app or internet-connected dashboard

### Battery and solar
- Measure voltage and current
- Estimate battery percentage
- Show charging status
- Detect low battery
- Support power-saving decisions

### Optional water-quality measurements
Only include these after final scope approval:
- pH
- Salinity/TDS
- Turbidity
- Dissolved oxygen
- Conductivity

Sensor accuracy, marine suitability, calibration, and maintenance requirements must be considered before inclusion.

---

## 11. AI Direction

The project should use a practical AI feature rather than adding AI only for branding.

### Preferred practical AI scope
**AI-based sea-condition classification using sensor data**

Possible inputs:
- Accelerometer readings
- Gyroscope readings
- Tilt
- Motion variance
- Water temperature
- Wind or pressure data if later added
- Historical sensor windows

Possible output classes:
- Calm
- Moderate
- Rough
- Abnormal movement

### Implementation options
- Train a lightweight model externally, then deploy a TinyML model to the ESP32
- Use a Raspberry Pi only if the final model or processing becomes too heavy
- Keep the ESP32 responsible for sensors, local networking, and power management

### Important rule
AI output must be based on collected and labeled data, not random thresholds presented as AI. A threshold-based prototype may be used first, but it must be labeled as rule-based until a trained model is implemented.

---

## 12. Anti-Theft Protection Direction

Planned anti-theft functions:
- GPS geofence
- Movement detection through IMU
- Anchor or home-location reference
- Armed/disarmed status
- Local alert display
- Future mobile notification
- Future remote location reporting
- Optional buzzer or alarm output
- Optional tamper switch for enclosure opening

Possible alert conditions:
- Buoy moves beyond the allowed geofence
- Sudden abnormal movement
- Device is tilted beyond a safety threshold
- Enclosure is opened
- GPS signal disappears after suspicious movement
- Battery or power cable is disconnected

The final design should avoid false alarms caused by normal waves and tides.

---

## 13. Local and Remote Product Roles

### Local dashboard
Best for:
- Installation
- Maintenance
- Calibration
- Near-buoy checks
- Sensor diagnostics
- Viewing live data without internet
- Restarting or changing settings

### Future mobile app
Best for:
- Remote monitoring
- Push notifications
- Historical charts
- Cloud data
- Geofence alerts
- Viewing multiple FALCON buoys
- User accounts and permissions

The local dashboard must remain usable even if the future cloud service or mobile application is unavailable.

---

## 14. Upload and Testing Workflow

### Firmware upload
Use PlatformIO normal upload for changes to `src/main.cpp` or other firmware files.

### Filesystem upload
Use:

```text
PlatformIO: Upload Filesystem Image
```

after changing:
- `data/index.html`
- `data/style.css`
- `data/app.js`
- any other files stored in LittleFS

### Test sequence
1. Connect ESP32 to computer.
2. Build firmware.
3. Upload filesystem image when web files changed.
4. Upload firmware.
5. Open PlatformIO Serial Monitor at 115200 baud.
6. Confirm LittleFS mounted.
7. Confirm AP started.
8. Connect phone to `FALCON-01`.
9. Keep the phone connected despite “No internet.”
10. Confirm captive portal appears.
11. Confirm dashboard loads and updates.
12. Test monitoring toggle.
13. Test restart button.
14. Repeat reconnect tests.

---

## 15. Current Milestones

### Completed
- ESP32 identified and powered
- CH340 driver identified and installed
- COM port working
- Blink test successful
- PlatformIO chosen
- ESP32 Wi-Fi access point established
- Captive portal established
- Automatic portal pop-up confirmed
- Initial local dashboard concept established
- LittleFS-based web structure planned

### In progress
- FALCON Local Dashboard v2 design
- Separating HTML, CSS, and JavaScript into LittleFS files
- Improving professional UI
- Building stable local API structure

### Not yet completed
- Real sensors
- GPS
- IMU
- Battery/solar monitoring
- Data logging
- AI model
- LoRa or cellular communication
- Cloud backend
- Mobile application
- Final marine enclosure
- Field testing
- Calibration and validation

---

## 16. Development Roadmap

### Phase 1 — Controller and local system
- ESP32 test
- PlatformIO setup
- Wi-Fi AP
- Captive portal
- Local dashboard
- Basic local controls
- Stable reconnect behavior

### Phase 2 — Dashboard foundation
- LittleFS web files
- Responsive UI
- Live API polling
- Sensor placeholders
- Error states
- Settings structure
- Local data export concept

### Phase 3 — Core sensors
- Waterproof water temperature
- IMU
- Battery voltage/current
- Solar voltage/current
- Sensor status detection
- Calibration pages

### Phase 4 — Navigation and security
- GPS
- Reference/home position
- Geofence
- Movement/tamper alerts
- Local security controls
- Alert logging

### Phase 5 — Data logging
- Timestamped readings
- Local storage
- CSV/JSON export
- Historical charts
- Memory management

### Phase 6 — AI sea-condition classification
- Data collection
- Dataset labeling
- Feature extraction
- Model training
- Validation
- TinyML deployment or Raspberry Pi integration

### Phase 7 — Remote communication
- LoRa or cellular selection
- Data transmission
- Remote command security
- Offline buffering
- Communication reliability testing

### Phase 8 — Cloud and mobile app
- Backend API
- Database
- User authentication
- Mobile dashboard
- Notifications
- Multiple-buoy support

### Phase 9 — Marine prototype and field validation
- Solar power integration
- Waterproof enclosure
- Corrosion protection
- Buoyancy and stability
- Anchoring
- Coastal deployment
- Accuracy and reliability evaluation

---

## 17. Coding and Design Rules for Codex

Codex should follow these rules whenever modifying the project:

1. Read this file before making changes.
2. Do not rename Project FALCON or FALCON-01.
3. Keep the official meaning:
   **Fullbright College's AI-powered Live Coastal Observation Network.**
4. Keep the system local-first and offline-capable.
5. Preserve captive-portal behavior.
6. Do not add unnecessary external libraries.
7. Keep code compatible with ESP32 Arduino and PlatformIO.
8. Do not remove existing API endpoints without documenting a replacement.
9. Separate firmware logic from web interface files.
10. Use responsive design for Android and laptop screens.
11. Keep the visual style dark, marine, modern, and professional.
12. Clearly label simulated values as demo data.
13. Never present rule-based thresholds as a trained AI model.
14. Add error handling for missing files, failed AP startup, and sensor errors.
15. Avoid exposing passwords or sensitive future cloud credentials in source files.
16. Preserve a path for future sensors, GPS, anti-theft, AI, LoRa/cellular, cloud, and app integration.
17. Update this context file and relevant documentation after major architecture changes.

---

## 18. Current Decisions That Are Still Open

The following items are not final and must not be treated as confirmed:

- Exact final thesis title wording
- Exact final set of environmental sensors
- Final buoy dimensions and mechanical design
- Final solar-panel wattage
- Final battery type and capacity
- Final long-range communication method
- Whether a Raspberry Pi will be included
- Exact AI model and dataset
- Exact cloud provider and app technology
- Final anti-theft thresholds
- Final water-quality sensor list
- Final production budget

These decisions should be finalized after component research, adviser approval, feasibility review, and testing.

---

## 19. Immediate Next Task

The immediate development task is:

1. Create and verify the LittleFS-based project structure.
2. Place the current dashboard into:
   - `data/index.html`
   - `data/style.css`
   - `data/app.js`
3. Upload the filesystem image.
4. Upload the ESP32 firmware.
5. Confirm that the captive portal still opens automatically.
6. Confirm all dashboard cards and controls function using demo data.
7. Improve the visual design only after the local system remains stable.

---

## 20. Source-of-Truth Rule

This document is the master project context for Project FALCON-01.

When ChatGPT, Codex, or another developer works on the project:
- Read this file first.
- Preserve confirmed decisions.
- Label proposals and unfinished items.
- Update the documentation when a decision becomes final.
- Do not silently replace the current architecture with a different one.

---

## 21. Implemented Firmware Structure

The local dashboard firmware now uses the following confirmed structure:

```text
include/
  config.h              Shared AP, HTTP, DNS, and LittleFS path constants
src/
  main.cpp              Arduino lifecycle entry point
  portal_server.h       Portal server interface and state ownership
  portal_server.cpp     Wi-Fi AP, DNS, captive routes, files, and local APIs
data/
  index.html             Dashboard document
  style.css              Dashboard presentation
  app.js                 Dashboard polling and controls
```

This is an incremental modularization of the existing local-first design. It does
not change the confirmed AP credentials, captive-portal paths, LittleFS storage,
or API contracts. Future sensor managers should provide data to the portal layer
without moving website content into firmware.
