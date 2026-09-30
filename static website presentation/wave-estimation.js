const clamp=v=>Math.max(0,Math.min(1,v));
export const stageFromScroll=fraction=>clamp((fraction-.04)/.5)*2;
export const morphStep=(current,target,dt)=>current+(target-current)*(1-Math.exp(-Math.max(0,dt)*5));
export function deviation(values){const mean=values.reduce((a,b)=>a+b,0)/values.length;return Math.sqrt(values.reduce((sum,v)=>sum+(v-mean)**2,0)/values.length);}
export function pressureSequence(time){
  const tide=Array.from({length:160},(_,i)=>.34*Math.sin(i*.024)+.13);
  const raw=tide.map((v,i)=>v+Math.sin(i*.15+time*.35)*.55+Math.sin(i*.37+time*.35)*.13+Math.sin(i*2.5+time*.6)*.055);
  const detrended=raw.map((v,i)=>v-tide[i]);
  const clean=detrended.map((_,i)=>{const window=detrended.slice(Math.max(0,i-2),Math.min(160,i+3));return window.reduce((a,b)=>a+b,0)/window.length;});
  // Unitless surface-response proxy, NOT a calibrated pressure-to-elevation conversion.
  const hs=clean.map((_,i)=>4*deviation(clean.slice(Math.max(0,i-21),Math.min(160,i+22))));
  return {raw,clean,hs,result:4*deviation(clean)};
}
export function morphSignal(samples,stage){
  const t=clamp(stage),u=clamp(stage-1);
  // Shared plotting coordinates permit a continuous scientific morph across units.
  return samples.raw.map((v,i)=>{const wave=v+(samples.clean[i]-v)*t;return wave+((samples.hs[i]-.9)-wave)*u;});
}
export function createWaveEstimation(root){
  let stage=0,manual=null,lastFraction=0,previousLabel=-1;
  const trace=root.querySelector('#raw-trace'),reference=root.querySelector('#processed-trace'),buttons=[...root.querySelectorAll('[data-process]')];
  const descriptions=[
    ['MEASURED QUANTITY','UNDERWATER PRESSURE','Relative pressure · simulated','Small fluctuations ride on a slow background component. These are illustrative samples, not live measurements.'],
    ['PROCESSED','WAVE-BAND SIGNAL','Relative pressure · simulated','Quality check → static/tidal removal → filtering. The same pressure record becomes a cleaner wave-band signal.'],
    ['DERIVED','ESTIMATED SIGNIFICANT WAVE HEIGHT (Hs)','Relative demonstration · not metres','A wave statistic is derived from a surface-response proxy. Depth response and calibration must be established before reporting physical Hs.']
  ];
  const path=values=>values.map((v,i)=>`${i?'L':'M'}${(i/159*880+10).toFixed(2)},${(130-v*66).toFixed(2)}`).join(' ');
  buttons.forEach(b=>b.addEventListener('click',()=>{manual={target:Number(b.dataset.process),at:lastFraction};}));
  function update(time,dt,fraction,moving){
    lastFraction=fraction;if(manual&&Math.abs(fraction-manual.at)>.08)manual=null;
    const target=manual?manual.target:stageFromScroll(fraction);stage=moving?morphStep(stage,target,dt):target;
    const samples=pressureSequence(time),current=morphSignal(samples,stage);
    trace.setAttribute('d',path(current));reference.setAttribute('d',path(samples.raw));reference.style.opacity=String(Math.min(.17,stage*.17));
    const label=stage<.5?0:stage<1.55?1:2;
    if(label!==previousLabel){previousLabel=label;const [type,name,unit,detail]=descriptions[label];root.querySelector('#wave-label').textContent=type;root.querySelector('#wave-name').textContent=name;root.querySelector('#wave-unit').textContent=unit;root.querySelector('#process-detail').textContent=detail;buttons.forEach((b,i)=>b.setAttribute('aria-pressed',String(i===label)));}
    const result=root.querySelector('#hs-result');result.style.opacity=String(clamp(stage-1));result.textContent=`${samples.result.toFixed(2)} rel.`;
    root.querySelector('#hs-caption').style.opacity=String(clamp(stage-1));
    root.querySelectorAll('.wave-method span').forEach((s,i)=>s.classList.toggle('is-lit',stage>=i/5*2));
    const surface=root.querySelector('#pressure-surface');surface.setAttribute('d',`M15 65 Q45 ${65+Math.sin(time*.7)*4} 75 65 T135 65 T195 65`);
    root.querySelectorAll('.pressure-front').forEach((node,i)=>{const phase=(time*.32+i/3)%1;node.setAttribute('cy',String(157-phase*75));node.setAttribute('rx',String(13+phase*22));node.style.opacity=String((1-phase)*.4);});
    root.style.setProperty('--signal-stage',stage.toFixed(3));
  }
  update(0,0,0,false);return {update};
}
