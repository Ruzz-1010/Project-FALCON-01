# FALCON — cinematic static presentation

This folder replaces the former `dashboard-next/thesis` presentation. It is a new vanilla HTML/CSS/JavaScript experience, not a restyled version of the former React site. The operational dashboard is unchanged.

## Run locally

```sh
cd "static website presentation"
npm run dev
```

Open http://127.0.0.1:5175. Existing Vite and Three.js dependencies in `dashboard-next/node_modules` are reused; no additional package installation is needed on this checkout.

```sh
npm run build
npm test
npm run preview
```

Preview: http://127.0.0.1:4175. Copy **this folder’s `dist/`** to any static host, or serve it with `python3 -m http.server 4175 --directory dist`. The built folder is self-contained, including the original CAD and logo. Use HTTP rather than double-clicking `index.html` (`file://` cannot reliably load ES modules/GLB). No backend, database, API, external fonts, login or live telemetry is used. The old `npm run thesis:*` aliases also point here.

## Experience

### Home opening

Home alone now uses a held four-shot ocean opening: wide offshore → discovery → approach → listening. Normal scrolling controls the camera; “Begin the journey” runs a cancellable 5.2-second approach into the original Instrument section. Wheel, touch or navigation keys interrupt the scripted scroll. Pause Motion/reduced-motion bypasses automatic travel.

Six directional wave components deform the Home water mesh itself, with corresponding analytical surface normals, restrained crest highlights and no moving texture shortcut. Home buoy heave/pitch/roll samples the same wave field. A center-dense mesh keeps geometry lightweight. Home ocean changes fade to the existing water before Instrument, and the final Home camera target matches the existing Instrument pose. Pages 01–09 markup is protected by a regression hash test. These are illustrative motions, not a validated ocean or buoyancy model.

### 04 / Crossing the Water — coastal environment

Chapter 04 replaces the flat radio illustration with a locally generated Three.js community: a modest Bay Station, 12 residences, 22 coconut trees, vegetation, roads, rocky beach and terrain. A single cylindrical receiver mast with a compact top-mounted receiver and coaxial antenna tip is positioned beside the station. Cyan packets cross the actual 3D space from the original offshore buoy to the receiver endpoint. Interrupt/restore controls also pause/resume that physical link visualization. The camera approaches the shoreline and receiver into chapter 05; the other story chapters and original buoy CAD remain intact.

This is a fictional illustrative environment, not a photograph, surveyed location, measured radio range or approved mast specification. Static meshes are batched by material; packet instances share geometry. The scene adds no remote assets or APIs. Tests check finite geometry, community inventory, endpoint alignment, camera framing and outage visibility. Browser visual verification is still pending because no browser is connected to the authoring session.

Scroll through ten scenes: Ocean → buoy reveal → sensors → ESP32 → LoRa → Bay Station → wave estimation → AI → dashboard reveal → system pullback. Bottom chapter markers are keyboard-accessible jump links. Drag the uncovered ocean area in the reveal/sensor scenes to orbit; component buttons provide the same selection access as projected hotspots.

Use the LoRa interruption/restore control to observe an in-memory queue replaying original timestamps and rejecting duplicate IDs. Processing steps switch the illustrative pressure signal. Run prediction reveals a simulated future trace against persistence. Four dashboard tabs are a static presentation of the FALCON operator interface, not an embedded connection to the live app.

Motion can be paused. System reduced-motion preference disables automatic movement by default; the control allows an explicit opt-in. Tab inactivity pauses rendering; packet simulation runs only in the ESP32/radio/shore scenes. Three.js is loaded separately, pixel ratio capped at 1.4 and the loop capped around 30 fps. No heavy physics. Loss of WebGL leaves the HTML diagrams and story accessible.

## Preserved design / research boundaries

### Component inspection

Click any of the five component buttons or CAD hotspots to run a 1.65-second eased inspection camera move. The panel appears after arrival; Escape or “Back to buoy” returns to the saved view without navigation. Hover/focus provides a light preview without moving the camera. Source materials are temporarily cloned for cyan emphasis and dimming, then restored; the CAD file is unchanged. The ESP32 target is the existing control enclosure, not an invented exposed board. Mobile framing leaves the component above the bottom sheet. Reduced-motion/pause uses immediate positioning instead of animated travel. Scrolling out of buoy scenes cancels inspection.

Inspection tests load the actual GLB and check all five target positions at desktop, tablet and mobile aspect ratios, plus easing endpoints and content. These are mathematical/automated checks, not a substitute for browser-based interaction and visual QA.

- Model: `dashboard-next/public/models/PROJECT-FALCON-V2.glb` — 622 nodes, 251 meshes; SHA-256 `d8674ce9415ce4b85b69ddddfd0a33609923146c191cabd915d5a6e8845d30ce`.
- No replacement buoy, removed meshes, remeshing or invented component placement. Original geometry and materials are retained. Whole-model orientation/position and mild illustrative motion are view transforms only. Ocean/waterline are illustrative, not a buoyancy solution.
- CAD retains legacy antenna names and an Orange Pi envelope. The on-screen reference note distinguishes those from V4.1: the buoy contains ESP32 sensing/LoRa, while computing, storage and AI remain on shore. Final mechanical revision is pending.
- Shore facility and controller diagrams are conceptual illustrations, not fabricated hardware CAD or actual deployment photography.
- Source: `THESIS DOCUMENTATION/BayStation.docx`, V4.1, 10 September 2026. HPT604 remains a deployment candidate with supplier confirmation/calibration pending. Simulation does not establish wave accuracy, radio range, energy endurance, AI skill or field readiness.
- “Measured quantity” identifies pressure’s role; every waveform and number in this site is simulated. The estimated Hs output is an illustration, not a pressure-processing implementation. AI and baseline curves are not trained-model results.

## Validation

`npm test` covers ten-scene coverage, packet buffering/recovery/duplicate rejection, time continuity, original CAD hash and asset identity, static-only constraints and accessibility hooks. `npm run build` bundles the complete local site. Browser-based visual/interaction QA remains required on desktop, tablet and mobile; the authoring session had no connected browser surface, so no visual pass is claimed.

Removed presentation source is recoverable through Git history; no operational dashboard, thesis document or source CAD was deleted. Generated output is intentionally excluded from Git.
