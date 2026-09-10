# Project FALCON Primary Sensor Selection and Architecture Baseline

Revision: 1.1  
Date: 2026-09-10  
Status: adviser-aligned Phase 1 engineering baseline; not yet a fabrication or deployment release

## 1. Purpose

This document freezes the intended function of the Project FALCON primary sensors and identifies the exact products that are acceptable for prototype work, the products recommended for field deployment, and the selections that still require physical validation. The primary measurement scope is limited to pressure-derived wave estimation and wind speed/direction. GPS, power, and security devices are supporting telemetry only.

Project FALCON estimates wave height from a submerged pressure time series. It does not claim that an IMU directly measures wave height. The shore Bay Station stores and processes the pressure data and may run the required wave-height prediction model. The buoy ESP32 performs acquisition, basic validation, buffering, and telemetry.

## 2. System signal flow

```text
Marine environment
  -> pressure and wind sensors
  -> protected sensor interfaces
  -> ESP32 acquisition and validation
  -> LoRa primary buoy link
  -> mobile network or shore LoRa gateway
  -> shore Bay Station
  -> database, pressure-derived wave estimate, AI prediction, dashboard and alerts

Battery and solar branches
  -> INA260 monitors
  -> ESP32 health telemetry

Enclosure switch and optional tamper accelerometer
  -> security-state logic only
```

## 3. Selection status definitions

- **Confirmed prototype** — exact part is selected for bench and supervised prototype testing.
- **Recommended deployment candidate** — exact part is technically preferable for the marine role, but procurement, installation, and field validation are still required.
- **Bench only** — may be used for development but must not be represented as a final marine-deployment component.
- **Optional** — not required for the Phase 1 monitoring claim.
- **TBD** — no exact product is approved; it must not be placed on a fabrication release.

## 4. Sensor and interface decisions

| Function | Exact part and status | Electrical interface | Key specification | Intended placement | Required validation and limitation |
| --- | --- | --- | --- | --- | --- |
| Submerged pressure / wave-height input | **Holykell HPT604 Type A, provisional 0–2 mH2O vented gauge, 4–20 mA — Recommended deployment candidate** | Protected 12 V loop; 150 ohm 0.1% shunt; protected ADS1115 at 3.3 V | Typical accuracy ≤±0.5% FS and response ≤20 ms in the manufacturer sheet; exact order code pending | Submerged at a documented fixed depth; cable vent ends in a protected dry breathable location | Obtain written continuous-saltwater compatibility and exact wetted-material/cable confirmation before purchase. Validate static depth, dynamic response, temperature, drift, fouling, vent/desiccant maintenance, corrosion, ingress and staged field endurance. See `PRESSURE_SENSOR_BASELINE.md`. |
| Short-duration pressure comparison | **Blue Robotics Bar02 R2, BR-100891 — Bench only** | Short protected 3.3 V I2C setup | Low-pressure prototype sensor | Supervised tank/bench fixture only | Manufacturer drying and maximum-immersion limitations prevent use as the unattended long-term deployment baseline. |
| Position and geofence | **Adafruit Ultimate GPS, PID 746 — Confirmed prototype** | 3.0–5.5 V board input; UART NMEA, 9600 baud default; 1–10 Hz update | MTK3339 receiver; use a conservative nominal position accuracy of approximately 3 m until site testing | Upper electronics area with clear sky view; optional external antenna after RF review | Perform cold/warm-start and stationary-position tests at the deployment site. Geofence radius must exceed measured GPS scatter. It is a security aid, not precision theft tracking. |
| Wind speed and direction | **SparkFun Weather Meter Kit, SEN-15901 — Confirmed prototype** | Reed-switch pulse for speed; passive resistor network through a 3.3 V ADC divider for direction | 1 switch closure/s corresponds to 1.492 mph; vane supports up to 16 positions, with eight cardinal directions reliably identified | Highest practical unobstructed mast location, mechanically aligned to true or corrected north | Compare with a reference anemometer and compass. Inspect bearings, contacts, RJ11 leads, and corrosion after salt exposure. Treat as a supervised prototype unless marine durability is demonstrated. The included rain gauge is outside Phase 1 scope. |
| Battery electrical health | **Adafruit INA260, PID 4226 — Confirmed prototype, quantity 1** | I2C; battery monitor target address `0x40`; 3 V/5 V logic | Up to 36 V bus and 15 A continuous on the breakout; integrated 2 mΩ shunt; better than 1% stated accuracy | Protected battery branch, with high-current path and connector temperature reviewed | Compare voltage/current against a calibrated DMM and load at no-load, normal-load, and near-maximum expected load. Do not exceed breakout current or thermal limits. |
| Solar electrical health | **Adafruit INA260, PID 4226 — Confirmed prototype, quantity 1** | I2C; solar monitor target address `0x41`; 3 V/5 V logic | Same as battery monitor | Protected solar/charger branch at a documented measurement point | Validate polarity, address strap, charging-current direction, and agreement with a reference meter over low, normal, and high sunlight/load conditions. |
| Enclosure temperature | **Adafruit MCP9808, PID 1782 — Recommended selection** | 2.7–5.5 V; I2C; target address `0x18` | −40 to 125 °C; typical ±0.25 °C; maximum ±0.5 °C from −20 to 100 °C | In representative enclosure air, away from converters, modem, heatsinks, direct sun-heated walls, and fan exhaust | Compare against a reference thermometer after thermal stabilization; record any offset. The reading represents its mounting location, not every component junction temperature. |
| Enclosure-open state | **Adafruit magnetic contact switch, PID 375 — Recommended prototype selection** | Dry contact to filtered/debounced GPIO; fail-safe wiring preferred | Normally open; closes when magnet is within approximately 13 mm; 100 mA maximum contact rating | Inside the dry enclosure or behind a properly sealed mechanical interface | Verify open/closed logic, magnet alignment, cable fault behavior, hardware/firmware debounce, and false alarms during vibration. The consumer ABS part has no claimed marine enclosure rating. |
| Vibration/tamper aid | **Adafruit LIS3DH breakout, PID 2809 — Optional security candidate** | 3-axis accelerometer; I2C or SPI; use `0x19` or SPI to avoid the MCP9808 `0x18` address | ±2/4/8/16 g selectable range; motion, tap and free-fall functions | Rigidly mounted to the electronics tray if later approved | Not used for wave-height estimation and not required for the Motion page. Ordinary wave motion can cause false tamper events; thresholds and persistence must be learned in supervised tests. |
| Security buzzer | **TBD** | ESP32 GPIO through a transistor/MOSFET driver; flyback protection if inductive | Voltage, current, sound pressure, duty cycle and environmental rating unresolved | Inside or through an approved acoustic/sealed interface | Select only after electrical load, audibility, nuisance-alarm and enclosure tests. Do not drive directly from an ESP32 GPIO. |
| LoRa buoy telemetry | **Exact buoy radio and barangay-hall gateway TBD — Required primary path** | SPI/UART on buoy; gateway network uplink at shore | Regional frequency, antenna, range, packet size, and data rate require approval | Buoy radio inside enclosure; gateway at barangay hall with elevated, clear-view placement | Verify legal regional band, line of sight, obstruction margin, packet loss, latency, gateway power, and recovery behavior. LoRa is not a general Internet link. |
| Bay Station Internet backhaul | **SIM/4G/5G modem/router TBD — Required shore function** | Approved modem/router interface at Bay Station | Provider coverage, data plan, cloud protocol, TLS, and remote-access controls require approval | Barangay-hall Bay Station, not buoy | Verify registration, data usage, cloud upload, remote access, firewall, reconnect, and modem power behavior. |

