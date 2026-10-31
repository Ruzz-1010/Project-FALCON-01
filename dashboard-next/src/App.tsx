import { lazy, Suspense, useEffect, useMemo, useRef, useState, type ReactNode } from "react";
import { Activity, BatteryCharging, Bell, Compass, LayoutDashboard, MapPin, Menu, Navigation, PanelLeftClose, PanelLeftOpen, Radio, Settings2, Thermometer, Waves, Wind, X, Zap } from "lucide-react";
import { getOverview } from "./api";
import type { DashboardData } from "./types";
import OverviewWaveChart from "./OverviewWaveChart";

const ActivityHub=lazy(()=>import("./ActivityHub"));
const SettingsPage=lazy(()=>import("./SettingsPage"));
const SensorsPage=lazy(()=>import("./SensorsPage"));
const GpsPage=lazy(()=>import("./GpsPage"));
type Page="overview"|"sensors"|"gps"|"activity"|"settings";
const navigation=[["overview","Overview","Station summary",LayoutDashboard],["sensors","Sensors","Check each device",Radio],["gps","GPS & safety","Location and anchor",Navigation],["activity","Alerts & records","Warnings and history",Bell]] as const;
const pageTitle:Record<Page,string>={overview:"Coastal overview",sensors:"Sensor readings",gps:"GPS location",activity:"Logs and alerts",settings:"Station settings"};
const n=(value:number|null|undefined,digits=1)=>value==null?"--":value.toFixed(digits);
const seaCondition=(wave:number|null|undefined)=>wave==null?"UNKNOWN":wave<.6?"CALM":wave<2.5?"MODERATE":"ROUGH";
const titleCase=(value:string)=>value.toLowerCase().replaceAll("_"," ").replace(/\b\w/g,letter=>letter.toUpperCase());

