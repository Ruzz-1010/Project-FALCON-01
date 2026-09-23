import logoUrl from '../dashboard-next/public/falcon-logo.jpg?url';
import {inspections} from './inspection.js';
import {smooth} from './home.js';
import {instrumentInfo} from './instrument.js';
import {createAcquisition} from './acquisition.js';
import {createController} from './controller.js';
import {baySteps,bayPipeline,arrivalPhase} from './bay-story.js';
import {createWaveEstimation} from './wave-estimation.js';
import {components,createLink,setLink,tickLink,waveSamples,forecastSamples,linePath} from './story.js';

// =============================================================
// FALCON-01 — 12-SECTION STRUCTURE
// All sections guarded — walang crash kung wala yung element
// =============================================================

const $ = selector => document.querySelector(selector);

// ---- Section names (12 total) ----
const SECTION_NAMES = [
  'Opening',
  'Challenge',
  'Solution',
  'Architecture',
  'Buoy',
  'How it works',
  'Bay Station',
  'Dashboard',
  'AI',
  'Validation',
  'Future',
  'Final'
];

// ---- Guarded initializations (walang crash kung wala yung element) ----
const acquisitionDock = $('#acquisition-dock');
const acquisition = acquisitionDock
  ? createAcquisition(acquisitionDock)
  : { select: () => {}, place: () => {}, draw: () => {} };

const packetConsole = $('#controller .packet-console');
if (packetConsole) {
  const controllerOutput = document.createElement('p');
  controllerOutput.className = 'controller-output';
  packetConsole.append(controllerOutput);
}

const controllerRoot = $('#controller .chip-stage') || $('#architecture .chip-stage');
const controller = controllerRoot
  ? createController(controllerRoot)
  : { draw: () => {} };

const waveEstimationRoot = $('#waves');
const waveEstimation = waveEstimationRoot
  ? createWaveEstimation(waveEstimationRoot)
  : { update: () => {} };

$('#logo').src = logoUrl;

const sections = [...document.querySelectorAll('.scene')];

const reduced = matchMedia('(prefers-reduced-motion: reduce)');
let paused = reduced.matches;
let active = 0, selected = 'pressure';
let world, elapsed = 0, last = 0, lastPacket = 0;
let predicting = false, predictionProgress = 0;
let currentTab = 'overview';
let link = createLink();
let bayInspecting = false, bayTrigger;

// ---- Bay Station panel ----
function openBay(id = 'station') {
  if (!world?.inspectBay?.(id)) {
    const btn = $('#open-bay');
    if (btn) btn.textContent = '3D unavailable — reload to inspect';
    return;
  }
  bayTrigger = document.activeElement;
  bayInspecting = true;
  document.body.classList.add('bay-inspecting');
  $('#bay-panel').hidden = false;
  const info = baySteps[id === 'validate' ? 'computer' : id];
  if (info) {
    $('#bay-title').textContent = info.title;
    $('#bay-detail').textContent = info.detail;
    $('#bay-note').textContent = info.note;
  }
  const menu = $('#bay-menu');
  const validateBtn = menu?.querySelector('[data-bay="validate"]');
  if (validateBtn) validateBtn.textContent = 'Bay Station computer';
  $('#bay-panel-menu')?.append(menu);
  $('#bay-explanation').hidden = true;
  document.querySelectorAll('[data-bay]').forEach(b =>
    b.setAttribute('aria-pressed', String(b.dataset.bay === id))
  );
}

function closeBay(restore = true) {
  if (!bayInspecting) return;
  bayInspecting = false;
  document.body.classList.remove('bay-inspecting');
  $('#bay-panel').hidden = true;
  $('#bay-menu-home')?.append($('#bay-menu'));
  world?.returnToBay?.();
  const validateBtn = $('#bay-menu [data-bay="validate"]');
  if (validateBtn) validateBtn.textContent = baySteps.validate.title;
  if (restore && bayTrigger?.isConnected) bayTrigger.focus({ preventScroll: true });
}

// ---- Populate bay menu ----
for (const id of bayPipeline) {
  const b = document.createElement('button');
  b.dataset.bay = id;
  b.textContent = baySteps[id].title;
  b.setAttribute('aria-pressed', 'false');
  b.addEventListener('click', () => openBay(id));
  $('#bay-menu')?.append(b);
}

