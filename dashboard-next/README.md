# FALCON Dashboard Next

Safe, page-by-page React + TypeScript migration of the FALCON dashboard. The existing dashboard remains the production fallback while this directory is developed and validated.

## Phase 1

- responsive application shell and standard navigation;
- live Overview page;
- two-second polling of the existing Python edge API;
- dark/light themes; and
- typed telemetry contracts.

## Run

Start the existing edge service on port `8765`, then:

```powershell
cd dashboard-next
npm install
npm run dev
```

Open `http://127.0.0.1:5173`. Other pages are intentionally marked as pending until migrated and verified.
