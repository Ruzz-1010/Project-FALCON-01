export const WAVE_GAP_MS = 30_000;

/** Display only the latest uninterrupted session; stored logs are untouched. */
export function recentWaveSession<T extends {recordedAt:string;waveHeight:number|null}>(rows:T[]) {
  const unique=new Map<number,T & {waveHeight:number}>();
  for(const row of rows){
    const time=Date.parse(row.recordedAt);
    if(Number.isFinite(time)&&row.waveHeight!==null&&Number.isFinite(row.waveHeight))
      unique.set(time,row as T & {waveHeight:number});
  }
  const ordered=[...unique.entries()].sort((a,b)=>a[0]-b[0]);
  let first=ordered.length-1;
  while(first>0&&ordered[first][0]-ordered[first-1][0]<=WAVE_GAP_MS)first--;
  return ordered.slice(Math.max(0,first)).map(([,row])=>row);
}

/** Never draw a line through an interval with missing prediction samples. */
export function timedLinePath(points:number[][],times:number[]){
  return points.map(([x,y],i)=>`${i===0||times[i]-times[i-1]>WAVE_GAP_MS?"M":"L"} ${x} ${y}`).join(" ");
}
