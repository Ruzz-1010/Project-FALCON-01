# FALCON-01 — Presentation build (how to present it)

This build makes the cinematic site easier to present and easier for a panel
and listeners to understand. **Nothing original was changed.** `index.html`,
`style.css`, `main.js` and the 3D scene are exactly as they were.

## What was added

| File | What it is |
| --- | --- |
| `present.html` | A copy of the page that also loads the new presentation layer |
| `present.css` | Bigger type, plain-language helpers, cinematic polish, print handout |
| `present.js` | Presenter mode, the chapter jump list, projector mode |

## How to open it

Run the dev server and use the presentation address:

```sh
npm run dev
```

Then open **http://127.0.0.1:5175/present.html**

Do not double-click the file. ES modules and the 3D model need a real web
server (`file://` will not load them).

## Controls

| Key or button | What it does |
| --- | --- |
| **L** | Opens the chapter jump list — every chapter with one plain line |
| **P** | Presenter mode — hides the small technical labels, enlarges the words |
| **?big=1** | Projector mode for a weak projector or a bright room |
| **Ctrl + P** | Prints a clean text handout, one block per chapter |

Presenter mode adds thin cinema bars and a deeper vignette. It hides the small
technical readouts (model status, coordinates, CAD caption, corner notes) but
**never** hides the research wording: `SIMULATED`, `ESTIMATE`,
`CALIBRATION REQUIRED` and the like always stay on screen.

## Reading order for the panel

The opening page now shows the whole story in ten words, so the panel knows
where you are going before you start:

```
THE OCEAN → FALCON BUOY → SIGNALS → ESP32 PACKS → LoRa SENDS
→ BAY STATION → WAVE ESTIMATE → AI PREDICTION → DASHBOARD → ONE SYSTEM
```

Each chapter also gets one **IN PLAIN WORDS** line, drawn from the glossary in
`THESIS DOCUMENTATION/DOST_IDEA_PRESENTATION_PACKAGE.md`. Say that line first,
then the technical term only if the panel asks.

## Wording rules still apply

The presenter rules in the thesis package are unchanged. Keep saying
*proposed*, *prototype*, *simulated*, *to be validated*. Do not claim the AI is
trained, the readings are live ocean data, or that FALCON replaces official
warnings.

## If you want the old look back

Open `index.html` instead of `present.html`, or delete this one line from
`present.html`:

```html
<link rel="stylesheet" href="./present.css">
```

## Note on the built folder

The dev and preview servers serve `present.html` automatically — Vite copies
every `.html` file it finds into `dist/` on build. The `dist/` folder already
on disk will not contain it until you run `npm run build` again.
