# ADJUSTABLE_LOW_BALLAST_V2


<!-- FALCON-DOST-REVISION-NOTE:START -->
> **Current revision note (2026-10-10):** Use the DOST major revision baseline in [`docs/REVISION_2026-10-10.md`](../../docs/REVISION_2026-10-10.md) unless this file is explicitly archived. The active design is a compact single-tube / small-buoy, ESP32-based, event-driven, cloud-first system. LoRa, large Bay Station hardware, tall tower layouts, and continuous every-second uploads are legacy or optional fallback assumptions.
<!-- FALCON-DOST-REVISION-NOTE:END -->

Creates a central 316L ballast rail below the rounded keel with four separate
removable weight plates, upper/lower locking collars, a secondary retention
cable, and a lower anchor-chain clevis. The old fixed ballast is hidden, not
deleted.

Plate mass and final rail depth must be established by loaded displacement,
freeboard, static-heel, roll/pitch recovery, and righting-moment tests. CAD
geometry alone does not approve deployment ballast.

The generator recognizes the V2 float by component-name prefix or its
`FALCON-MF-002` part metadata, so Fusion occurrence suffixes are supported.
