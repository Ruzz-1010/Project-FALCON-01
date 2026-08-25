import { Activity, Compass, Gauge, Rotate3d } from "lucide-react";
import MotionScene from "./MotionScene";
import type { DashboardData } from "./types";

const n=(value:number|null|undefined,digits=1)=>value==null?"--":value.toFixed(digits);
export default function MotionPage({data}:{data:DashboardData}){
 const {wave}=data,rough=(wave.waveHeight||0)>=2.5,alerts=data.status.alerts.map(alert=>`${alert.code} ${alert.message}`.toLowerCase()),fault=alerts.some(value=>value.includes("sensor"))?"sensor" as const:alerts.some(value=>value.includes("heat")||value.includes("temperature"))?"thermal" as const:alerts.some(value=>value.includes("battery")||value.includes("power"))?"power" as const:null;
 return <section className="content motion-page"><div className="page-head"><div><span>OPTIONAL VISUAL MOVEMENT MODEL</span><h1>Buoy motion</h1><p>The 3D view illustrates buoy response to estimated sea conditions. It is not a direct IMU measurement in the Phase 1 baseline.</p></div><em className="sensor-chip"><i/> VISUAL MODEL · {data.status.dataSource.toUpperCase()}</em></div>
 <div className="motion-layout"><article className="panel twin-panel"><header><div><span>FALCON-01 RESPONSE MODEL</span><h2>Interactive marine digital twin</h2></div><em>{fault?"COMPONENT ALERT":rough?"ROUGH SEA MODEL":"CALM SEA MODEL"}</em></header><MotionScene telemetry={{roll:0,pitch:0,yaw:data.gps.headingDegrees||0,wave:wave.waveHeight||.4,rough,fault}}/><footer>{fault?`Affected ${fault} component highlighted in red.`:"Animation follows the pressure-based estimated wave context; it is not measured orientation."}</footer></article>
 <aside className="motion-side"><article className="panel pose-readout"><header><div><span>VISUAL MODEL</span><h2>Illustrated orientation</h2></div><Rotate3d/></header><dl><div><dt>Roll</dt><dd>MODEL</dd></div><div><dt>Pitch</dt><dd>MODEL</dd></div><div><dt>Heading</dt><dd>{n(data.gps.headingDegrees)}°</dd></div><div><dt>Input</dt><dd>{n(wave.waveHeight,2)} m EST.</dd></div></dl></article>
 <article className="panel motion-quality"><header><div><span>ESTIMATE QUALITY</span><h2>Visualization input</h2></div><Gauge/></header><strong>{Math.round((wave.quality||0)*100)}%</strong><p>Quality indicator of the pressure-based wave estimate driving this visual model.</p><div className="quality-line"><i style={{width:`${(wave.quality||0)*100}%`}}/></div></article>
 <article className="panel axes"><span><Activity/> Roll <b>Side-to-side</b></span><span><Compass/> Pitch <b>Front-to-back</b></span></article></aside></div></section>
}
