# Project FALCON Prototype Redesign Baseline v6.1

Date: 26 August 2026

## Current status

The physical and visual buoy prototype is **under redesign**. No existing screenshot, rendered image, GLB/GLTF model, Fusion 360 assembly, component position, enclosure shape, float dimension, frame geometry, or solar-panel arrangement is approved as the replacement design.

Existing CAD, images, diagrams, prompts, and component READMEs are retained as design references and revision history only. They must not be described as the current, final, fabrication-ready, deployment-ready, or adviser-approved prototype.

## Requirements that remain valid

The redesign must preserve the approved functional architecture unless a later adviser decision changes it:

- pressure-based **estimated wave height**;
- ESP32 sensor acquisition;
- USB/UART transfer to an Orange Pi Zero 3 (4 GB);
- GPS, wind speed/direction, sealed water temperature, power, security, and enclosure-health monitoring;
- passive single-anchor mooring;
- local storage, API, and five-page dashboard;
- optional AI isolated from core monitoring;
- no required BNO085, salinity sensor, or anchor-chain load cell.

These requirements define system function, not the new external form or component placement.

## Values intentionally reset to TBD

The following must be re-established from the replacement prototype and may not be copied automatically from older revisions:

- float shape, dimensions, displacement, waterline, freeboard, and material thickness;
- frame geometry, mast height, member size, fasteners, and load paths;
- enclosure dimensions, internal tray layout, cooling approach, and cable-gland positions;
- solar-panel quantity, size, mounting position, and structural brackets;
- battery, ballast, center of gravity, righting moment, and lifting points;
- sensor, antenna, navigation-light, and wind-instrument placement;
- mooring attachment geometry, anchor hardware, and recovery arrangement;
- dashboard 3D model, presentation render, and deployment-video reference image.

The electrical energy requirement remains governed by measured consumption and the calculations in `POWER_CALCULATIONS.md`; the new geometry must not dictate unverified electrical ratings.

## Replacement acceptance checklist

Before the new design becomes the current prototype:

1. Assign a new mechanical revision and record the source CAD file.
2. Provide dimensioned overall, side, top, enclosure, and sensor-placement views.
3. Confirm every selected physical component fits with connector and service clearance.
4. Complete mass, displacement, loaded-waterline, freeboard, center-of-gravity, and initial-stability calculations.
5. Review structural load paths, corrosion isolation, fasteners, cable routing, ingress protection, drainage, ventilation, and maintenance access.
6. Verify solar exposure, antenna clearance, wind-sensor exposure, and pressure-sensor installation depth.
7. Run CAD interference checks and document every unresolved conflict.
8. Update the BOM, mechanical guide, assembly guide, wiring drawings, dashboard model, presentation material, and thesis figures from the same approved revision.
9. Complete dry fit, leak, flotation, heel/righting, ballast-retention, and controlled-water tests before any deployment claim.
10. Obtain adviser/team approval and then change the status from `UNDER REDESIGN` to `APPROVED FOR CONTROLLED PROTOTYPE BUILD`.

## Truthful-use rule

Until the checklist is complete, use the wording **proposed replacement prototype**. Do not use **final design**, **actual deployed unit**, **manufacturing-ready**, or **field-validated**.
