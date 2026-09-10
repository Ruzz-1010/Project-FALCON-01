# Project FALCON Proposal Defense Cheat Sheet

## 30-second project answer

Project FALCON is a proposed affordable solar-powered coastal observation buoy. It will use pressure sensing to estimate wave height and a wind sensor for local wind observations. The ESP32 is planned to send telemetry through LoRa to a barangay-hall Bay Station. The Bay Station will store and process the data, show it on a dashboard, and use SIM/4G/5G Internet as proposed backhaul for cloud upload and authorized remote access. The current system is still a software prototype; physical integration and validation are pending.

## Quick answers

**What does the pressure sensor measure?**

It directly measures underwater pressure. The software uses pressure changes over time, baseline removal, filtering, depth information, and calibration to estimate wave height.

**Is the wave height directly measured?**

No. Pressure is directly measured; wave height is derived and must be labeled `ESTIMATED` until reference validation is complete.

**Why is the Bay Station on shore?**

To keep storage, processing, dashboard hosting, and AI away from the low-power buoy. This reduces buoy power, heat, waterproofing, and maintenance requirements.

**Why LoRa?**

LoRa is the proposed low-rate buoy-to-barangay-hall telemetry link. It can support a local gateway path without placing a cellular Internet modem on the buoy. Range, frequency, gateway placement, and reliability still require testing.

**What is SIM/4G/5G for?**

It is the proposed Internet backhaul of the Bay Station for cloud upload and authorized remote access. It is not the primary buoy sensor link.

**Is it already deployed?**

No. The dashboard and edge service are software demonstrations. Hardware integration, calibration, waterproofing, communication testing, and supervised field validation are still pending.

**Is the AI accurate?**

Not yet proven. The current output is a transparent research baseline. Accuracy requires calibrated local data, chronological evaluation, baseline comparison, and reported MAE/RMSE/bias.

**What sensors are required?**

Pressure-derived wave sensing and wind speed/direction are the primary Phase 1 measurements. GPS, power, timestamps, and security are supporting telemetry. Water temperature, salinity, conductivity, BNO085, and HX711 mooring tension are excluded from the required Phase 1 scope.

**What is the innovation?**

The intended contribution is the affordable, documented integration and local evaluation of established sensing, LoRa telemetry, shore processing, solar power, security telemetry, and transparent prediction research. It is not the invention of a new sensor or AI algorithm.

**Can it issue warnings?**

No. FALCON is a research and local decision-support prototype. It does not replace PAGASA, coast guard instructions, navigation equipment, or official emergency-warning systems.

## Disclosure to say during the demo

> The dashboard values shown here are simulator-generated and demonstrate the software workflow. They are not live ocean measurements. Physical sensing, calibration, communication reliability, and AI accuracy will be evaluated during the proposed funded development.

## Answer pattern when unsure

> That value is currently a proposal or selection gate, not a verified field result. We will define the acceptance test, collect evidence, and update the design and thesis based on the result.

## Remember

- `LIVE` means connected physical data.
- `SIMULATED` means software-generated data.
- `ESTIMATED` means derived rather than directly measured.
- `CALIBRATION REQUIRED` means no accuracy claim yet.
- `PROPOSED` means planned, not installed.
- `PENDING` means procurement, integration, or validation is incomplete.
