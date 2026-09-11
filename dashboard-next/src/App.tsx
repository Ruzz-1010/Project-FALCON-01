import { lazy, Suspense, useEffect, useMemo, useRef, useState } from "react";
import { Activity, BatteryCharging, Bell, LayoutDashboard, Menu, Navigation, Orbit, PanelLeftClose, PanelLeftOpen, Radio, Settings2, Thermometer, Waves, Wind, X, Zap } from "lucide-react";
import { getOverview } from "./api";
import type { DashboardData } from "./types";
import OverviewWaveChart from "./OverviewWaveChart";

const ActivityHub=lazy(()=>import("./ActivityHub"));
const SettingsPage=lazy(()=>import("./SettingsPage"));
const SensorsPage=lazy(()=>import("./SensorsPage"));
const MotionPage=lazy(()=>import("./MotionPage"));
const GpsPage=lazy(()=>import("./GpsPage"));
type Page="overview"|"sensors"|"motion"|"gps"|"activity"|"settings";
const navigation=[["overview","Overview","Current conditions",LayoutDashboard],["sensors","Sensors","All sensor readings",Radio],["motion","Buoy Motion","Movement view",Orbit],["gps","GPS","Location and security",Navigation],["activity","Logs & Alerts","Warnings and history",Bell]] as const;
const pageTitle:Record<Page,string>={overview:"Coastal overview",sensors:"Sensor readings",motion:"Buoy motion",gps:"GPS location",activity:"Logs and alerts",settings:"Station settings"};
const n=(value:number|null|undefined,digits=1)=>value==null?"--":value.toFixed(digits);
const seaCondition=(wave:number|null|undefined)=>wave==null?"UNKNOWN":wave<.6?"CALM":wave<2.5?"MODERATE":"ROUGH";

