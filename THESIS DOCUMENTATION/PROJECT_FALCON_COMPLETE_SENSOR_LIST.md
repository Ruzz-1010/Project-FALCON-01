# Project FALCON Complete Sensor List

## Document Status

This document separates the approved Phase 1 sensor baseline from optional and
future upgrades. Physical integration and calibration are still pending. A sensor
must not be described as installed, accurate, or field-validated until supporting
test evidence is available.

## 1. Main Phase 1 Sensors

These sensors provide the primary coastal, movement, location, and weather
observations required by Project FALCON.

| No. | Sensor | Selected component | Interface | Primary measurements and purpose |
| ---: | --- | --- | --- | --- |
| 1 | Inertial Measurement Unit | Adafruit BNO085 | SPI preferred | Roll, pitch, yaw, acceleration, orientation, and buoy-motion features |
| 2 | Water-pressure sensor | Blue Robotics Bar02 R2 | I2C | Underwater-pressure changes, wave characteristics, and wave-height estimation support |
| 3 | Wind-speed sensor | SparkFun Weather Meter anemometer | Pulse/GPIO | Local wind speed and wave-development context |
| 4 | Wind-direction sensor | SparkFun Weather Meter wind vane | Analog through ADS1115 | Wind direction and directional wave context |
| 5 | GPS module | Adafruit Ultimate GPS | UART | Latitude, longitude, UTC time, satellite fix, and sustained buoy-drift assessment |

The expected primary inputs for wave-prediction research are the synchronized
BNO085 motion, Bar02 pressure, and wind measurements. Their actual contribution
must be established using calibrated field data and chronological model testing.

## 2. Supporting Phase 1 Sensors and Monitors

These devices monitor energy, thermal condition, and additional environmental
context. They support system reliability but are not all direct wave-height inputs.

| No. | Sensor or monitor | Selected component | Interface | Purpose |
| ---: | --- | --- | --- | --- |
| 1 | Battery power monitor | Adafruit INA260, address `0x40` | I2C | Battery voltage, current, power, and charging/discharging state |
| 2 | Solar power monitor | Adafruit INA260, address `0x41` | I2C | Solar voltage, current, power, and charging performance |
| 3 | Internal-temperature sensor | MCP9808, address `0x18` | I2C | Electronics-enclosure temperature, thermal warning, and cooling-policy input |
| 4 | Water-temperature probe | Sealed DS18B20, optional | One-Wire | Water-temperature context and possible pressure-compensation support |

## 3. Sensor Interface Component

The ADS1115 is part of the sensor interface but is not itself an environmental
sensor.

| Component | Function |
| --- | --- |
| Adafruit ADS1115 analog-to-digital converter | Converts the analog wind-vane output into a digital value that the ESP32 can process |

## 4. Future Optional Sensors

The following devices are outside the Phase 1 baseline. They may be considered
after project approval, funding, and successful validation of the focused system.

| Future sensor | Possible measurement or use | Minimum validation requirement |
| --- | --- | --- |
| pH sensor | Water acidity or alkalinity trend | Multi-point buffer calibration and temperature compensation |
| Conductivity/salinity sensor | Electrical conductivity and salinity trend | Certified standard solution and temperature compensation |
| Turbidity sensor | Suspended-particle or water-clarity trend | Reference standards, fouling inspection, and optical cleaning |
| Dissolved-oxygen sensor | Dissolved oxygen condition | Air/water calibration and comparison with a reference meter |
| Chlorophyll-a or fluorometer sensor | Algal-concentration proxy | Laboratory or field reference comparison and optical maintenance |
| Additional water-temperature probes | Temperature at defined depths | Comparison with a traceable thermometer |
| Rain sensor | Local rainfall detection | Comparison with a reference rain gauge |
| UV sensor | Ultraviolet-exposure context | Reference-instrument comparison and exposure review |
| Water-current meter | Current speed and direction | Controlled-flow or reference-instrument comparison |
| Hydrophone | Passive underwater acoustic research | Sampling, storage, privacy, and research protocol |
| Waterline or level sensor | Local waterline relative to the buoy | Mounting-effect study and reference measurement |
| Leak or water-ingress sensor | Water inside the electronics enclosure | Controlled leak detection and fault-response testing |
| Humidity/condensation sensor | Internal moisture and condensation risk | Humidity reference and enclosure-placement testing |
| Tamper or enclosure-open sensor | Unauthorized opening or maintenance event | Authorized-access and false-alarm testing |
| Weatherproof camera | On-demand visual inspection | Power, bandwidth, waterproofing, cybersecurity, and privacy testing |

The optional camera is intended for authenticated live viewing only. Routine
recording and permanent video storage are not part of the proposed baseline.
Computer vision would require a separate dataset, study objective, and validation.

## 5. Controllers and Computers

These components process sensor information but are not sensors.

| Component | Role |
| --- | --- |
| ESP32 DevKit | Initializes sensors, acquires readings, applies calibration, validates ranges, and creates timestamped telemetry |
| Orange Pi Zero 3 4GB | Receives ESP32 telemetry, stores records, performs edge processing and scikit-learn inference, and hosts the API and dashboard |
| Raspberry Pi 5 4GB | Conditional future edge-computer upgrade if Orange Pi benchmarks demonstrate insufficient performance |

## 6. Complete Data Flow

```text
Main and Supporting Sensors
            |
            v
       ESP32 DevKit
 acquisition, calibration,
 validation and timestamping
            |
      USB serial telemetry
            |
            v
   Orange Pi Zero 3 4GB
 local database, processing,
 scikit-learn AI, API and alerts
            |
            v
     Local Dashboard
            |
   Future secure synchronization
            |
            v
        Cloud Service
```

## 7. Important Research Boundaries

- Current dashboard sensor values are simulated until physical integration is completed.
- IMU acceleration or pressure alone must not be labeled as validated wave height.
- All measurements require calibration, timestamps, units, validity, and fault states.
- Missing or invalid measurements must be shown as unavailable, not silently changed to zero.
- More sensors do not automatically create a more accurate AI model.
- Future sensors require an approved research question, exact component selection,
  power and interface review, calibration method, maintenance plan, and field evidence.
- Project FALCON is a research and local decision-support prototype; it does not
  replace official PAGASA or other government monitoring and warning systems.

## 8. Summary

The Phase 1 system uses five main sensing functions: buoy motion, water pressure,
wind speed, wind direction, and GPS position. Battery, solar, enclosure temperature,
and optional water temperature provide supporting system information. Additional
water-quality, weather, acoustic, current, safety, and camera sensors remain
conditional future upgrades.
