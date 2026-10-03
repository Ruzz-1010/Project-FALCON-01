// Illustrative signals only. No live measurements, invented calibration or onboard estimation.
export const signals={
  pressure:{source:'Pressure',raw:'Relative pressure · illustrative',record:'Pressure, time and quality',result:'On shore → pressure-derived estimated wave height',kind:'wave'},
  wind:{source:'Wind',raw:'Wind pulses · illustrative',record:'Speed, direction and time',result:'Local wind conditions at the buoy',kind:'pulse'},
  gps:{source:'Position & time',raw:'Position fixes · illustrative',record:'Position, time and fix quality',result:'Quality-checked location and timing',kind:'fix'},
  solar:{source:'Solar power',raw:'Voltage / current · illustrative',record:'Panel and battery state + time',result:'Power monitoring for buoy health',kind:'energy'},
  battery:{source:'Battery',raw:'Stored energy · illustrative',record:'Battery and charging state + time',result:'Energy kept for sensing and telemetry',kind:'energy'},
  esp32:{source:'All sensor streams',raw:'Incoming records · illustrative',record:'Timestamp, quality and sequence',result:'Acquire → check → package for LoRa',kind:'streams'},
  lora:{source:'LoRa link',raw:'Link packets · illustrative',record:'Sequence, link state and buffer',result:'Buoy → shore telemetry link',kind:'streams'}
};
export function signalTrace(kind,time,row=0){
  return Array.from({length:100},(_,i)=>{
    const x=i*4,phase=i*.13+time*.7;
    const v=kind==='pulse'?(Math.sin(phase*2)> .5?16:-12):kind==='fix'?(i%20<3?15:0):kind==='energy'?Math.sin(phase*.45)*6+Math.sin(phase*2)*2:Math.sin(phase+row*2)*13+Math.sin(phase*2.7)*4;
    return `${i?'L':'M'}${x.toFixed(1)},${(40+row*23-v*(kind==='streams'?.35:1)).toFixed(1)}`;
  }).join(' ');
}
export function createAcquisition(dock){
  const view=document.createElement('div');view.id='acquisition-signal';
  view.innerHTML='<div class="signal-heading"><span>RAW SIGNAL</span><small>ILLUSTRATIVE / NOT LIVE</small></div><svg viewBox="0 0 400 100" role="img"><path class="signal-axis" d="M0 40H400 M0 75H400"/><path class="signal-trace"/><path class="signal-trace secondary"/><path class="signal-trace secondary"/></svg><p class="signal-unit"></p><div class="signal-record"><span>ACQUIRED DATA</span><p></p></div><p class="signal-result"></p>';
  dock.append(view);let current='pressure';
  function select(id){current=id;const s=signals[id];view.querySelector('svg').setAttribute('aria-label',s.raw);view.querySelector('.signal-unit').textContent=s.raw;view.querySelector('.signal-record p').textContent=s.record;view.querySelector('.signal-result').textContent=s.result;draw(0);}
  function draw(time){view.querySelectorAll('.signal-trace').forEach((p,i)=>{p.hidden=i>0&&signals[current].kind!=='streams';p.style.display=p.hidden?'none':'';p.setAttribute('d',signalTrace(signals[current].kind,time,i));});}
  select(current);return {view,select,draw,place(inspection){(inspection||dock).append(view);}};
}
