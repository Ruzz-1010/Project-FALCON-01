// FALCON Lite Option B — spar/can buoy preview (procedural, no CAD edit).
// Squat proportions, instrument cabinet with the panel as its roof, slim
// wind mast behind the cabinet.
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
  pvc: new THREE.MeshStandardMaterial({color:'#e8edee', roughness:.55, metalness:.05}),
  cabinet: new THREE.MeshStandardMaterial({color:'#dfe5e8', roughness:.5, metalness:.1}),
  collar: new THREE.MeshStandardMaterial({color:'#e8821a', roughness:.6, metalness:.08}),
  frame: new THREE.MeshStandardMaterial({color:'#5b6b72', roughness:.5, metalness:.6}),
  dark: new THREE.MeshStandardMaterial({color:'#161d20', roughness:.6, metalness:.3}),
  solar: new THREE.MeshStandardMaterial({color:'#12283f', roughness:.35, metalness:.55}),
  solarGrid: new THREE.MeshStandardMaterial({color:'#3f6d8f', roughness:.4, metalness:.4}),
  beacon: new THREE.MeshStandardMaterial({color:'#c01616', roughness:.4, metalness:.1, emissive:'#4a0000'}),
  cup: new THREE.MeshStandardMaterial({color:'#101415', roughness:.5, metalness:.35, side:THREE.DoubleSide}),
  vane: new THREE.MeshStandardMaterial({color:'#20282c', roughness:.55, metalness:.3, side:THREE.DoubleSide}),
  brass: new THREE.MeshStandardMaterial({color:'#d8a94e', roughness:.35, metalness:.7}),
  chain: new THREE.MeshStandardMaterial({color:'#3a3f42', roughness:.6, metalness:.6}),
  daymark: new THREE.MeshStandardMaterial({color:'#e8821a', roughness:.55, metalness:.08}),
};
function mesh(geo, mat, x=0, y=0, z=0, name=''){
  const m = new THREE.Mesh(geo, mat);
  m.position.set(x, y, z); m.castShadow = true; m.receiveShadow = true;
  if(name) m.name = name;
  return m;
}

const buoy = new THREE.Group();
scene.add(buoy);

// --- Hull: PVC tube Ø250mm x 2.0m, waterline at y=0 (1.0m freeboard).
const tube = mesh(new THREE.CylinderGeometry(0.125, 0.125, 2.0, 28), M.pvc, 0, 0.0, 0, 'PVC_SPAR_TUBE');
buoy.add(tube);
// Orange daymark band + collar float Ø0.9m at the waterline.
const daymark = mesh(new THREE.CylinderGeometry(0.13, 0.13, 0.26, 28, 1, true), M.daymark, 0, 0.45, 0, 'DAYMARK_BAND');
buoy.add(daymark);
const collar = mesh(new THREE.CylinderGeometry(0.45, 0.45, 0.22, 36), M.collar, 0, 0.02, 0, 'COLLAR_FLOAT');
buoy.add(collar);
// Ballast disc at the keel for self-righting + mooring eye + chain stub.
const ballast = mesh(new THREE.CylinderGeometry(0.13, 0.15, 0.12, 20), M.dark, 0, -0.92, 0, 'BALLAST');
buoy.add(ballast);
const eye = mesh(new THREE.TorusGeometry(0.05, 0.013, 8, 20), M.chain, 0, -1.03, 0, 'MOORING_EYE');
buoy.add(eye);
const chainStub = mesh(new THREE.CylinderGeometry(0.015, 0.015, 0.30, 10), M.chain, 0, -1.21, 0, 'MOORING_CHAIN_STUB');
buoy.add(chainStub);
// Pressure sensor can strapped low on the tube (below waterline).
const psens = mesh(new THREE.CylinderGeometry(0.035, 0.035, 0.12, 16), M.dark, 0.0, -0.50, 0.14, 'WATER_PRESSURE_SENSOR_ASSEMBLY');
psens.rotation.x = Math.PI/2.4;
buoy.add(psens);

