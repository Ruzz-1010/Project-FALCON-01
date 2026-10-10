# Previous project versions


<!-- FALCON-DOST-REVISION-NOTE:START -->
> **Current revision note (2026-10-10):** Use the DOST major revision baseline in [`docs/REVISION_2026-10-10.md`](../docs/REVISION_2026-10-10.md) unless this file is explicitly archived. The active design is a compact single-tube / small-buoy, ESP32-based, event-driven, cloud-first system. LoRa, large Bay Station hardware, tall tower layouts, and continuous every-second uploads are legacy or optional fallback assumptions.
<!-- FALCON-DOST-REVISION-NOTE:END -->

Files here were removed from active folders during the 2026-09-11 cleanup. They are retained unchanged for recovery and reference.

## Dashboard source

`dashboard-next/src/` retains the saved FalconAssistant component and its stylesheet for a future user-requested return. Seven disconnected legacy components (ArchitecturePage, CalibrationPage, HistoryPage, PowerPage, SecurityPage, TelemetryChart and WavePage) were moved to desktop Trash during the follow-up cleanup. They had no active source references or uncommitted edits. The running app still includes Overview, Sensors, Buoy Motion, GPS, Logs & Alerts, and Settings.

These source files are historical, not independently runnable. Removed files remain recoverable from desktop Trash or Git commit `7fb489a` at their `archive/dashboard-next/src/` paths. Before restoring any component to the active source folder, review its imports, API calls, styles, and navigation integration. Required shared dependencies remain in the active source tree. TypeScript checks and the dashboard build are required before enabling it.

Regenerable Python caches under tools, scripts, edge tests, edge services and the KiCad carrier folder were also moved to Trash. No source scripts, telemetry database, thesis version, CAD model, or generated active dashboard bundle was removed by this cleanup.

## Model exports

`exports/` contains the older `FALCON-01.fbx`, `FALCON-01-tilt.fbx`, and `FALCON-01-original.glb` reference exports. The active V2 FBX/Fusion files remain in the root `exports/` directory; original editable Fusion sources remain in `exports/source/`. The model loaded by Buoy Motion remains in `dashboard-next/public/models/`.

The root-level `PROJECT FALCON -01 tilt.fbx` was an exact duplicate of `FALCON-01-tilt.fbx` and was moved to the desktop Trash. The retained copy is here at `exports/FALCON-01-tilt.fbx`.

Superseded thesis files have their own archive at `THESIS DOCUMENTATION/archive/`. Use `THESIS DOCUMENTATION/BayStation.docx` for the current full thesis and `docs/PROJECT_CONTEXT.md` for the current engineering scope.
