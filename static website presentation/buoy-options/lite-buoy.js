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
  new THREE.MeshStandardMaterial({color:'#0e3a47', roughness:.85, metalness:.05, transparent:true, opacity:.96})
);
sea.rotation.x = -Math.PI/2; sea.position.y = 0; sea.receiveShadow = true;
scene.add(sea);

const M = {
  hull: new THREE.MeshStandardMaterial({color:'#e8821a', roughness:.55, metalness:.08}),
  deck: new THREE.MeshStandardMaterial({color:'#d9760f', roughness:.6, metalness:.08}),
  steel: new THREE.MeshStandardMaterial({color:'#6b7178', roughness:.45, metalness:.6}),
  frame: new THREE.MeshStandardMaterial({color:'#3a4046', roughness:.5, metalness:.6}),
  dark: new THREE.MeshStandardMaterial({color:'#232a2f', roughness:.6, metalness:.3}),
  solar: new THREE.MeshStandardMaterial({color:'#101f31', roughness:.32, metalness:.5}),
  solarFrame: new THREE.MeshStandardMaterial({color:'#9aa4ab', roughness:.4, metalness:.6}),
  brass: new THREE.MeshStandardMaterial({color:'#d8a94e', roughness:.35, metalness:.7}),
  chain: new THREE.MeshStandardMaterial({color:'#3a3f42', roughness:.6, metalness:.6}),
  tipRed: new THREE.MeshStandardMaterial({color:'#c01616', roughness:.4, metalness:.1, emissive:'#4a0000'}),
  led: new THREE.MeshStandardMaterial({color:'#3a2f10', roughness:.4, metalness:.2, emissive:'#d8a94e', emissiveIntensity:.4}),
  cup: new THREE.MeshStandardMaterial({color:'#262e34', roughness:.55, metalness:.15, side:THREE.DoubleSide}),
  vane: new THREE.MeshStandardMaterial({color:'#20282c', roughness:.55, metalness:.3, side:THREE.DoubleSide}),
  gpsBlue: new THREE.MeshStandardMaterial({color:'#244d75', roughness:.35, metalness:.25}),
  battery: new THREE.MeshStandardMaterial({color:'#1f3d2b', roughness:.55, metalness:.15}),
};
function mesh(geo, mat, x=0, y=0, z=0, name=''){
  const m = new THREE.Mesh(geo, mat);
  m.position.set(x, y, z); m.castShadow = true; m.receiveShadow = true;
  if(name) m.name = name;
  return m;
}

const buoy = new THREE.Group();
scene.add(buoy);

// --- Hull: squat compact can Ø0.84m x 0.42m, waterline at y=0.
const hull = mesh(new THREE.CylinderGeometry(0.42, 0.42, 0.42, 48), M.hull, 0, 0.08, 0, 'CAN_HULL');
buoy.add(hull);
const bottom = mesh(new THREE.CylinderGeometry(0.42, 0.34, 0.08, 48), M.hull, 0, -0.17, 0, 'HULL_BOTTOM');
buoy.add(bottom);
const bilge = mesh(new THREE.TorusGeometry(0.37, 0.024, 10, 48), M.steel, 0, -0.20, 0, 'BILGE_RING');
bilge.rotation.x = Math.PI/2;
buoy.add(bilge);
const rubband = mesh(new THREE.CylinderGeometry(0.425, 0.425, 0.045, 48, 1, true), M.steel, 0, 0.02, 0, 'RUB_BAND');
buoy.add(rubband);
// Deck disc + rim ring + bolts.
const deck = mesh(new THREE.CylinderGeometry(0.415, 0.415, 0.04, 48), M.deck, 0, 0.31, 0, 'DECK');
buoy.add(deck);
const rimRing = mesh(new THREE.TorusGeometry(0.395, 0.014, 10, 48), M.steel, 0, 0.332, 0, 'DECK_RIM');
rimRing.rotation.x = Math.PI/2;
buoy.add(rimRing);
for(let i=0;i<12;i++){
  const a = (i/12)*Math.PI*2;
  buoy.add(mesh(new THREE.CylinderGeometry(0.012, 0.012, 0.02, 8), M.steel, Math.cos(a)*0.36, 0.334, Math.sin(a)*0.36, 'DECK_BOLT'));
}
// Mooring eye + chain stub below the hull.
const eye = mesh(new THREE.TorusGeometry(0.045, 0.012, 8, 20), M.chain, 0, -0.27, 0, 'MOORING_EYE');
buoy.add(eye);
const chainStub = mesh(new THREE.CylinderGeometry(0.015, 0.015, 0.22, 10), M.chain, 0, -0.40, 0, 'MOORING_CHAIN_STUB');
buoy.add(chainStub);

