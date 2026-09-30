import {oceanSample} from './home.js';

// World-space buoy motion has no scroll/chapter input and never resets on navigation.
export function buoyMotion(time){
  const wave=oceanSample(0,0,time,0);
  return {heave:wave.height,pitch:Math.max(-.025,Math.min(.025,-wave.dz*.45)),roll:Math.max(-.025,Math.min(.025,wave.dx*.45))};
}
export const cameraBlend=dt=>1-Math.exp(-Math.max(0,dt)*5);
