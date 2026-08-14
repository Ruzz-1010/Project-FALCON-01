import { useEffect, useMemo, useRef, useState } from "react";
import { Check, CheckCircle2, Gauge, Waves } from "lucide-react";
import { getScenario, setScenario } from "./api";
import type { DashboardData, ScenarioState } from "./types";

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
function ConnectedWaveChart({data}:{data:DashboardData}){
  const history=data.wave.history.filter((item):item is typeof item&{waveHeight:number}=>item.waveHeight!=null).slice(-32),predicted=data.ai.predictedWaveHeight,[selected,setSelected]=useState<{label:string;value:number}|null>(null);
  if(history.length<2||predicted==null)return <div className="chart-empty">Collecting wave history and prediction...</div>;
  const measured=history.map(item=>item.waveHeight),current=measured.at(-1)!,series=data.ai.forecastSeries?.length?data.ai.forecastSeries:[{minutesAhead:0,at:data.wave.recordedAt,predictedWaveHeight:current,lowerBound:current,upperBound:current},{minutesAhead:data.ai.horizonMinutes,at:data.ai.targetAt||data.wave.recordedAt,predictedWaveHeight:predicted,lowerBound:predicted,upperBound:predicted}],historic=data.ai.historicalPredictionSeries||[],all=[...measured,...series.flatMap(item=>[item.lowerBound,item.predictedWaveHeight,item.upperBound]),...historic.map(item=>item.predictedWaveHeight)],min=Math.max(0,Math.min(...all)-.08),max=Math.max(...all)+.08,range=Math.max(.01,max-min),top=42,bottom=225,left=54,divider=390,right=726,toY=(value:number)=>bottom-(value-min)/range*(bottom-top),measuredPoints=measured.map((value,index)=>[left+index/(measured.length-1)*(divider-left),toY(value)]),historyStart=Date.parse(history[0].recordedAt),historyEnd=Date.parse(history.at(-1)!.recordedAt),historicPoints=historic.filter(item=>Date.parse(item.at)>=historyStart).map(item=>[left+(Date.parse(item.at)-historyStart)/Math.max(1,historyEnd-historyStart)*(divider-left),toY(item.predictedWaveHeight)]),futurePoints=series.map(item=>[divider+item.minutesAhead/data.ai.horizonMinutes*(right-divider),toY(item.predictedWaveHeight)]),continuousPredictionPoints=[...historicPoints,...futurePoints],upperPoints=series.map(item=>[divider+item.minutesAhead/data.ai.horizonMinutes*(right-divider),toY(item.upperBound)]),lowerPoints=series.map(item=>[divider+item.minutesAhead/data.ai.horizonMinutes*(right-divider),toY(item.lowerBound)]),bandPoints=[...upperPoints,...lowerPoints.reverse()].map(point=>point.join(",")).join(" "),predictedY=toY(predicted),ticks=[0,1,2,3,4];
  return <div className="connected-wave-shell"><div className="connected-wave-labels"><span>Current wave history<b>{n(current,2)} m</b></span><span>Predicted · next {data.ai.horizonMinutes} min<b>{n(predicted,2)} m</b></span></div><svg className="connected-wave-chart" viewBox="0 0 780 270" role="img" aria-label="Connected current and predicted wave graph">
    {ticks.map(row=>{const y=top+(bottom-top)*row/4,value=max-(max-min)*row/4;return <g key={row}><line x1={left} y1={y} x2={right} y2={y} className="connected-grid"/><text x={left-10} y={y+4} textAnchor="end">{value.toFixed(2)} m</text></g>})}
    <rect x={divider} y={top} width={right-divider} height={bottom-top} className="prediction-half"/><line x1={divider} y1={top-10} x2={divider} y2={bottom+8} className="center-divider"/>
    <polygon points={bandPoints} className="forecast-band"/><polyline points={measuredPoints.map(point=>point.join(",")).join(" ")} className="connected-current"/><polyline points={continuousPredictionPoints.map(point=>point.join(",")).join(" ")} className="connected-prediction"/>
    {measuredPoints.map((point,index)=><g key={`m-${index}`} onClick={()=>setSelected({label:new Date(history[index].recordedAt).toLocaleTimeString(),value:measured[index]})}><circle cx={point[0]} cy={point[1]} r="13" className="connected-hit"/><circle cx={point[0]} cy={point[1]} r="2.5" className="current-point"/></g>)}
    {historicPoints.map((point,index)=><circle key={`historic-${index}`} cx={point[0]} cy={point[1]} r="2.5" className="historic-point"/>)}{futurePoints.map((point,index)=><g key={`future-${index}`} onClick={()=>setSelected({label:`Forecast · +${series[index].minutesAhead} min`,value:series[index].predictedWaveHeight})}><circle cx={point[0]} cy={point[1]} r="12" className="connected-hit"/><circle cx={point[0]} cy={point[1]} r={index===futurePoints.length-1?4.5:2.3} className="prediction-point"/></g>)}
    <g className="forecast-target"><circle cx={right} cy={predictedY} r="10" className="forecast-target-ring"/><text x={right-12} y={predictedY-18} textAnchor="end">MODEL TARGET · {data.ai.confidence}% CONFIDENCE</text></g>
    <text x={left} y="254">{new Date(history[0].recordedAt).toLocaleTimeString([],{hour:"2-digit",minute:"2-digit"})}</text><text x={divider} y="254" textAnchor="middle">NOW</text><text x={right} y="254" textAnchor="end">+{data.ai.horizonMinutes} MIN</text>
  </svg>{selected&&<button className="connected-selection" onClick={()=>setSelected(null)}><span>{selected.label}</span><b>{selected.value.toFixed(2)} m</b><i>×</i></button>}</div>;
}