$('#open-bay')?.addEventListener('click', () => openBay());
$('#close-bay')?.addEventListener('click', () => closeBay());
document.addEventListener('keydown', e => { if (e.key === 'Escape') closeBay(); });

const pointer = { x: 0, y: 0 };
const history = waveSamples();
const future = forecastSamples(history.at(-1));

const nav = $('#chapter-nav');

// ---- Build navigation dots ----
SECTION_NAMES.forEach((name, i) => {
  const a = document.createElement('a');
  a.href = `#${sections[i]?.id ?? ''}`;
  a.title = name;
  a.setAttribute('aria-label', `${i + 1}. ${name}`);
  nav?.append(a);
});

let inspecting = false, inspectionTrigger;

function inspectionReady() {
  if (!inspecting) return;
  $('#inspection-content').hidden = false;
  $('#inspection-travel').hidden = true;
  document.body.classList.add('inspection-ready');
  $('#inspection-title')?.focus({ preventScroll: true });
}

function endInspection(restoreFocus = true) {
  if (!inspecting) return;
  inspecting = false;
  document.body.classList.remove('inspecting', 'inspection-ready', 'instrument-inspection');
  $('#inspection-panel').hidden = true;
  acquisition.place();
  world?.returnToBuoy?.();
  if (restoreFocus && inspectionTrigger?.isConnected) inspectionTrigger.focus({ preventScroll: true });
}

$('#inspection-back')?.addEventListener('click', () => endInspection());
document.addEventListener('keydown', e => { if (e.key === 'Escape') endInspection(); });

// ---- Component selection ----
function pick(id, inspect = true) {
  acquisition.select(id);
  selected = id;
  const title = $('#component-title');
  const detail = $('#component-detail');
  if (title) title.textContent = components[id]?.label ?? '';
  if (detail) detail.textContent = components[id]?.detail ?? '';
  document.querySelectorAll('[data-component]').forEach(b =>
    b.setAttribute('aria-pressed', String(b.dataset.component === id))
  );

  if (inspect) {
    if (!world?.inspect?.(id)) {
      const ms = $('#model-state');
      if (ms) ms.textContent = 'Component guide available; wait for the original 3D model to load before inspection.';
      return;
    }
    inspectionTrigger = document.activeElement;
    inspecting = true;
    const info = active === 4 ? instrumentInfo[id] : inspections[id];
    if (!info) return;
    document.body.classList.toggle('instrument-inspection', active === 4);
    const backBtn = $('#inspection-back');
    if (backBtn) backBtn.textContent = active === 4 ? '← Return to buoy' : '← Back to buoy';
    $('#inspection-title').textContent = info.name;
    $('#inspection-function').textContent = info.function;
    $('#inspection-data').replaceChildren(
      ...info.data.map(text => { const li = document.createElement('li'); li.textContent = text; return li; })
    );
    $('#inspection-flow').replaceChildren(
      ...info.flow.map(text => { const span = document.createElement('span'); span.textContent = text; return span; })
    );
    $('#inspection-status').textContent = info.status;
    $('#inspection-note').textContent = info.note;
    acquisition.place(active === 5 ? $('#inspection-content') : null);
    $('#inspection-panel').hidden = false;
    $('#inspection-content').hidden = true;
    $('#inspection-travel').hidden = false;
    document.body.classList.add('inspecting');
    document.body.classList.remove('inspection-ready');
  }
}

// ---- Populate component pickers ----
for (const [id, c] of Object.entries(components)) {
  for (const container of [$('#reveal-picks'), $('#sensor-menu')]) {
    if (!container) continue;
    const b = document.createElement('button');
    b.textContent = c.label;
    b.dataset.component = id;
    b.dataset.index = String(Object.keys(components).indexOf(id) + 1).padStart(2, '0');
    b.setAttribute('aria-pressed', String(id === selected));
    b.addEventListener('click', () => pick(id));
    container.append(b);
  }
}
pick(selected, false);

// ---- Hover / focus ----
document.addEventListener('pointerover', e => {
  const node = e.target.closest('[data-component]');
  if (node) world?.hover?.(node.dataset.component);
});
document.addEventListener('pointerout', e => {
  if (e.target.closest('[data-component]')) world?.hover?.(null);
});
document.addEventListener('focusin', e => {
  const node = e.target.closest('[data-component]');
  if (node) world?.hover?.(node.dataset.component);
});
document.addEventListener('focusout', e => {
  if (e.target.closest('[data-component]')) world?.hover?.(null);
});

