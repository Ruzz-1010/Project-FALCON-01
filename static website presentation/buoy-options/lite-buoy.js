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
  arrayBody: new THREE.MeshStandardMaterial({color:'#eef1f2', roughness:.45, metalness:.05}),
  arrayCup: new THREE.MeshStandardMaterial({color:'#0b0d0f', roughness:.3, metalness:.2, side:THREE.DoubleSide}),
  vane: new THREE.MeshStandardMaterial({color:'#20282c', roughness:.55, metalness:.3, side:THREE.DoubleSide}),
  gpsBlue: new THREE.MeshStandardMaterial({color:'#244d75', roughness:.35, metalness:.25}),
  battery: new THREE.MeshStandardMaterial({color:'#1f3d2b', roughness:.55, metalness:.15}),
  rope: new THREE.MeshStandardMaterial({color:'#b58d55', roughness:.8, metalness:.05}),
  anchor: new THREE.MeshStandardMaterial({color:'#272d31', roughness:.7, metalness:.55}),
  glass: new THREE.MeshStandardMaterial({color:'#8fc9dc', roughness:.2, metalness:.05, transparent:true, opacity:.28}),
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
function chainBetween(a, b, count, radius=0.030){
  const g = new THREE.Group();
  g.name = 'VISIBLE_MOORING_CHAIN_LINKS';
  const va = new THREE.Vector3(...a), vb = new THREE.Vector3(...b);
  const dir = vb.clone().sub(va);
  const q = new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0,1,0), dir.clone().normalize());
  for(let i=0;i<count;i++){
    const link = mesh(new THREE.TorusGeometry(radius, 0.006, 8, 18), M.chain, 0, 0, 0, 'CHAIN_LINK');
    link.position.copy(va).addScaledVector(dir, (i+0.5)/count);
    link.quaternion.copy(q);
    link.rotateX(Math.PI/2);
    if(i%2) link.rotateY(Math.PI/2);
    g.add(link);
  }
  return g;
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
const rubband = mesh(new THREE.CylinderGeometry(0.419, 0.419, 0.045, 48, 1, true), M.steel, 0, 0.02, 0, 'RUB_BAND');
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
// Mooring eye, keel ballast, and a visible chain/anchor study below the hull.
const eye = mesh(new THREE.TorusGeometry(0.045, 0.012, 8, 20), M.chain, 0, -0.352, 0, 'MOORING_EYE');
buoy.add(eye);
// Hull bottom face sits at y=-0.21; the ballast plug must start there or it hangs in open water.
const keel = mesh(new THREE.CylinderGeometry(0.19, 0.15, 0.13, 24), M.anchor, 0, -0.275, 0, 'LOW_KEEL_BALLAST');
buoy.add(keel);
const fairlead = mesh(new THREE.TorusGeometry(0.055, 0.010, 8, 20), M.chain, 0.30, -0.16, 0.30, 'SIDE_FAIRLEAD');
fairlead.rotation.y = Math.PI/4;
buoy.add(fairlead);
buoy.add(strut([0.05,-0.30,0.05],[0.30,-0.18,0.30],0.007,M.rope,'SHORT_BRIDLE_TO_FAIRLEAD'));
const mooring = new THREE.Group();
mooring.name = 'MOORING_CHAIN_AND_ANCHOR_STUDY';
mooring.add(chainBetween([0.30,-0.17,0.30],[0.52,-0.72,0.60],9,0.026)); // starts at the fairlead
mooring.add(strut([0.52,-0.72,0.60],[0.66,-0.98,0.82],0.010,M.rope,'SCOPE_ROPE_TO_ANCHOR'));
const anchorBlock = mesh(new THREE.BoxGeometry(0.34,0.10,0.24), M.anchor, 0.72, -1.03, 0.90, 'CONCRETE_OR_DEADWEIGHT_ANCHOR');
anchorBlock.rotation.y = 0.35;
mooring.add(anchorBlock);
// Eye sits in the scope-rope eye and in the anchor block, and its plane is
// turned so the rope actually threads through it instead of clipping its edge.
const anchorEye = mesh(new THREE.TorusGeometry(0.045,0.010,8,18), M.chain, 0.63, -0.95, 0.80, 'ANCHOR_EYE');
anchorEye.rotation.y = -1.0036;
mooring.add(anchorEye);
const anchorStock = mesh(new THREE.BoxGeometry(0.46,0.012,0.012), M.anchor, 0.72, -0.974, 0.90, 'ANCHOR_STOCK');
anchorStock.rotation.y = 0.35;   // must match the block, and rest on its top face
mooring.add(anchorStock);
buoy.add(mooring);

