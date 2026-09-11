import { BatteryCharging, Clock3, Compass, MapPin, ShieldAlert, ShieldCheck } from "lucide-react";
import type { DashboardData } from "./types";

export default function SecurityPage({data}:{data:DashboardData}){
  const distance=data.gps.anchorDistanceMeters??0,tilt=Math.hypot(data.wave.roll||0,data.wave.pitch||0),lowBattery=(data.battery.percentage??100)<25;
  const theft=distance>15&&tilt>12,displaced=distance>10,anchorSwing=distance>3&&!displaced;
  const state=theft?"POSSIBLE THEFT":displaced?"EQUIPMENT DISPLACEMENT":anchorSwing?"ANCHOR SWING":"NORMAL";
  const confidence=theft?86:displaced?76:anchorSwing?72:94;
  const reasons=[distance>10?`GPS distance is ${distance.toFixed(1)} m, beyond the 10 m demo geofence.`:`GPS distance is ${distance.toFixed(1)} m, inside the 10 m demo geofence.`,tilt>12?`Combined tilt is elevated at ${tilt.toFixed(1)}°.`:`Combined tilt is within the demo envelope at ${tilt.toFixed(1)}°.`,lowBattery?"Low battery may indicate power interruption or handling.":"Battery telemetry is available and not critically low.","The condition must persist before escalation; one sample is not treated as theft."];
  return <section className="content engineering-page"><div className="page-head"><div><span>MULTI-SIGNAL DISPLACEMENT ASSESSMENT</span><h1>Security logic</h1><p>GPS, IMU, time persistence, and power evidence combined into an explainable research alert.</p></div><em className={`sensor-chip ${state==="NORMAL"?"":"is-warning"}`}><i/> {state}</em></div>
    <div className="security-flow"><article className="panel"><h2>Inputs</h2><div><span><MapPin/><b>GPS</b>{distance.toFixed(1)} m from reference</span><span><Compass/><b>IMU</b>{tilt.toFixed(1)}° combined tilt</span><span><Clock3/><b>Persistence</b>Demo window active</span><span><BatteryCharging/><b>Battery</b>{data.battery.percentage?.toFixed(0)??"--"}%</span></div></article><i>→</i><article className="panel security-output">{state==="NORMAL"?<ShieldCheck/>:<ShieldAlert/>}<span>ASSESSMENT</span><h2>{state}</h2><strong>{confidence}% <small>evidence confidence</small></strong></article></div>
    <article className="panel trigger-evidence"><header><div><span>EXPLAINABLE ALERT</span><h2>Why this result was selected</h2></div><em>RESEARCH LOGIC</em></header><ul>{reasons.map(reason=><li key={reason}><i/>{reason}</li>)}</ul><footer>Not a certified theft detector. Confirm the event through authorized personnel before action.</footer></article>
  </section>;
}