$('#cad-note')?.addEventListener('click', () => {
  const expanded = $('#cad-note').getAttribute('aria-expanded') === 'true';
  $('#cad-note').setAttribute('aria-expanded', String(!expanded));
  $('#cad-detail').hidden = expanded;
});

// ---- Motion toggle ----
function applyMotion() {
  document.body.classList.toggle('motion-paused', paused);
  const m = $('#motion');
  if (m) {
    m.textContent = paused ? 'Play motion' : 'Pause motion';
    m.setAttribute('aria-pressed', String(paused));
  }
}
$('#motion')?.addEventListener('click', () => { paused = !paused; applyMotion(); });
reduced.addEventListener('change', e => { paused = e.matches; applyMotion(); });
applyMotion();

$('#fullscreen')?.addEventListener('click', async () => {
  try {
    if (document.fullscreenElement) await document.exitFullscreen();
    else await document.documentElement.requestFullscreen();
  } catch {
    const ms = $('#model-state');
    if (ms) ms.textContent = 'Fullscreen unavailable in this browser.';
  }
});
document.addEventListener('fullscreenchange', () => {
  $('#fullscreen')?.setAttribute('aria-label', document.fullscreenElement ? 'Exit fullscreen' : 'Enter fullscreen');
});

window.addEventListener('pointermove', e => {
  pointer.x = e.clientX / innerWidth * 2 - 1;
  pointer.y = 1 - e.clientY / innerHeight * 2;
}, { passive: true });

// ---- Radio link ----
function updateLink() {
  const route = $('#radio-route');
  if (route) route.classList.toggle('offline', !link.online);
  const interrupt = $('#interrupt');
  if (interrupt) interrupt.textContent = link.online ? 'Interrupt LoRa' : 'Restore LoRa';
  const label = $('#link-label');
  if (label) label.textContent = link.online
    ? (link.buffer.length ? 'LoRa / retransmitting' : 'LoRa / transmitting')
    : 'LoRa / interrupted';
  const status = $('#link-status');
  if (status) status.textContent = link.online
    ? (link.buffer.length ? 'Replaying original timestamps' : 'Simulated link available')
    : 'Buoy still sensing · shore data stale';
  const queued = $('#queued');
  if (queued) queued.textContent = String(link.buffer.length).padStart(2, '0');
  const received = $('#received');
  if (received) received.textContent = String(link.received.length).padStart(2, '0');
  const bufferPackets = $('#buffer-packets');
  if (bufferPackets) {
    bufferPackets.replaceChildren(
      ...link.buffer.slice(-10).map(p => {
        const i = document.createElement('i');
        i.textContent = String(p.id).padStart(3, '0');
        i.title = `Original sample: ${p.timestamp}`;
        return i;
      })
    );
  }
  const note = $('#recovery-note');
  if (note) {
    note.textContent =
      link.phase === 'buffering' ? 'Sample times stay with queued packets. This is a simulated buffer—not proof of field recovery.' :
      link.phase === 'retransmitting' ? 'Backlog replay → duplicate prevention → chronological storage. Original sample times preserved.' :
      'Hardware, legal band and site coverage pending. No range guarantee.';
  }
}

$('#interrupt')?.addEventListener('click', () => {
  link = setLink(link, !link.online);
  link = tickLink(link, new Date().toISOString());
  updateLink();
  renderDashboard();
  if (!link.online) {
    predicting = false;
    predictionProgress = 0;
    const reveal = $('#future-reveal');
    if (reveal) reveal.setAttribute('width', '0');
    const ps = $('#prediction-status');
    if (ps) ps.textContent = 'UNAVAILABLE: shore input is stale while LoRa is interrupted.';
  }
});
updateLink();

// ---- Prediction chart ----
const historyTrace = $('#history-trace');
const futureTrace = $('#future-trace');
const baselineTrace = $('#baseline-trace');
if (historyTrace) historyTrace.setAttribute('d', linePath(history, 45, 585, 190, 140));
if (futureTrace) futureTrace.setAttribute('d', linePath(future, 630, 340, 190, 140));
if (baselineTrace) baselineTrace.setAttribute('d', linePath([history.at(-1), history.at(-1)], 630, 340, 190, 140));

