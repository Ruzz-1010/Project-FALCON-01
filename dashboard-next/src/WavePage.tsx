import { useEffect, useState } from "react";
import { Activity, ArrowRight, BrainCircuit, CheckCircle2, Clock3, Database, Gauge, TrendingDown, TrendingUp, Waves, Wind } from "lucide-react";
import { getScenario, setScenario } from "./api";
import type { DashboardData, ScenarioState } from "./types";

const n = (value: number | null | undefined, digits = 1) => value == null ? "--" : value.toFixed(digits);
const scenarioLabels: Record<string,string> = { normal:"Normal operation", rough_sea:"Rough sea", low_battery:"Low battery", overheating:"Internal overheating", sensor_fault:"Wave sensor failure" };

function ForecastChart({data}:{data:DashboardData}) {
  const rows=data.wave.history.filter(row=>row.waveHeight!=null).slice(-50),values=rows.map(row=>row.waveHeight as number),prediction=data.ai.predictedWaveHeight;
  if(values.length<2)return <div className="chart-empty">Collecting scenario-specific wave history…</div>;
  const all=prediction==null?values:[...values,prediction],min=Math.max(0,Math.min(...all)-.18),max=Math.max(...all)+.18;
  const xy=values.map((value,index)=>[42+index/Math.max(1,values.length-1)*610,196-(value-min)/Math.max(.01,max-min)*150]);
  const last=xy.at(-1)!,targetY=prediction==null?null:196-(prediction-min)/Math.max(.01,max-min)*150;
  return <svg className="wave-chart" viewBox="0 0 740 240" role="img" aria-label="Current wave history and AI forecast">
    {[0,1,2,3].map(row=><g key={row}><line x1="42" y1={46+row*50} x2="700" y2={46+row*50} className="gridline"/><text x="34" y={50+row*50} textAnchor="end">{(max-(max-min)*row/3).toFixed(1)}m</text></g>)}
    <polyline points={xy.map(point=>point.join(",")).join(" ")} className="wave-line"/>
    {targetY!=null&&<><line x1={last[0]} y1={last[1]} x2="700" y2={targetY} className="forecast-line"/><circle cx="700" cy={targetY} r="5" className="forecast-dot"/><text x="692" y={targetY-12} textAnchor="end" className="forecast-label">{prediction!.toFixed(2)} m</text></>}
  </svg>;
}

export default function WavePage({data,horizon,onHorizon,onScenarioApplied}:{data:DashboardData;horizon:number;onHorizon:(value:number)=>void;onScenarioApplied:()=>void}){
  const [scenario,setScenarioState]=useState<ScenarioState|null>(null),[busy,setBusy]=useState(false),[controlError,setControlError]=useState<string|null>(null);
  useEffect(()=>{getScenario().then(setScenarioState).catch(error=>setControlError(error.message));},[]);
  const applyScenario=async(value:string)=>{setBusy(true);setControlError(null);try{setScenarioState(await setScenario(value));onScenarioApplied();}catch(error){setControlError(error instanceof Error?error.message:"Scenario update failed");}finally{setBusy(false);}};
  const ai=data.ai,details=ai.explanation?.details,ready=ai.status==="READY";
  return <section className="content wave-page">
    <div className="page-head"><div><span>AI-ASSISTED WAVE FORECAST</span><h1>Wave intelligence</h1><p>Transparent current-versus-predicted output from the local edge model.</p></div><div className="wave-controls"><label>Horizon<select value={horizon} onChange={event=>onHorizon(Number(event.target.value))}><option value="5">5 minutes</option><option value="10">10 minutes</option><option value="15">15 minutes</option></select></label><label>Demo scenario<select disabled={busy||!scenario?.available} value={scenario?.active||"normal"} onChange={event=>applyScenario(event.target.value)}>{(scenario?.scenarios||["normal"]).map(value=><option key={value} value={value}>{scenarioLabels[value]||value}</option>)}</select></label></div></div>
    {controlError&&<div className="inline-error">{controlError}</div>}
    <div className="ai-result-grid"><article className="panel ai-result"><header><div><span>AI PREDICTION</span><h2>Predicted wave height</h2></div><em>{ai.status}</em></header><div className="prediction-value"><strong>{ready?n(ai.predictedWaveHeight,2):"--"}</strong><b>m</b></div><div className="prediction-comparison"><span>Current<b>{n(ai.currentWaveHeight,2)} m</b></span><ArrowRight/><span>Next {ai.horizonMinutes} min<b>{n(ai.predictedWaveHeight,2)} m</b></span></div><footer>{ai.seaCondition} · {ai.direction.toUpperCase()} TREND</footer></article>
      <article className="panel confidence"><header><div><span>MODEL CONFIDENCE</span><h2>Prediction quality</h2></div><CheckCircle2/></header><strong>{ready?ai.confidence:"--"}%</strong><div className="confidence-bar"><i style={{width:`${ready?ai.confidence:0}%`}}/></div><p>{ai.sampleCount} valid samples · {ai.model} {ai.modelVersion}</p></article>
      <article className="panel forecast-status"><header><div><span>FORECAST STATUS</span><h2>Model output context</h2></div>{ai.direction==="up"?<TrendingUp/>:<TrendingDown/>}</header><dl><div><dt>Sea condition</dt><dd>{ai.seaCondition}</dd></div><div><dt>Expected change</dt><dd>{ai.change==null?"--":`${ai.change>=0?"+":""}${n(ai.change,2)} m`}</dd></div><div><dt>Target horizon</dt><dd><Clock3/> {ai.horizonMinutes} min</dd></div><div><dt>Evidence window</dt><dd><Database/> {ai.sampleCount} samples</dd></div></dl><footer>{ai.dataSource.toUpperCase()} · WAVE-ONLY FORECAST</footer></article>
      <article className="panel wave-chart-panel"><header><div><span>LIVE HISTORY + FORECAST</span><h2>Observed and predicted wave height</h2></div><em>SIMULATOR</em></header><ForecastChart data={data}/><footer>Solid line: observed estimates · dashed line: model output</footer></article>
      <article className="panel explanation"><header><div><span>HOW IT WAS PRODUCED</span><h2>Model explanation</h2></div><BrainCircuit/></header><div className="explain-flow"><div><Gauge/><span>Input<b>Pressure + IMU</b></span></div><ArrowRight/><div><Activity/><span>Analysis<b>Recent trend</b></span></div><ArrowRight/><div><Waves/><span>Output<b>{n(ai.predictedWaveHeight,2)} m</b></span></div></div><p>{ai.explanation?.method||ai.unavailableReason||"Waiting for valid model evidence."}</p></article>
      <article className="panel evidence"><header><div><span>MODEL EVIDENCE</span><h2>Calculation details</h2></div><Wind/></header><dl><div><dt>Sample window</dt><dd>{details?n(details.sampleWindowSeconds,1):"--"} sec</dd></div><div><dt>Detected trend</dt><dd>{details?n(details.trendMetersPerMinute,4):"--"} m/min</dd></div><div><dt>Raw projection</dt><dd>{details?n(details.rawProjection,3):"--"} m</dd></div><div><dt>Allowed change</dt><dd>±{details?n(details.maximumAllowedChange,3):"--"} m</dd></div><div><dt>Signal volatility</dt><dd>{details?n(details.residualVolatility,4):"--"} m</dd></div><div><dt>Damping factor</dt><dd>{details?n(details.dampingFactor,3):"--"}</dd></div></dl></article>
    </div>
  </section>;
}
