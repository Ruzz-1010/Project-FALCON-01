# Project FALCON Thesis Documentation Register


<!-- FALCON-DOST-REVISION-NOTE:START -->
> **Current revision note (2026-10-10):** Use the DOST major revision baseline in [`docs/REVISION_2026-10-10.md`](../docs/REVISION_2026-10-10.md) unless this file is explicitly archived. The active proposal core is a compact ESP32-based buoy with **water pressure sensing, wind speed/direction sensing, GPS for exact position and security, battery + solar power, and Wi-Fi/LTE internet communication**. LoRa, large Bay Station hardware, tall tower layouts, and continuous every-second uploads are legacy or optional fallback assumptions.
<!-- FALCON-DOST-REVISION-NOTE:END -->

## Active revision 2026-10-10

The approved direction is a smaller compact can-buoy with ESP32 local sampling, event-driven summaries and alerts, direct cloud connectivity through Wi-Fi for laboratory work or 4G/LTE for a remote trial, and a reduced battery sized from measured modem duty. The active equipment and alternative sensor list is in [FALCON Revised Event Driven BOM and Sensor Options.docx](FALCON%20Revised%20Event%20Driven%20BOM%20and%20Sensor%20Options.docx). The current architecture is maintained in `../docs/PROJECT_CONTEXT.md` and `../docs/BAY_STATION_ARCHITECTURE.md`.

## Current authority

- `FALCON Revised Event Driven BOM and Sensor Options.docx` — current equipment,
  alternative-sensor, cost, and procurement baseline after the 2026-10-10 DOST
  revision.
- `BayStation.docx` — earlier expanded thesis documentation retained for reference;
  its LoRa/Bay Station assumptions are superseded by the event-driven cloud baseline
  until the thesis chapters are regenerated.
- `PROJECT FALCON-01 - V3 Documentation.docx` — filename-compatible copy of the
  canonical Bay Station V3.7 thesis; it is retained for users who open the
  earlier V3 filename.
- `../docs/PROJECT_CONTEXT.md` — canonical repository context v9.0.
- `../docs/BAY_STATION_ARCHITECTURE.md` — approved functional split.
- `../docs/BAY_STATION_SELECTION_REGISTER.md` — unresolved decisions and release gates.
- `../docs/PRESSURE_SENSOR_BASELINE.md` — authoritative HPT604 candidate decision, interface, procurement, venting, and validation gates.

## Superseded records

Ten documents previously marked LEGACY / SUPERSEDED were moved unchanged to [archive/](archive/README.md) on 2026-09-11. Start with `BayStation.docx` for the current full thesis.

### Redundant-file cleanup (2026-10-02)

Three files that duplicated existing records were removed after a content audit. All three are recoverable from Git history if needed:

- `FALCON_Chapters1-2_Compile_first.docx` — superseded by `Design and Development of a Solar.docx`, which is the same Chapters 1–2 document in a newer, expanded revision (identical headings; added text).
- `Project_FALCON_DOST_Presentation.pptx` — superseded by `Project_FALCON_DOST_Presentation_Wednesday.pptx`, which has identical slide text and a newer revision.
- `visuals/electronics-wiring-sketch.png` — byte-identical duplicate of `visuals/electronics-wiring.png`.

`PROJECT FALCON-01 - V3 Documentation.docx` is intentionally retained because it is the generated sync output of `scripts/build_baystation_thesis.py`, not a duplicate.

Other DOCX files in this directory are supporting or legacy records. Every copy carries a dated document-control notice; any body text that conflicts with the revised BOM DOCX, `PROJECT_CONTEXT.md`, or `PRESSURE_SENSOR_BASELINE.md` is superseded. Older V2/V3 files, including `PROJECT FALCON-01 - V3 Documentation - LEGACY.docx`, are retained for historical traceability and must not override the event-driven cloud architecture.
They may contain obsolete Orange Pi-on-buoy, USB-only deployment, five-page
dashboard, BNO085, load-cell, optional-AI, power, or prototype assumptions.

## Current non-negotiable boundaries

- No mini PC is installed on or powered by the buoy.
- The buoy contains the ESP32, approved sensors, event-detection logic, local buffer, power, and either Wi-Fi or a 4G/LTE modem for the selected test path. It has no mini PC or LoRa gateway.
- The cloud service performs storage, pressure-wave processing, optional prediction, API/dashboard hosting, and alerts. A development computer may temporarily host the service during bench work.
- The dashboard has four primary pages: Overview, Buoy Motion, Sensors, and Logs & Alerts.
- Simulator/build/test results are not physical accuracy, cellular reliability, AI accuracy, or deployment-readiness evidence.
- The core proposal sensors/modules are water pressure, wind speed/direction, GPS position/security, battery/solar power monitoring, and internet communication. Water temperature and extra environmental sensors are excluded from the low-cost minimum build unless separately approved.
- The preferred long-duration pressure candidate is the Holykell HPT604 Type A, provisionally 0–2 mH2O vented gauge with 4–20 mA output. Documented 4–20 mA, 0–5 V/0–10 V, RS485/Modbus, and marine digital alternatives remain under the same seawater, sealing, range, and calibration gates. Bar02 is bench-only.