// --- Pressure stilling tube on the hull side (open top above waterline).
const still = mesh(new THREE.CylinderGeometry(0.026, 0.026, 0.42, 14, 1, true), M.steel, 0.45, -0.04, 0.12, 'PRESSURE_STILLING_TUBE');
buoy.add(still);
const stillCap = mesh(new THREE.CylinderGeometry(0.029, 0.029, 0.03, 14), M.dark, 0.45, -0.26, 0.12, 'STILLING_BOTTOM_CAP');
buoy.add(stillCap);
for(const sy of [0.08, -0.12]){
  buoy.add(mesh(new THREE.BoxGeometry(0.07, 0.026, 0.03), M.frame, 0.41, sy, 0.12, 'STILLING_STRAP'));
}

// --- Tapered top housing (4-sided frustum): lower and wider like the reference.
const HOUS_Y = 0.33, HOUS_H = 0.28, HOUS_CY = HOUS_Y + HOUS_H/2;
const housing = mesh(new THREE.CylinderGeometry(0.18, 0.34, HOUS_H, 4, 1), M.hull, 0, HOUS_CY, 0, 'TAPERED_HOUSING');
housing.rotation.y = Math.PI/4; // faces look along +-X / +-Z
buoy.add(housing);
// Small solar panel on each sloped face.
const tilt = Math.atan((0.240-0.127)/HOUS_H); // face slope from vertical
const solarGroup = new THREE.Group();
solarGroup.name = 'HOUSING_SOLAR_FACES';
buoy.add(solarGroup);
for(let k=0;k<4;k++){
  const face = new THREE.Group();
  face.rotation.y = k*Math.PI/2;
  const frame = mesh(new THREE.BoxGeometry(0.22, 0.23, 0.008), M.solarFrame, 0, HOUS_CY, 0.206, 'HOUSING_PANEL_FRAME');
  const panel = mesh(new THREE.BoxGeometry(0.20, 0.21, 0.014), M.solar, 0, HOUS_CY, 0.212, 'HOUSING_SOLAR_PANEL');
  frame.rotation.x = -tilt; panel.rotation.x = -tilt;
  face.add(frame, panel);
  solarGroup.add(face);
}
// Top cap plate + dark GPS puck + LTE/Wi-Fi antenna + heartbeat LED.
const TOP_Y = HOUS_Y + HOUS_H;
const plate = mesh(new THREE.BoxGeometry(0.25, 0.025, 0.25), M.deck, 0, TOP_Y + 0.012, 0, 'TOP_PLATE');
buoy.add(plate);
const gps = mesh(new THREE.CylinderGeometry(0.048, 0.052, 0.032, 20), M.gpsBlue, -0.085, TOP_Y + 0.040, 0.065, 'REQUIRED_GPS_POSITION_SECURITY_PUCK');
buoy.add(gps);
const gpsRing = mesh(new THREE.TorusGeometry(0.054, 0.005, 8, 20), M.brass, -0.085, TOP_Y + 0.059, 0.065, 'GPS_LABEL_RING');
gpsRing.rotation.x = Math.PI/2;
buoy.add(gpsRing);
const ANT_X = 0.07, ANT_Z = -0.04, ANT_BASE = TOP_Y + 0.025, ANT_H = 0.30;
const ant = mesh(new THREE.CylinderGeometry(0.007, 0.010, ANT_H, 8), M.dark, ANT_X, ANT_BASE + ANT_H/2, ANT_Z, 'LTE_WIFI_ANTENNA');
buoy.add(ant);
const antBand = mesh(new THREE.CylinderGeometry(0.011, 0.011, 0.05, 8), M.tipRed, ANT_X, ANT_BASE + ANT_H - 0.03, ANT_Z, 'ANTENNA_TIP_BAND');
buoy.add(antBand);
const antTip = mesh(new THREE.SphereGeometry(0.011, 10, 8), M.brass, ANT_X, ANT_BASE + ANT_H + 0.005, ANT_Z, 'ANTENNA_TIP');
buoy.add(antTip);
const led = mesh(new THREE.SphereGeometry(0.016, 10, 8), M.led, 0, HOUS_CY + 0.04, 0.192, 'HEARTBEAT_LED');
buoy.add(led);