## 5. Removed and excluded devices

- The BNO085 is removed from the required Phase 1 architecture. Its sensor-fusion complexity is unnecessary for the pressure-based wave estimate.
- Load cell and HX711 anchor-chain tension sensing are removed.
- Salinity/conductivity sensing is not part of the required Phase 1 system.
- The Orange Pi is not installed on the buoy. The current architecture uses a shore Bay Station for storage, processing, AI, API and dashboard services.
- The LIS3DH, if later added, is a security/tamper aid only. It does not restore IMU-based wave measurement.

## 6. Bus and channel allocation baseline

| Interface | Device/channel | Planned allocation | Design note |
| --- | --- | --- | --- |
| Analog loop / I2C ADC | HPT604 via 150 ohm shunt and ADS1115 | Approx. 0.60–3.00 V at 4–20 mA; ADS1115 address `0x48` subject to final bus review | The revised loop interface requires schematic and bench validation; it is not compatible with the old Bar02 connector. |
| I2C 3.3 V, bench only | Bar02 R2 | Verify purchased unit; expected MS5837 family address `0x76` | Short-duration comparison only; confirm with an I2C scan. |
| I2C 3.3 V | INA260 battery | `0x40` | Record physical address strap. |
| I2C 3.3 V | INA260 solar | `0x41` | Record physical address strap. |
| I2C 3.3 V | MCP9808 enclosure | `0x18` | Keep thermal placement representative. |
| I2C 3.3 V | ADS1115 wind direction | `0x48` | 3.3 V divider only; verify ADC range. |
| I2C/SPI optional | LIS3DH security | Prefer `0x19` or SPI | Do not use `0x18`, which conflicts with MCP9808. |
| UART | GPS PID 746 | Dedicated ESP32 UART per approved pinout | Cross TX/RX and verify logic levels. |
| UART or USB | Bay Station SIM/4G/5G modem/router | Shore-side Internet backhaul interface; exact connection TBD | Not installed on buoy and must not share the buoy GPS UART. |
| GPIO pulse | Wind speed | Dedicated interrupt-capable input | Include pull-up, protection, debounce and pulse-rate test. |
| GPIO | Enclosure contact | Filtered/debounced input | Prefer fault-detecting/fail-safe behavior. |

