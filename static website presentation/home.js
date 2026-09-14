// Home-only choreography. At t=1 this exactly meets the existing Instrument pose.
export const homeShots=[
  {at:0,eye:[8,2.65,15],aim:[-1.3,.35,0]},
  {at:.32,eye:[6,2.2,10.8],aim:[-1,.42,0]},
  {at:.72,eye:[3.6,1.7,5.7],aim:[-.75,.5,0]},
  {at:1,eye:[2.6,1.45,3.8],aim:[-.65,.55,0]}
];
export const smooth=t=>{t=Math.max(0,Math.min(1,t));return Math.max(0,Math.min(1,t*t*t*(t*(t*6-15)+10)));};
export function homeCamera(progress){
  const p=Math.max(0,Math.min(1,progress));let i=0;
  while(i<2&&p>homeShots[i+1].at)i++;
  const a=homeShots[i],b=homeShots[i+1],t=smooth((p-a.at)/(b.at-a.at));
  return {eye:a.eye.map((v,k)=>v+(b.eye[k]-v)*t),aim:a.aim.map((v,k)=>v+(b.aim[k]-v)*t)};
}
export const homeWeight=p=>1-smooth((p-.78)/.22);
// amplitude, kx, kz, angular speed, phase. Incommensurate periods avoid a short loop.
export const waveLayers=[
  [.048,.34,.19,.49,.3], [.031,-.43,.57,.713,1.2],
  [.019,.91,-.42,1.037,2.1], [.012,-1.47,.88,1.319,.7],
  [.006,2.41,1.73,1.871,2.8], [.004,-3.13,2.27,2.173,1.6]
];
export function oceanSample(x,z,time,progress){
  const gain=1+Math.min(.16,Math.max(0,progress)*.16);let height=0,dx=0,dz=0;
  for(const [a,kx,kz,w,phase] of waveLayers){const q=kx*x+kz*z+w*time+phase;height+=a*Math.sin(q);dx+=a*kx*Math.cos(q);dz+=a*kz*Math.cos(q);}
  return {height:height*gain,dx:dx*gain,dz:dz*gain};
}
export const oceanFieldGLSL=`vec3 homeField(vec2 p,float t,float progress){vec3 r=vec3(0.);float q;${waveLayers.map(([a,x,z,w,phase])=>`q=${x.toFixed(4)}*p.x+${z.toFixed(4)}*p.y+${w.toFixed(4)}*t+${phase.toFixed(4)};r+=vec3(${a.toFixed(4)}*sin(q),${(a*x).toFixed(6)}*cos(q),${(a*z).toFixed(6)}*cos(q));`).join('')}return r*(1.+clamp(progress,0.,1.)*.16);}`;
