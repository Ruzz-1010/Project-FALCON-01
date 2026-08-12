# Project FALCON Hardware Specification v4.0

## Document Control

| Field | Value |
| --- | --- |
| Prototype | FALCON-01 |
| Status | Phase 1 Hardware Baseline |
| Authority | PROJECT_CONTEXT.md v4.0 |
| Updated | 2026-08-09 |

## Verified Status

Confirmed repository/development hardware includes an ESP32 DevKit/ESP-WROOM-32-class board and basic development modules previously recorded in the project.

The full sensor set, selected Orange Pi Zero 3 (4GB), final solar/battery components, and complete marine deployment assembly shall not be treated as installed until procurement and physical verification records exist.

Part numbers, capacities, ratings, and dimensions marked **TBD** require selection and engineering review.

## Hardware Purpose

The Phase 1 hardware supports:

- real-time coastal monitoring;
- pressure- and IMU-based wave measurement;
- wind context;
- GPS position;
- battery and solar monitoring;
- internal-temperature monitoring;
- ESP32 data acquisition;
- UART or validated local Wi-Fi transfer to the Orange Pi;
- local AI-assisted wave prediction;
- and a local dashboard.

## Final Phase 1 Hardware Architecture

```text
BNO085 IMU --------------------+
Water Pressure Sensor ---------+
Wind Speed Sensor -------------+
Wind Direction Sensor ---------+--> ESP32 --> UART / Wi-Fi --> Orange Pi Zero 3 (4GB)
GPS Module --------------------+                    |
Battery Monitor ---------------+                    +--> REST API
Solar Monitor -----------------+                    |
Internal Temperature ----------+                    +--> Local Dashboard
Optional Water Temperature ----+
```

## Embedded Controller

### ESP32

Role: primary deterministic acquisition and control device.

Responsibilities:

- initialize approved sensors;
- acquire timestamped readings;
- apply calibration coefficients;
- validate ranges;
- report sensor health;
- parse GPS;
- monitor battery and solar state;
- monitor internal temperature;
- frame UART telemetry;
- handle watchdog recovery;
- and provide a limited local fallback interface where appropriate.

The ESP32 shall continue basic acquisition when the Orange Pi is unavailable.

The ESP32 is not the primary host for the full 3D dashboard or final AI service.

### Minimum Interface Requirements

- sufficient I2C/UART/ADC resources for selected sensors;
- 3.3 V logic compatibility;
- protected power input;
- accessible programming interface;
- watchdog capability;
- and documented pin allocation.

Final pin assignments belong in PINOUT.md after sensor selection.

## Orange Pi Zero 3 (4GB)

Role: selected local edge-processing and dashboard host.

Selected model: **Orange Pi Zero 3, 4GB LPDDR4**. Procurement and physical integration remain pending.

The laptop may temporarily perform this role during demonstrations.

Integration requirements:

- reliable 3.3 V UART or isolated USB-serial interface, with local Wi-Fi available as a validated alternate transport;
- regulated 5 V rail sized for a 3 A transient design envelope;
- short, low-resistance power wiring and brownout logging;
- adequate CPU for one lightweight wave-prediction model;
- adequate storage for local telemetry and prediction history;
- low enough power consumption for the validated energy budget;
- automatic startup after power restoration;
- serviceable local operating system;
- and physically secure mounting.

Responsibilities:

- UART ingestion;
- local data validation;
- wave processing;
- AI inference;
- local database;
- REST API;
- dashboard hosting;
- alert aggregation;
- and system logging.

The Orange Pi is not an autonomous-navigation computer.

## Approved Phase 1 Sensors

### BNO085 IMU

Purpose:

- pitch;
- roll;
- yaw;
- acceleration;
- orientation;
- and wave-motion features.

Selection status: approved sensor family; exact breakout and supplier **TBD**.

Interface: typically I2C or UART, subject to final design.

Mounting:

- rigid central structure;
- documented axes;
- away from loose vibration;
- and accessible for calibration.

### Water-Pressure Sensor

Purpose:

- pressure changes;
- wave-height estimation;
- wave-period features;
- and primary AI input support.

Exact model and pressure range: **TBD**.

Selection criteria:

- marine/water compatibility;
- suitable pressure range and resolution;
- stable output;
- calibration support;
- compatible electrical interface;
- and maintainable waterproof installation.

### Wind-Speed Sensor

Purpose:

- local wind-speed monitoring;
- wave-development context;
- and optional validated AI input.

Exact model: **TBD**.

The sensor shall tolerate salt exposure or include a protection/maintenance plan.

### Wind-Direction Sensor

Purpose:

- local wind-direction monitoring;
- directional context;
- and optional validated AI input.

Exact model: **TBD**.

The installation shall document true-north or magnetic-north convention.

### GPS Module

Purpose:

- deployment position;
- current position;
- satellite/fix state;
- time reference;
- and sustained drift assessment.

Exact model: **TBD**.

GPS does not provide autonomous navigation.

### Battery Monitor

Purpose:

- battery voltage;
- battery current;
- charging/discharging direction;
- battery-percentage estimate;
- and low/critical battery state.

Exact device and shunt rating: **TBD**.

### Solar Monitor

Purpose:

- solar voltage;
- solar current;
- calculated power where valid;
- and charging status.

Exact device and range: **TBD**.

### Internal-Temperature Sensor

Purpose:

- electronics-enclosure temperature;
- thermal warning;
- and cooling-policy input when cooling hardware is installed.

