import type { DashboardData } from "./types";

const curve=(points:number[][])=>{if(points.length<2)return"";let path=`M ${points[0][0]} ${points[0][1]}`;for(let index=0;index<points.length-1;index++){const current=points[index],next=points[index+1],midX=(current[0]+next[0])/2,midY=(current[1]+next[1])/2;path+=` Q ${current[0]} ${current[1]} ${midX} ${midY}`}const last=points.at(-1)!;return`${path} T ${last[0]} ${last[1]}`};

export default function OverviewWaveChart({data}:{data:DashboardData}){
  const history=data.wave.history.filter((item):item is typeof item&{waveHeight:number}=>item.waveHeight!=null).slice(-42);
  const ready=data.ai.status==="READY"&&data.ai.predictedWaveHeight!=null;
  if(history.length<2)return <div className="pro-chart-empty">Collecting estimated wave height history...</div>;
  const measured=history.map(item=>item.waveHeight),current=measured.at(-1)!;
  const historic=ready?(data.ai.historicalPredictionSeries||[]):[];
  const all=[...measured,...historic.map(item=>item.predictedWaveHeight)],min=Math.max(0,Math.min(...all)-.08),max=Math.max(...all)+.08,range=Math.max(.01,max-min);
  const left=58,right=714,top=26,bottom=214,toY=(value:number)=>bottom-(value-min)/range*(bottom-top);
  const measuredPoints=measured.map((value,index)=>[left+index/Math.max(1,measured.length-1)*(right-left),toY(value)]);
  const start=Date.parse(history[0].recordedAt),end=Date.parse(history.at(-1)!.recordedAt);
  const historicPoints=historic.filter(item=>Date.parse(item.at)>=start&&Date.parse(item.at)<=end).map(item=>[left+(Date.parse(item.at)-start)/Math.max(1,end-start)*(right-left),toY(item.predictedWaveHeight)]);
  const aiPoints=historicPoints.length>1?(()=>{const first=historicPoints[0],second=historicPoints[1],beforeSlope=(second[1]-first[1])/Math.max(1,second[0]-first[0]),last=historicPoints.at(-1)!,previous=historicPoints.at(-2)!,afterSlope=(last[1]-previous[1])/Math.max(1,last[0]-previous[0]),startY=Math.max(top,Math.min(bottom,first[1]+beforeSlope*(left-first[0]))),endY=Math.max(top,Math.min(bottom,last[1]+afterSlope*(right-last[0])));return[[left,startY],...historicPoints,[right,endY]]})():[];
  return <div className="overview-wave-shell"><div className="overview-wave-legend"><span><i/>Current estimate</span><span className="is-ai"><i/>AI prediction</span>{!ready&&<small>AI is collecting data</small>}</div><svg className="overview-wave-chart" viewBox="0 0 760 260" role="img" aria-label="Current estimated wave height and AI prediction">
    {[0,1,2,3,4].map(row=>{const y=top+(bottom-top)*row/4,value=max-(max-min)*row/4;return <g key={row}><line x1={left} y1={y} x2={right} y2={y}/><text x={left-11} y={y+4} textAnchor="end">{value.toFixed(2)} m</text></g>})}
    {aiPoints.length>1&&<path d={curve(aiPoints)} className="overview-ai-line"/>}
    <path d={`${curve(measuredPoints)} L ${right} ${bottom} L ${left} ${bottom} Z`} className="overview-wave-area"/><path d={curve(measuredPoints)} className="overview-current-line"/><circle cx={right} cy={toY(current)} r="4" className="overview-current-dot"/>
    <text x={left} y="245">{new Date(history[0].recordedAt).toLocaleTimeString([],{hour:"2-digit",minute:"2-digit"})}</text><text x={(left+right)/2} y="245" textAnchor="middle">{new Date(history[Math.floor(history.length/2)].recordedAt).toLocaleTimeString([],{hour:"2-digit",minute:"2-digit"})}</text><text x={right} y="245" textAnchor="end">{new Date(history.at(-1)!.recordedAt).toLocaleTimeString([],{hour:"2-digit",minute:"2-digit"})}</text>
  </svg></div>;
}
