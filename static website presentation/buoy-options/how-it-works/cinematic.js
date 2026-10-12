// FALCON Lite — "How it works" animated walkthrough.
//
// A timeline-driven cinematic of the Option A compact can buoy. The point of
// the piece is one idea: the buoy samples locally, summarizes each two-minute window, and uploads one compact packet to the cloud. The animation is written for panel review, so it emphasizes what is measured, what is estimated, and what still needs validation.
//
// PROPOSED ONLY. Timing, thresholds and the daily counts are DESIGN PARAMETERS
// from the revised proposal, not measurements from a deployed buoy. The buoy is
// not deployed. Geometry comes from the shared model so it matches Option A
// exactly; the V2 GLB used by world.js is untouched.
import * as THREE from 'three';
import {createCanBuoy} from '../buoy-can-model.js';
import {ISLANDS} from '../palawan-geo.js';

// ---------------------------------------------------------------- renderer
const stage = document.getElementById('stage');
const renderer = new THREE.WebGLRenderer({antialias:true});
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
stage.prepend(renderer.domElement);

const scene = new THREE.Scene();
scene.background = new THREE.Color('#08141b');
scene.fog = new THREE.FogExp2('#0b222e', 0.022);
const camera = new THREE.PerspectiveCamera(42, 1, 0.05, 220);

scene.add(new THREE.HemisphereLight('#cfe6ef', '#1c2f36', 2.3));
const sun = new THREE.DirectionalLight('#f6e2b6', 3.0);
sun.position.set(-4, 7, 3); sun.castShadow = true;
sun.shadow.mapSize.set(1024, 1024);
scene.add(sun);
const rim = new THREE.DirectionalLight('#8dc4e3', 1.5);
rim.position.set(4, 2, -5); scene.add(rim);
// A low fill from below so the mooring and keel stay readable in beat 2.
const under = new THREE.PointLight('#7fc4dd', 2.2, 6, 2);
under.position.set(0.4, -1.1, 0.8); scene.add(under);

const sea = new THREE.Mesh(
  new THREE.PlaneGeometry(120, 120, 90, 90),
  new THREE.MeshStandardMaterial({color:'#0e3a47', roughness:.85, metalness:.05, transparent:true, opacity:.92})
);
sea.rotation.x = -Math.PI/2; sea.receiveShadow = true;
scene.add(sea);

const model = createCanBuoy();
const buoy = model.group;
scene.add(buoy);
const D = model.dimensions;

// ---------------------------------------------------------------- channel highlights
// Each channel is a marker that billboards to the camera, a pulsing ring, and
// a DOM callout pinned to the projected screen position.
const RING_GEO = new THREE.RingGeometry(0.052, 0.062, 40);
const DOT_GEO = new THREE.CircleGeometry(0.03, 28);
const CHANNELS = {
  pressure: {label:'Water pressure', sub:'Stilling tube captures pressure changes for wave estimation', pos:[D.stillingTube.x, 0.02, D.stillingTube.z]},
  wind:     {label:'Wind speed + direction', sub:'Cup rotor and vane explain the sea condition', pos:[0, D.mastTopY + 0.12, 0]},
  gps:      {label:'GPS position + security', sub:'Location, timestamp and drift/geofence evidence', pos:[D.gpsPos.x, D.gpsPos.y, D.gpsPos.z]},
  power:    {label:'Battery + solar health', sub:'12.8 V LiFePO4 battery and 18 W solar plan need validation', pos:[0, D.housingCentreY + 0.02, D.solarFaceZ]},
};
for (const c of Object.values(CHANNELS)){
  c.pos = new THREE.Vector3(...c.pos);
  c.ring = new THREE.Mesh(RING_GEO, new THREE.MeshBasicMaterial({color:'#d8a94e', transparent:true, opacity:0, depthTest:false}));
  c.ring.renderOrder = 20;
  c.dot = new THREE.Mesh(DOT_GEO, new THREE.MeshBasicMaterial({color:'#e8c35a', transparent:true, opacity:0, depthTest:false}));
  c.dot.renderOrder = 21;
  c.ring.position.copy(c.pos); c.dot.position.copy(c.pos);
  scene.add(c.ring, c.dot);
}

// Radio pulse for beat 5: a bright bead climbing to the antenna tip.
const radio = new THREE.Mesh(
  new THREE.SphereGeometry(0.022, 14, 10),
  new THREE.MeshBasicMaterial({color:'#9fd8e8', transparent:true, opacity:0})
);
radio.renderOrder = 22; scene.add(radio);
const ANT_TOP = D.ANT_X, ANT_TOP_Z = D.ANT_Z, ANT_TOP_Y = D.antennaTipY;

