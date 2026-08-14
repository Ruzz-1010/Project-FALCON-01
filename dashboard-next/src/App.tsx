import { lazy, Suspense, useEffect, useMemo, useRef, useState } from "react";
import { Activity, BatteryCharging, Bell, Cpu, Database, Gauge, LayoutDashboard, MapPinned, Menu, Moon, Navigation, Orbit, PanelLeftClose, PanelLeftOpen, Satellite, Settings2, ShieldCheck, Siren, Sparkles, Sun, Thermometer, Waves, Wind, X, Zap } from "lucide-react";
import { getOverview } from "./api";
import type { DashboardData } from "./types";
import WavePage from "./WavePage";
import TelemetryChart from "./TelemetryChart";
const MotionPage = lazy(() => import("./MotionPage"));
const GpsPage = lazy(() => import("./GpsPage"));
const PowerPage = lazy(() => import("./PowerPage"));
const SystemPage = lazy(() => import("./SystemPage"));
const AlertsPage = lazy(() => import("./AlertsPage"));
const LogsPage = lazy(() => import("./LogsPage"));
const SettingsPage = lazy(() => import("./SettingsPage"));

const navigation = [
  ["overview", "Overview", "Mission control", LayoutDashboard, true], ["wave", "Wave AI", "Current & predicted", Waves, true],
  ["motion", "Motion", "BNO085 orientation", Orbit, true], ["gps", "GPS", "Position & drift", MapPinned, true],
  ["power", "Power", "Battery & solar", BatteryCharging, true], ["system", "System", "Health & settings", Cpu, true],
  ["activity", "Alerts", "Operational events", Siren, true], ["logs", "Logs", "History & exports", Database, true],
  ["settings", "Settings", "Station configuration", Settings2, true]
] as const;

const n = (value: number | null | undefined, digits = 1) => value == null ? "--" : value.toFixed(digits);

function LegacyTrend({ data }: { data: DashboardData }) {
  const points = data.wave.history.filter((item) => item.waveHeight != null).slice(-36);
  if (points.length < 2) return <div className="chart-empty">Collecting wave history…</div>;
  const values = points.map((item) => item.waveHeight as number);
  const forecast = data.ai.predictedWaveHeight;
  const all = forecast == null ? values : [...values, forecast];
  const min = Math.max(0, Math.min(...all) - .15), max = Math.max(...all) + .15;
  const xy = values.map((value, index) => `${32 + index / Math.max(1, values.length - 1) * 668},${184 - (value - min) / Math.max(.01, max - min) * 142}`);
  const last = xy.at(-1)!.split(",").map(Number);
  const forecastY = forecast == null ? null : 184 - (forecast - min) / Math.max(.01, max - min) * 142;
  return <svg className="trend" viewBox="0 0 740 220" role="img" aria-label="Observed and predicted wave height">
    {[0, 1, 2, 3].map((row) => <line key={row} x1="32" y1={42 + row * 47} x2="700" y2={42 + row * 47} className="gridline" />)}
    <polyline points={xy.join(" ")} className="wave-line" />
    {forecastY != null && <><line x1={last[0]} y1={last[1]} x2="700" y2={forecastY} className="forecast-line" /><circle cx="700" cy={forecastY} r="5" className="forecast-dot" /></>}
  </svg>;
}

void LegacyTrend;
function Trend({data,showPrediction}:{data:DashboardData;showPrediction:boolean}){
  return <TelemetryChart points={data.wave.history.slice(-42).map(item=>({value:item.waveHeight,recordedAt:item.recordedAt}))} forecast={showPrediction?data.ai.predictedWaveHeight:null} forecastLabel={`${data.ai.horizonMinutes} MIN AI`} unit=" m" color="#70b7bd" secondaryColor="#c49355" primaryLabel="Current wave" secondaryLabel="Predicted trend" minimumZero label="Observed and predicted wave height" variant="minimal" showSecondary/>;
}

