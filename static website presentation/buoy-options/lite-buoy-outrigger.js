// FALCON Lite Option C — mooring-ball sphere preview (procedural, no CAD edit).
// Off-the-shelf spherical float + through-mast with panel, wind head and
// hanging sensors below. Cheapest certified hull: zero hull fabrication.
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
  hull: new THREE.MeshStandardMaterial({color:'#e8821a', roughness:.5, metalness:.08}),
  steel: new THREE.MeshStandardMaterial({color:'#6b7178', roughness:.45, metalness:.6}),
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

const buoy = new THREE.Group();
scene.add(buoy);

// --- Hull: off-the-shelf mooring-ball sphere Ø0.7m, center just above water.
const ball = mesh(new THREE.SphereGeometry(0.35, 40, 28), M.hull, 0, 0.05, 0, 'MOORING_BALL_HULL');
buoy.add(ball);
// Waterline ring where the sphere meets the sea.
const waterRing = mesh(new THREE.TorusGeometry(0.346, 0.018, 10, 48), M.steel, 0, 0.0, 0, 'WATERLINE_RING');
waterRing.rotation.x = Math.PI/2;
buoy.add(waterRing);
// Keel stub + ballast ball + mooring eye + chain below.
const keel = mesh(new THREE.CylinderGeometry(0.05, 0.06, 0.18, 14), M.frame, 0, -0.36, 0, 'KEEL_STUB');
buoy.add(keel);
const ballast = mesh(new THREE.SphereGeometry(0.085, 16, 12), M.dark, 0, -0.50, 0, 'BALLAST');
buoy.add(ballast);
const eye = mesh(new THREE.TorusGeometry(0.045, 0.012, 8, 20), M.chain, 0, -0.60, 0, 'MOORING_EYE');
buoy.add(eye);
const chainStub = mesh(new THREE.CylinderGeometry(0.015, 0.015, 0.28, 10), M.chain, 0, -0.76, 0, 'MOORING_CHAIN_STUB');
buoy.add(chainStub);
// --- Pressure sensor hung beside the keel cable (protected under the ball).
const dropCable = mesh(new THREE.CylinderGeometry(0.008, 0.008, 0.30, 8), M.chain, 0.10, -0.42, 0.05, 'SENSOR_DROP_CABLE');
buoy.add(dropCable);
const psens = mesh(new THREE.CylinderGeometry(0.035, 0.035, 0.14, 14), M.dark, 0.10, -0.62, 0.05, 'WATER_PRESSURE_SENSOR');
buoy.add(psens);

// --- Through-mast: single pole from inside the ball up past the panel.
const MAST_R = 0.022, MAST_TOP = 1.20;
const mast = mesh(new THREE.CylinderGeometry(MAST_R, MAST_R, MAST_TOP - 0.10, 12), M.frame, 0, (MAST_TOP + 0.10)/2, 0, 'THROUGH_MAST');
buoy.add(mast);
const mastCollar = mesh(new THREE.TorusGeometry(0.045, 0.016, 8, 20), M.frame, 0, 0.41, 0, 'MAST_COLLAR');
mastCollar.rotation.x = Math.PI/2;
buoy.add(mastCollar);
// --- Small panel clamped on the mast, tilted 15° (single 40W-class).
const panelG = new THREE.Group();
panelG.position.set(0, 0.72, 0.0);
panelG.rotation.x = -0.26;
panelG.name = 'MAST_PANEL';
buoy.add(panelG);
const panelSlab = mesh(new THREE.BoxGeometry(0.50, 0.025, 0.38), M.solar, 0, 0, 0.035, 'SOLAR_PANEL');
panelG.add(panelSlab);
for(let i=-1;i<=1;i++){
  panelG.add(mesh(new THREE.BoxGeometry(0.012, 0.028, 0.38), M.solarGrid, i*0.15, 0, 0.035, 'SOLAR_GRID'));
}
buoy.add(mesh(new THREE.BoxGeometry(0.05, 0.05, 0.10), M.frame, 0, 0.72, -0.03, 'PANEL_CLAMP'));
// --- Red beacon band on the mast above the panel.
const tipDome = mesh(new THREE.SphereGeometry(0.032, 14, 10, 0, Math.PI*2, 0, Math.PI/2), M.beacon, 0, MAST_TOP, 0, 'TOPMARK_DOME');
buoy.add(tipDome);

// --- Compact wind head on the mast top (smaller cups suit the small buoy).
const ROTOR_Y = 1.10;
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
const vaneCollar = mesh(new THREE.TorusGeometry(0.028, 0.010, 8, 16), M.frame, 0, 0, 0, 'VANE_COLLAR');
vaneCollar.rotation.x = Math.PI/2;
vane.add(vaneCollar);
const tail = mesh(new THREE.BoxGeometry(0.012, 0.11, 0.09), M.vane, 0, 0.015, -0.10, 'VANE_TAIL');
vane.add(tail);
const nose = mesh(new THREE.ConeGeometry(0.018, 0.06, 10), M.brass, 0, 0.015, 0.10, 'VANE_NOSE');
nose.rotation.x = Math.PI/2;
vane.add(nose);
// Whip on a short bracket off the mast, below the panel.
buoy.add(mesh(new THREE.BoxGeometry(0.30, 0.025, 0.025), M.frame, -0.15, 0.62, 0, 'WHIP_BRACKET'));
const whip = mesh(new THREE.CylinderGeometry(0.006, 0.009, 0.30, 8), M.dark, -0.30, 0.76, 0, 'WHIP_ANTENNA');
buoy.add(whip);
const whipTip = mesh(new THREE.SphereGeometry(0.012, 10, 8), M.brass, -0.30, 0.91, 0, 'WHIP_TIP');
buoy.add(whipTip);

// --- Camera orbit (manual, no extra addon dependency).
const views = {
  orbit: {yaw:0.7, pitch:0.12, dist:3.6, focus:[0,0.30,0]},
  wind: {yaw:0.3, pitch:0.08, dist:1.7, focus:[0,ROTOR_Y-0.10,0]},
  solar: {yaw:0.7, pitch:0.12, dist:2.2, focus:[0,0.72,0.05]},
  below: {yaw:3.6, pitch:-0.25, dist:2.6, focus:[0,-0.45,0]},
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
  // Gentle float: round hulls roll a touch more (motion illustrative only).
  buoy.position.y = Math.sin(t*0.9)*0.03;
  buoy.rotation.x = Math.sin(t*0.7)*0.010;
  buoy.rotation.z = Math.sin(t*0.6)*0.010;
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
