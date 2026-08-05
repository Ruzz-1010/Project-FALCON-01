# Assembly Guide

## Purpose
Define safe current setup and gates for future assembly.

## Scope
USB-powered ESP32 bench setup and future electronics/marine assembly.

## Current Status
Only the ESP32 bench setup is confirmed; no sensor or marine assembly is approved.

## Architecture
Controller bench -> individual modules -> protected power -> enclosure -> mechanical structure -> integrated validation.

## Implementation
Place ESP32 on a non-conductive surface, inspect it, use a data-capable USB cable, confirm CH340 port, flash firmware and LittleFS separately, then verify startup and portal.

Do not guess GPIOs, connect unadjusted LM2596 output, energize an unprotected battery/solar system, or claim an IP rating without assembly testing.

## Future Expansion
Add approved schematics, wiring, connectors, torque/seal procedures, photographs, BOM revisions, and inspection forms.

## Engineering Notes
Disconnect power before wiring. Marine energy storage requires proper supervision and protective equipment.

## Revision History
| Version | Date | Change |
| --- | --- | --- |
| 1.0 | 2026-08-05 | Initial bench-only guide. |