function App() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [collapsed, setCollapsed] = useState(false);
  const [page, setPage] = useState<"overview"|"wave"|"motion"|"gps"|"power"|"system"|"activity"|"logs"|"settings">("overview");
  const [horizon, setHorizon] = useState(10);
  const [pollInterval,setPollInterval]=useState(()=>Number(localStorage.getItem("falcon-next-poll"))||2000);
  const [refreshToken, setRefreshToken] = useState(0);
  const [alertToast,setAlertToast]=useState<{code:string;message:string;severity:string}|null>(null);
  const [pageEntering,setPageEntering]=useState(true);
  const [overviewPredictionVisible,setOverviewPredictionVisible]=useState(false);
  const knownAlerts=useRef<Set<string>|null>(null);
  const [theme, setTheme] = useState<"dark" | "light">(() => (localStorage.getItem("falcon-next-theme") as "dark" | "light") || "dark");

  useEffect(() => { document.documentElement.dataset.theme = theme; localStorage.setItem("falcon-next-theme", theme); }, [theme]);
  useEffect(()=>localStorage.setItem("falcon-next-poll",String(pollInterval)),[pollInterval]);
  useEffect(() => {
    let active = true;
    const refresh = async () => { try { const next = await getOverview(horizon); if (active) { setData(next); setError(null); } } catch (reason) { if (active) setError(reason instanceof Error ? reason.message : "Edge service unavailable"); } };
    refresh(); const timer = window.setInterval(refresh, pollInterval); return () => { active = false; window.clearInterval(timer); };
  }, [horizon, refreshToken, pollInterval]);
  useEffect(()=>{if(!data)return;const next=new Set(data.status.alerts.map(item=>item.code));if(knownAlerts.current){const fresh=data.status.alerts.find(item=>!knownAlerts.current?.has(item.code));if(fresh){setAlertToast(fresh);const timer=window.setTimeout(()=>setAlertToast(null),8000);knownAlerts.current=next;return()=>window.clearTimeout(timer)}}knownAlerts.current=next},[data]);
  useEffect(()=>{if(!data)return;setPageEntering(true);const timer=window.setTimeout(()=>setPageEntering(false),850);return()=>window.clearTimeout(timer)},[page,!!data]);

  const lastUpdate = useMemo(() => data?.status.lastUpdate ? new Date(data.status.lastUpdate).toLocaleTimeString() : "--:--:--", [data]);
  const online = data?.status.system === "ONLINE";
  return <div className={`app ${collapsed ? "is-collapsed" : ""} ${sidebarOpen ? "is-menu-open" : ""}`}>
    <button className="scrim" onClick={() => setSidebarOpen(false)} aria-label="Close navigation" />
    <aside className="sidebar">
      <div className="brand"><img src="/falcon-logo.jpg" alt="FALCON logo" /><div><strong>FALCON-01</strong><span>COASTAL STATION</span></div></div>
      <nav>{navigation.map(([key, label, detail, Icon, ready]) => <button key={key} className={`nav-item ${page === key ? "is-active" : ""}`} disabled={!ready} onClick={()=>{if(ready){setPage(key as "overview"|"wave"|"motion"|"gps"|"power"|"system"|"activity"|"logs"|"settings");setSidebarOpen(false);}}} title={!ready ? `${label} migration pending` : label}><Icon /><span><b>{label}</b><small>{ready ? detail : "Migration pending"}</small></span></button>)}</nav>
      <div className="side-foot"><i className={online ? "online" : ""} /><span><b>{online ? "EDGE ONLINE" : "EDGE CONNECTING"}</b><small>FALCON OS · DASHBOARD v4.0</small></span></div>
    </aside>
    <main>
      <header className="topbar"><div className="title"><button className="mobile-menu" onClick={() => setSidebarOpen(true)} aria-label="Open navigation"><Menu /></button><button className="collapse" onClick={() => setCollapsed(!collapsed)} aria-label={collapsed?"Expand sidebar":"Collapse sidebar"} title={collapsed?"Expand sidebar":"Collapse sidebar"}>{collapsed?<PanelLeftOpen/>:<PanelLeftClose/>}</button><div><span>PROJECT FALCON / DASHBOARD NEXT</span><h1>{page === "wave" ? "Wave intelligence" : page === "motion" ? "Buoy motion" : page === "gps" ? "GPS and drift" : page === "power" ? "Power system" : page === "system" ? "System health" : page === "activity" ? "Alerts and events" : page === "logs" ? "Operational logs" : page === "settings" ? "Station settings" : "Mission control"}</h1></div></div><div className="top-actions"><div><span>LAST UPDATE</span><b>{lastUpdate}</b></div><div><span>SOURCE</span><b>{data?.status.dataSource?.toUpperCase() || "--"}</b></div><button className="notification-button" onClick={()=>setPage("activity")} aria-label="Open alerts"><Bell/>{data?.status.alerts.length?<b>{data.status.alerts.length}</b>:null}</button><button onClick={() => setTheme(theme === "dark" ? "light" : "dark")} aria-label="Toggle theme">{theme === "dark" ? <Sun /> : <Moon />}</button><span className={`live ${online ? "is-online" : ""}`}><i />{online ? "LIVE" : "OFFLINE"}</span></div></header>
      {error && <div className="error-banner"><Activity /> <span><b>Edge connection interrupted</b>{error}</span></div>}
      {alertToast&&<button className={`alert-toast is-${alertToast.severity}`} onClick={()=>{setPage("activity");setAlertToast(null)}}><Bell/><span><b>{alertToast.code.replaceAll("_"," ")}</b>{alertToast.message}</span><X/></button>}
      {data&&pageEntering&&<div className="overview-loader page-loader" role="status" aria-label="Opening dashboard page"><div className="overview-loader-mark"><i/><img src="/falcon-logo.jpg" alt=""/></div><b>FALCON-01</b><span>Preparing {page==="overview"?"mission overview":page==="wave"?"wave intelligence":page==="motion"?"digital twin":page==="gps"?"position view":page==="power"?"power telemetry":page==="system"?"system diagnostics":page==="activity"?"alert history":page==="logs"?"operational logs":"station settings"}</span><div className="overview-loader-line"><i/></div></div>}
      {!data ? <div className="loading"><img src="/falcon-logo.jpg" alt="" /><b>Connecting to FALCON edge service</b><span>Loading verified telemetry…</span></div> : page === "wave" ? <WavePage data={data} horizon={horizon} onHorizon={setHorizon} onScenarioApplied={()=>setRefreshToken(value=>value+1)}/> : page === "motion" ? <Suspense fallback={<div className="loading"><img src="/falcon-logo.jpg" alt=""/><b>Loading digital twin</b><span>Preparing Fusion CAD and marine scene…</span></div>}><MotionPage data={data}/></Suspense> : page === "gps" ? <Suspense fallback={<div className="loading"><img src="/falcon-logo.jpg" alt=""/><b>Loading coastal map</b><span>Preparing Puerto Princesa position view…</span></div>}><GpsPage data={data}/></Suspense> : page === "power" ? <Suspense fallback={<div className="loading"><img src="/falcon-logo.jpg" alt=""/><b>Loading power telemetry</b><span>Preparing energy and thermal history…</span></div>}><PowerPage data={data}/></Suspense> : page === "system" ? <Suspense fallback={<div className="loading"><img src="/falcon-logo.jpg" alt=""/><b>Loading diagnostics</b><span>Checking edge services and sensor health…</span></div>}><SystemPage data={data}/></Suspense> : page === "activity" ? <Suspense fallback={<div className="loading"><img src="/falcon-logo.jpg" alt=""/><b>Loading alert history</b><span>Reading local operational events…</span></div>}><AlertsPage data={data}/></Suspense> : page === "logs" ? <Suspense fallback={<div className="loading"><img src="/falcon-logo.jpg" alt=""/><b>Loading local archive</b><span>Reading telemetry and model records…</span></div>}><LogsPage/></Suspense> : page === "settings" ? <Suspense fallback={<div className="loading"><img src="/falcon-logo.jpg" alt=""/><b>Loading settings</b><span>Preparing local controls…</span></div>}><SettingsPage theme={theme} onTheme={setTheme} horizon={horizon} onHorizon={setHorizon} pollInterval={pollInterval} onPollInterval={setPollInterval} onRefresh={()=>setRefreshToken(value=>value+1)}/></Suspense> : <section className={`content overview-page ${pageEntering?"is-entering":""}`}>
        <div className="summary">
          <article><ShieldCheck /><span>System status<b className="good">{data.status.system}</b><small>{data.status.sensorsOnline}/{data.status.sensorsExpected} sensors online</small></span></article>
          <article><Waves /><span>Current wave<b>{n(data.wave.waveHeight, 2)} m</b><small>{data.wave.waveHeightState}</small></span></article>
          <article><Activity /><span>Predicted · {data.ai.horizonMinutes} min<b>{n(data.ai.predictedWaveHeight, 2)} m</b><small>{data.ai.status}</small></span></article>
          <article><Bell /><span>Sea condition<b>{data.ai.seaCondition}</b><small>{data.ai.confidence}% confidence</small></span></article>
        </div>
        <div className="ribbon"><span><Wind />Wind direction<b>{data.status.windDirection || "--"}</b></span><span><Satellite />GPS lock<b>{data.gps.valid ? `${data.gps.fix} · ${data.gps.satellites} SAT` : "NO FIX"}</b></span><span><BatteryCharging />Battery<b>{n(data.battery.percentage, 0)}%</b></span><span><Thermometer />Internal temp<b>{n(data.status.internalTemperature)} °C</b></span><span><Bell />Active alerts<b>{data.status.alerts.length}</b></span></div>
        <div className="dashboard-grid"><article className="panel chart-panel"><header><div className="panel-title"><Waves /><div><span>MARINE SIGNAL</span><h2>Wave height forecast</h2></div></div><em>LIVE</em></header><div className="prediction-controls"><div className="readouts"><span>Current <b>{n(data.wave.waveHeight, 2)} m</b></span>{overviewPredictionVisible&&<span>{data.ai.horizonMinutes}-min forecast <b>{n(data.ai.predictedWaveHeight, 2)} m</b></span>}</div><button className={overviewPredictionVisible?"is-active":""} onClick={()=>setOverviewPredictionVisible(value=>!value)}><Sparkles />{overviewPredictionVisible?"Hide prediction":`Predict next ${data.ai.horizonMinutes} min`}</button></div><Trend data={data} showPrediction={overviewPredictionVisible}/><footer>SIMULATED PRESENTATION DATA · NOT SAFETY VALIDATED</footer></article>
          <article className="panel snapshot"><header><div className="panel-title"><Gauge /><div><span>ENVIRONMENT</span><h2>Coastal snapshot</h2></div></div><em>SIMULATED</em></header><dl><div><dt><Wind />Wind</dt><dd>{n(data.status.windSpeed)} km/h · {data.status.windDirection}</dd></div><div><dt><Waves />Water pressure</dt><dd>{n(data.wave.pressure)} kPa</dd></div><div><dt><Navigation />GPS</dt><dd>{data.gps.fix} · {data.gps.satellites} SAT</dd></div><div><dt><BatteryCharging />Battery</dt><dd>{n(data.battery.percentage, 0)}% · {data.battery.status}</dd></div><div><dt><Zap />Solar</dt><dd>{data.solar.status} · {n(data.solar.power)} W</dd></div><div><dt><Thermometer />Temperature</dt><dd>{n(data.status.internalTemperature)} °C</dd></div></dl></article>
        </div>
      </section>}
    </main>
  </div>;
}

export default App;
