# TOP_CAP Fusion 360 Script


<!-- FALCON-DOST-REVISION-NOTE:START -->
> **Current revision note (2026-10-10):** Use the DOST major revision baseline in [`docs/REVISION_2026-10-10.md`](../../docs/REVISION_2026-10-10.md) unless this file is explicitly archived. The active proposal core is a compact ESP32-based buoy with **water pressure sensing, wind speed/direction sensing, GPS for exact position and security, battery + solar power, and Wi-Fi/LTE internet communication**. LoRa, large Bay Station hardware, tall tower layouts, and continuous every-second uploads are legacy or optional fallback assumptions.
<!-- FALCON-DOST-REVISION-NOTE:END -->

Creates `TOP_CAP` as a separate internal component in the active PROJECT
FALCON-01 design. The cap is positioned on the detected top of `MAIN_FLOAT`, but
it remains an independent component for joints, removal, and animation.

The full-width 650 mm HDPE cover includes a 12 mm plate, insertion skirt,
circumferential radial gasket groove, and outer drip lip. All nominal sizes are
listed as Fusion user parameters.
