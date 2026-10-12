// FALCON Lite — compact event-driven can-buoy preview (procedural, no CAD edit).
// Round float body, tapered solar housing, LTE/Wi-Fi antenna, pressure
// stilling tube, heartbeat LED, GPS puck, and compact wind sensor. No LoRa gateway in this reduced baseline.
// PROPOSED ONLY: illustrative geometry for cost/design review. Not final,
// not fabrication-ready, not field-validated. V2 GLB used by world.js is untouched.
import * as THREE from 'three';

const stage = document.getElementById('stage');
const renderer = new THREE.WebGLRenderer({antialias:true});
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
stage.prepend(renderer.domElement);

const scene = new THREE.Scene();
scene.background = new THREE.Color('#08141b');
scene.fog = new THREE.FogExp2('#0b222e', 0.028);
const camera = new THREE.PerspectiveCamera(42, 1, 0.05, 200);

scene.add(new THREE.HemisphereLight('#cfe6ef', '#1c2f36', 2.2));
const sun = new THREE.DirectionalLight('#f6e2b6', 3.0);
sun.position.set(-4, 7, 3); sun.castShadow = true;
sun.shadow.mapSize.set(1024, 1024);
scene.add(sun);
const rim = new THREE.DirectionalLight('#8dc4e3', 1.6);
rim.position.set(4, 2, -5); scene.add(rim);

// Sea plane (visual only, no measurement claim).
const sea = new THREE.Mesh(
  new THREE.PlaneGeometry(120, 120, 60, 60),
  new THREE.MeshStandardMaterial({color:'#0e3a47', roughness:.85, metalness:.05, transparent:true, opacity:.68})
);
sea.rotation.x = -Math.PI/2; sea.position.y = 0; sea.receiveShadow = true;
scene.add(sea);

// Buoy geometry now lives in the shared model module so the orbit preview and
// other Option A references stay identical.
import {createCanBuoy} from './buoy-can-model.js';

const model = createCanBuoy();
const buoy = model.group;
scene.add(buoy);
const M = model.M;
const {rotor, vane} = model.moving;
const {still, stillCap, gps, gpsRing, ant, antBand, antTip, led, arrayUnit,
       wmast, mastFoot, solarGroup, plate, housing, deck, serviceWindow,
       battery, bufferCard, bilge, rubband, rimRing, keel, eye, fairlead,
       mooring, hull} = model.parts;
