// FALCON Lite Option B — twin-float catamaran preview (procedural, no CAD edit).
// Two pontoon hulls + deck platform + electronics cabinet with the panel as
// its roof. Pressure sensor hangs protected between the hulls; mooring on a
// bow bridle eye. No LoRa gateway in this reduced baseline.
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
  cabinet: new THREE.MeshStandardMaterial({color:'#e8edee', roughness:.5, metalness:.08}),
  frame: new THREE.MeshStandardMaterial({color:'#3a4046', roughness:.5, metalness:.6}),
  dark: new THREE.MeshStandardMaterial({color:'#232a2f', roughness:.6, metalness:.3}),
  solar: new THREE.MeshStandardMaterial({color:'#12283f', roughness:.35, metalness:.55}),
  solarGrid: new THREE.MeshStandardMaterial({color:'#3f6d8f', roughness:.4, metalness:.4}),
  beacon: new THREE.MeshStandardMaterial({color:'#c01616', roughness:.4, metalness:.1, emissive:'#4a0000'}),
  cup: new THREE.MeshStandardMaterial({color:'#101415', roughness:.5, metalness:.35, side:THREE.DoubleSide}),
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

const buoy = new THREE.Group();
scene.add(buoy);

// --- Twin pontoon hulls: capsules Ø0.22m x 1.5m along Z, beam ±0.42m.
for(const sx of [-0.42, 0.42]){
  const hull = mesh(new THREE.CapsuleGeometry(0.11, 1.28, 6, 16), M.hull, sx, -0.02, 0, 'PONTOON_HULL');
  hull.rotation.x = Math.PI/2;
  buoy.add(hull);
  // Deck beams tying each hull to the platform.
  for(const sz of [-0.35, 0.35]){
    buoy.add(mesh(new THREE.BoxGeometry(0.30, 0.05, 0.08), M.frame, sx*0.72, 0.22, sz, 'DECK_BEAM'));
  }
}
// --- Deck platform + non-slip edge trim.
const deck = mesh(new THREE.BoxGeometry(1.10, 0.06, 1.00), M.deck, 0, 0.28, 0, 'DECK_PLATFORM');
buoy.add(deck);

// --- Electronics cabinet amidships (GPS/LoRa/ESP32 live inside it).
const CAB_H = 0.24, CAB_Y = 0.31, CAB_TOP = CAB_Y + CAB_H/2;
const cabinet = mesh(new THREE.BoxGeometry(0.44, CAB_H, 0.36), M.cabinet, 0, CAB_Y, 0, 'INSTRUMENT_CABINET');
buoy.add(cabinet);
const cabTrim = mesh(new THREE.BoxGeometry(0.46, 0.03, 0.38), M.frame, 0, CAB_Y - CAB_H/2 + 0.015, 0, 'CABINET_BASE_TRIM');
buoy.add(cabTrim);
// --- Single 40W-class panel as the cabinet roof, tilted 10°.
const roof = new THREE.Group();
roof.position.set(0, CAB_TOP + 0.07, -0.03);
roof.rotation.x = -0.18;
roof.name = 'SINGLE_40W_ROOF';
buoy.add(roof);
const panelSlab = mesh(new THREE.BoxGeometry(0.62, 0.025, 0.48), M.solar, 0, 0, 0, 'SOLAR_PANEL');
roof.add(panelSlab);
for(let i=-1;i<=1;i++){
  roof.add(mesh(new THREE.BoxGeometry(0.012, 0.028, 0.48), M.solarGrid, i*0.185, 0, 0, 'SOLAR_GRID'));
}
for(const sx of [-0.18, 0.18]){
  buoy.add(mesh(new THREE.BoxGeometry(0.04, 0.07, 0.36), M.frame, sx, CAB_TOP + 0.035, -0.02, 'ROOF_RAIL'));
}
// --- Red topmark light on a finial stub at the panel front edge.
const beaconStub = mesh(new THREE.CylinderGeometry(0.014, 0.014, 0.09, 10), M.frame, 0, CAB_TOP + 0.06, 0.20, 'BEACON_STUB');
buoy.add(beaconStub);
const beacon = mesh(new THREE.CylinderGeometry(0.038, 0.038, 0.085, 14), M.beacon, 0, CAB_TOP + 0.14, 0.20, 'TOPMARK_BEACON');
buoy.add(beacon);
const beaconDome = mesh(new THREE.SphereGeometry(0.038, 14, 10, 0, Math.PI*2, 0, Math.PI/2), M.beacon, 0, CAB_TOP + 0.182, 0.20, 'BEACON_DOME');
buoy.add(beaconDome);