// Ring bursts at the antenna when a packet leaves.
const BURSTS = [];
for (let i = 0; i < 3; i++){
  const m = new THREE.Mesh(new THREE.RingGeometry(0.03, 0.042, 32),
    new THREE.MeshBasicMaterial({color:'#9fd8e8', transparent:true, opacity:0, depthTest:false}));
  m.renderOrder = 21; m.position.set(ANT_TOP, ANT_TOP_Y, ANT_TOP_Z);
  scene.add(m); BURSTS.push(m);
}

// Threshold flare for beat 4: a ring around the waterline.
const flare = new THREE.Mesh(new THREE.RingGeometry(0.44, 0.50, 48),
  new THREE.MeshBasicMaterial({color:'#e87a7a', transparent:true, opacity:0, side:THREE.DoubleSide, depthTest:false}));
flare.rotation.x = -Math.PI/2; flare.position.y = 0.002; flare.renderOrder = 19; scene.add(flare);

// ---------------------------------------------------------------- cinematic state
// Everything the beats drive lives here so beats stay pure timeline entries.
const S = {
  seaAmp: 0.012, seaSurge: 0, seaSpeed: 1,
  bobAmp: 0.022, heel: 0.006,
  highlight: null,        // channel key currently lit
  highlightAmount: 0,
  radioT: -1,             // 0..1 progress of the transmit bead, -1 = idle
  burstT: -1,
  flareT: -1,
  counterT: -1,
  showCounters: false, showMap: false,
  sendPulse: 0,           // LED "transmitting" glow
  windRps: 0.018,
};

// ---------------------------------------------------------------- beats
// cam.from/cam.to are blended with an eased 0..1 across the beat, then the
// camera chases that with an exponential ease so cuts never snap.
const easeInOut = t => t < .5 ? 4*t*t*t : 1 - Math.pow(-2*t + 2, 3)/2;
const BEATS = [
  {
    id:'sea', name:'1 · SEA CONDITION', dur:7,
    cam:{from:{yaw:0.30, pitch:0.02, dist:5.2, focus:[0,-0.06,0]},
         to:{yaw:0.95, pitch:0.06, dist:4.0, focus:[0,-0.02,0]}},
    cap:'The buoy is placed where local wave and wind data are needed.',
    note:'This is an operating concept for panel validation, not field data.',
    tick:'standby',
  },
  {
    id:'buoy', name:'2 · COMPACT BUOY', dur:9,
    cam:{from:{yaw:0.95, pitch:0.02, dist:3.4, focus:[0,0.02,0]},
         to:{yaw:2.15, pitch:-0.16, dist:2.5, focus:[0.18,-0.30,0.22]}},
    cap:'Option A uses one compact body, a short mast, side pressure tube, solar faces and a visible mooring line.',
    note:'The body is illustrative. Final build still needs flotation, leak and anchor validation.',
    tick:'standby',
  },
  {
    id:'sense', name:'3 · SENSOR SAMPLING', dur:13,
    cam:{from:{yaw:2.15, pitch:0.06, dist:2.1, focus:[0.20,0.18,0.18]},
         to:{yaw:-1.15, pitch:0.20, dist:1.5, focus:[0, D.housingCentreY + 0.04, 0]}},
    cap:'The ESP32 reads pressure, wind, GPS and power locally.',
    note:'It does not upload every raw sample. It prepares clean records first.',
    tick:'sample',
    sequence:[
      {key:'pressure', at:0.06, to:0.31},
      {key:'wind',     at:0.31, to:0.55},
      {key:'gps',      at:0.55, to:0.77},
      {key:'power',    at:0.77, to:1.00},
    ],
  },
  {
    id:'window', name:'4 · TWO-MINUTE SUMMARY', dur:9,
    cam:{from:{yaw:-1.15, pitch:0.16, dist:1.7, focus:[0, D.housingCentreY, 0]},
         to:{yaw:0.75, pitch:0.08, dist:2.35, focus:[0,0.18,0]}},
    cap:'Every two minutes, the ESP32 compresses the local samples into one useful summary.',
    note:'The packet keeps average, minimum, maximum, peak and status flags, so a short high wave is still recorded.',
    tick:'window',
  },
  {
    id:'transmit', name:'5 · CLOUD PACKET', dur:8,
    cam:{from:{yaw:0.75, pitch:0.06, dist:2.2, focus:[0.10,0.35,0.10]},
         to:{yaw:2.60, pitch:0.16, dist:2.9, focus:[0.05,0.55,0.05]}},
    cap:'One compact Wi-Fi/LTE packet goes to the cloud.',
    note:'This is why the system can avoid constant network use while still preserving important events.',
    tick:'send',
  },
  {
    id:'dashboard', name:'6 · DASHBOARD UPDATE', dur:8,
    cam:{from:{yaw:2.60, pitch:0.10, dist:2.9, focus:[0.05,0.40,0.05]},
         to:{yaw:4.30, pitch:0.16, dist:3.5, focus:[0,0.24,0]}},
    cap:'The cloud stores the packet and updates the dashboard.',
    note:'Panel viewers see estimated wave state, wind, GPS position and power health with clear simulated/validated labels.',
    tick:'cloud',
  },
  {
    id:'power', name:'7 · POWER VALIDATION', dur:8,
    cam:{from:{yaw:4.30, pitch:0.14, dist:3.5, focus:[0,0.24,0]},
         to:{yaw:5.20, pitch:0.10, dist:4.2, focus:[0,0.16,0]}},
    cap:'Power plan: 12.8 V 10 Ah LiFePO4 battery + 6 × 3 W solar panels.',
    note:'This is a realistic validation baseline, but it still needs a 24-hour current log and solar recovery test.',
    tick:'power',
  },
];
const TOTAL = BEATS.reduce((a, b) => a + b.dur, 0);
// Beat start offsets, and the label used on the transport bar.
const STARTS = [];
BEATS.reduce((a, b) => { STARTS.push(a); return a + b.dur; }, 0);

