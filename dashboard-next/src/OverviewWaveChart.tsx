import { useState } from "react";
import type { DashboardData } from "./types";

const curve=(points:number[][])=>{if(points.length<2)return"";let path=`M ${points[0][0]} ${points[0][1]}`;for(let index=0;index<points.length-1;index++){const current=points[index],next=points[index+1],midX=(current[0]+next[0])/2,midY=(current[1]+next[1])/2;path+=` Q ${current[0]} ${current[1]} ${midX} ${midY}`}const last=points.at(-1)!;return`${path} T ${last[0]} ${last[1]}`};

export default function OverviewWaveChart({data}:{data:DashboardData}){
  const [selected,setSelected]=useState<number|null>(null);
  const history=data.wave.history.filter((item):item is typeof item&{waveHeight:number}=>item.waveHeight!=null).slice(-42);
  const ready=data.ai.status==="READY"&&data.ai.predictedWaveHeight!=null;
  if(history.length<2)return <div className="pro-chart-empty">Collecting estimated wave height history...</div>;
  const measured=history.map(item=>item.waveHeight),current=measured.at(-1)!;
  const historic=ready?(data.ai.historicalPredictionSeries||[]):[];
  const all=[...measured,...historic.map(item=>item.predictedWaveHeight)],min=Math.max(0,Math.min(...all)-.08),max=Math.max(...all)+.08,range=Math.max(.01,max-min);
  const left=58,right=714,top=26,bottom=214,toY=(value:number)=>bottom-(value-min)/range*(bottom-top);
  const measuredPoints=measured.map((value,index)=>[left+index/Math.max(1,measured.length-1)*(right-left),toY(value)]);
  const start=Date.parse(history[0].recordedAt),end=Date.parse(history.at(-1)!.recordedAt);
  const timedAi=historic.map(item=>({time:Date.parse(item.at),value:item.predictedWaveHeight})).filter(item=>Number.isFinite(item.time)&&item.time>=start&&item.time<=end).sort((a,b)=>a.time-b.time);
  const rawAi=history.map((row,index)=>{const time=Date.parse(row.recordedAt),afterIndex=timedAi.findIndex(item=>item.time>=time);if(afterIndex<0)return timedAi.at(-1)?.value??measured[index];if(afterIndex===0)return timedAi[0].time===time?timedAi[0].value:measured[index];const before=timedAi[afterIndex-1],after=timedAi[afterIndex],progress=(time-before.time)/Math.max(1,after.time-before.time);return before.value+(after.value-before.value)*progress});
  const smoothAi:number[]=[];rawAi.forEach((value,index)=>{if(index===0){smoothAi.push(value);return}const previous=smoothAi[index-1],blended=previous*.62+value*.38,maxStep=Math.max(.02,range*.09);smoothAi.push(Math.max(previous-maxStep,Math.min(previous+maxStep,blended)))});
  const aiPoints=ready&&timedAi.length>1?smoothAi.map((value,index)=>[left+index/Math.max(1,smoothAi.length-1)*(right-left),toY(value)]):[];
  const index=Math.min(selected??history.length-1,history.length-1),reading=history[index];
  return <div className="overview-wave-shell"><div className="overview-wave-legend"><span><i/>Current estimate</span><span className="is-ai"><i/>AI prediction</span>{!ready&&<small>AI is collecting data</small>}</div><div className="wave-chart-scroll"><svg className="overview-wave-chart" viewBox="0 0 760 260" role="img" aria-label="Current estimated wave height and AI prediction" onPointerMove={event=>{const bounds=event.currentTarget.getBoundingClientRect();const position=((event.clientX-bounds.left)/bounds.width*760-left)/(right-left);setSelected(Math.max(0,Math.min(history.length-1,Math.round(position*(history.length-1)))));}}>
    {[0,1,2,3,4].map(row=>{const y=top+(bottom-top)*row/4,value=max-(max-min)*row/4;return <g key={row}><line x1={left} y1={y} x2={right} y2={y}/><text x={left-11} y={y+4} textAnchor="end">{value.toFixed(2)} m</text></g>})}
    {aiPoints.length>1&&<path d={curve(aiPoints)} className="overview-ai-line"/>}
    <path d={`${curve(measuredPoints)} L ${right} ${bottom} L ${left} ${bottom} Z`} className="overview-wave-area"/><path d={curve(measuredPoints)} className="overview-current-line"/><circle cx={right} cy={toY(current)} r="4" className="overview-current-dot"/>
    {selected!==null&&<g className="wave-selection"><line x1={measuredPoints[index][0]} x2={measuredPoints[index][0]} y1={top} y2={bottom}/><circle cx={measuredPoints[index][0]} cy={measuredPoints[index][1]} r="5"/></g>}
    <text x={left} y="245">{new Date(history[0].recordedAt).toLocaleTimeString([],{hour:"2-digit",minute:"2-digit"})}</text><text x={(left+right)/2} y="245" textAnchor="middle">{new Date(history[Math.floor(history.length/2)].recordedAt).toLocaleTimeString([],{hour:"2-digit",minute:"2-digit"})}</text><text x={right} y="245" textAnchor="end">{new Date(history.at(-1)!.recordedAt).toLocaleTimeString([],{hour:"2-digit",minute:"2-digit"})}</text>
  </svg></div><div className="wave-inspector"><div><span>{selected===null?"Latest reading":"Selected reading"} · {new Date(reading.recordedAt).toLocaleTimeString()}</span><strong>{reading.waveHeight.toFixed(2)} <small>m</small></strong></div><label>Explore earlier readings<input type="range" min="0" max={history.length-1} value={index} onChange={event=>setSelected(Number(event.target.value))} aria-label="Choose a wave reading" aria-valuetext={`${new Date(reading.recordedAt).toLocaleTimeString()}, ${reading.waveHeight.toFixed(2)} meters`}/></label>{selected!==null&&<button onClick={()=>setSelected(null)}>Latest</button>}</div></div>;
}
