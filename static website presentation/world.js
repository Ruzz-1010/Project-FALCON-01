import * as THREE from 'three';
import {GLTFLoader} from 'three/examples/jsm/loaders/GLTFLoader.js';
import modelUrl from '../dashboard-next/public/models/PROJECT-FALCON-V2.glb?url';
import {components} from './story.js';
import {easeInspection,inspectionFrame} from './inspection.js';
import {createCoast,coastCamera,crossingCamera,RECEIVER} from './coast.js';
import {homeShots,homeCamera,homeWeight} from './home.js';
import {instrumentTargets} from './instrument.js';
import {placeCallout} from './composition.js';
import {buoyMotion,cameraBlend} from './motion.js';
import {createBayStation} from './bay-station.js';
import {createHomeOrbit} from './home-orbit.js';

// =============================================================
// FALCON-01 — Blue sky, CPU waves, technical layout
// Ch02: buoy right, proper size
// Ch03: NO buoy (hidden) — SVG + text lang
// =============================================================

const poses = [
  homeShots[0],
  {eye:[2.6,1.45,3.8], aim:[-.65,.55,0]},        // Ch01: centered
  {
 eye:[0.65,0.55,1.15],
 aim:[-0.45,0.25,0]
},         // Ch02: buoy MUCH closer, right side
  {eye:[8,4.5,14], aim:[0,1,0]},                 // Ch03: controller engineering view
  coastCamera[0],
  coastCamera[2],
  {eye:[12,1.1,7], aim:[10,.2,-2]},
  {eye:[10,2.1,7], aim:[9,.3,-2]},
  {eye:[9,2.3,8], aim:[7,.4,-2]},
  {eye:[5,3,9], aim:[0,.15,0]}
];

