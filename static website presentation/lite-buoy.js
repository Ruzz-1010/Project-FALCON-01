// FALCON Lite — proposed low-cost buoy preview (procedural, no CAD edit).
// Form follows the reference drum-buoy: squat cylindrical hull, tapered
// 4-sided tower, one solar panel per sloped face, red topmark beacon.
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
  dark: new THREE.MeshStandardMaterial({color:'#161d20', roughness:.6, metalness:.3}),
  enclosure: new THREE.MeshStandardMaterial({color:'#cfd8db', roughness:.5, metalness:.15}),
  solar: new THREE.MeshStandardMaterial({color:'#101f31', roughness:.32, metalness:.5}),
  solarFrame: new THREE.MeshStandardMaterial({color:'#9aa4ab', roughness:.4, metalness:.6}),
  gps: new THREE.MeshStandardMaterial({color:'#f2f4f4', roughness:.4, metalness:.05}),
  lora: new THREE.MeshStandardMaterial({color:'#7a1f1f', roughness:.55, metalness:.2}),
  beacon: new THREE.MeshStandardMaterial({color:'#c01616', roughness:.4, metalness:.1, emissive:'#4a0000'}),
  cup: new THREE.MeshStandardMaterial({color:'#101415', roughness:.5, metalness:.35, side:THREE.DoubleSide}),
  vane: new THREE.MeshStandardMaterial({color:'#20282c', roughness:.55, metalness:.3, side:THREE.DoubleSide}),
  brass: new THREE.MeshStandardMaterial({color:'#d8a94e', roughness:.35, metalness:.7}),
  chain: new THREE.MeshStandardMaterial({color:'#3a3f42', roughness:.6, metalness:.6}),
  fender: new THREE.MeshStandardMaterial({color:'#e8a0b4', roughness:.6, metalness:.0}),
};
function mesh(geo, mat, x=0, y=0, z=0, name=''){
  const m = new THREE.Mesh(geo, mat);
  m.position.set(x, y, z); m.castShadow = true; m.receiveShadow = true;
  if(name) m.name = name;
  return m;
}

const buoy = new THREE.Group();
scene.add(buoy);

// --- Hull: squat drum, Ø1.2m, rounded bilge (lathe). Deck top at y=0.55.
const profile = [
  [0.001,-0.10],[0.30,-0.10],[0.48,-0.02],[0.58,0.12],[0.60,0.25],[0.60,0.55]
].map(([r,y])=>new THREE.Vector2(r,y));
const hull = mesh(new THREE.LatheGeometry(profile, 40), M.hull, 0, 0, 0, 'DRUM_HULL');
buoy.add(hull);
// Waterline rub band.
const band = mesh(new THREE.CylinderGeometry(0.605, 0.605, 0.05, 40, 1, true), M.steel, 0, 0.14, 0, 'WATERLINE_BAND');
buoy.add(band);
// Deck disc + rim ring + bolts.
const deck = mesh(new THREE.CylinderGeometry(0.60, 0.60, 0.04, 40), M.deck, 0, 0.55, 0, 'DECK');
buoy.add(deck);
const rimRing = mesh(new THREE.TorusGeometry(0.585, 0.016, 10, 48), M.steel, 0, 0.575, 0, 'DECK_RIM');
rimRing.rotation.x = Math.PI/2;
buoy.add(rimRing);
for(let i=0;i<12;i++){
  const a = (i/12)*Math.PI*2;
  buoy.add(mesh(new THREE.CylinderGeometry(0.014, 0.014, 0.022, 8), M.steel, Math.cos(a)*0.54, 0.578, Math.sin(a)*0.54, 'DECK_BOLT'));
}
// Mooring eyes + chain stub below hull.
for(const sx of [-0.12, 0.12]){
  const e = mesh(new THREE.TorusGeometry(0.045, 0.012, 8, 20), M.chain, sx, -0.13, 0, 'MOORING_EYE');
  buoy.add(e);
}
const chainStub = mesh(new THREE.CylinderGeometry(0.016, 0.016, 0.35, 10), M.chain, 0, -0.32, 0, 'MOORING_CHAIN_STUB');
buoy.add(chainStub);
// Pressure sensor can strapped low on hull side + cable stub up.
const psens = mesh(new THREE.CylinderGeometry(0.035, 0.035, 0.12, 16), M.dark, 0.0, 0.02, 0.60, 'WATER_PRESSURE_SENSOR_ASSEMBLY');
psens.rotation.x = Math.PI/2.3;
buoy.add(psens);
// Side fender (pink capsule) hanging off the hull side.
const rope = mesh(new THREE.CylinderGeometry(0.008, 0.008, 0.22, 8), M.chain, 0.60, 0.48, -0.15, 'FENDER_ROPE');
buoy.add(rope);
const fender = mesh(new THREE.CapsuleGeometry(0.05, 0.22, 6, 12), M.fender, 0.63, 0.26, -0.15, 'SIDE_FENDER');
buoy.add(fender);

