// FALCON 8-buoy Palawan deployment preview — stylized SVG map + simulated
// telemetry. EVERYTHING here is simulated: positions are illustrative and all
// readings are generated in-page. No fetch, no tiles, no backend.
const LON0 = 116.7, LON1 = 120.5, LAT0 = 7.6, LAT1 = 12.3, W = 560, H = 700;
const X = lon => (lon - LON0) / (LON1 - LON0) * W;
const Y = lat => (LAT1 - lat) / (LAT1 - LAT0) * H;

// Stylized Palawan main-island spine (lon/lat, SW -> NE), drawn as a thick
// round-capped stroke so it reads as an island chain, not survey data.
const SPINE = [
  [117.05,7.90],[117.30,8.20],[117.55,8.45],[117.85,8.70],[118.05,8.95],
  [118.20,9.25],[118.35,9.50],[118.55,9.70],[118.72,9.74],[118.85,9.90],
  [118.95,10.10],[119.05,10.35],[119.15,10.55],[119.28,10.75],[119.35,11.00],
  [119.30,11.20],[119.22,11.35],[119.30,11.44]
];
// Calamian group (Busuanga/Coron) + Cuyo dots, stylized.
const CALAMIAN = [[119.85,11.85],[120.05,11.95],[120.25,12.05],[120.35,11.90],[120.15,11.75],[119.90,11.72]];
const CUYO = [[121.00 - 0.55,10.85],[121.00 - 0.40,10.60]];
const DUMARAN = [[119.75,10.55]];

const BUOYS = [
  {id:'FALCON-01', name:'Honda Bay', lon:118.95, lat:9.85, depth:18},
  {id:'FALCON-02', name:'El Nido · Bacuit Bay', lon:119.45, lat:11.30, depth:22},
  {id:'FALCON-03', name:'Coron Bay', lon:120.25, lat:12.00, depth:25},
  {id:'FALCON-04', name:'Balabac Strait', lon:116.95, lat:7.85, depth:30},
  {id:'FALCON-05', name:'San Vicente · Long Beach', lon:119.45, lat:10.60, depth:15},
  {id:'FALCON-06', name:'Ulugan Bay', lon:118.65, lat:10.05, depth:20},
  {id:'FALCON-07', name:'Linapacan Strait', lon:119.95, lat:11.55, depth:28},
  {id:'FALCON-08', name:'Puerto Princesa Bay', lon:118.60, lat:9.70, depth:12},
];

const DIRS = ['N','NNE','NE','ENE','E','ESE','SE','SSE','S','SSW','SW','WSW','W','WNW','NW','NNW'];
const dirName = d => DIRS[Math.round(d / 22.5) % 16];
// Deterministic per-buoy baseline so the map looks alive but stable.
function seedOf(s){ let h = 0; for(const c of s) h = (h*31 + c.charCodeAt(0)) >>> 0; return h; }
function mulberry(seed){
  let a = seed >>> 0;
  return () => { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };
}
for(const b of BUOYS){
  const r = mulberry(seedOf(b.id));
  b.windDir = r()*360; b.wind = 8 + r()*22; b.gust = 0;
  b.hs = 0.3 + r()*1.8; b.period = 4 + r()*5; b.batt = 62 + r()*36;
  b.rssi = -95 + r()*40; b.seen = Math.floor(r()*50) + 5; b.phase = r()*6.28;
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
// Islands.
const pathOf = pts => 'M' + pts.map(([lo,la]) => `${X(lo).toFixed(1)},${Y(la).toFixed(1)}`).join(' L');
el('path',{d:pathOf(SPINE),fill:'none',stroke:'#1d4a38','stroke-width':22,'stroke-linecap':'round','stroke-linejoin':'round'});
el('path',{d:pathOf(SPINE),fill:'none',stroke:'#2a6b4f','stroke-width':13,'stroke-linecap':'round','stroke-linejoin':'round'});
el('polygon',{points:CALAMIAN.map(([lo,la])=>`${X(lo).toFixed(1)},${Y(la).toFixed(1)}`).join(' '),fill:'#2a6b4f',stroke:'#1d4a38','stroke-width':2});
for(const [lo,la] of [...CUYO, ...DUMARAN]) el('circle',{cx:X(lo),cy:Y(la),r:5,fill:'#2a6b4f',stroke:'#1d4a38','stroke-width':1.5});
const lbl = (t,lo,la,size=13) => { const e = el('text',{x:X(lo),y:Y(la),fill:'#8fb0bd','font-size':size,'text-anchor':'middle'}); e.textContent = t; };
lbl('P A L A W A N', 118.55, 9.15, 15);
lbl('Balabac', 117.35, 7.62); lbl('El Nido', 119.05, 11.62); lbl('Coron', 120.28, 12.22);
lbl('Puerto Princesa', 118.30, 9.38); lbl('SULU SEA', 119.55, 9.30, 12); lbl('WPS', 117.15, 10.6, 12);
// Buoy markers.
const markers = new Map();
for(const b of BUOYS){
  const g = el('g',{class:'buoy',tabindex:'0',role:'button','aria-label':`${b.id} ${b.name} simulated data`});
  const pulse = el('circle',{class:'pulse',cx:X(b.lon),cy:Y(b.lat),r:13,stroke:stateColor(b.hs)},g);
  const core = el('circle',{class:'core',cx:X(b.lon),cy:Y(b.lat),r:9,fill:stateColor(b.hs)},g);
  const t = el('text',{x:X(b.lon)+14,y:Y(b.lat)+4},g); t.textContent = b.id.replace('FALCON-','F-');
  g.addEventListener('click', () => select(b.id));
  g.addEventListener('keydown', e => { if(e.key==='Enter'||e.key===' '){ e.preventDefault(); select(b.id); } });
  markers.set(b.id, {g, pulse, core});
}

const $ = id => document.getElementById(id);
let current = 0;
function select(id){
  current = BUOYS.findIndex(b => b.id === id);
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
  for(const [id, m] of markers){
    const on = id === b.id, bb = BUOYS.find(x => x.id === id);
    m.core.setAttribute('fill', stateColor(bb.hs));
    m.pulse.setAttribute('stroke', stateColor(bb.hs));
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
  }
  render();
}, 4000);
render();