function fmt(s){
  const m = Math.floor(s / 60), r = Math.floor(s % 60);
  return `${m}:${r < 10 ? '0' : ''}${r}`;
}
document.getElementById('t-end').textContent = fmt(TOTAL);

// ---------------------------------------------------------------- camera state
// Exponential chase, so the camera plays the same on 60 Hz and 120 Hz.
const camState = {yaw:0.30, pitch:0.02, dist:5.2, focus:new THREE.Vector3(0,-0.06,0)};
let camTarget = {...camState, focus:new THREE.Vector3(0,-0.06,0)};
const CHASE = 3.4;
function setCam(c){
  camTarget.yaw = c.yaw; camTarget.pitch = c.pitch; camTarget.dist = c.dist;
  camTarget.focus.set(...c.focus);
}
function blendCam(a, b, k){
  setCam({
    yaw: a.yaw + (b.yaw - a.yaw) * k,
    pitch: a.pitch + (b.pitch - a.pitch) * k,
    dist: a.dist + (b.dist - a.dist) * k,
    focus: [0,1,2].map(i => a.focus[i] + (b.focus[i] - a.focus[i]) * k),
  });
}

// ---------------------------------------------------------------- timeline
let time = 0, playing = false, beat = 0, freeCam = false, ccOn = true;
const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;

function beatAt(t){
  let i = 0;
  while (i < BEATS.length - 1 && t >= STARTS[i] + BEATS[i].dur) i++;
  return i;
}

function applyBeatState(bi, local01){
  const b = BEATS[bi];
  const k = easeInOut(Math.min(1, local01));
  blendCam(b.cam.from, b.cam.to, k);

  // Reset per-beat flags.
  S.showCounters = false; S.showMap = false;
  S.radioT = -1; S.burstT = -1; S.flareT = -1; S.counterT = -1;
  S.seaSurge = 0; S.heel = 0.006; S.sendPulse = 0;
  S.highlight = null;

  // Sea and hull motion per beat.
  switch (b.id){
    case 'sea':
      S.seaAmp = 0.008 + k * 0.030;
      S.bobAmp = 0.012 + k * 0.016;
      break;
    case 'buoy':
      S.seaAmp = 0.034; S.bobAmp = 0.026;
      break;
    case 'sense':
      S.seaAmp = 0.030; S.bobAmp = 0.022;
      if (b.sequence){
        for (const step of b.sequence){
          if (local01 >= step.at && local01 < step.to){ S.highlight = step.key; break; }
        }
      }
      break;
    case 'window': {
      S.seaAmp = 0.034;
      S.bobAmp = 0.026;
      // Surge peaks about 60% through the beat, then the flare fires.
      const s = local01 < 0.62 ? local01 / 0.62 : 1 - (local01 - 0.62) / 0.38;
      S.seaSurge = Math.max(0, s) * 0.075;
      S.heel = 0.006 + Math.max(0, s) * 0.026;
      if (local01 >= 0.55) S.flareT = (local01 - 0.55) / 0.45;
      break;
    }
    case 'transmit':
      S.seaAmp = 0.038; S.bobAmp = 0.030;
      if (local01 >= 0.30 && local01 < 0.72) S.radioT = (local01 - 0.30) / 0.42;
      if (local01 >= 0.68 && local01 < 1.0) S.burstT = (local01 - 0.68) / 0.32;
      if (local01 >= 0.24 && local01 < 0.62) S.sendPulse = 1 - (local01 - 0.24) / 0.38;
      break;
    case 'dashboard':
      S.seaAmp = 0.030; S.bobAmp = 0.022;
      S.showMap = true;
      break;
    case 'power':
      S.seaAmp = 0.026; S.bobAmp = 0.020;
      S.showCounters = true;
      if (local01 >= 0.12) S.counterT = Math.min(1, (local01 - 0.12) / 0.72);
      break;
  }
}