$('#predict')?.addEventListener('click', () => {
  if (!link.online) {
    const ps = $('#prediction-status');
    if (ps) ps.textContent = 'UNAVAILABLE: restore LoRa before running a new prediction.';
    return;
  }
  predicting = true;
  predictionProgress = paused ? 1 : 0;
  const ps = $('#prediction-status');
  if (ps) ps.textContent = 'SIMULATED: extending a candidate trace against persistence.';
  if (paused) drawPrediction(0);
});

function drawPrediction(dt) {
  if (!predicting) return;
  predictionProgress = Math.min(1, predictionProgress + dt * .32);
  const reveal = $('#future-reveal');
  if (reveal) reveal.setAttribute('width', String(predictionProgress * 350));
  if (predictionProgress === 1) {
    predicting = false;
    const ps = $('#prediction-status');
    if (ps) ps.textContent = 'Illustrative AI trace vs. persistence. No accuracy claim.';
  }
}

// ---- Dashboard ----
function overviewMarkup() {
  const stale = !link.online;
  return `<div class="demo-overview">
    <div>
      <div class="demo-readings">
        <span>Estimated wave height<strong>${stale ? '—' : history.at(-1).toFixed(2) + ' <small>m</small>'}</strong></span>
        <span>AI · next 10 min<strong>${stale ? '—' : future.at(-1).toFixed(2) + ' <small>m</small>'}</strong></span>
      </div>
      <svg class="demo-chart" viewBox="0 0 700 170" role="img" aria-label="Simulated estimated wave height and illustrative AI trace">
        <path class="chart-grid" d="M0 30H700 M0 85H700 M0 140H700"/>
        ${stale
          ? '<text x="210" y="85">STALE · waiting for packets</text>'
          : `<path class="estimated-trace" d="${linePath(history, 0, 480, 150, 150)}"/>
             <path class="future-trace" d="${linePath(future, 480, 210, 150, 150)}"/>`}
      </svg>
    </div>
    <dl class="demo-summary">
      <div><dt>Station</dt><dd>${stale ? 'STALE' : 'Simulation'}</dd></div>
      <div><dt>LoRa</dt><dd>${stale ? 'Offline' : 'Receiving'}</dd></div>
      <div><dt>Wind</dt><dd>${stale ? '—' : '11 km/h NE'}</dd></div>
      <div><dt>Battery</dt><dd>${stale ? '—' : '78% demo'}</dd></div>
      <div><dt>Security</dt><dd>${stale ? 'Unknown' : 'Secure demo'}</dd></div>
    </dl>
  </div>`;
}

function renderDashboard() {
  const host = $('#dashboard-content');
  if (!host) return;
  if (currentTab === 'overview') host.innerHTML = overviewMarkup();
  if (currentTab === 'motion') host.innerHTML = `
    <div class="demo-motion">
      <svg viewBox="0 0 160 200" aria-label="Illustrative heave indicator" role="img">
        <path d="M10 125Q40 113 80 125T150 125" fill="none" stroke="#448591"/>
        <g class="motion-outline">
          <path d="M80 40V100M70 50L80 40 90 50M70 90L80 100 90 90" fill="none" stroke="#357889" stroke-width="2"/>
          <circle cx="80" cy="125" r="9" fill="#397d8a"/>
        </g>
        <text x="80" y="175" text-anchor="middle">HEAVE / DEMO</text>
      </svg>
      <p><strong>Buoy Motion</strong>Pressure-informed visualization—not measured roll or pitch.<br>The original CAD is the physical reference.<br><a href="#buoy">Return to original buoy ↗</a></p>
    </div>`;
  if (currentTab === 'sensors') host.innerHTML = `
    <table class="sensor-table">
      <thead><tr><th>Observation</th><th>Role</th><th>Status</th></tr></thead>
      <tbody>
        <tr><td>Pressure</td><td>Wave processing input</td><td>${link.online ? 'Calibration pending' : 'Stale'}</td></tr>
        <tr><td>Wind</td><td>Environmental context</td><td>Simulated</td></tr>
        <tr><td>GPS</td><td>Supporting telemetry</td><td>Simulated</td></tr>
        <tr><td>Battery / solar</td><td>Energy monitoring</td><td>Simulated</td></tr>
        <tr><td>Enclosure</td><td>Health / security</td><td>Simulated</td></tr>
      </tbody>
    </table>`;
  if (currentTab === 'logs') host.innerHTML = `
    <div class="demo-log"><time>SIM</time><span>${link.online ? 'Shore link available.' : 'LoRa interrupted. Buoy packets buffered.'}</span></div>
    <div class="demo-log"><time>SIM</time><span>${link.buffer.length} packets queued · ${link.received.length} accepted without duplicate IDs.</span></div>
    <div class="demo-log"><time>NOTE</time><span>Calibration and controlled deployment validation remain pending.</span></div>
    <p class="demo-note">Presentation events only. No hardware, alarm or database connection.</p>`;
}

