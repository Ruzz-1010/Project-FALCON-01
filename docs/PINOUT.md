# Pinout Register

## Purpose
Prevent guessed or unsafe GPIO assignments.

## Scope
External sensors, buses, outputs, voltage domains, and future edge links.

## Current Status
**Status: Not Yet Finalized.** No external GPIO assignment exists in source.

## Architecture
Future devices may use I2C, UART, OneWire, ADC, or digital GPIO after board-specific review.

## Implementation
| Function | GPIO | Interface | Status |
| --- | --- | --- | --- |
| Temperature | TBD | TBD | Planned |
| IMU | TBD | I2C candidate | Planned |
| GPS | TBD | UART candidate | Planned |
| Power monitor | TBD | I2C candidate | Planned |
| Leak/tamper | TBD | TBD | Planned |
| Edge link | TBD | UART/USB candidate | Not finalized |

Approval requires datasheet, voltage/current review, pull-up requirements, connector, boot test, and source constant.

## Future Expansion
Add versioned wiring and schematic references after hardware selection.

## Engineering Notes
Never apply an unverified 5 V signal to an ESP32 GPIO. Board variants differ.

## Revision History
| Version | Date | Change |
| --- | --- | --- |
| 1.0 | 2026-08-05 | Unassigned pin register. |
