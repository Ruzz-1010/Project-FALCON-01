import { useEffect, useMemo, useState } from "react";
import { Activity, BatteryCharging, Bell, FileText, LayoutDashboard, MapPin, Menu, Moon, Move3d, Settings, ShieldCheck, Sun, Waves, X } from "lucide-react";
import { getOverview } from "./api";
import type { DashboardData } from "./types";

const navigation = [
  ["Overview", "Mission control", LayoutDashboard, true], ["Wave AI", "Current & predicted", Waves, false],
  ["Motion", "BNO085 orientation", Move3d, false], ["GPS", "Position & drift", MapPin, false],
  ["Power", "Battery & solar", BatteryCharging, false], ["System", "Health & settings", ShieldCheck, false],
  ["Alerts", "Operational events", Bell, false], ["Logs", "History & exports", FileText, false],
  ["Settings", "Station configuration", Settings, false]
] as const;

const n = (value: number | null | undefined, digits = 1) => value == null ? "--" : value.toFixed(digits);

function Trend({ data }: { data: DashboardData }) {
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

function App() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [collapsed, setCollapsed] = useState(false);
  const [theme, setTheme] = useState<"dark" | "light">(() => (localStorage.getItem("falcon-next-theme") as "dark" | "light") || "dark");

  useEffect(() => { document.documentElement.dataset.theme = theme; localStorage.setItem("falcon-next-theme", theme); }, [theme]);
  useEffect(() => {
    let active = true;
    const refresh = async () => { try { const next = await getOverview(); if (active) { setData(next); setError(null); } } catch (reason) { if (active) setError(reason instanceof Error ? reason.message : "Edge service unavailable"); } };
    refresh(); const timer = window.setInterval(refresh, 2000); return () => { active = false; window.clearInterval(timer); };
  }, []);

  const lastUpdate = useMemo(() => data?.status.lastUpdate ? new Date(data.status.lastUpdate).toLocaleTimeString() : "--:--:--", [data]);
  const online = data?.status.system === "ONLINE";
  return <div className={`app ${collapsed ? "is-collapsed" : ""} ${sidebarOpen ? "is-menu-open" : ""}`}>
    <button className="scrim" onClick={() => setSidebarOpen(false)} aria-label="Close navigation" />
    <aside className="sidebar">
      <div className="brand"><img src="/falcon-logo.jpg" alt="FALCON logo" /><div><strong>FALCON-01</strong><span>COASTAL STATION</span></div></div>
      <nav>{navigation.map(([label, detail, Icon, ready]) => <button key={label} className={`nav-item ${ready ? "is-active" : ""}`} disabled={!ready} title={!ready ? `${label} migration pending` : label}><Icon /><span><b>{label}</b><small>{ready ? detail : "Migration pending"}</small></span></button>)}</nav>
      <div className="side-foot"><i className={online ? "online" : ""} /><span><b>{online ? "EDGE ONLINE" : "EDGE CONNECTING"}</b><small>React migration · Phase 1</small></span></div>
    </aside>
    <main>
      <header className="topbar"><div className="title"><button className="mobile-menu" onClick={() => setSidebarOpen(true)}><Menu /></button><button className="collapse" onClick={() => setCollapsed(!collapsed)}>{collapsed ? <Menu /> : <X />}</button><div><span>PROJECT FALCON / DASHBOARD NEXT</span><h1>Mission control</h1></div></div><div className="top-actions"><div><span>LAST UPDATE</span><b>{lastUpdate}</b></div><div><span>SOURCE</span><b>{data?.status.dataSource?.toUpperCase() || "--"}</b></div><button onClick={() => setTheme(theme === "dark" ? "light" : "dark")} aria-label="Toggle theme">{theme === "dark" ? <Sun /> : <Moon />}</button><span className={`live ${online ? "is-online" : ""}`}><i />{online ? "LIVE" : "OFFLINE"}</span></div></header>
      {error && <div className="error-banner"><Activity /> <span><b>Edge connection interrupted</b>{error}</span></div>}
      {!data ? <div className="loading"><img src="/falcon-logo.jpg" alt="" /><b>Connecting to FALCON edge service</b><span>Loading verified telemetry…</span></div> : <section className="content">
        <div className="summary">
          <article><ShieldCheck /><span>System status<b className="good">{data.status.system}</b><small>{data.status.sensorsOnline}/{data.status.sensorsExpected} sensors online</small></span></article>
          <article><Waves /><span>Current wave<b>{n(data.wave.waveHeight, 2)} m</b><small>{data.wave.waveHeightState}</small></span></article>
          <article><Activity /><span>Predicted · {data.ai.horizonMinutes} min<b>{n(data.ai.predictedWaveHeight, 2)} m</b><small>{data.ai.status}</small></span></article>
          <article><Bell /><span>Sea condition<b>{data.ai.seaCondition}</b><small>{data.ai.confidence}% confidence</small></span></article>
        </div>
        <div className="ribbon"><span>Wind direction<b>{data.status.windDirection || "--"}</b></span><span>GPS lock<b>{data.gps.valid ? `${data.gps.fix} · ${data.gps.satellites} SAT` : "NO FIX"}</b></span><span>Battery<b>{n(data.battery.percentage, 0)}%</b></span><span>Internal temp<b>{n(data.status.internalTemperature)} °C</b></span><span>Active alerts<b>{data.status.alerts.length}</b></span></div>
        <div className="dashboard-grid"><article className="panel chart-panel"><header><div><span>PRIMARY MARINE SIGNAL</span><h2>Wave height · observed to forecast</h2></div><em>LIVE · 2 SEC</em></header><div className="readouts"><span>Current <b>{n(data.wave.waveHeight, 2)} m</b></span><span>Forecast <b>{n(data.ai.predictedWaveHeight, 2)} m</b></span></div><Trend data={data} /><footer>SIMULATED PRESENTATION DATA · NOT SAFETY VALIDATED</footer></article>
          <article className="panel snapshot"><header><div><span>LIVE SENSORS</span><h2>Coastal snapshot</h2></div><em>SIMULATED</em></header><dl><div><dt>Wind</dt><dd>{n(data.status.windSpeed)} km/h · {data.status.windDirection}</dd></div><div><dt>Water pressure</dt><dd>{n(data.wave.pressure)} kPa</dd></div><div><dt>GPS</dt><dd>{data.gps.fix} · {data.gps.satellites} SAT</dd></div><div><dt>Battery</dt><dd>{n(data.battery.percentage, 0)}% · {data.battery.status}</dd></div><div><dt>Solar</dt><dd>{data.solar.status} · {n(data.solar.power)} W</dd></div><div><dt>Internal temperature</dt><dd>{n(data.status.internalTemperature)} °C</dd></div></dl></article>
        </div>
      </section>}
    </main>
  </div>;
}

export default App;
