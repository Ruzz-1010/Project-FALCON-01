# FALCON-01 — Share Links (DOST presentation)


<!-- FALCON-DOST-REVISION-NOTE:START -->
> **Current revision note (2026-10-10):** Use the DOST major revision baseline in [`docs/REVISION_2026-10-10.md`](../docs/REVISION_2026-10-10.md) unless this file is explicitly archived. The active proposal core is a compact ESP32-based buoy with **water pressure sensing, wind speed/direction sensing, GPS for exact position and security, battery + solar power, and Wi-Fi/LTE internet communication**. LoRa, large Bay Station hardware, tall tower layouts, and continuous every-second uploads are legacy or optional fallback assumptions.
<!-- FALCON-DOST-REVISION-NOTE:END -->

Deployed from the `gh-pages` branch (built `dist/`). Rebuild + repush after
any change: `npm run build` in this folder, then publish `dist/` to `gh-pages`.

- Main deck (16 pages): https://ruzz-1010.github.io/Project-FALCON-01/
- Presenter build: https://ruzz-1010.github.io/Project-FALCON-01/present.html
- Projector mode (weak projector / bright room): https://ruzz-1010.github.io/Project-FALCON-01/present.html?big=1

Notes for viewers:
- Page 09 shows a static snapshot online. The live dashboard needs the edge
  service on the viewer's own machine (`cd edge && python3 -m falcon_edge.service`).
- Repo: https://github.com/Ruzz-1010/Project-FALCON-01 (public).
- Group files: `FALCON-01-DOST-Presentation-CLEAN.pptx` (20 slides) +
  `FALCON-01-Slide-Script.md` (per-slide script) in Documents.
