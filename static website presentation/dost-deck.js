/* ============================================================================
   FALCON-01 — DOST DECK  (dost-deck.js)

   The interactive half of the DOST wrap-up chapters:

     ROADMAP & TEAM — five bootcamp gates, each with the limit on what it is
                      allowed to claim, plus the crew and mentors.
     IMPACT & FUNDING — intended beneficiaries with the check still owed, and
                      the preliminary peso breakdown with running total.

   Plain DOM only: no fetch, no storage, no framework, no live data. Every
   number shown comes from story.js. Thesis honesty wording is not softened.
   ========================================================================== */

import {phases, execution, funding, fundingKinds, pesoAmount, fundingRange, beneficiaries} from './story.js';

const $ = selector => document.querySelector(selector);
const esc = value => String(value).replace(/[&<>"]/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[c]));
const SPAN = '<i aria-hidden="true">→</i>';

/* ---------------------------------------------------------------------------
   12 / ROADMAP & TEAM — one gate at a time, so the room reads one idea, not five.
   -------------------------------------------------------------------------- */
function buildRoadmap() {
  const track = $('#phase-track'), detail = $('#phase-detail');
  if (!track || !detail) return;

  track.innerHTML = phases.map((phase, i) => `<button type="button" role="tab" data-phase="${i}" aria-selected="${i === 0}" aria-pressed="${i === 0}">
      <b>${phase.index}</b><span>${esc(phase.name)}</span><small>${esc(phase.span)}</small>
    </button>`).join(SPAN);

  function show(index) {
    const phase = phases[index];
    detail.innerHTML = `<div class="phase-head"><span class="phase-index">GATE ${phase.index} · ${esc(phase.span)}</span><h3>${esc(phase.name)}</h3></div>
      <dl class="phase-body">
        <div><dt>Output</dt><dd>${esc(phase.output)}</dd></div>
        <div><dt>What may be claimed afterwards</dt><dd>${esc(phase.claim)}</dd></div>
      </dl>
      <p class="micro">Bootcamp: ${esc(execution.model)} — ${esc(execution.weekly)}.</p>`;
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
   13 / IMPACT & FUNDING — beneficiaries, each with the verification still owed,
   then the peso table, its filter and the total that follows it.
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
   The funding table shares the Impact chapter's scene, so it needs no header
   of its own.
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

/* ---------------------------------------------------------------------------
   TEAM — bootcamp crew + mentors. Rendered into #team-grid on the Roadmap
   chapter so the panel sees who owns each gate.
   -------------------------------------------------------------------------- */
function buildTeam() {
  const grid = $('#team-grid');
  if (!grid || !execution) return;
  grid.innerHTML =
    execution.team.map(m => `<article class="teammate"><h3>${esc(m.name)}</h3><p>${esc(m.role)}</p></article>`).join('') +
    execution.mentors.map(m => `<article class="teammate mentor"><h3>${esc(m.name)}</h3><p>${esc(m.role)}</p></article>`).join('') +
    `<p class="micro team-model">${esc(execution.model)} — ${esc(execution.weekly)}.</p>`;
}

export function buildDostDeck() {
  buildRoadmap();
  buildImpact();
  buildFunding();
  buildTeam();
}
