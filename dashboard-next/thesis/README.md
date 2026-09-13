# FALCON interactive thesis website

Separate, static/local-first research presentation. It does not replace the monitoring dashboard, call the Bay Station API, change hardware settings or upload data.

## Run

From `dashboard-next/` (uses the existing dependencies):

```sh
npm run thesis:dev
```

Open `http://127.0.0.1:5175/`.

For the static build:

```sh
npm run thesis:build
npm run thesis:preview
```

Preview: `http://127.0.0.1:4175/`. The portable build is in repository-root `thesis-dist/`. Serve that folder over local HTTP, not `file://`. After dependencies are installed, the build and presentation require no external APIs or Internet connection. Model, scripts, styles and logo are bundled locally. Generated output is intentionally not committed.

## Authority and preserved assets

- Content: `THESIS DOCUMENTATION/BayStation.docx`, Version 4.1, 10 September 2026. Its complete body text was inspected for this implementation; the DOCX was not edited or reformatted.
- Supplied geometry: `dashboard-next/public/models/PROJECT-FALCON-V2.glb`, 622 nodes / 251 meshes. SHA-256: `d8674ce9415ce4b85b69ddddfd0a33609923146c191cabd915d5a6e8845d30ce`.
- No buoy geometry is generated or substituted. Whole-model orientation and uniform view scaling are presentation transforms. The ocean and selection marker are visual aids, not fabricated hardware.
- Existing CAD includes legacy LTE/Wi-Fi antenna names and an Orange Pi envelope. The visible CAD note explains these conflicts. No LoRa hardware is mapped to those objects and no legacy computer is described as part of the V4.1 buoy. Final mechanical revision remains pending.
- Hotspots use existing named CAD nodes. ESP32/battery labels refer to model envelopes; tamper highlights the enclosure rather than guessing a switch location. LoRa has a text guide only because its final hardware/placement is not frozen.

## Interaction coverage

- Orbit/zoom/pan, reset view, mild optional illustrative buoy/water motion, mesh picking and keyboard-accessible component guide.
- Sixteen-step play/pause/next/reset walkthrough with packet-route highlighting.
- Selectable pressure-processing stages and method-freeze requirements.
- AI sequence, simulated history/future chart, chronological split and pending metrics.
- Four-page standalone dashboard preview, compact settings and rule-based assistant.
- Failure scenarios P-01, C-01, I-01, G-01, T-01, A-01, B-01, R-01 and maintenance DISARMED.
- LoRa buffer/recovery illustration, preserved example timestamps, separate Internet-outage behavior.
- Planning-only energy calculator and eight validation categories; six milestones.

No numeric metric claims field accuracy. Examples do not execute the physical pressure correction, AI training, radio transport, authentication, database recovery or alarms. Buffer capacity and recovery text are design expectations, not implementation proof.

## Validation

`npm run thesis:build` checks TypeScript and bundles the static site. `node --test tests/thesis-site.test.mjs` checks scenario semantics, thesis content, original-model identity and local asset references. The separate monitoring app must still pass `npm run build`.

Browser visual/interaction QA must include 360 px mobile, tablet and desktop; model picking, context-loss fallback, play/pause, AI demo, all outages, keyboard focus, and reduced motion. No browser surface was connected in the authoring session, so those visual tests remain a handoff check rather than a claimed pass.

Performance: 3D is a lazy-loaded chunk, the original model is about 4.3 MB, pixel ratio is capped at 1.5, rendering is limited to roughly 30 fps and paused offscreen/background. Reduced-motion disables automatic buoy movement and CSS motion. No heavy physics, external font requests or generated textures are used.
