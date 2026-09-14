export const controllerInputs=['PRESSURE','WIND','GPS','POWER / HEALTH'];
export function controllerStep(time){
  const normalized=Math.max(0,time)/4.8,cycle=Math.floor(normalized+1e-10),phase=Math.max(0,normalized-cycle);
  return {input:cycle%4,sequence:cycle+1,phase,stage:phase<.4?'ACQUIRE':phase<.58?'TIMESTAMP':phase<.74?'VALIDATE':phase<.86?'PACKAGE':'TO LoRa'};
}
export function createController(root){
  const svg=root.querySelector('svg'),paths=[...svg.querySelectorAll('.traces path')];
  svg.querySelector('.trace-packets').remove();
  paths[4].setAttribute('d','M465 235H560V420H360V452');
  const output=svg.querySelector('text:last-child');output.textContent='FRAME ↓';output.setAttribute('x','580');output.setAttribute('y','405');
  const ns='http://www.w3.org/2000/svg',pulse=document.createElementNS(ns,'circle');pulse.setAttribute('r','4');pulse.classList.add('controller-pulse');svg.append(pulse);
  const status=svg.querySelectorAll('text')[1],labels=[...svg.querySelectorAll('text')].slice(2,6);
  const code=root.querySelector('#packet-frame');let previous='';
  function draw(time){
    const s=controllerStep(time),incoming=s.phase<.4,outgoing=s.phase>=.86;
    const path=paths[incoming?s.input:4],fraction=incoming?s.phase/.4:(s.phase-.86)/.14;
    const point=path.getPointAtLength(path.getTotalLength()*Math.max(0,Math.min(1,fraction)));
    pulse.setAttribute('cx',point.x);pulse.setAttribute('cy',point.y);pulse.style.opacity=incoming||outgoing?'1':'0';
    labels.forEach((label,i)=>label.classList.toggle('input-arrived',i===s.input&&s.phase>=.4&&s.phase<.86));
    root.classList.toggle('processing',!incoming&&!outgoing);status.textContent=s.stage;
    const key=s.sequence+':'+s.stage;
    if(key!==previous){previous=key;const stamp=new Date(s.sequence*4800).toISOString().slice(11,23);code.textContent=s.phase<.86?`${controllerInputs[s.input]} → ${s.stage.toLowerCase()}\nFrame ${String(s.sequence).padStart(4,'0')} · preparing…`:`FALCON-01 · seq ${String(s.sequence).padStart(4,'0')}\n${stamp} demo time · schema v1`;
      root.querySelector('.controller-output').textContent=outgoing?'SIMULATED · FRAME → TO LoRa':'SIMULATED · assembling telemetry';}
  }
  draw(0);return {draw};
}
