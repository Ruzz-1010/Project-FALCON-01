import * as THREE from 'three';
import {STATION,RECEIVER,groundHeight} from './coast.js';
import {arrivalPhase} from './bay-story.js';

export function createBayStation(coast){
  const group=new THREE.Group();group.name='Page 05 station inspection';group.visible=false;coast.group.add(group);
  const interior=new THREE.Group();interior.name='Illustrative shared shore computer';group.add(interior);
  const geometries=[],materials=[],textures=[],targets=new Map();
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
  const pcMat=material('#59666a',{metalness:.35,emissive:'#619d99',emissiveIntensity:0});
  const radioMat=material('#65716c',{metalness:.25,emissive:'#619d99',emissiveIntensity:0});
  const monitorMat=material('#29363b',{emissive:'#619d99',emissiveIntensity:0});
  const networkMat=material('#6e7771'),upsMat=material('#39454a');
  const localRadio=box(interior,radioMat,[x-.98,y+1.055,z+.25],[.3,.15,.28]);localRadio.name='Indoor LoRa radio';localRadio.userData.bayId='rx';
  const pc=box(interior,pcMat,[x-.43,y+1.065,z+.25],[.4,.17,.36]);pc.name='Shared Bay Station computer';pc.userData.bayId='validate';
  for(const id of ['computer','validate','sqlite','processing','ai'])targets.set(id,pc);
  const router=box(interior,networkMat,[x+1.12,y+1.08,z+.3],[.4,.18,.3]);router.name='Shore Internet router';
  box(interior,metal,[x-1.08,y+.23,z-.1],[.6,.06,.6]);
  const ups=box(interior,upsMat,[x-1.08,y+.49,z-.1],[.28,.46,.38]);ups.name='Small UPS power unit';
  label(interior,'UPS',[x-1.08,y+.5,z+.095],.2,.08);
  const monitor=box(interior,monitorMat,[x+.35,y+1.48,z-.12],[.88,.56,.055]);monitor.name='Physical dashboard monitor';monitor.userData.bayId='dashboard';targets.set('dashboard',monitor);
  box(interior,monitorMat,[x+.35,y+1.11,z-.12],[.055,.24,.05]);box(interior,monitorMat,[x+.35,y+.994,z-.08],[.35,.025,.22]);
  box(interior,metal,[x+.32,y+1.002,z+.42],[.62,.028,.19]);
  for(let i=0;i<4;i++)box(interior,shell,[x+.32,y+1.018,z+.36+i*.037],[.54,.002,.012]);
  for(let i=0;i<7;i++)box(interior,metal,[x-.58+i*.047,y+1.153,z+.24],[.012,.006,.23]);
  for(let i=0;i<3;i++){box(interior,metal,[x-.55+i*.085,y+1.07,z+.432],[.05,.025,.009]);box(interior,shell,[x+1+i*.06,y+1.095,z+.456],[.013,.009,.004]);}
  label(interior,'LoRa RX',[x-.98,y+.92,z+.658],.48,.105);
  label(interior,'SHORE COMPUTER',[x-.42,y+.925,z+.658],.76,.095);
  label(interior,'LOCAL STORAGE',[x-.42,y+.845,z+.658],.76,.068);
  label(interior,'PROCESSING + AI',[x-.42,y+.78,z+.658],.76,.068);
  label(interior,'INTERNET BACKHAUL',[x+1.12,y+1.08,z+.456],.62,.095);
  // One display attached to a real monitor bezel, not a wall of functional cards.
  const screen=label(interior,'FALCON-01 / SIMULATED',[x+.35,y+1.48,z-.09],.82,.49);screen.userData.bayId='dashboard';
  if(typeof document!=='undefined'){
    const canvas=document.createElement('canvas');canvas.width=1024;canvas.height=640;const ctx=canvas.getContext('2d');
    ctx.fillStyle='#e8efed';ctx.fillRect(0,0,1024,640);ctx.fillStyle='#1c3945';ctx.fillRect(0,0,1024,100);ctx.fillStyle='#e7f2ef';ctx.font='bold 35px sans-serif';ctx.fillText('FALCON-01  /  MONITORING',35,60);
    const rows=[['Estimated wave height','0.62 rel.'],['AI prediction · +10 min','0.68 rel.'],['Wind observation','11 km/h · NE'],['Battery / power','78% · demo'],['LoRa connection','Receiving · demo'],['System status','Simulation only']];
    rows.forEach(([name,value],i)=>{const row=145+i*64;ctx.fillStyle='#344f58';ctx.font='27px sans-serif';ctx.fillText(name,35,row);ctx.font='bold 27px sans-serif';ctx.fillText(value,655,row);ctx.strokeStyle='#c5d3d2';ctx.beginPath();ctx.moveTo(35,row+21);ctx.lineTo(990,row+21);ctx.stroke();});
    ctx.font='24px sans-serif';ctx.fillStyle='#665b40';ctx.fillText('ILLUSTRATIVE · RELATIVE UNITS · NOT LIVE',35,610);
    const map=new THREE.CanvasTexture(canvas);map.colorSpace=THREE.SRGBColorSpace;textures.push(map);screen.material.map=map;screen.material.needsUpdate=true;
  }
  const equipment=[localRadio,pc,router,ups,monitor];const baseColors=new Map(equipment.map(o=>[o,o.material.color.clone()]));
  function wire(points,radius=.009){const curve=new THREE.CatmullRomCurve3(points.map(p=>new THREE.Vector3(...p)),false,'centripetal');const geometry=new THREE.TubeGeometry(curve,24,radius,5,false);geometries.push(geometry);interior.add(new THREE.Mesh(geometry,metal));return curve;}
  const radioToPC=wire([[x-.98,y+1.06,.25],[x-.85,y+1.0,.05],[x-.65,y+1.0,.05],[x-.43,y+1.06,.25]]);
  const pcToScreen=wire([[x-.43,y+1.06,.1],[x-.2,y+1.0,-.3],[x+.35,y+1.1,-.2],[x+.35,y+1.45,-.16]]);
  wire([[x+1.12,y+1.05,.18],[x+.9,y+1.0,-.3],[x-.43,y+1.0,-.3],[x-.43,y+1.06,.1]]);
  wire([[x-1.08,y+.65,-.1],[x-1.08,y+.85,-.3],[x-.43,y+1.0,-.3]]);
  const dataPulse=box(interior,material('#a4cac4',{emissive:'#71aaa4',emissiveIntensity:.2}),[0,0,0],[.025,.025,.025]);
  const rxPosition=[RECEIVER[0],groundHeight(RECEIVER[0],RECEIVER[2])+4.46,RECEIVER[2]+.083];
  const rxMat=material('#87c9ca',{transparent:true,opacity:0,emissive:'#77b9bd',emissiveIntensity:.2,depthWrite:false});
  const rx=box(group,rxMat,rxPosition,[.23,.33,.17]);rx.userData.bayId='rx';targets.set('rx',localRadio);
  const cableCurve=new THREE.CatmullRomCurve3([new THREE.Vector3(...rxPosition),new THREE.Vector3(RECEIVER[0],y+.3,RECEIVER[2]),new THREE.Vector3(x-2.55,y+.3,.1),new THREE.Vector3(x-2.32,y+.7,.1),new THREE.Vector3(x-.98,y+1.09,.25)],false,'centripetal');
  const cableGeo=new THREE.TubeGeometry(cableCurve,40,.014,6,false);geometries.push(cableGeo);const cable=new THREE.Mesh(cableGeo,material('#26373d'));group.add(cable);
  const pulse=box(group,material('#b2e3df',{emissive:'#72c3c4',emissiveIntensity:.45}),[0,0,0],[.07,.07,.07]);
  let selected=null,active=false,revealed=false;
  function select(id){selected=id;}
  function update(time,online,visible){
    active=visible;group.visible=visible;interior.visible=visible&&selected!==null&&revealed;coast.stationVisual.visible=!interior.visible;sign.visible=!interior.visible;
    const state=arrivalPhase(time,online);pulse.visible=visible&&state.cable!==null;if(pulse.visible)pulse.position.copy(cableCurve.getPoint(state.cable));
    rxMat.opacity=visible&&(selected==='rx'||state.receiver)?.28:0;
    const focused=targets.get(selected),processing=state.stage>=1&&state.stage<=4;
    equipment.forEach(o=>{o.material.color.copy(baseColors.get(o)).multiplyScalar(focused&&o!==focused?.62:1);if(o.material.emissive)o.material.emissiveIntensity=o===focused?.12:o===pc&&processing?.045:0;});
    screen.material.color.set(focused&&focused!==monitor?'#a1b3b5':'#ffffff');
    dataPulse.visible=interior.visible&&online&&(state.stage===0||state.stage===5);
    if(dataPulse.visible){const phase=((time*.405)%1+1)%1,local=((phase-.42)/.58*6)%1;dataPulse.position.copy((state.stage===0?radioToPC:pcToScreen).getPoint(Math.max(0,Math.min(1,local))));}
  }
  function focus(id,aspect){
    if(id==='station'){const scale=aspect<1?1.25:1;return {eye:[x-3.15*scale,y+2.75*scale,z+4.75*scale],aim:[x+(aspect<1?0:.35),y+(aspect<1?.25:.95),z+.02]};}
    const target=targets.get(id);if(!target)return null;
    const p=target.position;const distance=id==='rx'?1.9:id==='dashboard'?2.25:2.45;
    return {eye:[p.x-.55,p.y+.42,p.z+distance/Math.min(1,aspect)],aim:[p.x+(aspect<1?0:.22),p.y-(aspect<1?.25:0),p.z]};
  }
  function pick(raycaster){
    if(!active)return null;
    const objects=interior.visible?[localRadio,pc,monitor,screen]:[rx,...coast.stationVisual.children];
    const hit=raycaster.intersectObjects(objects,true)[0];
    if(hit?.object===pc&&targets.get(selected)===pc)return selected;
    return hit?(hit.object.userData.bayId||'station'):null;
  }
  return {group,targets,cableCurve,select,update,focus,pick,reveal(value){revealed=value;},
    dispose(){coast.stationVisual.visible=true;group.removeFromParent();geometries.forEach(g=>g.dispose());materials.forEach(m=>m.dispose());textures.forEach(t=>t.dispose());}};
}
