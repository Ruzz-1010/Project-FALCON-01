// FALCON Lite Option B — twin-float catamaran preview (procedural, no CAD edit).
// Two pontoon hulls + deck platform + electronics cabinet with the panel as
// its roof. Pressure sensor hangs protected between the hulls; mooring on a
// bow bridle eye, with GPS and Wi-Fi/LTE placement shown. No LoRa gateway in this reduced baseline.
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
  deck: new THREE.MeshStandardMaterial({color:'#cfd6da', roughness:.6, metalness:.1}),
  cabinet: new THREE.MeshStandardMaterial({color:'#e8edee', roughness:.5, metalness:.08}),
  frame: new THREE.MeshStandardMaterial({color:'#3a4046', roughness:.5, metalness:.6}),
  dark: new THREE.MeshStandardMaterial({color:'#232a2f', roughness:.6, metalness:.3}),
  solar: new THREE.MeshStandardMaterial({color:'#12283f', roughness:.35, metalness:.55}),
  solarGrid: new THREE.MeshStandardMaterial({color:'#3f6d8f', roughness:.4, metalness:.4}),
  beacon: new THREE.MeshStandardMaterial({color:'#c01616', roughness:.4, metalness:.1, emissive:'#4a0000'}),
  cup: new THREE.MeshStandardMaterial({color:'#262e34', roughness:.55, metalness:.15, side:THREE.DoubleSide}),
  vane: new THREE.MeshStandardMaterial({color:'#20282c', roughness:.55, metalness:.3, side:THREE.DoubleSide}),
  brass: new THREE.MeshStandardMaterial({color:'#d8a94e', roughness:.35, metalness:.7}),
  chain: new THREE.MeshStandardMaterial({color:'#3a3f42', roughness:.6, metalness:.6}),
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

// --- Twin pontoon hulls: capsules Ø0.22m x 1.5m along Z, beam ±0.42m.
for(const sx of [-0.42, 0.42]){
  const hull = mesh(new THREE.CapsuleGeometry(0.11, 1.28, 6, 16), M.hull, sx, -0.02, 0, 'PONTOON_HULL');
  hull.rotation.x = Math.PI/2;
  buoy.add(hull);
  // Deck beams tying each hull to the platform.
  for(const sz of [-0.35, 0.35]){
    buoy.add(mesh(new THREE.BoxGeometry(0.30, 0.05, 0.08), M.frame, sx*0.72, 0.225, sz, 'DECK_BEAM'));
    // Support post: pontoon top (y=0.09) up into the beam — no floating deck.
    buoy.add(mesh(new THREE.BoxGeometry(0.06, 0.16, 0.06), M.frame, sx, 0.15, sz, 'HULL_POST'));
  }
}
// --- Deck platform + non-slip edge trim.
const deck = mesh(new THREE.BoxGeometry(1.10, 0.06, 1.00), M.deck, 0, 0.28, 0, 'DECK_PLATFORM');
buoy.add(deck);
for(const sx of [-0.535, 0.535]){
  buoy.add(mesh(new THREE.BoxGeometry(0.03, 0.045, 1.00), M.hull, sx, 0.33, 0, 'TOE_RAIL_SIDE'));
}
for(const sz of [-0.485, 0.485]){
  buoy.add(mesh(new THREE.BoxGeometry(1.10, 0.045, 0.03), M.hull, 0, 0.33, sz, 'TOE_RAIL_END'));
}

