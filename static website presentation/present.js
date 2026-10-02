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
  {n:'00',name:'The Ocean',plain:'The ocean we are here to listen to.'},
  {n:'01',name:'FALCON Buoy',plain:'Our floating sensing buoy.'},
  {n:'02',name:'Signals',plain:'Pressure and wind, measured at sea.'},
  {n:'03',name:'ESP32',plain:'The controller turns the readings into one clear frame.'},
  {n:'04',name:'LoRa',plain:'A long-range radio carries the frame to shore.'},
  {n:'05',name:'Bay Station',plain:'The shore computer stores, processes, and prepares the data.'},
  {n:'06',name:'Wave Estimate',plain:'Pressure in — estimated wave height out.'},
  {n:'07',name:'AI Prediction',plain:'A research target: the next ten minutes.'},
  {n:'08',name:'Dashboard',plain:'One clear picture for the people who use it.'},
  {n:'09',name:'One System',plain:'Buoy to insight, connected end to end.'}
];

const scenes=[...document.querySelectorAll('main .scene')];
const presenterBtn=document.getElementById('p-presenter');

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
  All readings shown are simulated. Nothing here is a live measurement.</p>`;
document.body.append(jump);

jump.addEventListener('click',e=>{
  const btn=e.target.closest('[data-jump]');
  if(!btn)return;
  const target=scenes[Number(btn.dataset.jump)];
  if(target)target.scrollIntoView({behavior:'smooth',block:'start'});
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
   The page already uses Escape, the arrow keys, Page Up/Down, Home, End,
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
