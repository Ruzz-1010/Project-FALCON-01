import { useEffect, useMemo, useState } from "react";
import { Check, CheckCircle2, Gauge, Waves } from "lucide-react";
import { getScenario, setScenario } from "./api";
import type { DashboardData, ScenarioState } from "./types";
import TelemetryChart from "./TelemetryChart";

const n = (value: number | null | undefined, digits = 1) => value == null ? "--" : value.toFixed(digits);
const scenarioLabels: Record<string,string> = { normal:"Normal operation", rough_sea:"Rough sea", low_battery:"Low battery", overheating:"Internal overheating", sensor_fault:"Wave sensor failure" };
const weights = [["IMU Roll",23],["IMU Pitch",17],["Water Pressure",42],["Wind Speed",13],["Wind Direction",5]] as const;

function LegacyForecastChart({data}:{data:DashboardData}) {
  const rows=data.wave.history.filter(row=>row.waveHeight!=null).slice(-50),values=rows.map(row=>row.waveHeight as number),prediction=data.ai.predictedWaveHeight;
  if(values.length<2)return <div className="chart-empty">Collecting scenario-specific wave history...</div>;
  const all=prediction==null?values:[...values,prediction],min=Math.max(0,Math.min(...all)-.18),max=Math.max(...all)+.18;
  const xy=values.map((value,index)=>[42+index/Math.max(1,values.length-1)*610,196-(value-min)/Math.max(.01,max-min)*150]);
  const last=xy.at(-1)!,targetY=prediction==null?null:196-(prediction-min)/Math.max(.01,max-min)*150;
  return <svg className="wave-chart" viewBox="0 0 740 240" role="img" aria-label="Current wave history and AI forecast">
    {[0,1,2,3].map(row=><g key={row}><line x1="42" y1={46+row*50} x2="700" y2={46+row*50} className="gridline"/><text x="34" y={50+row*50} textAnchor="end">{(max-(max-min)*row/3).toFixed(1)}m</text></g>)}
    <polyline points={xy.map(point=>point.join(",")).join(" ")} className="wave-line"/>
    {targetY!=null&&<><line x1={last[0]} y1={last[1]} x2="700" y2={targetY} className="forecast-line"/><circle cx="700" cy={targetY} r="5" className="forecast-dot"/><text x="692" y={targetY-12} textAnchor="end" className="forecast-label">{prediction!.toFixed(2)} m</text></>}
  </svg>;
}

void LegacyForecastChart;
function ForecastChart({data}:{data:DashboardData}){
  return <TelemetryChart points={data.wave.history.slice(-50).map(item=>({value:item.waveHeight,recordedAt:item.recordedAt}))} forecast={data.ai.predictedWaveHeight} forecastLabel={`${data.ai.horizonMinutes} MIN FORECAST`} unit=" m" color="#48d9df" minimumZero label="Live wave history and forecast"/>;
}

