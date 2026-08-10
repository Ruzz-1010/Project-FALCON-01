import { useId } from "react";

export type ChartPoint = { value: number | null; recordedAt?: string };

const smoothPath = (points: number[][]) => {
  if (!points.length) return "";
  if (points.length === 1) return `M ${points[0][0]} ${points[0][1]}`;
  let path = `M ${points[0][0]} ${points[0][1]}`;
  for (let index = 0; index < points.length - 1; index++) {
    const previous = points[Math.max(0,index-1)],current=points[index],next=points[index+1],after=points[Math.min(points.length-1,index+2)];
    const c1x=current[0]+(next[0]-previous[0])/6,c1y=current[1]+(next[1]-previous[1])/6;
    const c2x=next[0]-(after[0]-current[0])/6,c2y=next[1]-(after[1]-current[1])/6;
    path += ` C ${c1x} ${c1y}, ${c2x} ${c2y}, ${next[0]} ${next[1]}`;
  }
  return path;
};

const timeLabel=(value?:string)=>value?new Date(value).toLocaleTimeString([],{hour:"2-digit",minute:"2-digit",second:"2-digit"}):"--";

export default function TelemetryChart({points,unit,color,forecast,forecastLabel="FORECAST",minimumZero=false,threshold,label}:{points:ChartPoint[];unit:string;color:string;forecast?:number|null;forecastLabel?:string;minimumZero?:boolean;threshold?:number;label:string}){
  const gradientId=`chart-fill-${useId().replaceAll(":","")}`;
  const valid=points.filter((point):point is ChartPoint&{value:number}=>point.value!=null).slice(-60);
  if(valid.length<2)return <div className="pro-chart-empty">Collecting {label.toLowerCase()} history...</div>;
  const values=valid.map(point=>point.value),all=forecast==null?values:[...values,forecast];
  const rawMin=Math.min(...all),rawMax=Math.max(...all),rawRange=Math.max(.01,rawMax-rawMin),padding=Math.max(rawRange*.2,unit==="%"?.15:.05);
  const min=minimumZero?Math.max(0,rawMin-padding):rawMin-padding,max=rawMax+padding,range=Math.max(.01,max-min);
  const left=58,right=forecast==null?714:642,top=26,bottom=214;
  const xy=valid.map((point,index)=>[left+index/Math.max(1,valid.length-1)*(right-left),bottom-(point.value-min)/range*(bottom-top)]);
  const line=smoothPath(xy),area=`${line} L ${right} ${bottom} L ${left} ${bottom} Z`,last=xy.at(-1)!;
  const forecastY=forecast==null?null:bottom-(forecast-min)/range*(bottom-top);
  const ticks=[0,1,2,3,4],mid=Math.floor((valid.length-1)/2);
  return <svg className="pro-chart" viewBox="0 0 760 260" role="img" aria-label={label}>
    <defs><linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor={color} stopOpacity=".28"/><stop offset="1" stopColor={color} stopOpacity=".015"/></linearGradient></defs>
    {ticks.map(row=>{const y=top+(bottom-top)*row/4,value=max-(max-min)*row/4;return <g key={row}><line x1={left} y1={y} x2="714" y2={y} className="pro-grid"/><text x={left-11} y={y+4} textAnchor="end" className="pro-axis">{value.toFixed(unit==="%"?1:2)}{unit}</text></g>})}
    {forecastY!=null&&<rect x={right} y={top} width={714-right} height={bottom-top} className="forecast-zone"/>}
    {threshold!=null&&threshold>=min&&threshold<=max&&<g><line x1={left} y1={bottom-(threshold-min)/range*(bottom-top)} x2="714" y2={bottom-(threshold-min)/range*(bottom-top)} className="threshold-line"/><text x="708" y={bottom-(threshold-min)/range*(bottom-top)-7} textAnchor="end" className="threshold-label">LIMIT {threshold}{unit}</text></g>}
    <path d={area} fill={`url(#${gradientId})`} className="pro-area"/><path d={line} style={{stroke:color}} className="pro-line"/>
    {xy.map((point,index)=><circle key={index} cx={point[0]} cy={point[1]} r="8" className="pro-hit"><title>{timeLabel(valid[index].recordedAt)} · {valid[index].value.toFixed(2)}{unit}</title></circle>)}
    <circle cx={last[0]} cy={last[1]} r="5" style={{fill:color}} className="current-dot"/>
    {forecastY!=null&&<g><path d={`M ${last[0]} ${last[1]} C ${last[0]+24} ${last[1]}, ${right+37} ${forecastY}, 714 ${forecastY}`} className="pro-forecast"/><circle cx="714" cy={forecastY} r="6" className="forecast-dot"/><text x="706" y={forecastY-12} textAnchor="end" className="forecast-value">{forecast!.toFixed(2)}{unit}</text><text x={right+8} y={top+14} className="forecast-zone-label">{forecastLabel}</text></g>}
    <text x={left} y="245" className="pro-time">{timeLabel(valid[0].recordedAt)}</text><text x={(left+right)/2} y="245" textAnchor="middle" className="pro-time">{timeLabel(valid[mid].recordedAt)}</text><text x={right} y="245" textAnchor="end" className="pro-time">{timeLabel(valid.at(-1)?.recordedAt)}</text>
  </svg>;
}