Exact ESP32 GPIO numbers remain governed by `PINOUT.md` and the verified schematic. A documentation table must not override a physically validated pin map.

## 7. Calibration and acceptance plan

### 7.1 Pressure channel

1. Inspect the sensing gel, connector, O-ring/bulkhead and cable before energizing.
2. Record raw pressure at air reference and at multiple known water depths.
3. Compare with a traceable pressure/depth reference and record temperature.
4. Verify no trapped air, leaks, discontinuities, drift or implausible spikes.
5. Freeze the installation-depth offset and pressure-to-wave algorithm version.
6. Report the dashboard value as **Estimated wave height** until the full method is validated.

### 7.2 Temperature channels

Use a stirred bath or stable comparison chamber at a minimum of three points covering the expected range. Allow stabilization, compare against a traceable thermometer, calculate offset and repeatability, and record probe serial number and date. Perform a separate leak/ingress test for the deployed water probe.

### 7.3 Wind channel

Align the vane reference mechanically, verify every expected direction code, and compare speed at several steady points against a reference anemometer. Test cable movement, contact bounce, salt contamination and low-speed startup.

### 7.4 GPS and security

Measure stationary GPS scatter over time in clear sky and realistic installation conditions. Select geofence and persistence values from that evidence. Exercise the enclosure switch and any optional accelerometer during normal waves, maintenance, intentional opening and simulated tampering; ordinary motion must not create a theft alarm.

### 7.5 Electrical health

Compare both INA260 channels against a calibrated DMM and controlled load. Confirm current direction, bus voltage, address, alert behavior, connector heating and measurement error. Thermal-test the MCP9808 placement with the modem transmitting and converters at normal load.

## 8. Procurement and release gates

Before ordering or PCB fabrication, record for every installed item:

- manufacturer, exact product/SKU, board revision and supplier;
- official datasheet URL and archived copy;
- measured dimensions, connector and pinout;
- supply voltage, logic level, normal and peak current;
- environmental and ingress limitations;
- footprint and 3D-model match;
- calibration equipment and acceptance limits;
- spare quantity and lead time.

The final PCB release is blocked until the buzzer, LoRa interface, connector variants, footprints, cable glands, current budget and enclosure integration are physically verified. A rendered PCB or 3D model is not proof of electrical or mechanical validation.

## 9. Primary manufacturer references

1. Holykell. [HPT604 Type A level-sensor datasheet](https://www.holykell.com/wp-content/uploads/2023/08/HPT604A-Level-sensor-Datasheet-Holykell-V26-CS-1.pdf).
2. Holykell. [HPT604 product family](https://www.holykell.com/products/HPT604-H_Water_Level_Sensor_with_Economical_Model.html).
3. Blue Robotics. [Bar sensor technical guide](https://bluerobotics.com/learn/bar-sensors-guide/).
4. Adafruit. [Ultimate GPS breakout, PID 746](https://www.adafruit.com/product/746).
5. GlobalTop Technology. [PA1616S GPS module datasheet](https://cdn-shop.adafruit.com/product-files/746/CD%20PA1616S%20Datasheet.v03.pdf).
6. SparkFun. [Weather Meter Kit, SEN-15901](https://www.sparkfun.com/weather-meter-kit.html).
7. SparkFun. [Weather Meter Kit datasheet](https://cdn.sparkfun.com/assets/d/1/e/0/6/DS-15901-Weather_Meter.pdf).
9. Adafruit. [INA260 current, voltage and power sensor, PID 4226](https://www.adafruit.com/product/4226).
10. Adafruit. [MCP9808 precision temperature sensor, PID 1782](https://www.adafruit.com/product/1782).
11. Adafruit. [LIS3DH triple-axis accelerometer, PID 2809](https://www.adafruit.com/category/682).
12. STMicroelectronics. [LIS3DH datasheet](https://cdn-shop.adafruit.com/datasheets/LIS3DH.pdf).
13. Adafruit. [Magnetic contact switch, PID 375](https://www.adafruit.com/product/375).
14. Waveshare. [SIM7600G-H 4G HAT](https://www.waveshare.com/product/iot-communication/sim7600g-h-4g-hat.htm).

## 10. Thesis-safe summary

The Phase 1 deployment candidate is an exact-configuration HPT604 4–20 mA pressure channel for estimated wave height plus wind speed/direction. Bar02 is limited to short-duration bench comparison. GPS, electrical-health, enclosure, and security values are supporting telemetry only. Pressure time series are processed at the shore Bay Station to estimate wave height and support AI prediction. No hardware is described as deployment-ready until procurement confirmation, revised-interface review, calibration, ingress, LoRa, Bay Station Internet backhaul, environmental and integration tests are complete.
