import { Activity, Compass, Gauge, Rotate3d } from "lucide-react";
import MotionScene from "./MotionScene";
import type { DashboardData } from "./types";

const n=(value:number|null|undefined,digits=1)=>value==null?"--":value.toFixed(digits);
export default function MotionPage({data}:{data:DashboardData}){
 const {wave}=data,tilt=Math.hypot(wave.roll||0,wave.pitch||0),rough=(wave.waveHeight||0)>=2.5,alerts=data.status.alerts.map(alert=>`${alert.code} ${alert.message}`.toLowerCase()),fault=alerts.some(value=>value.includes("sensor"))?"sensor" as const:alerts.some(value=>value.includes("heat")||value.includes("temperature"))?"thermal" as const:alerts.some(value=>value.includes("battery")||value.includes("power"))?"power" as const:null;
 return <section className="content motion-page"><div className="page-head"><div><span>LIVE DIGITAL TWIN</span><h1>Buoy motion</h1><p>Fusion CAD orientation synchronized with BNO085 presentation telemetry.</p></div><em className="sensor-chip"><i/> IMU STREAM ACTIVE</em></div>
 <div className="motion-layout"><article className="panel twin-panel"><header><div><span>FALCON-01 ORIENTATION</span><h2>Interactive marine digital twin</h2></div><em>{fault?"COMPONENT ALERT":rough?"ROUGH MOTION":"STABLE"}</em></header><MotionScene telemetry={{roll:wave.roll||0,pitch:wave.pitch||0,yaw:wave.yaw||0,wave:wave.waveHeight||.4,rough,fault}}/><footer>{fault?`Affected ${fault} component highlighted in red.`:"Model motion is smoothed between two-second sensor samples."}</footer></article>
 <aside className="motion-side"><article className="panel pose-readout"><header><div><span>BNO085</span><h2>Live orientation</h2></div><Rotate3d/></header><dl><div><dt>Roll</dt><dd>{n(wave.roll)}°</dd></div><div><dt>Pitch</dt><dd>{n(wave.pitch)}°</dd></div><div><dt>Heading</dt><dd>{n(wave.yaw)}°</dd></div><div><dt>Combined tilt</dt><dd>{n(tilt)}°</dd></div></dl></article>
 <article className="panel motion-quality"><header><div><span>SIGNAL QUALITY</span><h2>Motion assessment</h2></div><Gauge/></header><strong>{Math.round((wave.quality||0)*100)}%</strong><p>{tilt>8?"Strong oscillation detected":tilt>3?"Elevated movement":"Motion is within the normal operating envelope"}.</p><div className="quality-line"><i style={{width:`${(wave.quality||0)*100}%`}}/></div></article>
 <article className="panel axes"><span><Activity/> Roll <b>Side-to-side</b></span><span><Compass/> Pitch <b>Front-to-back</b></span></article></aside></div></section>
}