document.querySelectorAll('[data-tab]').forEach(b => b.addEventListener('click', () => {
  currentTab = b.dataset.tab;
  document.querySelectorAll('[data-tab]').forEach(el =>
    el.setAttribute('aria-pressed', String(el === b))
  );
  renderDashboard();
}));
renderDashboard();

// ---- Home orbit ----
let offsets = [];
let homeJourney = null;
const home = $('#ocean');
let homeOrbitActive = false;

function setHomeOrbit(enabled) {
  if (enabled && !world?.setHomeOrbit?.(true)) {
    const s = $('#home-orbit-status');
    if (s) s.textContent = 'The original CAD is still loading or 3D is unavailable.';
    return;
  }
  if (!enabled) world?.setHomeOrbit?.(false);
  homeOrbitActive = enabled;
  homeJourney = null;
  document.body.classList.toggle('home-orbit', enabled);
  const ex = $('#explore-home');
  const rs = $('#reset-home');
  const hh = $('#home-orbit-help');
  const hs = $('#home-orbit-status');
  if (ex) { ex.hidden = enabled; ex.setAttribute('aria-pressed', String(enabled)); }
  if (rs) rs.hidden = !enabled;
  if (hh) hh.hidden = !enabled;
  if (hs) hs.textContent = '';
  if (enabled) rs?.focus({ preventScroll: true });
}

$('#explore-home')?.addEventListener('click', () => setHomeOrbit(true));
$('#reset-home')?.addEventListener('click', () => {
  setHomeOrbit(false);
  $('#explore-home')?.focus({ preventScroll: true });
});

window.addEventListener('keydown', e => {
  if (!homeOrbitActive) return;
  if (e.key === 'Escape') {
    setHomeOrbit(false);
    $('#explore-home')?.focus({ preventScroll: true });
    return;
  }
  const steps = {
    ArrowLeft: [-20, 0], ArrowRight: [20, 0],
    ArrowUp: [0, -20], ArrowDown: [0, 20],
    '+': [0, 0, -80], '-': [0, 0, 80]
  };
  if (steps[e.key]) { e.preventDefault(); world?.moveHomeOrbit?.(...steps[e.key]); }
});

const cancelHomeJourney = () => { homeJourney = null; };
for (const event of ['wheel', 'touchstart', 'pointerdown'])
  window.addEventListener(event, cancelHomeJourney, { passive: true });
window.addEventListener('keydown', e => {
  if (['Escape', 'ArrowDown', 'ArrowUp', 'PageDown', 'PageUp', 'Home', 'End', ' '].includes(e.key))
    cancelHomeJourney();
});

$('#begin-journey')?.addEventListener('click', e => {
  if (homeOrbitActive) setHomeOrbit(false);
  e.preventDefault();
  const target = $('#challenge') ?? $('#buoy');
  if (!target) return;
  const to = target.offsetTop - Math.min(80, innerHeight * .15);
  if (paused) { window.scrollTo({ top: to, behavior: 'instant' }); return; }
  homeJourney = { from: scrollY, to, elapsed: 0 };
});

function measure() { offsets = sections.map(s => s.offsetTop); }
measure();
window.addEventListener('resize', measure);
document.fonts.ready.then(measure);
const layoutObserver = new ResizeObserver(measure);
sections.forEach(s => layoutObserver.observe(s));

function scrollState() {
  const y = scrollY + innerHeight * .18;
  let chapter = 0;
  for (let i = 0; i < offsets.length; i++) if (y >= offsets[i]) chapter = i;
  const span = (offsets[chapter + 1] ?? offsets[chapter] + innerHeight) - offsets[chapter];
  const fraction = Math.max(0, Math.min(1, (y - offsets[chapter]) / span));
  return { chapter, progress: Math.min(sections.length - 1, chapter + fraction) };
}

