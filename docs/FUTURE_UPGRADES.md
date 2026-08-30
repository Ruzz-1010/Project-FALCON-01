# Future Upgrade Roadmap

## Purpose

This document records possible post-Phase 1 improvements for Project FALCON.
These items are **not installed, funded, calibrated, or validated in the current
prototype**. They may proceed only after Phase 1 is approved and field results
show a justified need.

## Upgrade Principles

- Preserve the ESP32 as the deterministic sensor-acquisition and basic safety controller.
- Keep compute hardware at the shore Bay Station; select it from measured service requirements.
- Upgrade only when measurements identify a performance, reliability, or research need.
- Prefer modular, replaceable interfaces rather than redesigning the complete buoy.
- Recalculate energy, thermal, enclosure, network, and maintenance requirements before purchase.
- Treat every new sensor as unavailable until calibrated against a traceable reference.
- Preserve ESP32 sensing/security and buffered records when cellular service is absent.

## Proposed Upgrade Stages

| Priority | Upgrade | Intended benefit | Release gate |
| --- | --- | --- | --- |
| 1 | Reliability and maintainability | Safer, longer field operation | Phase 1 validation findings closed |
| 2 | On-demand viewing camera | Remote visual inspection without continuous recording | Privacy, bandwidth, power, and ingress review |
| 3 | Additional environmental sensors | Broader coastal research measurements | Research question, calibration method, and reference instrument approved |
| 4 | Communications resilience | Remote operation beyond local Wi-Fi | Site survey and recurring-service budget approved |
| 5 | Raspberry Pi 5 4GB Bay Station option | More compute margin for heavier analytics | Bay Station benchmarks demonstrate a real limitation |
| 6 | Fleet and advanced analytics | Multi-buoy regional observations | Single-buoy field performance is repeatable |

## Raspberry Pi 5 4GB Upgrade

The Raspberry Pi 5 4GB is a possible shore Bay Station computer when heavier analytics, higher dashboard load, camera processing, or additional services exceed the final measured requirement. It is never installed on or powered by the buoy.

Before migration:

1. Benchmark the development/final Bay Station CPU, memory, prediction latency, storage I/O, temperature,
   boot time, and service recovery under the complete measured workload.
2. Confirm that optimization cannot meet the requirement more efficiently.
3. Provide a manufacturer-compliant shore power supply and separately evaluate UPS needs.
4. Add approved cooling and verify the Bay Station room/enclosure environment.
5. Revise shore mounting, network, storage, service, and spare-parts plans; do not charge this load to the buoy solar budget.
6. Re-run software installation, watchdog, brownout, reboot, 24/72-hour endurance,
   and supervised deployment tests.

This upgrade improves compute headroom, but sustainability depends on measured
energy use, repairability, software support, and system lifetime—not CPU speed alone.

## On-Demand Camera Upgrade

The preferred future camera is a weatherproof USB UVC camera with native H.264
output. It is for remote visual inspection only, not Phase 1 measurement or AI.

Proposed behavior:

`Future camera -> authenticated cellular/network path -> shore Bay Station -> dashboard viewer`

- 720p at approximately 10–15 frames per second;
- streaming starts only while an authorized user is viewing;
- no routine video recording or permanent archive;
- short volatile RAM buffers only, cleared when viewing stops;
- automatic shutdown after an inactivity timeout;
- no public stream URL;
- encrypted authenticated access, access logging, and configurable privacy masking;
- separate fused power control, waterproof housing, cable gland, sun shield,
  condensation control, and lens-cleaning/inspection schedule.

Even without recording, the camera increases uplink data, power, heat, and privacy
risk. Site bandwidth and energy testing are mandatory. Computer vision remains a
separate future study requiring consent, a dataset, performance evidence, and an
explicit research objective.

## Additional Sensor Options

Only sensors that answer an approved research question should be added.

| Sensor | Possible use | Required validation |
| --- | --- | --- |
| pH | Acidity/alkalinity trend | Multi-point buffer calibration and temperature compensation |
| Electrical conductivity/salinity | Salinity trend | Certified standard solution and temperature compensation |
| Turbidity | Suspended-particle trend | Reference standards, fouling checks, and optical cleaning |
| Dissolved oxygen | Water-quality condition | Air/water calibration and comparison with a reference meter |
| Water temperature probe | Subsurface temperature | Traceable thermometer comparison and depth definition |
| Chlorophyll-a/fluorometer | Algal proxy research | Laboratory/field reference comparison and optical maintenance |
| Rain and UV | Local weather context | Reference instrument comparison and exposure review |
| Current meter | Water-current speed/direction | Controlled flow/reference comparison and mounting-effect study |
| Hydrophone | Passive acoustic research | Separate sampling, storage, privacy, and species-study protocol |

Each addition requires an interface and address audit, power budget, corrosion and
biofouling plan, physical mounting review, calibration record, uncertainty estimate,
API/schema fields, dashboard state, and missing/stale-data behavior. More sensors do
not automatically produce better predictions.

## Communications and Platform Upgrades

- LTE/4G for sites with verified coverage and a funded data plan;
- LoRa for low-rate telemetry to a nearby managed gateway;
- satellite messaging only for compact priority telemetry where cost is justified;
- VPN-based remote maintenance rather than exposed device ports;
- store-and-forward synchronization during outages;
- signed updates, per-device credentials, role-based dashboard access, and audit logs;
- optional SSD only after storage endurance and power impacts are measured;
- multi-buoy fleet identifiers, time synchronization, health reporting, and map views.

## Power, Mechanical, and Sustainability Upgrades

- higher-efficiency MPPT and DC-DC conversion selected from logged energy losses;
- remotely controlled load switching for optional camera/modem loads;
- measured low-power modes and energy-aware service scheduling;
- larger solar or LiFePO4 capacity only after a revised worst-case energy budget;
- replaceable sensor harnesses, keyed marine connectors, strain relief, and labeled wiring;
- improved condensation sensing, desiccant service indicators, leak detection, and thermal monitoring;
- corrosion-resistant fasteners, sacrificial protection where appropriate, and documented maintenance intervals;
- modular trays and field-replaceable assemblies to reduce waste and repair time.

## Evidence Required Before Calling an Upgrade Implemented

- approved research or operational requirement;
- exact part number, datasheet, supplier, cost, and received-part photographs;
- revised schematic, BOM, power calculation, layout, enclosure, and software contract;
- calibration and uncertainty record where applicable;
- bench, fault, thermal, endurance, ingress, network, and supervised field results;
- cybersecurity and privacy review for remote connectivity or cameras;
- updated user, maintenance, recovery, and deployment instructions.

Until those records exist, every item in this document remains **Future Expansion**.
