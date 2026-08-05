# Power System

## Purpose
Define safety and design gates for autonomous power.

## Scope
Solar generation, charging, battery, protection, regulation, monitoring, and thermal behavior.

## Current Status
**Status: Not Yet Finalized.** Current development uses USB power; LM2596 is not integrated.

## Architecture
Solar panel -> disconnect/protection -> charger -> protected battery -> fused distribution -> regulated rails -> loads.

## Implementation
No marine power system exists. Proposed 12 V 60 Ah battery and 150 W panel require measured load, autonomy, solar-resource, loss, thermal, fault, and budget calculations.

Required artifacts: load table, energy budget, sizing calculations, protection/wire/connector schedule, thermal review, low-voltage behavior, and endurance/fault tests.

## Future Expansion
Power modes, telemetry, controlled loads, and energy-aware AI after hardware approval.

## Engineering Notes
LM2596 is a regulator, not a charger/BMS/fuse. Verify its output before connection. Do not field-deploy an unreviewed battery system.

## Revision History
| Version | Date | Change |
| --- | --- | --- |
| 1.0 | 2026-08-05 | Initial power gates. |