// --- Electronics enclosure amidships.
//
// ROUND TUBE, not a box. On a moored buoy the wind dominates the mooring load
// (current offshore is weak), so the enclosure is a vertical cylinder: its
// projected area to horizontal wind is a circle at EVERY heading, with no sharp
// edges to separate flow and shed vortices. Secondary benefit: a tube is one
// part plus two discs instead of six panels and twelve welds, so it is cheaper
// to build and has fewer seams to leak through.
//
// Volume is held at parity with the old 0.44 x 0.24 x 0.36 box (38.0 L):
//   pi * 0.19^2 * 0.34 = 38.5 L
const CAB_R = 0.19, CAB_H = 0.34;
const CAB_Y = 0.31 + CAB_H/2, CAB_TOP = CAB_Y + CAB_H/2;   // sits on the deck top
const cabinet = mesh(new THREE.CylinderGeometry(CAB_R, CAB_R, CAB_H, 40, 1, true), M.cabinet, 0, CAB_Y, 0, 'ROUND_ELECTRONICS_TUBE');
buoy.add(cabinet);
// Round foot flange that spreads the load onto the deck and closes the bottom.
const cabFlange = mesh(new THREE.CylinderGeometry(CAB_R + 0.022, CAB_R + 0.030, 0.026, 40), M.frame, 0, CAB_Y - CAB_H/2 + 0.013, 0, 'ROUND_CABINET_FOOT_FLANGE');
buoy.add(cabFlange);
buoy.add(mesh(new THREE.CylinderGeometry(CAB_R - 0.004, CAB_R - 0.004, 0.020, 40), M.frame, 0, CAB_Y - CAB_H/2 + 0.010, 0, 'CABINET_BASE_DISC'));
// Bolted top hatch replaces the hinged side door: one gasket seam on a flat
// disc is far more reliable to seal than a seam following a curved wall.
const hatch = mesh(new THREE.CylinderGeometry(CAB_R - 0.012, CAB_R - 0.012, 0.022, 40), M.deck, 0, CAB_TOP + 0.011, 0, 'BOLTED_TOP_HATCH');
buoy.add(hatch);
for(let i=0;i<8;i++){
  const a = (i/8)*Math.PI*2 + Math.PI/8;
  buoy.add(mesh(new THREE.CylinderGeometry(0.008, 0.008, 0.012, 8), M.brass,
    Math.cos(a)*(CAB_R - 0.026), CAB_TOP + 0.028, Math.sin(a)*(CAB_R - 0.026), 'HATCH_BOLT'));
}
buoy.add(mesh(new THREE.BoxGeometry(0.09, 0.010, 0.018), M.frame, 0, CAB_TOP + 0.028, 0.085, 'HATCH_HANDLE'));
// Dry (pressure-equalising) vent so condensation cannot build up inside.
const vent = mesh(new THREE.CylinderGeometry(0.012, 0.014, 0.032, 12), M.brass, 0.085, CAB_TOP + 0.038, 0.075, 'DRY_VENT');
buoy.add(vent);
// Flanged round inspection port, facing forward.
const port = mesh(new THREE.CylinderGeometry(0.048, 0.048, 0.012, 24), M.glass, 0, CAB_Y - 0.02, CAB_R - 0.004, 'SERVICE_PORT_TO_INTERNAL_ELECTRONICS');
port.rotation.x = Math.PI/2;
buoy.add(port);
const portRing = mesh(new THREE.TorusGeometry(0.052, 0.007, 8, 24), M.frame, 0, CAB_Y - 0.02, CAB_R + 0.004, 'SERVICE_PORT_FLANGE');
buoy.add(portRing);

// --- Single 40W-class panel on a tilted frame off a collar band.
// The panel is wider than the tube, so it rides on two posts instead of lying
// on a roof. Tilting it 10 deg keeps it clear of its own shadow.
const COLLAR_Y = CAB_TOP - 0.05;
const collar = mesh(new THREE.TorusGeometry(CAB_R + 0.006, 0.012, 10, 40), M.frame, 0, COLLAR_Y, 0, 'PANEL_COLLAR_BAND');
collar.rotation.x = Math.PI/2;
buoy.add(collar);
const FRAME_Y = 0.7785, PANEL_TILT = -0.18;
for(const sx of [-0.19, 0.19]){
  const h = FRAME_Y - 0.0125 - COLLAR_Y;
  buoy.add(mesh(new THREE.BoxGeometry(0.03, h, 0.03), M.frame, sx, COLLAR_Y + h/2, -0.03, 'PANEL_SUPPORT_POST'));
}
buoy.add(mesh(new THREE.BoxGeometry(0.42, 0.022, 0.028), M.frame, 0, FRAME_Y - 0.023, -0.03, 'PANEL_CROSS_MEMBER'));
const roof = new THREE.Group();
roof.position.set(0, FRAME_Y, -0.03);
roof.rotation.x = PANEL_TILT;
roof.name = 'SINGLE_40W_PANEL_ON_TILTED_FRAME';
buoy.add(roof);
const panelSlab = mesh(new THREE.BoxGeometry(0.62, 0.025, 0.48), M.solar, 0, 0, 0, 'SOLAR_PANEL');
roof.add(panelSlab);
for(let i=-1;i<=1;i++){
  roof.add(mesh(new THREE.BoxGeometry(0.012, 0.028, 0.48), M.solarGrid, i*0.185, 0, 0, 'SOLAR_GRID'));
}
const roofFrame = new THREE.Group();
roofFrame.position.copy(roof.position); roofFrame.rotation.x = PANEL_TILT;
for(const sz of [-0.25, 0.19]){
  roofFrame.add(mesh(new THREE.BoxGeometry(0.66, 0.03, 0.025), M.frame, 0, 0, sz, 'PANEL_END_RAIL'));
}
buoy.add(roofFrame);