const trendOf=(values:Array<number|null|undefined>)=>{
  const clean=values.filter((v):v is number=>typeof v==="number"&&Number.isFinite(v));
  if(clean.length<2)return{shape:"flat" as const,label:"No trend yet",delta:0};
  const first=clean[0],last=clean[clean.length-1],span=Math.abs(first)||1,change=(last-first)/span;
  if(Math.abs(change)<0.015)return{shape:"flat" as const,label:"Holding steady",delta:last-first};
  return change>0?{shape:"up" as const,label:"Trending up",delta:last-first}:{shape:"down" as const,label:"Trending down",delta:last-first};
};
function Spark({values}:{values:Array<number|null|undefined>}){
  const clean=values.filter((v):v is number=>typeof v==="number"&&Number.isFinite(v)).slice(-28);
  if(clean.length<2)return <svg className="reading-spark" viewBox="0 0 96 34" aria-hidden="true" />;
  const lo=Math.min(...clean),hi=Math.max(...clean),range=hi-lo||1,step=96/(clean.length-1);
  const points=clean.map((v,i)=>`${(i*step).toFixed(1)} ${(30-((v-lo)/range)*26).toFixed(1)}`);
  return <svg className="reading-spark" viewBox="0 0 96 34" preserveAspectRatio="none" role="img" aria-label={`Trend across the last ${clean.length} samples`}>
    <polygon points={`0 34 ${points.join(" ")} 96 34`} className="reading-spark-fill" />
    <polyline points={points.join(" ")} className="reading-spark-line" />
  </svg>;
}
type ReadingCardProps={icon:ReactNode;name:string;chip:string;value:string;unit?:string;note:string;trendValues:Array<number|null|undefined>;stateText:string;stateTone:"ok"|"info";meter?:number|null};
function ReadingCard({icon,name,chip,value,unit,note,trendValues,stateText,stateTone,meter}:ReadingCardProps){
  const trend=trendOf(trendValues);
  return <div className={`reading-card is-${stateTone} trend-${trend.shape}`}>
    <div className="reading-top"><span className="reading-icon">{icon}</span><div className="reading-heading"><dt>{name}</dt><span className="reading-chip">{chip}</span></div></div>
    <div className="reading-value"><dd>{value}{unit?<small>{unit}</small>:null}</dd><div className="reading-trend"><Spark values={trendValues}/><span className="reading-trend-label">{trend.label}</span></div></div>
    <p className="reading-note">{note}</p>
    <span className="reading-state">{stateText}</span>
    {meter!=null?<meter min="0" max="100" value={meter} aria-label={`${name} level`} />:null}
  </div>;
}
function OverviewTrend({data}:{data:DashboardData}){
  return <><OverviewWaveChart data={data}/><footer>{data.wave.calibration.includes("REQUIRED")?"Calibration pending · Wave height is an estimate.":"Wave height is estimated from water pressure."}</footer></>;
}
function PlainStatus({data}:{data:DashboardData}){
  const wave=data.wave.valid?`${n(data.wave.waveHeight,2)} m estimated wave height`:"Wave reading unavailable";
  const location=geofenceLabel(data.current.security.geofenceState);
  const power=data.battery.percentage==null?"Battery reading unavailable":`${n(data.battery.percentage,0)}% battery`;
  return <section className="plain-status" aria-label="How to read this dashboard">
    <div><span>1</span><p><b>Water</b>{wave}</p></div>
    <div><span>2</span><p><b>Safety</b>{location}</p></div>
    <div><span>3</span><p><b>Power</b>{power}</p></div>
  </section>;
}
function SeaCondition({height}:{height:number|null|undefined}){
  const condition=seaCondition(height);
  return <div className={`sea-condition is-${condition.toLowerCase()}`}>
    <span className="sea-label">Sea condition</span>
    <strong>{condition==="UNKNOWN"?"Unavailable":titleCase(condition)}</strong>
    <p>{condition==="CALM"?"Waves 0.00 to 0.59 m":condition==="MODERATE"?"Waves 0.60 to 2.49 m":condition==="ROUGH"?"Waves 2.50 m and above":"Waiting for a valid wave estimate"}</p>
  </div>;
}
function geofenceLabel(state:string|undefined){
  if(!state)return "Unknown";
  if(state==="SECURE"||state==="INSIDE"||state==="INSIDE_SAFE_ZONE")return "Inside safe zone";
  if(state==="BREACH"||state==="OUTSIDE"||state==="OUTSIDE_SAFE_ZONE")return "Outside safe zone";
  return titleCase(state);
}
export default function App(){
  const [data,setData]=useState<DashboardData|null>(null),[error,setError]=useState<string|null>(null),[page,setPage]=useState<Page>("overview"),[sidebarOpen,setSidebarOpen]=useState(false),[collapsed,setCollapsed]=useState(false),[horizon,setHorizon]=useState(10),[refreshToken,setRefreshToken]=useState(0);
  const [pollInterval,setPollInterval]=useState(()=>Number(localStorage.getItem("falcon-next-poll"))||2000);
  const [alertToast,setAlertToast]=useState<{code:string;message:string;severity:string}|null>(null),knownAlerts=useRef<Set<string>|null>(null);
  useEffect(()=>{document.documentElement.dataset.theme="light"},[]);
  useEffect(()=>localStorage.setItem("falcon-next-poll",String(pollInterval)),[pollInterval]);
  useEffect(()=>{let active=true;const refresh=async()=>{try{const next=await getOverview(horizon);if(active){setData(next);setError(null)}}catch(reason){if(active)setError(reason instanceof Error?reason.message:"Edge service unavailable")}};refresh();const timer=window.setInterval(refresh,pollInterval);return()=>{active=false;window.clearInterval(timer)}},[horizon,pollInterval,refreshToken]);
  useEffect(()=>{if(!data)return;const next=new Set(data.status.alerts.map(item=>item.code));if(knownAlerts.current){const fresh=data.status.alerts.find(item=>!knownAlerts.current?.has(item.code));if(fresh){setAlertToast(fresh);window.setTimeout(()=>setAlertToast(null),8000)}}knownAlerts.current=next},[data]);
  const lastUpdate=useMemo(()=>data?.status.lastUpdate?new Date(data.status.lastUpdate).toLocaleTimeString([],{hour12:false}):"--:--:--",[data]);
  const online=!error&&data?.status.system==="ONLINE";
  const simulator=data?.status.dataSource?.toLowerCase()==="simulator";
  const critical=data?.status.alerts.some(alert=>["CRITICAL","EMERGENCY"].includes(alert.severity.toUpperCase()))??false;
  const severity=critical?"danger":seaCondition(data?.wave.waveHeight)==="ROUGH"?"rough":"calm";
  const fallback=<div className="loading"><img src="/falcon-logo.jpg" alt=""/><b>Loading FALCON data</b><span>Reading local edge records…</span></div>;
  return <div className={`app ${collapsed?"is-collapsed":""} ${sidebarOpen?"is-menu-open":""}`}>
    <a className="skip-link" href="#main-content">Skip to dashboard content</a>
    <button className="scrim" onClick={()=>setSidebarOpen(false)} aria-label="Close navigation"/>
    <aside className="sidebar"><div className="brand"><img src="/falcon-logo.jpg" alt="FALCON logo"/><div><strong>FALCON-01</strong><span>Coastal Station</span></div></div><nav aria-label="Main navigation">{navigation.map(([key,label,detail,Icon])=><button key={key} className={`nav-item ${page===key?"is-active":""}`} aria-label={label} title={label} aria-current={page===key?"page":undefined} onClick={()=>{setPage(key);setSidebarOpen(false)}}><Icon/><span><b>{label}</b><small>{detail}</small></span></button>)}</nav><div className="side-foot"><i className={online?"online":""}/><span><b>{online?"Station is online":"Station is connecting"}</b><small>{simulator?"Presentation simulator":"Shore-based edge computer"}</small></span></div></aside>
    <main id="main-content" tabIndex={-1}>
      <header className="topbar">
        <div className="title">
          <button className="mobile-menu" onClick={()=>setSidebarOpen(true)} aria-label="Open navigation"><Menu/></button>
          <button className="collapse" onClick={()=>setCollapsed(!collapsed)} aria-label={collapsed?"Expand sidebar":"Collapse sidebar"}>{collapsed?<PanelLeftOpen/>:<PanelLeftClose/>}</button>
          <div><h1>{pageTitle[page]}</h1><p className="coastal-subtitle">{page==="overview"?"Waves, wind, and station health at a glance":page==="sensors"?"Every sensor and its latest reading":page==="gps"?"Station location and anchor watch":page==="activity"?"Review warnings and earlier readings":"Preferences and station maintenance"}</p></div>
        </div>
        <div className="top-actions">
          <span className={`live ${online?"is-online":""}`} title={online?`Data source: ${data?.status.dataSource} · ESP32 ${data?.status.esp32}`:"Reconnecting to the edge service"}><i/><span><b>{online?(simulator?"Demo data":"Live data"):"Offline"}</b><small>{online?(simulator?"Prototype simulation":`ESP32 ${data?.status.esp32?.toLowerCase()||"linked"}`):"Reconnecting"}</small></span></span>
          <button className="notification-button" onClick={()=>setPage("activity")} title="Logs & Alerts" aria-label="Open notifications"><Bell/>{data?.status.alerts.length?<b>{data.status.alerts.length}</b>:null}</button>
          <button onClick={()=>setPage("settings")} title="Settings" aria-label="Open settings"><Settings2/></button>
        </div>
      </header>
      {error&&<div className="error-banner" role="alert"><Activity/><span><b>Station connection interrupted</b>{data?"Showing the last received readings. Reconnecting automatically…":"Unable to load readings. Check that the Bay Station service is running."}</span><button onClick={()=>setRefreshToken(value=>value+1)}>Try again</button></div>}
      {alertToast&&<button className={`alert-toast is-${alertToast.severity}`} onClick={()=>{setPage("activity");setAlertToast(null)}}><Bell/><span><b>{alertToast.code.replaceAll("_"," ")}</b>{alertToast.message}</span><X/></button>}
      {!data?fallback:page==="sensors"?<Suspense fallback={fallback}><SensorsPage data={data}/></Suspense>:page==="gps"?<Suspense fallback={fallback}><GpsPage data={data}/></Suspense>:page==="activity"?<Suspense fallback={fallback}><ActivityHub data={data}/></Suspense>:page==="settings"?<Suspense fallback={fallback}><SettingsPage horizon={horizon} onHorizon={setHorizon} pollInterval={pollInterval} onPollInterval={setPollInterval} onRefresh={()=>setRefreshToken(value=>value+1)}/></Suspense>:<section className={`content overview-page operator-overview tone-${severity}`}>
        <PlainStatus data={data}/>
        <article className="panel coastal-wave">
          <div className="coastal-wave-heading">
            <div className="wave-hero">
              <h2>Estimated wave height now</h2>
              <div className="coastal-wave-reading"><strong>{data.wave.valid?n(data.wave.waveHeight,2):"--"}<small>m</small></strong></div>
              <p className="wave-hero-caption">Calculated from water pressure · <b>{n(data.wave.filteredPressure,2)} kPa</b></p>
            </div>
            <SeaCondition height={data.wave.valid?data.wave.waveHeight:null}/>
            <div className={`ai-prediction is-${data.ai.status.toLowerCase()}`}>
              <span>Research estimate in {data.ai.horizonMinutes||horizon} minutes</span>
              {data.ai.status==="READY"?<strong>{n(data.ai.predictedWaveHeight,2)}<small>m</small></strong>:<strong className="prediction-pending">Not ready</strong>}
              <p>{data.ai.status==="READY"?"Research estimate, not an official forecast":"Waiting for enough readings to create an estimate."}</p>
              <button className="model-chip" onClick={()=>setPage("settings")} title="Open model and prediction settings">About estimate</button>
            </div>
          </div>
          <div className="chart-heading"><h3>Measured wave height and research estimate</h3></div>
          <OverviewTrend data={data}/>
        </article>
        <dl className="coastal-readings" aria-label="Current station readings">
          <ReadingCard icon={<Wind aria-hidden="true"/>} name="Wind" chip={data.status.windDirection||"No data"}
            value={n(data.status.windSpeed)} unit="km/h"
            note="Wind affecting the buoy"
            trendValues={data.status.sensorHistory.map(row=>row.windSpeed)}
            stateText={data.status.windSpeed==null?"Waiting for wind data":"Blowing "+(data.status.windDirection||"from an unknown direction")}
            stateTone="info"/>
          <ReadingCard icon={<Waves aria-hidden="true"/>} name="Water pressure" chip={data.wave.valid?"Reading":"No sensor"}
            value={n(data.wave.filteredPressure,2)} unit="kPa"
            note="Used to estimate wave height"
            trendValues={data.wave.history.map(row=>row.filteredPressure??null)}
            stateText={data.wave.valid?`Estimate ${n(data.wave.waveHeight,2)} m · quality ${Math.round((data.wave.quality??0)*100)}%`:"Waiting for a valid pressure reading"}
            stateTone={data.wave.valid?"ok":"info"}/>
          <ReadingCard icon={<BatteryCharging aria-hidden="true"/>} name="Battery" chip={data.battery.status||"--"}
            value={n(data.battery.percentage,0)} unit="%" meter={data.battery.percentage}
            note="Available energy for reporting"
            trendValues={data.battery.history.map(row=>row.percentage)}
            stateText={data.battery.estimatedRuntimeHours!=null?`About ${n(data.battery.estimatedRuntimeHours,1)} h left`:"Runtime unknown"}
            stateTone={data.battery.percentage!=null&&data.battery.percentage<30?"info":"ok"}/>
          <ReadingCard icon={<Zap aria-hidden="true"/>} name="Solar input" chip={data.solar.charging?"Charging":data.solar.status||"--"}
            value={n(data.solar.power)} unit="W"
            note="Solar energy reaching the battery"
            trendValues={data.status.sensorHistory.map(row=>row.solarPower)}
            stateText={data.solar.charging?"Charging the battery now":"Not charging right now"}
            stateTone={data.solar.charging?"ok":"info"}/>
        </dl>
        <div className="coastal-footer">
          <span><MapPin aria-hidden="true"/><span><em>Location</em><b>{geofenceLabel(data.current.security.geofenceState)}</b></span></span>
          <span><Thermometer aria-hidden="true"/><span><em>Inside box</em><b>{n(data.status.internalTemperature)} °C</b></span></span>
          <span><Compass aria-hidden="true"/><span><em>Drift</em><b>{n(data.gps.anchorDistanceMeters)} m</b></span></span>
          <span className="footer-updated">Updated {lastUpdate}</span>
        </div>
        <p className="overview-tip">Use this page for a quick status. Open Sensors for device readings, GPS &amp; safety for the buoy position, and Alerts &amp; records for warnings and saved data.</p>
        <p className="overview-tip">Values are from {simulator?"the presentation simulator":"the buoy"}. Wave height and prediction are research estimates, not official marine warnings.</p>
      </section>}</main>
  </div>;
}