// --- Pressure stilling tube on the hull side (open top above waterline).
// Hull r=0.42: put the tube axis at 0.43 so its wall bites into the shell
// (0.43-0.026 = 0.404) instead of hovering 2cm clear of it.
const still = mesh(new THREE.CylinderGeometry(0.026, 0.026, 0.42, 14, 1, true), M.steel, 0.413, -0.04, 0.12, 'PRESSURE_STILLING_TUBE');
buoy.add(still);
const stillCap = mesh(new THREE.CylinderGeometry(0.029, 0.029, 0.03, 14), M.dark, 0.413, -0.26, 0.12, 'STILLING_BOTTOM_CAP');
buoy.add(stillCap);
for(const sy of [0.08, -0.12]){
  buoy.add(mesh(new THREE.BoxGeometry(0.07, 0.026, 0.03), M.frame, 0.415, sy, 0.12, 'STILLING_STRAP'));
}

// --- Tapered top housing (4-sided frustum): lower and wider like the reference.
const HOUS_Y = 0.33, HOUS_H = 0.28, HOUS_CY = HOUS_Y + HOUS_H/2;
const housing = mesh(new THREE.CylinderGeometry(0.18, 0.34, HOUS_H, 4, 1), M.hull, 0, HOUS_CY, 0, 'TAPERED_HOUSING');
housing.rotation.y = Math.PI/4; // faces look along +-X / +-Z
buoy.add(housing);
// Small solar panel on each sloped face.
// The housing is a 4-sided frustum turned 45 deg, so its flat faces are NOT at
// `radius` -- the face midpoints sit at radius/sqrt(2) along +-X and +-Z. Seating
// the panels on the real face plane is what stops them hovering off the shell.
const FACE_K = Math.SQRT1_2;
const housingR = y => 0.34 + (y - HOUS_Y)/HOUS_H * (0.18 - 0.34);
const faceZ = y => housingR(y) * FACE_K;
const tilt = Math.atan((0.34 - 0.18) * FACE_K / HOUS_H); // face slope from vertical
const faceN = new THREE.Vector3(0, Math.sin(tilt), Math.cos(tilt)); // outward normal of the +Z face
const solarGroup = new THREE.Group();
solarGroup.name = 'HOUSING_SOLAR_FACES';
buoy.add(solarGroup);
for(let k=0;k<4;k++){
  const face = new THREE.Group();
  face.rotation.y = k*Math.PI/2;
  const facePt = new THREE.Vector3(0, HOUS_CY, faceZ(HOUS_CY));
  const frame = mesh(new THREE.BoxGeometry(0.22, 0.23, 0.008), M.solarFrame, 0, 0, 0, 'HOUSING_PANEL_FRAME');
  const panel = mesh(new THREE.BoxGeometry(0.20, 0.21, 0.014), M.solar, 0, 0, 0, 'HOUSING_SOLAR_PANEL');
  // Back of the frame rests on the face (halfDepth 0.004 -> standoff 0.004);
  // the cell sits 0.002 proud of the frame front.
  frame.position.copy(facePt).addScaledVector(faceN, 0.004);
  panel.position.copy(facePt).addScaledVector(faceN, 0.013);
  frame.rotation.x = -tilt; panel.rotation.x = -tilt;
  face.add(frame, panel);
  solarGroup.add(face);
}
// Top cap plate + dark GPS puck + LTE/Wi-Fi antenna + heartbeat LED. Only external fittings are shown; battery/ESP32 stay inside.
const TOP_Y = HOUS_Y + HOUS_H;
const plate = mesh(new THREE.BoxGeometry(0.25, 0.025, 0.25), M.deck, 0, TOP_Y + 0.012, 0, 'TOP_PLATE');
buoy.add(plate);
const gps = mesh(new THREE.CylinderGeometry(0.048, 0.052, 0.032, 20), M.gpsBlue, -0.085, TOP_Y + 0.040, 0.065, 'REQUIRED_GPS_POSITION_SECURITY_PUCK');
buoy.add(gps);
const gpsRing = mesh(new THREE.TorusGeometry(0.054, 0.005, 8, 20), M.brass, -0.085, TOP_Y + 0.059, 0.065, 'GPS_LABEL_RING');
gpsRing.rotation.x = Math.PI/2;
buoy.add(gpsRing);
const ANT_X = 0.095, ANT_Z = -0.055, ANT_BASE = TOP_Y + 0.025, ANT_H = 0.30;
const ant = mesh(new THREE.CylinderGeometry(0.007, 0.010, ANT_H, 8), M.dark, ANT_X, ANT_BASE + ANT_H/2, ANT_Z, 'LTE_WIFI_ANTENNA');
buoy.add(ant);
const antBand = mesh(new THREE.CylinderGeometry(0.011, 0.011, 0.05, 8), M.tipRed, ANT_X, ANT_BASE + ANT_H - 0.03, ANT_Z, 'ANTENNA_TIP_BAND');
buoy.add(antBand);
const antTip = mesh(new THREE.SphereGeometry(0.011, 10, 8), M.brass, ANT_X, ANT_BASE + ANT_H + 0.005, ANT_Z, 'ANTENNA_TIP');
buoy.add(antTip);
const led = mesh(new THREE.SphereGeometry(0.016, 10, 8), M.led, 0, HOUS_CY + 0.04, 0.170, 'HEARTBEAT_LED');
buoy.add(led);