// --- Wind mast at the deck rear (slim Ø36mm pole straight into the hub).
const WMAST_X = 0, WMAST_Z = -0.44, DECK_TOP = 0.31, ROTOR_Y = DECK_TOP + 1.10;
const wmast = mesh(new THREE.CylinderGeometry(0.018, 0.018, 1.10, 12), M.frame, WMAST_X, DECK_TOP + 0.55, WMAST_Z, 'WIND_MAST');
buoy.add(wmast);
const mastFoot = mesh(new THREE.CylinderGeometry(0.035, 0.045, 0.06, 12), M.frame, WMAST_X, DECK_TOP + 0.03, WMAST_Z, 'MAST_FOOT');
buoy.add(mastFoot);
const rotor = new THREE.Group();
rotor.position.set(WMAST_X, ROTOR_Y, WMAST_Z);
rotor.name = 'WIND_SPEED_DIRECTION_SENSOR';
buoy.add(rotor);
const hub = mesh(new THREE.SphereGeometry(0.055, 16, 12), M.dark, 0, 0, 0, 'WIND_HUB');
rotor.add(hub);
// 3 open cups: Ø130mm, Ø600mm spacing circle, mouths facing tangentially.
const cupR = 0.065, armR = 0.30;
for(let i=0;i<3;i++){
  const a = (i/3)*Math.PI*2;
  const arm = mesh(new THREE.CylinderGeometry(0.014, 0.014, armR, 8), M.frame, Math.cos(a)*armR/2, 0, Math.sin(a)*armR/2, 'WIND_ARM');
  arm.rotation.z = Math.PI/2; arm.rotation.y = -a;
  rotor.add(arm);
  const cup = mesh(new THREE.SphereGeometry(cupR, 18, 12, 0, Math.PI*2, 0, Math.PI*0.55), M.cup, Math.cos(a)*armR, 0, Math.sin(a)*armR, 'WIND_CUP');
  cup.rotation.y = -a + Math.PI/2;
  cup.rotation.x = Math.PI/2;
  rotor.add(cup);
}
// Wind vane on its own turret, 150mm below the rotor.
const vane = new THREE.Group();
vane.position.set(WMAST_X, ROTOR_Y - 0.15, WMAST_Z);
vane.name = 'WIND_VANE';
buoy.add(vane);
const vaneMast = mesh(new THREE.CylinderGeometry(0.012, 0.012, 0.12, 8), M.frame, 0, 0, 0, 'VANE_TURRET');
vane.add(vaneMast);
const tail = mesh(new THREE.BoxGeometry(0.02, 0.18, 0.14), M.vane, 0, 0.02, -0.14, 'VANE_TAIL');
vane.add(tail);
const nose = mesh(new THREE.ConeGeometry(0.025, 0.09, 12), M.brass, 0, 0.02, 0.14, 'VANE_NOSE');
nose.rotation.x = Math.PI/2;
vane.add(nose);
// Whip on the wind mast, kept below the rotor plane.
buoy.add(mesh(new THREE.BoxGeometry(0.10, 0.03, 0.03), M.frame, -0.05, ROTOR_Y - 0.42, WMAST_Z, 'WHIP_BRACKET'));
const whip = mesh(new THREE.CylinderGeometry(0.006, 0.009, 0.30, 8), M.dark, -0.09, ROTOR_Y - 0.27, WMAST_Z, 'WHIP_ANTENNA');
buoy.add(whip);
const whipTip = mesh(new THREE.SphereGeometry(0.012, 10, 8), M.brass, -0.09, ROTOR_Y - 0.12, WMAST_Z, 'WHIP_TIP');
buoy.add(whipTip);

// --- Pressure sensor hung between the hulls (protected + easy service).
const dropCable = mesh(new THREE.CylinderGeometry(0.008, 0.008, 0.35, 8), M.chain, 0, 0.10, 0.10, 'SENSOR_DROP_CABLE');
buoy.add(dropCable);
const psens = mesh(new THREE.CylinderGeometry(0.035, 0.035, 0.14, 14), M.dark, 0, -0.14, 0.10, 'WATER_PRESSURE_SENSOR');
buoy.add(psens);
// --- Bow mooring eye + chain stub (bridle point for a single anchor line).
buoy.add(mesh(new THREE.BoxGeometry(0.06, 0.05, 0.20), M.frame, 0, 0.12, 0.50, 'BOW_SPRIT'));
const bowEye = mesh(new THREE.TorusGeometry(0.05, 0.013, 8, 20), M.chain, 0, 0.12, 0.60, 'BOW_MOORING_EYE');
buoy.add(bowEye);
const chainStub = mesh(new THREE.CylinderGeometry(0.015, 0.015, 0.30, 10), M.chain, 0, -0.05, 0.62, 'MOORING_CHAIN_STUB');
chainStub.rotation.x = 0.5;
buoy.add(chainStub);

// --- Camera orbit (manual, no extra addon dependency).
const views = {
  orbit: {yaw:0.7, pitch:0.12, dist:4.4, focus:[0,0.45,0]},
  wind: {yaw:0.3, pitch:0.08, dist:1.9, focus:[WMAST_X,ROTOR_Y-0.12,WMAST_Z]},
  solar: {yaw:0.7, pitch:0.12, dist:2.4, focus:[0,CAB_TOP+0.10,0]},
  below: {yaw:3.6, pitch:-0.25, dist:2.8, focus:[0,-0.20,0.15]},
};
let yaw = views.orbit.yaw, pitch = views.orbit.pitch, dist = views.orbit.dist;
let focus = new THREE.Vector3(...views.orbit.focus);
let target = {yaw, pitch, dist, focus: focus.clone()};
document.querySelectorAll('#hud button').forEach(b=>{
  b.addEventListener('click', ()=>{ const v = views[b.dataset.view]; if(v) target = {...v, focus: new THREE.Vector3(...v.focus)}; });
});
let dragging = false, px = 0, py = 0;
const el = renderer.domElement;
el.addEventListener('pointerdown', e=>{ dragging = true; px = e.clientX; py = e.clientY; el.setPointerCapture(e.pointerId); });
el.addEventListener('pointermove', e=>{
  if(!dragging) return;
  target.yaw -= (e.clientX - px)*0.006;
  target.pitch = Math.max(-0.9, Math.min(1.1, target.pitch + (e.clientY - py)*0.004));
  px = e.clientX; py = e.clientY;
});
el.addEventListener('pointerup', ()=>{ dragging = false; });
el.addEventListener('wheel', e=>{ e.preventDefault(); target.dist = Math.max(1.2, Math.min(12, target.dist + e.deltaY*0.003)); }, {passive:false});

function resize(){
  const w = stage.clientWidth, h = stage.clientHeight;
  renderer.setSize(w, h, false);
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
  // Gentle float + rotor spin (motion illustrative only).
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
