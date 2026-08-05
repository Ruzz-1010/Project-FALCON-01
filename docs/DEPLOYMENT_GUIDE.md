# Deployment Guide

## Purpose
Define software deployment and future field gates.

## Scope
Build, firmware/filesystem flash, bench acceptance, and marine readiness.

## Current Status
Bench deployment is supported; marine deployment is not approved.

## Architecture
Source -> firmware/LittleFS builds -> both flashes -> bench acceptance -> client matrix -> future field gate.

## Implementation
Close serial monitor; run `platformio run`, `platformio run --target buildfs`, `platformio run --target upload`, and `platformio run --target uploadfs`. Use BOOT when required, then release it and press EN. Verify serial, AP, portal, API, controls, and record the Git commit.

Marine use additionally requires mechanical calculations, power/protection review, ingress testing, sensor calibration, mooring/stability tests, endurance tests, and emergency/maintenance plans.

## Future Expansion
Add signed artifacts, rollback, provisioning, deployment coordinates, and maintenance schedules.

## Engineering Notes
The maintenance dashboard does not prove marine readiness.

## Revision History
| Version | Date | Change |
| --- | --- | --- |
| 1.0 | 2026-08-05 | Initial deployment gates. |