// GPS/security puck moved onto its own short deck post. It used to stand on the
// old flat roof, which no longer exists, and the panel frame now occupies that
// space above the tube.
const GPS_X = -0.30, GPS_Z = 0.26, GPS_POST_H = 0.22;
buoy.add(mesh(new THREE.CylinderGeometry(0.014, 0.016, GPS_POST_H, 10), M.frame, GPS_X, 0.31 + GPS_POST_H/2, GPS_Z, 'GPS_POST'));
const gps = mesh(new THREE.CylinderGeometry(0.045, 0.050, 0.030, 18), M.gpsBlue, GPS_X, 0.31 + GPS_POST_H + 0.015, GPS_Z, 'REQUIRED_GPS_POSITION_SECURITY_PUCK');
buoy.add(gps);
const gpsRing = mesh(new THREE.TorusGeometry(0.052, 0.005, 8, 18), M.brass, GPS_X, 0.31 + GPS_POST_H + 0.033, GPS_Z, 'GPS_LABEL_RING');
gpsRing.rotation.x = Math.PI/2;
buoy.add(gpsRing);

// Internal hints (ESP32, power board, battery, buffer) live inside the tube.
buoy.add(mesh(new THREE.BoxGeometry(0.14, 0.045, 0.08), M.battery, -0.10, CAB_Y - 0.02, -0.03, 'INTERNAL_BATTERY_SOLAR_POWER_BAY'));
buoy.add(mesh(new THREE.BoxGeometry(0.056, 0.012, 0.040), M.dark, 0.12, CAB_Y - 0.02, -0.05, 'MICROSD_OR_FLASH_BUFFER_INSIDE_CABINET'));
// Cable glands now exit radially through the curved wall.
for(const ga of [-0.62, 0, 0.62]){
  const radial = new THREE.Vector3(Math.sin(ga), 0, Math.cos(ga));
  const g = mesh(new THREE.CylinderGeometry(0.011, 0.011, 0.030, 10), M.frame, 0, 0, 0, 'SEALED_CABLE_GLAND');
  g.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0), radial);
  g.position.copy(radial).multiplyScalar(CAB_R + 0.010);
  g.position.y = CAB_Y - CAB_H/2 + 0.055;
  buoy.add(g);
}

// --- Red topmark light on a finial stub at the panel front edge.

