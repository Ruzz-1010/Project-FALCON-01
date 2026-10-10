// FALCON 8-buoy Palawan deployment preview — real-coastline SVG map +
// simulated telemetry. Coastline: GADM v4.1, simplified for display.
// Positions are illustrative and all readings are generated in-page.
// No fetch, no tiles, no backend.
import {ISLANDS} from './palawan-geo.js';
const LON0 = 116.7, LON1 = 121.2, LAT0 = 7.6, LAT1 = 12.5, W = 560, H = 700;
const X = lon => (lon - LON0) / (LON1 - LON0) * W;
const Y = lat => (LAT1 - lat) / (LAT1 - LAT0) * H;

const BUOYS = [
  {id:'FALCON-01', name:'Honda Bay', lon:119.10, lat:9.88, depth:18},
  {id:'FALCON-02', name:'El Nido · Bacuit Bay', lon:119.45, lat:11.30, depth:22},
  {id:'FALCON-03', name:'Coron Bay', lon:120.25, lat:12.00, depth:25},
  {id:'FALCON-04', name:'Balabac Strait', lon:116.95, lat:7.85, depth:30},
  {id:'FALCON-05', name:'San Vicente · Long Beach', lon:119.62, lat:10.60, depth:15},
  {id:'FALCON-06', name:'Ulugan Bay', lon:118.52, lat:10.05, depth:20},
  {id:'FALCON-07', name:'Linapacan Strait', lon:119.95, lat:11.55, depth:28},
  {id:'FALCON-08', name:'Puerto Princesa Bay', lon:118.88, lat:9.66, depth:12},
];

const DIRS = ['N','NNE','NE','ENE','E','ESE','SE','SSE','S','SSW','SW','WSW','W','WNW','NW','NNW'];
const dirName = d => DIRS[Math.round(d / 22.5) % 16];
// Deterministic per-buoy baseline so the map looks alive but stable.
function seedOf(s){ let h = 0; for(const c of s) h = (h*31 + c.charCodeAt(0)) >>> 0; return h; }
function mulberry(seed){
  let a = seed >>> 0;
  return () => { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };
}
const HN = 24; // history points per buoy (~2h at 5-min heartbeat)
for(const b of BUOYS){
  const r = mulberry(seedOf(b.id));
  b.windDir = r()*360; b.wind = 8 + r()*22; b.gust = 0;
  b.hs = 0.3 + r()*1.8; b.period = 4 + r()*5; b.batt = 62 + r()*36;
  b.rssi = -95 + r()*40; b.seen = Math.floor(r()*50) + 5; b.phase = r()*6.28;
  // Backfill a plausible simulated history ending at current values.
  b.hsHist = []; b.windHist = [];
  let hw = b.hs, ww = b.wind;
  for(let i=0;i<HN;i++){ hw = Math.max(.15, Math.min(3.2, hw + (r()-.5)*.3)); ww = Math.max(3, Math.min(55, ww + (r()-.5)*4)); b.hsHist.unshift(hw); b.windHist.unshift(ww); }
  b.hsHist[HN-1] = b.hs; b.windHist[HN-1] = b.wind;
}
const stateOf = hs => hs < 0.6 ? ['CALM','calm'] : hs < 1.6 ? ['MODERATE','mod'] : ['ROUGH','rough'];
const stateColor = hs => hs < 0.6 ? '#8fd694' : hs < 1.6 ? '#e8c35a' : '#e87a7a';
const wordsOf = (b, st) => st === 'CALM'
  ? `Calm water at ${b.name} — light winds, small waves. Good sea day.`
  : st === 'MODERATE'
  ? `Breezy at ${b.name} — moderate winds and noticeable waves. Small craft take care.`
  : `Windy at ${b.name} — strong winds and rough waves. Not a small-boat day.`;

