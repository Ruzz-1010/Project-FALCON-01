import { useEffect, useRef } from "react";
import * as THREE from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";

type Telemetry = { roll: number; pitch: number; yaw: number; wave: number; rough: boolean; fault: "sensor"|"thermal"|"power"|null };

export default function MotionScene({ telemetry }: { telemetry: Telemetry }) {
  const host = useRef<HTMLDivElement>(null);
  const live = useRef(telemetry);
  useEffect(() => { live.current = telemetry; }, [telemetry]);
  useEffect(() => {
    const container = host.current;
    if (!container) return;
    const canvas = document.createElement("canvas");
    canvas.setAttribute("aria-label", "Interactive FALCON buoy digital twin");
    container.prepend(canvas);
    const renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true });
    renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(34, 1, .01, 100);
    scene.add(new THREE.HemisphereLight(0xe7f6fb, 0x153d50, 2.55));
    const key = new THREE.DirectionalLight(0xf2f6f5, 3.2); key.position.set(3, 5, 4); scene.add(key);
    const rim = new THREE.DirectionalLight(0xa9d9e9, 1.15); rim.position.set(-4, 2, -3); scene.add(rim);
    const pose = new THREE.Group(); scene.add(pose);
    const seaGeometry = new THREE.PlaneGeometry(22, 22, 44, 44).toNonIndexed(); seaGeometry.rotateX(-Math.PI / 2);
    const base = new Float32Array(seaGeometry.attributes.position.array);
    const seaColors = new Float32Array(seaGeometry.attributes.position.count * 3);
    seaGeometry.setAttribute("color", new THREE.BufferAttribute(seaColors, 3));
    const seaMaterial = new THREE.MeshPhongMaterial({ color: 0xffffff, vertexColors:true, emissive: 0x123b4d, emissiveIntensity: .09, specular: 0x8ab7c5, shininess: 38, flatShading:true, transparent: true, opacity: .94, side: THREE.DoubleSide });
    const sea = new THREE.Mesh(seaGeometry, seaMaterial);
    sea.position.y = -.58; scene.add(sea);
    const seaGrid = new THREE.Mesh(seaGeometry, new THREE.MeshBasicMaterial({color:0x87afbc,wireframe:true,transparent:true,opacity:.038,depthWrite:false}));
    seaGrid.position.y=-.578;scene.add(seaGrid);
    const ringMaterial = new THREE.MeshBasicMaterial({ color: 0xc8ebf5, transparent: true, opacity: .2, side: THREE.DoubleSide, depthWrite:false });
    const ring = new THREE.Mesh(new THREE.RingGeometry(.43, .54, 64), ringMaterial);
    ring.rotation.x = -Math.PI / 2; scene.add(ring);
    let ready = false;
    let modelWaterlineOffset = -.08;
    const diagnostic: Record<string, Array<{material:THREE.MeshStandardMaterial;base:number;intensity:number}>> = {};
    new GLTFLoader().load("/models/FALCON-01.glb?v=4", gltf => {
      const model = gltf.scene; model.rotation.x = -Math.PI / 2;
      model.traverse(object => { if (object.name.toUpperCase().startsWith("ANCHOR_MOORING_SYSTEM")) object.visible = false; });
      model.updateMatrixWorld(true);
      const bounds = new THREE.Box3().setFromObject(model), size = bounds.getSize(new THREE.Vector3()), center = bounds.getCenter(new THREE.Vector3());
      const scale = 3.15 / Math.max(size.x, size.y, size.z, .001); model.scale.setScalar(scale); model.position.copy(center).multiplyScalar(-scale); pose.add(model);
      model.updateMatrixWorld(true);
      const mainFloat=model.getObjectByName("MAIN_FLOAT_TRADITIONAL_V2")||model.getObjectByName("MAIN_FLOAT_TRADITIONAL_V2:2")||model.getObjectByName("MAIN_FLOAT_TRADITIONAL_V2_HDPE_BODY");
      if(mainFloat){
        const floatBounds=new THREE.Box3().setFromObject(mainFloat),floatSize=floatBounds.getSize(new THREE.Vector3());
        // Presentation datum: water crosses 42% up from the rounded hull bottom.
        // Use only the main float geometry, excluding ballast, chain and tower.
        modelWaterlineOffset=-(floatBounds.min.y+floatSize.y*.42);
      }
      const register=(keyName:string,names:string[])=>{const part=names.map(name=>model.getObjectByName(name)||model.getObjectByName(`${name}:2`)||model.getObjectByName(`${name}:3`)).find(Boolean);diagnostic[keyName]=[];part?.traverse(object=>{const mesh=object as THREE.Mesh;if(!mesh.isMesh||!mesh.material)return;const materials=Array.isArray(mesh.material)?mesh.material:[mesh.material];materials.forEach(raw=>{const material=raw.clone() as THREE.MeshStandardMaterial;mesh.material=material;diagnostic[keyName].push({material,base:material.emissive?.getHex?.()||0,intensity:material.emissiveIntensity||0})})})};
      register("sensor",["TOP_SENSOR_ARRAY"]);register("thermal",["ELECTRONICS_BOX_V3"]);register("power",["ELECTRONICS_BOX_V3"]);
      [[-.28,.8,.02,0x72d99d],[0,.94,.02,0x56d7df],[.28,.8,.02,0xefbb70]].forEach(([x,y,z,color]) => { const light = new THREE.Mesh(new THREE.SphereGeometry(.035, 12, 8), new THREE.MeshBasicMaterial({color:color as number})); light.position.set(x as number,y as number,z as number); pose.add(light); });
      ready = true; container.classList.add("is-ready");
    }, undefined, () => container.classList.add("is-error"));
    const orbit = { yaw:.66, pitch:.34, distance:4.5 }, target = { ...{yaw:.66,pitch:.34,distance:4.5} };
    let pointer: {id:number;x:number;y:number}|null = null;
    const down=(e:PointerEvent)=>{pointer={id:e.pointerId,x:e.clientX,y:e.clientY};canvas.setPointerCapture(e.pointerId)};
    const move=(e:PointerEvent)=>{if(!pointer||pointer.id!==e.pointerId)return;target.yaw-=(e.clientX-pointer.x)*.008;target.pitch=THREE.MathUtils.clamp(target.pitch+(e.clientY-pointer.y)*.006,-.18,1.18);pointer.x=e.clientX;pointer.y=e.clientY};
    const up=()=>{pointer=null}; const wheel=(e:WheelEvent)=>{e.preventDefault();target.distance=THREE.MathUtils.clamp(target.distance+e.deltaY*.003,2.7,7)};
    canvas.addEventListener("pointerdown",down);canvas.addEventListener("pointermove",move);canvas.addEventListener("pointerup",up);canvas.addEventListener("wheel",wheel,{passive:false});
    const resize=()=>{const w=container.clientWidth,h=container.clientHeight;renderer.setSize(w,h,false);camera.aspect=w/Math.max(1,h);camera.updateProjectionMatrix()}; const observer=new ResizeObserver(resize);observer.observe(container);resize();
    const clock=new THREE.Clock(); let frame=0,phase=0,previous=0,normalFrame=0; const motion={roll:0,pitch:0,yaw:0,wave:.4};
    const surface=(x:number,z:number,a:number)=>Math.sin(x*.52+phase)*a+Math.sin(z*.64-phase*.58+x*.14)*a*.38+Math.sin((x+z)*.96+phase*.82)*a*.1;
    const deepSea=new THREE.Color(0x205b72),midSea=new THREE.Color(0x397f97),waveCrest=new THREE.Color(0x75a9b9),seaShade=new THREE.Color();
    const animate=()=>{frame=requestAnimationFrame(animate);const elapsed=clock.getElapsedTime(),dt=Math.min(.05,Math.max(.001,elapsed-previous));previous=elapsed;const t=live.current;
      motion.roll=THREE.MathUtils.damp(motion.roll,t.roll,1.25,dt);motion.pitch=THREE.MathUtils.damp(motion.pitch,t.pitch,1.25,dt);motion.yaw=THREE.MathUtils.damp(motion.yaw,t.yaw,1,dt);motion.wave=THREE.MathUtils.damp(motion.wave,t.wave,.72,dt);phase+=dt*(t.rough?.72:.38);
      const amp=THREE.MathUtils.lerp(.055,.25,THREE.MathUtils.clamp(motion.wave/3.5,0,1)),p=seaGeometry.attributes.position,colors=seaGeometry.attributes.color;
      for(let i=0;i<p.count;i++){const o=i*3,height=surface(base[o],base[o+2],amp),crest=THREE.MathUtils.smoothstep(height,-amp*.2,amp*1.25);seaShade.copy(deepSea).lerp(midSea,crest*.82).lerp(waveCrest,Math.max(0,(crest-.8)/.2)*.72);p.setY(i,height);colors.setXYZ(i,seaShade.r,seaShade.g,seaShade.b)}p.needsUpdate=true;colors.needsUpdate=true;if((normalFrame++%2)===0)seaGeometry.computeVertexNormals();
      const sway=Math.sin(phase*.38)*(.015+motion.wave*.009),surge=Math.sin(phase*.51+1.4)*(.014+motion.wave*.008),h=surface(sway,surge,amp),sample=.13,slopeX=(surface(sway+sample,surge,amp)-surface(sway-sample,surge,amp))/(sample*2),slopeZ=(surface(sway,surge+sample,amp)-surface(sway,surge-sample,amp))/(sample*2),waveRoll=THREE.MathUtils.radToDeg(Math.atan(slopeX))*.72,wavePitch=THREE.MathUtils.radToDeg(Math.atan(slopeZ))*.72;
      pose.position.x=THREE.MathUtils.damp(pose.position.x,sway,1.65,dt);pose.position.z=THREE.MathUtils.damp(pose.position.z,surge,1.65,dt);pose.position.y=THREE.MathUtils.damp(pose.position.y,-.58+h+modelWaterlineOffset,2.15,dt);pose.rotation.z=THREE.MathUtils.damp(pose.rotation.z,THREE.MathUtils.degToRad(-motion.roll*.38-waveRoll),2.15,dt);pose.rotation.x=THREE.MathUtils.damp(pose.rotation.x,THREE.MathUtils.degToRad(motion.pitch*.38+wavePitch),2.15,dt);pose.rotation.y=THREE.MathUtils.damp(pose.rotation.y,THREE.MathUtils.degToRad(motion.yaw),1.45,dt);ring.position.set(pose.position.x,-.555+h,pose.position.z);ring.rotation.z=-Math.atan(slopeX);ring.rotation.x=-Math.PI/2+Math.atan(slopeZ);ring.scale.setScalar(1+Math.sin(phase)*.035+Math.min(.12,motion.wave*.025));ringMaterial.opacity=.18+Math.max(0,Math.sin(phase*1.2))*.07;
      Object.entries(diagnostic).forEach(([name,materials])=>materials.forEach(item=>{const active=t.fault===name;item.material.emissive?.setHex(active?0xff302c:item.base);item.material.emissiveIntensity=active?.8+Math.max(0,Math.sin(elapsed*7))*2.4:item.intensity}));
      orbit.yaw=THREE.MathUtils.damp(orbit.yaw,target.yaw,10,dt);orbit.pitch=THREE.MathUtils.damp(orbit.pitch,target.pitch,10,dt);orbit.distance=THREE.MathUtils.damp(orbit.distance,target.distance,10,dt);const horizontal=orbit.distance*Math.cos(orbit.pitch);camera.position.set(horizontal*Math.sin(orbit.yaw),.05+orbit.distance*Math.sin(orbit.pitch),horizontal*Math.cos(orbit.yaw));camera.lookAt(0,.05,0);if(ready)renderer.render(scene,camera)};animate();
    return()=>{cancelAnimationFrame(frame);observer.disconnect();renderer.dispose();canvas.remove()};
  }, []);
  return <div className="motion-scene" ref={host}><span className="model-state">FUSION CAD · LIVE</span><span className="model-help">Drag to orbit · Scroll to zoom</span></div>;
}