// --- Wind mast at the deck rear (slim Ø36mm pole straight into the hub).
const WMAST_X = 0, WMAST_Z = -0.44, DECK_TOP = 0.31, MAST_H = 0.38, ROTOR_Y = DECK_TOP + MAST_H;
const wmast = mesh(new THREE.CylinderGeometry(0.018, 0.018, MAST_H, 12), M.frame, WMAST_X, DECK_TOP + MAST_H/2, WMAST_Z, 'WIND_MAST');
buoy.add(wmast);
const mastFoot = mesh(new THREE.CylinderGeometry(0.035, 0.045, 0.06, 12), M.frame, WMAST_X, DECK_TOP + 0.03, WMAST_Z, 'MAST_FOOT');
buoy.add(mastFoot);
// Masthead beacon on the wind mast, well clear of the panel and vane.
const beacon = mesh(new THREE.CylinderGeometry(0.026, 0.026, 0.065, 12), M.beacon, WMAST_X, 0.57, WMAST_Z, 'TOPMARK_BEACON');
buoy.add(beacon);
const beaconDome = mesh(new THREE.SphereGeometry(0.026, 12, 8, 0, Math.PI*2, 0, Math.PI/2), M.beacon, WMAST_X, 0.602, WMAST_Z, 'BEACON_DOME');
buoy.add(beaconDome);
const rotor = new THREE.Group();
rotor.position.set(WMAST_X, ROTOR_Y, WMAST_Z);
rotor.name = 'WIND_SPEED_DIRECTION_SENSOR';
buoy.add(rotor);
const hub = mesh(new THREE.SphereGeometry(0.035, 16, 12), M.dark, 0, 0, 0, 'WIND_HUB');
rotor.add(hub);
rotor.add(mesh(new THREE.CylinderGeometry(0.012, 0.012, 0.022, 10), M.brass, 0, 0.040, 0, 'HUB_NUT'));
// 3 open cups: Ø130mm on a Ø600mm circle. Each cup rides on a pivot rotated
// about Y so every mouth faces the same tangential direction (convex side
// forward, like a real drag anemometer) — never hand-angled per cup.
const cupR = 0.034, armR = 0.140;
for(let i=0;i<3;i++){
  const pivot = new THREE.Group();
  pivot.rotation.y = (i/3)*Math.PI*2;
  rotor.add(pivot);
  const arm = mesh(new THREE.CylinderGeometry(0.008, 0.008, armR, 8), M.frame, armR/2, 0, 0, 'WIND_ARM');
  arm.rotation.z = Math.PI/2;
  pivot.add(arm);
  const cup = mesh(new THREE.SphereGeometry(cupR, 18, 12, 0, Math.PI*2, 0, Math.PI*0.62), M.cup, armR, 0, 0, 'WIND_CUP');
  cup.rotation.x = Math.PI/2; // mouth faces local -Z = backward of travel
  pivot.add(cup);
}
// Wind vane on its own turret, 150mm below the rotor.
const vane = new THREE.Group();
vane.position.set(WMAST_X, ROTOR_Y - 0.075, WMAST_Z);
vane.name = 'WIND_VANE';
buoy.add(vane);
const vaneCollar = mesh(new THREE.TorusGeometry(0.024, 0.010, 8, 16), M.frame, 0, 0, 0, 'VANE_COLLAR');
vaneCollar.rotation.x = Math.PI/2;
vane.add(vaneCollar);
const tail = mesh(new THREE.BoxGeometry(0.009, 0.090, 0.070), M.vane, 0, 0.02, -0.11, 'VANE_TAIL');
vane.add(tail);
vane.add(mesh(new THREE.BoxGeometry(0.010, 0.035, 0.016), M.vane, 0, -0.03, -0.05, 'VANE_FIN_ROOT'));
const nose = mesh(new THREE.ConeGeometry(0.014, 0.050, 12), M.brass, 0, 0.014, 0.085, 'VANE_NOSE');
nose.rotation.x = Math.PI/2;
vane.add(nose);
// Whip on the deck rear corner, far from the rotor (clean mast, clean airflow).
buoy.add(mesh(new THREE.BoxGeometry(0.06, 0.03, 0.06), M.frame, 0.48, 0.325, -0.42, 'WHIP_FOOT'));
const whip = mesh(new THREE.CylinderGeometry(0.006, 0.009, 0.35, 8), M.dark, 0.48, 0.515, -0.42, 'WIFI_LTE_WHIP_ANTENNA');
buoy.add(whip);
const whipTip = mesh(new THREE.SphereGeometry(0.012, 10, 8), M.brass, 0.48, 0.69, -0.42, 'WHIP_TIP');
buoy.add(whipTip);

