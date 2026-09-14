export function intersects(a,b,gap=0){return a.left<b.right+gap&&a.right>b.left-gap&&a.top<b.bottom+gap&&a.bottom>b.top-gap;}
export function placeCallout(source,silhouette,obstacles,viewport){
  const size=44;
  for(const x of [silhouette.right+30,silhouette.left-30]){
    const rect={left:x-size/2,right:x+size/2,top:source.y-size/2,bottom:source.y+size/2};
    if(rect.left<viewport.left||rect.right>viewport.right||rect.top<viewport.top||rect.bottom>viewport.bottom)continue;
    if(obstacles.some(r=>intersects(rect,r,12)))continue;
    // A horizontal leader must not run through text or another callout.
    const line={left:Math.min(source.x,x),right:Math.max(source.x,x),top:source.y-1,bottom:source.y+1};
    if(obstacles.some(r=>intersects(line,r,5)))continue;
    return {x,y:source.y,rect,path:`M${source.x},${source.y}H${x}`};
  }
  return null; // The accessible source index remains available when no label fits.
}
