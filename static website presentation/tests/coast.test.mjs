import test from 'node:test';
import assert from 'node:assert/strict';
import {fileURLToPath} from 'node:url';
import {createServer} from '../../dashboard-next/node_modules/vite/dist/node/index.js';

test('Coastal geometry, single receiver pole, route endpoints and outage animation',async()=>{
  const server=await createServer({configFile:fileURLToPath(new URL('../vite.config.mjs',import.meta.url)),server:{middlewareMode:true},appType:'custom'});
  try{
    const {createCoast,RECEIVER,STATION,shoreline,coastCamera,crossingCamera}=await server.ssrLoadModule('/coast.js');
    const {PerspectiveCamera,Vector3}=await server.ssrLoadModule('/../dashboard-next/node_modules/three/build/three.module.js');
    const coast=createCoast();
    assert.equal(coast.group.userData.poleCount,1);assert.ok(coast.group.userData.houseCount>=10);assert.ok(coast.group.userData.palmCount>=20);
    assert.ok(coast.route.getPoint(1).distanceTo(new Vector3(...RECEIVER))<1e-9);
    assert.deepEqual(coast.route.getPoint(0).toArray(),[-8,1.2,0]);
    let meshes=0;coast.group.traverse(o=>{if(o.isMesh){meshes++;assert.ok(o.geometry.attributes.position.count>0);const a=o.geometry.attributes.position.array;assert.ok(a.every(Number.isFinite));}});
    assert.ok(meshes<35,`Batched mesh count ${meshes}`);
    const camera=new PerspectiveCamera(42,1440/900,.03,180);
    for(const pose of coastCamera){camera.position.fromArray(pose.eye);camera.lookAt(new Vector3().fromArray(pose.aim));camera.updateMatrixWorld();const projected=new Vector3(...RECEIVER).project(camera);assert.ok(projected.z<1&&projected.z>-1);assert.ok(Math.abs(projected.x)<1&&Math.abs(projected.y)<1,'Receiver inside camera view');}
    coast.update(1,true,camera,true);const route=coast.group.getObjectByName('Physical buoy-to-shore LoRa path');assert.equal(route.visible,true);
    const packet=route.children.find(o=>o.isInstancedMesh);const first=packet.instanceMatrix.array.slice();coast.update(2,true,camera,true);assert.notDeepEqual(packet.instanceMatrix.array,first);
    coast.update(2,false,camera,true);assert.equal(route.visible,false);coast.update(2,true,camera,true);assert.equal(route.visible,true);
    const originalCommunity=coast.group.matrix.clone();
    assert.ok(STATION[0]>shoreline(STATION[2]),'Station remains on land');
    assert.deepEqual(crossingCamera.at(-1),coastCamera[2],'Page 04 joins unchanged Page 05 camera');
    for(const aspect of [1440/900,390/844]){
      camera.aspect=aspect;camera.updateProjectionMatrix();
      // The narrow-screen camera uses the same multiplier as the renderer.
      const pose=crossingCamera[0];camera.position.fromArray(pose.eye);const aim=new Vector3(...pose.aim);
      if(aspect<1){camera.position.sub(aim).multiplyScalar(1.9).add(aim).multiplyScalar(1.25);aim.x+=.45;aim.y+=.35;}
      camera.lookAt(aim);camera.updateMatrixWorld();
      const tx=coast.route.getPoint(0).project(camera),rx=new Vector3(...RECEIVER).project(camera);
      assert.ok(tx.z<1&&rx.z<1);assert.ok(rx.x>tx.x,'Buoy left, shore right');
      assert.ok(Math.abs(tx.x)<1&&Math.abs(rx.x)<1,'Both endpoints in wide shot, including portrait');
      assert.ok(rx.x-tx.x>.6,'Ocean route has visible screen width');
    }
    coast.update(3,true,camera,true,true);
    const crossing=route.getObjectByName('Crossing telemetry frames');assert.equal(crossing.visible,true);
    const frames=crossing.children.find(o=>o.isInstancedMesh);const framePositions=frames.instanceMatrix.array.slice();
    coast.update(4,true,camera,true,true);assert.notDeepEqual(frames.instanceMatrix.array,framePositions,'Telemetry frames advance across water');
    coast.update(4,false,camera,true,true);assert.equal(route.visible,false,'Interruption stops visible transmission');
    coast.update(4,true,camera,true,false);assert.equal(crossing.visible,false);assert.equal(packet.visible,true,'Page 05 original packets restored');
    assert.ok(coast.group.matrix.equals(originalCommunity),'No shore relocation');
    coast.update(2,true,camera,false);assert.equal(coast.group.visible,false);coast.dispose();
  }finally{await server.close();}
});
