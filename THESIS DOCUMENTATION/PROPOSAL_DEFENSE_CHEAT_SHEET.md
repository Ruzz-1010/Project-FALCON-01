# Project FALCON Proposal Defense Cheat Sheet

## 30-second project answer

Project FALCON is a proposed affordable solar-powered coastal observation buoy. It will use pressure sensing to estimate wave height and may include a wind sensor for local wind observations. The ESP32 will sample and process data locally, then send event-driven summaries and alerts through Wi-Fi during testing or 4G/LTE during a remote trial. The cloud service will store and present the data. The current system is still a software prototype; physical integration and validation are pending.

## Quick answers

**What does the pressure sensor measure?**

It directly measures underwater pressure. The software uses pressure changes over time, baseline removal, filtering, depth information, and calibration to estimate wave height.

**Which pressure sensor is proposed for long-term deployment?**

The current candidate is a Holykell HPT604 Type A with a provisional 0–2 mH2O vented-gauge range and 4–20 mA output. We chose an industrial current-loop candidate because it is better suited to a longer noisy cable run than direct I2C. It is not yet approved hardware: the exact order code, continuous-saltwater compatibility, cable, seals, vent arrangement, interface, and calibration must still be confirmed and tested. Bar02 is only for supervised short-duration bench comparison.

**Is the wave height directly measured?**

No. Pressure is directly measured; wave height is derived and must be labeled `ESTIMATED` until reference validation is complete.

**Why is most processing outside the buoy?**

To keep storage, dashboard hosting, and heavier analysis away from the low-power buoy. The ESP32 remains responsible for sensing, event detection, buffering, and upload. This reduces buoy power, heat, waterproofing, and maintenance requirements.

**Why event-driven cloud telemetry?**

The buoy continuously samples locally but transmits only short summaries and significant event packets. This keeps the cloud data current while reducing mobile-data use and battery load. The ocean is always moving, so an event means a significant change or system condition, not every individual wave.

**What is 4G/LTE for?**

It is the proposed direct Internet link from the remote buoy to the cloud. The ESP32 requires an external LTE modem and SIM because ordinary ESP32 boards do not have built-in cellular connectivity.

**Is it already deployed?**

No. The dashboard and edge service are software demonstrations. Hardware integration, calibration, waterproofing, communication testing, and supervised field validation are still pending.

**Is the AI accurate?**

Not yet proven. The current output is a transparent research baseline. Accuracy requires calibrated local data, chronological evaluation, baseline comparison, and reported MAE/RMSE/bias.

**What sensors are required?**

Pressure-derived wave sensing is the core measurement. Wind speed/direction, GPS, power, timestamps, and security are supporting or optional channels subject to adviser approval. Water temperature, salinity, conductivity, BNO085, and HX711 mooring tension are excluded from the low-cost minimum build.

**What is the innovation?**

The intended contribution is the affordable, documented integration and local evaluation of established sensing, event-driven cloud telemetry, solar power, security telemetry, and transparent prediction research. It is not the invention of a new sensor or AI algorithm.

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
