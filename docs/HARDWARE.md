# Project FALCON Hardware Baseline v6.2

> Hardware functions remain the Phase 1 baseline. Physical placement, enclosure integration, brackets, harness lengths, and mechanical interfaces are under redesign and remain TBD until the replacement prototype is approved.

Status: adviser-approved design baseline; procurement and physical validation remain pending. [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md) is authoritative.

## Architecture

```text
Sensors -> protected interfaces -> ESP32 -> LTE/cellular primary OR LoRa fallback -> shore gateway/Bay Station
Solar -> charge controller -> LiFePO4 battery -> protected DC rails
```

No single-board computer or mini PC is installed on the buoy. The shore Bay Station is facility powered or uses a separately designed UPS and provides storage, pressure processing, required AI prediction, API, dashboard, and alerts. LTE is the preferred link; an optional LoRa radio requires a powered shore gateway with a raised antenna and tested line of sight. USB/UART is retained only for bench commissioning; the exact LTE/LoRa interfaces must be approved before PCB release.

## Required Phase 1 groups

| Group | Device/function | Status |
| --- | --- | --- |
| Core | Blue Robotics Bar02 R2, BR-100891 | Confirmed prototype; continuous-submersion/service limitation must be resolved |
| Supporting | Adafruit Ultimate GPS, PID 746 | Confirmed prototype; field accuracy and geofence persistence testing required |
| Core | SparkFun Weather Meter, SEN-15901 | Confirmed prototype; marine durability remains unqualified |
| Health | Adafruit INA260, PID 4226, battery branch | Confirmed prototype; range, thermal and reference-meter tests pending |
| Health | Adafruit INA260, PID 4226, solar branch | Confirmed prototype; address and charging-direction tests pending |
| Health | Adafruit MCP9808, PID 1782 | Recommended enclosure-temperature selection at `0x18` |
| Security | GPS geofence | Software function using GPS |
| Security | Adafruit LIS3DH, PID 2809 | Optional tamper candidate only; not used for wave-height estimation |
| Security | Adafruit magnetic contact switch, PID 375 | Recommended prototype selection; sealed installation and debounce pending |
| Security | Buzzer | Exact part/driver TBD |

## Removed or optional items

- BNO085 is no longer required for Phase 1. Existing IMU code is a deprecated optional prototype only.
- Load cell and HX711 anchor-chain tension sensing are removed.
- Passive single-anchor mooring uses adequate line scope for tides, waves, and ordinary buoy movement.
- AI hardware acceleration is not required.
- LoRa is an optional compact telemetry fallback, not a general Internet connection; it requires a shore gateway and site-specific range testing.

The detailed selection evidence, interface allocation, calibration plan and manufacturer references are in [SENSOR_SELECTION_BASELINE.md](SENSOR_SELECTION_BASELINE.md). That document is the component-selection authority where this summary is abbreviated.

## Pressure installation

The pressure sensor must be waterproof, mechanically protected, located at a documented submerged depth, exposed to water without trapped air, and serviceable. Record its model, serial number, pressure range, units, installation depth, baseline, temperature conditions, calibration reference, date, and coefficients. Estimated wave height must not be called measured wave height.

## Electrical requirements

- fused battery/solar input and reverse-polarity protection;
- transient protection where cables enter the enclosure;
- regulated 5 V and 3.3 V rails with verified current and thermal margins;
- local decoupling and bulk capacitance;
- protected external connectors with documented pin 1 and cable colors;
- common ground or documented isolation strategy;
- I2C pull-ups sized for bus voltage and cable capacitance;
- UART logic-level compatibility;
- strain relief, corrosion control, and marine-rated sealing;
- test points for VBAT, 5 V, 3V3, GND, UART TX/RX, SDA, and SCL.

## Security input design rules

The vibration/tamper and enclosure-switch inputs require hardware filtering where appropriate plus firmware debounce and persistence. Ordinary wave motion must not trigger theft alarms. The buzzer needs a transistor/MOSFET driver and flyback protection if the selected device is inductive. Exact thresholds remain TBD until bench and motion testing.

## Power verification

The solar panel, charge controller, LiFePO4 battery, fuses, wire gauges, converters, and connectors must be selected from a measured load budget. Verify normal draw, peak draw, conversion loss, autonomy without sun, charge recovery, brownout behavior, enclosure temperature, and safe battery protection before deployment.

## Procurement gate

Do not fabricate a final PCB or claim hardware completion until exact models, datasheets, connector pinouts, logic voltages, maximum currents, environmental ratings, footprints, 3D models, and availability are verified. The current KiCad carrier is an engineering prototype and requires ERC/DRC plus physical footprint checks.