function advance(dt){
  if (playing && !freeCam){
    time += dt;
    if (time >= TOTAL){ time = 0; }
  }
  const bi = beatAt(time);
  if (bi !== beat){ beat = bi; syncBeatUI(); }
  const b = BEATS[bi];
  const local01 = Math.min(1, Math.max(0, (time - STARTS[bi]) / b.dur));
  if (!freeCam) applyBeatState(bi, local01);
}

// ---------------------------------------------------------------- overlay wiring
const capEl = document.getElementById('cap');
const capNote = document.getElementById('cap-note');
const clockFace = document.getElementById('clock-face');
const clockSub = document.getElementById('clock-sub');
const beatName = document.getElementById('beat-name');
const barFill = document.getElementById('bar-fill');
const barHead = document.getElementById('bar-head');
const bar = document.getElementById('bar');
const tNow = document.getElementById('t-now');
const btnPlay = document.getElementById('btn-play');
const btnReplay = document.getElementById('btn-replay');
const btnCC = document.getElementById('btn-cc');
const btnOrbit = document.getElementById('btn-orbit');
const callout = document.getElementById('callout');
const calloutT = document.getElementById('callout-t');
const calloutS = document.getElementById('callout-s');
const counters = document.getElementById('counters');
const cSense = document.getElementById('c-sense');
const cSend = document.getElementById('c-send');
const cRatio = document.getElementById('c-ratio');
const minimap = document.getElementById('minimap');
const roLink = document.getElementById('ro-link');
const roWind = document.getElementById('ro-wind');
const roWave = document.getElementById('ro-wave');
const roBatt = document.getElementById('ro-batt');
const workflowSteps = [...document.querySelectorAll('[data-wf]')];
const dataRibbon = document.getElementById('data-ribbon');

// Beat ticks on the scrub bar.
for (const b of BEATS){
  const tick = document.createElement('div');
  tick.className = 'tick';
  tick.style.left = `${STARTS[BEATS.indexOf(b)] / TOTAL * 100}%`;
  tick.dataset.beat = BEATS.indexOf(b);
  bar.appendChild(tick);
}


function workflowKeyForBeat(id){
  if (id === 'sense') return 'sense';
  if (id === 'window') return 'window';
  if (id === 'transmit') return 'packet';
  if (id === 'dashboard') return 'dashboard';
  if (id === 'power') return 'validate';
  return '';
}
function updateWorkflowBoard(){
  const current = workflowKeyForBeat(BEATS[beat].id);
  const order = ['sense','window','packet','dashboard','validate'];
  const currentIndex = order.indexOf(current);
  workflowSteps.forEach(step => {
    const idx = order.indexOf(step.dataset.wf);
    step.classList.toggle('active', idx === currentIndex);
    step.classList.toggle('done', currentIndex > idx && idx >= 0);
  });
  dataRibbon?.classList.toggle('on', current === 'packet' || current === 'dashboard');
}

