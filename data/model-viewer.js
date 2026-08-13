import * as THREE from "three";
import {GLTFLoader} from "/vendor/GLTFLoader.js?v=1";

const canvas = document.getElementById("buoy3dCanvas");
const container = document.getElementById("buoyScene");
const loadState = document.getElementById("modelLoadState");
const diagnosticCallout = document.getElementById("diagnosticCallout");

if (canvas && container) {
  const renderer = new THREE.WebGLRenderer({canvas, alpha: true, antialias: true, powerPreference: "high-performance"});
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.15;

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(34, 1, .01, 100);
  camera.position.set(2.65, 1.7, 3.4);
  camera.lookAt(0, .05, 0);
  const orbit = {yaw: .66, pitch: .36, distance: 4.62, targetYaw: .66, targetPitch: .36, targetDistance: 4.62};
  const cameraTarget = new THREE.Vector3(0, .05, 0);
  let pointer = null;

  canvas.addEventListener("pointerdown", (event) => {
    pointer = {id: event.pointerId, x: event.clientX, y: event.clientY};
    canvas.setPointerCapture(event.pointerId);
    canvas.classList.add("is-dragging");
  });
  canvas.addEventListener("pointermove", (event) => {
    if (!pointer || pointer.id !== event.pointerId) return;
    orbit.targetYaw -= (event.clientX - pointer.x) * .008;
    orbit.targetPitch = THREE.MathUtils.clamp(orbit.targetPitch + (event.clientY - pointer.y) * .006, -.18, 1.18);
    pointer.x = event.clientX;
    pointer.y = event.clientY;
  });
  function releasePointer(event) {
    if (!pointer || pointer.id !== event.pointerId) return;
    pointer = null;
    canvas.classList.remove("is-dragging");
  }
  canvas.addEventListener("pointerup", releasePointer);
  canvas.addEventListener("pointercancel", releasePointer);
  canvas.addEventListener("wheel", (event) => {
    event.preventDefault();
    orbit.targetDistance = THREE.MathUtils.clamp(orbit.targetDistance + event.deltaY * .003, 2.7, 7.2);
  }, {passive: false});
  canvas.addEventListener("dblclick", () => {
    orbit.targetYaw = .66;
    orbit.targetPitch = .36;
    orbit.targetDistance = 4.62;
  });

  scene.add(new THREE.HemisphereLight(0xc7fff4, 0x082124, 2.4));
  const keyLight = new THREE.DirectionalLight(0xffffff, 3.2);
  keyLight.position.set(3, 5, 4);
  scene.add(keyLight);
  const rimLight = new THREE.DirectionalLight(0x50e3c2, 2.1);
  rimLight.position.set(-4, 2, -3);
  scene.add(rimLight);

  // Telemetry-driven sea surface. It stays in world space while the buoy
  // responds independently, which makes the heave and tilt readable.
  const seaGeometry = new THREE.PlaneGeometry(12, 12, 72, 72);
  seaGeometry.rotateX(-Math.PI / 2);
  const seaPositions = seaGeometry.attributes.position;
  const seaBase = new Float32Array(seaPositions.array);
  const seaMaterial = new THREE.MeshPhongMaterial({
    color: 0x087681,
    emissive: 0x052d35,
    emissiveIntensity: .55,
    specular: 0x9bfff0,
    shininess: 105,
    transparent: true,
    opacity: .64,
    side: THREE.DoubleSide,
    depthWrite: false,
  });
  const SEA_LEVEL = -.58;
  const BUOY_FREEBOARD = .72;
  const sea = new THREE.Mesh(seaGeometry, seaMaterial);
  sea.position.y = SEA_LEVEL;
  sea.renderOrder = 2;
  scene.add(sea);

  const rippleGeometry = seaGeometry.clone();
  const rippleMaterial = new THREE.MeshBasicMaterial({color: 0x55dccd, transparent: true, opacity: .13, wireframe: true, depthWrite: false});
  const seaRipples = new THREE.Mesh(rippleGeometry, rippleMaterial);
  seaRipples.position.y = SEA_LEVEL + .015;
  seaRipples.renderOrder = 3;
  scene.add(seaRipples);

  const foamMaterial = new THREE.MeshBasicMaterial({color: 0xc8fff7, transparent: true, opacity: .2, side: THREE.DoubleSide, depthWrite: false});
  const foamRing = new THREE.Mesh(new THREE.RingGeometry(.34, .39, 64), foamMaterial);
  foamRing.rotation.x = -Math.PI / 2;
  foamRing.position.y = SEA_LEVEL + .025;
  foamRing.renderOrder = 4;
  scene.add(foamRing);

  const poseRoot = new THREE.Group();
  const normalizedRoot = new THREE.Group();
  poseRoot.add(normalizedRoot);
  scene.add(poseRoot);

  const indicatorGroup = new THREE.Group();
  poseRoot.add(indicatorGroup);
  const warningLight = new THREE.PointLight(0xf47d78, 0, 2.5);
  warningLight.position.set(0, .82, .12);
  poseRoot.add(warningLight);

  const telemetry = {roll: 0, pitch: 0, yaw: 42, wave: .4, rough: false, fault: false, scenario: "normal", battery: 87, enclosureTemperature: 34.2, batteryTemperature: 31.7};
  const diagnosticMeshes = [];
  const diagnosticParts = {};
  let modelReady = false;

  function prepareDiagnosticPart(model, key, names) {
    const part = names.map((name) => model.getObjectByName(name)).find(Boolean);
    if (!part) return;
    const meshes = [];
    part.traverse((object) => {
      if (!object.isMesh || !object.material) return;
      if (Array.isArray(object.material)) object.material = object.material.map((material) => material.clone());
      else object.material = object.material.clone();
      const materials = Array.isArray(object.material) ? object.material : [object.material];
      materials.forEach((material) => {
        if (!material.emissive) return;
        material.userData.baseEmissive = material.emissive.getHex();
        material.userData.baseEmissiveIntensity = material.emissiveIntensity;
        meshes.push(material);
      });
    });
    diagnosticParts[key] = meshes;
    diagnosticMeshes.push(...meshes);
  }

  function highlightPart(key, severity) {
    const color = severity === "critical" ? 0xff302c : 0xffa62b;
    (diagnosticParts[key] || []).forEach((material) => {
      material.userData.diagnosticSeverity = severity;
      material.emissive.setHex(color);
    });
  }

  function updateDiagnostics() {
    diagnosticMeshes.forEach((material) => {
      material.userData.diagnosticSeverity = null;
      material.emissive.setHex(material.userData.baseEmissive);
      material.emissiveIntensity = material.userData.baseEmissiveIntensity;
    });
    let message = "ALL COMPONENTS NORMAL";
    let level = "healthy";
    if (telemetry.scenario === "sensor_fault") {
      highlightPart("sensorArray", "critical");
      message = "SENSOR FAULT · TOP SENSOR ARRAY OFFLINE";
      level = "critical";
    } else if (telemetry.scenario === "overheating" || telemetry.enclosureTemperature >= 50) {
      highlightPart("electronics", "critical");
      highlightPart("intakeFan", "warning");
      highlightPart("exhaustFan", "warning");
      message = `THERMAL ALERT · ELECTRONICS ${telemetry.enclosureTemperature.toFixed(1)}°C`;
      level = "critical";
    } else if (telemetry.scenario === "low_battery" || telemetry.battery <= 30) {
      const severity = telemetry.battery <= 15 ? "critical" : "warning";
      highlightPart("electronics", severity);
      message = `POWER ${severity === "critical" ? "CRITICAL" : "WARNING"} · BATTERY ${Math.round(telemetry.battery)}%`;
      level = severity;
    }
    if (diagnosticCallout) {
      diagnosticCallout.textContent = message;
      diagnosticCallout.className = `diagnostic-callout is-${level}`;
    }
  }

  new GLTFLoader().load("/models/FALCON-01.glb?v=3", (gltf) => {
    const model = gltf.scene;
    // Fusion exports this assembly Z-up; Three.js scenes are Y-up.
    model.rotation.x = -Math.PI / 2;
    model.updateMatrixWorld(true);
    model.traverse((object) => {
      const componentName = object.name.toUpperCase();
      if (componentName.startsWith("ANCHOR_MOORING_SYSTEM")) object.visible = false;
      if (object.isMesh) {
        object.castShadow = false;
        object.receiveShadow = false;
        if (object.material) object.material.side = THREE.DoubleSide;
      }
    });
    const anchorSystem = model.getObjectByName("ANCHOR_MOORING_SYSTEM:2") || model.getObjectByName("ANCHOR_MOORING_SYSTEM");
    if (anchorSystem?.parent) anchorSystem.parent.remove(anchorSystem);
    model.updateMatrixWorld(true);
    const bounds = new THREE.Box3().setFromObject(model);
    const size = bounds.getSize(new THREE.Vector3());
    const center = bounds.getCenter(new THREE.Vector3());
    const maximumDimension = Math.max(size.x, size.y, size.z, .001);
    const scale = 2.72 / maximumDimension;
    model.scale.setScalar(scale);
    model.position.copy(center).multiplyScalar(-scale);
    normalizedRoot.add(model);
    scene.updateMatrixWorld(true);

    prepareDiagnosticPart(model, "sensorArray", ["TOP_SENSOR_ARRAY:3", "TOP_SENSOR_ARRAY"]);
    prepareDiagnosticPart(model, "electronics", ["ELECTRONICS_BOX_V3:2", "ELECTRONICS_BOX_V3"]);
    prepareDiagnosticPart(model, "intakeFan", ["INTAKE_FAN_MODULE:2", "INTAKE_FAN_MODULE"]);
    prepareDiagnosticPart(model, "exhaustFan", ["EXHAUST_FAN_MODULE:2", "EXHAUST_FAN_MODULE"]);

    const lightTargets = [
      ["GNSS_GPS_ANTENNA", 0x76dda5],
      ["LTE_4G_ANTENNA", 0x50e3c2],
      ["WIFI_ANTENNA", 0xf2b96d],
      ["NAVIGATION_LIGHT_CLEAR_LED_LENS", 0xf47d78],
    ];
    lightTargets.forEach(([targetName, color]) => {
      const target = model.getObjectByName(targetName) || model.getObjectByName(`${targetName}:1`);
      if (!target) return;
      const point = target.getWorldPosition(new THREE.Vector3());
      poseRoot.worldToLocal(point);
      const material = new THREE.MeshBasicMaterial({color, transparent: true, toneMapped: false});
      const indicator = new THREE.Mesh(new THREE.SphereGeometry(.032, 14, 10), material);
      indicator.position.copy(point);
      indicator.userData.baseColor = color;
      indicatorGroup.add(indicator);
      if (targetName.startsWith("NAVIGATION_LIGHT")) warningLight.position.copy(point);
    });
    modelReady = true;
    updateDiagnostics();
    container.classList.add("has-cad-model");
    container.classList.remove("model-load-error");
    if (loadState) loadState.textContent = "FUSION CAD · LIVE";
  }, (event) => {
    if (!loadState || !event.total) return;
    const percent = Math.min(99, Math.round((event.loaded / event.total) * 100));
    loadState.textContent = `LOADING FUSION MODEL · ${percent}%`;
  }, (error) => {
    console.error("Unable to load the FALCON Fusion CAD model.", error);
    container.classList.add("model-load-error");
    container.classList.remove("has-cad-model");
    if (loadState) loadState.textContent = "FUSION CAD LOAD FAILED";
  });

  function resize() {
    const width = Math.max(1, container.clientWidth);
    const height = Math.max(1, container.clientHeight);
    renderer.setSize(width, height, false);
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
  }
  new ResizeObserver(resize).observe(container);
  resize();

  const clock = new THREE.Clock();
  let previousElapsed = 0;
  let wavePhase = 0;
  let seaFrame = 0;
  const motion = {roll: 0, pitch: 0, yaw: 42, wave: .4, roughMix: 0};
  function waveSurfaceAt(x,z,phase,amplitude,detail){
    return Math.sin(x*.72+phase)*amplitude
      + Math.sin(z*.92-phase*.72+x*.18)*amplitude*.58
      + Math.sin((x+z)*2.35+phase*2.05)*detail;
  }
  function animate() {
    requestAnimationFrame(animate);
    const elapsed = clock.getElapsedTime();
    const delta = Math.min(.05, Math.max(.001, elapsed - previousElapsed));
    previousElapsed = elapsed;
    motion.roll = THREE.MathUtils.damp(motion.roll, telemetry.roll, 1.35, delta);
    motion.pitch = THREE.MathUtils.damp(motion.pitch, telemetry.pitch, 1.35, delta);
    motion.yaw = THREE.MathUtils.damp(motion.yaw, telemetry.yaw, 1.1, delta);
    motion.wave = THREE.MathUtils.damp(motion.wave, telemetry.wave, .9, delta);
    motion.roughMix = THREE.MathUtils.damp(motion.roughMix, telemetry.rough ? 1 : 0, .75, delta);
    const waveEnergy = THREE.MathUtils.clamp(motion.wave, .1, 3.5);
    const motionRate = THREE.MathUtils.lerp(1.05, 1.55, motion.roughMix);
    wavePhase += delta * motionRate;
    const seaAmplitude = THREE.MathUtils.lerp(.035, .22, THREE.MathUtils.clamp(waveEnergy / 3.5, 0, 1));
    const roughDetail = THREE.MathUtils.lerp(.005, .045, motion.roughMix);
    for(let index=0;index<seaPositions.count;index++){
      const offset=index*3,x=seaBase[offset],z=seaBase[offset+2];
      seaPositions.setY(index,waveSurfaceAt(x,z,wavePhase,seaAmplitude,roughDetail));
    }
    seaPositions.needsUpdate=true;
    rippleGeometry.attributes.position.array.set(seaPositions.array);
    rippleGeometry.attributes.position.needsUpdate=true;
    if((seaFrame++%3)===0)seaGeometry.computeVertexNormals();
    seaMaterial.opacity=THREE.MathUtils.lerp(.58,.73,motion.roughMix);
    rippleMaterial.opacity=THREE.MathUtils.lerp(.09,.22,motion.roughMix);
    seaRipples.position.x=Math.sin(wavePhase*.35)*.035;
    seaRipples.position.z=Math.cos(wavePhase*.28)*.035;
    const surfaceBelowBuoy=waveSurfaceAt(poseRoot.position.x,poseRoot.position.z,wavePhase,seaAmplitude,roughDetail);
    foamRing.position.set(poseRoot.position.x,SEA_LEVEL+surfaceBelowBuoy+.025,poseRoot.position.z);
    foamRing.scale.setScalar(1+Math.sin(wavePhase*1.2)*.07+motion.roughMix*.12);
    foamMaterial.opacity=THREE.MathUtils.lerp(.16,.38,motion.roughMix)*(.82+Math.sin(wavePhase*2.1)*.18);
    container.classList.toggle("is-rough",motion.roughMix>.45);
    const floatHeave=SEA_LEVEL+surfaceBelowBuoy+BUOY_FREEBOARD;
    const surge = Math.sin(wavePhase * .52 + .6) * (.006 + waveEnergy * .006);
    const sway = Math.sin(wavePhase * .68 + 2.1) * (.008 + waveEnergy * .007);
    const rollTarget = -motion.roll
      + Math.sin(wavePhase * .78 + .25) * (1.1 + waveEnergy * 1.15)
      + Math.sin(wavePhase * 1.31 + 1.8) * (.25 + waveEnergy * .28);
    const pitchTarget = motion.pitch
      + Math.sin(wavePhase * .61 + 1.15) * (.75 + waveEnergy * .82)
      + Math.sin(wavePhase * 1.17 + .4) * (.18 + waveEnergy * .2);
    const yawTarget = motion.yaw + Math.sin(wavePhase * .24) * (.35 + waveEnergy * .28);
    const damping = THREE.MathUtils.lerp(2.6, 2.15, motion.roughMix);
    poseRoot.position.x = THREE.MathUtils.damp(poseRoot.position.x, sway, damping, delta);
    poseRoot.position.y = THREE.MathUtils.damp(poseRoot.position.y, floatHeave, THREE.MathUtils.lerp(3.2,2.35,motion.roughMix), delta);
    poseRoot.position.z = THREE.MathUtils.damp(poseRoot.position.z, surge, damping, delta);
    poseRoot.rotation.x = THREE.MathUtils.damp(poseRoot.rotation.x, THREE.MathUtils.degToRad(pitchTarget), damping, delta);
    poseRoot.rotation.z = THREE.MathUtils.damp(poseRoot.rotation.z, THREE.MathUtils.degToRad(rollTarget), damping, delta);
    poseRoot.rotation.y = THREE.MathUtils.damp(poseRoot.rotation.y, THREE.MathUtils.degToRad(yawTarget), 1.8, delta);
    orbit.yaw = THREE.MathUtils.damp(orbit.yaw, orbit.targetYaw, 10, delta);
    orbit.pitch = THREE.MathUtils.damp(orbit.pitch, orbit.targetPitch, 10, delta);
    orbit.distance = THREE.MathUtils.damp(orbit.distance, orbit.targetDistance, 10, delta);
    const horizontalDistance = orbit.distance * Math.cos(orbit.pitch);
    camera.position.set(
      horizontalDistance * Math.sin(orbit.yaw),
      cameraTarget.y + orbit.distance * Math.sin(orbit.pitch),
      horizontalDistance * Math.cos(orbit.yaw),
    );
    camera.lookAt(cameraTarget);
    const pulse = .45 + Math.sin(elapsed * (telemetry.fault ? 12 : 3)) * .35;
    indicatorGroup.children.forEach((indicator, index) => {
      indicator.material.color.setHex(telemetry.fault && index === 2 ? 0xf47d78 : indicator.userData.baseColor);
      indicator.material.opacity = Math.max(.2, pulse + index * .08);
      indicator.material.transparent = true;
    });
    warningLight.intensity = telemetry.rough || telemetry.fault ? Math.max(0, Math.sin(elapsed * 8)) * 5 : 0;
    diagnosticMeshes.forEach((material) => {
      if (!material.userData.diagnosticSeverity) return;
      const rate = material.userData.diagnosticSeverity === "critical" ? 7 : 3.5;
      material.emissiveIntensity = .75 + Math.max(0, Math.sin(elapsed * rate)) * 2.4;
    });
    if (modelReady) renderer.render(scene, camera);
  }
  animate();

  window.falconDigitalTwin = {
    setTelemetry(next) {
      Object.assign(telemetry, next);
      if (modelReady) updateDiagnostics();
    }
  };
}
