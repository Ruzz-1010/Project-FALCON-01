import * as THREE from 'three';
import {GLTFLoader} from 'three/examples/jsm/loaders/GLTFLoader.js';
import modelUrl from '../dashboard-next/public/models/PROJECT-FALCON-V2.glb?url';
import {components} from './story.js';
import {easeInspection,inspectionFrame} from './inspection.js';
import {createCoast,coastCamera,RECEIVER} from './coast.js';
import {homeShots,homeCamera,homeWeight,oceanSample,oceanFieldGLSL} from './home.js';
import {instrumentTargets} from './instrument.js';

// Camera choreography only. The supplied CAD mesh and its materials are untouched.
const poses = [
  homeShots[0],
  {eye:[2.6,1.45,3.8], aim:[-.65,.55,0]},
  {eye:[2.1,.65,3.3], aim:[-.65,.36,0]},
  {eye:[1.4,1,2.6], aim:[1.8,.7,0]},
  coastCamera[0],
  coastCamera[2],
  {eye:[12,1.1,7], aim:[10,.2,-2]},
  {eye:[10,2.1,7], aim:[9,.3,-2]},
  {eye:[9,2.3,8], aim:[7,.4,-2]},
  {eye:[5,3,9], aim:[0,.15,0]}
];

export async function createWorld(host, {onPick, onStatus, onInspectionReady=()=>{}}) {
  let renderer;
  try { renderer = new THREE.WebGLRenderer({antialias: true, alpha: false, powerPreference:'low-power'}); }
  catch { document.body.classList.add('webgl-unavailable'); onStatus('3D unavailable · diagrams and story remain accessible'); return {update(){},dispose(){}}; }
  renderer.setPixelRatio(Math.min(devicePixelRatio, 1.4));
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.15;
  renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;
  host.append(renderer.domElement);
  const scene = new THREE.Scene();
  scene.fog = new THREE.FogExp2('#102b38', .022);
  const camera = new THREE.PerspectiveCamera(42, 1, .03, 180);
  camera.position.fromArray(poses[0].eye);
  const aim = new THREE.Vector3().fromArray(poses[0].aim);
  scene.add(new THREE.HemisphereLight('#d0e5ed', '#203039', 2.4));
  const sun = new THREE.DirectionalLight('#f8e1b5', 3.4); sun.position.set(-3, 6, 2); scene.add(sun);
  const rim = new THREE.DirectionalLight('#8dc4e3', 2); rim.position.set(3, 2, -4); scene.add(rim);
  const sky = new THREE.Mesh(new THREE.SphereGeometry(130,32,16), new THREE.ShaderMaterial({
    side: THREE.BackSide, depthWrite:false,
    vertexShader: 'varying vec3 vDirection; void main(){vDirection=position;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}',
    fragmentShader: `varying vec3 vDirection;
      void main(){vec3 d=normalize(vDirection);float h=smoothstep(-.02,.75,d.y);
      vec3 c=mix(vec3(.11,.23,.28),vec3(.012,.035,.065),h);
      float sun=pow(max(dot(d,normalize(vec3(-.7,.16,-1.))),0.),180.);
      c+=vec3(.55,.49,.36)*sun;gl_FragColor=vec4(c,1.);}`
  })); scene.add(sky);
  const ocean = new THREE.Mesh(new THREE.PlaneGeometry(130,130,150,150),new THREE.ShaderMaterial({
    transparent:true, side:THREE.DoubleSide,
    uniforms:{time:{value:0},opacity:{value:1},homeWeight:{value:0},homeProgress:{value:0}},
    vertexShader:`uniform float time;uniform float homeWeight;uniform float homeProgress;varying vec3 vWorld;varying float vHeight;
      ${oceanFieldGLSL}
      void main(){vec3 p=position;float t=time*.55;
      p.z=sin(p.x*.85+t)*.043+sin(p.y*1.3+t*.7)*.026+sin(p.x*2.6+p.y*1.7+t*1.3)*.013;
      if(homeWeight>0.)p.z=mix(p.z,homeField(vec2(p.x,-p.y),time,homeProgress).x,homeWeight);
      vec4 w=modelMatrix*vec4(p,1.);vWorld=w.xyz;vHeight=p.z;gl_Position=projectionMatrix*viewMatrix*w;}`,
    fragmentShader:`uniform float time;uniform float opacity;uniform float homeWeight;uniform float homeProgress;varying vec3 vWorld;varying float vHeight;
      ${oceanFieldGLSL}
      void main(){vec3 n=normalize(cross(dFdx(vWorld),dFdy(vWorld)));if(n.y<0.)n=-n;
      vec3 field=vec3(0.);
      if(homeWeight>0.){field=homeField(vWorld.xz,time,homeProgress);n=normalize(mix(n,normalize(vec3(-field.y,1.,-field.z)),homeWeight));}
      vec3 v=normalize(cameraPosition-vWorld);float fresnel=pow(1.-max(dot(v,n),0.),3.);
      vec3 light=normalize(vec3(-.6,.7,.4));float shine=pow(max(dot(reflect(-light,n),v),0.),85.);
      vec3 c=mix(vec3(.015,.082,.115),vec3(.12,.24,.28),fresnel);
      c+=max(vHeight,0.)*vec3(.4,.7,.7)+shine*vec3(.65,.65,.49)*.65;
      float crest=smoothstep(.08,.125,field.x)*.085*homeWeight;
      c+=vec3(.54,.68,.69)*crest;
      float fog=1.-exp(-length(cameraPosition-vWorld)*.022);c=mix(c,vec3(.063,.17,.22),fog);
      gl_FragColor=vec4(c,opacity);}`
  })); ocean.rotation.x=-Math.PI/2;scene.add(ocean);
  const legacyOceanGeometry=ocean.geometry,homeOceanGeometry=legacyOceanGeometry.clone();
  // More vertices near the camera/buoy; broad, cheaper cells toward the horizon.
  const homePositions=homeOceanGeometry.attributes.position;
  for(let i=0;i<homePositions.count;i++){for(const axis of ['X','Y']){const v=homePositions[`get${axis}`](i)/65;homePositions[`set${axis}`](i,Math.sign(v)*Math.pow(Math.abs(v),1.45)*65);}}
  const buoy = new THREE.Group();scene.add(buoy);
  const coast=createCoast();coast.group.visible=false;scene.add(coast.group);
  document.body.classList.add('coast-ready');
  const receiverLabel=document.querySelector('#coast-receiver-label');
  const markers = new Map(), hotspotLayer = document.querySelector('#hotspots');
  let pageOneTargets=new Map();
  const targetFor=id=>currentChapter===1?pageOneTargets.get(id):markers.get(id)?.target;
  let model, disposed=false, contextLost=false, yaw=0, drag=null, needsDraw=true;
  let inspection=null, overview=null, hovered=null, tintKey='';
  const materialCopies=[];
  const connection=document.querySelector('#inspection-wire path');
  function restoreMaterials(){for(const {mesh,original,copies} of materialCopies){mesh.material=original;copies.forEach(m=>m.dispose());}materialCopies.length=0;}
  function tint(target,focused){
    restoreMaterials();if(!model||!target)return;
    const selectedMeshes=new Set();target.traverse(o=>{if(o.isMesh)selectedMeshes.add(o);});
    model.traverse(mesh=>{if(!mesh.isMesh)return;const original=mesh.material;
      const copies=[].concat(original).map(m=>{const copy=m.clone();if(selectedMeshes.has(mesh)){if(copy.emissive){copy.emissive.set('#48aebc');copy.emissiveIntensity=focused?.3:.12;}}else if(focused&&copy.color)copy.color.multiplyScalar(.62);return copy;});
      mesh.material=Array.isArray(original)?copies:copies[0];materialCopies.push({mesh,original,copies,selected:selectedMeshes.has(mesh)});
    });needsDraw=true;
  }
  function beginInspection(id){
    if(contextLost||!markers.has(id))return false;
    if(!overview)overview={eye:camera.position.clone(),aim:aim.clone()};
    const target=targetFor(id);if(!target)return false;
    const bounds=new THREE.Box3().setFromObject(target),center=bounds.getCenter(new THREE.Vector3()),size=bounds.getSize(new THREE.Vector3());
    const frame=inspectionFrame(center.toArray(),Math.max(size.x,size.y,size.z),camera.aspect,innerWidth<650);
    const eye=new THREE.Vector3().fromArray(frame.eye),targetAim=new THREE.Vector3().fromArray(frame.aim);
    inspection={id,page:currentChapter,from:camera.position.clone(),fromAim:aim.clone(),eye,aim:targetAim,elapsed:0,returning:false,ready:false};
    drag=null;needsDraw=true;return true;
  }
  function returnToBuoy(){
    if(!overview)return;
    inspection={id:inspection?.id,page:inspection?.page,from:camera.position.clone(),fromAim:aim.clone(),eye:overview.eye,aim:overview.aim,elapsed:0,returning:true,ready:false};
    overview=null;hovered=null;needsDraw=true;
  }
  const projection=new THREE.Vector3(), box=new THREE.Box3();
  const halo=new THREE.Mesh(new THREE.TorusGeometry(.035,.002,6,24),new THREE.MeshBasicMaterial({color:'#e4c999',depthTest:false,transparent:true}));halo.visible=false;halo.renderOrder=10;scene.add(halo);
  function disposeModel(root){root.traverse(o=>{if(o.isMesh){o.geometry.dispose();for(const m of [].concat(o.material)){for(const value of Object.values(m))if(value?.isTexture)value.dispose();m.dispose();}}});}
  new GLTFLoader().load(modelUrl,gltf=>{
    if(disposed){disposeModel(gltf.scene);return;}
    model=gltf.scene;model.rotation.x=-Math.PI/2;needsDraw=true;
    // View origin aligned to the existing float. Waterline is illustrative, not a draft result.
    model.position.y=-2.05;buoy.add(model);buoy.updateMatrixWorld(true);
    pageOneTargets=instrumentTargets(model);
    for(const [id,c] of Object.entries(components)) {
      const prefix=id==='esp32'?'REV5_RECTANGULAR_MARINE_ELECTRONICS_POD':c.prefix;
      let target;model.traverse(o=>{if(!target&&o.name.toUpperCase().startsWith(prefix))target=o;});
      if(!target)continue;
      const button=document.createElement('button');button.className='hotspot';button.textContent=c.label;button.dataset.component=id;button.setAttribute('aria-pressed','false');
      button.addEventListener('click',()=>onPick(id));hotspotLayer.append(button);markers.set(id,{target,button});
    }
    onStatus('Original V2 CAD · motion / waterline illustrative');
  },undefined,()=>{onStatus('Original CAD failed to load · no substitute model used');document.body.classList.add('webgl-unavailable');});
  const raycaster=new THREE.Raycaster();
  let currentChapter=0;
  const down=e=>{if(!inspection&&(currentChapter===1||currentChapter===2))drag={x:e.clientX,y:e.clientY,last:e.clientX,distance:0};};
  const move=e=>{if(!drag||e.pointerType==='touch')return;const delta=e.clientX-drag.last;drag.distance+=Math.abs(delta);yaw+=delta*.005;drag.last=e.clientX;};
  const up=e=>{
    if(!drag)return;
    const distance=Math.hypot(e.clientX-drag.x,e.clientY-drag.y)+drag.distance;drag=null;
    if(!model||distance>8)return;
    raycaster.setFromCamera(new THREE.Vector2(e.clientX/innerWidth*2-1,1-e.clientY/innerHeight*2),camera);
    for(const hit of raycaster.intersectObject(model,true)){let object=hit.object;while(object){const id=Object.keys(components).find(key=>currentChapter===1?object===targetFor(key):object.name.toUpperCase().startsWith(components[key].prefix));if(id){onPick(id);return;}object=object.parent;}}
  };
  renderer.domElement.addEventListener('pointerdown',down);window.addEventListener('pointermove',move);window.addEventListener('pointerup',up);
  const cancel=()=>{drag=null;};window.addEventListener('pointercancel',cancel);
  const reset=()=>{yaw=0;};document.querySelector('#reset-camera').addEventListener('click',reset);
  const resize=()=>{renderer.setSize(innerWidth,innerHeight);camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();if(inspection?.id&&!inspection.returning)beginInspection(inspection.id);needsDraw=true;};resize();window.addEventListener('resize',resize);
  const lost=e=>{e.preventDefault();contextLost=true;onStatus('3D paused by device · reload to restore');document.body.classList.add('webgl-unavailable');};renderer.domElement.addEventListener('webglcontextlost',lost);
  const desiredEye=new THREE.Vector3(),desiredAim=new THREE.Vector3(),nextEye=new THREE.Vector3(),nextAim=new THREE.Vector3();
  let lastProgress=-1,lastPick='',lastYaw=-1,lastLink=true;
  return {
    inspect:beginInspection,
    returnToBuoy,
    hover(id){hovered=id;needsDraw=true;},
    update({progress,chapter,time,dt,moving,pointer,selected,linkOnline=true,homeProgress=0}) {
      if(disposed||contextLost)return;
      currentChapter=chapter;
      const a=Math.max(0,Math.min(9,Math.floor(progress))),b=Math.min(9,a+1),t=THREE.MathUtils.smoothstep(progress-a,0,1);
      desiredEye.fromArray(poses[a].eye).lerp(nextEye.fromArray(poses[b].eye),t);
      desiredAim.fromArray(poses[a].aim).lerp(nextAim.fromArray(poses[b].aim),t);
      if(progress<1){const shot=homeCamera(homeProgress);desiredEye.fromArray(shot.eye);desiredAim.fromArray(shot.aim);}
      if(progress>=4&&progress<6){
        const p=Math.min(3,(progress-4)*2),i=Math.floor(p),j=Math.min(3,i+1),u=THREE.MathUtils.smoothstep(p-i,0,1);
        desiredEye.fromArray(coastCamera[i].eye).lerp(nextEye.fromArray(coastCamera[j].eye),u);
        desiredAim.fromArray(coastCamera[i].aim).lerp(nextAim.fromArray(coastCamera[j].aim),u);
        if(progress>5.75){const blend=THREE.MathUtils.smoothstep(progress,5.75,6);desiredEye.lerp(nextEye.fromArray(poses[6].eye),blend);desiredAim.lerp(nextAim.fromArray(poses[6].aim),blend);}
      }
      if(innerWidth<650){desiredEye.multiplyScalar(1.25);desiredAim.x+=.45;desiredAim.y+=.35;}
      if(innerWidth<650&&progress<1)desiredAim.y+=(1-homeProgress)*desiredEye.distanceTo(desiredAim)*.16;
      if(moving){desiredEye.x+=pointer.x*.1;desiredEye.y+=pointer.y*.06;}
      const blend=moving?1-Math.exp(-dt*5):1;
      if(inspection){
        if((chapter!==1&&chapter!==2)||(inspection.page===1&&chapter!==1)){inspection=null;overview=null;}
        else {
          inspection.elapsed+=dt;
          const t=moving?Math.min(1,inspection.elapsed/1.65):1,eased=easeInspection(t);
          camera.position.lerpVectors(inspection.from,inspection.eye,eased);aim.lerpVectors(inspection.fromAim,inspection.aim,eased);
          if(t===1&&!inspection.ready){inspection.ready=true;if(inspection.returning)inspection=null;else onInspectionReady();}
          needsDraw=true;
        }
      }else{camera.position.lerp(desiredEye,blend);aim.lerp(desiredAim,blend);}
      camera.lookAt(aim);
      buoy.rotation.y=yaw;
      const homeMix=progress<1?homeWeight(homeProgress):0;
      ocean.geometry=homeMix>0?homeOceanGeometry:legacyOceanGeometry;
      ocean.material.uniforms.homeWeight.value=homeMix;ocean.material.uniforms.homeProgress.value=homeProgress;
      if(moving){if(!inspection){
        const wave=oceanSample(0,0,time,homeProgress);
        buoy.position.y=THREE.MathUtils.lerp(Math.sin(time*.65)*.014,wave.height,homeMix);
        buoy.rotation.z=THREE.MathUtils.lerp(Math.sin(time*.44)*.006,THREE.MathUtils.clamp(wave.dx*.45,-.025,.025),homeMix);
        buoy.rotation.x=THREE.MathUtils.clamp(-wave.dz*.45,-.025,.025)*homeMix;
      }ocean.material.uniforms.time.value=time;}
      else if(progress>=1&&!inspection){buoy.rotation.x=0;}
      ocean.material.uniforms.opacity.value=inspection?.id==='pressure'?.12:chapter===2?.62:1;
      buoy.updateMatrixWorld(true);camera.updateMatrixWorld(true);
      const coastVisible=progress>=3.65&&progress<6.15;
      coast.update(time,linkOnline,camera,coastVisible);
      if(receiverLabel){
        projection.set(...RECEIVER).project(camera);
        const x=(projection.x*.5+.5)*innerWidth,y=(-projection.y*.5+.5)*innerHeight;
        receiverLabel.hidden=!coastVisible||projection.z>1||x<0||x>innerWidth-110||y<110||y>innerHeight-100;
        receiverLabel.style.left=`${x}px`;receiverLabel.style.top=`${y-25}px`;
        receiverLabel.textContent=linkOnline?'LoRa RX · BAY STATION':'LoRa RX · LINK INTERRUPTED';
      }
      const visible=chapter===1||chapter===2;
      hotspotLayer.hidden=!visible;
      const occupied=[];
      for(const [id,{button}] of markers){
        const target=targetFor(id);
        box.setFromObject(target).getCenter(projection);projection.project(camera);
        const x=(projection.x*.5+.5)*innerWidth,y=(-projection.y*.5+.5)*innerHeight;
        const overlaps=occupied.some(p=>Math.abs(p.y-y)<42&&Math.abs(p.x-x)<175);
        const leftLimit=inspection?20:innerWidth*(innerWidth<650?.56:.42);
        const bottomLimit=inspection&&innerWidth<650?innerHeight*.46:innerHeight-95;
        const show=visible&&projection.z<1&&projection.z>-1&&x>leftLimit&&x<innerWidth-165&&y>125&&y<bottomLimit&&(!overlaps||id===selected);
        button.hidden=!show;button.style.left=`${x}px`;button.style.top=`${y}px`;button.setAttribute('aria-pressed',String(id===selected));if(show)occupied.push({x,y});
      }
      const focused=inspection?.id;
      const chosenTarget=targetFor(focused||hovered||selected),chosen=chosenTarget?{target:chosenTarget}:null;halo.visible=visible&&!!chosen;
      const nextTint=visible?(focused||hovered||'')+(focused?':focus':'')+chapter:'';
      if(nextTint!==tintKey){tintKey=nextTint;tint(targetFor(focused||hovered),!!focused);}
      halo.material.opacity=1;
      if(focused){
        const ramp=moving?easeInspection(inspection.elapsed/1.65):1,strength=inspection.returning?1-ramp:ramp;
        halo.material.opacity=strength;
        for(const entry of materialCopies)entry.copies.forEach((m,i)=>{const original=[].concat(entry.original)[i];if(!entry.selected&&m.color)m.color.copy(original.color).multiplyScalar(1-.38*strength);if(entry.selected&&m.emissive)m.emissiveIntensity=.3*strength;});
      }
      halo.material.color.set(focused||hovered?'#70c7d2':'#e4c999');
      halo.scale.setScalar(focused?(1.15+(moving?Math.sin(time*2.2)*.12:0)):1);
      if(chosen){box.setFromObject(chosen.target).getCenter(halo.position);halo.quaternion.copy(camera.quaternion);}
      if(focused&&!inspection.returning&&inspection.ready&&chosen){
        projection.copy(halo.position).project(camera);
        const x=(projection.x*.5+.5)*innerWidth,y=(-projection.y*.5+.5)*innerHeight;
        const rect=document.querySelector('#inspection-panel').getBoundingClientRect();
        const endX=innerWidth<650?rect.left+rect.width*.5:rect.left,endY=innerWidth<650?rect.top:rect.top+110;
        connection.setAttribute('d',`M${x},${y} L${(x+endX)*.5},${y} L${endX},${endY}`);
      }else connection.setAttribute('d','');
      needsDraw=moving||lastLink!==linkOnline||lastProgress!==progress||lastPick!==selected||lastYaw!==yaw||camera.position.distanceTo(desiredEye)>.001||needsDraw;
      if(needsDraw)renderer.render(scene,camera);
      needsDraw=false;lastProgress=progress;lastPick=selected;lastYaw=yaw;lastLink=linkOnline;
    },
    dispose(){disposed=true;restoreMaterials();coast.dispose();window.removeEventListener('resize',resize);window.removeEventListener('pointermove',move);window.removeEventListener('pointerup',up);window.removeEventListener('pointercancel',cancel);document.querySelector('#reset-camera').removeEventListener('click',reset);if(model)disposeModel(model);legacyOceanGeometry.dispose();homeOceanGeometry.dispose();for(const mesh of [ocean,sky,halo]){if(mesh!==ocean)mesh.geometry.dispose();mesh.material.dispose();}renderer.dispose();renderer.domElement.remove();hotspotLayer.replaceChildren();}
  };
}