function OverviewTrend({data}:{data:DashboardData}){
  return <><OverviewWaveChart data={data}/><footer>{data.wave.calibration.includes("REQUIRED")?"Calibration pending · Wave height is an estimate.":"Wave height is estimated from water pressure."}</footer></>;
}
function SeaCondition({height}:{height:number|null|undefined}){
  const condition=seaCondition(height);
  return <div className={`condition-card is-${condition.toLowerCase()}`}><div><Waves aria-hidden="true"/><span>Current sea condition<strong>{condition==="UNKNOWN"?"Unavailable":condition[0]+condition.slice(1).toLowerCase()}</strong></span></div><p>{condition==="CALM"?"Estimated wave height below 0.60 m":condition==="MODERATE"?"Estimated wave height from 0.60 to 2.49 m":condition==="ROUGH"?"Estimated wave height of 2.50 m or above":"Waiting for a valid wave estimate"}</p></div>;
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
  const online=!error&&data?.status.system==="ONLINE";
  const fallback=<div className="loading"><img src="/falcon-logo.jpg" alt=""/><b>Loading FALCON data</b><span>Reading local edge records…</span></div>;
  return <div className={`app ${collapsed?"is-collapsed":""} ${sidebarOpen?"is-menu-open":""}`}>
    <a className="skip-link" href="#main-content">Skip to dashboard content</a>
    <button className="scrim" onClick={()=>setSidebarOpen(false)} aria-label="Close navigation"/>
    <aside className="sidebar"><div className="brand"><img src="/falcon-logo.jpg" alt="FALCON logo"/><div><strong>FALCON-01</strong><span>COASTAL STATION</span></div></div><nav aria-label="Main navigation">{navigation.map(([key,label,detail,Icon])=><button key={key} className={`nav-item ${page===key?"is-active":""}`} aria-label={label} title={label} aria-current={page===key?"page":undefined} onClick={()=>{setPage(key);setSidebarOpen(false)}}><Icon/><span><b>{label}</b><small>{detail}</small></span></button>)}</nav><div className="side-foot"><i className={online?"online":""}/><span><b>{online?"BAY STATION ONLINE":"BAY STATION CONNECTING"}</b><small>SHORE-BASED EDGE COMPUTER</small></span></div></aside>
    <main id="main-content" tabIndex={-1}><header className="topbar"><div className="title"><button className="mobile-menu" onClick={()=>setSidebarOpen(true)} aria-label="Open navigation"><Menu/></button><button className="collapse" onClick={()=>setCollapsed(!collapsed)} aria-label={collapsed?"Expand sidebar":"Collapse sidebar"}>{collapsed?<PanelLeftOpen/>:<PanelLeftClose/>}</button><div><span>PROJECT FALCON</span><h1>{pageTitle[page]}</h1><p className="coastal-subtitle">{page==="overview"?"Waves, wind, and station health":page==="sensors"?"Your sensors and their latest readings":page==="motion"?"Explore the buoy’s response to water movement":page==="gps"?"Station location and anchor watch":page==="activity"?"Review warnings and previous readings":"Preferences and station maintenance"}</p></div></div><div className="top-actions"><div><span>Last update</span><b>{lastUpdate}</b></div><div><span>Source</span><b>{data?.status.dataSource?.toUpperCase()||"--"}</b></div><button className="notification-button" onClick={()=>setPage("activity")} title="Logs & Alerts" aria-label="Open notifications"><Bell/>{data?.status.alerts.length?<b>{data.status.alerts.length}</b>:null}</button><button onClick={()=>setPage("settings")} title="Settings" aria-label="Open settings"><Settings2/></button><span className={`live ${online?"is-online":""}`}><i/>{online?(data?.status.dataSource?.toLowerCase()==="simulator"?"Demo data":"Live data"):"Offline"}</span></div></header>
    {error&&<div className="error-banner" role="alert"><Activity/><span><b>Station connection interrupted</b>{data?"Showing the last received readings. Reconnecting automatically…":"Unable to load readings. Check that the Bay Station service is running."}</span><button onClick={()=>setRefreshToken(value=>value+1)}>Try again</button></div>}
    {alertToast&&<button className={`alert-toast is-${alertToast.severity}`} onClick={()=>{setPage("activity");setAlertToast(null)}}><Bell/><span><b>{alertToast.code.replaceAll("_"," ")}</b>{alertToast.message}</span><X/></button>}
    {!data?fallback:page==="motion"?<Suspense fallback={fallback}><MotionPage data={data}/></Suspense>:page==="sensors"?<Suspense fallback={fallback}><SensorsPage data={data}/></Suspense>:page==="gps"?<Suspense fallback={fallback}><GpsPage data={data}/></Suspense>:page==="activity"?<Suspense fallback={fallback}><ActivityHub data={data}/></Suspense>:page==="settings"?<Suspense fallback={fallback}><SettingsPage horizon={horizon} onHorizon={setHorizon} pollInterval={pollInterval} onPollInterval={setPollInterval} onRefresh={()=>setRefreshToken(value=>value+1)}/></Suspense>:<section className="content overview-page operator-overview">
      <article className="panel coastal-wave">
        <div className="coastal-wave-heading">
          <div><h2>Estimated wave height</h2><div className="coastal-wave-reading"><strong>{n(data.wave.waveHeight,2)} <small>m</small></strong><SeaCondition height={data.wave.valid?data.wave.waveHeight:null}/></div></div>
          <div className="coastal-prediction"><span>AI prediction · in {data.ai.horizonMinutes||10} min</span><strong>{data.ai.status==="READY"?n(data.ai.predictedWaveHeight,2):"--"} <small>m</small></strong><p>{data.ai.status==="READY"?"Research estimate":"Collecting readings…"}</p></div>
        </div>
        <OverviewTrend data={data}/>
      </article>
      <dl className="coastal-readings panel" aria-label="Current station readings">
        <div><Wind aria-hidden="true"/><dt>Wind</dt><dd>{n(data.status.windSpeed)} <small>km/h</small><span>{data.status.windDirection}</span></dd></div>
        <div><Waves aria-hidden="true"/><dt>Water pressure</dt><dd>{n(data.wave.filteredPressure,2)} <small>kPa</small></dd></div>
        <div><BatteryCharging aria-hidden="true"/><dt>Battery</dt><dd>{n(data.battery.percentage,0)}<small>%</small><meter min="0" max="100" value={data.battery.percentage??0} aria-label="Battery level"/><span>{data.battery.status}</span></dd></div>
        <div><Zap aria-hidden="true"/><dt>Solar</dt><dd>{n(data.solar.power)} <small>W</small><span>{data.solar.status}</span></dd></div>
      </dl>
      <div className="coastal-footer"><span><Navigation aria-hidden="true"/>GPS: <b>{data.current.security.geofenceState.replaceAll("_"," ")}</b></span><span><Thermometer aria-hidden="true"/>Enclosure: <b>{n(data.status.internalTemperature)} °C</b></span><span>Updated {lastUpdate}</span></div>
    </section>}</main>
  </div>;
}
