# FALCON-01 — Presentation build

Two pages, one look.

| Page | Open it when | What it adds |
| --- | --- | --- |
| `index.html` | the site is being read | the story, the 3D scene |
| `present.html` | you are in front of the panel | presenter mode, chapter list, plain-language lines |

Both now carry the **Deep Water** design.

---

## How to run it

The 3D model needs a real server. Double-clicking the file will not work.

```sh
npm run dev
```

- Main site: **http://127.0.0.1:5175/**
- Presentation: **http://127.0.0.1:5175/present.html**

---

## The Deep Water design

One stylesheet, `theme-deep.css`, plus a small toggle, `theme-deep.js`.

It is not a recolour. What actually changed:

- **A left spine instead of a bottom bar.** The chapter number, the chapter
  ladder, the chapter name and the progress line all moved into a 96px column
  down the left edge. The panel's eyes always know where they are.
- **Big chapter numerals** sit as faint watermarks in the corner of each
  chapter.
- **A calmer type scale.** Smaller headings, a shorter reading measure, and
  labels that whisper instead of shout.
- **Flat plates and hairline borders** instead of glow and glass.

### Why it is dark

The 3D ocean is lit as a night scene once, at load. A dark page agrees with it.
A white page fights it, and glare is what makes a presentation tiring.

Nothing in the palette goes above about 88% brightness, so it stays readable on
a projector without burning the eyes.

### Why it does not lag

This is the important part. Three rules:

1. **No `:has()`.** The previous attempt put `:has()` on `<html>`. That makes
   the browser re-check the whole document every time any class changes — and
   `main.js` changes a class on `<body>` on every animation frame. That was the
   stutter.
2. **No `backdrop-filter`.** Blur over a live WebGL canvas re-reads the frame
   every time it moves.
3. **Borders instead of shadows.** Two small shadows in the whole file.

---

## Keyboard

| Key | What it does |
| --- | --- |
| `P` | presenter mode (only on `present.html`) |
| `L` | chapter list (only on `present.html`) |
| `D` | Deep Water look off / on |
| arrows, space, Home, End | move through the story |
| `Esc` | leave an inspection |

Add `?big=1` to the address for larger type on a weak projector.

---

## Turning it off

Remove `theme-deep` from the `<body>` tag. Every rule is scoped to that class,
so the original look comes straight back. No other file needs to change.

---

## What was not touched

- **No research wording changed.** `SIMULATED`, `ESTIMATE`, `CALIBRATION
  REQUIRED`, `MEASURED QUANTITY`, `Persistence baseline` are all exactly where
  the thesis puts them.
- **No content changed.** This is a stylesheet layer only.
- **`world.js` is byte-identical to the original.** The 3D scene is untouched.
- **The original geometry is untouched.**

---

## Test status

`npm test` reports **25 passing, 7 failing** — the same seven that were already
failing before this design work started. They concern the CAD geometry,
inspection framing and acquisition copy, not the look.

```
npm test
```
