# PCB Physical-Fit Checklist


<!-- FALCON-DOST-REVISION-NOTE:START -->
> **Current revision note (2026-10-10):** Use the DOST major revision baseline in [`docs/REVISION_2026-10-10.md`](../../../docs/REVISION_2026-10-10.md) unless this file is explicitly archived. The active design is a compact single-tube / small-buoy, ESP32-based, event-driven, cloud-first system. LoRa, large Bay Station hardware, tall tower layouts, and continuous every-second uploads are legacy or optional fallback assumptions.
<!-- FALCON-DOST-REVISION-NOTE:END -->

Status: **required before final copper routing**. Print the PCB at exactly
100% scale; disable every printer option named Fit, Shrink, or Scale to page.

## Print calibration

- [ ] Measure a printed 50.00 mm reference with a caliper; acceptable result is
      49.90–50.10 mm.
- [ ] Measure the 165 x 125 mm board outline.
- [ ] Confirm all four M3-hole centers against the intended enclosure/standoffs.
- [ ] Sign and date the print only after scale is verified.

## Module fit

- [ ] U2 ESP32-DevKitC V4: both header rows, USB overhang, antenna end, and
      removal clearance match.
- [ ] U3 BNO085: headers and mounting holes align; axis/orientation is recorded.
- [ ] J3 GPS: header and holes align; antenna and optional u.FL access are clear.
- [ ] J4/J5 INA260: headers and mounting holes align; terminal-block cable paths
      stay off the carrier high-current copper.
- [ ] J6 MCP9808 and U4 ADS1115: headers, board edges, and connector access match.

## Harness connectors

- [ ] J2 accepts `GHR-04V-S`; latch and pin 1 match the board legend.
- [ ] J7–J10 accept `GHR-03V-S`; every latch faces the same service direction.
- [ ] A plugged cable can be removed without hitting the enclosure lid.
- [ ] Cable service loops meet the intended gland position without sharp bends.
- [ ] J11/J13 fan connectors mate without force and preserve fan pin order.

## Evidence and release

- [ ] Photograph the bare 1:1 print with a ruler/caliper visible.
- [ ] Photograph the top and bottom of every received module.
- [ ] Record results and photo paths in `footprint_measurements.csv`.
- [ ] Any mismatch is corrected in the footprint generator and reprinted.
- [ ] Final routing begins only after every critical row is marked `PASS`.

Reviewer: ____________________  Date: ____________________

Second reviewer: ______________  Date: ____________________
