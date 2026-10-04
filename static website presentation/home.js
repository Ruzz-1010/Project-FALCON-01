// Home-only choreography. At t=1 this exactly meets the existing Instrument pose.
export const homeShots=[
  // 2026-10-09: aims pushed −0.35 (buoy further right, clear of the cover/hero
  // text). Last knot untouched — it hands off to the chapter-01 pose, which
  // home.test.mjs pins by exact value.
  // 2026-10-09 (2): another −0.20 with a slimmer cover box — buoy hard right,
  // text column narrow, maximum separation between the two.
  {at:0,eye:[3.9,1.75,6.7],aim:[-1.25,.52,0]},
  {at:.32,eye:[3.7,1.72,6.1],aim:[-1.23,.52,0]},
  {at:.72,eye:[3.15,1.58,4.85],aim:[-1.21,.53,0]},
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
  [.055,.34,.19,.49,.3], [.035,-.43,.57,.713,1.2],
  [.022,.91,-.42,1.037,2.1], [.014,-1.47,.88,1.319,.7],
  [.006,2.41,1.73,1.871,2.8], [.003,-3.13,2.27,2.173,1.6]
];
export function oceanSample(x,z,time,progress){
  const gain=1+Math.min(.16,Math.max(0,progress)*.16);let height=0,dx=0,dz=0;
  for(const [a,kx,kz,w,phase] of waveLayers){const q=kx*x+kz*z+w*time+phase;height+=a*Math.sin(q);dx+=a*kx*Math.cos(q);dz+=a*kz*Math.cos(q);}
  return {height:height*gain,dx:dx*gain,dz:dz*gain};
}
export const oceanFieldGLSL=`vec3 homeField(vec2 p,float t,float progress){vec3 r=vec3(0.);float q;${waveLayers.map(([a,x,z,w,phase])=>`q=${x.toFixed(4)}*p.x+${z.toFixed(4)}*p.y+${w.toFixed(4)}*t+${phase.toFixed(4)};r+=vec3(${a.toFixed(4)}*sin(q),${(a*x).toFixed(6)}*cos(q),${(a*z).toFixed(6)}*cos(q));`).join('')}return r*(1.+clamp(progress,0.,1.)*.16);}`;