function syncBeatUI(){
  const b = BEATS[beat];
  capEl.innerHTML = b.cap;
  capNote.textContent = b.note;
  capEl.classList.add('on');
  beatName.textContent = b.name;
  clockFace.textContent = b.tick === 'send' ? 'UPLOADING PACKET' : b.tick === 'window' ? 'SUMMARY WINDOW — 2:00' : b.tick === 'sample' ? 'LOCAL SAMPLING' : b.tick === 'cloud' ? 'DASHBOARD UPDATE' : b.tick === 'power' ? 'POWER CHECK' : 'READY';
  clockFace.classList.toggle('send', b.tick === 'send');
  clockFace.classList.toggle('on', b.tick === 'sample' || b.tick === 'window' || b.tick === 'cloud' || b.tick === 'power');
  clockSub.textContent = b.tick === 'send' ? 'Wi-Fi/LTE · one compact packet'
    : b.tick === 'sample' ? 'pressure · wind · GPS · power'
    : b.tick === 'window' ? 'average · min · max · peak · flags'
    : b.tick === 'cloud' ? 'store · visualize · label state'
    : b.tick === 'power' ? 'battery · solar · current log'
    : 'proposal animation · not field data';
  updateWorkflowBoard();
}

function setPlaying(on){
  playing = on;
  btnPlay.textContent = on ? '❚❚ PAUSE' : '▶ PLAY';
  btnPlay.setAttribute('aria-label', on ? 'Pause' : 'Play');
}

// Proposal arithmetic: local samples about every 5 s, one cloud packet every 2 min.
const DAILY_SENSE = Math.round(86400 / 5);
const DAILY_SEND = 720;
const fmtN = n => n.toLocaleString('en-US');

function updateOverlay(){
  const pct = time / TOTAL;
  barFill.style.width = `${pct * 100}%`;
  barHead.style.left = `${pct * 100}%`;
  tNow.textContent = fmt(time);
  bar.setAttribute('aria-valuenow', Math.round(pct * 100));
  for (const t of bar.querySelectorAll('.tick')) t.classList.toggle('on', +t.dataset.beat === beat);

  // Channel callout follows the highlighted sensor on screen.
  const ch = S.highlight ? CHANNELS[S.highlight] : null;
  if (ch){
    const v = ch.pos.clone().project(camera);
    const w = stage.clientWidth, h = stage.clientHeight;
    const x = (v.x * 0.5 + 0.5) * w;
    const y = (-v.y * 0.5 + 0.5) * h;
    callout.style.left = `${Math.max(96, Math.min(w - 96, x))}px`;
    callout.style.top = `${Math.max(40, y - 78)}px`;
    calloutT.textContent = ch.label;
    calloutS.textContent = ch.sub;
    callout.classList.add('on');
  } else {
    callout.classList.remove('on');
  }

  counters.classList.toggle('on', S.showCounters);
  minimap.classList.toggle('on', S.showMap);
  if (S.showCounters && S.counterT >= 0){
    const k = easeInOut(S.counterT);
    cSense.textContent = fmtN(Math.round(DAILY_SENSE * k));
    cSend.textContent = fmtN(Math.round(DAILY_SEND * k));
    cRatio.textContent = S.counterT > 0.85
      ? `≈ ${Math.round(DAILY_SENSE / DAILY_SEND)}×`
      : '—';
  }
}

// Readouts: illustrative values driven by the timeline, not random.
function updateReadouts(){
  const b = BEATS[beat];
  const k = Math.min(1, (time - STARTS[beat]) / b.dur);
  const rough = b.id === 'window' ? Math.sin(Math.PI * Math.min(1, k * 1.2)) : 0;
  const hs = 0.55 + rough * 0.95 + S.seaAmp * 4;
  roWave.querySelector('b').textContent = `${hs.toFixed(2)} m`;
  roWave.className = `readout ${rough > 0.4 ? 'hot' : 'idle'}`;
  const wind = 14 + Math.sin(time * 0.6) * 3 + rough * 9;
  roWind.querySelector('b').textContent = `${wind.toFixed(0)} km/h`;
  roWind.className = `readout idle`;
  const batt = 92 - ((time / TOTAL) * 0.6);
  roBatt.querySelector('b').textContent = `${batt.toFixed(0)}%`;
  roBatt.className = `readout live`;
  const sending = b.tick === 'send' && S.radioT >= 0;
  roLink.querySelector('b').textContent = sending ? 'UPLOADING' : b.tick === 'cloud' ? 'CLOUD OK' : b.tick === 'power' ? 'LOGGING' : 'LOCAL';
  roLink.className = `readout ${sending ? 'hot' : (b.tick === 'cloud' || b.tick === 'power') ? 'live' : 'idle'}`;
}

