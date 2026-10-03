export const chapters = ['Ocean', 'FALCON', 'Sensors', 'ESP32', 'LoRa', 'Bay Station', 'Wave estimate', 'AI prediction', 'Dashboard', 'Connected'];
export const components = {
  pressure: {label: 'Underwater pressure', prefix: 'WATER_PRESSURE_SENSOR_ASSEMBLY', detail: 'Underwater pressure sensor provides input for pressure-based estimated wave height. Calibration is pending.'},
  wind: {label: 'Wind observation', prefix: 'WIND_SPEED_DIRECTION_SENSOR', detail: 'Wind speed and direction sensors provide primary meteorological measurements. Reference comparison pending.'},
  gps: {label: 'GPS / position', prefix: 'GNSS_GPS_ANTENNA', detail: 'GPS provides position and timing for system health and security. Quality checks are applied before alerts.'},
  battery: {label: 'Battery / energy storage', prefix: 'LIFEPO4_BATTERY_12V_ENVELOPE', detail: 'LiFePO4 battery stores solar energy for continuous operation during low light.'},
  solar: {label: 'Solar / power', prefix: 'DUAL_30W_SOLAR_ARRAY', detail: 'Dual solar panels supply power to the buoy. Energy performance measurement is pending.'},
  esp32: {label: 'ESP32 controller', prefix: 'ESP32_CONTROLLER_ENVELOPE', detail: 'ESP32 acquires sensor data, timestamps and validates values, then prepares LoRa telemetry frames. Processing remains on shore.'},
  lora: {label: 'LoRa transceiver', prefix: 'NAVIGATION_LIGHT', detail: 'LoRa radio link transmits telemetry from buoy to shore Bay Station. Placement illustrated using existing model.'}
};

// Pure presentation state: no radio, database or operational telemetry involved.
export function createLink() { return {online: true, sequence: 0, buffer: [], received: [], phase: 'receiving'}; }
export function setLink(state, online) {
  return {...state, online, phase: online ? (state.buffer.length ? 'retransmitting' : 'receiving') : 'buffering'};
}
export function tickLink(state, timestamp) {
  const packet = {id: state.sequence + 1, timestamp};
  if (!state.online) return {...state, sequence: packet.id, buffer: [...state.buffer, packet], phase: 'buffering'};
  const outgoing = [...state.buffer.slice(0, 2), packet];
  const retained = new Map(state.received.map(p => [p.id, p]));
  outgoing.forEach(p => retained.set(p.id, p));
  const buffer = state.buffer.slice(2);
  return {...state, sequence: packet.id, buffer, received: [...retained.values()].sort((a, b) => a.id - b.id), phase: buffer.length ? 'retransmitting' : 'receiving'};
}
export function waveSamples(count = 64, phase = 0) {
  return Array.from({length: count}, (_, i) => .61 + Math.sin(i * .24 + phase) * .095 + Math.sin(i * .81 + phase) * .028);
}
export function forecastSamples(last, count = 20) {
  return Array.from({length: count}, (_, i) => last + Math.sin(i * .21) * .07 + i * .001);
}
export function linePath(values, x = 0, width = 600, y = 160, scale = 140) {
  return values.map((v, i) => `${i ? 'L' : 'M'}${(x + i * width / Math.max(1, values.length - 1)).toFixed(2)},${(y - v * scale).toFixed(2)}`).join(' ');
}