export default function WavePage({data,horizon,onHorizon,onScenarioApplied}:{data:DashboardData;horizon:number;onHorizon:(value:number)=>void;onScenarioApplied:()=>void}){
  const [scenario,setScenarioState]=useState<ScenarioState|null>(null),[busy,setBusy]=useState(false),[controlError,setControlError]=useState<string|null>(null);
  useEffect(()=>{getScenario().then(setScenarioState).catch(error=>setControlError(error.message));},[]);
  const applyScenario=async(value:string)=>{setBusy(true);setControlError(null);try{setScenarioState(await setScenario(value));onScenarioApplied();}catch(error){setControlError(error instanceof Error?error.message:"Scenario update failed");}finally{setBusy(false);}};
  const ai=data.ai,ready=ai.status==="READY",current=ai.currentWaveHeight,predicted=ai.predictedWaveHeight;
  const midpoint=current!=null&&predicted!=null?current+(predicted-current)*.55:null;
  const quality=ai.confidence>=85?"High confidence":ai.confidence>=70?"Good confidence":"Review required";
  const agreement=ai.confidence>=85?"STRONG":ai.confidence>=70?"GOOD":"LIMITED";
  const analysis=useMemo(()=>{
    const wind=data.status.sensorHistory.filter(row=>row.windSpeed!=null).slice(-42);
    const windStart=wind.at(0)?.windSpeed,windEnd=wind.at(-1)?.windSpeed??data.status.windSpeed;
    const tilt=Math.hypot(data.wave.roll||0,data.wave.pitch||0);
    const pressureDirection=(ai.direction==="up"?"increased":"decreased");
    const pressureDelta=Math.abs((ai.change||0)*2.3);
    return [
      `Water pressure ${pressureDirection} by ${n(pressureDelta,2)} kPa across recent samples.`,
      windStart!=null&&windEnd!=null?`Wind speed ${windEnd>=windStart?"increased":"decreased"} from ${n(windStart)} to ${n(windEnd)} km/h.`:`Wind speed is currently ${n(data.status.windSpeed)} km/h.`,
      `Buoy oscillation is ${tilt<5?"within normal range":"elevated"} at ${n(tilt,2)}° combined roll/pitch.`,
      `Historical window contains ${ai.sampleCount} valid wave samples with an ${ai.direction.toUpperCase()} trend.`
    ];
  },[ai.change,ai.direction,ai.sampleCount,data.status.sensorHistory,data.status.windSpeed,data.wave.pitch,data.wave.roll]);

  return <section className="content wave-page wave-report">
    <div className="page-head"><div><span>AI-ASSISTED WAVE FORECAST</span><h1>Wave intelligence</h1><p>Current conditions, model evidence, and the expected wave state in one transparent operational view.</p></div><div className="wave-controls"><label>Horizon<select value={horizon} onChange={event=>onHorizon(Number(event.target.value))}><option value="5">5 minutes</option><option value="10">10 minutes</option><option value="15">15 minutes</option></select></label><label>Demo scenario<select disabled={busy||!scenario?.available} value={scenario?.active||"normal"} onChange={event=>applyScenario(event.target.value)}>{(scenario?.scenarios||["normal"]).map(value=><option key={value} value={value}>{scenarioLabels[value]||value}</option>)}</select></label></div></div>
    {controlError&&<div className="inline-error">{controlError}</div>}
    <div className="wave-report-grid">
      <article className="panel forecast-result">
        <header><div><span>AI PREDICTION</span><h2>Wave forecast result</h2></div><em>DEMO AI</em></header>
        <div className="result-core"><span>Predicted Wave Height</span><strong>{ready?n(predicted,2):"--"}<small>m</small></strong><p>Current: {n(current,2)} m · {ai.direction.toUpperCase()} trend</p></div>
        <dl className="result-metrics"><div><dt>Confidence</dt><dd>{ai.confidence}%</dd></div><div><dt>Prediction Time</dt><dd>Next {ai.horizonMinutes} minutes</dd></div><div><dt>Status</dt><dd>{ai.seaCondition}</dd></div></dl>
        <section className="prediction-inputs"><div className="inputs-heading"><span>Prediction based on</span><small>Configured demo-model input weights</small></div><strong className="weight-total">100% total</strong><div className="input-list">{weights.map(([label,value])=><div className="input-row" key={label}><i><Check/></i><span>{label}</span><b>{value}%</b><div className="input-track"><em style={{width:`${value}%`}}/></div></div>)}</div></section>
      </article>

      <article className="panel wave-chart-panel report-chart"><header><div><span>LIVE WAVE GRAPH</span><h2>Observed and predicted wave energy</h2></div><em>HISTORY + FORECAST</em></header><div className="chart-legend"><span><i/>Current wave</span><span><i/>Predicted wave</span></div><ForecastChart data={data}/><footer><span>Hover-ready timestamped local history</span><span>Dashed segment indicates model output</span></footer></article>

      <article className="panel ai-summary"><header><div><span>EXPLAINABLE AI</span><h2>AI analysis summary</h2></div><em>COMPLETE</em></header><ul>{analysis.map(item=><li key={item}><i/>{item}</li>)}</ul><div className="therefore"><span>Therefore</span><strong>{n(predicted,2)} meters · {ai.seaCondition}</strong><small>Expected within {ai.horizonMinutes} minutes</small></div></article>

      <article className="panel report-confidence"><header><div><span>MODEL CONFIDENCE</span><h2>Prediction confidence</h2></div><CheckCircle2/></header><strong>{ai.confidence}%</strong><div className="confidence-bar"><i style={{width:`${ai.confidence}%`}}/></div><b>{quality}</b><p>Recent signals are stable and the trend fit has low disagreement.</p></article>

      <article className="panel prediction-timeline"><header><div><span>PREDICTION TIMELINE</span><h2>Expected wave progression</h2></div><Waves/></header><div><section><span>NOW</span><strong>{n(current,2)} m</strong><small>Current estimate</small></section><i/><section><span>{Math.max(1,Math.round(ai.horizonMinutes/2))} MIN</span><strong>{n(midpoint,2)} m</strong><small>Near-term</small></section><i/><section><span>{ai.horizonMinutes} MIN</span><strong>{n(predicted,2)} m</strong><small>Selected horizon</small></section></div></article>

      <article className="panel prediction-quality"><header><div><span>PREDICTION QUALITY</span><h2>Presentation validation</h2></div><em>NOT FIELD ACCURACY</em></header><dl><div><dt>Samples used</dt><dd>{ai.sampleCount}</dd></div><div><dt>Model confidence</dt><dd>{ai.confidence}%</dd></div><div><dt>Signal agreement</dt><dd>{agreement}</dd></div><div><dt>Data source</dt><dd>{ai.dataSource.toUpperCase()}</dd></div></dl><footer>Demo output for presentation. Field calibration and validation are still required.</footer></article>
    </div>
  </section>;
}