const svgNS = 'http://www.w3.org/2000/svg';
const svg = document.getElementById('palawan');
// Smooth sea animation state: one clock drives every buoy's rings + bob so
// nothing uses CSS transitions (they cannot loop cleanly) and nothing restarts.
const anim = [];
function el(tag, attrs, parent){
  const e = document.createElementNS(svgNS, tag);
  for(const [k,v] of Object.entries(attrs)) e.setAttribute(k, v);
  (parent || svg).appendChild(e);
  return e;
}
// Sea grid.
for(let i=1;i<7;i++){ el('line',{x1:W*i/7,y1:0,x2:W*i/7,y2:H,stroke:'#12333f','stroke-width':1}); }
for(let i=1;i<8;i++){ el('line',{x1:0,y1:H*i/8,x2:W,y2:H*i/8,stroke:'#12333f','stroke-width':1}); }
// Compass rose.
const cx = 70, cy = 620;
el('circle',{cx,cy,r:26,fill:'none',stroke:'#2c5a6b','stroke-width':1.5});
el('text',{x:cx,y:cy-32,fill:'#8fb0bd','font-size':12,'text-anchor':'middle'}).textContent = 'N ↑';
// Real coastline polygons (GADM, simplified): main island + groups.
for(const ring of ISLANDS){
  el('polygon',{
    points: ring.map(([lo,la]) => `${X(lo).toFixed(1)},${Y(la).toFixed(1)}`).join(' '),
    fill:'#2a6b4f', stroke:'#1d4a38', 'stroke-width':1.5, 'stroke-linejoin':'round'
  });
}
const lbl = (t,lo,la,size=13) => { const e = el('text',{x:X(lo),y:Y(la),fill:'#8fb0bd','font-size':size,'text-anchor':'middle'}); e.textContent = t; };
lbl('P A L A W A N', 118.35, 8.95, 15);
lbl('Balabac', 117.62, 8.30); lbl('El Nido', 118.95, 11.62); lbl('Coron', 120.32, 12.28);
lbl('Puerto Princesa', 118.15, 9.30); lbl('SULU SEA', 119.75, 9.45, 12); lbl('WPS', 117.05, 10.35, 12);
// Buoy markers.
const markers = new Map();
for(const b of BUOYS){
  // wrap = animated bob/sway (vertical + rotation), g = static map position.
  const wrap = el('g',{}, svg);
  const g = el('g',{class:'buoy',tabindex:'0',role:'button','aria-label':`${b.id} ${b.name} simulated data`}, wrap);
  const pulse = el('circle',{class:'pulse',cx:X(b.lon),cy:Y(b.lat),r:13,stroke:stateColor(b.hs)},g);
  // Animated wave rings, visible only while seas are ROUGH at this buoy.
  // Smooth rolling sea: nested smooth rings that grow + fade on long loops.
  // CSS transitions alone can't restart reliably, so use Web Animations API.
  const seas = el('g',{class:'seas'},g);
  for(let k=0;k<4;k++){
    const w = el('circle',{class:'wave-ring',cx:X(b.lon),cy:Y(b.lat),r:16,stroke:'#e87a7a'},seas);
    anim.push({node:w, phase:k/4, base:16});
  }
  const core = el('circle',{class:'core',cx:X(b.lon),cy:Y(b.lat),r:9,fill:stateColor(b.hs)},g);
  const t = el('text',{x:X(b.lon)+14,y:Y(b.lat)+4},g); t.textContent = b.id.replace('FALCON-','F-');
  g.addEventListener('click', () => select(b.id));
  g.addEventListener('keydown', e => { if(e.key==='Enter'||e.key===' '){ e.preventDefault(); select(b.id); } });
  markers.set(b.id, {g, wrap, pulse, core, seas});
}