// --- Topside: cap + compact instrument cabinet (GPS/LoRa/ESP32 live
// inside it) + single 40W-class panel as the cabinet roof.
const CAP_Y = 1.00;
const cap = mesh(new THREE.CylinderGeometry(0.15, 0.15, 0.05, 24), M.frame, 0, CAP_Y, 0, 'TOP_CAP');
buoy.add(cap);
const CAB_H = 0.26, CAB_TOP = CAP_Y + 0.03 + CAB_H;
const cabinet = mesh(new THREE.BoxGeometry(0.46, CAB_H, 0.40), M.cabinet, 0, CAP_Y + 0.03 + CAB_H/2, 0, 'INSTRUMENT_CABINET');
buoy.add(cabinet);
const cabTrim = mesh(new THREE.BoxGeometry(0.48, 0.03, 0.42), M.frame, 0, CAP_Y + 0.03, 0, 'CABINET_BASE_TRIM');
buoy.add(cabTrim);
const roof = new THREE.Group();
roof.position.set(0, CAB_TOP + 0.075, -0.08);
roof.rotation.x = -0.21; // ~12° tilt, face up-south
roof.name = 'SINGLE_40W_ROOF';
buoy.add(roof);
const panelSlab = mesh(new THREE.BoxGeometry(0.56, 0.025, 0.44), M.solar, 0, 0, 0, 'SOLAR_PANEL');
roof.add(panelSlab);
for(let i=-1;i<=1;i++){
  roof.add(mesh(new THREE.BoxGeometry(0.012, 0.028, 0.44), M.solarGrid, i*0.165, 0, 0, 'SOLAR_GRID'));
}
for(const sx of [-0.20, 0.20]){
  buoy.add(mesh(new THREE.BoxGeometry(0.04, 0.06, 0.36), M.frame, sx, CAB_TOP + 0.03, -0.06, 'ROOF_RAIL'));
}
// Red topmark light on a finial stub at the panel front edge (clamped look).
const beaconStub = mesh(new THREE.CylinderGeometry(0.015, 0.015, 0.10, 10), M.frame, 0, CAB_TOP + 0.06, 0.145, 'BEACON_STUB');
buoy.add(beaconStub);
const beacon = mesh(new THREE.CylinderGeometry(0.04, 0.04, 0.09, 14), M.beacon, 0, CAB_TOP + 0.145, 0.145, 'TOPMARK_BEACON');
buoy.add(beacon);
const beaconDome = mesh(new THREE.SphereGeometry(0.04, 14, 10, 0, Math.PI*2, 0, Math.PI/2), M.beacon, 0, CAB_TOP + 0.19, 0.145, 'BEACON_DOME');
buoy.add(beaconDome);
const loraSma = mesh(new THREE.CylinderGeometry(0.008, 0.008, 0.05, 10), M.brass, 0.12, CAP_Y + 0.16, -0.205, 'LORA_SMA');
loraSma.rotation.x = Math.PI/2;
buoy.add(loraSma);

// --- Wind head on a slim mast behind the cabinet (Ø36mm pole straight
// into the hub: standard anemometer mount, no fat tube in the rotor plane).
const WMAST_Z = -0.34, ROTOR_Y = CAB_TOP + 0.60;
buoy.add(mesh(new THREE.BoxGeometry(0.05, 0.05, 0.26), M.frame, 0, CAB_TOP + 0.05, -0.26, 'MAST_BRACKET'));
const wmast = mesh(new THREE.CylinderGeometry(0.018, 0.018, 0.65, 12), M.frame, 0, CAB_TOP + 0.275, WMAST_Z, 'WIND_MAST');
buoy.add(wmast);
const rotor = new THREE.Group();
rotor.position.set(0, ROTOR_Y, WMAST_Z);
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
vane.position.set(0, ROTOR_Y - 0.15, WMAST_Z);
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

// --- Camera orbit (manual, no extra addon dependency).
const views = {
  orbit: {yaw:0.7, pitch:0.10, dist:5.4, focus:[0,0.35,0]},
  wind: {yaw:0.3, pitch:0.08, dist:1.9, focus:[0,ROTOR_Y-0.12,WMAST_Z]},
  solar: {yaw:0.7, pitch:0.12, dist:2.6, focus:[0,CAB_TOP+0.10,0]},
  below: {yaw:3.6, pitch:-0.28, dist:3.0, focus:[0,-0.50,0]},
};
let yaw = views.orbit.yaw, pitch = views.orbit.pitch, dist = views.orbit.dist;
let focus = new THREE.Vector3(...views.orbit.focus);
let target = {yaw, pitch, dist, focus: focus.clone()};
document.querySelectorAll('#hud button').forEach(b=>{
  b.addEventListener('click', ()=>{ const v = views[b.dataset.view]; target = {...v, focus: new THREE.Vector3(...v.focus)}; });
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
  buoy.position.y = Math.sin(t*0.9)*0.03;
  buoy.rotation.z = Math.sin(t*0.6)*0.008;
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
