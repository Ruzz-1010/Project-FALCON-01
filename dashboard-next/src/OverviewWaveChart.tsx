import type { DashboardData } from "./types";

const n=(value:number|null|undefined)=>value==null?"--":value.toFixed(2);
const curve=(points:number[][])=>{if(points.length<2)return"";let path=`M ${points[0][0]} ${points[0][1]}`;for(let index=0;index<points.length-1;index++){const current=points[index],next=points[index+1],midX=(current[0]+next[0])/2,midY=(current[1]+next[1])/2;path+=` Q ${current[0]} ${current[1]} ${midX} ${midY}`}const last=points.at(-1)!;return`${path} T ${last[0]} ${last[1]}`};

export default function OverviewWaveChart({data}:{data:DashboardData}){
  const history=data.wave.history.filter((item):item is typeof item&{waveHeight:number}=>item.waveHeight!=null).slice(-42);
  const ready=data.ai.status==="READY"&&data.ai.predictedWaveHeight!=null;
  if(history.length<2)return <div className="pro-chart-empty">Collecting estimated wave height history...</div>;
  const measured=history.map(item=>item.waveHeight),current=measured.at(-1)!;
  const series=ready?(data.ai.forecastSeries?.length?data.ai.forecastSeries:[{minutesAhead:0,at:data.wave.recordedAt,predictedWaveHeight:current,lowerBound:current,upperBound:current},{minutesAhead:data.ai.horizonMinutes,at:data.ai.targetAt||data.wave.recordedAt,predictedWaveHeight:data.ai.predictedWaveHeight!,lowerBound:data.ai.predictedWaveHeight!,upperBound:data.ai.predictedWaveHeight!}]):[];
  const historic=ready?(data.ai.historicalPredictionSeries||[]):[];
  const all=[...measured,...historic.map(item=>item.predictedWaveHeight),...series.flatMap(item=>[item.lowerBound,item.predictedWaveHeight,item.upperBound])],min=Math.max(0,Math.min(...all)-.08),max=Math.max(...all)+.08,range=Math.max(.01,max-min);
  const left=58,divider=470,right=714,top=26,bottom=214,toY=(value:number)=>bottom-(value-min)/range*(bottom-top);
  const measuredPoints=measured.map((value,index)=>[left+index/Math.max(1,measured.length-1)*(divider-left),toY(value)]);
  const start=Date.parse(history[0].recordedAt),end=Date.parse(history.at(-1)!.recordedAt);
  const historicPoints=historic.filter(item=>Date.parse(item.at)>=start&&Date.parse(item.at)<=end).map(item=>[left+(Date.parse(item.at)-start)/Math.max(1,end-start)*(divider-left),toY(item.predictedWaveHeight)]);
  const horizon=Math.max(1,data.ai.horizonMinutes||10),futurePoints=series.map(item=>[divider+item.minutesAhead/horizon*(right-divider),toY(item.predictedWaveHeight)]);
  const predictionPoints=[...(historicPoints.length?historicPoints:[measuredPoints.at(-1)!]),...futurePoints];
  const upper=series.map(item=>[divider+item.minutesAhead/horizon*(right-divider),toY(item.upperBound)]),lower=series.map(item=>[divider+item.minutesAhead/horizon*(right-divider),toY(item.lowerBound)]),band=series.length>1?`${curve(upper)} ${curve([...lower].reverse()).replace(/^M/,"L")} Z`:"";
  return <div className="overview-wave-shell"><div className="overview-wave-legend"><span><i/>Current estimate</span><span className="is-ai"><i/>AI prediction</span>{!ready&&<small>AI is collecting data</small>}</div><svg className="overview-wave-chart" viewBox="0 0 760 260" role="img" aria-label="Current estimated wave height and AI prediction">
    {[0,1,2,3,4].map(row=>{const y=top+(bottom-top)*row/4,value=max-(max-min)*row/4;return <g key={row}><line x1={left} y1={y} x2={right} y2={y}/><text x={left-11} y={y+4} textAnchor="end">{value.toFixed(2)} m</text></g>})}
    {ready&&<><path d={band} className="overview-ai-band"/><path d={curve(predictionPoints)} className="overview-ai-line"/><line x1={divider} y1={top} x2={divider} y2={bottom} className="overview-now-line"/><text x={divider+8} y={top+14} className="overview-ai-label">AI · NEXT {horizon} MIN</text></>}
    <path d={`${curve(measuredPoints)} L ${divider} ${bottom} L ${left} ${bottom} Z`} className="overview-wave-area"/><path d={curve(measuredPoints)} className="overview-current-line"/><circle cx={divider} cy={toY(current)} r="4" className="overview-current-dot"/>{ready&&<circle cx={right} cy={toY(data.ai.predictedWaveHeight!)} r="5" className="overview-ai-dot"/>}
    <text x={left} y="245">{new Date(history[0].recordedAt).toLocaleTimeString([],{hour:"2-digit",minute:"2-digit"})}</text><text x={divider} y="245" textAnchor="middle">NOW</text><text x={right} y="245" textAnchor="end">{ready?`+${horizon} MIN`:new Date(history.at(-1)!.recordedAt).toLocaleTimeString([],{hour:"2-digit",minute:"2-digit"})}</text>
  </svg>{ready&&<div className="overview-ai-result"><span>AI estimate after {horizon} minutes</span><b>{n(data.ai.predictedWaveHeight)} m · {data.ai.seaCondition}</b></div>}</div>;
}
