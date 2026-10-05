import test from 'node:test';
import assert from 'node:assert/strict';
import {fileURLToPath} from 'node:url';
import {createServer} from '../../dashboard-next/node_modules/vite/dist/node/index.js';
import {bayPipeline,arrivalPhase} from '../bay-story.js';
test('Shore arrival synchronizes receiver, cable and local software stages',()=>{
  const at=phase=>arrivalPhase(phase/.405);
  assert.equal(at(.05).receiver,true);assert.equal(at(.05).cable,null);
  assert.ok(at(.25).cable>0&&at(.25).cable<1);assert.equal(at(.25).stage,-1);
  for(let i=0;i<6;i++)assert.equal(at(.42+(i+.5)*.58/6).stage,i);
  assert.deepEqual(arrivalPhase(12,false),{receiver:false,cable:null,stage:-1});
});
test('Station cutaway, real cable, selectable functions, focus framing and reset preserve other scenes',async()=>{
  const server=await createServer({configFile:fileURLToPath(new URL('../vite.config.mjs',import.meta.url)),server:{middlewareMode:true},appType:'custom'});
  try{
    const {createCoast,RECEIVER}=await server.ssrLoadModule('/coast.js');
    const {createBayStation}=await server.ssrLoadModule('/bay-station.js');
    const {PerspectiveCamera,Vector3,Vector2,Raycaster}=await server.ssrLoadModule('/../dashboard-next/node_modules/three/build/three.module.js');
    const coast=createCoast(),bay=createBayStation(coast);
    for(const id of ['computer','validate','sqlite','processing','ai'])assert.equal(bay.targets.get(id),bay.targets.get('computer'),'Software functions share one physical PC');
    assert.notEqual(bay.targets.get('dashboard'),bay.targets.get('computer'));
    assert.equal(bay.targets.get('rx').name,'Indoor LoRa radio');
    assert.ok(bay.group.getObjectByName('Small UPS power unit'));
    // 2026-10-09: the Shore Internet router prop was removed from the cutaway
    // per presenter (backhaul stays a copy-level concept, not a 3D box).
    assert.equal(bay.group.getObjectByName('Shore Internet router'),undefined);
    assert.ok(bay.group.getObjectByName('Physical dashboard monitor'));
    assert.equal(coast.group.userData.poleCount,1);
    assert.ok(bay.cableCurve.getPoint(0).distanceTo(new Vector3(...RECEIVER))<.6);
    bay.select('station');bay.update(0,true,true);assert.equal(coast.stationVisual.visible,true,'Exterior stays until camera arrives');
    bay.reveal(true);
    for(const id of ['station',...bayPipeline]){
      bay.select(id);bay.update(1,true,true);assert.equal(coast.stationVisual.visible,false);
      for(const aspect of [1440/900,390/844]){
        const pose=bay.focus(id,aspect);assert.ok(pose);assert.ok([...pose.eye,...pose.aim].every(Number.isFinite));
        if(id!=='station'){const camera=new PerspectiveCamera(42,aspect,.03,180);camera.position.fromArray(pose.eye);camera.lookAt(new Vector3(...pose.aim));camera.updateMatrixWorld();const point=bay.targets.get(id).position.clone().project(camera);assert.ok(Math.abs(point.x)<1&&Math.abs(point.y)<1&&point.z<1,`${id} target visible`);assert.ok(aspect<1?(1-point.y)/2<.5:(point.x+1)/2<.63,`${id} outside panel`);coast.group.updateMatrixWorld(true);const ray=new Raycaster();ray.setFromCamera(new Vector2(point.x,point.y),camera);assert.equal(bay.pick(ray),id,`${id} raycast hits the correct physical target`);}
      }
    }
    bay.select(null);bay.update(2,true,true);assert.equal(coast.stationVisual.visible,true);
    bay.select('ai');bay.update(2,true,false);assert.equal(bay.group.visible,false);assert.equal(coast.stationVisual.visible,true,'Original exterior on every other page');
    bay.dispose();coast.dispose();
  }finally{await server.close();}
});
