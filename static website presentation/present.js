/* ============================================================================
   FALCON-01 — PRESENTATION CONTROLS  (present.js)

   Loaded only by present.html. It never touches main.js, the 3D scene, the
   telemetry simulation or any original file. It only adds:

   1. PRESENTER MODE  — header button, or press P.
      Deepens the cinematic framing, hides the little technical readouts and
      enlarges the words so the panel and the back row can follow.

   2. CHAPTER JUMP LIST — press L.
      Every chapter, with one plain-language line saying what happens in it.
      This is the panel-friendly map of the whole presentation.

   3. PROJECTOR MODE — open present.html?big=1
      Bigger text and higher contrast for a weak projector or a bright room.
   ========================================================================== */

const CHAPTERS=[
  {n:'00',name:'The Ocean',plain:'Title plus the problem: affordable coastal data is hard to get.'},
  {n:'01',name:'Objectives',plain:'Six objectives for a Phase 1 prototype — serviceable, calibrated, evaluated.'},
  {n:'02',name:'FALCON buoy',plain:'The floating sensing buoy, and what lives on it and what does not.'},
  {n:'03',name:'Sensors',plain:'Pressure and wind are primary; GPS, power and security support them.'},
  {n:'04',name:'ESP32',plain:'The controller turns the readings into one clear frame.'},
  {n:'05',name:'LoRa link',plain:'A long-range radio carries the frame to shore. No cellular on the buoy.'},
  {n:'06',name:'Bay Station',plain:'The shore computer stores, processes, and prepares the data.'},
  {n:'07',name:'Wave estimate',plain:'Pressure in — estimated wave height out. Calibration still required.'},
  {n:'08',name:'AI prediction',plain:'A research target: 5, 10 and 15 minutes ahead, versus a baseline.'},
  {n:'09',name:'Dashboard and health',plain:'Four pages, plus the security states that must not false-alarm.'},
  {n:'10',name:'Validation',plain:'The tests each number has to pass before it is called accurate.'},
  {n:'11',name:'Current status',plain:'What is built and what is not, before we claim performance.'},
  {n:'12',name:'Scope limits',plain:'What this prototype does not do, and why that is safe.'},
  {n:'13',name:'Risks and next steps',plain:'Known risks, and the work that remains before any claim.'},
  {n:'14',name:'Acknowledgment',plain:'The people and places the project exists because of.'}
];

const scenes=[...document.querySelectorAll('main .scene')];
const presenterBtn=document.getElementById('p-presenter');

/* --- movement --------------------------------------------------------------
   main.js owns one eased scroll engine and publishes it on window.falcon, so
   the jump list glides with exactly the same curve as the on-screen Next
   button. If the 3D chunk failed to load the page still moves, using the
   browser's own smooth scroll. */
const nav=window.falcon;
function goTo(index){
  if(nav?.goToChapter)nav.goToChapter(index);
  else scenes[index]?.scrollIntoView({behavior:'smooth',block:'start'});
}

/* --- projector mode: ?big=1 ------------------------------------------------ */
if(new URLSearchParams(location.search).get('big')==='1'){
  document.body.classList.add('p-big');
}

/* --- presenter mode ------------------------------------------------------- */
function setPresenter(on){
  document.body.classList.toggle('p-presenter',on);
  if(presenterBtn)presenterBtn.setAttribute('aria-pressed',String(on));
}
if(presenterBtn){
  presenterBtn.addEventListener('click',()=>{
    setPresenter(!document.body.classList.contains('p-presenter'));
  });
}

/* --- chapter jump list ---------------------------------------------------- */
const jump=document.createElement('section');
jump.id='p-jump';
jump.hidden=true;
jump.setAttribute('aria-label','Chapter list');
jump.innerHTML=`
  <h2>CHAPTERS</h2>
  <ol>${CHAPTERS.map((c,i)=>`
    <li><button type="button" data-jump="${i}">
      <span><b>${c.n}</b>${c.name}</span>
      <span class="p-jump-plain">${c.plain}</span>
    </button></li>`).join('')}
  </ol>
  <p class="p-jump-foot">Press <b>L</b> to close · <b>P</b> for presenter mode.<br>
  <b>&larr;</b> <b>&rarr;</b> or <b>Space</b> step between chapters.<br>
  All readings shown are simulated. Nothing here is a live measurement.</p>`;
document.body.append(jump);

jump.addEventListener('click',e=>{
  const btn=e.target.closest('[data-jump]');
  if(!btn)return;
  goTo(Number(btn.dataset.jump));
  setJump(false);
});

function setJump(open){
  jump.hidden=!open;
  if(open){
    const first=jump.querySelector('button');
    if(first)first.focus({preventScroll:true});
  }
}

/* Keep the list in step with the chapter the audience is watching. */
const jumpBtns=[...jump.querySelectorAll('[data-jump]')];
const observer=new IntersectionObserver(entries=>{
  for(const entry of entries){
    if(!entry.isIntersecting)continue;
    const index=scenes.indexOf(entry.target);
    jumpBtns.forEach((b,i)=>b.setAttribute('aria-current',String(i===index)));
  }
},{threshold:.45});
scenes.forEach(s=>observer.observe(s));

/* --- the small reminder that the list exists ----------------------------- */
const hint=document.createElement('p');
hint.id='p-hint';
hint.textContent='L CHAPTERS · P PRESENTER MODE';
document.body.append(hint);

/* --- keyboard ------------------------------------------------------------
   main.js already owns Escape, the arrow keys, Page Up/Down, Home, End,
   Space and the + and - keys, so this layer only claims L and P. -------- */
document.addEventListener('keydown',e=>{
  const tag=e.target&&e.target.tagName;
  if(tag==='INPUT'||tag==='TEXTAREA'||tag==='SELECT'||e.target?.isContentEditable)return;
  if(e.metaKey||e.ctrlKey||e.altKey)return;

  if(e.key==='l'||e.key==='L'){
    e.preventDefault();
    setJump(jump.hidden);
    return;
  }
  if(e.key==='p'||e.key==='P'){
    e.preventDefault();
    setPresenter(!document.body.classList.contains('p-presenter'));
    return;
  }
  if(e.key==='Escape'&&!jump.hidden){
    setJump(false);
    if(presenterBtn)presenterBtn.focus({preventScroll:true});
  }
},true);
