// Camera-only orbit state. Never writes to the buoy or the page scroll position.
export function createHomeOrbit(){
  const center=[0,.5,0];let active=false,theta=0,phi=1.2,radius=4.8,targetTheta=0,targetPhi=1.2,targetRadius=4.8;
  return {
    get active(){return active;},
    enter(eye){const d=eye.map((v,i)=>v-center[i]);const length=Math.hypot(...d);theta=targetTheta=Math.atan2(d[0],d[2]);phi=targetPhi=Math.acos(Math.max(-1,Math.min(1,d[1]/length)));radius=length;targetRadius=4.8;active=true;},
    exit(){active=false;},
    drag(dx,dy){if(!active)return;targetTheta-=dx*.006;targetPhi=Math.max(.3,Math.min(1.78,targetPhi+dy*.005));},
    zoom(delta){if(active)targetRadius=Math.max(3.2,Math.min(9,targetRadius*Math.exp(Math.max(-200,Math.min(200,delta))*.0015)));},
    update(dt){const blend=1-Math.exp(-Math.max(0,dt)*7);theta+=(targetTheta-theta)*blend;phi+=(targetPhi-phi)*blend;radius+=(targetRadius-radius)*blend;return {eye:[center[0]+radius*Math.sin(phi)*Math.sin(theta),center[1]+radius*Math.cos(phi),center[2]+radius*Math.sin(phi)*Math.cos(theta)],aim:[...center]};}
  };
}
