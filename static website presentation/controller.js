export const controllerInputs=['PRESSURE','WIND','GPS','POWER / HEALTH'];

// One telemetry cycle: all sensing channels arrive together, are timestamped,
// validated, assembled into one frame, then handed to LoRa.
export function controllerStep(time){
  const normalized=Math.max(0,time)/4.8,sequence=Math.floor(normalized+1e-10)+1,phase=Math.max(0,normalized-Math.floor(normalized+1e-10));
  return {
    input:-1,
    inputs:[...controllerInputs],
    sequence,
    phase,
    stage:phase<.36?'ACQUIRE':phase<.56?'TIMESTAMP':phase<.74?'VALIDATE':phase<.86?'PACKAGE':'TO LoRa'
  };
}

export function createController(root){
  const svg=root.querySelector('svg');
  const paths=[...svg.querySelectorAll('.traces path')];
  const packetPaths=[...svg.querySelectorAll('.trace-packets path')];
  const outputPath=paths[4];
  const outputPacket=packetPaths[4];
  const pulses=[];
  const ns='http://www.w3.org/2000/svg';

  // Four independent pulses move at the same time so the diagram reads as
  // parallel acquisition rather than a round-robin sensor sequence.
  packetPaths.slice(0,4).forEach((path)=>{
    const pulse=document.createElementNS(ns,'circle');
    pulse.setAttribute('r','4');
    pulse.classList.add('controller-pulse');
    svg.append(pulse);
    pulses.push(pulse);
  });

  const outputPulse=document.createElementNS(ns,'circle');
  outputPulse.setAttribute('r','4');
  outputPulse.classList.add('controller-pulse','controller-output-pulse');
  svg.append(outputPulse);

  const status=svg.querySelectorAll('text')[1];
  const labels=[...svg.querySelectorAll('text')].slice(2,6);
  const code=root.querySelector('#packet-frame');
  let previous='';

  function placePulse(pulse,path,fraction,visible){
    const point=path.getPointAtLength(path.getTotalLength()*Math.max(0,Math.min(1,fraction)));
    pulse.setAttribute('cx',point.x);
    pulse.setAttribute('cy',point.y);
    pulse.style.opacity=visible?'1':'0';
  }

  function draw(time){
    const s=controllerStep(time);
    const acquiring=s.phase<.36;
    const sending=s.phase>=.86;
    const inputFraction=acquiring?s.phase/.36:1;

    packetPaths.slice(0,4).forEach((path,i)=>placePulse(pulses[i],path,inputFraction,acquiring));
    const outputFraction=sending?(s.phase-.86)/.14:0;
    placePulse(outputPulse,outputPacket,outputFraction,sending);

    labels.forEach(label=>label.classList.toggle('input-arrived',!acquiring));
    root.classList.toggle('processing',!acquiring&&!sending);
    root.classList.toggle('sending',sending);
    status.textContent=s.stage;

    const key=s.sequence+':'+s.stage;
    if(key!==previous){
      previous=key;
      const stamp=new Date((s.sequence-1)*4800).toISOString().slice(11,23);
      if(s.stage==='ACQUIRE'){
        code.textContent=`PRESSURE + WIND + GPS + POWER / HEALTH\nFrame ${String(s.sequence).padStart(4,'0')} · parallel acquisition`;
      }else if(s.stage==='TIMESTAMP'){
        code.textContent=`FALCON-01 · frame ${String(s.sequence).padStart(4,'0')}\n${stamp} demo time · timestamping all inputs`;
      }else if(s.stage==='VALIDATE'){
        code.textContent=`FALCON-01 · frame ${String(s.sequence).padStart(4,'0')}\n4 inputs · quality checks · no silent zeroing`;
      }else if(s.stage==='PACKAGE'){
        code.textContent=`FALCON-01 · FRAME ${String(s.sequence).padStart(4,'0')}\npressure | wind | GPS | power/health → one telemetry packet`;
      }else{
        code.textContent=`FALCON-01 · seq ${String(s.sequence).padStart(4,'0')}\nschema v1 · timestamp · quality flags → LoRa`;
      }
      root.querySelector('.controller-output').textContent=sending?'SIMULATED · FRAME → TO LoRa':'SIMULATED · processing all inputs together';
    }
  }

  draw(0);
  return {draw};
}