// --- Required compact wind speed + direction sensor on a short mast.
// Cleaner mini anemometer assembly: three cup rotor on top, wind vane below,
// slim mast and clamp. Geometry only; does not change the buoy body design.
const WMAST_X = 0, WMAST_Z = 0, WMAST_BASE = TOP_Y + 0.018, WMAST_H = 0.46;
const wmast = mesh(new THREE.CylinderGeometry(0.008, 0.011, WMAST_H, 14), M.frame, WMAST_X, WMAST_BASE + WMAST_H/2, WMAST_Z, 'REQUIRED_WIND_MAST');
buoy.add(wmast);
const mastFoot = mesh(new THREE.CylinderGeometry(0.030, 0.040, 0.035, 16), M.frame, WMAST_X, WMAST_BASE + 0.018, WMAST_Z, 'WIND_MAST_FOOT');
buoy.add(mastFoot);
const mastCollar = mesh(new THREE.TorusGeometry(0.022, 0.005, 8, 18), M.steel, WMAST_X, WMAST_BASE + WMAST_H - 0.015, WMAST_Z, 'WIND_MAST_TOP_COLLAR');
mastCollar.rotation.x = Math.PI / 2;
buoy.add(mastCollar);

const AY = WMAST_BASE + WMAST_H;
const arrayUnit = new THREE.Group();
arrayUnit.position.set(WMAST_X, AY, WMAST_Z);
arrayUnit.name = 'WIND_ARRAY_UNIT_REFINED';
buoy.add(arrayUnit);

// Compact commercial-style head body.
arrayUnit.add(mesh(new THREE.CylinderGeometry(0.025, 0.030, 0.095, 18), M.arrayBody, 0, 0.030, 0, 'WIND_SENSOR_CENTER_BODY'));
arrayUnit.add(mesh(new THREE.CylinderGeometry(0.034, 0.034, 0.020, 18), M.dark, 0, -0.030, 0, 'WIND_SENSOR_LOWER_CLAMP'));
arrayUnit.add(mesh(new THREE.CylinderGeometry(0.010, 0.010, 0.145, 12), M.frame, 0, 0.118, 0, 'WIND_ROTOR_POST'));

// Three-cup rotor: arms are longer and cups have visible rims, so the part reads
// as an anemometer instead of a generic black blob.
const rotor = new THREE.Group();
rotor.position.set(0, 0.195, 0);
rotor.name = 'REQUIRED_WIND_SPEED_CUPS';
arrayUnit.add(rotor);
rotor.add(mesh(new THREE.SphereGeometry(0.022, 16, 10), M.dark, 0, 0, 0, 'WIND_HUB'));
rotor.add(mesh(new THREE.CylinderGeometry(0.012, 0.012, 0.020, 12), M.brass, 0, 0.023, 0, 'WIND_HUB_CAP'));
const cupR = 0.038, armR = 0.135;
for(let i=0;i<3;i++){
  const pivot = new THREE.Group();
  pivot.rotation.y = (i/3)*Math.PI*2;
  rotor.add(pivot);
  const arm = mesh(new THREE.CylinderGeometry(0.0045, 0.0045, armR, 10), M.frame, armR/2, 0, 0, 'WIND_ARM');
  arm.rotation.z = Math.PI/2;
  pivot.add(arm);
  const cupGroup = new THREE.Group();
  cupGroup.position.set(armR, 0, 0);
  cupGroup.rotation.z = -0.22;
  pivot.add(cupGroup);
  const cup = mesh(new THREE.SphereGeometry(cupR, 20, 12, 0, Math.PI*2, 0, Math.PI*0.62), M.arrayCup, 0, 0, 0, 'WIND_CUP');
  cup.rotation.x = Math.PI/2;
  cup.rotation.y = Math.PI/2;
  cupGroup.add(cup);
  const rim = mesh(new THREE.TorusGeometry(cupR*0.82, 0.0035, 8, 20), M.frame, 0, 0, 0, 'WIND_CUP_RIM');
  rim.rotation.y = Math.PI/2;
  cupGroup.add(rim);
}

