# UPPER_POD_ELECTRONICS_LAYOUT


<!-- FALCON-DOST-REVISION-NOTE:START -->
> **Current revision note (2026-10-10):** Use the DOST major revision baseline in [`docs/REVISION_2026-10-10.md`](../../docs/REVISION_2026-10-10.md) unless this file is explicitly archived. The active design is a compact single-tube / small-buoy, ESP32-based, event-driven, cloud-first system. LoRa, large Bay Station hardware, tall tower layouts, and continuous every-second uploads are legacy or optional fallback assumptions.
<!-- FALCON-DOST-REVISION-NOTE:END -->

Creates separate editable equipment-envelope components inside the sealed upper
pod. The battery and BMS occupy the lowest level, the MPPT, DC-DC, fuse block,
and disconnect occupy the thermal/power level, and the Mini PC, ESP32, LTE
modem, and sensor distribution board occupy the upper service level.

These are parametric packaging envelopes, not manufacturer-certified component
models. Confirm purchased hardware dimensions before manufacturing.
