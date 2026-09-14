import test from 'node:test';
import assert from 'node:assert/strict';
import {fileURLToPath} from 'node:url';
import {createServer} from '../../dashboard-next/node_modules/vite/dist/node/index.js';

test('Coastal geometry, single receiver pole, route endpoints and outage animation',async()=>{
  const server=await createServer({configFile:fileURLToPath(new URL('../vite.config.mjs',import.meta.url)),server:{middlewareMode:true},appType:'custom'});
  try{
    const {createCoast,RECEIVER,coastCamera}=await server.ssrLoadModule('/coast.js');
    const {PerspectiveCamera,Vector3}=await server.ssrLoadModule('/../dashboard-next/node_modules/three/build/three.module.js');
    const coast=createCoast();
    assert.equal(coast.group.userData.poleCount,1);assert.ok(coast.group.userData.houseCount>=10);assert.ok(coast.group.userData.palmCount>=20);
    assert.ok(coast.route.getPoint(1).distanceTo(new Vector3(...RECEIVER))<1e-9);
    assert.deepEqual(coast.route.getPoint(0).toArray(),[0,1.2,0]);
    let meshes=0;coast.group.traverse(o=>{if(o.isMesh){meshes++;assert.ok(o.geometry.attributes.position.count>0);const a=o.geometry.attributes.position.array;assert.ok(a.every(Number.isFinite));}});
    assert.ok(meshes<35,`Batched mesh count ${meshes}`);
    const camera=new PerspectiveCamera(42,1440/900,.03,180);
    for(const pose of coastCamera){camera.position.fromArray(pose.eye);camera.lookAt(new Vector3().fromArray(pose.aim));camera.updateMatrixWorld();const projected=new Vector3(...RECEIVER).project(camera);assert.ok(projected.z<1&&projected.z>-1);assert.ok(Math.abs(projected.x)<1&&Math.abs(projected.y)<1,'Receiver inside camera view');}
    coast.update(1,true,camera,true);const route=coast.group.getObjectByName('Physical buoy-to-shore LoRa path');assert.equal(route.visible,true);
    const packet=route.children.find(o=>o.isInstancedMesh);const first=packet.instanceMatrix.array.slice();coast.update(2,true,camera,true);assert.notDeepEqual(packet.instanceMatrix.array,first);
    coast.update(2,false,camera,true);assert.equal(route.visible,false);coast.update(2,true,camera,true);assert.equal(route.visible,true);
    coast.update(2,true,camera,false);assert.equal(coast.group.visible,false);coast.dispose();
  }finally{await server.close();}
});