Exact device: **TBD**.

### Optional Water-Temperature Sensor

Water temperature is optional.

It may provide monitoring and compensation context.

Water-temperature prediction is not in scope.

## Excluded Phase 1 Sensors

The following are Future Expansion:

- pH;
- salinity;
- turbidity;
- dissolved oxygen;
- rain;
- UV;
- camera;
- hydrophone;
- current meter;
- and Water Quality Index sensors.

They shall not be included in the Phase 1 procurement baseline.

## Power System

### Approved Power Chain

```text
Solar Panel
    |
    v
MPPT Charge Controller
    |
    v
12 V LiFePO4 Battery
    |
    v
Protected Power Distribution
    |
    +--> ESP32
    +--> Orange Pi Zero 3
    +--> Sensors
```

### Solar Panel

Final wattage: **TBD through energy-budget calculation**.

Requirements:

- adequate daily energy production;
- marine/outdoor suitability;
- secure tilted mounting;
- acceptable wind loading;
- and maintainable wiring.

### MPPT Charge Controller

Final model: **TBD**.

Requirements:

- compatible solar input;
- compatible LiFePO4 charge profile;
- current rating above expected maximum;
- protection features;
- and charging-state visibility where practical.

### 12 V LiFePO4 Battery

Final capacity: **TBD through measured autonomy requirement**.

Requirements:

- suitable BMS;
- adequate continuous/peak current;
- protected enclosure installation;
- temperature awareness;
- and safe service disconnect.

### Power Distribution

Requirements:

- branch fusing;
- reverse-polarity protection;
- suitable conductor sizing;
- regulated rails;
- labeled connectors;
- strain relief;
- and measured conversion efficiency.

### Energy-Budget Inputs

- ESP32 average and peak current;
- Orange Pi idle, average, and startup power;
- all approved sensors;
- GPS;
- cooling hardware when installed;
- regulator losses;
- nighttime duration;
- cloudy-day margin;
- and required reserve.

No autonomy duration shall be claimed without measurement.

## Cooling Hardware

Cooling may include intake and exhaust fans if thermal testing proves they are required.

Fan modules shown in CAD are mechanical provisions until installed and electrically verified.

Automatic fan control shall be deterministic and based on internal temperature thresholds.

Cooling status shall not be presented as active when the hardware is absent.

## Communication Hardware

### ESP32 to Orange Pi

Approved Phase 1 transport: UART.

Requirements:

- common ground or approved isolation;
- compatible logic levels;
- short protected wiring;
- defined connector;
- strain relief;
- and documented baud/framing.

USB serial may be used for development while preserving the UART protocol boundary.

### Local Dashboard Network

The Orange Pi provides the local web service over Wi-Fi or Ethernet according to the validated deployment design.

Public Internet is not required.

### Future Communication Hardware

- LTE;
- LoRa;
- satellite communication;
- mesh networking;
- and fleet networking.

## Mechanical Hardware Interface

Hardware installation shall preserve:

- HDPE main float;
- four stabilizer buoys;
- marine aluminum arms;
- stainless steel tension cables;
- central ballast;
- single anchor;
- waterproof enclosure;
- solar-panel assembly;
- upper sensor array;
- and antenna clearances.

Refer to MECHANICAL.md for the mechanical baseline.

## Waterproofing and Marine Protection

Design intent: IP67 or better for the electronics enclosure, subject to testing.

Required practices:

- marine-suitable cable glands;
- waterproof connectors where disconnection is required;
- strain relief;
- gasket inspection;
- pressure equalization or condensation management;
- corrosion-resistant fasteners;
- protected exposed copper;
- and post-deployment fresh-water rinsing.

## Hardware Fault Behavior

### Sensor Disconnect

- mark sensor unavailable;
- preserve remaining acquisition;
- log the fault;
- and transmit health state.

### Mini-PC Loss

- ESP32 continues acquisition;
- AI becomes unavailable;
- and the system reports degraded state.

### Low Battery

- issue warning;
- apply approved deterministic power policy;
- and avoid unsafe discharge.

### Internal Overtemperature

- issue warning/critical alert;
- activate verified cooling when installed;
- and reduce nonessential load only according to approved rules.

## Procurement and Acceptance

Every selected part shall record:

- manufacturer;
- model;
- supplier;
- datasheet;
- electrical rating;
- environmental rating;
- interface;
- calibration needs;
- unit cost;
- quantity;
- and acceptance-test result.

## Hardware Validation

Required categories:

- power-up and brownout;
- current consumption;
- solar charging;
- battery endurance;
- sensor accuracy and repeatability;
- UART reliability;
- enclosure temperature;
- waterproofing;
- corrosion inspection;
- and controlled marine operation.

## Future Expansion

Future hardware may include water-quality sensors, camera, hydrophone, current meter, LTE, LoRa, satellite communication, alternate edge computers, larger power systems, and multi-buoy hardware.

None are Phase 1 requirements.

## Revision History

| Version | Date | Change |
| --- | --- | --- |
| 3.1 | 2026-08-05 | Added verified available-hardware notice. |
| 4.1 | 2026-08-12 | Selected Orange Pi Zero 3 (4GB), added UART/Wi-Fi transport wording, and linked provisional power sizing. |
| 4.0 | 2026-08-09 | Replaced broad hardware plan with approved core sensors, UART edge architecture, measured power-design requirements, and explicit Future Expansion boundaries. |
