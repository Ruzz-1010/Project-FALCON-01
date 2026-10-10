import logoUrl from '../data/falcon-logo.jpg?url';
import {inspections} from './inspection.js';
import {smooth} from './home.js';
import {instrumentInfo} from './instrument.js';
import {createAcquisition} from './acquisition.js';
import {createController} from './controller.js';
import {baySteps,bayPipeline,arrivalPhase} from './bay-story.js';
import {createWaveEstimation} from './wave-estimation.js';
import {chapters,CH,chapterCount,components,createLink,setLink,tickLink} from './story.js';
import {buildDostDeck} from './dost-deck.js';

const $=selector=>document.querySelector(selector);
// The DOST wrap-up chapters (12 Roadmap & Team, 13 Impact & Funding) are static
// markup, so they are populated once at load rather than every frame. This adds
// no 3D work and no animation loop.
buildDostDeck();
const acquisition=createAcquisition($('#acquisition-dock'));
const controllerOutput=document.createElement('p');controllerOutput.className='controller-output';$('#controller .packet-console').append(controllerOutput);
const controller=createController($('#controller .chip-stage'));
const waveEstimation=createWaveEstimation($('#waves'));
$('#logo').src=logoUrl;
const sections=[...document.querySelectorAll('.scene')];
// Nodes the render loop touches every frame, resolved once. Querying these
// inside the loop is what made scrolling feel heavy.
const chapterNumber=$('#chapter-number'),chapterTitle=$('#chapter-name'),coordinateTop=$('#coordinate-top');
const journeyProgress=$('#journey-progress'),homeShotLabel=$('#home-shot-label');
const reduced=matchMedia('(prefers-reduced-motion: reduce)');
let paused=reduced.matches,active=0,selected='pressure',world,elapsed=0,last=0,lastPacket=0,process=0;
let link=createLink();
let bayInspecting=false,bayTrigger;
function openBay(id='station'){
  if(!world?.inspectBay?.(id)){ $('#open-bay').textContent='3D unavailable — reload to inspect';return; }
  bayTrigger=document.activeElement;bayInspecting=true;document.body.classList.add('bay-inspecting');
  $('#bay-panel').hidden=id==='station';
  const info=baySteps[id==='validate'?'computer':id];
  $('#bay-title').textContent=info.title;
  $('#bay-detail').textContent=info.detail;
  $('#bay-note').textContent='Illustrative only. Final layout pending.';
  $('#bay-step-index').textContent=id==='station'?'01':'02';
  $('#bay-step-kind').textContent='SYSTEM';
  $('#bay-panel-menu').replaceChildren();
  $('#bay-explanation').hidden=false;
  $('#bay-path-current').textContent='RECEIVE → PROCESS → INSIGHT';
  document.querySelectorAll('[data-bay]').forEach(b=>b.setAttribute('aria-pressed','false'));
}
function closeBay(restore=true){
  if(!bayInspecting)return;bayInspecting=false;document.body.classList.remove('bay-inspecting');$('#bay-panel').hidden=true;$('#bay-menu-home').append($('#bay-menu'));world?.returnToBay?.();
  $('#bay-menu [data-bay="validate"]').textContent=baySteps.validate.title;
  $('#bay-path-current').textContent='RECEIVE';
  if(restore&&bayTrigger?.isConnected)bayTrigger.focus({preventScroll:true});
}
const bayButtons=[];
for(const id of bayPipeline){const b=document.createElement('button');b.dataset.bay=id;b.textContent=({rx:'LoRa receiver',validate:'Bay Station computer',sqlite:'Local storage',processing:'Processing',ai:'AI prediction',dashboard:'Dashboard / alerts'})[id]||baySteps[id].title;b.setAttribute('aria-pressed','false');b.addEventListener('click',()=>openBay(id));$('#bay-menu').append(b);bayButtons.push(b);}
$('#open-bay').addEventListener('click',()=>openBay());$('#close-bay').addEventListener('click',()=>closeBay());
document.addEventListener('keydown',e=>{if(e.key==='Escape')closeBay();});
const pointer={x:0,y:0};
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
    if(!world?.inspect?.(id) && id !== 'lora'){ $('#model-state').textContent='Component guide available; wait for the original 3D model to load before inspection.';return; }
    inspectionTrigger=document.activeElement;inspecting=true;
    const info=active===CH.objectives?instrumentInfo[id]:inspections[id];
    document.body.classList.toggle('instrument-inspection',active===CH.objectives);
    $('#inspection-back').textContent=active===CH.objectives?'← Return to buoy':'← Back to buoy';
    $('#inspection-title').textContent=info.name;$('#inspection-function').textContent=info.function;
    $('#inspection-how').textContent=info.how||info.function;
    $('#inspection-acquire').textContent=info.acquire||info.data.join(' · ');
    const specsEl=$('#inspection-specs');const specs=info.specs||[];
    specsEl.replaceChildren(...specs.map(text=>{const li=document.createElement('li');li.textContent=text;return li;}));
    specsEl.closest('details').hidden=specs.length===0;
    $('#inspection-data').replaceChildren(...info.data.map(text=>{const li=document.createElement('li');li.textContent=text;return li;}));
    $('#inspection-flow').replaceChildren(...info.flow.map(text=>{const span=document.createElement('span');span.textContent=text;return span;}));
    $('#inspection-status').textContent=info.status;$('#inspection-note').textContent=info.note;
    acquisition.place(active===CH.buoy?$('#inspection-content'):null);
    $('#inspection-panel').hidden=false;$('#inspection-content').hidden=true;$('#inspection-travel').hidden=false;
    document.body.classList.add('inspecting');document.body.classList.remove('inspection-ready');
  }
}
for(const [id,c] of Object.entries(components)){
  for(const container of [$('#reveal-picks'),$('#sensor-menu')]){
    const b=document.createElement('button');b.textContent=c.label;b.dataset.component=id;b.dataset.index=String(Object.keys(components).indexOf(id)+1).padStart(2,'0');b.setAttribute('aria-pressed',String(id===selected));b.addEventListener('click',()=>pick(id, container.id!=='sensor-menu'));container.append(b);
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
  link=tickLink(link,new Date().toISOString());updateLink();
});
updateLink();

