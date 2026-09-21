// Buoy motion synced to world.js CPU waves.
// Must match oceanWave() in world.js

function oceanWave(x, z, time) {
  const t = time * 0.55;
  const h1 = Math.sin(x * 0.18 + t * 0.9) * 0.28;
  const h2 = Math.sin(z * 0.24 - t * 0.7) * 0.18;
  const h3 = Math.sin((x * 0.35 + z * 0.3) + t * 1.3) * 0.10;
  return h1 + h2 + h3;
}

function waveSlope(x, z, time) {
  const t = time * 0.55;
  // Partial derivatives of oceanWave
  const dx =
    Math.cos(x * 0.18 + t * 0.9) * 0.18 * 0.28 +
    Math.cos((x * 0.35 + z * 0.3) + t * 1.3) * 0.35 * 0.10;
  const dz =
    Math.cos(z * 0.24 - t * 0.7) * 0.24 * 0.18 +
    Math.cos((x * 0.35 + z * 0.3) + t * 1.3) * 0.30 * 0.10;
  return { dx, dz };
}

export function buoyMotion(time) {
  const x = 0, z = 0;  // buoy position
  const heave = oceanWave(x, z, time);
  const slope = waveSlope(x, z, time);

  return {
    heave,
    pitch: Math.max(-0.06, Math.min(0.06, -slope.dz * 0.8)),
    roll:  Math.max(-0.06, Math.min(0.06,  slope.dx * 0.8))
  };
}

export const cameraBlend = dt => 1 - Math.exp(-Math.max(0, dt) * 5);