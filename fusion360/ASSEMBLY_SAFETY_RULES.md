# PROJECT FALCON-01 Assembly Safety Rules


<!-- FALCON-DOST-REVISION-NOTE:START -->
> **Current revision note (2026-10-10):** Use the DOST major revision baseline in [`docs/REVISION_2026-10-10.md`](../docs/REVISION_2026-10-10.md) unless this file is explicitly archived. The active design is a compact single-tube / small-buoy, ESP32-based, event-driven, cloud-first system. LoRa, large Bay Station hardware, tall tower layouts, and continuous every-second uploads are legacy or optional fallback assumptions.
<!-- FALCON-DOST-REVISION-NOTE:END -->

1. Never delete, transform, edit, suppress, hide, or replace an existing component.
2. Every generator creates only one new separate component unless explicitly approved.
3. Before creating geometry, stop if Fusion reports uncaptured component positions.
4. Never assign a name through `Occurrence.name`; name only the new component.
5. On rerun, stop without changes if the target component already exists.
6. After each successful component, inspect, Capture Position, and save before continuing.