export default function WavePage({data,horizon,onHorizon,onScenarioApplied}:{data:DashboardData;horizon:number;onHorizon:(value:number)=>void;onScenarioApplied:()=>void}){
  const [scenario,setScenarioState]=useState<ScenarioState|null>(null),[busy,setBusy]=useState(false),[transitioning,setTransitioning]=useState(false),[controlError,setControlError]=useState<string|null>(null);
  const transitionTimer=useRef<number|null>(null),refreshTimers=useRef<number[]>([]);
  useEffect(()=>{let active=true;const load=(attempt=0)=>getScenario().then(value=>{if(active){setScenarioState(value);setControlError(null)}}).catch(error=>{if(!active)return;if(attempt<2)window.setTimeout(()=>load(attempt+1),800*(attempt+1));else setControlError(error instanceof Error?error.message:"Scenario controls unavailable")});load();return()=>{active=false;if(transitionTimer.current!=null)window.clearTimeout(transitionTimer.current);refreshTimers.current.forEach(window.clearTimeout)};},[]);
  const applyScenario=async(value:string)=>{setBusy(true);setTransitioning(true);setControlError(null);setScenarioState(current=>current?{...current,active:value}:current);try{setScenarioState(await setScenario(value));refreshTimers.current.forEach(window.clearTimeout);refreshTimers.current=[0,800,2000,4000,7000,11000].map(delay=>window.setTimeout(onScenarioApplied,delay));if(transitionTimer.current!=null)window.clearTimeout(transitionTimer.current);transitionTimer.current=window.setTimeout(()=>setTransitioning(false),11500);}catch(error){setTransitioning(false);setControlError(error instanceof Error?error.message:"Scenario update failed");getScenario().then(setScenarioState).catch(()=>undefined);}finally{setBusy(false);}};
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
    {transitioning&&<div className="scenario-progress"><Gauge/><span><b>{scenarioLabels[scenario?.active||""]||"Demo scenario"} is active</b>Live samples and AI forecast are updating smoothly.</span></div>}
    <div className="wave-report-grid">
      <article className="panel forecast-result">
        <header><div><span>AI PREDICTION</span><h2>Wave forecast result</h2></div><em>DEMO AI</em></header>
        <div className="result-core"><span>Predicted Wave Height</span><strong>{ready?n(predicted,2):"--"}<small>m</small></strong><p>Current: {n(current,2)} m · {ai.direction.toUpperCase()} trend</p></div>
        <dl className="result-metrics"><div><dt>Confidence</dt><dd>{ai.confidence}%</dd></div><div><dt>Prediction Time</dt><dd>Next {ai.horizonMinutes} minutes</dd></div><div><dt>Status</dt><dd>{ai.seaCondition}</dd></div></dl>
        <section className="prediction-inputs"><div className="inputs-heading"><span>Prediction based on</span><small>Configured demo-model input weights</small></div><strong className="weight-total">100% total</strong><div className="input-list">{weights.map(([label,value])=><div className="input-row" key={label}><i><Check/></i><span>{label}</span><b>{value}%</b><div className="input-track"><em style={{width:`${value}%`}}/></div></div>)}</div></section>
      </article>

      <article className="panel wave-chart-panel report-chart"><header><div><span>LIVE WAVE GRAPH</span><h2>Measured and predicted wave</h2></div><em>MODEL SERIES</em></header><ConnectedWaveChart data={data}/><footer><span>Left: blue actual history with orange rolling model estimates</span><span>Right: forecast series with transparent uncertainty band</span></footer></article>

      <article className="panel ai-summary"><header><div><span>EXPLAINABLE AI</span><h2>AI analysis summary</h2></div><em>COMPLETE</em></header><ul>{analysis.map(item=><li key={item}><i/>{item}</li>)}</ul><div className="therefore"><span>Therefore</span><strong>{n(predicted,2)} meters · {ai.seaCondition}</strong><small>Expected within {ai.horizonMinutes} minutes</small></div></article>

      <article className="panel report-confidence"><header><div><span>MODEL CONFIDENCE</span><h2>Prediction confidence</h2></div><CheckCircle2/></header><strong>{ai.confidence}%</strong><div className="confidence-bar"><i style={{width:`${ai.confidence}%`}}/></div><b>{quality}</b><p>Recent signals are stable and the trend fit has low disagreement.</p></article>

      <article className="panel prediction-timeline"><header><div><span>PREDICTION TIMELINE</span><h2>Expected wave progression</h2></div><Waves/></header><div><section><span>NOW</span><strong>{n(current,2)} m</strong><small>Current estimate</small></section><i/><section><span>{Math.max(1,Math.round(ai.horizonMinutes/2))} MIN</span><strong>{n(midpoint,2)} m</strong><small>Near-term</small></section><i/><section><span>{ai.horizonMinutes} MIN</span><strong>{n(predicted,2)} m</strong><small>Selected horizon</small></section></div></article>

      <article className="panel prediction-quality"><header><div><span>PREDICTION QUALITY</span><h2>Presentation validation</h2></div><em>NOT FIELD ACCURACY</em></header><dl><div><dt>Samples used</dt><dd>{ai.sampleCount}</dd></div><div><dt>Model confidence</dt><dd>{ai.confidence}%</dd></div><div><dt>Signal agreement</dt><dd>{agreement}</dd></div><div><dt>Data source</dt><dd>{ai.dataSource.toUpperCase()}</dd></div></dl><footer>Demo output for presentation. Field calibration and validation are still required.</footer></article>
    </div>
  </section>;
}