const $ = id => document.getElementById(id);
// Dashboard-style history chart: normalized polyline + last-point dot.
function drawChart(svgId, data, color, unit){
  const svgEl = $(svgId);
  while(svgEl.firstChild) svgEl.removeChild(svgEl.firstChild);
  const lo = Math.min(...data), hi = Math.max(...data), span = (hi - lo) || 1;
  const px = i => (i / (data.length - 1) * 196 + 2).toFixed(1);
  const py = v => (52 - (v - lo) / span * 46).toFixed(1);
  const NS = 'http://www.w3.org/2000/svg';
  const pl = document.createElementNS(NS, 'polyline');
  pl.setAttribute('points', data.map((v,i) => `${px(i)},${py(v)}`).join(' '));
  pl.setAttribute('fill', 'none'); pl.setAttribute('stroke', color);
  pl.setAttribute('stroke-width', '2'); pl.setAttribute('stroke-linejoin', 'round');
  svgEl.appendChild(pl);
  const last = data[data.length-1];
  const dot = document.createElementNS(NS, 'circle');
  dot.setAttribute('cx', px(data.length-1)); dot.setAttribute('cy', py(last));
  dot.setAttribute('r', '3'); dot.setAttribute('fill', color);
  svgEl.appendChild(dot);
  const tx = document.createElementNS(NS, 'text');
  tx.setAttribute('x', '4'); tx.setAttribute('y', '12');
  tx.setAttribute('fill', '#8fb0bd'); tx.setAttribute('font-size', '10');
  tx.setAttribute('stroke', '#0e212c'); tx.setAttribute('stroke-width', '4');
  tx.setAttribute('paint-order', 'stroke');
  tx.textContent = `${lo.toFixed(1)}–${hi.toFixed(1)} ${unit}`;
  svgEl.appendChild(tx);
}
let current = 0;
function select(id){
  current = BUOYS.findIndex(b => b.id === id);
  currentId = id;
  render();
}
function render(){
  const b = BUOYS[current], [st, cls] = stateOf(b.hs);
  $('b-name').textContent = `${b.id} · ${b.name}`;
  $('b-coords').textContent = `${b.lat.toFixed(2)}°N ${b.lon.toFixed(2)}°E · ~${b.depth}m site (illustrative)`;
  const pill = $('b-state'); pill.textContent = st; pill.className = 'pill ' + cls;
  $('b-words').textContent = wordsOf(b, st);
  $('b-wind').textContent = `${b.wind.toFixed(0)} km/h · gust ${b.gust.toFixed(0)}`;
  $('b-winddir').textContent = `from ${dirName(b.windDir)} (${b.windDir.toFixed(0)}°)`;
  $('b-hs').textContent = `${b.hs.toFixed(2)} m (est.)`;
  $('b-period').textContent = `period ~${b.period.toFixed(0)}s · ${st.toLowerCase()} seas`;
  $('b-batt').textContent = `${b.batt.toFixed(0)}% ${b.batt < 30 ? 'LOW' : 'OK'}`;
  $('b-battbar').style.width = `${b.batt.toFixed(0)}%`;
  $('b-battbar').style.background = b.batt < 30 ? '#e87a7a' : '#8fd694';
  $('b-link').textContent = `${'▂▄▆'.slice(0, b.rssi > -80 ? 3 : b.rssi > -95 ? 2 : 1)} ${b.rssi.toFixed(0)} dBm`;
  $('b-seen').textContent = `reported ${b.seen}s ago · heartbeat 5–15 min`;
  drawChart('b-hschart', b.hsHist, stateColor(b.hs), 'm');
  drawChart('b-windchart', b.windHist, '#9fd8e8', 'km/h');
  for(const [id, m] of markers){
    const on = id === b.id, bb = BUOYS.find(x => x.id === id);
    m.core.setAttribute('fill', stateColor(bb.hs));
    m.pulse.setAttribute('stroke', stateColor(bb.hs));
    // Wave animation plays on the clicked (selected) buoy only.
    m.seas.style.display = id === currentId ? '' : 'none';
    m.g.style.filter = on ? 'drop-shadow(0 0 6px #fff)' : '';
  }
  // Header stats.
  $('st-count').textContent = `${BUOYS.length} / ${BUOYS.length}`;
  const w = BUOYS.reduce((a,x) => x.wind > a.wind ? x : a);
  $('st-wind').textContent = `${w.wind.toFixed(0)} km/h @ ${w.name.split(' ')[0]}`;
  const hmax = BUOYS.reduce((a,x) => x.hs > a.hs ? x : a);
  $('st-sea').textContent = `${hmax.hs.toFixed(2)} m @ ${hmax.name.split(' ')[0]}`;
  const lbat = BUOYS.reduce((a,x) => x.batt < a.batt ? x : a);
  $('st-batt').textContent = `${lbat.batt.toFixed(0)}% @ ${lbat.id.replace('FALCON-','F-')}`;
}
// One rAF loop: wave rings grow+fade smoothly around the SELECTED buoy
// only. Markers stay pinned on the map — no dancing buoys.
let currentId = BUOYS[0].id;
let t0 = performance.now();
function tick(now){
  const t = (now - t0) / 1000;
  for(const {node, phase, base} of anim){
    const u = (t / 5 + phase) % 1;          // 5s per ring cycle, staggered
    const scale = 0.55 + u * 2.6;           // smooth grow
    const opacity = Math.sin(Math.PI * u) * 0.85; // fade in then out
    node.setAttribute('r', (base * scale).toFixed(2));
    node.setAttribute('opacity', Math.max(0, opacity).toFixed(3));
  }
  requestAnimationFrame(tick);
}
requestAnimationFrame(tick);

$('prev').addEventListener('click', () => select(BUOYS[(current + BUOYS.length - 1) % BUOYS.length].id));
$('next').addEventListener('click', () => select(BUOYS[(current + 1) % BUOYS.length].id));
// Simulated live tick every 4s: random-walk every buoy, re-render selection.
setInterval(() => {
  const t = Date.now()/1000;
  for(const b of BUOYS){
    b.wind = Math.max(3, Math.min(55, b.wind + Math.sin(t/9 + b.phase)*1.2 + (Math.random()-.5)*1.5));
    b.gust = b.wind + 4 + Math.random()*9;
    b.windDir = (b.windDir + (Math.random()-.5)*8 + 360) % 360;
    b.hs = Math.max(.15, Math.min(3.2, b.hs + Math.cos(t/12 + b.phase)*.08 + (Math.random()-.5)*.1));
    b.period = Math.max(3, Math.min(11, b.period + (Math.random()-.5)*.4));
    b.batt = Math.max(5, Math.min(100, b.batt + (Math.random() > .6 ? .2 : -.15)));
    b.rssi = Math.max(-110, Math.min(-50, b.rssi + (Math.random()-.5)*3));
    b.seen = 3 + Math.floor(Math.random()*40);
    b.hsHist.push(b.hs); b.hsHist.shift();
    b.windHist.push(b.wind); b.windHist.shift();
  }
  render();
}, 4000);
render();
