# FALCON-01 Presentation Session Notes — 2026-10-05

How this file was made: chat recap written by the coding agent so decisions and
changes are not lost. The chat app itself has no export button — copy/paste from
the chat window is the only way to keep the raw conversation.

## Team (locked)
- Jhon Ruzzel Correa — Hardware + Power + LoRa firmware
- Mayla Bacaltos + Gina Caballero — Thesis papers (hati)
- Gwyn Isabel Enriquez — Edge + AI + Dashboard
- Sir Jam — papers adviser · Sir Jeff — hardware adviser · 3rd mentor (SW/AI or DOST) — sourcing

## Decisions (locked)
- 15 pages (merged from 18): 10 Validation&Status · 11 Scope&Risks · 12 Roadmap&Team · 13 Impact&Funding · 14 Close
- Budget: PHP 90,000–150,000, midpoint ~115,000 (was 72–131k)
- Timeline: 5 months / 20 weeks bootcamp, half-OJT half-thesis, DOST as OJT host (was 8–12 mo)
- Keep: 3D buoy inspect (1.65s eased), Bay Station cutaway, LoRa crossing, smooth eased motion
- present.html = DOST projector master (`?big=1`, `P` presenter, `L` chapter list)

## Changes applied (in `static website presentation/`)
1. `story.js` — 15 chapters + CH renumbered, 5 bootcamp gates + execution/team export, funding 90–150k
2. `world.js` — poses 18→15 (finale kept); buoy/controller aim shifted right (x −0.9) off text column
3. `index.html` + `present.html` — merged wrap-up sections, 6-step Live Link strip, team-grid, new budget/timeline copy, footer 01/15
4. `dost-deck.js` — Gate labels, bootcamp line, team grid render
5. `dost-deck.css` — 5-gate rail, team-grid, link-steps styles
6. `style.css` — readability panels on text columns; unified plates for labs; dark table base; wave pills; 05 HUD solid plate + lifted micro-labels
7. `theme-deep.css` — removed 3 backdrop-blur rules over WebGL; 05 plate solid
8. `bay-station.css`, `present.css` — removed remaining backdrop blurs (projector stutter fix)
9. `main.js` — 200ms clicker/key debounce
10. `tests/story.test.mjs`, `tests/home.test.mjs` — guards updated for 15 pages + new budget (hash recomputed, reasons noted in-test)
11. Deleted: `PRESENTATION-REDESIGN-V2-CHANGELOG.md` (superseded), `node_modules/.vite*` cache

## Validation status
- `npm test`: 32 pass / 3 fail — the 3 fails are PRE-EXISTING (acquisition regex + 2 camera-framing math, files never touched, noted in PRESENTATION-BUILD.md)
- `npm run build`: passes · `git diff --check`: clean
- dist/ rebuilt and verified (15 chapters, new budget, team-grid, link-steps)

## Still open / needs human eyes (no browser in this session)
- Page 02 buoy position — confirm on real screen (tune aim x if needed)
- Page 05 HUD readability — user confirmed OK 2026-10-05
- 3rd mentor name + OJT hours — 1-line swap in `story.js` execution block when known
- Projector + mobile visual QA pass before defense

## Run it
```sh
cd "static website presentation"
npm run dev      # http://127.0.0.1:5175 + /present.html
npm run preview  # http://127.0.0.1:4175 (built dist)
npm test         # guard suite
```
