# Project FALCON Mechanical Baseline v4.0

## Authority

Authority: PROJECT_CONTEXT.md v4.0.

Status: approved Phase 1 mechanical baseline; validation ongoing.

This refactor does not redesign the mechanical system.

## Approved Assembly

- HDPE main float;
- four HDPE stabilizer buoys;
- marine aluminum arms;
- stainless steel tension cables;
- central ballast;
- single anchor;
- waterproof electronics enclosure;
- upper equipment/sensor structure;
- and solar-panel assembly.
- Orange Pi Zero 3 mounting, airflow, cable strain relief, and service access within the electronics enclosure.

## Design Objectives

- stable flotation;
- reduced roll and pitch;
- reliable sensor orientation;
- low center of gravity;
- marine corrosion resistance;
- serviceable electronics;
- secure solar mounting;
- protected cable routing;
- and recoverable single-anchor deployment.

## HDPE Main Float

Functions:

- primary buoyancy;
- central structural support;
- electronics support;
- solar-frame support;
- sensor-frame support;
- and ballast/mooring load transfer.

Requirements:

- no cracks or unapproved penetrations;
- sealed interfaces;
- documented waterline under test load;
- and serviceable mounting points.

## Four Stabilizer Buoys

Quantity: four.

Functions:

- increase righting stability;
- reduce excessive roll;
- reduce excessive pitch;
- and support consistent sensor attitude.

The stabilizers shall remain symmetric unless an approved analysis supports a change.

## Marine Aluminum Arms

Functions:

- connect stabilizers to the main assembly;
- transfer buoyancy/stability loads;
- and preserve geometry.

Requirements:

- marine-suitable alloy and finish;
- replaceable fastening;
- acceptable deflection;
- no sharp exposed edges;
- and isolation review where dissimilar metals contact.

## Stainless Steel Tension Cables

Functions:

- reduce arm flex;
- distribute loads;
- reinforce the stabilizer geometry;
- and improve durability under repeated motion.

Requirements:

- marine-grade stainless material;
- controlled tension;
- secure terminations;
- no broken strands;
- and inspection access.

## Central Ballast

Functions:

- lower center of gravity;
- increase righting moment;
- assist upright recovery;
- and stabilize sensor orientation.

Requirements:

- calculated/validated mass;
- secure primary attachment;
- secondary retention where practical;
- corrosion protection;
- and safe lifting/handling method.

## Single Anchor and Mooring

Phase 1 uses one anchor.

Functions:

- retain the buoy within an expected area;
- permit controlled swing;
- and support position-reference testing.

Requirements:

- site-appropriate anchor selection;
- documented line length;
- suitable line strength;
- chafe protection;
- secure connection below the central structure;
- and recovery plan.

Expected anchor swing and GPS uncertainty shall be included in drift thresholds.

## Electronics Enclosure

Design intent: IP67 or better, subject to validation.

Requirements:

- gasketed access;
- marine-suitable cable glands;
- strain relief;
- condensation management;
- internal mounting trays;
- separation of power and signal wiring;
- temperature monitoring;
- and maintenance access.

## Solar-Panel Assembly

The current approved digital model may use tilted solar panels.

Requirements:

- adequate sunlight exposure;
- secure wind-resistant brackets;
- no interference with antennas/sensors;
- no obstruction of service access;
- acceptable center-of-gravity effect;
- drainage;
- protected wiring;
- and safe edges.

Solar tilt shall be validated mechanically and energetically.

## Upper Sensor Array

The upper structure may support:

- wind-speed sensor;
- wind-direction sensor;
- GPS antenna;
- local communication antennas;
- navigation light;
- and lightning/air terminal provisions where approved.

Requirements:

- unobstructed wind exposure;
- antenna separation;
- rigid orientation reference;
- maintenance access;
- and protected cable entry.

## Sensor Placement

- IMU near the rigid central structure;
- pressure sensor at documented submerged depth;
- wind sensors above major obstructions;
- GPS with clear sky view;
- internal temperature at a representative enclosure location;
- battery monitor near the battery circuit;
- and solar monitor in the approved charging measurement path.

## CAD Configuration Management

CAD files shall use meaningful component names.

Every major revision shall record:

- revision identifier;
- date;
- author;
- purpose;
- changed components;
- compatibility impact;
- exported FBX/GLB version when used by the dashboard;
- and archived previous revision.

The dashboard 3D model is a visualization artifact and does not replace engineering drawings.

## Assembly Inspection

Before testing:

- inspect main float;
- inspect four stabilizers;
- verify arm fasteners;
- verify cable tension;
- verify ballast retention;
- verify mooring connection;
- verify enclosure seal;
- verify solar brackets;
- verify sensor mast;
- and verify cable strain relief.

## Mechanical Testing

Required tests:

- dry assembly inspection;
- flotation;
- static load;
- waterline measurement;
- roll recovery;
- pitch recovery;
- controlled motion/wave response;
- arm deflection observation;
- tension-cable inspection;
- ballast retention;
- anchor attachment;
- enclosure splash/waterproof test;
- and post-test damage inspection.

## Acceptance Evidence

Each test shall record:

- assembly revision;
- load condition;
- water condition;
- procedure;
- measured result;
- photographs/video;
- pass/fail;
- and corrective action.

## Maintenance

- rinse salt after retrieval;
- inspect corrosion;
- inspect biofouling;
- inspect cracks/deformation;
- inspect fastener torque;
- inspect tension-cable condition;
- inspect ballast and mooring;
- inspect seals/glands;
- clean solar panels;
- and record maintenance.

## Safety

- use appropriate lifting methods;
- secure ballast during handling;
- isolate battery power before enclosure work;
- avoid working beneath suspended loads;
- wear marine PPE during deployment/recovery;
- and follow site/boat safety requirements.

## Non-Goals

Phase 1 mechanical design does not include autonomous propulsion, autonomous navigation, dynamic positioning, multi-buoy docking, or alternate fleet hardware.

## Future Expansion

Alternate mooring systems, larger platforms, harsher-environment qualification, multi-buoy deployments, and additional sensor structures require later review.

## Revision History

| Version | Date | Change |
| --- | --- | --- |
| 4.0 | 2026-08-09 | Created controlled mechanical baseline without redesigning the approved main float, stabilizers, arms, cables, ballast, and single anchor. |