// --- Pressure sensor hung between the hulls (protected + easy service).
const stillingBar = mesh(new THREE.BoxGeometry(0.72,0.026,0.026), M.frame, 0, 0.05, 0.10, 'PRESSURE_SENSOR_SUPPORT_BAR');
buoy.add(stillingBar);
const dropCable = mesh(new THREE.CylinderGeometry(0.008, 0.008, 0.36, 8), M.chain, 0, -0.05, 0.10, 'SENSOR_DROP_CABLE');
buoy.add(dropCable);
const psens = mesh(new THREE.CylinderGeometry(0.035, 0.035, 0.14, 14), M.dark, 0, -0.28, 0.10, 'WATER_PRESSURE_SENSOR');
buoy.add(psens);
const sensorGuard = new THREE.Group();
sensorGuard.name = 'PRESSURE_SENSOR_GUARD_CAGE';
for(const sx of [-0.08,0.08]) sensorGuard.add(strut([sx,0.05,0.10],[sx,-0.36,0.10],0.006,M.frame,'GUARD_POST'));
sensorGuard.add(strut([-0.08,-0.36,0.10],[0.08,-0.36,0.10],0.006,M.frame,'GUARD_BOTTOM'));
buoy.add(sensorGuard);
// --- Balanced underside bridle, visible center chain, and anchor/deadweight study.
// The chain now hangs from the geometric center under the deck. Four bridle
// legs share the load back to both pontoons so wave/current pull is applied
// through the middle instead of twisting the catamaran from one side.
const centerSwivel = mesh(new THREE.TorusGeometry(0.058, 0.013, 8, 22), M.chain, 0, -0.20, 0, 'CENTER_MOORING_SWIVEL');
centerSwivel.rotation.x = Math.PI/2;
buoy.add(centerSwivel);
for(const sx of [-0.42, 0.42]){
  for(const sz of [-0.24, 0.24]){
    buoy.add(strut([sx, -0.045, sz], [0, -0.20, 0], 0.009, M.rope, 'BALANCED_FOUR_POINT_BRIDLE_LINE'));
  }
}
const mooring = new THREE.Group();
mooring.name = 'MOORING_CHAIN_AND_ANCHOR_STUDY';
mooring.add(chainBetween([0,-0.20,0],[0,-0.72,0],11,0.028));
mooring.add(strut([0,-0.72,0],[0.16,-1.00,0.72],0.011,M.rope,'SCOPE_ROPE_TO_ANCHOR'));
const anchorBlock = mesh(new THREE.BoxGeometry(0.42,0.11,0.28), M.anchor, 0.22, -1.05, 0.82, 'CONCRETE_OR_DEADWEIGHT_ANCHOR');
anchorBlock.rotation.y = -0.12;
mooring.add(anchorBlock);
const anchorEye = mesh(new THREE.TorusGeometry(0.050,0.011,8,18), M.chain, 0.12, -0.98, 0.65, 'ANCHOR_EYE');
anchorEye.rotation.y = Math.PI/2;
mooring.add(anchorEye);
const anchorStock = mesh(new THREE.BoxGeometry(0.54,0.012,0.012), M.anchor, 0.22, -0.96, 0.82, 'ANCHOR_STOCK');
anchorStock.rotation.y = -0.12;
mooring.add(anchorStock);
buoy.add(mooring);