// ---------------------------------------------------------------- transport
btnPlay.addEventListener('click', () => {
  if (freeCam) toggleFreeCam();
  setPlaying(!playing);
});
btnReplay.addEventListener('click', () => {
  time = 0; if (freeCam) toggleFreeCam(); setPlaying(true);
});
btnCC.addEventListener('click', () => {
  ccOn = !ccOn;
  document.getElementById('captions').classList.toggle('hidden', !ccOn);
  btnCC.textContent = ccOn ? 'CC ON' : 'CC OFF';
  btnCC.setAttribute('aria-pressed', String(ccOn));
});
function toggleFreeCam(){
  freeCam = !freeCam;
  btnOrbit.textContent = freeCam ? 'FOLLOW TIMELINE' : 'FREE CAMERA';
  btnOrbit.setAttribute('aria-pressed', String(freeCam));
  if (!freeCam) setPlaying(true);
}
btnOrbit.addEventListener('click', toggleFreeCam);

// Scrub by clicking or dragging the bar.
let scrubbing = false;
const seek = e => {
  const r = bar.getBoundingClientRect();
  time = Math.max(0, Math.min(1, (e.clientX - r.left) / r.width)) * TOTAL;
};
bar.addEventListener('pointerdown', e => {
  scrubbing = true;
  // Synthetic/synthetic-id events can reject capture; seeking still works.
  try { bar.setPointerCapture(e.pointerId); } catch {}
  seek(e);
});
bar.addEventListener('pointermove', e => { if (scrubbing) seek(e); });
bar.addEventListener('pointerup', () => { scrubbing = false; });
bar.addEventListener('keydown', e => {
  if (e.key === 'ArrowRight'){ time = Math.min(TOTAL - 0.1, time + 2); e.preventDefault(); }
  if (e.key === 'ArrowLeft'){ time = Math.max(0, time - 2); e.preventDefault(); }
});
addEventListener('keydown', e => {
  if (e.key === ' '){ if (freeCam) toggleFreeCam(); setPlaying(!playing); e.preventDefault(); }
});

// Drag the stage to take the camera; pinch to zoom on touch.
const touches = new Map();
let pinchStart = 0, pinchDist0 = 0;
const el = renderer.domElement;
el.addEventListener('pointerdown', e => {
  if (!freeCam) toggleFreeCam();
  stage.classList.add('dragging');
  el.setPointerCapture(e.pointerId);
  if (e.pointerType === 'touch') touches.set(e.pointerId, e);
});
el.addEventListener('pointermove', e => {
  if (e.pointerType === 'touch' && touches.has(e.pointerId)){
    touches.set(e.pointerId, e);
    if (touches.size === 2){
      const [a, b] = [...touches.values()];
      const d = Math.hypot(a.clientX - b.clientX, a.clientY - b.clientY);
      if (pinchDist0 > 0 && d > 0) camState.dist = Math.max(0.6, Math.min(9, pinchDist0 / d * pinchStart));
      return;
    }
  }
  if (!el.hasPointerCapture || !el.hasPointerCapture(e.pointerId)) return;
  const dx = e.movementX ?? 0, dy = e.movementY ?? 0;
  camTarget.yaw -= dx * 0.006;
  camTarget.pitch = Math.max(-1.0, Math.min(1.15, camTarget.pitch + dy * 0.004));
});
['pointerup','pointercancel'].forEach(ev => el.addEventListener(ev, e => {
  touches.delete(e.pointerId);
  stage.classList.remove('dragging');
  if (touches.size === 2){
    const [a, b] = [...touches.values()];
    pinchDist0 = Math.hypot(a.clientX - b.clientX, a.clientY - b.clientY);
    pinchStart = camState.dist;
  } else { pinchDist0 = 0; }
}));
el.addEventListener('wheel', e => {
  e.preventDefault();
  if (!freeCam) toggleFreeCam();
  camState.dist = Math.max(0.6, Math.min(9, camState.dist + e.deltaY * 0.0025));
}, {passive:false});

