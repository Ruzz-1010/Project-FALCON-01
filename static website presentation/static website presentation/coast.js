import * as THREE from 'three';
import {mergeGeometries} from 'three/examples/jsm/utils/BufferGeometryUtils.js';

// A fictional, metre-scale coastal setting for the presentation, not a surveyed site.
export const shoreline = z => 8.1 + Math.sin(z*.13)*1.35 + Math.cos(z*.31)*.35;
export const groundHeight = (x,z) => Math.max(-.28, Math.min(2.6,(x-shoreline(z))*.085)) + Math.sin(z*.17)*.07;
export const STATION = [18, groundHeight(18,0), 0];
export const RECEIVER = [15.2, groundHeight(15.2,-1.7)+4.9, -1.7];
export const coastCamera = [
  {eye:[-9,7.2,25],aim:[4,1.7,0]},
  {eye:[-2,6.4,21],aim:[8,2,-.5]},
  {eye:[7,6.0,14],aim:[15,2.8,-1]},
  {eye:[12,5.5,8],aim:[17,3,-1.5]}
];
// Page 04-only framing: broadside ocean gap, then follow the route to shore.
// End at the original Page 05 pose. No world-space endpoint is relocated.
export const crossingCamera=[
  {eye:[-8,5.8,29],aim:[3.5,1.7,0]},
  {eye:[-1,5.8,24],aim:[9.5,2,-.5]},
  coastCamera[2]
];

