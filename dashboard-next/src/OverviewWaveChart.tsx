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
  const historic=ready?(data.ai.historicalPredictionSeries||[]):[];
  const all=[...measured,...historic.map(item=>item.predictedWaveHeight)];
  const peak=Math.max(0,...all.filter(Number.isFinite)),min=0;
  const scaleStep=peak<=5?1:5;
  const max=Math.max(1,Math.ceil(peak*1.1/scaleStep)*scaleStep),range=max;
  const left=64,right=chartWidth-24,top=14,bottom=266,toY=(value:number)=>bottom-(value-min)/range*(bottom-top);
  const measuredPoints=measured.map((value,index)=>[left+index/Math.max(1,measured.length-1)*(right-left),toY(value)]);
  const start=Date.parse(history[0].recordedAt),end=Date.parse(history.at(-1)!.recordedAt);
  const timedAi=historic.map(item=>({time:Date.parse(item.at),value:item.predictedWaveHeight})).filter(item=>Number.isFinite(item.time)&&item.time>=start&&item.time<=end).sort((a,b)=>a.time-b.time);
  const rawAi=history.map((row,index)=>{const time=Date.parse(row.recordedAt),afterIndex=timedAi.findIndex(item=>item.time>=time);if(afterIndex<0)return timedAi.at(-1)?.value??measured[index];if(afterIndex===0)return timedAi[0].time===time?timedAi[0].value:measured[index];const before=timedAi[afterIndex-1],after=timedAi[afterIndex],progress=(time-before.time)/Math.max(1,after.time-before.time);return before.value+(after.value-before.value)*progress});

  const aiPoints=ready&&timedAi.length>1?rawAi.map((value,index)=>[left+index/Math.max(1,rawAi.length-1)*(right-left),toY(value)]):[];
  const index=Math.min(selected??history.length-1,history.length-1),reading=history[index];
  return <div className="overview-wave-shell"><div className="overview-wave-legend"><span><i/>Current estimate</span><span className="is-ai"><i/>Earlier AI predictions</span>{!ready&&<small>AI is collecting data</small>}</div><div className="wave-chart-scroll" ref={chartHost}><svg className="overview-wave-chart" viewBox={`0 0 ${chartWidth} 320`} role="group" tabIndex={0} aria-label="Wave height history. Use left and right arrow keys to explore readings; Escape returns to latest." onKeyDown={event=>{if(event.key==="Escape"){setSelected(null);return}if(event.key==="ArrowLeft"||event.key==="ArrowRight"){event.preventDefault();setSelected(Math.max(0,Math.min(history.length-1,index+(event.key==="ArrowLeft"?-1:1))))}}} onPointerMove={event=>{const bounds=event.currentTarget.getBoundingClientRect();const position=((event.clientX-bounds.left)/bounds.width*chartWidth-left)/(right-left);setSelected(Math.max(0,Math.min(history.length-1,Math.round(position*(history.length-1)))));}}>
    <rect className="wave-plot-frame" x={left} y={top} width={right-left} height={bottom-top}/>
    <text className="wave-axis-title" transform={`translate(16 ${(top+bottom)/2}) rotate(-90)`} textAnchor="middle">Wave height (m)</text>
    <text className="wave-axis-title" x={(left+right)/2} y="313" textAnchor="middle">Time</text>
    {[0,1,2,3,4,5].map(row=>{const y=top+(bottom-top)*row/5,value=max-(max-min)*row/5;return <g key={row}><line className="wave-axis-tick" x1={left-5} y1={y} x2={left} y2={y}/><text x={left-11} y={y+4} textAnchor="end">{value.toFixed(max<5?1:0)}</text></g>})}
    {aiPoints.length>1&&<path d={linePath(aiPoints)} className="overview-ai-line"/>}
    <path d={linePath(measuredPoints)} className="overview-current-line"/>
    {measuredPoints.map(([x,y],i)=><circle key={`${history[i].recordedAt}-${i}`} cx={x} cy={y} r="2.2" className="wave-sample-dot"/>)}
    {selected!==null&&<g className="wave-selection"><line x1={measuredPoints[index][0]} x2={measuredPoints[index][0]} y1={top} y2={bottom}/><circle cx={measuredPoints[index][0]} cy={measuredPoints[index][1]} r="5"/></g>}
    <text x={left} y="289">{new Date(history[0].recordedAt).toLocaleTimeString([],{hour:"2-digit",minute:"2-digit"})}</text><text x={(left+right)/2} y="289" textAnchor="middle">{new Date(history[Math.floor(history.length/2)].recordedAt).toLocaleTimeString([],{hour:"2-digit",minute:"2-digit"})}</text><text x={right} y="289" textAnchor="end">{new Date(history.at(-1)!.recordedAt).toLocaleTimeString([],{hour:"2-digit",minute:"2-digit"})}</text>
  </svg></div><div className="wave-inspector"><div><span>{selected===null?"Latest reading":"Selected reading"} · {new Date(reading.recordedAt).toLocaleTimeString()}</span><strong>{reading.waveHeight.toFixed(2)} <small>m</small></strong></div>{selected!==null&&<button onClick={()=>setSelected(null)}>Latest</button>}</div></div>;
}
