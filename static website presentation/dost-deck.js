/* ============================================================================
   FALCON-01 — DOST DECK  (dost-deck.js)

   The interactive half of the three DOST funding chapters that the earlier build
   had no page for:

     14 ROADMAP   — the seven funded development stages, each with the limit on
                    what it is allowed to claim once it is finished.
     15 IMPACT    — intended beneficiaries, each card naming the check that has
                    to pass before an intention becomes a promise.
     16 FUNDING   — the preliminary peso breakdown, filterable, with the running
                    total computed from the rows on screen.

   Plain DOM only: no fetch, no storage, no framework, no live data. Every number
   shown comes from story.js, which took it from the DOST idea package. The
   wording of the honesty labels is thesis wording and is not softened here.
   ========================================================================== */

import {phases, funding, fundingKinds, pesoAmount, fundingRange, beneficiaries} from './story.js';

const $ = selector => document.querySelector(selector);
const esc = value => String(value).replace(/[&<>"]/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[c]));
const SPAN = '<i aria-hidden="true">→</i>';

/* ---------------------------------------------------------------------------
   14 / ROADMAP — one stage at a time, so the room reads one idea, not seven.
   -------------------------------------------------------------------------- */
function buildRoadmap() {
  const track = $('#phase-track'), detail = $('#phase-detail');
  if (!track || !detail) return;

  track.innerHTML = phases.map((phase, i) => `<button type="button" role="tab" data-phase="${i}" aria-selected="${i === 0}" aria-pressed="${i === 0}">
      <b>${phase.index}</b><span>${esc(phase.name)}</span><small>${esc(phase.span)}</small>
    </button>`).join(SPAN);

  function show(index) {
    const phase = phases[index];
    detail.innerHTML = `<div class="phase-head"><span class="phase-index">STAGE ${phase.index}</span><h3>${esc(phase.name)}</h3><span class="phase-span">${esc(phase.span)}</span></div>
      <dl class="phase-body">
        <div><dt>Output</dt><dd>${esc(phase.output)}</dd></div>
        <div><dt>What may be claimed afterwards</dt><dd>${esc(phase.claim)}</dd></div>
      </dl>`;
    track.querySelectorAll('[data-phase]').forEach((button, i) => {
      const on = i === index;
      button.setAttribute('aria-selected', String(on));
      button.setAttribute('aria-pressed', String(on));
    });
  }

  track.addEventListener('click', event => {
    const button = event.target.closest('[data-phase]');
    if (button) show(Number(button.dataset.phase));
  });
  // Left/Right walk the stages, which is how a clicker is usually held.
  track.addEventListener('keydown', event => {
    if (event.key !== 'ArrowRight' && event.key !== 'ArrowLeft') return;
    const buttons = [...track.querySelectorAll('[data-phase]')];
    const current = buttons.findIndex(b => b.getAttribute('aria-selected') === 'true');
    const next = (current + (event.key === 'ArrowRight' ? 1 : buttons.length - 1)) % buttons.length;
    event.preventDefault();
    event.stopPropagation();
    buttons[next].focus();
    show(next);
  });

  show(0);
}

/* ---------------------------------------------------------------------------
   15 / IMPACT — beneficiaries, each with the verification still owed.
   -------------------------------------------------------------------------- */
function buildImpact() {
  const grid = $('#beneficiary-grid');
  if (!grid) return;
  grid.innerHTML = beneficiaries.map(person => `<article class="beneficiary">
      <h3>${esc(person.who)}</h3>
      <p class="beneficiary-value">${esc(person.value)}</p>
      <p class="beneficiary-check"><b>STILL TO CONFIRM</b>${esc(person.verify)}</p>
    </article>`).join('');
}

/* ---------------------------------------------------------------------------
   16 / FUNDING — the table, the filter and the total that follows it.
   -------------------------------------------------------------------------- */
function buildFunding() {
  const body = $('#funding-body');
  if (!body) return;
  const total = $('#funding-total'), shown = $('#funding-shown');
  const controls = document.querySelector('.funding-controls');

  function render(kind) {
    const rows = kind === 'all' ? funding : funding.filter(row => row.kind === kind);
    body.innerHTML = rows.map(row => `<tr>
        <td>${esc(row.category)}</td>
        <td class="funding-amount">${pesoAmount(row)}</td>
        <td class="funding-kind" data-kind="${row.kind}">${esc(fundingKinds[row.kind])}</td>
      </tr>`).join('') || '<tr><td colspan="3">No category in this group.</td></tr>';
    // The headline request is always the whole plan. The line under it reports
    // what the filter is currently showing, so the two can never be confused.
    if (total) total.textContent = fundingRange();
    if (shown) {
      shown.textContent = kind === 'all'
        ? `Showing all ${funding.length} categories`
        : `Showing ${rows.length} of ${funding.length} categories · ${fundingRange(rows)}`;
    }
    controls?.querySelectorAll('[data-fund]').forEach(button => {
      const on = button.dataset.fund === kind;
      button.setAttribute('aria-pressed', String(on));
    });
  }

  controls?.addEventListener('click', event => {
    const button = event.target.closest('[data-fund]');
    if (button) render(button.dataset.fund);
  });

  render('all');
}

export function buildDostDeck() {
  buildRoadmap();
  buildImpact();
  buildFunding();
}