// ---------------------------------------------------------------- mini map (beat 7)
const MM = {lon0:116.7, lon1:121.3, lat0:7.5, lat1:12.6, w:100, h:210};
const mmX = lon => (lon - MM.lon0) / (MM.lon1 - MM.lon0) * MM.w;
const mmY = lat => (MM.lat1 - lat) / (MM.lat1 - MM.lat0) * MM.h;
const NET = [
  {id:'F-01', name:'Honda Bay', lon:119.10, lat:9.88},
  {id:'F-02', name:'El Nido · Bacuit Bay', lon:119.45, lat:11.30},
  {id:'F-03', name:'Coron Bay', lon:120.25, lat:12.00},
  {id:'F-04', name:'Balabac Strait', lon:116.95, lat:7.85},
  {id:'F-05', name:'San Vicente', lon:119.62, lat:10.60},
  {id:'F-06', name:'Ulugan Bay', lon:118.52, lat:10.05},
  {id:'F-07', name:'Linapacan Strait', lon:119.95, lat:11.55},
  {id:'F-08', name:'Puerto Princesa Bay', lon:118.88, lat:9.66},
];
(function buildMinimap(){
  const svg = document.getElementById('mm-svg');
  const NS = 'http://www.w3.org/2000/svg';
  const mk = (tag, attrs, parent) => {
    const e = document.createElementNS(NS, tag);
    for (const k in attrs) e.setAttribute(k, attrs[k]);
    (parent || svg).appendChild(e);
    return e;
  };
  for (const ring of ISLANDS){
    mk('polygon', {points: ring.map(([lo, la]) => `${mmX(lo).toFixed(1)},${mmY(la).toFixed(1)}`).join(' '),
      fill:'#2a6b4f', stroke:'#1d4a38', 'stroke-width':0.6, 'stroke-linejoin':'round'});
  }
  NET.forEach((b, i) => {
    mk('circle', {id:`mm-${i}`, cx:mmX(b.lon).toFixed(1), cy:mmY(b.lat).toFixed(1), r:2.4,
      fill:'#0b2a33', stroke:'#4a7484', 'stroke-width':0.8});
  });
})();
function animateMinimap(){
  if (!S.showMap){ NET.forEach((_, i) => { const c = document.getElementById(`mm-${i}`); if(c){ c.setAttribute('fill','#0b2a33'); c.setAttribute('r',2.4); } }); return; }
  const b = BEATS[beat];
  const k = Math.min(1, (time - STARTS[beat]) / b.dur);
  NET.forEach((_, i) => {
    const c = document.getElementById(`mm-${i}`);
    if (!c) return;
    const lit = k > 0.18 + i * 0.075;
    c.setAttribute('fill', lit ? '#d8a94e' : '#0b2a33');
    c.setAttribute('r', lit ? 3.1 : 2.4);
  });
}

// ---------------------------------------------------------------- frame loop
const projected = new THREE.Vector3();
function updateChannelMarkers(elapsed, dt){
  for (const c of Object.values(CHANNELS)){
    const on = S.highlight && CHANNELS[S.highlight] === c;
    const want = on ? 1 : 0;
    c.amount = (c.amount ?? 0) + (want - (c.amount ?? 0)) * (1 - Math.exp(-dt * 7));
    if (c.amount < 0.01){ c.ring.material.opacity = 0; c.dot.material.opacity = 0; continue; }
    const pulse = 0.5 + 0.5 * Math.sin(elapsed * 3.4);
    c.ring.material.opacity = c.amount * (0.45 + pulse * 0.45);
    c.dot.material.opacity = c.amount * 0.85;
    c.ring.quaternion.copy(camera.quaternion);
    c.dot.quaternion.copy(camera.quaternion);
    c.ring.position.copy(c.pos);
    c.dot.position.copy(c.pos);
    c.ring.scale.setScalar(1 + pulse * 0.28);
  }
}

function updateRadio(elapsed){
  // Transmit bead climbs from the deck to the antenna tip, then bursts.
  if (S.radioT >= 0){
    const k = easeInOut(Math.min(1, S.radioT));
    radio.position.set(ANT_TOP, D.housingCentreY + k * (ANT_TOP_Y - D.housingCentreY), ANT_TOP_Z);
    radio.material.opacity = 0.35 + 0.65 * Math.abs(Math.sin(k * Math.PI));
    radio.scale.setScalar(1 + 0.4 * Math.sin(k * Math.PI));
  } else {
    radio.material.opacity = 0;
  }
  BURSTS.forEach((m, i) => {
    if (S.burstT >= 0){
      const u = (S.burstT + i / BURSTS.length) % 1;
      m.scale.setScalar(1 + u * 5);
      m.material.opacity = Math.max(0, (1 - u) * 0.85);
    } else {
      m.material.opacity = 0;
    }
  });
  // Threshold flare at the waterline.
  if (S.flareT >= 0){
    const u = Math.min(1, S.flareT);
    flare.scale.setScalar(1 + u * 1.5);
    flare.material.opacity = Math.max(0, (1 - u) * 0.8);
  } else {
    flare.material.opacity = 0;
  }
}

