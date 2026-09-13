import {useEffect,useRef,useState} from 'react';
import * as THREE from 'three';
import {GLTFLoader} from 'three/examples/jsm/loaders/GLTFLoader.js';
import {OrbitControls} from 'three/examples/jsm/controls/OrbitControls.js';
import modelUrl from '../public/models/PROJECT-FALCON-V2.glb?url';
import {sensors} from './content';

export default function BuoyModel({selected,onSelect,moving}:{selected:string;onSelect:(id:string)=>void;moving:boolean}){
 const host=useRef<HTMLDivElement>(null),selection=useRef(selected),callback=useRef(onSelect),motion=useRef(moving);
 const [state,setState]=useState('Loading your original CAD model…');
 useEffect(()=>{selection.current=selected;callback.current=onSelect;motion.current=moving},[selected,onSelect,moving]);
 useEffect(()=>{
  const container=host.current!;let disposed=false,frame=0,visible=true,model:THREE.Object3D|undefined;
  let renderer:THREE.WebGLRenderer;
  try{renderer=new THREE.WebGLRenderer({antialias:true,alpha:true})}catch{setState('3D is unavailable on this device. The component guide remains usable.');return}
  renderer.setPixelRatio(Math.min(devicePixelRatio,1.5));renderer.outputColorSpace=THREE.SRGBColorSpace;
  container.prepend(renderer.domElement);renderer.domElement.setAttribute('aria-label','Original FALCON CAD. Drag to orbit, scroll to zoom. Use component buttons for keyboard access.');
  const scene=new THREE.Scene(),camera=new THREE.PerspectiveCamera(38,1,.01,200);
  scene.add(new THREE.HemisphereLight(0xcde8f5,0x30444e,3));const sun=new THREE.DirectionalLight(0xffffff,3);sun.position.set(4,8,6);scene.add(sun);
  const group=new THREE.Group();scene.add(group);
  const waterGeometry=new THREE.PlaneGeometry(30,30,32,32);waterGeometry.rotateX(-Math.PI/2);
  const water=new THREE.Mesh(waterGeometry,new THREE.MeshPhongMaterial({color:0x285a6c,shininess:25,transparent:true,opacity:.55,side:THREE.DoubleSide}));water.position.y=-1.15;scene.add(water);
  camera.position.set(4,2,6);const controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=true;controls.minDistance=.5;controls.maxDistance=22;controls.maxPolarAngle=Math.PI*.85;
  const markers=new Map<string,THREE.Object3D>();
  const dot=new THREE.Mesh(new THREE.SphereGeometry(.045,12,8),new THREE.MeshBasicMaterial({color:0xe4bc72,depthTest:false}));dot.renderOrder=2;dot.visible=false;scene.add(dot);
  const reset=()=>{camera.position.set(4,2,6);controls.target.set(0,0,0);controls.update()};
  container.addEventListener('reset-camera',reset);
  const disposeModel=(root:THREE.Object3D)=>root.traverse(o=>{if(o instanceof THREE.Mesh){o.geometry.dispose();for(const m of Array.isArray(o.material)?o.material:[o.material]){for(const value of Object.values(m))if(value instanceof THREE.Texture)value.dispose();m.dispose()}}});
  new GLTFLoader().load(modelUrl,gltf=>{
   if(disposed){disposeModel(gltf.scene);return}
   model=gltf.scene;model.rotation.x=-Math.PI/2;model.updateMatrixWorld(true);
   const bounds=new THREE.Box3().setFromObject(model),size=bounds.getSize(new THREE.Vector3()),center=bounds.getCenter(new THREE.Vector3()),scale=4/Math.max(size.x,size.y,size.z);
   model.scale.setScalar(scale);model.position.copy(center).multiplyScalar(-scale);group.add(model);group.updateMatrixWorld(true);
   for(const sensor of sensors){if(!sensor.prefix)continue;model.traverse(o=>{if(!markers.has(sensor.id)&&o.name.toUpperCase().startsWith(sensor.prefix))markers.set(sensor.id,o)})}
   setState('Original V2 CAD · geometry unchanged');
  },undefined,()=>setState('Model could not load. Reload this local site; no substitute buoy is generated.'));
  const raycaster=new THREE.Raycaster();let down={x:0,y:0};
  const pointerDown=(e:PointerEvent)=>{down={x:e.clientX,y:e.clientY}};
  const pointerUp=(e:PointerEvent)=>{
   if(!model||Math.hypot(e.clientX-down.x,e.clientY-down.y)>6)return;
   const box=renderer.domElement.getBoundingClientRect();raycaster.setFromCamera(new THREE.Vector2((e.clientX-box.left)/box.width*2-1,-(e.clientY-box.top)/box.height*2+1),camera);
   for(const hit of raycaster.intersectObject(model,true)){let object:THREE.Object3D|null=hit.object;while(object){const sensor=sensors.find(s=>s.prefix&&object!.name.toUpperCase().startsWith(s.prefix));if(sensor){callback.current(sensor.id);return}object=object.parent}}
  };
  renderer.domElement.addEventListener('pointerdown',pointerDown);renderer.domElement.addEventListener('pointerup',pointerUp);
  const resize=()=>{const width=container.clientWidth,height=container.clientHeight;renderer.setSize(width,height);camera.aspect=width/Math.max(1,height);camera.updateProjectionMatrix()};const observer=new ResizeObserver(resize);observer.observe(container);resize();
  const intersection=new IntersectionObserver(([entry])=>{visible=entry.isIntersecting});intersection.observe(container);
  const reduced=matchMedia('(prefers-reduced-motion: reduce)');let previous=0,phase=0;
  const loop=(now:number)=>{
   frame=requestAnimationFrame(loop);if(now-previous<33)return;const dt=Math.min(.05,(now-previous)/1000);previous=now;if(!visible||document.hidden)return;
   if(motion.current&&!reduced.matches){phase+=dt*.55;group.position.y=Math.sin(phase)*.035;group.rotation.z=Math.sin(phase*.7)*.008;const p=waterGeometry.attributes.position;for(let i=0;i<p.count;i++)p.setY(i,Math.sin(p.getX(i)*.55+phase)*.045+Math.cos(p.getZ(i)*.6+phase)*.025);p.needsUpdate=true;waterGeometry.computeVertexNormals()}
   const target=markers.get(selection.current);dot.visible=!!target;if(target)dot.position.copy(new THREE.Box3().setFromObject(target).getCenter(new THREE.Vector3()));
   controls.update();renderer.render(scene,camera);
  };frame=requestAnimationFrame(loop);
  return()=>{disposed=true;cancelAnimationFrame(frame);observer.disconnect();intersection.disconnect();container.removeEventListener('reset-camera',reset);controls.dispose();if(model)disposeModel(model);waterGeometry.dispose();(water.material as THREE.Material).dispose();dot.geometry.dispose();(dot.material as THREE.Material).dispose();renderer.dispose();renderer.domElement.remove()};
 },[]);
 return <div className="model-host" ref={host}><span className="model-caption" role="status">{state}</span><button className="reset-view" onClick={()=>host.current?.dispatchEvent(new Event('reset-camera'))}>Reset view</button><span className="model-hint">Drag to rotate · Scroll to zoom · Tap a component</span></div>
}