function setChapter(chapter) {
  active = chapter;
  document.body.dataset.experience = String(chapter);
  sections.forEach((s, i) => s.classList.toggle('is-active', i === chapter));
  [...(nav?.children ?? [])].forEach((a, i) => {
    if (i === chapter) a.setAttribute('aria-current', 'step');
    else a.removeAttribute('aria-current');
  });
  const cn = $('#chapter-number');
  if (cn) cn.textContent = `${String(chapter + 1).padStart(2, '0')} / ${sections.length}`;
  const cname = $('#chapter-name');
  if (cname) cname.textContent = SECTION_NAMES[chapter] ?? '';
  const ct = $('#coordinate-top');
  if (ct) ct.textContent = chapter < 5 ? 'OFFSHORE / OBSERVATION NODE'
    : chapter < 9 ? 'ON SHORE / BAY STATION'
    : 'BUOY TO SHORE / CONNECTED';
}
setChapter(0);

let raf;
function frame(now) {
  raf = requestAnimationFrame(frame);
  if (now - last < 33) return;
  const dt = Math.min(.06, (now - last) / 1000);
  last = now;
  if (document.hidden) return;

  if (homeJourney) {
    if (paused) homeJourney = null;
    else {
      homeJourney.elapsed += dt;
      const t = Math.min(1, homeJourney.elapsed / 5.2);
      window.scrollTo({ top: homeJourney.from + (homeJourney.to - homeJourney.from) * smooth(t), behavior: 'instant' });
      if (t === 1) {
        homeJourney = null;
        window.history.replaceState(null, '', '#challenge');
      }
    }
  }

  const moving = !paused;
  if (moving) elapsed += dt;

  const state = scrollState();
  if (inspecting && state.chapter !== active) endInspection(false);
  if (state.chapter !== active) setChapter(state.chapter);
  if (homeOrbitActive && state.chapter !== 0) setHomeOrbit(false);
  if (bayInspecting && state.chapter !== 6) closeBay(false);

  const homeProgress = Math.max(0, Math.min(1, scrollY / Math.max(1, offsets[1] - innerHeight * .18)));
  home?.style.setProperty('--home-progress', String(homeProgress));
  home?.classList.toggle('home-departed', homeProgress > .52);
  const hsl = $('#home-shot-label');
  if (hsl) hsl.textContent = homeProgress < .25 ? '01 / THE OCEAN'
    : homeProgress < .55 ? '02 / DISCOVERY'
    : homeProgress < .82 ? '03 / APPROACH'
    : '04 / LISTEN';

  const jp = $('#journey-progress');
  if (jp) jp.style.width = `${Math.min(100, scrollY / Math.max(1, document.documentElement.scrollHeight - innerHeight) * 100)}%`;

  world?.update({
    ...state, time: elapsed, dt, moving, pointer, selected,
    linkOnline: link.online, homeProgress
  });

  // Active-section-specific updates (may guards)
  if (active === 5 && moving && acquisition.draw) acquisition.draw(elapsed);
  if (active === 4 && controller.draw) controller.draw(elapsed);
  if (active === 6) {
    const s = arrivalPhase(elapsed, link.online);
    document.querySelectorAll('[data-bay]').forEach((b, i) => b.classList.toggle('receiving-stage', i === s.stage));
  }
  if (active === 9 && waveEstimation.update) waveEstimation.update(elapsed, dt, state.progress - 9, moving);
  if (active === 8 && moving) drawPrediction(dt);
  if (moving && active >= 4 && active <= 6 && elapsed - lastPacket > 1.5) {
    lastPacket = elapsed;
    link = tickLink(link, new Date().toISOString());
    updateLink();
  }
}
raf = requestAnimationFrame(frame);

// ---- Lazy load 3D world ----
import('./world.js').then(async ({ createWorld }) => {
  world = await createWorld($('#world'), {
    onPick: pick,
    onInspectionReady: inspectionReady,
    onBayPick: openBay,
    onBayReady: () => {
      if (bayInspecting) {
        $('#bay-explanation').hidden = false;
        $('#bay-title')?.focus({ preventScroll: true });
      }
    },
    onStatus: text => { const ms = $('#model-state'); if (ms) ms.textContent = text; }
  });
}).catch(err => {
  console.error('World load failed:', err);
  const ms = $('#model-state');
  if (ms) ms.textContent = '3D unavailable · reload or continue the accessible diagrams';
  document.body.classList.add('webgl-unavailable');
});

window.addEventListener('pagehide', e => {
  if (!e.persisted) {
    cancelAnimationFrame(raf);
    world?.dispose();
    layoutObserver.disconnect();
  }
});