import * as THREE from 'three';
import {STATION,RECEIVER,groundHeight} from './coast.js';
import {bayPipeline,baySteps,arrivalPhase} from './bay-story.js';

export function createBayStation(coast){
  const group=new THREE.Group();group.name='Page 05 station inspection';group.visible=false;coast.group.add(group);
  const interior=new THREE.Group();interior.name='Illustrative shared shore computer';group.add(interior);
  const geometries=[],materials=[],textures=[],targets=new Map(),tiles=[];
  const material=(color,extra={})=>{const m=new THREE.MeshStandardMaterial({color,roughness:.75,...extra});materials.push(m);return m;};
  const shell=material('#a8afa8'),metal=material('#303e43'),desk=material('#80745d');
  function box(parent,mat,position,size){const g=new THREE.BoxGeometry(...size);geometries.push(g);const mesh=new THREE.Mesh(g,mat);mesh.position.set(...position);parent.add(mesh);return mesh;}
  function label(parent,text,position,width,height){
    const canvas=typeof document==='undefined'?null:document.createElement('canvas');let map=null;
    if(canvas){canvas.width=1024;canvas.height=192;const ctx=canvas.getContext('2d');ctx.fillStyle='#142932';ctx.fillRect(0,0,1024,192);ctx.fillStyle='#d7e7e6';ctx.font='500 62px sans-serif';ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillText(text,512,96,980);map=new THREE.CanvasTexture(canvas);map.colorSpace=THREE.SRGBColorSpace;textures.push(map);}
    const g=new THREE.PlaneGeometry(width,height);geometries.push(g);const m=new THREE.MeshBasicMaterial({map,color:map?'#ffffff':'#a2c5c7'});materials.push(m);const mesh=new THREE.Mesh(g,m);mesh.position.set(...position);parent.add(mesh);return mesh;
  }
  const [x,y,z]=STATION;
  const sign=label(group,'FALCON-01  /  BAY STATION',[x,y+2.05,z+1.86],2.35,.38);
  box(interior,shell,[x,y+.09,z],[4.85,.18,3.85]);
  box(interior,shell,[x,y+1.4,z-1.75],[4.6,2.8,.13]);
  box(interior,desk,[x,y+.92,z+.1],[3,.12,1.1]);
  for(const dx of [-1.3,1.3])box(interior,metal,[x+dx,y+.48,z+.1],[.06,.85,.75]);
  box(interior,metal,[x-.98,y+1.09,z+.25],[.5,.2,.62]);
  label(interior,'SHORE PC',[x-.98,y+1.09,z+.57],.47,.12);
  box(interior,metal,[x+1.12,y+1.08,z+.3],[.4,.18,.3]);
  label(interior,'BACKHAUL',[x+1.12,y+1.08,z+.455],.39,.11);
  box(interior,metal,[x,y+1.6,z-.18],[2.2,1.22,.1]);
  box(interior,metal,[x,y+1.08,z-.18],[.1,.35,.12]);
  // Distinct software stages live on one practical screen, not separate invented hardware.
  bayPipeline.forEach((id,i)=>{const tile=label(interior,baySteps[id].title,[x,y+2.08-i*.19,z-.115],1.96,.155);tile.userData.bayId=id;tiles.push(tile);if(id!=='rx')targets.set(id,tile);});
  const arrows=new THREE.BufferGeometry().setFromPoints(Array.from({length:6},(_,i)=>new THREE.Vector3(x-1.03,y+2.08-i*.19,z-.10)));geometries.push(arrows);const arrowMat=new THREE.LineBasicMaterial({color:'#89bbb9'});materials.push(arrowMat);interior.add(new THREE.Line(arrows,arrowMat));
  const rxPosition=[RECEIVER[0],groundHeight(RECEIVER[0],RECEIVER[2])+4.46,RECEIVER[2]+.083];
  const rxMat=material('#87c9ca',{transparent:true,opacity:0,emissive:'#77b9bd',emissiveIntensity:.2,depthWrite:false});
  const rx=box(group,rxMat,rxPosition,[.23,.33,.17]);rx.userData.bayId='rx';targets.set('rx',rx);
  const cableCurve=new THREE.CatmullRomCurve3([new THREE.Vector3(...rxPosition),new THREE.Vector3(RECEIVER[0],y+.3,RECEIVER[2]),new THREE.Vector3(x-2.55,y+.3,.1),new THREE.Vector3(x-2.32,y+.7,.1),new THREE.Vector3(x-.98,y+1.09,.25)],false,'centripetal');
  const cableGeo=new THREE.TubeGeometry(cableCurve,40,.014,6,false);geometries.push(cableGeo);const cable=new THREE.Mesh(cableGeo,material('#26373d'));group.add(cable);
  const pulse=box(group,material('#b2e3df',{emissive:'#72c3c4',emissiveIntensity:.45}),[0,0,0],[.07,.07,.07]);
  let selected=null,active=false,revealed=false;
  function select(id){selected=id;}
  function update(time,online,visible){
    active=visible;group.visible=visible;interior.visible=visible&&selected!==null&&revealed;coast.stationVisual.visible=!interior.visible;sign.visible=!interior.visible;
    const state=arrivalPhase(time,online);pulse.visible=visible&&state.cable!==null;if(pulse.visible)pulse.position.copy(cableCurve.getPoint(state.cable));
    rxMat.opacity=visible&&(selected==='rx'||state.receiver)?.28:0;
    tiles.forEach((tile,i)=>{const focused=bayPipeline[i]===selected;tile.material.color.set(focused?'#fff1ca':i===state.stage?'#a9e2d8':selected&&selected!=='station'?'#718b91':'#ffffff');});
  }
  function focus(id,aspect){
    if(id==='station'){const scale=aspect<1?2.2:1;return {eye:[x-4*scale,y+3.8*scale,z+7*scale],aim:[x+(aspect<1?0:.5),y+(aspect<1?-.2:1.3),z]};}
    const target=targets.get(id);if(!target)return null;
    const p=target.position;const distance=id==='rx'?2.2:3.1;
    return {eye:[p.x-.35,p.y+.35,p.z+distance/Math.min(1,aspect)],aim:[p.x+(aspect<1?0:.5),p.y-(aspect<1?.55:0),p.z]};
  }
  function pick(raycaster){
    if(!active)return null;
    const objects=[rx,...(interior.visible?tiles:coast.stationVisual.children)];
    const hit=raycaster.intersectObjects(objects,true)[0];return hit?(hit.object.userData.bayId||'station'):null;
  }
  return {group,targets,cableCurve,select,update,focus,pick,reveal(value){revealed=value;},
    dispose(){coast.stationVisual.visible=true;group.removeFromParent();geometries.forEach(g=>g.dispose());materials.forEach(m=>m.dispose());textures.forEach(t=>t.dispose());}};
}
