import * as THREE from 'three';
import {GLTFLoader} from 'three/examples/jsm/loaders/GLTFLoader.js';
import modelUrl from '../dashboard-next/public/models/PROJECT-FALCON-V2.glb?url';
import {components,CH,chapterCount} from './story.js';
import {easeInspection,inspectionFrame} from './inspection.js';
import {createCoast,coastCamera,crossingCamera,RECEIVER} from './coast.js';
import {homeShots,homeCamera,homeWeight,oceanFieldGLSL} from './home.js';
import {instrumentTargets} from './instrument.js';
import {placeCallout} from './composition.js';
import {buoyMotion,cameraBlend} from './motion.js';
import {createBayStation} from './bay-station.js';
import {createHomeOrbit} from './home-orbit.js';

// Camera choreography only. The supplied CAD mesh and its materials are untouched.
// One pose per chapter, in chapter order. Indices 2, 3 and 4 are the buoy
// views the chapter-01/02 hotspot solver was tuned against, so they keep their
// exact original framing; the wrap-up chapters reuse the final wide shot.
const poses = [
  homeShots[0],
  {eye:[2.6,1.45,3.8], aim:[-.65,.55,0]},
  {eye:[2.9,1.25,4.5], aim:[-.2,.5,0]},
  {eye:[1.4,1,2.6], aim:[1.8,.7,0]},
  {eye:[2.9,1.25,4.5], aim:[-.2,.5,0]},
  coastCamera[0],
  coastCamera[2],
  {eye:[12,1.1,7], aim:[10,.2,-2]},
  {eye:[10,2.1,7], aim:[9,.3,-2]},
  {eye:[9,2.3,8], aim:[7,.4,-2]},
  {eye:[8,2.6,8.2], aim:[5,.4,-1]},
  {eye:[7.2,2.7,8.3], aim:[4.5,.35,-1]},
  {eye:[7,2.8,8.4], aim:[4,.35,-1]},
  {eye:[6,3,8.8], aim:[2.5,.25,-.5]},
  // Roadmap & Team -> Impact & Funding -> Acknowledgement: one slow,
  // continuous pull-back over the water. The last pose is the original finale
  // framing, so the ending still looks exactly as it always did.
  {eye:[5,3,9], aim:[0,.15,0]}
];
// The poses array and the chapter list must stay the same length: a mismatch
// would silently stretch or compress the whole camera timeline.
if(poses.length!==chapterCount)console.warn(`FALCON-01: ${poses.length} camera poses for ${chapterCount} chapters.`);

