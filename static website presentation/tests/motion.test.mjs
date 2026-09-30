import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {buoyMotion,cameraBlend} from '../motion.js';
import {homeCamera} from '../home.js';

test('Slow scroll, stop, resume and rapid scroll never reset time-based buoy motion',()=>{
  let eye=homeCamera(0).eye,previous=buoyMotion(0);
  for(let frame=1;frame<=600;frame++){
    const t=frame/30;
    const progress=frame<120?frame/240:frame<240?.5:frame<360?.5+(frame-240)/240:frame%2;
    const target=homeCamera(progress).eye;
    const before=eye;eye=eye.map((v,i)=>v+(target[i]-v)*cameraBlend(1/30));
    for(let i=0;i<3;i++){assert.ok(Number.isFinite(eye[i]));assert.ok(Math.abs(eye[i]-before[i])<=Math.abs(target[i]-before[i])*.154);}
    const motion=buoyMotion(t);
    assert.ok(Math.abs(motion.heave-previous.heave)<.005);
    assert.ok(Math.abs(motion.pitch-previous.pitch)<.003);
    assert.ok(Math.abs(motion.roll-previous.roll)<.003);
    previous=motion;
  }
  assert.notEqual(buoyMotion(5).heave,buoyMotion(6).heave,'continues while scroll is stationary');
  assert.deepEqual(buoyMotion(6),buoyMotion(6),'paused clock holds the exact transform');
});
test('Camera damping is frame-rate independent and cannot jump to a new target',()=>{
  const follow=(fps)=>{let x=0;for(let i=0;i<fps;i++)x+=(10-x)*cameraBlend(1/fps);return x;};
  assert.ok(Math.abs(follow(30)-follow(60))<1e-10);
  assert.equal(cameraBlend(0),0);assert.ok(cameraBlend(1/30)<1);
});
test('Renderer has no post-interpolation auto-zoom or scroll-dependent buoy transform',()=>{
  const source=readFileSync(new URL('../world.js',import.meta.url),'utf8');
  assert.doesNotMatch(source,/setViewOffset|uncomposedEye|camera\.position\.sub\(aim\)\.multiplyScalar/);
  assert.match(source,/const motion=buoyMotion\(time\)/);
  assert.match(source,/buoy\.position\.y=motion\.heave/);
  assert.match(source,/buoy\.rotation\.x=motion\.pitch/);
  assert.match(source,/buoy\.rotation\.z=motion\.roll/);
  assert.match(source,/ocean\.material\.uniforms\.time\.value=time/);
});
