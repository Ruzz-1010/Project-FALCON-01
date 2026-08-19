import { useState } from "react";
import { BatteryCharging, CheckCircle2, Compass, Crosshair, LoaderCircle, MapPin, Sun, Waves, Wind } from "lucide-react";
import { startCalibration } from "./api";

const sensors=[
  {id:"gps",name:"GPS reference",icon:MapPin,note:"Record the surveyed deployment coordinate and verify position error in open sky."},
  {id:"bno085",name:"IMU orientation",icon:Compass,note:"Fix the mounting orientation, hold the buoy level, then validate roll, pitch, and heading."},
  {id:"water-pressure",name:"Pressure / depth",icon:Waves,note:"Zero in air, compare at known water depths, and document water density and sensor mounting depth."},
  {id:"wind",name:"Wind speed + direction",icon:Wind,note:"Compare speed with a reference meter and map every vane direction to the ADS1115 reading."},
  {id:"battery",name:"Battery monitor",icon:BatteryCharging,note:"Compare INA260 voltage and current with a calibrated multimeter under known loads."},
  {id:"solar",name:"Solar monitor",icon:Sun,note:"Compare panel-side voltage and current under controlled charging conditions."},
] as const;

export default function CalibrationPage(){
  const [states,setStates]=useState<Record<string,{status:string;at:string;progress:number}>>({}),[error,setError]=useState<string|null>(null);
  const run=async(id:string)=>{setError(null);setStates(value=>({...value,[id]:{status:"IN PROGRESS",at:"Now",progress:35}}));try{await startCalibration(id);window.setTimeout(()=>setStates(value=>({...value,[id]:{status:"PROCEDURE STARTED",at:new Date().toLocaleString(),progress:65}})),700);}catch(reason){setStates(value=>({...value,[id]:{status:"NOT STARTED",at:"--",progress:0}}));setError(reason instanceof Error?reason.message:"Calibration request failed")}};
  return <section className="content engineering-page"><div className="page-head"><div><span>CONTROLLED REFERENCE PROCEDURES</span><h1>Calibration</h1><p>Start and document calibration workflows. A completed button does not replace reference measurements or approval.</p></div><em className="sensor-chip is-warning"><i/> FIELD RECORDS REQUIRED</em></div>{error&&<div className="inline-error">{error}</div>}
    <div className="truth-banner"><Crosshair/><span><b>CALIBRATION REGISTER</b>All dates remain pending until a real procedure, reference instrument, operator, and result are recorded.</span></div>
    <div className="calibration-grid">{sensors.map(({id,name,icon:Icon,note})=>{const state=states[id]||{status:"NOT CALIBRATED",at:"No field record",progress:0};return <article className="panel calibration-card" key={id}><header><Icon/><div><span>CALIBRATION CHANNEL</span><h2>{name}</h2></div>{state.progress?<CheckCircle2/>:null}</header><p>{note}</p><dl><div><dt>Current status</dt><dd>{state.status}</dd></div><div><dt>Last calibration</dt><dd>{state.at}</dd></div><div><dt>Notes</dt><dd>Reference evidence required</dd></div></dl><div className="calibration-progress"><span>Procedure progress <b>{state.progress}%</b></span><i><em style={{width:`${state.progress}%`}}/></i></div><button onClick={()=>run(id)} disabled={state.status==="IN PROGRESS"}>{state.status==="IN PROGRESS"?<LoaderCircle/>:<Crosshair/>}{state.status==="IN PROGRESS"?"Starting…":"Start guided procedure"}</button></article>})}</div>
  </section>;
}
