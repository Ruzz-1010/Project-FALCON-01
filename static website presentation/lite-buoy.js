// FALCON Lite — proposed low-cost buoy preview (procedural, no CAD edit).
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
  collar: new THREE.MeshStandardMaterial({color:'#274b5a', roughness:.7, metalness:.1}),
  frame: new THREE.MeshStandardMaterial({color:'#5b6b72', roughness:.5, metalness:.6}),
  dark: new THREE.MeshStandardMaterial({color:'#161d20', roughness:.6, metalness:.3}),
  enclosure: new THREE.MeshStandardMaterial({color:'#cfd8db', roughness:.5, metalness:.15}),
  solar: new THREE.MeshStandardMaterial({color:'#12283f', roughness:.35, metalness:.55}),
  solarGrid: new THREE.MeshStandardMaterial({color:'#3f6d8f', roughness:.4, metalness:.4}),
  gps: new THREE.MeshStandardMaterial({color:'#f2f4f4', roughness:.4, metalness:.05}),
  lora: new THREE.MeshStandardMaterial({color:'#7a1f1f', roughness:.55, metalness:.2}),
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

// --- Hull: single vertical PVC tube Ø200mm x 1.5m, waterline at y=0.
const tube = mesh(new THREE.CylinderGeometry(0.10, 0.10, 1.5, 28), M.pvc, 0, 0.35, 0, 'PVC_HULL_TUBE');
buoy.add(tube);
// Collar float Ø1.1m x 0.15m at waterline (light, low-cost collar).
const collar = mesh(new THREE.CylinderGeometry(0.55, 0.55, 0.15, 40), M.collar, 0, 0.02, 0, 'COLLAR_FLOAT');
buoy.add(collar);
// Keel stub + mooring eye + chain stub below.
const keel = mesh(new THREE.CylinderGeometry(0.045, 0.045, 0.5, 16), M.frame, 0, -0.62, 0, 'KEEL_STUB');
buoy.add(keel);
const eye = mesh(new THREE.TorusGeometry(0.055, 0.014, 10, 24), M.chain, 0, -0.9, 0, 'MOORING_EYE');
buoy.add(eye);
const chainStub = mesh(new THREE.CylinderGeometry(0.016, 0.016, 0.35, 10), M.chain, 0, -1.12, 0, 'MOORING_CHAIN_STUB');
buoy.add(chainStub);
// Pressure sensor can (illustrative) strapped low on tube, cable up.
const psens = mesh(new THREE.CylinderGeometry(0.035, 0.035, 0.12, 16), M.dark, 0.0, -0.35, 0.115, 'WATER_PRESSURE_SENSOR_ASSEMBLY');
psens.rotation.x = Math.PI/2.4;
buoy.add(psens);

// --- Topside: faceted cap plate + single enclosure + clamp band.
const capY = 1.12;
const cap = mesh(new THREE.CylinderGeometry(0.30, 0.34, 0.10, 6), M.enclosure, 0, capY, 0, 'TOP_CAP_FACETED');
buoy.add(cap);
const enclosure = mesh(new THREE.BoxGeometry(0.34, 0.26, 0.24), M.enclosure, -0.02, capY + 0.19, -0.05, 'ESP32_CONTROLLER_ENVELOPE');
buoy.add(enclosure);
const band = mesh(new THREE.CylinderGeometry(0.115, 0.115, 0.07, 24, 1, true), M.frame, 0, 0.92, 0, 'CLAMP_BAND');
buoy.add(band);
// GPS dome (true hemisphere) left of band; LoRa case right of band.
const gps = mesh(new THREE.SphereGeometry(0.082, 24, 12, 0, Math.PI*2, 0, Math.PI/2), M.gps, -0.16, 0.955, 0.02, 'GNSS_GPS_ANTENNA');
buoy.add(gps);
const lora = mesh(new THREE.BoxGeometry(0.09, 0.12, 0.05), M.lora, 0.16, 0.92, 0.02, 'LORA_BUOY_RADIO');
buoy.add(lora);
const loraSma = mesh(new THREE.CylinderGeometry(0.008, 0.008, 0.05, 10), M.brass, 0.16, 1.0, 0.02, 'LORA_SMA');
buoy.add(loraSma);
// Whip on offset bracket, kept below rotor plane.
const whipBracket = mesh(new THREE.BoxGeometry(0.16, 0.02, 0.02), M.frame, -0.10, 1.30, -0.10, 'WHIP_BRACKET');
buoy.add(whipBracket);
const whip = mesh(new THREE.CylinderGeometry(0.006, 0.009, 0.55, 8), M.dark, -0.17, 1.58, -0.10, 'WHIP_ANTENNA');
buoy.add(whip);
const whipTip = mesh(new THREE.SphereGeometry(0.012, 10, 8), M.brass, -0.17, 1.86, -0.10, 'WHIP_TIP');
buoy.add(whipTip);