// Dimensions the HUD views are framed against.
const {HOUS_CY, ANT_BASE, ANT_H, ANT_X, ANT_Z, WMAST_BASE, WMAST_H, WMAST_X, WMAST_Z} = model.dimensions;
// --- Camera orbit (manual, no extra addon dependency).
// HUD views on this page: orbit / cloud / solar / below.
const views = {
  orbit: {yaw:0.7, pitch:0.18, dist:3.0, focus:[0,0.24,0]},
  wind: {yaw:0.52, pitch:0.12, dist:1.15, focus:[WMAST_X,WMAST_BASE+WMAST_H+0.05,WMAST_Z]},
  cloud: {yaw:0.4, pitch:0.10, dist:1.6, focus:[ANT_X,ANT_BASE+ANT_H-0.1,ANT_Z]},
  solar: {yaw:0.7, pitch:0.12, dist:1.8, focus:[0,HOUS_CY,0.05]},
  mooring: {yaw:3.6, pitch:-0.35, dist:2.3, focus:[0.45,-0.62,0.58]},
  below: {yaw:3.6, pitch:-0.25, dist:2.1, focus:[0.14,-0.10,0]},
};
let yaw = views.orbit.yaw, pitch = views.orbit.pitch, dist = views.orbit.dist;
let focus = new THREE.Vector3(...views.orbit.focus);
let target = {yaw, pitch, dist, focus: focus.clone()};
document.querySelectorAll('#hud button').forEach(b=>{
  b.addEventListener('click', ()=>{ const v = views[b.dataset.view]; if(v) target = {...v, focus: new THREE.Vector3(...v.focus)}; });
});
const DMIN = 1.0, DMAX = 10;
let dragging = false, px = 0, py = 0;
const el = renderer.domElement;
el.addEventListener('pointerdown', e=>{ dragging = true; px = e.clientX; py = e.clientY; el.setPointerCapture(e.pointerId); });
el.addEventListener('pointermove', e=>{
  if(!dragging || touches.size >= 2) return; // 2 fingers = pinch, not orbit
  target.yaw -= (e.clientX - px)*0.006;
  target.pitch = Math.max(-0.9, Math.min(1.1, target.pitch + (e.clientY - py)*0.004));
  px = e.clientX; py = e.clientY;
});
el.addEventListener('pointerup', ()=>{ dragging = false; });
// Touch: two-finger pinch to zoom (wheel has no equivalent on phones/tablets).
const touches = new Map();
let pinchStart = 0, pinchDist0 = 0;
el.addEventListener('pointerdown', e=>{ if(e.pointerType === 'touch') touches.set(e.pointerId, e); });
el.addEventListener('pointermove', e=>{
  if(e.pointerType !== 'touch' || !touches.has(e.pointerId)) return;
  touches.set(e.pointerId, e);
  if(touches.size === 2){
    const [a, b] = [...touches.values()];
    const d = Math.hypot(a.clientX - b.clientX, a.clientY - b.clientY);
    if(pinchDist0 > 0 && d > 0) target.dist = Math.max(DMIN, Math.min(DMAX, pinchDist0 / d * pinchStart));
  }
});
const pinchSync = ()=>{
  if(touches.size === 2){
    const [a, b] = [...touches.values()];
    pinchDist0 = Math.hypot(a.clientX - b.clientX, a.clientY - b.clientY);
    pinchStart = target.dist;
  } else { pinchDist0 = 0; }
};
['pointerup','pointercancel','pointerleave'].forEach(ev=>
  el.addEventListener(ev, e=>{ touches.delete(e.pointerId); dragging = false; pinchSync(); }));
el.addEventListener('wheel', e=>{ e.preventDefault(); target.dist = Math.max(DMIN, Math.min(DMAX, target.dist + e.deltaY*0.003)); }, {passive:false});

function resize(){
  // Explicit pixel size (never CSS %): % heights + grid rows feed back into
  // each other and can blow the stage up to thousands of px in small windows,
  // which collapses the camera frustum into a closeup.
  const w = Math.max(2, stage.clientWidth);
  const h = Math.max(2, Math.min(stage.clientHeight || 560, 720));
  renderer.setSize(w, h);
  camera.aspect = w/h; camera.updateProjectionMatrix();
}
addEventListener('resize', resize); resize();

const clock = new THREE.Clock();
function frame(){
  requestAnimationFrame(frame);
  const t = clock.getElapsedTime();
  yaw += (target.yaw - yaw)*0.08;
  pitch += (target.pitch - pitch)*0.08;
  dist += (target.dist - dist)*0.08;
  focus.lerp(target.focus, 0.08);
  camera.position.set(
    focus.x + Math.cos(pitch)*Math.sin(yaw)*dist,
    focus.y + Math.sin(pitch)*dist,
    focus.z + Math.cos(pitch)*Math.cos(yaw)*dist
  );
  camera.lookAt(focus);
  // Gentle float (motion illustrative only) + slow heartbeat blink (~5s).
  buoy.position.y = Math.sin(t*0.9)*0.025;
  buoy.rotation.z = Math.sin(t*0.6)*0.008;
  const beat = Math.pow(Math.max(0, Math.sin(t*2*Math.PI/5)), 8);
  M.led.emissiveIntensity = 0.25 + beat*2.2;
  rotor.rotation.y += 0.018;
  vane.rotation.y = Math.sin(t*0.36)*0.25;
  // Small wave ripple on sea vertices.
  const p = sea.geometry.attributes.position;
  for(let i=0;i<p.count;i++){
    const x = p.getX(i), y = p.getY(i);
    p.setZ(i, Math.sin(x*0.5 + t)*0.03 + Math.cos(y*0.4 + t*0.8)*0.025);
  }
  p.needsUpdate = true;
  sea.geometry.computeVertexNormals();
  renderer.render(scene, camera);
}
frame();
