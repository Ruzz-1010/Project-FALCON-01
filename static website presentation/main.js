import logoUrl from '../dashboard-next/public/falcon-logo.jpg?url';
import {inspections} from './inspection.js';
import {smooth} from './home.js';
import {chapters,components,createLink,setLink,tickLink,waveSamples,forecastSamples,linePath} from './story.js';

const $=selector=>document.querySelector(selector);
$('#logo').src=logoUrl;
const sections=[...document.querySelectorAll('.scene')];
const reduced=matchMedia('(prefers-reduced-motion: reduce)');
let paused=reduced.matches,active=0,selected='pressure',world,elapsed=0,last=0,lastPacket=0,process=0,predicting=false,predictionProgress=0,currentTab='overview';
let link=createLink();
const pointer={x:0,y:0};
const history=waveSamples(),future=forecastSamples(history.at(-1));
const nav=$('#chapter-nav');
chapters.forEach((name,i)=>{const a=document.createElement('a');a.href=`#${sections[i].id}`;a.title=name;a.setAttribute('aria-label',`${i+1}. ${name}`);nav.append(a);});
let inspecting=false,inspectionTrigger;
function inspectionReady(){
  if(!inspecting)return;
  $('#inspection-content').hidden=false;$('#inspection-travel').hidden=true;
  document.body.classList.add('inspection-ready');$('#inspection-title').focus({preventScroll:true});
}
function endInspection(restoreFocus=true){
  if(!inspecting)return;inspecting=false;
  document.body.classList.remove('inspecting','inspection-ready');$('#inspection-panel').hidden=true;
  world?.returnToBuoy?.();
  if(restoreFocus&&inspectionTrigger?.isConnected)inspectionTrigger.focus({preventScroll:true});
}
$('#inspection-back').addEventListener('click',()=>endInspection());
document.addEventListener('keydown',e=>{if(e.key==='Escape')endInspection();});
function pick(id,inspect=true){
  selected=id;$('#component-title').textContent=components[id].label;$('#component-detail').textContent=components[id].detail;
  document.querySelectorAll('[data-component]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.component===id)));
  if(inspect){
    if(!world?.inspect?.(id)){ $('#model-state').textContent='Component guide available; wait for the original 3D model to load before inspection.';return; }
    inspectionTrigger=document.activeElement;inspecting=true;
    const info=inspections[id];$('#inspection-title').textContent=info.name;$('#inspection-function').textContent=info.function;
    $('#inspection-data').replaceChildren(...info.data.map(text=>{const li=document.createElement('li');li.textContent=text;return li;}));
    $('#inspection-flow').replaceChildren(...info.flow.map(text=>{const span=document.createElement('span');span.textContent=text;return span;}));
    $('#inspection-status').textContent=info.status;$('#inspection-note').textContent=info.note;
    $('#inspection-panel').hidden=false;$('#inspection-content').hidden=true;$('#inspection-travel').hidden=false;
    document.body.classList.add('inspecting');document.body.classList.remove('inspection-ready');
  }
}
for(const [id,c] of Object.entries(components)){
  for(const container of [$('#reveal-picks'),$('#sensor-menu')]){
    const b=document.createElement('button');b.textContent=c.label;b.dataset.component=id;b.setAttribute('aria-pressed',String(id===selected));b.addEventListener('click',()=>pick(id));container.append(b);
  }
}
pick(selected,false);
document.addEventListener('pointerover',e=>{const node=e.target.closest('[data-component]');if(node)world?.hover?.(node.dataset.component);});
document.addEventListener('pointerout',e=>{if(e.target.closest('[data-component]'))world?.hover?.(null);});
document.addEventListener('focusin',e=>{const node=e.target.closest('[data-component]');if(node)world?.hover?.(node.dataset.component);});
document.addEventListener('focusout',e=>{if(e.target.closest('[data-component]'))world?.hover?.(null);});
$('#cad-note').addEventListener('click',()=>{const expanded=$('#cad-note').getAttribute('aria-expanded')==='true';$('#cad-note').setAttribute('aria-expanded',String(!expanded));$('#cad-detail').hidden=expanded;});
function applyMotion(){document.body.classList.toggle('motion-paused',paused);$('#motion').textContent=paused?'Play motion':'Pause motion';$('#motion').setAttribute('aria-pressed',String(paused));}
$('#motion').addEventListener('click',()=>{paused=!paused;applyMotion();});
reduced.addEventListener('change',e=>{paused=e.matches;applyMotion();});applyMotion();
$('#fullscreen').addEventListener('click',async()=>{try{if(document.fullscreenElement)await document.exitFullscreen();else await document.documentElement.requestFullscreen();}catch{$('#model-state').textContent='Fullscreen unavailable in this browser.';}});
document.addEventListener('fullscreenchange',()=>$('#fullscreen').setAttribute('aria-label',document.fullscreenElement?'Exit fullscreen':'Enter fullscreen'));
window.addEventListener('pointermove',e=>{pointer.x=e.clientX/innerWidth*2-1;pointer.y=1-e.clientY/innerHeight*2;},{passive:true});

function updateLink(){
  $('#radio-route').classList.toggle('offline',!link.online);
  $('#interrupt').textContent=link.online?'Interrupt LoRa':'Restore LoRa';
  $('#link-label').textContent=link.online?(link.buffer.length?'LoRa / retransmitting':'LoRa / transmitting'):'LoRa / interrupted';
  $('#link-status').textContent=link.online?(link.buffer.length?'Replaying original timestamps':'Simulated link available'):'Buoy still sensing · shore data stale';
  $('#queued').textContent=String(link.buffer.length).padStart(2,'0');$('#received').textContent=String(link.received.length).padStart(2,'0');
  $('#buffer-packets').replaceChildren(...link.buffer.slice(-10).map(p=>{const i=document.createElement('i');i.textContent=String(p.id).padStart(3,'0');i.title=`Original sample: ${p.timestamp}`;return i;}));
  $('#recovery-note').textContent=link.phase==='buffering'?'Sample times stay with queued packets. This is a simulated buffer—not proof of field recovery.':link.phase==='retransmitting'?'Backlog replay → duplicate prevention → chronological storage. Original sample times preserved.':'Hardware, legal band and site coverage pending. No range guarantee.';
  $('#packet-frame').textContent=`FALCON-01 · seq ${String(link.sequence).padStart(4,'0')}\n${link.received.at(-1)?.timestamp||'sample timestamp'} · schema v1 · SIMULATED`;
}
$('#interrupt').addEventListener('click',()=>{
  link=setLink(link,!link.online);
  // Always demonstrate an immediate state change, even with reduced motion enabled.
  link=tickLink(link,new Date().toISOString());updateLink();renderDashboard();
  if(!link.online){predicting=false;predictionProgress=0;$('#future-reveal').setAttribute('width','0');$('#prediction-status').textContent='UNAVAILABLE: shore input is stale while LoRa is interrupted.';}
});
updateLink();

const processDescriptions=[
  ['MEASURED QUANTITY / SIMULATED PRESSURE','Relative signal · arbitrary units','The pressure sensor records underwater variations. These samples are illustrative, not hardware measurements.','—'],
  ['PROCESSED SIGNAL / SIMULATED','Relative signal · arbitrary units','Remove slow variation, filter, correct for depth response and calibrate. Processing parameters and reference method remain to be finalized.','—'],
  ['ESTIMATED Hs / SIMULATED','Estimated significant wave height','Compute a wave statistic over a defined observation window. Pressure itself is not wave height.',history.at(-1).toFixed(2)+' m']
];
function selectProcess(value){process=value;document.querySelectorAll('[data-process]').forEach(b=>b.setAttribute('aria-pressed',String(Number(b.dataset.process)===process)));const [label,unit,detail,result]=processDescriptions[value];$('#wave-label').textContent=label;$('#wave-unit').textContent=unit;$('#process-detail').textContent=detail;$('#hs-result').textContent=result;drawPressure(elapsed);}
document.querySelectorAll('[data-process]').forEach(b=>b.addEventListener('click',()=>selectProcess(Number(b.dataset.process))));
function drawPressure(time){const phase=time*.9;const clean=Array.from({length:160},(_,i)=>Math.sin(i*.15+phase)*.62+Math.sin(i*.37+phase)*.18);const raw=clean.map((v,i)=>v+Math.sin(i*.025)*.45+Math.sin(i*2.5)*.13);$('#raw-trace').setAttribute('d',linePath(raw,0,1000,112,65));$('#raw-trace').style.opacity=process===0?'.8':'.16';$('#processed-trace').setAttribute('d',linePath(clean,0,1000,112,65));$('#processed-trace').style.opacity=process===0?'0':'1';}
drawPressure(0);
$('#history-trace').setAttribute('d',linePath(history,45,585,190,140));$('#future-trace').setAttribute('d',linePath(future,630,340,190,140));$('#baseline-trace').setAttribute('d',linePath([history.at(-1),history.at(-1)],630,340,190,140));
$('#predict').addEventListener('click',()=>{if(!link.online){$('#prediction-status').textContent='UNAVAILABLE: restore LoRa before running a new prediction.';return;}predicting=true;predictionProgress=paused?1:0;$('#prediction-status').textContent='SIMULATED: extending a candidate trace against persistence.';if(paused)drawPrediction(0);});
function drawPrediction(dt){if(!predicting)return;predictionProgress=Math.min(1,predictionProgress+dt*.32);$('#future-reveal').setAttribute('width',String(predictionProgress*350));if(predictionProgress===1){predicting=false;$('#prediction-status').textContent='Illustrative AI trace vs. persistence. No accuracy claim.';}}

function overviewMarkup(){const stale=!link.online;return `<div class="demo-overview"><div><div class="demo-readings"><span>Estimated wave height<strong>${stale?'—':history.at(-1).toFixed(2)+' <small>m</small>'}</strong></span><span>AI · next 10 min<strong>${stale?'—':future.at(-1).toFixed(2)+' <small>m</small>'}</strong></span></div><svg class="demo-chart" viewBox="0 0 700 170" role="img" aria-label="Simulated estimated wave height and illustrative AI trace"><path class="chart-grid" d="M0 30H700 M0 85H700 M0 140H700"/>${stale?'<text x="210" y="85">STALE · waiting for packets</text>':`<path class="estimated-trace" d="${linePath(history,0,480,150,150)}"/><path class="future-trace" d="${linePath(future,480,210,150,150)}"/>`}</svg></div><dl class="demo-summary"><div><dt>Station</dt><dd>${stale?'STALE':'Simulation'}</dd></div><div><dt>LoRa</dt><dd>${stale?'Offline':'Receiving'}</dd></div><div><dt>Wind</dt><dd>${stale?'—':'11 km/h NE'}</dd></div><div><dt>Battery</dt><dd>${stale?'—':'78% demo'}</dd></div><div><dt>Security</dt><dd>${stale?'Unknown':'Secure demo'}</dd></div></dl></div>`;}
function renderDashboard(){
  const host=$('#dashboard-content');
  if(currentTab==='overview')host.innerHTML=overviewMarkup();
  if(currentTab==='motion')host.innerHTML='<div class="demo-motion"><svg viewBox="0 0 160 200" aria-label="Illustrative heave indicator, not a replacement buoy model" role="img"><path d="M10 125Q40 113 80 125T150 125" fill="none" stroke="#448591"/><g class="motion-outline"><path d="M80 40V100M70 50L80 40 90 50M70 90L80 100 90 90" fill="none" stroke="#357889" stroke-width="2"/><circle cx="80" cy="125" r="9" fill="#397d8a"/></g><text x="80" y="175" text-anchor="middle">HEAVE / DEMO</text></svg><p><strong>Buoy Motion</strong>Pressure-informed visualization—not measured roll or pitch.<br>The original CAD is the physical reference.<br><a href="#buoy">Return to original buoy ↗</a></p></div>';
  if(currentTab==='sensors')host.innerHTML=`<table class="sensor-table"><thead><tr><th>Observation</th><th>Role</th><th>Status</th></tr></thead><tbody><tr><td>Pressure</td><td>Wave processing input</td><td>${link.online?'Calibration pending':'Stale'}</td></tr><tr><td>Wind</td><td>Environmental context</td><td>Simulated</td></tr><tr><td>GPS</td><td>Supporting telemetry</td><td>Simulated</td></tr><tr><td>Battery / solar</td><td>Energy monitoring</td><td>Simulated</td></tr><tr><td>Enclosure</td><td>Health / security</td><td>Simulated</td></tr></tbody></table>`;
  if(currentTab==='logs')host.innerHTML=`<div class="demo-log"><time>SIM</time><span>${link.online?'Shore link available.':'LoRa interrupted. Buoy packets buffered.'}</span></div><div class="demo-log"><time>SIM</time><span>${link.buffer.length} packets queued · ${link.received.length} accepted without duplicate IDs.</span></div><div class="demo-log"><time>NOTE</time><span>Calibration and controlled deployment validation remain pending.</span></div><p class="demo-note">Presentation events only. No hardware, alarm or database connection.</p>`;
}
document.querySelectorAll('[data-tab]').forEach(b=>b.addEventListener('click',()=>{currentTab=b.dataset.tab;document.querySelectorAll('[data-tab]').forEach(el=>el.setAttribute('aria-pressed',String(el===b)));renderDashboard();}));renderDashboard();

let offsets=[];
let homeJourney=null;
const home=$('#ocean');
const cancelHomeJourney=()=>{homeJourney=null;};
for(const event of ['wheel','touchstart','pointerdown'])window.addEventListener(event,cancelHomeJourney,{passive:true});
window.addEventListener('keydown',e=>{if(['Escape','ArrowDown','ArrowUp','PageDown','PageUp','Home','End',' '].includes(e.key))cancelHomeJourney();});
$('#begin-journey').addEventListener('click',e=>{
  e.preventDefault();const to=$('#buoy').offsetTop-Math.min(80,innerHeight*.15);
  if(paused){window.scrollTo({top:to,behavior:'instant'});return;}
  homeJourney={from:scrollY,to,elapsed:0};
});
function measure(){offsets=sections.map(s=>s.offsetTop);}
measure();window.addEventListener('resize',measure);document.fonts.ready.then(measure);
const layoutObserver=new ResizeObserver(measure);sections.forEach(s=>layoutObserver.observe(s));
function scrollState(){
  const y=scrollY+innerHeight*.18;let chapter=0;
  for(let i=0;i<offsets.length;i++)if(y>=offsets[i])chapter=i;
  const span=(offsets[chapter+1]??offsets[chapter]+innerHeight)-offsets[chapter];
  const fraction=Math.max(0,Math.min(1,(y-offsets[chapter])/span));
  return {chapter,progress:Math.min(9,chapter+fraction)};
}
function setChapter(chapter){active=chapter;sections.forEach((s,i)=>s.classList.toggle('is-active',i===chapter));[...nav.children].forEach((a,i)=>{if(i===chapter)a.setAttribute('aria-current','step');else a.removeAttribute('aria-current');});$('#chapter-number').textContent=`${String(chapter+1).padStart(2,'0')} / 10`;$('#chapter-name').textContent=chapters[chapter];$('#coordinate-top').textContent=chapter<4?'OFFSHORE / OBSERVATION NODE':chapter<9?'ON SHORE / BAY STATION':'BUOY TO SHORE / CONNECTED';}
setChapter(0);
let raf;
function frame(now){
  raf=requestAnimationFrame(frame);if(now-last<33)return;
  const dt=Math.min(.06,(now-last)/1000);last=now;if(document.hidden)return;
  if(homeJourney){
    if(paused)homeJourney=null;
    else{homeJourney.elapsed+=dt;const t=Math.min(1,homeJourney.elapsed/5.2);window.scrollTo({top:homeJourney.from+(homeJourney.to-homeJourney.from)*smooth(t),behavior:'instant'});if(t===1){homeJourney=null;window.history.replaceState(null,'','#buoy');}}
  }
  const moving=!paused;if(moving)elapsed+=dt;
  const state=scrollState();if(inspecting&&state.chapter!==1&&state.chapter!==2)endInspection(false);if(state.chapter!==active)setChapter(state.chapter);
  const homeProgress=Math.max(0,Math.min(1,scrollY/Math.max(1,offsets[1]-innerHeight*.18)));
  home.style.setProperty('--home-progress',String(homeProgress));home.classList.toggle('home-departed',homeProgress>.52);
  $('#home-shot-label').textContent=homeProgress<.25?'01 / THE OCEAN':homeProgress<.55?'02 / DISCOVERY':homeProgress<.82?'03 / APPROACH':'04 / LISTEN';
  $('#journey-progress').style.width=`${Math.min(100,scrollY/Math.max(1,document.documentElement.scrollHeight-innerHeight)*100)}%`;
  world?.update({...state,time:elapsed,dt,moving,pointer,selected,linkOnline:link.online,homeProgress});
  if(moving&&active===6)drawPressure(elapsed);
  if(active===7&&moving)drawPrediction(dt);
  if(moving&&active>=3&&active<=5&&elapsed-lastPacket>1.5){lastPacket=elapsed;link=tickLink(link,new Date().toISOString());updateLink();}
}
raf=requestAnimationFrame(frame);
// 3D is a separate local chunk. All HTML diagrams and controls work if WebGL fails.
import('./world.js').then(async({createWorld})=>{world=await createWorld($('#world'),{onPick:pick,onInspectionReady:inspectionReady,onStatus:text=>{$('#model-state').textContent=text;}});}).catch(()=>{$('#model-state').textContent='3D unavailable · reload or continue the accessible diagrams';document.body.classList.add('webgl-unavailable');});
window.addEventListener('pagehide',e=>{if(!e.persisted){cancelAnimationFrame(raf);world?.dispose();layoutObserver.disconnect();}});