function updateSea(elapsed, dt){
  const p = sea.geometry.attributes.position;
  const amp = S.seaAmp, surge = S.seaSurge;
  const t = elapsed * S.seaSpeed;
  for (let i = 0; i < p.count; i++){
    const x = p.getX(i), y = p.getY(i);
    const base = Math.sin(x * 0.5 + t) * amp + Math.cos(y * 0.4 + t * 0.8) * amp * 0.8;
    const travelling = surge * Math.sin(x * 0.9 - t * 2.6);
    p.setZ(i, base + travelling);
  }
  p.needsUpdate = true;
  sea.geometry.computeVertexNormals();

  // Hull motion follows the sea it floats on.
  buoy.position.y = Math.sin(t * 0.9) * S.bobAmp;
  buoy.rotation.z = Math.sin(t * 0.6) * S.heel;
  buoy.rotation.x = Math.cos(t * 0.7) * S.heel * 0.5;
  model.moving.rotor.rotation.y += S.windRps * (0.6 + S.seaAmp * 6);
  model.moving.vane.rotation.y = Math.sin(t * 0.36) * 0.25;
}

function updateLed(elapsed){
  // Slow LED heartbeat, with an extra bright pulse while transmitting.
  const beatv = Math.pow(Math.max(0, Math.sin(elapsed * 2 * Math.PI / 5)), 8);
  model.M.led.emissiveIntensity = 0.25 + beatv * 2.2 + S.sendPulse * 3.4;
}

function resize(){
  // Explicit pixels, never CSS %: % heights plus a grid row can feed back into
  // each other and blow the stage up, which collapses the camera frustum.
  const w = Math.max(2, stage.clientWidth);
  const h = Math.max(2, Math.min(stage.clientHeight || 520, 760));
  renderer.setSize(w, h);
  camera.aspect = w / h; camera.updateProjectionMatrix();
}
addEventListener('resize', resize); resize();

const clock = new THREE.Clock();
let last = 0;
function frame(){
  requestAnimationFrame(frame);
  const elapsed = clock.getElapsedTime();
  const dt = Math.min(0.05, elapsed - last) || 0.016;
  last = elapsed;

  advance(dt);

  // Chase the blended camera target (only when the timeline is driving).
  if (!freeCam){
    const k = 1 - Math.exp(-dt * CHASE);
    camState.yaw += (camTarget.yaw - camState.yaw) * k;
    camState.pitch += (camTarget.pitch - camState.pitch) * k;
    camState.dist += (camTarget.dist - camState.dist) * k;
    camState.focus.lerp(camTarget.focus, k);
  }
  const f = camState.focus;
  camera.position.set(
    f.x + Math.cos(camState.pitch) * Math.sin(camState.yaw) * camState.dist,
    f.y + Math.sin(camState.pitch) * camState.dist,
    f.z + Math.cos(camState.pitch) * Math.cos(camState.yaw) * camState.dist
  );
  camera.lookAt(f);

  updateSea(elapsed, dt);
  updateLed(elapsed);
  updateRadio(elapsed);
  updateChannelMarkers(elapsed, dt);
  updateOverlay();
  updateReadouts();
  animateMinimap();
  renderer.render(scene, camera);
}

// ---------------------------------------------------------------- start
// The option row scrolls horizontally on narrow screens; bring this page's own
// link into view so the visitor can see where they are.
document.querySelector('nav.opts a.here')?.scrollIntoView({block:'nearest', inline:'center'});

// Deep links, so a panel member can bookmark one moment:
//   ?beat=5      jump to the start of beat 5 and hold there
//   ?t=41        jump to 41 s and hold there
const qs = new URLSearchParams(location.search);
const jumpBeat = parseInt(qs.get('beat'), 10);
const jumpTime = parseFloat(qs.get('t'));
let deepLinked = false;
if (jumpBeat >= 1 && jumpBeat <= BEATS.length){
  time = STARTS[jumpBeat - 1] + 0.01;
  deepLinked = true;
} else if (Number.isFinite(jumpTime)){
  time = Math.max(0, Math.min(TOTAL - 0.1, jumpTime));
  deepLinked = true;
}

syncBeatUI();
beat = beatAt(time);
syncBeatUI();
updateReadouts();
// Respect prefers-reduced-motion: hold on the first frame and let the viewer
// press play, rather than moving the camera on its own. A deep link also holds,
// so the reader lands on the moment that was linked instead of racing past it.
if (reduced || deepLinked){
  setPlaying(false);
  clock.getDelta();
} else {
  setPlaying(true);
}
frame();