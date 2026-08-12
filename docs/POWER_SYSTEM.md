# Power System

## Purpose
Define safety and design gates for autonomous power.

## Scope
Solar generation, charging, battery, protection, regulation, monitoring, and thermal behavior.

## Current Status
**Status: Provisional sizing baseline.** Current development uses USB power; the complete marine charging and protection system is not yet integrated.

## Architecture
Solar panel -> disconnect/protection -> charger -> protected battery -> fused distribution -> regulated rails -> loads.

## Implementation
No marine power system exists. The previous 12 V 60 Ah battery and 150 W panel concept is no longer the preferred Phase 1 starting point. The selected Orange Pi Zero 3 uses a regulated 5 V input. Official Orange Pi guidance permits a 5 V/2 A or 5 V/3 A Type-C source, so the buoy regulator shall be designed for a stable 5 V/3 A transient envelope even if measured average consumption is lower.

## Recommended Prototype Baseline

- **Battery:** 12.8 V 20 Ah LiFePO4 with integrated BMS and a marine-rated fuse near the battery.
- **Solar panel:** 60 W nominal monocrystalline for supervised presentations, bench endurance, and controlled short coastal trials.
- **Preferred margin:** 80 W when cloudy-day recovery, partial shading, continuous Wi-Fi, active fans, or longer unattended trials are expected.
- **Charger:** LiFePO4-compatible MPPT controller sized for the selected panel voltage and current.
- **Orange Pi regulator:** quality synchronous 12 V-to-5 V buck regulator rated for at least 5 V/3 A continuous, with ripple, temperature, transient, and brownout validation.

A 20 Ah LiFePO4 battery stores about 256 Wh nominal. Assuming 80% usable energy gives approximately 205 Wh. At a complete measured average load of 6 W, the estimate is about 34 hours without solar; at 10 W, about 20 hours. These are design estimates, not validated endurance claims.

A 60 W panel at four peak-sun-hours and 70% net system efficiency gives an estimated 168 Wh/day. An 80 W panel gives about 224 Wh/day. Puerto Princesa weather, tilt, salt contamination, temperature, wiring, charger, and shading losses must be measured.

Do not reduce below 12.8 V 20 Ah and 60 W for unattended operation until a 24-hour load log and at least a 72-hour solar-endurance trial demonstrate adequate reserve. A smaller protected battery is acceptable for a supervised indoor presentation only when clearly labeled non-deployment hardware.

Required artifacts: load table, energy budget, sizing calculations, protection/wire/connector schedule, thermal review, low-voltage behavior, and endurance/fault tests.

## Future Expansion
Power modes, telemetry, controlled loads, and energy-aware AI after hardware approval.

## Engineering Notes
LM2596 is a regulator, not a charger/BMS/fuse. Verify its output before connection. Do not field-deploy an unreviewed battery system.

## Revision History
| Version | Date | Change |
| --- | --- | --- |
| 1.1 | 2026-08-12 | Added provisional Orange Pi-based 20 Ah battery and 60–80 W solar sizing baseline. |
| 1.0 | 2026-08-05 | Initial power gates. |
