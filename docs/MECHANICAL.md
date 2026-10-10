# Project FALCON Mechanical Reference — Redesign Hold


<!-- FALCON-DOST-REVISION-NOTE:START -->
> **Current revision note (2026-10-10):** Use the DOST major revision baseline in [`docs/REVISION_2026-10-10.md`](REVISION_2026-10-10.md) unless this file is explicitly archived. The active proposal core is a compact ESP32-based buoy with **water pressure sensing, wind speed/direction sensing, GPS for exact position and security, battery + solar power, and Wi-Fi/LTE internet communication**. LoRa, large Bay Station hardware, tall tower layouts, and continuous every-second uploads are legacy or optional fallback assumptions.
<!-- FALCON-DOST-REVISION-NOTE:END -->

## Authority

Authority: `PROJECT_CONTEXT.md` v6.1 and `PROTOTYPE_REDESIGN_BASELINE.md`.

Status: **SUPERSEDED REFERENCE — NOT THE CURRENT PROTOTYPE.** The replacement body, dimensions, frame, enclosure, solar arrangement, ballast, sensor placement, and dashboard model are TBD.

## Previous Revision 5 Assembly Reference

- `MAIN_FLOAT_TRADITIONAL_V2`: marine-grade HDPE single-body float;
- Ø650 mm cylindrical upper body with the existing removable top-cap interface;
- 240 mm-deep rounded tapered underwater keel;
- central ballast and suspension connection;
- single-anchor mooring system;
- waterproof two-layer electronics enclosure and ventilation ducts;
- removable upper equipment frame and structural stanchions;
- tilted four-panel solar array;
- navigation light, GNSS, wind-speed/direction sensor, and approved antennas.

This entire Revision 5 assembly and the earlier four-stabilizer Revision 4 arrangement remain in CAD only for traceability. Neither is the approved replacement prototype.

## Single-Body Main Float

Nominal geometry:

- upper outside diameter: 650 mm;
- upper cylindrical height: 380 mm;
- rounded tapered keel depth: 240 mm;
- overall body height: 620 mm;
- nominal HDPE wall: 6 mm;
- open/removable service top compatible with the existing top cap.

Functions:

- primary buoyancy;
- hydrodynamic roll/pitch damping from the tapered keel;
- support for the electronics and upper equipment structure;
- direct ballast/mooring load transfer;
- reduced deployed footprint compared with the outrigger configuration.

Requirements:

- no unapproved penetrations;
- sealed and gasketed interfaces;
- smooth underwater transitions without sharp snagging edges;
- documented loaded waterline, freeboard, displacement, and center of gravity;
- verified righting moment with final ballast;
- serviceable top cover and ventilation bulkheads.

The new geometry is not approved for field deployment until flotation and stability tests demonstrate acceptable roll recovery, pitch recovery, and freeboard without the stabilizers.

## Central Ballast

The ballast shall be repositioned below the new keel so it does not intersect the V2 hull. Final position and mass shall be established by calculation and controlled flotation testing.

Requirements:

- calculated and measured mass;
- secure primary attachment;
- secondary retention where practical;
- corrosion protection;
- safe lifting method;
- clearance from the hull through the full motion envelope.

## Single Anchor and Mooring

Phase 1 retains one anchor below the central ballast. The mooring shall permit controlled swing and include appropriate line/chain strength, shackles, chafe protection, and a recovery plan. GPS drift thresholds shall include expected anchor swing and measurement uncertainty.

## Electronics and Ventilation

The enclosure design intent remains IP67 or better, subject to validation. Intake and exhaust paths shall use sealed top-cover bulkheads, hidden upper risers, downward-facing rain outlets, serviceable filters, strain relief, and condensation management.

## Solar and Upper Sensor Structure

The removable upper structure carries the tilted solar array and approved sensors. Requirements include wind-resistant brackets, direct load paths to the structural frame, antenna separation, unobstructed wind exposure, drainage, protected wiring, and top-cap service access.

## Archived CAD Configuration

- Previous Revision 5 body: `MAIN_FLOAT_TRADITIONAL_V2` (`FALCON-MF-002`).
- Legacy body: `MAIN_FLOAT` (`FALCON-MF-001`).
- Legacy stabilizer scripts remain archived and must not be used for new Revision 5 assemblies.
- Never delete legacy CAD components from the master design; suppress/hide them in the Revision 5 representation.
- Exported F3D/FBX/GLB files must identify their mechanical revision.
- Dashboard models must be labeled `REFERENCE MODEL` until replaced from the newly approved assembly.

## Replacement design rule

Do not revise this old geometry into a new baseline by changing isolated dimensions. Create a named new mechanical revision, then complete the calculation, fit, interference, serviceability, and controlled-test gates in `PROTOTYPE_REDESIGN_BASELINE.md`. Only after approval should the new verified values replace this reference.

## Assembly Inspection

- inspect the V2 HDPE body and tapered keel;
- inspect top-cap gasket and vent bulkheads;
- verify upper-frame fasteners and stanchions;
- verify solar brackets and sensor clearances;
- verify ballast clearance and retention;
- verify mooring and anchor connections;
- inspect cable glands and strain relief.

## Required Mechanical Tests

- dry assembly and interference inspection;
- leak test;
- loaded flotation and waterline measurement;
- freeboard measurement;
- static heel test;
- roll and pitch recovery;
- controlled wave response;
- ballast-retention and mooring-load tests;
- ventilation splash/rain-ingress test;
- post-test crack, deformation, and water-ingress inspection.

## Safety

- use appropriate lifting methods;
- secure ballast during handling;
- isolate battery power before enclosure work;
- do not work below suspended ballast or anchor loads;
- use marine PPE during deployment/recovery;
- do not field-deploy Revision 5 before documented stability validation.

## Revision History

| Version | Date | Change |
| --- | --- | --- |
| 4.0 | 2026-08-09 | Controlled four-stabilizer mechanical baseline. |
| 5.0 | 2026-08-13 | Replaced the production direction with a compact single-body Ø650 HDPE buoy and 240 mm rounded tapered keel; moved the outrigger system to Legacy Revision 4. |
| HOLD | 2026-08-26 | Superseded Revision 5 as the active prototype; all replacement geometry and placement reset to TBD. |
