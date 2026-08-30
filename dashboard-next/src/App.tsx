import { lazy, Suspense, useEffect, useMemo, useRef, useState } from "react";
import { Activity, ArrowRight, BatteryCharging, Bell, BrainCircuit, Gauge, LayoutDashboard, Menu, Navigation, Orbit, PanelLeftClose, PanelLeftOpen, Radio, Settings2, Thermometer, Waves, Wind, X, Zap } from "lucide-react";
import { getOverview } from "./api";
import type { DashboardData } from "./types";
import OverviewWaveChart from "./OverviewWaveChart";

const ActivityHub=lazy(()=>import("./ActivityHub"));
const SettingsPage=lazy(()=>import("./SettingsPage"));
const SensorsPage=lazy(()=>import("./SensorsPage"));
const MotionPage=lazy(()=>import("./MotionPage"));
type Page="overview"|"motion"|"sensors"|"activity"|"settings";
const navigation=[["overview","Overview","Current conditions",LayoutDashboard],["motion","Buoy Motion","Buoy movement view",Orbit],["sensors","Sensors","All sensor readings",Radio],["activity","Logs & Alerts","Warnings and history",Bell]] as const;
const pageTitle:Record<Page,string>={overview:"Coastal overview",motion:"Buoy motion",sensors:"Sensor readings",activity:"Logs and alerts",settings:"Station settings"};
const n=(value:number|null|undefined,digits=1)=>value==null?"--":value.toFixed(digits);
const seaCondition=(wave:number|null|undefined)=>wave==null?"UNKNOWN":wave<.6?"CALM":wave<2.5?"MODERATE":"ROUGH";

function OverviewTrend({data}:{data:DashboardData}){
  return <><OverviewWaveChart data={data}/><footer>{data.wave.calibration} · Blue-gray line is the current estimate · Red line is the AI prediction</footer></>;
}
function MiniTrend({label,value,unit,color,icon:Icon,points}:{label:string;value:number|null|undefined;unit:string;color:string;icon:typeof Gauge;points:Array<number|null|undefined>}){
  const valid=points.filter((item):item is number=>typeof item==="number").slice(-30),min=Math.min(...valid),max=Math.max(...valid),range=Math.max(.01,max-min),coords=valid.map((item,index)=>[12+index/Math.max(1,valid.length-1)*276,82-(item-min)/range*54]);
  const curve=coords.length?coords.slice(1).reduce((path,next,index)=>{const current=coords[index],midX=(current[0]+next[0])/2,midY=(current[1]+next[1])/2;return`${path} Q ${current[0]} ${current[1]} ${midX} ${midY}`},`M ${coords[0][0]} ${coords[0][1]}`)+` T ${coords.at(-1)![0]} ${coords.at(-1)![1]}`:"";
  return <article className="panel mini-trend"><header><div className="panel-title"><Icon/><div><span>Recent trend</span><h2>{label}</h2></div></div><strong>{n(value,label==="Water pressure"?2:1)}{unit}</strong></header>{valid.length>1?<svg viewBox="0 0 300 96" role="img" aria-label={`${label} recent trend`}><line x1="12" y1="28" x2="288" y2="28"/><line x1="12" y1="55" x2="288" y2="55"/><line x1="12" y1="82" x2="288" y2="82"/><path d={curve} style={{stroke:color}}/></svg>:<p>Collecting history…</p>}</article>;
}

function AiWavePrediction({data}:{data:DashboardData}){
  const prediction=data.ai,ready=prediction.status==="READY"&&prediction.predictedWaveHeight!=null;
  const current=prediction.currentWaveHeight??data.wave.waveHeight;
  const source=data.status.dataSource?.toUpperCase()==="SIMULATOR"?"SIMULATED AI DEMO":"EDGE AI MODEL";
  return <article className={`panel ai-wave-card ${ready?"is-ready":"is-collecting"}`}>
    <header><div className="panel-title"><BrainCircuit/><div><span>FALCON AI</span><h2>Wave prediction</h2></div></div><em>{source}</em></header>
    <div className="ai-prediction-flow">
      <div><span>Current estimate</span><strong>{n(current,2)} m</strong><small>Pressure-based reading</small></div>
      <ArrowRight aria-hidden="true"/>
      <div><span>In {prediction.horizonMinutes||10} minutes</span><strong>{ready?`${n(prediction.predictedWaveHeight,2)} m`:"Collecting data"}</strong><small>{ready?`${prediction.direction||"stable"} trend`:"At least 8 readings required"}</small></div>
    </div>
    <dl className="ai-prediction-details"><div><dt>Expected condition</dt><dd>{ready?prediction.seaCondition:"PENDING"}</dd></div><div><dt>Confidence</dt><dd>{ready&&prediction.confidence!=null?`${prediction.confidence}%`:"--"}</dd></div><div><dt>Model status</dt><dd>{ready?"ACTIVE":"COLLECTING"}</dd></div><div><dt>Samples used</dt><dd>{prediction.sampleCount??0}</dd></div></dl>
    <footer>{ready?"Short-term estimate from recent wave-height records. For research monitoring, not an official marine forecast.":"The AI prediction will start automatically when enough wave records are available."}</footer>
  </article>;
}

