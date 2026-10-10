import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {GLTFLoader} from '../node_modules/three/examples/jsm/loaders/GLTFLoader.js';
import {Box3,Vector3,PerspectiveCamera} from '../node_modules/three/build/three.module.js';
import {inspections,easeInspection,inspectionFrame} from '../inspection.js';
import {components} from '../story.js';

test('All five nodes have concise, architecture-safe inspection content',()=>{
  assert.deepEqual(Object.keys(inspections),Object.keys(components));
  for(const info of Object.values(inspections)){assert.ok(info.function.length<210);assert.ok(info.data.length>=4);assert.ok(info.flow.length>=2);}
  assert.equal(inspections.pressure.status,'CALIBRATION REQUIRED');
  assert.equal(inspections.pressure.flow.at(-1),'ESTIMATED WAVE HEIGHT');
  assert.match(inspections.esp32.note,/enclosure/);
});
test('Camera easing has exact endpoints, bounded monotonic movement and reversible return',()=>{
  assert.equal(easeInspection(-1),0);assert.equal(easeInspection(2),1);
  let prior=0;for(let i=0;i<=100;i++){const t=i/100,v=easeInspection(t);assert.ok(v>=prior-1e-12);assert.ok(Math.abs(v+easeInspection(1-t)-1)<1e-12);prior=v;}
});
test('Every real CAD target is framed outside the panel on desktop, tablet and mobile',async()=>{
  const bytes=readFileSync(new URL('../../edge/static/dashboard/models/PROJECT-FALCON-V2.glb',import.meta.url));
  const gltf=await new GLTFLoader().parseAsync(bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength),'');
  gltf.scene.rotation.x=-Math.PI/2;gltf.scene.position.y=-2.05;gltf.scene.updateMatrixWorld(true);
  for(const [id,component] of Object.entries(components)){
    const prefix=id==='esp32'?'REV5_RECTANGULAR_MARINE_ELECTRONICS_POD':component.prefix;
    let target;gltf.scene.traverse(o=>{if(!target&&o.name.toUpperCase().startsWith(prefix))target=o;});assert.ok(target,id);
    const bounds=new Box3().setFromObject(target),center=bounds.getCenter(new Vector3()),size=bounds.getSize(new Vector3());
    for(const [width,height] of [[1440,900],[820,1180],[390,844],[360,640]]){
      const frame=inspectionFrame(center.toArray(),Math.max(size.x,size.y,size.z),width/height,width<650);
      const camera=new PerspectiveCamera(42,width/height,.03,180);camera.position.fromArray(frame.eye);camera.lookAt(new Vector3().fromArray(frame.aim));camera.updateMatrixWorld(true);
      const projected=center.clone().project(camera);assert.ok(projected.z<1&&projected.z>-1,id);assert.ok(Math.abs(projected.x)<.8,id);
      const screenY=(1-projected.y)*height/2,screenX=(projected.x+1)*width/2;
      if(width<650){assert.ok(screenY>90&&screenY<height*.5,`${id} mobile ${screenY}`);}
      else assert.ok(screenX<width*.6,`${id} desktop panel clearance`);
      assert.ok(!bounds.containsPoint(camera.position),`${id} camera outside target`);
    }
  }
});