/* --- 09 LIVE EDGE DASHBOARD -------------------------------------------
   Chapter 09 embeds the real edge service (dashboard-next build) instead of
   a mock. The iframe src is set from JS so the static build stays free of
   hard-coded hosts; `?edge=http://host:8765` points at another machine.
   No fetch/XHR here: iframe load = online, 6s silence = offline fallback.
   The static snapshot inside #edge-fallback keeps the chapter useful when
   the service is not running. */
const edgeBase=(new URLSearchParams(location.search).get('edge')||'http://127.0.0.1:8765').replace(/\/+$/,'');
const edgeFrame=$('#edge-frame'),edgeDot=$('#edge-dot'),edgeStatus=$('#edge-status'),edgeFallback=$('#edge-fallback'),edgeOpen=$('#edge-open');
let edgeResolved=false,edgeTimer=0;
function setEdgeChecking(){if(!edgeFrame)return;edgeResolved=false;edgeDot.className='edge-dot';edgeStatus.textContent=`Connecting to the edge service at ${edgeBase}…`;edgeFrame.hidden=false;edgeFallback.hidden=true;}
function setEdgeOnline(){if(!edgeFrame||edgeResolved)return;edgeResolved=true;window.clearTimeout(edgeTimer);edgeDot.className='edge-dot online';edgeStatus.textContent=`EDGE ONLINE · live dashboard from ${edgeBase}`;edgeFrame.hidden=false;edgeFallback.hidden=true;}
function setEdgeOffline(){if(!edgeFrame||edgeResolved)return;edgeResolved=true;edgeDot.className='edge-dot offline';edgeStatus.textContent=`EDGE OFFLINE · start the edge service, then press Retry`;edgeFrame.hidden=true;edgeFallback.hidden=false;}
function loadEdge(){if(!edgeFrame)return;setEdgeChecking();window.clearTimeout(edgeTimer);edgeFrame.src=`${edgeBase}/`;edgeTimer=window.setTimeout(setEdgeOffline,6000);}
if(edgeFrame){edgeOpen.href=`${edgeBase}/`;edgeFrame.addEventListener('load',setEdgeOnline);$('#edge-retry').addEventListener('click',loadEdge);loadEdge();}