export default function App(){
  const [data,setData]=useState<DashboardData|null>(null),[error,setError]=useState<string|null>(null),[page,setPage]=useState<Page>("overview"),[sidebarOpen,setSidebarOpen]=useState(false),[collapsed,setCollapsed]=useState(false),[horizon,setHorizon]=useState(10),[refreshToken,setRefreshToken]=useState(0);
  const [pollInterval,setPollInterval]=useState(()=>Number(localStorage.getItem("falcon-next-poll"))||2000);
  const [alertToast,setAlertToast]=useState<{code:string;message:string;severity:string}|null>(null),knownAlerts=useRef<Set<string>|null>(null);
  useEffect(()=>{document.documentElement.dataset.theme="light"},[]);
  useEffect(()=>localStorage.setItem("falcon-next-poll",String(pollInterval)),[pollInterval]);
  useEffect(()=>{let active=true;const refresh=async()=>{try{const next=await getOverview(horizon);if(active){setData(next);setError(null)}}catch(reason){if(active)setError(reason instanceof Error?reason.message:"Edge service unavailable")}};refresh();const timer=window.setInterval(refresh,pollInterval);return()=>{active=false;window.clearInterval(timer)}},[horizon,pollInterval,refreshToken]);
  useEffect(()=>{if(!data)return;const next=new Set(data.status.alerts.map(item=>item.code));if(knownAlerts.current){const fresh=data.status.alerts.find(item=>!knownAlerts.current?.has(item.code));if(fresh){setAlertToast(fresh);window.setTimeout(()=>setAlertToast(null),8000)}}knownAlerts.current=next},[data]);
  const lastUpdate=useMemo(()=>data?.status.lastUpdate?new Date(data.status.lastUpdate).toLocaleTimeString():"--:--:--",[data]);
  const online=data?.status.system==="ONLINE";
  const fallback=<div className="loading"><img src="/falcon-logo.jpg" alt=""/><b>Loading FALCON data</b><span>Reading local edge records…</span></div>;
  return <div className={`app ${collapsed?"is-collapsed":""} ${sidebarOpen?"is-menu-open":""}`}>
    <button className="scrim" onClick={()=>setSidebarOpen(false)} aria-label="Close navigation"/>
    <aside className="sidebar"><div className="brand"><img src="/falcon-logo.jpg" alt="FALCON logo"/><div><strong>FALCON-01</strong><span>COASTAL STATION</span></div></div><nav>{navigation.map(([key,label,detail,Icon])=><button key={key} className={`nav-item ${page===key?"is-active":""}`} onClick={()=>{setPage(key);setSidebarOpen(false)}}><Icon/><span><b>{label}</b><small>{detail}</small></span></button>)}</nav><div className="side-foot"><i className={online?"online":""}/><span><b>{online?"BAY STATION ONLINE":"BAY STATION CONNECTING"}</b><small>SHORE-BASED EDGE COMPUTER</small></span></div></aside>
    <main><header className="topbar"><div className="title"><button className="mobile-menu" onClick={()=>setSidebarOpen(true)} aria-label="Open navigation"><Menu/></button><button className="collapse" onClick={()=>setCollapsed(!collapsed)} aria-label="Toggle sidebar">{collapsed?<PanelLeftOpen/>:<PanelLeftClose/>}</button><div><span>PROJECT FALCON</span><h1>{pageTitle[page]}</h1></div></div><div className="top-actions"><div><span>Last update</span><b>{lastUpdate}</b></div><div><span>Source</span><b>{data?.status.dataSource?.toUpperCase()||"--"}</b></div><button className="notification-button" onClick={()=>setPage("activity")} title="Logs & Alerts" aria-label="Open notifications"><Bell/>{data?.status.alerts.length?<b>{data.status.alerts.length}</b>:null}</button><button onClick={()=>setPage("settings")} title="Settings" aria-label="Open settings"><Settings2/></button><span className={`live ${online?"is-online":""}`}><i/>{online?(data?.current.system.labels[0]||"LIVE"):"OFFLINE"}</span></div></header>
    {error&&<div className="error-banner"><Activity/><span><b>Edge connection interrupted</b>{error}</span></div>}
    {alertToast&&<button className={`alert-toast is-${alertToast.severity}`} onClick={()=>{setPage("activity");setAlertToast(null)}}><Bell/><span><b>{alertToast.code.replaceAll("_"," ")}</b>{alertToast.message}</span><X/></button>}
    {!data?fallback:page==="motion"?<Suspense fallback={fallback}><MotionPage data={data}/></Suspense>:page==="sensors"?<Suspense fallback={fallback}><SensorsPage data={data}/></Suspense>:page==="activity"?<Suspense fallback={fallback}><ActivityHub data={data}/></Suspense>:page==="settings"?<Suspense fallback={fallback}><SettingsPage horizon={horizon} onHorizon={setHorizon} pollInterval={pollInterval} onPollInterval={setPollInterval} onRefresh={()=>setRefreshToken(value=>value+1)}/></Suspense>:<section className="content overview-page operator-overview">
      <div className="dashboard-grid"><article className="panel chart-panel sensor-history-card"><header><div className="panel-title"><Waves/><div><span>Main reading</span><h2>Estimated wave height</h2></div></div><strong className="wave-value">{n(data.wave.waveHeight,2)} m</strong></header><div className="sea-condition-summary"><span>Sea condition</span><div className="sea-condition-scale" aria-label={`Current sea condition: ${seaCondition(data.wave.waveHeight)}`}>{([{name:"CALM",range:"Below 0.60 m"},{name:"MODERATE",range:"0.60–2.49 m"},{name:"ROUGH",range:"2.50 m and above"}] as const).map(condition=><div key={condition.name} className={seaCondition(data.wave.waveHeight)===condition.name?`is-current is-${condition.name.toLowerCase()}`:""}><b>{condition.name}</b><small>{condition.range}</small></div>)}</div></div><OverviewTrend data={data}/></article>
      <article className="panel snapshot"><header><div className="panel-title"><Gauge/><div><span>Current readings</span><h2>Station status</h2></div></div><em className={data.current.security.state==="SECURE"?"status-good":"status-danger"}>{data.current.security.state}</em></header><dl><div><dt><Wind/>Wind</dt><dd>{n(data.status.windSpeed)} km/h · {data.status.windDirection}</dd></div><div><dt><Waves/>Pressure</dt><dd>{n(data.wave.filteredPressure,2)} kPa</dd></div><div><dt><Navigation/>GPS security</dt><dd>{data.current.security.geofenceState}</dd></div><div><dt><BatteryCharging/>Battery</dt><dd>{n(data.battery.percentage,0)}% · {data.battery.status}</dd></div><div><dt><Zap/>Solar</dt><dd>{data.solar.status} · {n(data.solar.power)} W</dd></div><div><dt><Thermometer/>Temperature</dt><dd>Water {n(data.current.environment.waterTemperature)} °C<br/>Enclosure {n(data.status.internalTemperature)} °C</dd></div></dl></article></div>
      <AiWavePrediction data={data}/>
      <div className="always-visible-trends"><MiniTrend label="Water pressure" value={data.wave.filteredPressure} unit=" kPa" color="#6B8FA3" icon={Gauge} points={data.wave.history.map(item=>item.filteredPressure)}/><MiniTrend label="Wind speed" value={data.status.windSpeed} unit=" km/h" color="#3F7F7A" icon={Wind} points={data.status.sensorHistory.map(item=>item.windSpeed)}/><MiniTrend label="GPS distance from anchor" value={data.gps.anchorDistanceMeters} unit=" m" color="#9A7C55" icon={Navigation} points={data.status.sensorHistory.map(item=>item.anchorDistance)}/></div>
    </section>}</main>
  </div>;
}
