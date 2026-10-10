import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {GLTFLoader} from '../node_modules/three/examples/jsm/loaders/GLTFLoader.js';
import {Box3,Vector3,PerspectiveCamera} from '../node_modules/three/build/three.module.js';
import {instrumentTargets,instrumentInfo} from '../instrument.js';
import {inspectionFrame,easeInspection} from '../inspection.js';

test('All Page 01 buttons resolve to physical CAD targets, focus and return precisely',async()=>{
  const bytes=readFileSync(new URL('../../edge/static/dashboard/models/PROJECT-FALCON-V2.glb',import.meta.url));
  const {scene}=await new GLTFLoader().parseAsync(bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength),'');
  scene.rotation.x=-Math.PI/2;scene.position.y=-2.05;scene.updateMatrixWorld(true);
  const targets=instrumentTargets(scene),full=new Box3().setFromObject(scene).getSize(new Vector3()).length();
  assert.equal(targets.size,6);assert.match(targets.get('solar').name,/SOLAR_30W_01_EAST/);
  for(const [id,target] of targets){
    const box=new Box3().setFromObject(target),center=box.getCenter(new Vector3()),size=box.getSize(new Vector3());
    assert.ok(size.length()<full*.5,`${id} target is a component, not entire buoy`);
    assert.ok(instrumentInfo[id].data.length<=3);assert.ok(instrumentInfo[id].function.length<140);
    for(const aspect of [1440/900,390/844]){
      const focus=inspectionFrame(center.toArray(),Math.max(size.x,size.y,size.z),aspect,aspect<1);
      const original=new Vector3(2.6,1.45,3.8),destination=new Vector3(...focus.eye),eye=original.clone();
      for(let frame=0;frame<=50;frame++)eye.lerpVectors(original,destination,easeInspection(frame/50));
      assert.ok(eye.distanceTo(destination)<1e-9);
      const camera=new PerspectiveCamera(42,aspect,.03,180);camera.position.copy(eye);camera.lookAt(new Vector3(...focus.aim));camera.updateMatrixWorld(true);
      const projected=center.clone().project(camera);assert.ok(Math.abs(projected.x)<1&&Math.abs(projected.y)<1&&projected.z<1,`${id} visible at focus`);
      const screenX=(projected.x+1)/2,screenY=(1-projected.y)/2;
      assert.ok(aspect<1?screenY<.5:screenX<.58,`${id} focus stays outside information panel region`);
      for(let frame=0;frame<=50;frame++)eye.lerpVectors(destination,original,easeInspection(frame/50));
      assert.ok(eye.distanceTo(original)<1e-9,`${id} exact reset`);
    }
  }
  assert.match(instrumentInfo.pressure.function,/pressure-derived estimated wave height/);
  assert.equal(instrumentInfo.pressure.status,'CALIBRATION REQUIRED');
});