// Direction vane: horizontal boom and triangular tail, placed below the rotor.
const vane = new THREE.Group();
vane.position.set(0, 0.060, 0);
vane.name = 'REQUIRED_WIND_DIRECTION_VANE';
arrayUnit.add(vane);
vane.add(strut([0, 0, 0.075], [0, 0, -0.185], 0.006, M.frame, 'WIND_VANE_BOOM'));
const vaneNose = mesh(new THREE.ConeGeometry(0.018, 0.070, 14), M.brass, 0, 0, 0.105, 'VANE_NOSE');
vaneNose.rotation.x = Math.PI/2;
vane.add(vaneNose);
const finShape = new THREE.Shape();
finShape.moveTo(0, 0.060);
finShape.lineTo(0, -0.060);
finShape.lineTo(0.150, 0);
finShape.lineTo(0, 0.060);
const fin = new THREE.Mesh(new THREE.ShapeGeometry(finShape), M.vane);
fin.name = 'VANE_TRIANGULAR_FIN';
fin.position.set(-0.075, 0.000, -0.185);
fin.rotation.y = Math.PI/2;
fin.castShadow = true; fin.receiveShadow = true;
vane.add(fin);
const finRib = mesh(new THREE.BoxGeometry(0.006, 0.095, 0.010), M.frame, 0, 0, -0.185, 'VANE_FIN_RIB');
vane.add(finRib);

// Small shield plates under the head suggest the combined weather-sensor package,
// but they are kept compact so the wind sensor no longer dominates the buoy.
arrayUnit.add(mesh(new THREE.CylinderGeometry(0.007, 0.007, 0.070, 8), M.arrayBody, 0, -0.072, 0.035, 'SHIELD_STEM'));
for(let i=0;i<3;i++){
  const r = i % 2 === 0 ? 0.036 : 0.031;
  arrayUnit.add(mesh(new THREE.CylinderGeometry(r, r, 0.007, 18), M.arrayBody, 0, -0.045 - i*0.014, 0.035, 'COMPACT_RADIATION_SHIELD'));
}

// Sealed service bay hints: transparent window on housing, with battery/buffer tucked inside.
// Lay the pane flat on the -Z face; a flat box on the 45 deg corner edge
// hangs off one side, and a vertical pane on a sloped face lifts at the top.
const WIN_Y = HOUS_CY - 0.01;
const serviceWindow = mesh(new THREE.BoxGeometry(0.16, 0.10, 0.008), M.glass, 0, 0, 0, 'SERVICE_WINDOW_TO_INTERNAL_ELECTRONICS');
serviceWindow.position.set(0, WIN_Y + faceN.y * 0.003, -(faceZ(WIN_Y) + faceN.z * 0.003));
serviceWindow.rotation.x = -tilt;
buoy.add(serviceWindow);
const battery = mesh(new THREE.BoxGeometry(0.13, 0.045, 0.08), M.battery, -0.045, HOUS_CY - 0.035, -0.055, 'INTERNAL_BATTERY_SOLAR_POWER_BAY');
buoy.add(battery);
const bufferCard = mesh(new THREE.BoxGeometry(0.050, 0.010, 0.036), M.dark, 0.045, HOUS_CY - 0.025, -0.060, 'MICROSD_OR_FLASH_BUFFER_INSIDE_HOUSING');
buoy.add(bufferCard);
for(const [gx,gz] of [[-0.28,-0.28],[-0.22,-0.30]]){
  buoy.add(mesh(new THREE.CylinderGeometry(0.010,0.010,0.022,10), M.frame, gx, 0.338, gz, 'SEALED_CABLE_GLAND'));
}

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