// --- Tower: 4-sided tapered frustum on deck. Base face 0.72 -> top face 0.38, h 0.48.
const TOWER_Y = 0.57, TOWER_H = 0.48, TOWER_CY = TOWER_Y + TOWER_H/2;
const tower = mesh(new THREE.CylinderGeometry(0.27, 0.51, TOWER_H, 4, 1), M.hull, 0, TOWER_CY, 0, 'TOWER_FRUSTUM');
tower.rotation.y = Math.PI/4; // faces look along +-X / +-Z
buoy.add(tower);
// One solar panel per sloped face (4 faces, ~40W class total for Lite budget).
const tilt = Math.atan((0.36-0.19)/TOWER_H); // face slope from vertical
const solarGroup = new THREE.Group();
solarGroup.name = 'SOLAR_FACE_PANELS';
buoy.add(solarGroup);
for(let k=0;k<4;k++){
  const face = new THREE.Group();
  face.rotation.y = k*Math.PI/2;
  const frame = mesh(new THREE.BoxGeometry(0.32, 0.42, 0.008), M.solarFrame, 0, TOWER_CY, 0.286, 'SOLAR_PANEL_FRAME');
  const panel = mesh(new THREE.BoxGeometry(0.30, 0.40, 0.014), M.solar, 0, TOWER_CY, 0.292, 'SOLAR_PANEL_FACE');
  frame.rotation.x = -tilt; panel.rotation.x = -tilt;
  face.add(frame, panel);
  solarGroup.add(face);
}
// Top plate + red topmark beacon + whip.
const plate = mesh(new THREE.BoxGeometry(0.40, 0.03, 0.40), M.deck, 0, TOWER_Y+TOWER_H+0.015, 0, 'TOP_PLATE');
buoy.add(plate);
const TOP_Y = TOWER_Y+TOWER_H+0.03;
const beaconBase = mesh(new THREE.CylinderGeometry(0.07, 0.07, 0.04, 16), M.dark, 0.05, TOP_Y+0.02, 0.05, 'BEACON_BASE');
buoy.add(beaconBase);
const beacon = mesh(new THREE.CylinderGeometry(0.055, 0.055, 0.12, 16), M.beacon, 0.05, TOP_Y+0.10, 0.05, 'TOPMARK_BEACON');
buoy.add(beacon);
const beaconDome = mesh(new THREE.SphereGeometry(0.055, 16, 10, 0, Math.PI*2, 0, Math.PI/2), M.beacon, 0.05, TOP_Y+0.16, 0.05, 'BEACON_DOME');
buoy.add(beaconDome);
const whip = mesh(new THREE.CylinderGeometry(0.006, 0.009, 0.40, 8), M.dark, -0.10, TOP_Y+0.20, -0.10, 'WHIP_ANTENNA');
buoy.add(whip);
const whipTip = mesh(new THREE.SphereGeometry(0.012, 10, 8), M.brass, -0.10, TOP_Y+0.40, -0.10, 'WHIP_TIP');
buoy.add(whipTip);

// --- Wind head on a slim mast at the plate corner (Ø36mm pole straight
// into the hub: standard anemometer mount, no fat tube in the rotor plane).
const WMAST_X = -0.14, WMAST_Z = 0.13, ROTOR_Y = TOP_Y + 0.62;
const wmast = mesh(new THREE.CylinderGeometry(0.018, 0.018, 0.62, 12), M.frame, WMAST_X, TOP_Y+0.31, WMAST_Z, 'WIND_MAST');
buoy.add(wmast);
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

// --- Deck kept clean like the reference: GPS puck, LoRa and controller ride
// inside the hull/tower (illustrative internal mount, no deck clutter).
// Only the LoRa SMA stub stays visible on the tower rear face.
const loraSma = mesh(new THREE.CylinderGeometry(0.008, 0.008, 0.05, 10), M.brass, 0, 0.95, -0.235, 'LORA_SMA');
loraSma.rotation.x = Math.PI/2;
buoy.add(loraSma);

// --- Camera orbit (manual, no extra addon dependency).
const views = {
  orbit: {yaw:0.7, pitch:0.16, dist:4.8, focus:[0,0.75,0]},
  wind: {yaw:0.3, pitch:0.10, dist:1.9, focus:[WMAST_X,1.62,WMAST_Z]},
  solar: {yaw:0.7, pitch:0.14, dist:2.6, focus:[0,0.82,0.10]},
  below: {yaw:3.6, pitch:-0.28, dist:3.0, focus:[0,-0.02,0]},
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
el.addEventListener('wheel', e=>{ e.preventDefault(); target.dist = Math.max(1.2, Math.min(10, target.dist + e.deltaY*0.003)); }, {passive:false});

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
