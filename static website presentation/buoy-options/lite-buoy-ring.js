// FALCON Lite Option C — ring-buoy (donut) preview (procedural, no CAD edit).
// Foam-filled ring float with open moon pool, single center pole carrying the
// panel, beacon and wind head, heave damping plate below, pressure sensor
// hanging sheltered in the moon pool.
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
  new THREE.MeshStandardMaterial({color:'#0e3a47', roughness:.85, metalness:.05, transparent:true, opacity:.96})
);
sea.rotation.x = -Math.PI/2; sea.position.y = 0; sea.receiveShadow = true;
scene.add(sea);

const M = {
  hull: new THREE.MeshStandardMaterial({color:'#e8821a', roughness:.55, metalness:.08}),
  deck: new THREE.MeshStandardMaterial({color:'#cfd6da', roughness:.6, metalness:.1}),
  frame: new THREE.MeshStandardMaterial({color:'#3a4046', roughness:.5, metalness:.6}),
  dark: new THREE.MeshStandardMaterial({color:'#232a2f', roughness:.6, metalness:.3}),
  solar: new THREE.MeshStandardMaterial({color:'#12283f', roughness:.35, metalness:.55}),
  solarGrid: new THREE.MeshStandardMaterial({color:'#3f6d8f', roughness:.4, metalness:.4}),
  beacon: new THREE.MeshStandardMaterial({color:'#c01616', roughness:.4, metalness:.1, emissive:'#4a0000'}),
  cup: new THREE.MeshStandardMaterial({color:'#262e34', roughness:.55, metalness:.15, side:THREE.DoubleSide}),
  vane: new THREE.MeshStandardMaterial({color:'#20282c', roughness:.55, metalness:.3, side:THREE.DoubleSide}),
  brass: new THREE.MeshStandardMaterial({color:'#d8a94e', roughness:.35, metalness:.7}),
  chain: new THREE.MeshStandardMaterial({color:'#3a3f42', roughness:.6, metalness:.6}),
};
function mesh(geo, mat, x=0, y=0, z=0, name=''){
  const m = new THREE.Mesh(geo, mat);
  m.position.set(x, y, z); m.castShadow = true; m.receiveShadow = true;
  if(name) m.name = name;
  return m;
}
function strut(a, b, r, mat, name=''){
  const va = new THREE.Vector3(...a), vb = new THREE.Vector3(...b);
  const dir = vb.clone().sub(va), len = dir.length();
  const m = new THREE.Mesh(new THREE.CylinderGeometry(r, r, len, 8), mat);
  m.position.copy(va).addScaledVector(dir, 0.5);
  m.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0), dir.normalize());
  m.castShadow = true; m.receiveShadow = true;
  if(name) m.name = name;
  return m;
}

const buoy = new THREE.Group();
scene.add(buoy);