export async function createWorld(host, {onPick, onStatus, onInspectionReady=()=>{},onBayPick=()=>{},onBayReady=()=>{}}) {
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
  const bay=createBayStation(coast);let bayMove=null,bayOverview=null;
  function inspectBay(id){
    if(currentChapter!==5||contextLost)return false;const pose=bay.focus(id,camera.aspect);if(!pose)return false;
    if(!bayOverview){bayOverview={eye:camera.position.clone(),aim:aim.clone()};bay.reveal(false);}bay.select(id);
    bayMove={id,from:camera.position.clone(),fromAim:aim.clone(),eye:new THREE.Vector3(...pose.eye),aim:new THREE.Vector3(...pose.aim),elapsed:0,ready:false};return true;
  }
  function returnToBay(){if(!bayOverview)return;bay.select(null);bayMove={from:camera.position.clone(),fromAim:aim.clone(),...bayOverview,elapsed:0,ready:false,returning:true};bayOverview=null;}
  document.body.classList.add('coast-ready');
  const receiverLabel=document.querySelector('#coast-receiver-label');
  const markers = new Map(), hotspotLayer = document.querySelector('#hotspots');
  const leaderSvg=document.createElementNS('http://www.w3.org/2000/svg','svg');leaderSvg.setAttribute('aria-hidden','true');hotspotLayer.append(leaderSvg);
  let pageOneTargets=new Map();
  const targetFor=id=>currentChapter===1||currentChapter===2?pageOneTargets.get(id):markers.get(id)?.target;
  let model, disposed=false, contextLost=false, yaw=0, drag=null, orbitReset=null, needsDraw=true;
  let inspection=null, overview=null, hovered=null, tintKey='';
  // The callout solver reads layout from six elements every frame. Resolving
  // the list once and reusing the leader paths turns ~40 DOM operations per
  // frame into two attribute writes, which is the difference between a smooth
  // chapter and a stuttering one.
  const leaderPaths=new Map();
  const allObstacleEls=[
    ...document.querySelectorAll('header,.journey-nav,.model-state,.cad-caption,.source-caption,#inspection-panel,#acquisition-signal')
  ];
  // Which elements actually stand in the way only changes when the chapter or
  // the inspection panel changes - never frame to frame. The rects, on the
  // other hand, move with the scroll, so those are still measured every frame.
  let obstacleEpoch='',obstacleEls=[];
  function obstacleRects(chapter,isInspecting){
    const epoch=`${chapter}|${isInspecting?1:0}`;
    if(epoch!==obstacleEpoch){
      obstacleEpoch=epoch;
      obstacleEls=[...allObstacleEls,...document.querySelectorAll('#buoy.is-active .copy,#sensors.is-active .copy')]
        .filter(e=>e.getClientRects().length&&getComputedStyle(e).visibility!=='hidden');
    }
    return obstacleEls.map(e=>e.getBoundingClientRect());
  }
  const materialCopies=[];
  const connection=document.querySelector('#inspection-wire path');
  const inspectionPanel=document.querySelector('#inspection-panel');
  const acquisitionSignal=document.querySelector('#acquisition-signal');
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
    const frame=inspectionFrame(center.toArray(),Math.max(size.x,size.y,size.z),camera.aspect,innerWidth<650,camera.position.toArray());
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
  const compositionBounds=new THREE.Box3();
  function projectedBounds(bounds){
    const result={left:Infinity,right:-Infinity,top:Infinity,bottom:-Infinity};
    for(const x of [bounds.min.x,bounds.max.x])for(const y of [bounds.min.y,bounds.max.y])for(const z of [bounds.min.z,bounds.max.z]){
      projection.set(x,y,z).project(camera);const px=(projection.x+1)*innerWidth/2,py=(1-projection.y)*innerHeight/2;
      result.left=Math.min(result.left,px);result.right=Math.max(result.right,px);result.top=Math.min(result.top,py);result.bottom=Math.max(result.bottom,py);
    }return result;
  }
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
      const aliases=id==='battery'?[prefix,'LIFEPO4_BATTERY','BATTERY_12V','BATTERY']:[prefix];
      let target;model.traverse(o=>{if(!target){const name=o.name.toUpperCase();if(aliases.some(alias=>name.startsWith(alias)))target=o;}});
      if(!target)continue;
      const button=document.createElement('button');button.className='hotspot';button.textContent=c.label;button.dataset.component=id;button.dataset.index=String(Object.keys(components).indexOf(id)+1).padStart(2,'0');button.setAttribute('aria-label',c.label);button.setAttribute('aria-pressed','false');
      button.addEventListener('click',()=>onPick(id));hotspotLayer.append(button);markers.set(id,{target,button});
    }
    onStatus('Original V2 CAD · motion / waterline illustrative');
  },undefined,()=>{onStatus('Original CAD failed to load · no substitute model used');document.body.classList.add('webgl-unavailable');});
  const raycaster=new THREE.Raycaster();
  let currentChapter=0;
  const homeOrbit=createHomeOrbit();
  const down=e=>{if(homeOrbit.active&&currentChapter===0){drag={last:e.clientX,lastY:e.clientY};return;}if(currentChapter===5||(!inspection&&(currentChapter===1||currentChapter===2))){orbitReset=null;drag={x:e.clientX,y:e.clientY,last:e.clientX,distance:0};}};
  const move=e=>{if(!drag)return;if(homeOrbit.active&&currentChapter===0){homeOrbit.drag(e.clientX-drag.last,e.clientY-drag.lastY);drag.last=e.clientX;drag.lastY=e.clientY;needsDraw=true;return;}if(e.pointerType==='touch')return;const delta=e.clientX-drag.last;drag.distance+=Math.abs(delta);if(currentChapter!==5)yaw+=delta*.005;drag.last=e.clientX;};
  const up=e=>{
    if(!drag)return;
    if(homeOrbit.active&&currentChapter===0){drag=null;return;}
    const distance=Math.hypot(e.clientX-drag.x,e.clientY-drag.y)+drag.distance;drag=null;
    if(distance>8)return;
    raycaster.setFromCamera(new THREE.Vector2(e.clientX/innerWidth*2-1,1-e.clientY/innerHeight*2),camera);
    if(currentChapter===5){const id=bay.pick(raycaster);if(id)onBayPick(id);return;}
    if(!model)return;
    for(const hit of raycaster.intersectObject(model,true)){let object=hit.object;while(object){const id=Object.keys(components).find(key=>object===targetFor(key));if(id){onPick(id);return;}object=object.parent;}}
  };
  renderer.domElement.addEventListener('pointerdown',down);window.addEventListener('pointermove',move);window.addEventListener('pointerup',up);
  const wheel=e=>{if(currentChapter===0&&homeOrbit.active){e.preventDefault();homeOrbit.zoom(e.deltaY*(e.deltaMode===1?16:e.deltaMode===2?innerHeight:1));needsDraw=true;}};
  renderer.domElement.addEventListener('wheel',wheel,{passive:false});
  const cancel=()=>{drag=null;};window.addEventListener('pointercancel',cancel);
  const reset=()=>{orbitReset={from:yaw,elapsed:0};};document.querySelector('#reset-camera').addEventListener('click',reset);
  const resize=()=>{renderer.setSize(innerWidth,innerHeight);camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();if(inspection?.id&&!inspection.returning)beginInspection(inspection.id);if(bayMove?.id&&!bayMove.returning)inspectBay(bayMove.id);needsDraw=true;};resize();window.addEventListener('resize',resize);
  const lost=e=>{e.preventDefault();contextLost=true;onStatus('3D paused by device · reload to restore');document.body.classList.add('webgl-unavailable');};renderer.domElement.addEventListener('webglcontextlost',lost);
  const desiredEye=new THREE.Vector3(),desiredAim=new THREE.Vector3(),nextEye=new THREE.Vector3(),nextAim=new THREE.Vector3();
  let lastProgress=-1,lastPick='',lastYaw=-1,lastLink=true;
  return {
    setHomeOrbit(enabled){if(enabled){if(currentChapter!==0||!model||contextLost)return false;homeOrbit.enter(camera.position.toArray());}else homeOrbit.exit();drag=null;needsDraw=true;return true;},
    moveHomeOrbit(dx,dy,zoom=0){if(currentChapter===0&&homeOrbit.active){homeOrbit.drag(dx,dy);homeOrbit.zoom(zoom);needsDraw=true;}},
    inspectBay,returnToBay,
    inspect:beginInspection,
    returnToBuoy,
    hover(id){hovered=id;needsDraw=true;},
    update({progress,chapter,time,dt,moving,pointer,selected,linkOnline=true,homeProgress=0}) {
      if(disposed||contextLost)return;
      currentChapter=chapter;
      if(chapter!==0)homeOrbit.exit();
      if(chapter!==5&&(bayMove||bayOverview)){bayMove=null;bayOverview=null;bay.select(null);}
      if(orbitReset){orbitReset.elapsed+=dt;const t=moving?Math.min(1,orbitReset.elapsed/1.2):1;yaw=orbitReset.from*(1-easeInspection(t));if(t===1)orbitReset=null;needsDraw=true;}
      const a=Math.max(0,Math.min(chapterCount-1,Math.floor(progress))),b=Math.min(chapterCount-1,a+1),t=THREE.MathUtils.smoothstep(progress-a,0,1);
      desiredEye.fromArray(poses[a].eye).lerp(nextEye.fromArray(poses[b].eye),t);
      desiredAim.fromArray(poses[a].aim).lerp(nextAim.fromArray(poses[b].aim),t);
      if(progress<CH.objectives){const shot=homeCamera(homeProgress);desiredEye.fromArray(shot.eye);desiredAim.fromArray(shot.aim);}
      // The radio -> shore run is a four-shot coastal fly-through. Its span is
      // derived from the named chapter indices so moving a chapter moves it too.
      const coastFrom=CH.radio, coastTo=CH.shore+1;
      if(progress>=coastFrom&&progress<coastTo){
        const p=Math.min(3,(progress-coastFrom)*2),i=Math.floor(p),j=Math.min(3,i+1),u=THREE.MathUtils.smoothstep(p-i,0,1);
        desiredEye.fromArray(coastCamera[i].eye).lerp(nextEye.fromArray(coastCamera[j].eye),u);
        desiredAim.fromArray(coastCamera[i].aim).lerp(nextAim.fromArray(coastCamera[j].aim),u);
        if(progress>coastTo-.25){const blend=THREE.MathUtils.smoothstep(progress,coastTo-.25,coastTo);desiredEye.lerp(nextEye.fromArray(poses[coastTo].eye),blend);desiredAim.lerp(nextAim.fromArray(poses[coastTo].aim),blend);}
      }
      if(chapter===CH.radio){
        const p=Math.min(2,(progress-coastFrom)*2),i=Math.min(1,Math.floor(p)),u=THREE.MathUtils.smoothstep(p-i,0,1);
        desiredEye.fromArray(crossingCamera[i].eye).lerp(nextEye.fromArray(crossingCamera[i+1].eye),u);
        desiredAim.fromArray(crossingCamera[i].aim).lerp(nextAim.fromArray(crossingCamera[i+1].aim),u);
        if(innerWidth<650){const wide=1+.9*(1-THREE.MathUtils.smoothstep(progress,coastFrom+.65,coastFrom+1));desiredEye.sub(desiredAim).multiplyScalar(wide).add(desiredAim);}
      }
      if(innerWidth<650){desiredEye.multiplyScalar(1.25);desiredAim.x+=.45;desiredAim.y+=.35;}
      if(innerWidth<650&&progress<CH.objectives)desiredAim.y+=(1-homeProgress)*desiredEye.distanceTo(desiredAim)*.16;
      // Reserve a middle-water stage between the mobile title and source index.
      if(innerWidth<650&&progress>=CH.objectives&&progress<CH.sensors){
        const weight=THREE.MathUtils.smoothstep(progress,CH.objectives,CH.objectives+.25)*(1-THREE.MathUtils.smoothstep(progress,CH.sensors-.35,CH.sensors));
        desiredEye.lerp(nextEye.set(3.8,1.8,6),weight);desiredAim.lerp(nextAim.set(0,1.15,0),weight);
      }
      if(moving){desiredEye.x+=pointer.x*.1;desiredEye.y+=pointer.y*.06;}
      if(chapter===CH.ocean&&homeOrbit.active){const pose=homeOrbit.update(dt);desiredEye.fromArray(pose.eye);desiredAim.fromArray(pose.aim);needsDraw=true;}
      const blend=moving?cameraBlend(dt):1;
      if(chapter===CH.shore&&bayMove){
        bayMove.elapsed+=dt;const t=moving?Math.min(1,bayMove.elapsed/1.65):1,u=easeInspection(t);
        camera.position.lerpVectors(bayMove.from,bayMove.eye,u);aim.lerpVectors(bayMove.fromAim,bayMove.aim,u);
        if(t===1&&!bayMove.ready){bayMove.ready=true;if(bayMove.returning)bayMove=null;else{bay.reveal(true);onBayReady();}}
        needsDraw=true;
      }else if(inspection){
        if(inspection.page!==chapter){inspection=null;overview=null;}
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
      const homeMix=progress<CH.objectives?homeWeight(homeProgress):0;
      ocean.geometry=homeMix>0?homeOceanGeometry:legacyOceanGeometry;
      ocean.material.uniforms.homeWeight.value=homeMix;ocean.material.uniforms.homeProgress.value=homeProgress;
      const motion=buoyMotion(time);
      buoy.position.x=progress>=coastFrom-.35&&progress<coastTo+.15?-8:0;
      buoy.position.y=motion.heave;
      buoy.rotation.z=motion.roll;
      buoy.rotation.x=motion.pitch;
      ocean.material.uniforms.time.value=time;
      ocean.material.uniforms.opacity.value=inspection?.id==='pressure'?.12:chapter===CH.buoy?.62:1;
      buoy.updateMatrixWorld(true);camera.updateMatrixWorld(true);
      compositionBounds.makeEmpty();if(chapter<=CH.buoy)for(const target of pageOneTargets.values())compositionBounds.union(box.setFromObject(target));
      const coastVisible=progress>=coastFrom-.35&&progress<coastTo+.15;
      coast.update(time,linkOnline,camera,coastVisible,chapter===CH.radio,chapter===CH.shore);
      // The coastal hamlet only exists while the radio -> shore run is on screen.
      bay.update(time,linkOnline,chapter===CH.shore);
      if(receiverLabel){
        projection.set(...RECEIVER).project(camera);
        const x=(projection.x*.5+.5)*innerWidth,y=(-projection.y*.5+.5)*innerHeight;
        receiverLabel.hidden=!coastVisible||projection.z>1||x<0||x>innerWidth-110||y<110||y>innerHeight-100;
        receiverLabel.style.left=`${x}px`;receiverLabel.style.top=`${y-25}px`;
        receiverLabel.textContent=linkOnline?'LoRa RX · BAY STATION':'LoRa RX · LINK INTERRUPTED';
      }
      const visible=chapter===CH.objectives||chapter===CH.buoy;
      hotspotLayer.hidden=!visible;
      if(visible){
        const occupied=[];
        const obstacles=obstacleRects(chapter,!!inspection);
        const silhouette=compositionBounds.isEmpty()?{left:0,right:innerWidth}:projectedBounds(compositionBounds);
        for(const [id,{button}] of markers){
          const target=targetFor(id);
          box.setFromObject(target).getCenter(projection);projection.project(camera);
          const x=(projection.x*.5+.5)*innerWidth,y=(-projection.y*.5+.5)*innerHeight;
          const placement=!inspection&&projection.z<1&&projection.z>-1?placeCallout({x,y},silhouette,[...obstacles,...occupied],{left:24,right:innerWidth-24,top:115,bottom:innerHeight-105}):null;
          button.hidden=!placement;button.setAttribute('aria-pressed',String(id===selected));
          let line=leaderPaths.get(id);
          if(placement){
            button.style.left=`${placement.x}px`;button.style.top=`${placement.y}px`;occupied.push(placement.rect);
            if(!line){line=document.createElementNS('http://www.w3.org/2000/svg','path');leaderPaths.set(id,line);leaderSvg.append(line);}
            if(line.getAttribute('d')!==placement.path)line.setAttribute('d',placement.path);
          }else if(line)line.setAttribute('d','');
        }
      }else{
        // Leaving the chapter clears the layer once instead of laying out for
        // callouts that are already hidden.
        for(const [id,{button}] of markers){button.hidden=true;leaderPaths.get(id)?.setAttribute('d','');}
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
        const rect=inspectionPanel.getBoundingClientRect();
        const endX=innerWidth<650?rect.left+rect.width*.5:rect.left,endY=innerWidth<650?rect.top:rect.top+110;
        connection.setAttribute('d',`M${x},${y} L${(x+endX)*.5},${y} L${endX},${endY}`);
      }else if(chapter===CH.buoy&&chosen&&!inspection){
        projection.copy(halo.position).project(camera);
        const rect=acquisitionSignal.getBoundingClientRect();
        const x=(projection.x*.5+.5)*innerWidth,y=(-projection.y*.5+.5)*innerHeight;
        connection.setAttribute('d',projection.z<1&&x>0&&x<innerWidth&&rect.top>90&&rect.top<innerHeight-80?`M${x},${y} L${rect.left-22},${y} L${rect.left},${rect.top+35}`:'');
      }else connection.setAttribute('d','');
      needsDraw=moving||lastLink!==linkOnline||lastProgress!==progress||lastPick!==selected||lastYaw!==yaw||camera.position.distanceTo(desiredEye)>.001||needsDraw;
      if(needsDraw)renderer.render(scene,camera);
      needsDraw=false;lastProgress=progress;lastPick=selected;lastYaw=yaw;lastLink=linkOnline;
    },
    dispose(){disposed=true;restoreMaterials();bay.dispose();coast.dispose();window.removeEventListener('resize',resize);window.removeEventListener('pointermove',move);window.removeEventListener('pointerup',up);window.removeEventListener('pointercancel',cancel);document.querySelector('#reset-camera').removeEventListener('click',reset);if(model)disposeModel(model);legacyOceanGeometry.dispose();homeOceanGeometry.dispose();for(const mesh of [ocean,sky,halo]){if(mesh!==ocean)mesh.geometry.dispose();mesh.material.dispose();}renderer.dispose();renderer.domElement.remove();hotspotLayer.replaceChildren();}
  };
}
