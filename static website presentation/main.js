import logoUrl from '../dashboard-next/public/falcon-logo.jpg?url';
import {inspections} from './inspection.js';
import {smooth} from './home.js';
import {instrumentInfo} from './instrument.js';
import {createAcquisition} from './acquisition.js';
import {createController} from './controller.js';
import {baySteps,bayPipeline,arrivalPhase} from './bay-story.js';
import {createWaveEstimation} from './wave-estimation.js';
import {chapters,components,createLink,setLink,tickLink,waveSamples,forecastSamples,linePath} from './story.js';

const $=selector=>document.querySelector(selector);
const acquisition=createAcquisition($('#acquisition-dock'));
const controllerOutput=document.createElement('p');controllerOutput.className='controller-output';$('#controller .packet-console').append(controllerOutput);
const controller=createController($('#controller .chip-stage'));
const waveEstimation=createWaveEstimation($('#waves'));
$('#logo').src=logoUrl;
const sections=[...document.querySelectorAll('.scene')];
const reduced=matchMedia('(prefers-reduced-motion: reduce)');
let paused=reduced.matches,active=0,selected='pressure',world,elapsed=0,last=0,lastPacket=0,process=0,predicting=false,predictionProgress=0,currentTab='overview';
let link=createLink();
let bayInspecting=false,bayTrigger;
function openBay(id='station'){
  if(!world?.inspectBay?.(id)){ $('#open-bay').textContent='3D unavailable — reload to inspect';return; }
  bayTrigger=document.activeElement;bayInspecting=true;document.body.classList.add('bay-inspecting');
  $('#bay-panel').hidden=false;const info=baySteps[id==='validate'?'computer':id];$('#bay-title').textContent=info.title;$('#bay-detail').textContent=info.detail;$('#bay-note').textContent=info.note;
  const displayId=id==='station'?'01':String(bayPipeline.indexOf(id)+2).padStart(2,'0');
  const isPhysical=id==='station'||id==='rx'||id==='dashboard';
  $('#bay-step-index').textContent=displayId;$('#bay-step-kind').textContent=isPhysical?'PHYSICAL':'SOFTWARE';
  $('#bay-menu [data-bay="validate"]').textContent='Bay Station computer';
  $('#bay-panel-menu').append($('#bay-menu'));$('#bay-explanation').hidden=false;
  $('#bay-path-current').textContent=({station:'RECEIVE → PROCESS → INSIGHT',rx:'RECEIVE',validate:'AUTHENTICATE / VALIDATE',sqlite:'STORE',processing:'PROCESS',ai:'PREDICT',dashboard:'DISPLAY'})[id]||'RECEIVE';
  document.querySelectorAll('[data-bay]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.bay===id)));
}
function closeBay(restore=true){
  if(!bayInspecting)return;bayInspecting=false;document.body.classList.remove('bay-inspecting');$('#bay-panel').hidden=true;$('#bay-menu-home').append($('#bay-menu'));world?.returnToBay?.();
  $('#bay-menu [data-bay="validate"]').textContent=baySteps.validate.title;
  $('#bay-path-current').textContent='RECEIVE';
  if(restore&&bayTrigger?.isConnected)bayTrigger.focus({preventScroll:true});
}
for(const id of bayPipeline){const b=document.createElement('button');b.dataset.bay=id;b.textContent=({rx:'LoRa receiver',validate:'Bay Station computer',sqlite:'Local storage',processing:'Processing',ai:'AI prediction',dashboard:'Dashboard / alerts'})[id]||baySteps[id].title;b.setAttribute('aria-pressed','false');b.addEventListener('click',()=>openBay(id));$('#bay-menu').append(b);}
$('#open-bay').addEventListener('click',()=>openBay());$('#close-bay').addEventListener('click',()=>closeBay());
document.addEventListener('keydown',e=>{if(e.key==='Escape')closeBay();});
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
  document.body.classList.remove('inspecting','inspection-ready','instrument-inspection');$('#inspection-panel').hidden=true;
  acquisition.place();
  world?.returnToBuoy?.();
  if(restoreFocus&&inspectionTrigger?.isConnected)inspectionTrigger.focus({preventScroll:true});
}
$('#inspection-back').addEventListener('click',()=>endInspection());
document.addEventListener('keydown',e=>{if(e.key==='Escape')endInspection();});
function pick(id,inspect=true){
  acquisition.select(id);
  selected=id;$('#component-title').textContent=components[id].label;$('#component-detail').textContent=components[id].detail;
  document.querySelectorAll('[data-component]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.component===id)));
  if(inspect){
    if(!world?.inspect?.(id)){ $('#model-state').textContent='Component guide available; wait for the original 3D model to load before inspection.';return; }
    inspectionTrigger=document.activeElement;inspecting=true;
    const info=active===1?instrumentInfo[id]:inspections[id];
    document.body.classList.toggle('instrument-inspection',active===1);
    $('#inspection-back').textContent=active===1?'← Return to buoy':'← Back to buoy';
    $('#inspection-title').textContent=info.name;$('#inspection-function').textContent=info.function;
    $('#inspection-data').replaceChildren(...info.data.map(text=>{const li=document.createElement('li');li.textContent=text;return li;}));
    $('#inspection-flow').replaceChildren(...info.flow.map(text=>{const span=document.createElement('span');span.textContent=text;return span;}));
    $('#inspection-status').textContent=info.status;$('#inspection-note').textContent=info.note;
    acquisition.place(active===2?$('#inspection-content'):null);
    $('#inspection-panel').hidden=false;$('#inspection-content').hidden=true;$('#inspection-travel').hidden=false;
    document.body.classList.add('inspecting');document.body.classList.remove('inspection-ready');
  }
}
for(const [id,c] of Object.entries(components)){
  for(const container of [$('#reveal-picks'),$('#sensor-menu')]){
    const b=document.createElement('button');b.textContent=c.label;b.dataset.component=id;b.dataset.index=String(Object.keys(components).indexOf(id)+1).padStart(2,'0');b.setAttribute('aria-pressed',String(id===selected));b.addEventListener('click',()=>pick(id));container.append(b);
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
  $('#link-status').textContent=link.online?(link.buffer.length?'REPLAYING ORIGINAL TIMESTAMPS':'SIMULATED LINK AVAILABLE'):'BUOY STILL SENSING · SHORE DATA STALE';
  $('#link-state').textContent=link.online?'ONLINE':'INTERRUPTED';
  $('#queued').textContent=String(link.buffer.length).padStart(2,'0');$('#received').textContent=String(link.received.length).padStart(2,'0');$('#received-copy').textContent=String(link.received.length).padStart(2,'0');
  $('#packet-seq').textContent=String(link.sequence||42).padStart(4,'0');
  $('#buffer-packets').replaceChildren(...link.buffer.slice(-10).map(p=>{const i=document.createElement('i');i.textContent=String(p.id).padStart(3,'0');i.title=`Original sample: ${p.timestamp}`;return i;}));
  $('#recovery-note').textContent=link.phase==='buffering'?'Sample times stay with queued packets. This is a simulated buffer—not proof of field recovery.':link.phase==='retransmitting'?'Backlog replay → duplicate prevention → chronological storage. Original sample times preserved.':'Hardware, legal band and site coverage pending. No range guarantee.';
  // Page 03 owns its illustrative frame; link simulation on 04–05 remains separate.
}
$('#interrupt').addEventListener('click',()=>{
  link=setLink(link,!link.online);
  // Always demonstrate an immediate state change, even with reduced motion enabled.
  link=tickLink(link,new Date().toISOString());updateLink();renderDashboard();
  if(!link.online){predicting=false;predictionProgress=0;$('#future-reveal').setAttribute('width','0');$('#prediction-status').textContent='UNAVAILABLE: shore input is stale while LoRa is interrupted.';}
});
updateLink();

$('#history-trace').setAttribute('d',linePath(history,45,585,190,140));$('#future-trace').setAttribute('d',linePath(future,630,340,190,140));$('#baseline-trace').setAttribute('d',linePath([history.at(-1),history.at(-1)],630,340,190,140));
$('#predict').addEventListener('click',()=>{if(!link.online){$('#prediction-status').textContent='UNAVAILABLE: restore LoRa before running a new prediction.';return;}predicting=true;predictionProgress=paused?1:0;$('#prediction-status').textContent='SIMULATED: extending a candidate trace against persistence.';if(paused)drawPrediction(0);});
function drawPrediction(dt){if(!predicting)return;predictionProgress=Math.min(1,predictionProgress+dt*.32);$('#future-reveal').setAttribute('width',String(predictionProgress*350));if(predictionProgress===1){predicting=false;$('#prediction-status').textContent='Illustrative AI trace vs. persistence. No accuracy claim.';}}

function overviewMarkup(){const stale=!link.online;return `<div class="demo-overview"><div><div class="demo-readings"><span>Estimated wave height<strong>${stale?'—':history.at(-1).toFixed(2)+' <small>m</small>'}</strong></span><span>Prediction · next 10 min<strong>${stale?'—':future.at(-1).toFixed(2)+' <small>m</small>'}</strong></span></div><svg class="demo-chart" viewBox="0 0 700 170" role="img" aria-label="Simulated estimated wave height and illustrative AI trace"><path class="chart-grid" d="M0 30H700 M0 85H700 M0 140H700"/>${stale?'<text x="210" y="85">STALE · waiting for packets</text>':`<path class="estimated-trace" d="${linePath(history,0,480,150,150)}"/><path class="future-trace" d="${linePath(future,480,210,150,150)}"/>`}</svg></div><dl class="demo-summary"><div><dt>Station</dt><dd>${stale?'STALE':'Simulation'}</dd></div><div><dt>LoRa</dt><dd>${stale?'Offline':'Receiving'}</dd></div><div><dt>Wind</dt><dd>${stale?'—':'11 km/h NE'}</dd></div><div><dt>Battery</dt><dd>${stale?'—':'78% demo'}</dd></div><div><dt>Security</dt><dd>${stale?'Unknown':'Secure demo'}</dd></div></dl></div>`;}
function renderDashboard(){
  const host=$('#dashboard-content');
  if(currentTab==='overview')host.innerHTML=overviewMarkup();
  if(currentTab==='motion')host.innerHTML='<div class="demo-motion"><svg viewBox="0 0 160 200" aria-label="Illustrative heave indicator, not a replacement buoy model" role="img"><path d="M10 125Q40 113 80 125T150 125" fill="none" stroke="#448591"/><g class="motion-outline"><path d="M80 40V100M70 50L80 40 90 50M70 90L80 100 90 90" fill="none" stroke="#357889" stroke-width="2"/><circle cx="80" cy="125" r="9" fill="#397d8a"/></g><text x="80" y="175" text-anchor="middle">HEAVE / DEMO</text></svg><p><strong>Buoy Motion</strong><br>A pressure-informed illustration—not measured roll or pitch.<br>The original CAD stays the physical reference.<br><a href="#buoy">Return to the buoy ↗</a></p></div>';
  if(currentTab==='sensors')host.innerHTML=`<table class="sensor-table"><thead><tr><th>Observation</th><th>Role</th><th>Status</th></tr></thead><tbody><tr><td>Pressure</td><td>Wave processing input</td><td>${link.online?'Calibration pending':'Stale'}</td></tr><tr><td>Wind</td><td>Primary measurement</td><td>Simulated</td></tr><tr><td>GPS</td><td>Supporting telemetry</td><td>Simulated</td></tr><tr><td>Battery / solar</td><td>Energy monitoring</td><td>Simulated</td></tr><tr><td>Enclosure</td><td>Health / security</td><td>Simulated</td></tr></tbody></table>`;
  if(currentTab==='logs')host.innerHTML=`<div class="demo-log"><time>SIM</time><span>${link.online?'Shore link available.':'LoRa interrupted. Buoy packets buffered.'}</span></div><div class="demo-log"><time>SIM</time><span>${link.buffer.length} packets queued · ${link.received.length} accepted without duplicate IDs.</span></div><div class="demo-log"><time>NOTE</time><span>Calibration and controlled deployment validation remain pending.</span></div><p class="demo-note">Presentation events only. No hardware, alarm or database connection.</p>`;
}
document.querySelectorAll('[data-tab]').forEach(b=>b.addEventListener('click',()=>{currentTab=b.dataset.tab;document.querySelectorAll('[data-tab]').forEach(el=>el.setAttribute('aria-pressed',String(el===b)));renderDashboard();}));renderDashboard();

let offsets=[];
let homeJourney=null;
const home=$('#ocean');
let homeOrbitActive=false;
function setHomeOrbit(enabled){
  if(enabled&&!world?.setHomeOrbit?.(true)){$('#home-orbit-status').textContent='The original CAD is still loading or 3D is unavailable.';return;}
  if(!enabled)world?.setHomeOrbit?.(false);
  homeOrbitActive=enabled;homeJourney=null;document.body.classList.toggle('home-orbit',enabled);
  $('#explore-home').hidden=enabled;$('#explore-home').setAttribute('aria-pressed',String(enabled));
  $('#reset-home').hidden=!enabled;$('#home-orbit-help').hidden=!enabled;$('#home-orbit-status').textContent='';
  if(enabled)$('#reset-home').focus({preventScroll:true});
}
$('#explore-home').addEventListener('click',()=>setHomeOrbit(true));
$('#reset-home').addEventListener('click',()=>{setHomeOrbit(false);$('#explore-home').focus({preventScroll:true});});
window.addEventListener('keydown',e=>{
  if(!homeOrbitActive)return;
  if(e.key==='Escape'){setHomeOrbit(false);$('#explore-home').focus({preventScroll:true});return;}
  const steps={ArrowLeft:[-20,0],ArrowRight:[20,0],ArrowUp:[0,-20],ArrowDown:[0,20],'+':[0,0,-80],'-':[0,0,80]};
  if(steps[e.key]){e.preventDefault();world?.moveHomeOrbit?.(...steps[e.key]);}
});
const cancelHomeJourney=()=>{homeJourney=null;};
for(const event of ['wheel','touchstart','pointerdown'])window.addEventListener(event,cancelHomeJourney,{passive:true});
window.addEventListener('keydown',e=>{if(['Escape','ArrowDown','ArrowUp','PageDown','PageUp','Home','End',' '].includes(e.key))cancelHomeJourney();});
$('#begin-journey').addEventListener('click',e=>{
  if(homeOrbitActive)setHomeOrbit(false);
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
function setChapter(chapter){active=chapter;document.body.dataset.experience=chapter<3?String(chapter):'later';sections.forEach((s,i)=>s.classList.toggle('is-active',i===chapter));[...nav.children].forEach((a,i)=>{if(i===chapter)a.setAttribute('aria-current','step');else a.removeAttribute('aria-current');});$('#chapter-number').textContent=`${String(chapter+1).padStart(2,'0')} / 10`;$('#chapter-name').textContent=chapters[chapter];$('#coordinate-top').textContent=chapter<4?'OFFSHORE / OBSERVATION NODE':chapter<9?'ON SHORE / BAY STATION':'BUOY TO SHORE / CONNECTED';}
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
  const state=scrollState();if(inspecting&&state.chapter!==active)endInspection(false);if(state.chapter!==active)setChapter(state.chapter);
  if(homeOrbitActive&&state.chapter!==0)setHomeOrbit(false);
  if(bayInspecting&&state.chapter!==5)closeBay(false);
  const homeProgress=Math.max(0,Math.min(1,scrollY/Math.max(1,offsets[1]-innerHeight*.18)));
  home.style.setProperty('--home-progress',String(homeProgress));home.classList.toggle('home-departed',homeProgress>.52);
  $('#home-shot-label').textContent=homeProgress<.25?'01 / THE OCEAN':homeProgress<.55?'02 / DISCOVERY':homeProgress<.82?'03 / APPROACH':'04 / LISTEN';
  $('#journey-progress').style.width=`${Math.min(100,scrollY/Math.max(1,document.documentElement.scrollHeight-innerHeight)*100)}%`;
  world?.update({...state,time:elapsed,dt,moving,pointer,selected,linkOnline:link.online,homeProgress});
  if(active===2&&moving)acquisition.draw(elapsed);
  if(active===3)controller.draw(elapsed);
  if(active===5){const s=arrivalPhase(elapsed,link.online);document.querySelectorAll('[data-bay]').forEach((b,i)=>b.classList.toggle('receiving-stage',i===s.stage));}
  if(active===6)waveEstimation.update(elapsed,dt,state.progress-6,moving);
  if(active===7&&moving)drawPrediction(dt);
  if(moving&&active>=3&&active<=5&&elapsed-lastPacket>1.5){lastPacket=elapsed;link=tickLink(link,new Date().toISOString());updateLink();}
}
raf=requestAnimationFrame(frame);
// 3D is a separate local chunk. All HTML diagrams and controls work if WebGL fails.
import('./world.js').then(async({createWorld})=>{world=await createWorld($('#world'),{onPick:pick,onInspectionReady:inspectionReady,onBayPick:openBay,onBayReady:()=>{if(bayInspecting){$('#bay-explanation').hidden=false;$('#bay-title').focus({preventScroll:true});}},onStatus:text=>{$('#model-state').textContent=text;}});}).catch(()=>{$('#model-state').textContent='3D unavailable · reload or continue the accessible diagrams';document.body.classList.add('webgl-unavailable');});
window.addEventListener('pagehide',e=>{if(!e.persisted){cancelAnimationFrame(raf);world?.dispose();layoutObserver.disconnect();}});