// --- Float: foam-filled ring Ø1.1m overall, open moon pool in the middle.
const ring = mesh(new THREE.TorusGeometry(0.42, 0.13, 20, 56), M.hull, 0, 0, 0, 'RING_FLOAT');
ring.rotation.x = Math.PI/2;
buoy.add(ring);
// Rub strake around the outer equator.
const strake = mesh(new THREE.TorusGeometry(0.55, 0.022, 10, 56), M.frame, 0, 0.02, 0, 'RUB_STRAKE');
strake.rotation.x = Math.PI/2;
buoy.add(strake);
// --- Center pole: underwater stem + tower + wind mast in one piece.
const pole = mesh(new THREE.CylinderGeometry(0.025, 0.035, 1.22, 14), M.frame, 0, 0.46, 0, 'CENTER_POLE');
buoy.add(pole); // spans y -0.15 .. 1.07
// --- Tripod braces: ring inner edge up to the pole (the joint that matters).
for(let i=0;i<3;i++){
  const a = (i/3)*Math.PI*2 + Math.PI/6;
  buoy.add(strut(
    [Math.cos(a)*0.30, 0.05, Math.sin(a)*0.30],
    [Math.cos(a)*0.035, 0.30, Math.sin(a)*0.035],
    0.020, M.frame, 'TOWER_BRACE'));
}
// --- Work deck disc + toe rail around the pole.
const deck = mesh(new THREE.CylinderGeometry(0.16, 0.16, 0.04, 28), M.deck, 0, 0.32, 0, 'WORK_DECK');
buoy.add(deck);
const toeRail = mesh(new THREE.TorusGeometry(0.15, 0.012, 8, 32), M.hull, 0, 0.35, 0, 'TOE_RAIL');
toeRail.rotation.x = Math.PI/2;
buoy.add(toeRail);
// --- Heave damping plate + stem below, mooring eye + chain at the bottom.
const stem = mesh(new THREE.CylinderGeometry(0.03, 0.03, 0.40, 10), M.frame, 0, -0.35, 0, 'DAMPING_STEM');
buoy.add(stem);
const plate = mesh(new THREE.CylinderGeometry(0.25, 0.25, 0.03, 28), M.dark, 0, -0.55, 0, 'HEAVE_PLATE');
buoy.add(plate);
const eye = mesh(new THREE.TorusGeometry(0.045, 0.012, 8, 20), M.chain, 0, -0.60, 0, 'MOORING_EYE');
buoy.add(eye);
const chainStub = mesh(new THREE.CylinderGeometry(0.015, 0.015, 0.26, 10), M.chain, 0, -0.75, 0, 'MOORING_CHAIN_STUB');
buoy.add(chainStub);
// --- Pressure sensor hanging sheltered in the moon pool.
buoy.add(mesh(new THREE.BoxGeometry(0.20, 0.02, 0.02), M.frame, 0.10, 0.09, 0.02, 'SENSOR_BOOM'));
const dropCable = mesh(new THREE.CylinderGeometry(0.008, 0.008, 0.30, 8), M.chain, 0.19, -0.06, 0.02, 'SENSOR_DROP_CABLE');
buoy.add(dropCable);
const psens = mesh(new THREE.CylinderGeometry(0.035, 0.035, 0.14, 14), M.dark, 0.19, -0.28, 0.02, 'WATER_PRESSURE_SENSOR');
buoy.add(psens);
// --- Tower access hatch + GPS puck on the deck edge.
buoy.add(mesh(new THREE.BoxGeometry(0.08, 0.12, 0.02), M.dark, 0, 0.15, 0.062, 'TOWER_HATCH'));
const gps = mesh(new THREE.CylinderGeometry(0.035, 0.038, 0.025, 14), M.dark, 0.10, 0.352, 0.10, 'GNSS_GPS_PUCK');
buoy.add(gps);
// --- Small panel clamped on the pole, tilted 15°.
const panelG = new THREE.Group();
panelG.position.set(0, 0.72, 0.02);
panelG.rotation.x = -0.26;
panelG.name = 'MAST_PANEL';
buoy.add(panelG);
// Panel with a center hole: 4 strips around a 0.12m square opening so the
// mast passes straight through (front/back full-width strips + side strips).
const HOLE = 0.12, PW = 0.44, PD = 0.34, PT = 0.025;
const stripD = (PD - HOLE) / 2, stripW = (PW - HOLE) / 2;
for(const sz of [-(HOLE/2 + stripD/2), HOLE/2 + stripD/2]){
  panelG.add(mesh(new THREE.BoxGeometry(PW, PT, stripD), M.solar, 0, 0, sz, 'SOLAR_PANEL_STRIP'));
}
for(const sx of [-(HOLE/2 + stripW/2), HOLE/2 + stripW/2]){
  panelG.add(mesh(new THREE.BoxGeometry(stripW, PT, HOLE), M.solar, sx, 0, 0, 'SOLAR_PANEL_STRIP'));
}
for(const gx of [-0.15, -0.05, 0.05, 0.15]){
  panelG.add(mesh(new THREE.BoxGeometry(0.012, PT + 0.003, PD), M.solarGrid, gx, 0, 0, 'SOLAR_GRID'));
}
// Mount block under the hole, mast passes through both.
buoy.add(mesh(new THREE.BoxGeometry(0.07, 0.06, 0.07), M.frame, 0, 0.68, 0.02, 'PANEL_CLAMP'));
// --- Red beacon band on the pole above the panel.
const beacon = mesh(new THREE.CylinderGeometry(0.032, 0.032, 0.07, 12), M.beacon, 0, 0.98, 0, 'TOPMARK_BEACON');
buoy.add(beacon);
// --- Compact wind head on the pole top.
const ROTOR_Y = 1.04;
const rotor = new THREE.Group();
rotor.position.set(0, ROTOR_Y, 0);
rotor.name = 'WIND_SPEED_DIRECTION_SENSOR';
buoy.add(rotor);
const hub = mesh(new THREE.SphereGeometry(0.045, 14, 10), M.dark, 0, 0, 0, 'WIND_HUB');
rotor.add(hub);
rotor.add(mesh(new THREE.CylinderGeometry(0.015, 0.015, 0.025, 8), M.brass, 0, 0.05, 0, 'HUB_NUT'));
// 3 open cups on pivots: every mouth faces the same tangential direction
// (convex side forward, like a real drag anemometer).
const cupR = 0.055, armR = 0.255;
for(let i=0;i<3;i++){
  const pivot = new THREE.Group();
  pivot.rotation.y = (i/3)*Math.PI*2;
  rotor.add(pivot);
  const arm = mesh(new THREE.CylinderGeometry(0.011, 0.011, armR, 8), M.frame, armR/2, 0, 0, 'WIND_ARM');
  arm.rotation.z = Math.PI/2;
  pivot.add(arm);
  const cup = mesh(new THREE.SphereGeometry(cupR, 16, 10, 0, Math.PI*2, 0, Math.PI*0.62), M.cup, armR, 0, 0, 'WIND_CUP');
  cup.rotation.x = Math.PI/2;
  pivot.add(cup);
}
// Wind vane on a collar, 120mm below the rotor.
const vane = new THREE.Group();
vane.position.set(0, ROTOR_Y - 0.12, 0);
vane.name = 'WIND_VANE';
buoy.add(vane);
const vaneCollar = mesh(new THREE.TorusGeometry(0.031, 0.010, 8, 16), M.frame, 0, 0, 0, 'VANE_COLLAR');
vaneCollar.rotation.x = Math.PI/2;
vane.add(vaneCollar);
const tail = mesh(new THREE.BoxGeometry(0.012, 0.11, 0.09), M.vane, 0, 0.015, -0.10, 'VANE_TAIL');
vane.add(tail);
const nose = mesh(new THREE.ConeGeometry(0.018, 0.06, 10), M.brass, 0, 0.015, 0.10, 'VANE_NOSE');
nose.rotation.x = Math.PI/2;
vane.add(nose);
// Short whip on the deck edge, clear of the panel.
buoy.add(mesh(new THREE.BoxGeometry(0.05, 0.03, 0.05), M.frame, 0.13, 0.355, -0.08, 'WHIP_FOOT'));
const whip = mesh(new THREE.CylinderGeometry(0.006, 0.009, 0.25, 8), M.dark, 0.13, 0.49, -0.08, 'WHIP_ANTENNA');
buoy.add(whip);
const whipTip = mesh(new THREE.SphereGeometry(0.012, 10, 8), M.brass, 0.13, 0.615, -0.08, 'WHIP_TIP');
buoy.add(whipTip);

// --- Camera orbit (manual, no extra addon dependency).
const views = {
  orbit: {yaw:0.7, pitch:0.12, dist:3.8, focus:[0,0.20,0]},
  wind: {yaw:0.3, pitch:0.08, dist:1.7, focus:[0,ROTOR_Y-0.10,0]},
  solar: {yaw:0.7, pitch:0.12, dist:2.2, focus:[0,0.72,0.05]},
  below: {yaw:3.6, pitch:-0.25, dist:2.6, focus:[0,-0.50,0]},
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
  // Gentle float (motion illustrative only).
  buoy.position.y = Math.sin(t*0.9)*0.025;
  buoy.rotation.x = Math.sin(t*0.7)*0.006;
  buoy.rotation.z = Math.sin(t*0.6)*0.006;
  rotor.rotation.y += 0.03;
  vane.rotation.y = Math.sin(t*0.4)*0.35;
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