// --- Camera orbit (manual, no extra addon dependency).
const views = {
  top: {yaw:0.72, pitch:1.42, dist:1.9, focus:[0,0.28,0]},
  orbit: {yaw:0.7, pitch:0.12, dist:4.4, focus:[0,0.45,0]},
  wind: {yaw:0.3, pitch:0.08, dist:1.75, focus:[WMAST_X,ROTOR_Y-0.08,WMAST_Z]},
  solar: {yaw:0.7, pitch:0.12, dist:2.4, focus:[0,CAB_TOP+0.15,0]},
  mooring: {yaw:3.3, pitch:-0.34, dist:3.2, focus:[0.22,-0.62,0.92]},
  below: {yaw:3.6, pitch:-0.25, dist:2.8, focus:[0,-0.20,0.15]},
};
let yaw = views.orbit.yaw, pitch = views.orbit.pitch, dist = views.orbit.dist;
let focus = new THREE.Vector3(...views.orbit.focus);
let target = {yaw, pitch, dist, focus: focus.clone()};
document.querySelectorAll('#hud button').forEach(b=>{
  b.addEventListener('click', ()=>{ const v = views[b.dataset.view]; if(v) target = {...v, focus: new THREE.Vector3(...v.focus)}; });
});
const DMIN = 1.2, DMAX = 12;
let dragging = false, px = 0, py = 0;
const el = renderer.domElement;
el.addEventListener('pointerdown', e=>{ dragging = true; px = e.clientX; py = e.clientY; el.setPointerCapture(e.pointerId); });
el.addEventListener('pointermove', e=>{
  if(!dragging || touches.size >= 2) return; // 2 fingers = pinch, not orbit
  target.yaw -= (e.clientX - px)*0.006;
  target.pitch = Math.max(-0.9, Math.min(1.48, target.pitch + (e.clientY - py)*0.004));
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

// Fixed approval renders for screenshots: front, top, bottom and side.
// Each card uses a clone of the actual Option B model so the approval views
// cannot drift from the interactive preview.
function initApprovalViewCards(){
  const targets = [...document.querySelectorAll('[data-approval-view]')];
  if(!targets.length) return;
  const configs = {
    front: {pos:[0,0.40,3.5], up:[0,1,0], zoom:1.05, focus:[0,0.22,0]},
    side: {pos:[3.5,0.36,0], up:[0,1,0], zoom:1.05, focus:[0,0.20,0]},
    top: {pos:[0,4.0,0.001], up:[0,0,-1], zoom:1.05, focus:[0,0.20,0]},
    bottom: {pos:[0,-4.0,0.001], up:[0,0,1], zoom:1.20, focus:[0,-0.25,0.08]},
  };
  const renderers = [];
  for(const box of targets){
    const key = box.dataset.approvalView;
    const cfg = configs[key];
    if(!cfg) continue;
    const r = new THREE.WebGLRenderer({antialias:true, alpha:true, preserveDrawingBuffer:true});
    r.setPixelRatio(Math.min(devicePixelRatio, 2));
    r.outputColorSpace = THREE.SRGBColorSpace;
    box.prepend(r.domElement);

    const sc = new THREE.Scene();
    sc.background = new THREE.Color('#071720');
    sc.add(new THREE.HemisphereLight('#d8edf4', '#1d333b', 2.4));
    const keyLight = new THREE.DirectionalLight('#f6e2b6', 3.0);
    keyLight.position.set(-3, 4, 5); sc.add(keyLight);
    const fill = new THREE.DirectionalLight('#80bdd7', 1.4);
    fill.position.set(4, 2, -4); sc.add(fill);

    const clone = buoy.clone(true);
    clone.rotation.y = key === 'side' ? -Math.PI / 2 : 0;
    if(key !== 'bottom') clone.traverse(o=>{ if(o.name === 'MOORING_CHAIN_AND_ANCHOR_STUDY') o.visible = false; });
    clone.traverse(o=>{
      if(o.name === 'WIND_SPEED_DIRECTION_SENSOR') o.rotation.y = 0.35;
      if(o.name === 'WIND_VANE') o.rotation.y = 0.15;
    });
    sc.add(clone);

    const cam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0.05, 20);
    cam.position.set(...cfg.pos);
    cam.up.set(...cfg.up);
    cam.lookAt(new THREE.Vector3(...cfg.focus));

    const render = ()=>{
      const w = Math.max(2, box.clientWidth);
      const h = Math.max(2, box.clientHeight);
      r.setSize(w, h, false);
      const aspect = w / h;
      const base = cfg.zoom;
      cam.left = -base * aspect; cam.right = base * aspect;
      cam.top = base; cam.bottom = -base;
      cam.updateProjectionMatrix();
      r.render(sc, cam);
    };
    renderers.push({box, render});
    render();
  }
  const ro = new ResizeObserver(entries=>{
    const changed = new Set(entries.map(e=>e.target));
    for(const item of renderers) if(changed.has(item.box)) item.render();
  });
  for(const item of renderers) ro.observe(item.box);
}
initApprovalViewCards();

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
