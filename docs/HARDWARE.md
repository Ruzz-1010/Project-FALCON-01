# Project FALCON Hardware Baseline v6.0

Status: adviser-approved design baseline; procurement and physical validation remain pending. [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md) is authoritative.

## Architecture

```text
Sensors -> protected interfaces -> ESP32 -> USB/UART -> Orange Pi Zero 3
Solar -> charge controller -> LiFePO4 battery -> protected DC rails
```

The Orange Pi is powered separately from the sensor carrier and is not placed on the ESP32 PCB. It provides local storage, API, dashboard, and optional future AI.

## Required Phase 1 groups

| Group | Device/function | Status |
| --- | --- | --- |
| Core | Blue Robotics Bar02 or compatible waterproof pressure sensor | Selected family; exact interface/range verification required |
| Core | GPS receiver | Exact model TBD |
| Core | Wind-speed sensor | Exact model TBD |
| Core | Wind-direction sensor | Exact model TBD |
| Supporting | Sealed DS18B20 water-temperature probe | Selected family |
| Health | Battery voltage/current monitor | Exact design/range TBD |
| Health | Solar voltage/current monitor | Exact design/range TBD |
| Health | Enclosure-temperature sensor | Exact model TBD |
| Security | GPS geofence | Software function using GPS |
| Security | Vibration/tamper input | Exact part TBD |
| Security | Reed/limit enclosure switch | Exact part TBD |
| Security | Buzzer | Exact part/driver TBD |

## Removed or optional items

- BNO085 is no longer required for Phase 1. Existing IMU code is a deprecated optional prototype only.
- Load cell and HX711 anchor-chain tension sensing are removed.
- Passive single-anchor mooring uses adequate line scope for tides, waves, and ordinary buoy movement.
- AI hardware acceleration is not required.

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