export async function createWorld(host, {onPick, onStatus, onInspectionReady=()=>{},onBayPick=()=>{},onBayReady=()=>{}}) {
  let renderer;
  try { renderer = new THREE.WebGLRenderer({antialias: true, alpha: false, powerPreference:'low-power'}); }
  catch { document.body.classList.add('webgl-unavailable'); onStatus('3D unavailable · diagrams and story remain accessible'); return {update(){},dispose(){}}; }

  renderer.setPixelRatio(Math.min(devicePixelRatio, 1.25));
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.15;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFShadowMap;
  host.append(renderer.domElement);

  const scene = new THREE.Scene();
  scene.background = new THREE.Color('#6a9ac8');
  scene.fog = new THREE.FogExp2('#a8c0d8', 0.008);

  const camera = new THREE.PerspectiveCamera(42, 1, .03, 300);
  camera.position.fromArray(poses[0].eye);
  const aim = new THREE.Vector3().fromArray(poses[0].aim);

  const sun = new THREE.DirectionalLight('#ffffff', 2.4);
  sun.position.set(0, 25, 10);   // higher, from front
  sun.castShadow = true;
  sun.shadow.mapSize.set(1024, 1024);
  sun.shadow.camera.near = 0.5;
  sun.shadow.camera.far = 80;
  sun.shadow.camera.left = -28;
  sun.shadow.camera.right = 28;
  sun.shadow.camera.top = 28;
  sun.shadow.camera.bottom = -28;
  sun.shadow.bias = -0.0005;
  sun.shadow.normalBias = 0.02;
  scene.add(sun);
  scene.add(sun.target);
  sun.target.position.set(0, 0, 0);

  const hemi = new THREE.HemisphereLight('#a8c8e8', '#5a6a70', 1.8);
  scene.add(hemi);

  const OCEAN_W = 74;
  const OCEAN_D = 130;
  const OCEAN_CX = -65 + OCEAN_W / 2;
  const OCEAN_SEG = 100;

  const oceanGeo = new THREE.PlaneGeometry(OCEAN_W, OCEAN_D, OCEAN_SEG, OCEAN_SEG);
  oceanGeo.rotateX(-Math.PI / 2);
  oceanGeo.translate(OCEAN_CX, 0, 0);

  const oceanBasePositions = new Float32Array(oceanGeo.attributes.position.array);
  const oceanPositions = oceanGeo.attributes.position;

  const oceanMat = new THREE.MeshStandardMaterial({
    color: '#1a5a78',
    roughness: 0.25,
    metalness: 0.55,
    transparent: true,
    opacity: 1,
    side: THREE.DoubleSide,
    flatShading: false
  });

  const ocean = new THREE.Mesh(oceanGeo, oceanMat);
  ocean.position.y = 0;
  ocean.receiveShadow = false;
  scene.add(ocean);

  function oceanWave(x, z, time) {
    const t = time * 0.55;
    const h1 = Math.sin(x * 0.18 + t * 0.9) * 0.28;
    const h2 = Math.sin(z * 0.24 - t * 0.7) * 0.18;
    const h3 = Math.sin((x * 0.35 + z * 0.3) + t * 1.3) * 0.10;
    return h1 + h2 + h3;
  }

  function updateOceanVertices(time) {
    const arr = oceanPositions.array;
    for (let i = 0; i < oceanBasePositions.length; i += 3) {
      const bx = oceanBasePositions[i];
      const bz = oceanBasePositions[i + 2];
      const y = oceanWave(bx, bz, time);
      arr[i + 1] = y;
    }
    oceanPositions.needsUpdate = true;
    oceanGeo.computeVertexNormals();
  }

  const skyDome = new THREE.Mesh(
    new THREE.SphereGeometry(200, 16, 12),
    new THREE.ShaderMaterial({
      side: THREE.BackSide,
      depthWrite: false,
      uniforms: {
        skyTop:     { value: new THREE.Color('#2a6ab0') },
        skyMid:     { value: new THREE.Color('#5a90c8') },
        skyHorizon: { value: new THREE.Color('#b8d0e0') },
        sunDir:     { value: new THREE.Vector3(-0.5, 0.5, -0.7).normalize() },
        sunColor:   { value: new THREE.Color('#ffffff') }
      },
      vertexShader: `
        varying vec3 vDir;
        void main(){
          vDir = position;
          gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
        }`,
      fragmentShader: `
        uniform vec3 skyTop;
        uniform vec3 skyMid;
        uniform vec3 skyHorizon;
        uniform vec3 sunDir;
        uniform vec3 sunColor;
        varying vec3 vDir;
        void main(){
          vec3 d = normalize(vDir);
          float h = max(d.y, 0.0);
          vec3 col;
          if (h < 0.35) col = mix(skyHorizon, skyMid, h / 0.35);
          else col = mix(skyMid, skyTop, (h - 0.35) / 0.65);
          float sunDot = max(dot(d, sunDir), 0.0);
          col += sunColor * pow(sunDot, 16.0) * 0.25;
          col += sunColor * pow(sunDot, 400.0) * 1.2;
          if (d.y < 0.0) col = mix(col, vec3(0.45, 0.5, 0.55), smoothstep(0.0, -0.3, d.y));
          gl_FragColor = vec4(col, 1.0);
        }`
    })
  );
  skyDome.name = 'Blue sky dome';
  scene.add(skyDome);

  const buoy = new THREE.Group();
  scene.add(buoy);

  const coast = createCoast();
  coast.group.visible = false;
  scene.add(coast.group);

  const bay = createBayStation(coast);
  let bayMove = null, bayOverview = null;

  function inspectBay(id) {
    if (currentChapter !== 5 || contextLost) return false;
    const pose = bay.focus(id, camera.aspect);
    if (!pose) return false;
    if (!bayOverview) {
      bayOverview = { eye: camera.position.clone(), aim: aim.clone() };
      bay.reveal(false);
    }
    bay.select(id);
    bayMove = {
      id, from: camera.position.clone(), fromAim: aim.clone(),
      eye: new THREE.Vector3(...pose.eye), aim: new THREE.Vector3(...pose.aim),
      elapsed: 0, ready: false
    };
    return true;
  }
  function returnToBay() {
    if (!bayOverview) return;
    bay.select(null);
    bayMove = { from: camera.position.clone(), fromAim: aim.clone(), ...bayOverview, elapsed: 0, ready: false, returning: true };
    bayOverview = null;
  }

  document.body.classList.add('coast-ready');
  const receiverLabel = document.querySelector('#coast-receiver-label');

  const markers = new Map(), hotspotLayer = document.querySelector('#hotspots');
  const leaderSvg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  leaderSvg.setAttribute('aria-hidden', 'true');
  hotspotLayer.append(leaderSvg);

  let pageOneTargets = new Map();
  const targetFor = id => (currentChapter === 1 || currentChapter === 2) ? pageOneTargets.get(id) : markers.get(id)?.target;

  let model, disposed = false, contextLost = false, yaw = 0, drag = null, orbitReset = null, needsDraw = true;
  let inspection = null, overview = null, hovered = null, tintKey = '';
  const materialCopies = [];
  const connection = document.querySelector('#inspection-wire path');

  function restoreMaterials() {
    for (const { mesh, original, copies } of materialCopies) {
      mesh.material = original;
      copies.forEach(m => m.dispose());
    }
    materialCopies.length = 0;
  }
  function tint(target, focused) {
    restoreMaterials();
    if (!model || !target) return;
    const selectedMeshes = new Set();
    target.traverse(o => { if (o.isMesh) selectedMeshes.add(o); });
    model.traverse(mesh => {
      if (!mesh.isMesh) return;
      const original = mesh.material;
      const copies = [].concat(original).map(m => {
        const copy = m.clone();
        if (selectedMeshes.has(mesh)) {
          if (copy.emissive) { copy.emissive.set('#48aebc'); copy.emissiveIntensity = focused ? .3 : .12; }
        } else if (focused && copy.color) { copy.color.multiplyScalar(.62); }
        return copy;
      });
      mesh.material = Array.isArray(original) ? copies : copies[0];
      materialCopies.push({ mesh, original, copies, selected: selectedMeshes.has(mesh) });
    });
    needsDraw = true;
  }

  function beginInspection(id) {
    if (contextLost || !markers.has(id)) return false;
    if (!overview) overview = { eye: camera.position.clone(), aim: aim.clone() };
    const target = targetFor(id);
    if (!target) return false;
    const bounds = new THREE.Box3().setFromObject(target);
    const center = bounds.getCenter(new THREE.Vector3());
    const size = bounds.getSize(new THREE.Vector3());
    const frame = inspectionFrame(center.toArray(), Math.max(size.x, size.y, size.z), camera.aspect, innerWidth < 650);
    inspection = {
      id, page: currentChapter,
      from: camera.position.clone(), fromAim: aim.clone(),
      eye: new THREE.Vector3().fromArray(frame.eye), aim: new THREE.Vector3().fromArray(frame.aim),
      elapsed: 0, returning: false, ready: false
    };
    drag = null;
    needsDraw = true;
    return true;
  }
  function returnToBuoy() {
    if (!overview) return;
    inspection = {
      id: inspection?.id, page: inspection?.page,
      from: camera.position.clone(), fromAim: aim.clone(),
      eye: overview.eye, aim: overview.aim,
      elapsed: 0, returning: true, ready: false
    };
    overview = null;
    hovered = null;
    needsDraw = true;
  }

  const projection = new THREE.Vector3(), box = new THREE.Box3();
  const compositionBounds = new THREE.Box3();
  function projectedBounds(bounds) {
    const result = { left: Infinity, right: -Infinity, top: Infinity, bottom: -Infinity };
    for (const x of [bounds.min.x, bounds.max.x])
      for (const y of [bounds.min.y, bounds.max.y])
        for (const z of [bounds.min.z, bounds.max.z]) {
          projection.set(x, y, z).project(camera);
          const px = (projection.x + 1) * innerWidth / 2;
          const py = (1 - projection.y) * innerHeight / 2;
          result.left = Math.min(result.left, px); result.right = Math.max(result.right, px);
          result.top = Math.min(result.top, py); result.bottom = Math.max(result.bottom, py);
        }
    return result;
  }

  const halo = new THREE.Mesh(
    new THREE.TorusGeometry(.035, .002, 6, 20),
    new THREE.MeshBasicMaterial({ color: '#e4c999', depthTest: false, transparent: true })
  );
  halo.visible = false;
  halo.renderOrder = 10;
  scene.add(halo);

  function disposeModel(root) {
    root.traverse(o => {
      if (o.isMesh) {
        o.geometry.dispose();
        for (const m of [].concat(o.material)) {
          for (const value of Object.values(m)) if (value?.isTexture) value.dispose();
          m.dispose();
        }
      }
    });
  }

  new GLTFLoader().load(modelUrl, gltf => {
    if (disposed) { disposeModel(gltf.scene); return; }
    model = gltf.scene;
    model.rotation.x = -Math.PI / 2;
    model.position.y = -2.65;
    // Presentation scale tuning
    model.scale.setScalar(1.35);
    buoy.add(model);
    buoy.updateMatrixWorld(true);
    pageOneTargets = instrumentTargets(model);

    model.traverse(node => {
      if (node.name === 'ANCHOR_MOORING_SYSTEM' ||
          (node.name && node.name.toUpperCase().includes('ANCHOR'))) {
        node.visible = false;
      }
    });

    for (const [id, c] of Object.entries(components)) {
      const prefix = id === 'esp32' ? 'REV5_RECTANGULAR_MARINE_ELECTRONICS_POD' : c.prefix;
      let target;
      model.traverse(o => { if (!target && o.name.toUpperCase().startsWith(prefix)) target = o; });
      if (!target) continue;
      const button = document.createElement('button');
      button.className = 'hotspot';
      button.textContent = c.label;
      button.dataset.component = id;
      button.dataset.index = String(Object.keys(components).indexOf(id) + 1).padStart(2, '0');
      button.setAttribute('aria-label', c.label);
      button.setAttribute('aria-pressed', 'false');
      button.addEventListener('click', () => onPick(id));
      hotspotLayer.append(button);
      markers.set(id, { target, button });
    }
    onStatus('Original V2 CAD · motion / waterline illustrative');
  }, undefined, () => {
    onStatus('Original CAD failed to load · no substitute model used');
    document.body.classList.add('webgl-unavailable');
  });

  const raycaster = new THREE.Raycaster();
  let currentChapter = 0;
  const homeOrbit = createHomeOrbit();

  const down = e => {
    if (homeOrbit.active && currentChapter === 0) { drag = { last: e.clientX, lastY: e.clientY }; return; }
    if (currentChapter === 5 || (!inspection && (currentChapter === 1 || currentChapter === 2))) {
      orbitReset = null;
      drag = { x: e.clientX, y: e.clientY, last: e.clientX, distance: 0 };
    }
  };
  const move = e => {
    if (!drag) return;
    if (homeOrbit.active && currentChapter === 0) {
      homeOrbit.drag(e.clientX - drag.last, e.clientY - drag.lastY);
      drag.last = e.clientX; drag.lastY = e.clientY;
      needsDraw = true; return;
    }
    if (e.pointerType === 'touch') return;
    const delta = e.clientX - drag.last;
    drag.distance += Math.abs(delta);
    if (currentChapter !== 5) yaw += delta * .005;
    drag.last = e.clientX;
  };
  const up = e => {
    if (!drag) return;
    if (homeOrbit.active && currentChapter === 0) { drag = null; return; }
    const distance = Math.hypot(e.clientX - drag.x, e.clientY - drag.y) + drag.distance;
    drag = null;
    if (distance > 8) return;
    raycaster.setFromCamera(new THREE.Vector2(e.clientX / innerWidth * 2 - 1, 1 - e.clientY / innerHeight * 2), camera);
    if (currentChapter === 5) { const id = bay.pick(raycaster); if (id) onBayPick(id); return; }
    if (!model) return;
    for (const hit of raycaster.intersectObject(model, true)) {
      let object = hit.object;
      while (object) {
        const id = Object.keys(components).find(key => object === targetFor(key));
        if (id) { onPick(id); return; }
        object = object.parent;
      }
    }
  };
  renderer.domElement.addEventListener('pointerdown', down);
  window.addEventListener('pointermove', move);
  window.addEventListener('pointerup', up);

  const wheel = e => {
    if (currentChapter === 0 && homeOrbit.active) {
      e.preventDefault();
      homeOrbit.zoom(e.deltaY * (e.deltaMode === 1 ? 16 : e.deltaMode === 2 ? innerHeight : 1));
      needsDraw = true;
    }
  };
  renderer.domElement.addEventListener('wheel', wheel, { passive: false });

  const cancel = () => { drag = null; };
  window.addEventListener('pointercancel', cancel);

  const reset = () => { orbitReset = { from: yaw, elapsed: 0 }; };
  document.querySelector('#reset-camera').addEventListener('click', reset);

  const resize = () => {
    renderer.setSize(innerWidth, innerHeight);
    camera.aspect = innerWidth / innerHeight;
    camera.updateProjectionMatrix();
    if (inspection?.id && !inspection.returning) beginInspection(inspection.id);
    if (bayMove?.id && !bayMove.returning) inspectBay(bayMove.id);
    needsDraw = true;
  };
  resize();
  window.addEventListener('resize', resize);

  const lost = e => { e.preventDefault(); contextLost = true; onStatus('3D paused by device · reload to restore'); document.body.classList.add('webgl-unavailable'); };
  renderer.domElement.addEventListener('webglcontextlost', lost);

  const desiredEye = new THREE.Vector3(), desiredAim = new THREE.Vector3();
  const nextEye = new THREE.Vector3(), nextAim = new THREE.Vector3();
  let lastProgress = -1, lastPick = '', lastYaw = -1, lastLink = true;

  return {
    setHomeOrbit(enabled) {
      if (enabled) { if (currentChapter !== 0 || !model || contextLost) return false; homeOrbit.enter(camera.position.toArray()); }
      else homeOrbit.exit();
      drag = null; needsDraw = true; return true;
    },
    moveHomeOrbit(dx, dy, zoom = 0) {
      if (currentChapter === 0 && homeOrbit.active) { homeOrbit.drag(dx, dy); homeOrbit.zoom(zoom); needsDraw = true; }
    },
    inspectBay, returnToBay,
    inspect: beginInspection,
    returnToBuoy,
    hover(id) { hovered = id; needsDraw = true; },

    update({ progress, chapter, time, dt, moving, pointer, selected, linkOnline = true, homeProgress = 0 }) {
      if (disposed || contextLost) return;
      currentChapter = chapter;
      if (chapter !== 0) homeOrbit.exit();
      if (chapter !== 5 && (bayMove || bayOverview)) { bayMove = null; bayOverview = null; bay.select(null); }

      if (orbitReset) {
        orbitReset.elapsed += dt;
        const t = moving ? Math.min(1, orbitReset.elapsed / 1.2) : 1;
        yaw = orbitReset.from * (1 - easeInspection(t));
        if (t === 1) orbitReset = null;
        needsDraw = true;
      }

      const a = Math.max(0, Math.min(9, Math.floor(progress)));
      const b = Math.min(9, a + 1);
      const t = THREE.MathUtils.smoothstep(progress - a, 0, 1);
      desiredEye.fromArray(poses[a].eye).lerp(nextEye.fromArray(poses[b].eye), t);
      desiredAim.fromArray(poses[a].aim).lerp(nextAim.fromArray(poses[b].aim), t);

      if (progress < 1) { const shot = homeCamera(homeProgress); desiredEye.fromArray(shot.eye); desiredAim.fromArray(shot.aim); }

      if (progress >= 4 && progress < 6) {
        const p = Math.min(3, (progress - 4) * 2);
        const i = Math.floor(p), j = Math.min(3, i + 1);
        const u = THREE.MathUtils.smoothstep(p - i, 0, 1);
        desiredEye.fromArray(coastCamera[i].eye).lerp(nextEye.fromArray(coastCamera[j].eye), u);
        desiredAim.fromArray(coastCamera[i].aim).lerp(nextAim.fromArray(coastCamera[j].aim), u);
        if (progress > 5.75) {
          const blend = THREE.MathUtils.smoothstep(progress, 5.75, 6);
          desiredEye.lerp(nextEye.fromArray(poses[6].eye), blend);
          desiredAim.lerp(nextAim.fromArray(poses[6].aim), blend);
        }
      }

      if (chapter === 4) {
        const p = Math.min(2, (progress - 4) * 2);
        const i = Math.min(1, Math.floor(p));
        const u = THREE.MathUtils.smoothstep(p - i, 0, 1);
        desiredEye.fromArray(crossingCamera[i].eye).lerp(nextEye.fromArray(crossingCamera[i + 1].eye), u);
        desiredAim.fromArray(crossingCamera[i].aim).lerp(nextAim.fromArray(crossingCamera[i + 1].aim), u);
        if (innerWidth < 650) {
          const wide = 1 + .9 * (1 - THREE.MathUtils.smoothstep(progress, 4.65, 5));
          desiredEye.sub(desiredAim).multiplyScalar(wide).add(desiredAim);
        }
      }

      if (innerWidth < 650) { desiredEye.multiplyScalar(1.25); desiredAim.x += .45; desiredAim.y += .35; }
      if (innerWidth < 650 && progress < 1) desiredAim.y += (1 - homeProgress) * desiredEye.distanceTo(desiredAim) * .16;

      if (innerWidth < 650 && progress >= 1 && progress < 3) {
        const weight = THREE.MathUtils.smoothstep(progress, 1, 1.25) * (1 - THREE.MathUtils.smoothstep(progress, 2.65, 3));
        desiredEye.lerp(nextEye.set(3.8, 1.8, 6), weight);
        desiredAim.lerp(nextAim.set(0, 1.15, 0), weight);
      }

      if (moving) { desiredEye.x += pointer.x * .1; desiredEye.y += pointer.y * .06; }

      if (chapter === 0 && homeOrbit.active) {
        const pose = homeOrbit.update(dt);
        desiredEye.fromArray(pose.eye);
        desiredAim.fromArray(pose.aim);
        needsDraw = true;
      }

      const blend = moving ? cameraBlend(dt) : 1;

      if (chapter === 5 && bayMove) {
        bayMove.elapsed += dt;
        const t2 = moving ? Math.min(1, bayMove.elapsed / 1.65) : 1;
        const u = easeInspection(t2);
        camera.position.lerpVectors(bayMove.from, bayMove.eye, u);
        aim.lerpVectors(bayMove.fromAim, bayMove.aim, u);
        if (t2 === 1 && !bayMove.ready) {
          bayMove.ready = true;
          if (bayMove.returning) bayMove = null;
          else { bay.reveal(true); onBayReady(); }
        }
        needsDraw = true;
      } else if (inspection) {
        if (inspection.page !== chapter) { inspection = null; overview = null; }
        else {
          inspection.elapsed += dt;
          const t2 = moving ? Math.min(1, inspection.elapsed / 1.65) : 1;
          const eased = easeInspection(t2);
          camera.position.lerpVectors(inspection.from, inspection.eye, eased);
          aim.lerpVectors(inspection.fromAim, inspection.aim, eased);
          if (t2 === 1 && !inspection.ready) {
            inspection.ready = true;
            if (inspection.returning) inspection = null;
            else onInspectionReady();
          }
          needsDraw = true;
        }
      } else {
        camera.position.lerp(desiredEye, blend);
        aim.lerp(desiredAim, blend);
      }

      camera.lookAt(aim);
      buoy.rotation.y = yaw;

      // HIDE BUOY in Ch03 (Controller) — SVG + text lang
      buoy.visible = (chapter !== 3);

      if (moving || chapter === 0) {
        updateOceanVertices(time);
      }

      // Ocean opacity per chapter — Ch03 consistent with Ch01
      let oceanOpacity = 1;
      if (inspection?.id === 'pressure') oceanOpacity = 0.12;
      else if (chapter === 2) oceanOpacity = 0.62;
      else if (chapter === 7 || chapter === 8 || chapter === 9) oceanOpacity = 0.15;
      oceanMat.opacity = oceanOpacity;
      ocean.visible = oceanOpacity > 0.01;

      skyDome.position.copy(camera.position);

      sun.position.set(camera.position.x - 18, 20, camera.position.z + 14);
      sun.target.position.set(camera.position.x, 0, camera.position.z);
      sun.target.updateMatrixWorld();

      const motion = buoyMotion(time);
      buoy.position.y = motion.heave;
      buoy.rotation.z = motion.roll;
      buoy.rotation.x = motion.pitch;

      buoy.updateMatrixWorld(true);
      camera.updateMatrixWorld(true);

      compositionBounds.makeEmpty();
      if (chapter < 3) for (const target of pageOneTargets.values()) compositionBounds.union(box.setFromObject(target));

      const coastVisible = progress >= 3.65 && progress < 6.15;
      coast.update(time, linkOnline, camera, coastVisible, chapter === 4, chapter === 5);
      bay.update(time, linkOnline, chapter === 5);

      if (receiverLabel) {
        projection.set(...RECEIVER).project(camera);
        const x = (projection.x * .5 + .5) * innerWidth;
        const y = (-projection.y * .5 + .5) * innerHeight;
        receiverLabel.hidden = !coastVisible || projection.z > 1 || x < 0 || x > innerWidth - 110 || y < 110 || y > innerHeight - 100;
        receiverLabel.style.left = `${x}px`;
        receiverLabel.style.top = `${y - 25}px`;
        receiverLabel.textContent = linkOnline ? 'LoRa RX · BAY STATION' : 'LoRa RX · LINK INTERRUPTED';
      }

      const visible = chapter === 1 || chapter === 2;
      hotspotLayer.hidden = !visible;

      const occupied = [];
      const obstacles = [...document.querySelectorAll('header,.journey-nav,.model-state,#buoy.is-active .copy,#sensors.is-active .copy,.cad-caption,.source-caption,#inspection-panel:not([hidden])')].filter(e => e.getClientRects().length && getComputedStyle(e).visibility !== 'hidden').map(e => e.getBoundingClientRect());
      const silhouette = compositionBounds.isEmpty() ? { left: 0, right: innerWidth } : projectedBounds(compositionBounds);

      leaderSvg.replaceChildren();
      for (const [id, { button }] of markers) {
        const target = targetFor(id);
        box.setFromObject(target).getCenter(projection);
        projection.project(camera);
        const x = (projection.x * .5 + .5) * innerWidth;
        const y = (-projection.y * .5 + .5) * innerHeight;
        const placement = visible && !inspection && projection.z < 1 && projection.z > -1
          ? placeCallout({ x, y }, silhouette, [...obstacles, ...occupied], { left: 24, right: innerWidth - 24, top: 115, bottom: innerHeight - 105 })
          : null;
        button.hidden = !placement;
        button.setAttribute('aria-pressed', String(id === selected));
        if (placement) {
          button.style.left = `${placement.x}px`;
          button.style.top = `${placement.y}px`;
          occupied.push(placement.rect);
          const line = document.createElementNS('http://www.w3.org/2000/svg', 'path');
          line.setAttribute('d', placement.path);
          leaderSvg.append(line);
        }
      }

      const focused = inspection?.id;
      const chosenTarget = targetFor(focused || hovered || selected);
      const chosen = chosenTarget ? { target: chosenTarget } : null;
      halo.visible = visible && !!chosen;

      const nextTint = visible ? (focused || hovered || '') + (focused ? ':focus' : '') + chapter : '';
      if (nextTint !== tintKey) { tintKey = nextTint; tint(targetFor(focused || hovered), !!focused); }
      halo.material.opacity = 1;
      if (focused) {
        const ramp = moving ? easeInspection(inspection.elapsed / 1.65) : 1;
        const strength = inspection.returning ? 1 - ramp : ramp;
        halo.material.opacity = strength;
        for (const entry of materialCopies) entry.copies.forEach((m, i) => {
          const original = [].concat(entry.original)[i];
          if (!entry.selected && m.color) m.color.copy(original.color).multiplyScalar(1 - .38 * strength);
          if (entry.selected && m.emissive) m.emissiveIntensity = .3 * strength;
        });
      }
      halo.material.color.set(focused || hovered ? '#70c7d2' : '#e4c999');
      halo.scale.setScalar(focused ? (1.15 + (moving ? Math.sin(time * 2.2) * .12 : 0)) : 1);
      if (chosen) { box.setFromObject(chosen.target).getCenter(halo.position); halo.quaternion.copy(camera.quaternion); }

      if (focused && !inspection.returning && inspection.ready && chosen) {
        projection.copy(halo.position).project(camera);
        const x = (projection.x * .5 + .5) * innerWidth;
        const y = (-projection.y * .5 + .5) * innerHeight;
        const rect = document.querySelector('#inspection-panel').getBoundingClientRect();
        const endX = innerWidth < 650 ? rect.left + rect.width * .5 : rect.left;
        const endY = innerWidth < 650 ? rect.top : rect.top + 110;
        connection.setAttribute('d', `M${x},${y} L${(x + endX) * .5},${y} L${endX},${endY}`);
      } else if (chapter === 2 && chosen && !inspection) {
        projection.copy(halo.position).project(camera);
        const rect = document.querySelector('#acquisition-signal').getBoundingClientRect();
        const x = (projection.x * .5 + .5) * innerWidth;
        const y = (-projection.y * .5 + .5) * innerHeight;
        connection.setAttribute('d', projection.z < 1 && x > 0 && x < innerWidth && rect.top > 90 && rect.top < innerHeight - 80
          ? `M${x},${y} L${rect.left - 22},${y} L${rect.left},${rect.top + 35}` : '');
      } else connection.setAttribute('d', '');

      needsDraw = moving || lastLink !== linkOnline || lastProgress !== progress || lastPick !== selected || lastYaw !== yaw || camera.position.distanceTo(desiredEye) > .001 || needsDraw;
      if (needsDraw) renderer.render(scene, camera);
      needsDraw = false;
      lastProgress = progress;
      lastPick = selected;
      lastYaw = yaw;
      lastLink = linkOnline;
    },

    dispose() {
      disposed = true;
      restoreMaterials();
      bay.dispose();
      coast.dispose();
      window.removeEventListener('resize', resize);
      window.removeEventListener('pointermove', move);
      window.removeEventListener('pointerup', up);
      window.removeEventListener('pointercancel', cancel);
      document.querySelector('#reset-camera').removeEventListener('click', reset);
      if (model) disposeModel(model);
      oceanGeo.dispose();
      oceanMat.dispose();
      skyDome.geometry.dispose();
      skyDome.material.dispose();
      halo.geometry.dispose();
      halo.material.dispose();
      renderer.dispose();
      renderer.domElement.remove();
      hotspotLayer.replaceChildren();
    }
  };
}