let offsets=[],scrollRange=1,coverH=0;
const home=$('#ocean');
let homeOrbitActive=false;
function setHomeOrbit(enabled){
  if(enabled&&!world?.setHomeOrbit?.(true)){$('#home-orbit-status').textContent='The original CAD is still loading or 3D is unavailable.';return;}
  if(!enabled)world?.setHomeOrbit?.(false);
  homeOrbitActive=enabled;cancelScrollTween();document.body.classList.toggle('home-orbit',enabled);
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
/* ---------------------------------------------------------------------------
   ONE SCROLL ENGINE
   Everything that moves the page — the opening journey, the chapter ladder,
   the Next/Previous controls, the keyboard and the presenter jump list — runs
   through a single eased tween instead of the browser's own smooth scrolling.
   That matters for three reasons:
     - the easing curve is the same smootherstep the 3D camera uses, so the
       words and the water arrive together instead of a beat apart;
     - the duration scales with distance, so one chapter and five chapters
       both feel deliberate rather than one feeling like a lurch;
     - reduced motion and the Pause-motion control get an instant, honest
       jump instead of a half-finished animation.
   Any wheel, touch or pointer input cancels the tween, so the reader is never
   fighting the page for control of the scroll position.
   --------------------------------------------------------------------------- */
let scrollTween=null;
const scrollCeiling=()=>Math.max(1,document.documentElement.scrollHeight-innerHeight);
function cancelScrollTween(){scrollTween=null;}
/** Ease toward a scroll position. `label` is only used for the address bar. */
function glideTo(top,{minSeconds=.55,maxSeconds=1.35,label=null}={}){
  cancelScrollTween();
  const to=Math.max(0,Math.min(top,scrollCeiling()));
  const distance=Math.abs(to-scrollY);
  if(paused||distance<4){window.scrollTo({top:to,behavior:'instant'});if(label)window.history.replaceState(null,'',`#${label}`);return;}
  scrollTween={from:scrollY,to,elapsed:0,duration:Math.min(maxSeconds,Math.max(minSeconds,distance/(innerHeight*1.45))),label};
}
for(const event of ['wheel','touchstart','pointerdown'])window.addEventListener(event,cancelScrollTween,{passive:true});
window.addEventListener('keydown',e=>{if(['Escape','ArrowDown','ArrowUp','PageDown','PageUp','Home','End',' '].includes(e.key))cancelScrollTween();});
$('#begin-journey').addEventListener('click',e=>{
  if(homeOrbitActive)setHomeOrbit(false);
  e.preventDefault();glideTo(offsets[CH.objectives]-Math.min(80,innerHeight*.15),{label:sections[CH.objectives].id});
});
// Cover card (chapter 00, first screen): title + team, then glide one screen
// down to the hero. Uses the same eased engine as every other move.
$('#cover-start').addEventListener('click',()=>{
  if(homeOrbitActive)setHomeOrbit(false);
  const cover=$('#ocean .cover-stage');
  glideTo(cover?cover.offsetHeight:innerHeight,{});
});
function measure(){offsets=sections.map(s=>s.offsetTop);scrollRange=scrollCeiling();coverH=document.querySelector('#ocean .cover-stage')?.offsetHeight??0;}
measure();window.addEventListener('resize',measure);document.fonts.ready.then(measure);
const layoutObserver=new ResizeObserver(measure);sections.forEach(s=>layoutObserver.observe(s));

/* --- CHAPTER PAGING ------------------------------------------------------
   The audience needs one obvious way forward. These are the controls, and
   every other entry point (ladder, keys, presenter list) calls the same two
   functions, so they can never disagree about where "next" is. */
const chapterTop=i=>Math.max(0,offsets[Math.max(0,Math.min(sections.length-1,i))]-(i?Math.min(80,innerHeight*.15):0));
function goToChapter(i){
  const index=Math.max(0,Math.min(sections.length-1,i));
  if(inspecting)endInspection(false);
  if(bayInspecting)closeBay(false);
  if(inspecting&&index!==active)endInspection(false);
  if(homeOrbitActive&&index!==0)setHomeOrbit(false);
  // setChapter is driven by scroll position, so announce the destination now
  // and let the tween confirm it. This keeps the ladder in step on long jumps.
  if(index!==active)setChapter(index);
  glideTo(chapterTop(index),{label:sections[index].id});
}
const nextChapter=()=>goToChapter(active>=sections.length-1?0:active+1);
const prevChapter=()=>goToChapter(active<=0?0:active-1);
// 200ms key debounce so a held clicker key never double-jumps chapters.
let lastPageAt=0;
function pagedNext(){const now=performance.now();if(now-lastPageAt<200)return;lastPageAt=now;nextChapter();}
function pagedPrev(){const now=performance.now();if(now-lastPageAt<200)return;lastPageAt=now;prevChapter();}
const nextBtn=$('#chapter-next'),prevBtn=$('#chapter-prev');
if(nextBtn)nextBtn.addEventListener('click',pagedNext);
if(prevBtn)prevBtn.addEventListener('click',pagedPrev);
// Clicking a chapter tick glides there instead of jumping.
nav.addEventListener('click',e=>{const link=e.target.closest('a');if(!link)return;e.preventDefault();goToChapter([...nav.children].indexOf(link));});
// Adviser shortcut rail (side buttons): direct jumps, same engine as paging.
document.querySelectorAll('#adviser-route [data-goto]').forEach(b=>b.addEventListener('click',()=>goToChapter(Number(b.dataset.goto))));
document.addEventListener('keydown',e=>{
  if(e.defaultPrevented||e.metaKey||e.ctrlKey||e.altKey)return;
  const el=e.target;
  if(el&&(el.isContentEditable||['INPUT','TEXTAREA','SELECT'].includes(el.tagName)))return;
  // A panel that owns focus owns the arrow keys: the open inspection panel and
  // the Bay Station cutaway would otherwise be scrolled away mid-look.
  if(document.body.classList.contains('inspecting')||bayInspecting)return;
  // The orbit camera owns the arrow keys while it is open, and Escape still
  // belongs to the inspection panels.
  if(homeOrbitActive)return;
  if(e.key==='ArrowRight'||e.key==='PageDown'){e.preventDefault();pagedNext();}
  else if(e.key==='ArrowLeft'||e.key==='PageUp'){e.preventDefault();pagedPrev();}
  else if(e.key==='Home'){e.preventDefault();goToChapter(0);}
  else if(e.key==='End'){e.preventDefault();goToChapter(sections.length-1);}
  // Space advances, which is what a presenter expects from a clicker. It is
  // left alone when a button or link holds focus, so the keyboard can still
  // operate whatever the panel is currently pointing at.
  else if(e.key===' '&&!el?.closest('button,a[href],summary,details,[role=button]')){e.preventDefault();pagedNext();}
});
window.falcon={goToChapter,nextChapter,prevChapter,isPaused:()=>paused};
function scrollState(){
  const y=scrollY+innerHeight*.18;let chapter=0;
  for(let i=0;i<offsets.length;i++)if(y>=offsets[i])chapter=i;
  const span=(offsets[chapter+1]??offsets[chapter]+innerHeight)-offsets[chapter];
  const fraction=Math.max(0,Math.min(1,(y-offsets[chapter])/span));
  return {chapter,progress:Math.min(chapterCount-1,chapter+fraction)};
}
function setChapter(chapter){
  active=chapter;document.body.dataset.experience=chapter===CH.radio?'radio':(chapter<=CH.sensors?String(chapter):'later');
  sections.forEach((s,i)=>s.classList.toggle('is-active',i===chapter));
  [...nav.children].forEach((a,i)=>{if(i===chapter)a.setAttribute('aria-current','step');else a.removeAttribute('aria-current');});
  document.querySelectorAll('#adviser-route [data-goto]').forEach(b=>{if(Number(b.dataset.goto)===chapter)b.setAttribute('aria-current','true');else b.removeAttribute('aria-current');});
  chapterNumber.textContent=`${String(chapter+1).padStart(2,'0')} / ${chapterCount}`;
  chapterTitle.textContent=chapters[chapter];
  coordinateTop.textContent=chapter<CH.radio?'OFFSHORE / OBSERVATION NODE':chapter<=CH.shore?'ON SHORE / BAY STATION':'BUOY TO SHORE / CONNECTED';
  // The paging controls carry their own labels, so the panel can read the
  // destination out loud instead of only seeing an arrow.
  if(nextBtn){const last=chapter>=sections.length-1;nextBtn.querySelector('span').textContent=last?'Back to the ocean':chapters[chapter+1];nextBtn.setAttribute('aria-label',last?'Return to the first chapter':`Next chapter: ${chapters[chapter+1]}`);}
  if(prevBtn)prevBtn.disabled=chapter===0;
}
setChapter(0);
let raf,lastShot='';
function frame(now){
  raf=requestAnimationFrame(frame);
  // ~60fps. The old 33ms gate capped the whole page at 30fps, which is what
  // made every scroll-driven movement look like it was being dragged.
  if(now-last<16)return;
  const dt=Math.min(.06,(now-last)/1000);last=now;if(document.hidden)return;
  if(scrollTween){
    if(paused)scrollTween=null;
    else{
      scrollTween.elapsed+=dt;
      const t=Math.min(1,scrollTween.elapsed/scrollTween.duration);
      window.scrollTo({top:scrollTween.from+(scrollTween.to-scrollTween.from)*smooth(t),behavior:'instant'});
      if(t===1){const label=scrollTween.label;scrollTween=null;if(label)window.history.replaceState(null,'',`#${label}`);}
    }
  }
  const moving=!paused;if(moving)elapsed+=dt;
  const state=scrollState();if(inspecting&&state.chapter!==active)endInspection(false);if(state.chapter!==active)setChapter(state.chapter);
  if(homeOrbitActive&&state.chapter!==0)setHomeOrbit(false);
  if(bayInspecting&&state.chapter!==CH.shore)closeBay(false);
  // The cover card sits one screen above the hero inside #ocean, so its
  // height is subtracted: progress 0 = hero fully visible, same as before.
  const homeProgress=Math.max(0,Math.min(1,(scrollY-coverH)/Math.max(1,offsets[CH.objectives]-coverH-innerHeight*.18)));
  home.style.setProperty('--home-progress',homeProgress.toFixed(4));
  home.classList.toggle('home-departed',homeProgress>.52);
  const shot=homeProgress<.25?'01 / THE OCEAN':homeProgress<.55?'02 / DISCOVERY':homeProgress<.82?'03 / APPROACH':'04 / LISTEN';
  if(shot!==lastShot){lastShot=shot;homeShotLabel.textContent=shot;}
  journeyProgress.style.width=`${Math.min(100,scrollY/scrollRange*100).toFixed(3)}%`;
  world?.update({progress:state.progress,chapter:state.chapter,time:elapsed,dt,moving,pointer,selected,linkOnline:link.online,homeProgress});
  if(active===CH.buoy&&moving)acquisition.draw(elapsed);
  if(active===CH.controller)controller.draw(elapsed);
  if(active===CH.shore){const s=arrivalPhase(elapsed,link.online);bayButtons.forEach((b,i)=>b.classList.toggle('receiving-stage',i===s.stage));}
  if(active===CH.waves)waveEstimation.update(elapsed,dt,state.progress-CH.waves,moving);
  if(moving&&active>=CH.controller&&active<=CH.radio&&elapsed-lastPacket>1.5){lastPacket=elapsed;link=tickLink(link,new Date().toISOString());updateLink();}
}
raf=requestAnimationFrame(frame);
// 3D is a separate local chunk. All HTML diagrams and controls work if WebGL fails.
import('./world.js').then(async({createWorld})=>{world=await createWorld($('#world'),{onPick:pick,onInspectionReady:inspectionReady,onBayPick:openBay,onBayReady:()=>{if(bayInspecting){$('#bay-explanation').hidden=false;$('#bay-title').focus({preventScroll:true});}},onStatus:text=>{$('#model-state').textContent=text;}});}).catch(()=>{$('#model-state').textContent='3D unavailable · reload or continue the accessible diagrams';document.body.classList.add('webgl-unavailable');});
window.addEventListener('pagehide',e=>{if(!e.persisted){cancelAnimationFrame(raf);world?.dispose();layoutObserver.disconnect();}});
