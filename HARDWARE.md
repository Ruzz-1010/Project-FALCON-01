# Project FALCON-01 Hardware Documentation

**Project Name:** Project FALCON

**Prototype:** FALCON-01

**Meaning:**
**F**ullbright College's **A**I-powered **L**ive **C**oastal **O**bservation **N**etwork

**Document Version:** Hardware Documentation v3.0

**Status:** Approved Phase 1 Hardware Baseline

**Related Documents:**

* PROJECT_CONTEXT.md v3
* SYSTEM_ARCHITECTURE.md
* FIRMWARE_SPEC.md (Planned)
* AI_SPEC.md (Planned)

---

# 1. System Overview

FALCON-01 is a solar-powered intelligent coastal observation buoy designed for long-term autonomous deployment in marine environments.

The system combines IoT, embedded systems, renewable energy, edge AI, and environmental sensing to provide continuous coastal monitoring, AI-assisted sea-state classification, buoy self-diagnostics, and remote telemetry.

Primary capabilities include:

* Real-time environmental monitoring
* AI-assisted sea condition classification
* Local Wi-Fi maintenance dashboard
* Remote cloud synchronization
* Autonomous solar-powered operation
* GPS-based positioning
* Anti-theft and drift detection
* Tidal-aware buoy health monitoring
* Predictive maintenance support (future)

---

# 2. System Architecture

The hardware is divided into the following subsystems:

1. Mechanical Structure
2. Power System
3. Embedded Controller
4. Edge AI Computer
5. Sensor Network
6. Communications
7. Diagnostics & Safety
8. Expansion Interface

---

# 3. Embedded Controller

## Primary Controller

**ESP32 DevKit**

### Responsibilities

* Primary embedded controller
* Sensor acquisition
* Local Wi-Fi Access Point
* Captive Portal
* Local Web Dashboard
* REST API
* GPS processing
* Power monitoring
* Buoy health monitoring
* Communication with AI computer
* OTA firmware updates
* Data logging
* Alert generation
* Watchdog recovery

The ESP32 remains operational even if the AI computer is unavailable.

---

# 4. Edge AI Computer

## Current Development Platform

**Dell OptiPlex 3050 Micro**

### Recommended Specification

* Intel Core i5-7500T
* 8 GB DDR4 RAM
* 256 GB SSD
* Ubuntu Server 24.04 LTS

### Responsibilities

* AI inference
* Sensor fusion
* Local database
* Dashboard backend
* Cloud synchronization
* Historical analytics
* Future computer vision
* Fleet management support

**Note:** Future production versions may migrate to a lower-power platform (e.g., Raspberry Pi or equivalent ARM-based edge computer) after prototype validation.

---

# 5. Mechanical Structure

## Main Float

**Modified HDPE Drum**

### Recommended Capacity

60–80 Liters

### Material

High-Density Polyethylene (HDPE)

### Features

* Waterproof
* UV resistant
* Corrosion resistant
* Marine suitable
* Easy maintenance
* Lightweight
* Replaceable

The modified HDPE drum serves as the primary flotation body and structural support for all electronics.

---

# 6. Stabilization System

Approved Phase 1 Baseline:

* Four HDPE Stabilizer Buoys
* Aluminum 6061-T6 Support Arms
* Stainless Steel 316 Tension Cables
* Stainless Steel Marine Brackets
* Central Ballast
* Single Marine Anchor
* Single Mooring Line

### Purpose

* Reduce roll
* Reduce pitch
* Improve wave stability
* Improve AI sensor accuracy
* Maintain solar panel orientation
* Increase survivability during rough sea conditions

---

# 7. Internal Compartments

## Upper Electronics Bay

Contains:

* AI Computer
* ESP32
* GPS Module
* LTE Module
* Wi-Fi Antenna
* Electronics Mounting Plate
* Communication Interfaces

---

## Middle Power Bay

Contains:

* MPPT Charge Controller
* DC-DC Buck Converter
* Fuse Block
* Power Distribution Board
* Current Monitoring
* Voltage Monitoring

---

## Lower Battery Bay

Contains:

* 12V LiFePO₄ Battery
* Battery Protection
* Temperature Sensor

---

## Bottom Section

Contains:

* Central Ballast Assembly
* Mooring Connection
* Anchor Attachment

---

# 8. Power System

## Battery

### Type

LiFePO₄

### Capacity

12V 60Ah

### Advantages

* Long cycle life
* High safety
* Stable voltage
* Excellent marine suitability
* Fast charging
* Low maintenance

---

## Solar Panel

Recommended:

150W Monocrystalline Solar Panel

Future Upgrade:

200W

---

## Charge Controller

MPPT Solar Charge Controller

Functions:

* Maximum charging efficiency
* Battery protection
* Solar monitoring

---

## Voltage Conversion

LM2596 DC-DC Buck Converter

Provides regulated voltages for:

* ESP32
* AI Computer
* Sensors
* LTE Module
* Cooling Fans

---

# 9. Cooling System

## Electronics Cooling

* Intake Fan
* Exhaust Fan
* Passive Airflow Channels

