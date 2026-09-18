import test from 'node:test';
import assert from 'node:assert/strict';
import {createHomeOrbit} from '../home-orbit.js';
import {homeCamera} from '../home.js';
import {buoyMotion} from '../motion.js';

test('Home orbit starts at the current camera and approaches without a cut',()=>{
  const orbit=createHomeOrbit(),eye=homeCamera(.2).eye;
  orbit.enter(eye);
  const initial=orbit.update(0).eye;
  assert.ok(Math.hypot(...initial.map((v,i)=>v-eye[i]))<1e-10);
  const next=orbit.update(1/60).eye;
  assert.ok(Math.hypot(...next.map((v,i)=>v-eye[i]))<.6);
  for(let n=0;n<300;n++)orbit.update(1/60);
  const pose=orbit.update(0);
  assert.ok(Math.abs(Math.hypot(...pose.eye.map((v,i)=>v-pose.aim[i]))-4.8)<1e-8);
});
test('Camera can orbit around every side with bounded elevation and zoom',()=>{
  const orbit=createHomeOrbit();orbit.enter([0,1,5]);
  for(const direction of [-1,1]){
    orbit.drag(direction*1500,direction*10000);
    for(let i=0;i<100;i++)orbit.zoom(direction*200);
    for(let i=0;i<400;i++)orbit.update(1/60);
    const {eye,aim}=orbit.update(0),offset=eye.map((v,i)=>v-aim[i]);
    const radius=Math.hypot(...offset),phi=Math.acos(offset[1]/radius);
    assert.ok(radius>=3.2-1e-8&&radius<=9+1e-8);
    assert.ok(phi>=.3-1e-8&&phi<=1.78+1e-8);
    assert.ok(eye.every(Number.isFinite));
  }
});
test('Reset exits orbit without changing story camera data or time-based buoy motion',()=>{
  const orbit=createHomeOrbit(),before=homeCamera(.4),motion=buoyMotion(17);
  orbit.enter(before.eye);orbit.drag(200,100);orbit.update(.03);orbit.exit();
  assert.equal(orbit.active,false);
  assert.deepEqual(homeCamera(.4),before);assert.deepEqual(buoyMotion(17),motion);
  orbit.enter(before.eye);
  assert.ok(Math.hypot(...orbit.update(0).eye.map((v,i)=>v-before.eye[i]))<1e-10);
});