// --- Required compact wind speed + direction sensor on a short mast.
const WMAST_X = 0.14, WMAST_Z = 0.14, WMAST_BASE = TOP_Y + 0.018, WMAST_H = 0.42;
const wmast = mesh(new THREE.CylinderGeometry(0.010, 0.012, WMAST_H, 10), M.frame, WMAST_X, WMAST_BASE + WMAST_H/2, WMAST_Z, 'REQUIRED_WIND_MAST');
buoy.add(wmast);
const mastFoot = mesh(new THREE.CylinderGeometry(0.026, 0.033, 0.035, 12), M.frame, WMAST_X, WMAST_BASE + 0.018, WMAST_Z, 'WIND_MAST_FOOT');
buoy.add(mastFoot);
const rotor = new THREE.Group();
rotor.position.set(WMAST_X, WMAST_BASE + WMAST_H + 0.025, WMAST_Z);
rotor.name = 'REQUIRED_WIND_SPEED_CUPS';
buoy.add(rotor);
rotor.add(mesh(new THREE.SphereGeometry(0.028, 12, 8), M.dark, 0, 0, 0, 'WIND_HUB'));
const cupR = 0.026, armR = 0.115;
for(let i=0;i<3;i++){
  const pivot = new THREE.Group();
  pivot.rotation.y = (i/3)*Math.PI*2;
  rotor.add(pivot);
  const arm = mesh(new THREE.CylinderGeometry(0.006, 0.006, armR, 8), M.frame, armR/2, 0, 0, 'WIND_ARM');
  arm.rotation.z = Math.PI/2;
  pivot.add(arm);
  const cup = mesh(new THREE.SphereGeometry(cupR, 14, 10, 0, Math.PI*2, 0, Math.PI*0.62), M.cup, armR, 0, 0, 'WIND_CUP');
  cup.rotation.x = Math.PI/2;
  pivot.add(cup);
}
const vane = new THREE.Group();
vane.position.set(WMAST_X, WMAST_BASE + WMAST_H - 0.075, WMAST_Z);
vane.name = 'REQUIRED_WIND_DIRECTION_VANE';
buoy.add(vane);
const vaneTail = mesh(new THREE.BoxGeometry(0.010, 0.065, 0.058), M.vane, 0, 0.012, -0.055, 'VANE_TAIL');
vane.add(vaneTail);
const vaneNose = mesh(new THREE.ConeGeometry(0.014, 0.050, 10), M.brass, 0, 0.012, 0.055, 'VANE_NOSE');
vaneNose.rotation.x = Math.PI/2;
vane.add(vaneNose);

// Visual cutaway hints for internal battery/power bay and offline buffer.
const battery = mesh(new THREE.BoxGeometry(0.18, 0.055, 0.11), M.battery, -0.12, 0.36, -0.12, 'INTERNAL_BATTERY_SOLAR_POWER_BAY');
buoy.add(battery);
const bufferCard = mesh(new THREE.BoxGeometry(0.065, 0.012, 0.050), M.dark, 0.12, 0.35, -0.14, 'MICROSD_OR_FLASH_BUFFER');
buoy.add(bufferCard);

// --- Camera orbit (manual, no extra addon dependency).
// HUD views on this page: orbit / cloud / solar / below.
const views = {
  orbit: {yaw:0.7, pitch:0.18, dist:3.0, focus:[0,0.24,0]},
  wind: {yaw:0.52, pitch:0.12, dist:1.45, focus:[WMAST_X,WMAST_BASE+WMAST_H,WMAST_Z]},
  cloud: {yaw:0.4, pitch:0.10, dist:1.6, focus:[ANT_X,ANT_BASE+ANT_H-0.1,ANT_Z]},
  solar: {yaw:0.7, pitch:0.12, dist:1.8, focus:[0,HOUS_CY,0.05]},
  below: {yaw:3.6, pitch:-0.25, dist:2.1, focus:[0.14,-0.10,0]},
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
el.addEventListener('wheel', e=>{ e.preventDefault(); target.dist = Math.max(1.0, Math.min(10, target.dist + e.deltaY*0.003)); }, {passive:false});

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
