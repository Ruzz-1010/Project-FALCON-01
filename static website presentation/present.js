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

import {chapters} from './story.js';

/* The chapter list is generated from story.js instead of being typed out here.
   It used to be a hand-written copy, and when the wrap-up was merged from 18
   pages to 15 the copy was left behind: the list showed 18 rows, named the
   merged chapters after pages that no longer existed, and its last three
   buttons pointed at scenes that were not there. Deriving it means the
   presenter's list cannot disagree with the deck again.

   Only the plain-language line is presenter-only copy, one per chapter. */
const PLAIN=[
  'Title cover (team + school) then the problem: affordable coastal data is hard to get.',
  'Six objectives for a Phase 1 prototype — serviceable, calibrated, evaluated.',
  'The floating sensing buoy, and what lives on it and what does not.',
  'Pressure and wind are primary; GPS, power and security support them.',
  'The controller turns the readings into one clear frame.',
  'A long-range radio carries the frame to shore. No cellular on the buoy.',
  'The shore computer stores, processes, and prepares the data.',
  'Pressure in — estimated wave height out. Calibration still required.',
  'Four plain steps: data source, trend, safety caps, judged vs "no change". A trend line today, not a trained model.',
  'Live edge dashboard on stage — needs the edge service running. Security states must not false-alarm.',
  'The tests each number has to pass before it is called accurate — plus what is built and what is not.',
  'What this prototype does not do, what the known risks are, and how each is handled.',
  'Five funded bootcamp gates over five months, and who owns each one.',
  'Who the pilot serves, and the preliminary peso request.',
  'Next steps, the team and the closing statement. Closes with a looping animated signal journey, buoy to shore.',
  'The whole system in one looping 3D flight, buoy to Bay Station interior. The animation page.'
];
const CHAPTERS=chapters.map((name,i)=>({n:String(i).padStart(2,'0'),name,plain:PLAIN[i]??''}));

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