// --- Mast post: flat post 0.11 -> 0.085 (not a spire).
const mastBase = capY + 0.05;
const mastTop = 2.05;
const mastH = mastTop - mastBase;
const mast = mesh(new THREE.CylinderGeometry(0.085, 0.11, mastH, 16), M.pvc, 0, mastBase + mastH/2, 0, 'MAST_POST');
buoy.add(mast);

// --- Wind head: Ø36mm standoff gives 350mm clearance above tube/mast top.
// Rotor plane at mastTop + 0.35.
const rotorY = mastTop + 0.35;
const standoff = mesh(new THREE.CylinderGeometry(0.018, 0.018, 0.35, 12), M.frame, 0, mastTop + 0.175, 0, 'WIND_STANDOFF');
buoy.add(standoff);
const rotor = new THREE.Group();
rotor.position.set(0, rotorY, 0);
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
  // Face opening tangentially so rotation reads wind (illustrative orientation).
  cup.rotation.y = -a + Math.PI/2;
  cup.rotation.x = Math.PI/2;
  rotor.add(cup);
}
// Wind vane 150mm below rotor on its own free-turning turret.
const vane = new THREE.Group();
vane.position.set(0, rotorY - 0.15, 0);
vane.name = 'WIND_VANE';
buoy.add(vane);
const vaneMast = mesh(new THREE.CylinderGeometry(0.012, 0.012, 0.12, 8), M.frame, 0, 0, 0, 'VANE_TURRET');
vane.add(vaneMast);
const tail = mesh(new THREE.BoxGeometry(0.02, 0.18, 0.14), M.vane, 0, 0.02, -0.14, 'VANE_TAIL');
vane.add(tail);
const nose = mesh(new THREE.ConeGeometry(0.025, 0.09, 12), M.brass, 0, 0.02, 0.14, 'VANE_NOSE');
nose.rotation.x = Math.PI/2;
vane.add(nose);

// --- Single 40W panel ≈670x530mm, tilted 18°, mounted on cap south face.
const panel = new THREE.Group();
panel.position.set(0, capY + 0.02, 0.38);
panel.rotation.x = -0.32;
panel.name = 'SINGLE_40W_SOLAR';
buoy.add(panel);
const panelSlab = mesh(new THREE.BoxGeometry(0.67, 0.025, 0.53), M.solar, 0, 0, 0, 'SOLAR_PANEL');
panel.add(panelSlab);
for(let i=-1;i<=1;i++){
  const rib = mesh(new THREE.BoxGeometry(0.012, 0.028, 0.53), M.solarGrid, i*0.2, 0, 0, 'SOLAR_GRID');
  panel.add(rib);
}
const panelArmL = mesh(new THREE.BoxGeometry(0.03, 0.22, 0.03), M.frame, -0.28, -0.12, -0.10, 'PANEL_BRACKET');
panelArmL.rotation.x = 0.5;
panel.add(panelArmL);
const panelArmR = panelArmL.clone(); panelArmR.position.x = 0.28;
panel.add(panelArmR);

// Battery envelope inside tube (shown as translucent marker, not a cutaway claim).
const batt = mesh(new THREE.CylinderGeometry(0.075, 0.075, 0.42, 18), new THREE.MeshStandardMaterial({color:'#3f6d2f', roughness:.6}), 0, 0.45, 0, 'LIFEPO4_BATTERY_12V_ENVELOPE');
batt.material.transparent = true; batt.material.opacity = 0.0;
buoy.add(batt);

// --- Camera orbit (manual, no extra addon dependency).
let yaw = 0.7, pitch = 0.32, dist = 4.6;
const views = {
  orbit: {yaw:0.7, pitch:0.32, dist:4.6},
  wind: {yaw:0.15, pitch:0.18, dist:2.4},
  solar: {yaw:2.6, pitch:0.22, dist:2.8},
  below: {yaw:3.6, pitch:-0.35, dist:3.4},
};
let target = {yaw:yaw, pitch:pitch, dist:dist};
document.querySelectorAll('#hud button').forEach(b=>{
  b.addEventListener('click', ()=>{ target = {...views[b.dataset.view]}; });
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
el.addEventListener('wheel', e=>{ e.preventDefault(); target.dist = Math.max(1.6, Math.min(10, target.dist + e.deltaY*0.003)); }, {passive:false});

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
  const focus = new THREE.Vector3(0, 0.9, 0);
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