---

## Battery Cooling

Dedicated battery compartment

Includes:

* Temperature monitoring
* Passive airflow
* Thermal isolation

---

## Automatic Cooling

The ESP32 automatically controls cooling fans based on internal enclosure temperature.

---

# 10. Communication System

## Local

ESP32 Wi-Fi Access Point

Features:

* Local Dashboard
* Captive Portal
* Maintenance Interface
* Offline Diagnostics

---

## Remote

LTE Module

Functions:

* Cloud synchronization
* Remote monitoring
* Alert transmission

---

## Future Expansion

* LoRa
* Satellite communication
* Mesh networking

---

# 11. Sensor Package

## Marine Sensors

* Water Temperature
* Salinity
* pH
* Turbidity
* Dissolved Oxygen (Optional)
* Water Level / Waterline Sensor

---

## Weather Sensors

* Wind Speed
* Wind Direction
* Air Temperature
* Humidity
* Atmospheric Pressure

---

## Navigation

* GPS Module

Functions:

* Position tracking
* Drift detection
* Anti-theft monitoring
* Geofencing
* Time synchronization

---

## Motion Monitoring

### BNO085 IMU

Measures:

* Roll
* Pitch
* Motion
* Orientation
* Acceleration

Used for:

* Wave analysis
* Stability monitoring
* Tidal-aware diagnostics

---

## Power Monitoring

* Battery Voltage
* Battery Current
* Solar Voltage
* Solar Current

---

## Safety Sensors

* Internal Temperature
* Enclosure Humidity
* Water Leak Sensor
* Tamper Switch
* RTC DS3231

---

# 12. Buoy Health Monitoring

The buoy evaluates multiple systems simultaneously.

Inputs include:

* Waterline changes
* IMU stability
* GPS position
* Leak detection
* Battery health
* Solar charging
* Sensor availability
* Communication status

This sensor fusion approach prevents false alarms caused by normal tidal movement.

---

# 13. Waterproof Protection

## Target Rating

IP67 (minimum)

Target production:

IP68

### Protection Features

* Waterproof cable glands
* Waterproof connectors
* Silicone seals
* Marine-grade enclosure
* Pressure equalization vent
* Desiccant packs
* Corrosion-resistant coating
* Stainless steel marine fasteners

---

# 14. Internal Wiring

## Power Flow

Solar Panel

↓

MPPT Charge Controller

↓

12V LiFePO₄ Battery

↓

Fuse Block

↓

Power Distribution Board

↓

DC-DC Buck Converter

↓

ESP32

↓

AI Computer

↓

Sensors & Communication Modules

---

## Data Flow

Environmental Sensors

↓

ESP32

↓

Health Monitoring & Local Logging

↓

AI Computer

↓

Cloud Database

↓

Dashboard

↓

User Interface

---

# 15. Estimated Major Hardware

## Computing

* ESP32 DevKit
* Dell OptiPlex 3050 Micro

## Power

* 12V 60Ah LiFePO₄ Battery
* 150W Solar Panel
* MPPT Charge Controller
* LM2596 Buck Converter

## Communications

* GPS Module
* LTE Module

## Motion

* BNO085 IMU

## Environmental Sensors

* Wind Speed Sensor
* Wind Direction Sensor
* Water Temperature Sensor
* Salinity Sensor
* pH Sensor
* Turbidity Sensor
* Atmospheric Pressure Sensor
* Humidity Sensor
* Air Temperature Sensor
* Waterline Sensor

## Diagnostics

* Battery Monitor
* Solar Monitor
* Leak Sensor
* Internal Temperature Sensor
* Enclosure Humidity Sensor
* RTC DS3231

## Mechanical

* Modified HDPE Drum
* Four HDPE Stabilizer Buoys
* Aluminum 6061-T6 Support Arms
* Stainless Steel 316 Tension Cables
* Stainless Steel Brackets
* Central Ballast
* Marine Anchor
* Waterproof Enclosure
* Marine Fasteners

---

# 16. Future Expansion

Planned hardware upgrades include:

* Camera Module
* Thermal Camera
* Oil Spill Detection Sensor
* Hydrophone
* Water Current Sensor
* Rain Sensor
* UV Sensor
* LoRa Gateway
* Satellite Communication
* Mesh Networking
* Fleet Management
* Edge Computer Upgrade
* Automatic Firmware Updates
* Smart Predictive Maintenance
* Multi-Buoy Synchronization

---

# 17. Design Principles

Project FALCON hardware follows these principles:

* Modular architecture
* Marine durability
* Low maintenance
* Solar-powered autonomy
* Expandable subsystem design
* Fault tolerance
* Energy efficiency
* Easy field servicing
* Cost-effective deployment
* Research-grade reliability

---

# End of Hardware Documentation

**Document:** Hardware Documentation v3.0

**Prototype:** FALCON-01

**Status:** Approved Phase 1 Hardware Baseline

This document defines the official hardware configuration for Project FALCON-01 and should be used as the baseline for mechanical design, electronics integration, firmware development, and future hardware revisions unless superseded by a newer approved version.
