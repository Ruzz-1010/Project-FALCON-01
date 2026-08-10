# FALCON Dashboard Next

Safe, page-by-page React + TypeScript migration of the FALCON dashboard. The existing dashboard remains the production fallback while this directory is developed and validated.

## Migrated pages

- responsive application shell and standard navigation;
- live Overview page;
- two-second polling of the existing Python edge API;
- dark/light themes; and
- typed telemetry contracts.

Phase 2 adds the Wave AI page with current-versus-predicted results, selectable
5/10/15-minute horizons, live history and forecast plotting, model confidence,
calculation evidence, and reversible presentation scenarios. A simulated sensor
failure is contained to the affected wave feed instead of taking down the shell.

## Run

Start the existing edge service on port `8765`, then:

```powershell
cd dashboard-next
npm install
npm run dev
```

Open `http://127.0.0.1:5173`. Overview and Wave AI are available. Other pages are
intentionally marked as pending until migrated and verified.
