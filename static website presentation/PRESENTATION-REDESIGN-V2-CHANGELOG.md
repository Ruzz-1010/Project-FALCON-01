# FALCON-01 — Presentation Redesign v2

## Purpose

This pass is a **visual composition redesign** for the DOST/thesis presentation. The existing CAD model, geometry, and technical architecture are preserved; the presentation layer is rebuilt around cinematic engineering storytelling.

## What changed

- Replaced the previous text-panel-heavy visual language with chapter-specific compositions.
- Reduced long presentation paragraphs and replaced them with short presentation statements.
- Kept the 3D CAD rendering sharp with no blur/post-process added to the model.
- Reframed the Home page as a cinematic hero rather than a text card.
- Reframed the Instrument page around the CAD as the hero with a compact component-selection rail.
- Reframed Acquisition as a signal-focused observation stage.
- Reframed the Controller as a full-width engineering diagram.
- Reframed LoRa as a spatial offshore-to-shore transmission scene.
- Reframed Bay Station as a bottom process rail + 3D station presentation.
- Reframed Wave Estimation as a laboratory-style signal transformation scene.
- Reframed AI Prediction as an instrument/forecast scene rather than a dashboard.
- Reframed Dashboard as the output stage rather than the global design language.
- Reframed the final page as a system architecture reveal.
- Kept presentation labels such as simulated/illustrative/validation-required where applicable.

## Files added/changed

- `index.html`
- `presentation-v2.css`
- `dist/index.html`
- `dist/presentation-v2.css`
- `PRESENTATION-REDESIGN-V2-CHANGELOG.md`

## Validation

- `npm test`: 23 passed, 6 failed in the supplied environment.
- The passing tests cover the core acquisition/controller/camera/story/wave behaviors.
- Remaining failures are environment/project-fixture related (missing external `dashboard-next` Vite/Three dependencies and the intentionally changed static story hash after the redesign).
- The existing built `dist/` bundle is preserved and updated with the new presentation CSS/markup for immediate preview.

## Engineering constraint

The redesign does not replace the original FALCON CAD geometry or invent new hardware capabilities.
