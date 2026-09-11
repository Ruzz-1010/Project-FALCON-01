# Previous project versions

Files here were removed from active folders during the 2026-09-11 cleanup. They are retained unchanged for recovery and reference.

## Dashboard source

`dashboard-next/src/` contains eight components that are not reachable from the current application's `main.tsx` import graph: ArchitecturePage, CalibrationPage, FalconAssistant, HistoryPage, PowerPage, SecurityPage, TelemetryChart and WavePage. The unused assistant stylesheet is stored alongside them. The running app still includes Overview, Sensors, Buoy Motion, GPS, Logs & Alerts, and Settings.

These source files are historical, not independently runnable. To restore one, copy it to the active `dashboard-next/src/` folder and review its imports, API calls, styles, and navigation integration. Required shared dependencies remain in the active source tree. TypeScript checks and the dashboard build are required before enabling it.

## Model exports

`exports/` contains the older `FALCON-01.fbx`, `FALCON-01-tilt.fbx`, and `FALCON-01-original.glb` reference exports. The active V2 FBX/Fusion files remain in the root `exports/` directory; original editable Fusion sources remain in `exports/source/`. The model loaded by Buoy Motion remains in `dashboard-next/public/models/`.

The root-level `PROJECT FALCON -01 tilt.fbx` was an exact duplicate of `FALCON-01-tilt.fbx` and was moved to the desktop Trash. The retained copy is here at `exports/FALCON-01-tilt.fbx`.

Superseded thesis files have their own archive at `THESIS DOCUMENTATION/archive/`. Use `THESIS DOCUMENTATION/BayStation.docx` for the current full thesis and `docs/PROJECT_CONTEXT.md` for the current engineering scope.
