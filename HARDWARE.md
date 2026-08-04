# FALCON-01 Hardware Plan

## Confirmed current hardware
- ESP32 DevKit / ESP-WROOM-32
- CH340 USB-to-serial interface
- Jumper wires
- LM2596 DC-DC buck converter
- Relay module and miscellaneous power modules

## Planned core modules
- Waterproof DS18B20 temperature sensor
- IMU such as MPU6050 or a more suitable orientation sensor
- GPS module such as NEO-6M or NEO-M8N
- INA219 or another voltage/current monitor
- Solar panel, battery, charge controller, and DC regulation
- LoRa or cellular module for future remote communication

## Optional sensors
- pH
- Salinity/TDS
- Turbidity
- Dissolved oxygen
- Conductivity

Optional sensors require final scope approval, calibration planning, and marine suitability review.

## Protection requirements
- IP67/IP68 enclosure where practical
- Marine-grade cable glands
- Corrosion-resistant connectors
- Condensation control
- Secure internal mounting
- Salt-air and splash protection
- Separate wet probes from dry electronics

## Important measurement note
A low-cost IMU can measure movement and tilt, but true wave-height estimation requires calibration, signal processing, and validation.
