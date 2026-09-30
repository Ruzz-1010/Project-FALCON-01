/* ============================================================================
   PROJECT FALCON-01 — DEEP WATER toggle  (theme-deep.js)

   One job: let the presenter flip the new look off and on by pressing D.

   It only toggles the "theme-deep" class on <body>, which is the single switch
   the whole design hangs on. No other part of the page is touched and no
   research wording is changed.

   The 3D sea and sky are lit once, when three.js first builds the scene, so
   pressing D repaints every panel and every word at once but the water keeps
   the mood it started with. Reload to re-light the 3D scene.

   No storage, no network, no tracking: the choice lasts until the page is
   reloaded, which is all a presentation needs.
   ========================================================================== */

const DEEP = 'theme-deep';
const DEEP_META = '#060d12';
const ORIGINAL_META = '#06151e';

function applyDeep(on) {
  document.body.classList.toggle(DEEP, on);
  // Both looks are dark, so the colour scheme never changes. Kept explicit so
  // a future light option cannot land here by accident.
  document.documentElement.style.colorScheme = 'dark';
  const meta = document.querySelector('meta[name="theme-color"]');
  if (meta) meta.setAttribute('content', on ? DEEP_META : ORIGINAL_META);
}

function isTyping(target) {
  if (!target) return false;
  const tag = target.tagName;
  return tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT' || target.isContentEditable;
}

document.addEventListener('keydown', (event) => {
  // Leave every other key alone: the story already uses arrows, space, Home,
  // End, Escape, + and -, and the presentation layer uses P and L.
  if (event.key !== 'd' && event.key !== 'D') return;
  if (event.ctrlKey || event.altKey || event.metaKey) return;
  if (isTyping(event.target)) return;
  event.preventDefault();
  applyDeep(!document.body.classList.contains(DEEP));
});

// Start from whatever the page was written with, so the tiny theme-color meta
// always agrees with the class in the HTML.
applyDeep(document.body.classList.contains(DEEP));

window.addEventListener('load', () => {
  const hint = document.getElementById('p-hint');
  if (!hint || hint.dataset.deepHint) return;
  hint.dataset.deepHint = '1';
  hint.textContent = `${hint.textContent} · D look`;
});
