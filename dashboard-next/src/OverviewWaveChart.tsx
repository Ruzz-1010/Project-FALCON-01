import { useEffect, useRef, useState } from "react";
import type { DashboardData } from "./types";

const linePath=(points:number[][])=>points.length<2?"":points.map(([x,y],index)=>`${index===0?"M":"L"} ${x} ${y}`).join(" ");

export default function OverviewWaveChart({data}:{data:DashboardData}){
  const [selected,setSelected]=useState<number|null>(null);
  const chartHost=useRef<HTMLDivElement>(null);
  const [chartWidth,setChartWidth]=useState(760);
  useEffect(()=>{
    const host=chartHost.current;
    if(!host)return;
    const observer=new ResizeObserver(([entry])=>setChartWidth(Math.max(480,Math.round(entry.contentRect.width))));
    observer.observe(host);
    return ()=>observer.disconnect();
  },[data.wave.history.filter(item=>item.waveHeight!=null).length>=2]);
  const history=data.wave.history.filter((item):item is typeof item&{waveHeight:number}=>item.waveHeight!=null);
  const ready=data.ai.status==="READY"&&data.ai.predictedWaveHeight!=null;
  if(history.length<2)return <div className="pro-chart-empty">Collecting estimated wave height history...</div>;
  const measured=history.map(item=>item.waveHeight);
  const historic=data.ai.historicalPredictionSeries||[];
  const start=Date.parse(history[0].recordedAt),end=Date.parse(history.at(-1)!.recordedAt);
  const timedAi=historic.map(item=>({time:Date.parse(item.at),value:item.predictedWaveHeight})).filter(item=>Number.isFinite(item.time)&&Number.isFinite(item.value)&&item.time>=start&&item.time<=end).sort((a,b)=>a.time-b.time);
  const all=[...measured,...timedAi.map(item=>item.value)];
  const low=Math.min(...all),high=Math.max(...all),span=Math.max(.2,high-low);
  const rawStep=span*1.3/5,magnitude=10**Math.floor(Math.log10(rawStep));
  const step=([1,2,5,10].find(value=>value*magnitude>=rawStep)??10)*magnitude;
  const min=Math.max(0,Math.floor((low-span*.15)/step)*step);
  const max=Math.max(min+step,Math.ceil((high+span*.15)/step)*step),range=max-min;
  const ticks=Array.from({length:Math.round(range/step)+1},(_,i)=>min+i*step);
  const decimals=Math.max(0,-Math.floor(Math.log10(step)));
  const left=72,right=chartWidth-24,top=18,bottom=266,toY=(value:number)=>bottom-(value-min)/range*(bottom-top);
  const toX=(time:number)=>left+(time-start)/Math.max(1,end-start)*(right-left);
  const measuredPoints=history.map(item=>[toX(Date.parse(item.recordedAt)),toY(item.waveHeight)]);
  const aiPoints=timedAi.map(item=>[left+(item.time-start)/Math.max(1,end-start)*(right-left),toY(item.value)]);
  const index=Math.min(selected??history.length-1,history.length-1),reading=history[index];
  return <div className="overview-wave-shell"><div className="overview-wave-legend"><span><i/>Current estimate</span><span className="is-ai"><i/>Earlier AI predictions</span><span className="wave-scale-note">Auto scale · {min.toFixed(decimals)}–{max.toFixed(decimals)} m</span>{aiPoints.length===0&&<small>{ready?"AI history is collecting":"AI prediction unavailable"}</small>}{aiPoints.length===1&&<small>First AI prediction received</small>}</div><div className="wave-chart-scroll" ref={chartHost}><svg className="overview-wave-chart" viewBox={`0 0 ${chartWidth} 320`} role="group" tabIndex={0} aria-label="Wave height history. Use left and right arrow keys to explore readings; Escape returns to latest." onKeyDown={event=>{if(event.key==="Escape"){setSelected(null);return}if(event.key==="ArrowLeft"||event.key==="ArrowRight"){event.preventDefault();setSelected(Math.max(0,Math.min(history.length-1,index+(event.key==="ArrowLeft"?-1:1))))}}} onPointerMove={event=>{const bounds=event.currentTarget.getBoundingClientRect();const position=((event.clientX-bounds.left)/bounds.width*chartWidth-left)/(right-left),time=start+position*(end-start);setSelected(history.reduce((nearest,row,i)=>Math.abs(Date.parse(row.recordedAt)-time)<Math.abs(Date.parse(history[nearest].recordedAt)-time)?i:nearest,0));}}>
    <rect className="wave-plot-frame" x={left} y={top} width={right-left} height={bottom-top}/>
    <text className="wave-axis-title" transform={`translate(16 ${(top+bottom)/2}) rotate(-90)`} textAnchor="middle">Wave height (m)</text>
    <text className="wave-axis-title" x={(left+right)/2} y="313" textAnchor="middle">Time</text>
    {ticks.map(value=><g key={value}><line className="wave-grid-line" x1={left} y1={toY(value)} x2={right} y2={toY(value)}/><text x={left-11} y={toY(value)+4} textAnchor="end">{value.toFixed(decimals)}</text></g>)}
    <path d={linePath(measuredPoints)} className="overview-current-line"/>
    {measuredPoints.map(([x,y],i)=><circle key={`${history[i].recordedAt}-${i}`} cx={x} cy={y} r="2.2" className="wave-sample-dot"/>)}
    {aiPoints.length>1&&<path d={linePath(aiPoints)} className="overview-ai-line"/>}
    {aiPoints.map(([x,y],i)=><circle key={`${timedAi[i].time}-${i}`} cx={x} cy={y} r="2.5" className="wave-ai-sample-dot"/>)}
    {selected!==null&&<g className="wave-selection"><line x1={measuredPoints[index][0]} x2={measuredPoints[index][0]} y1={top} y2={bottom}/><circle cx={measuredPoints[index][0]} cy={measuredPoints[index][1]} r="5"/></g>}
    {[0,1,2,3,4].map(i=>{const time=start+(end-start)*i/4,x=toX(time);return <g key={i}><line className="wave-axis-tick" x1={x} y1={bottom} x2={x} y2={bottom+5}/><text x={x} y="289" textAnchor={i===0?"start":i===4?"end":"middle"}>{new Date(time).toLocaleTimeString([],{hour:"2-digit",minute:"2-digit",second:"2-digit",hour12:false})}</text></g>})}
  </svg></div><div className="wave-inspector"><div><span>{selected===null?"Latest reading":"Selected reading"} · {new Date(reading.recordedAt).toLocaleTimeString()}</span><strong>{reading.waveHeight.toFixed(2)} <small>m</small></strong></div>{selected!==null&&<button onClick={()=>setSelected(null)}>Latest</button>}</div></div>;
}