export function createCoast(){
  const group=new THREE.Group();group.name='Fictional coastal community';
  const materials=[],geometries=[];
  const mat=(color,extra={})=>{const m=new THREE.MeshStandardMaterial({color,roughness:.88,...extra});materials.push(m);return m;};
  const plaster=[mat('#b7b3a1'),mat('#a7b6af'),mat('#b7aaa0'),mat('#a3aaa9')];
  const roofs=[mat('#784c40',{metalness:.12}),mat('#65777a',{metalness:.25}),mat('#6e807d',{metalness:.2})];
  const concrete=mat('#777c74'),wood=mat('#514d3e'),glass=mat('#647e80',{emissive:'#e7b466',emissiveIntensity:.3,roughness:.35}),dark=mat('#263b40');
  const metal=mat('#a6b4b7',{metalness:.7,roughness:.38}),radio=mat('#d2d7cc',{roughness:.55});
  const foliage=mat('#315343',{side:THREE.DoubleSide}),trunk=mat('#847a60'),rock=mat('#626e69');
  const boxGeometry=new THREE.BoxGeometry(1,1,1),cylinder=new THREE.CylinderGeometry(1,1,1,10);geometries.push(boxGeometry,cylinder);
  function mesh(geo,material,x,y,z,sx=1,sy=1,sz=1,parent=group){const m=new THREE.Mesh(geo,material);m.position.set(x,y,z);m.scale.set(sx,sy,sz);parent.add(m);return m;}
  function box(material,x,y,z,w,h,d,parent){return mesh(boxGeometry,material,x,y,z,w,h,d,parent);}
  function house(x,z,w,d,h,index,station=false){
    const base=groundHeight(x,z),house=new THREE.Group();house.position.set(x,base,z);house.name=station?'Bay Station building':`Residence ${index}`;group.add(house);
    box(concrete,0,.09,0,w+.25,.18,d+.25,house);
    box(station?plaster[0]:plaster[index%4],0,h/2+.18,0,w,h,d,house);
    const roofRise=.65,angle=Math.atan2(roofRise,w/2+.3),length=Math.hypot(w/2+.3,roofRise);
    for(const sign of [-1,1]){
      const panel=box(roofs[index%3],sign*(w/4+.15),h+.18+roofRise/2,0,length,.075,d+.6,house);panel.rotation.z=-sign*angle;
      // Corrugation follows the slope; fine ridges catch the evening light.
      for(let j=0;j<Math.ceil((d+.5)/.24);j++){
        const ridge=box(roofs[index%3],sign*(w/4+.15),h+.225+roofRise/2,-d/2-.2+j*.24,length,.018,.025,house);ridge.rotation.z=-sign*angle;
      }
    }
    box(wood,0,.85,d/2+.02,.65,1.35,.045,house);
    for(const sign of [-1,1]){
      box(dark,sign*w*.3,h*.56,d/2+.025,.72,.77,.05,house);
      box(glass,sign*w*.3,h*.56,d/2+.06,.59,.64,.018,house);
      box(wood,sign*w*.3,h*.56,d/2+.075,.025,.65,.015,house);
      box(wood,sign*w*.3,h*.56,d/2+.075,.61,.025,.015,house);
      box(glass,sign*(w/2+.018),h*.57,-d*.14,.018,.6,.74,house);
    }
    box(concrete,0,.07,d/2+.4,1.1,.14,.7,house);
    if(station){
      const awning=box(roofs[1],0,1.95,d/2+.62,w*.85,.065,1.15,house);awning.rotation.x=.09;
      // Building supports are not antenna poles.
      for(const sign of [-1,1])box(wood,sign*w*.39,1,d/2+1.05,.07,1.9,.07,house);
      box(dark,0,h-.25,d/2+.05,2.35,.38,.06,house);
    }
    return house;
  }
  const station=house(STATION[0],STATION[2],4.6,3.6,2.3,1,true);
  const homeSites=[[22,6],[25,-6],[18,12],[30,3],[30,13],[23,-15],[34,-10],[36,21],[16,-12],[40,8],[29,24],[39,-23]];
  homeSites.forEach(([x,z],i)=>house(x,z,3.1+(i%3)*.4,2.8+(i%2)*.6,1.9+(i%3)*.15,i));

  // Continuous sculpted terrain and beach, with per-vertex sand/grass coloration.
  const terrain=new THREE.PlaneGeometry(58,84,72,88);terrain.rotateX(-Math.PI/2);terrain.translate(31,0,0);
  const pos=terrain.attributes.position,colors=[];
  for(let i=0;i<pos.count;i++){
    const x=pos.getX(i),z=pos.getZ(i),distance=x-shoreline(z),y=groundHeight(x,z);
    pos.setY(i,y);const color=new THREE.Color(distance<1.2?'#8c9280':distance<3.2?'#768773':'#425d49');
    color.multiplyScalar(.93+.07*Math.sin(x*2.1+z*1.3));colors.push(color.r,color.g,color.b);
  }
  terrain.setAttribute('color',new THREE.Float32BufferAttribute(colors,3));terrain.computeVertexNormals();geometries.push(terrain);
  const terrainMaterial=mat('#ffffff',{vertexColors:true});mesh(terrain,terrainMaterial,0,0,0);
  function path(points,width){
    const curve=new THREE.CatmullRomCurve3(points.map(([x,z])=>new THREE.Vector3(x,groundHeight(x,z)+.025,z))),vertices=[],indices=[];
    for(let i=0;i<=60;i++){const t=i/60,p=curve.getPoint(t),dir=curve.getTangent(t);const side=new THREE.Vector3(-dir.z,0,dir.x).normalize().multiplyScalar(width/2);for(const sign of [-1,1]){const q=p.clone().addScaledVector(side,sign);q.y=groundHeight(q.x,q.z)+.035;vertices.push(q.x,q.y,q.z);}if(i<60){const a=i*2;indices.push(a,a+1,a+2,a+1,a+3,a+2);}}
    const geo=new THREE.BufferGeometry();geo.setAttribute('position',new THREE.Float32BufferAttribute(vertices,3));geo.setIndex(indices);geo.computeVertexNormals();geometries.push(geo);mesh(geo,concrete,0,0,0);
  }
  path([[19,-33],[20,-15],[21,-4],[21,7],[25,22],[29,36]],1.35);
  path([[21,3.2],[18,3.2],[16,2.7]],1.05);
  homeSites.forEach(([x,z])=>path([[21,z+2],[x,z+2]],.65));

  // One physical antenna mast, no lattice or parallel antenna support poles.
  const mast=new THREE.Group();mast.name='Single-tube LoRa receiver';group.add(mast);
  const ground=groundHeight(RECEIVER[0],RECEIVER[2]),poleHeight=4.6;
  const pole=mesh(cylinder,metal,RECEIVER[0],ground+poleHeight/2,RECEIVER[2],.048,poleHeight,.048,mast);pole.name='LoRa single cylindrical pole';
  box(concrete,RECEIVER[0],ground+.08,RECEIVER[2],.34,.16,.34,mast);
  const receiver=box(radio,RECEIVER[0],ground+4.46,RECEIVER[2]+.083,.17,.27,.105,mast);receiver.name='Compact LoRa receiver';
  const cap=mesh(cylinder,radio,RECEIVER[0],ground+4.78,RECEIVER[2],.028,.24,.028,mast);cap.name='Short coaxial antenna tip';
  // The tip is coaxial with the single mast, not a second parallel pole.

  const leafVertices=[];
  for(let i=0;i<13;i++){
    const t=i/13,t2=(i+1)/13,x=t*1.7,x2=t2*1.7,y=Math.sin(t*Math.PI)*.55-t*.45,y2=Math.sin(t2*Math.PI)*.55-t2*.45;
    const width=Math.sin(t2*Math.PI)*.26;
    for(const sign of [-1,1])leafVertices.push(x,y,0,x2,y2,0,x2-.13,y2-.04,sign*width);
  }
  const leaf=new THREE.BufferGeometry();leaf.setAttribute('position',new THREE.Float32BufferAttribute(leafVertices,3));leaf.computeVertexNormals();geometries.push(leaf);
  const treeSites=[[12,7],[13,-7],[17,7],[20,-8],[26,-10],[25,11],[28,7],[32,18],[18,19],[32,-17],[38,14],[38,-5],[23,21],[16,-20],[36,-29],[42,26],[46,-14],[29,-27],[44,0],[48,19],[33,30],[51,-27]];
  treeSites.forEach(([x,z],i)=>{
    const y=groundHeight(x,z),h=3.6+(i%4)*.5,lean=(i%2?1:-1)*.22;
    for(let j=0;j<4;j++){const trunkPiece=mesh(cylinder,trunk,x+lean*j/4,y+(j+.5)*h/4,z,.06,h/4+.035,.06);trunkPiece.rotation.z=-lean/h;}
    for(let j=0;j<9;j++){const frond=mesh(leaf,foliage,x+lean,y+h,z);frond.rotation.y=j*Math.PI*2/9+i;frond.rotation.z=(j%3)*.12;}
    for(let j=0;j<3;j++)mesh(cylinder,wood,x+lean+Math.cos(j*2)*.09,y+h-.12,z+Math.sin(j*2)*.09,.065,.11,.065);
  });
  const rockGeometry=new THREE.IcosahedronGeometry(1,1);geometries.push(rockGeometry);
  for(let i=0;i<64;i++){
    const z=-36+i*1.13,x=shoreline(z)+.3+Math.sin(i*2)*.35;
    const r=mesh(rockGeometry,rock,x,groundHeight(x,z)+.12,z,.3+(i%3)*.11,.18+(i%4)*.07,.3);r.rotation.set(i*.2,i*.7,0);
  }
  for(let i=0;i<35;i++){
    const x=26+(i%7)*4,z=-35+Math.floor(i/7)*16,y=groundHeight(x,z);
    mesh(rockGeometry,foliage,x,y+1,z,1.2,1.5+(i%3)*.4,1.1);
  }
  // Distant forested terrain retains depth behind the residential area.
  for(let i=0;i<8;i++)mesh(rockGeometry,foliage,55+(i%2)*8,1,-48+i*13,15,8+(i%3)*3,12);

  // Merge static scene meshes by material to avoid hundreds of individual draw calls.
  group.updateMatrixWorld(true);const batches=new Map(),stationBatches=new Map();
  group.traverse(o=>{if(!o.isMesh)return;let parent=o,isStation=false;while(parent){if(parent===station)isStation=true;parent=parent.parent;}const target=isStation?stationBatches:batches;let geo=o.geometry.clone().applyMatrix4(o.matrixWorld);if(geo.index){const unindexed=geo.toNonIndexed();geo.dispose();geo=unindexed;}geo.deleteAttribute('uv');if(!target.has(o.material))target.set(o.material,[]);target.get(o.material).push(geo);});
  const visual=new THREE.Group();visual.name='Batched coastal community';
  for(const [material,list] of batches){const geometry=mergeGeometries(list,false);if(geometry){const batch=new THREE.Mesh(geometry,material);batch.castShadow=material!==terrainMaterial;batch.receiveShadow=true;visual.add(batch);geometries.push(geometry);}list.forEach(g=>g.dispose());}
  const stationVisual=new THREE.Group();stationVisual.name='Bay Station exterior';
  for(const [material,list] of stationBatches){const geometry=mergeGeometries(list,false);if(geometry){const batch=new THREE.Mesh(geometry,material);batch.castShadow=true;batch.receiveShadow=true;stationVisual.add(batch);geometries.push(geometry);}list.forEach(g=>g.dispose());}
  group.clear();group.add(visual,stationVisual);
  const eveningLight=new THREE.DirectionalLight('#ffe4b8',.85);eveningLight.position.set(9,24,12);eveningLight.target.position.set(...STATION);eveningLight.castShadow=true;
  eveningLight.shadow.mapSize.set(1024,1024);Object.assign(eveningLight.shadow.camera,{left:-28,right:28,top:28,bottom:-28,near:.5,far:75});eveningLight.shadow.bias=-.0005;
  group.add(eveningLight,eveningLight.target);
  // Testable semantic inventory survives batching without duplicating geometry.
  group.userData={poleCount:1,houseCount:homeSites.length,palmCount:treeSites.length,receiver:RECEIVER,station:STATION};

  const linkGroup=new THREE.Group();linkGroup.name='Physical buoy-to-shore LoRa path';group.add(linkGroup);
  const points=[new THREE.Vector3(-8,1.2,0),new THREE.Vector3(-2,1.8,-.4),new THREE.Vector3(7,3.2,-1.1),new THREE.Vector3(...RECEIVER)];
  const route=new THREE.CatmullRomCurve3(points);
  const routeGeometry=new THREE.BufferGeometry().setFromPoints(route.getPoints(100));geometries.push(routeGeometry);
  const routeMaterial=new THREE.LineBasicMaterial({color:'#70d1dc',transparent:true,opacity:.43});materials.push(routeMaterial);linkGroup.add(new THREE.Line(routeGeometry,routeMaterial));
  const packetGeometry=new THREE.OctahedronGeometry(.075,0),packetMaterial=new THREE.MeshBasicMaterial({color:'#9aedf2'});geometries.push(packetGeometry);materials.push(packetMaterial);
  const packets=new THREE.InstancedMesh(packetGeometry,packetMaterial,9);linkGroup.add(packets);
  const rings=[];
  const ringGeometry=new THREE.TorusGeometry(.25,.007,6,48),ringMaterial=new THREE.MeshBasicMaterial({color:'#68d1de',transparent:true,opacity:.65});geometries.push(ringGeometry);materials.push(ringMaterial);
  for(let i=0;i<3;i++){const ring=new THREE.Mesh(ringGeometry,ringMaterial.clone());materials.push(ring.material);ring.position.fromArray(RECEIVER);linkGroup.add(ring);rings.push(ring);}
  const dummy=new THREE.Object3D();
  // Page 04 packet frames: discrete observations, not a beam or network icon.
  const crossingPackets=new THREE.Group();crossingPackets.name='Crossing telemetry frames';linkGroup.add(crossingPackets);
  const frameGeometry=new THREE.BoxGeometry(.19,.12,.035),frameMaterial=new THREE.MeshBasicMaterial({color:'#9edce0',wireframe:true});geometries.push(frameGeometry);materials.push(frameMaterial);
  const frames=new THREE.InstancedMesh(frameGeometry,frameMaterial,12);crossingPackets.add(frames);
  const endpointRings=[];
  for(const endpoint of [points[0],points[3]])for(let i=0;i<2;i++){
    const cue=new THREE.Mesh(ringGeometry,ringMaterial.clone());cue.position.copy(endpoint);materials.push(cue.material);crossingPackets.add(cue);endpointRings.push(cue);
  }
  return {
    group,route,stationVisual,
    update(time,online,camera,visible,crossing=false,shore=false){
      group.visible=visible;linkGroup.visible=visible&&online;
      crossingPackets.visible=crossing;packets.visible=!crossing;routeMaterial.opacity=crossing?.18:.43;
      rings.forEach(r=>r.visible=!crossing);
      if(!visible)return;
      if(crossing){
        for(let i=0;i<12;i++){const phase=(time*.09+i/12)%1;dummy.position.copy(route.getPoint(phase));dummy.quaternion.copy(camera.quaternion);dummy.updateMatrix();frames.setMatrixAt(i,dummy.matrix);}
        frames.instanceMatrix.needsUpdate=true;
        endpointRings.forEach((ring,i)=>{const phase=(time*.5+(i%2)*.5)%1;ring.scale.setScalar(.7+phase*2.3);ring.material.opacity=(1-phase)*.32;ring.quaternion.copy(camera.quaternion);});
      }
      for(let i=0;i<9;i++){const phase=(time*(shore?.045:.12)+i/9)%1;dummy.position.copy(route.getPoint(phase));dummy.rotation.set(0,time+i,Math.PI/4);dummy.updateMatrix();packets.setMatrixAt(i,dummy.matrix);}
      packets.instanceMatrix.needsUpdate=true;
      for(let i=0;i<rings.length;i++){const phase=(time*.7+i/3)%1;rings[i].scale.setScalar(1+phase*2);rings[i].material.opacity=(1-phase)*.55;rings[i].quaternion.copy(camera.quaternion);}
    },
    dispose(){eveningLight.shadow.map?.dispose();new Set(geometries).forEach(g=>g.dispose());new Set(materials).forEach(m=>m.dispose());}
  };
}
