// =============================================================
// FALCON-01 — Story data
// 12-section structure aligned with main.js SECTION_NAMES
// =============================================================

export const chapters = [
  'Opening',
  'Challenge',
  'Solution',
  'Architecture',
  'Buoy',
  'How it works',
  'Bay Station',
  'Dashboard',
  'AI',
  'Validation',
  'Future',
  'Final'
];

// ---- CAD component definitions (used by world.js + main.js) ----
export const components = {
  pressure: {
    label: 'Underwater pressure',
    prefix: 'WATER_PRESSURE_SENSOR_ASSEMBLY',
    detail: 'HPT604 Type A candidate. Pressure variation travels to shore for calibration and wave processing. Continuous-seawater suitability and exact configuration pending.'
  },
  wind: {
    label: 'Wind observation',
    prefix: 'WIND_SPEED_DIRECTION_SENSOR',
    detail: 'Wind speed and direction provide environmental context. Marine durability and reference testing pending.'
  },
  gps: {
    label: 'GPS / position',
    prefix: 'GNSS_GPS_ANTENNA',
    detail: 'Position and time support. Geofence decisions require quality checks and persistence—not a single drifting coordinate.'
  },
  solar: {
    label: 'Solar / power',
    prefix: 'DUAL_30W_SOLAR_ARRAY',
    detail: 'Two-panel CAD reference. Solar charging, battery and two power-monitoring channels support the ESP32 sensing node. Energy performance is not yet measured.'
  },
  esp32: {
    label: 'ESP32 controller',
    prefix: 'ESP32_CONTROLLER_ENVELOPE',
    detail: 'Controller envelope in the original CAD. Acquire → timestamp → check → package. Main processing, storage and AI stay on shore.'
  }
};

// ---- LoRa link simulation state ----
export function createLink() {
  return {
    online: true,
    sequence: 0,
    buffer: [],
    received: [],
    phase: 'receiving'
  };
}

export function setLink(state, online) {
  return {
    ...state,
    online,
    phase: online ? (state.buffer.length ? 'retransmitting' : 'receiving') : 'buffering'
  };
}

export function tickLink(state, timestamp) {
  const packet = { id: state.sequence + 1, timestamp };

  if (!state.online) {
    return {
      ...state,
      sequence: packet.id,
      buffer: [...state.buffer, packet],
      phase: 'buffering'
    };
  }

  const outgoing = [...state.buffer.slice(0, 2), packet];
  const retained = new Map(state.received.map(p => [p.id, p]));
  outgoing.forEach(p => retained.set(p.id, p));

  const buffer = state.buffer.slice(2);

  return {
    ...state,
    sequence: packet.id,
    buffer,
    received: [...retained.values()].sort((a, b) => a.id - b.id),
    phase: buffer.length ? 'retransmitting' : 'receiving'
  };
}

// ---- Wave + forecast sample generators ----
export function waveSamples(count = 64, phase = 0) {
  return Array.from({ length: count }, (_, i) =>
    .61 + Math.sin(i * .24 + phase) * .095 + Math.sin(i * .81 + phase) * .028
  );
}

export function forecastSamples(last, count = 20) {
  return Array.from({ length: count }, (_, i) =>
    last + Math.sin(i * .21) * .07 + i * .001
  );
}

// ---- SVG polyline path builder ----
export function linePath(values, x = 0, width = 600, y = 160, scale = 140) {
  return values.map((v, i) =>
    `${i ? 'L' : 'M'}${(x + i * width / Math.max(1, values.length - 1)).toFixed(2)},${(y - v * scale).toFixed(2)}`
  ).join(' ');
}