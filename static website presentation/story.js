// Eighteen chapters. The first fifteen carry the DOST draft slides; the last
// three answer the three questions a funding panel always asks and the earlier
// build had no slide for: what is the plan, who benefits, and what will it cost.
// The first half keeps the spatial journey (offshore -> buoy -> shore) so the
// original CAD stays the centrepiece; the second half is the wrap-up slides.
export const chapters = ['Ocean', 'Objectives', 'FALCON buoy', 'Sensors', 'Software', 'LoRa link', 'Bay Station', 'Wave estimate', 'AI prediction', 'Dashboard', 'Validation', 'Status', 'Scope limits', 'Risks', 'Roadmap', 'Impact', 'Funding', 'Acknowledgement'];

// Named chapter indices. The 3D choreography in world.js and the paging engine
// in main.js both read these instead of magic numbers, so inserting or moving a
// chapter can never silently re-point a camera pose at the wrong scene.
// Roadmap, Impact and Funding were appended AFTER every original index, so the
// chapters the CAD choreography was tuned against (1, 2, 5, 6) keep their exact
// original numbers.
export const CH = {
  ocean: 0, objectives: 1, buoy: 2, sensors: 3, controller: 4, radio: 5, shore: 6,
  waves: 7, prediction: 8, dashboard: 9, validation: 10, status: 11, scope: 12,
  risks: 13, roadmap: 14, impact: 15, funding: 16, connected: 17
};

// The seven funded development stages, straight from the DOST idea package
// (Slide 8, "Development plan"). These are proposals with indicative durations,
// not commitments, and are shown that way on the Roadmap chapter.
export const phases = [
  {index: '01', name: 'Design + procure', span: '1 month', output: 'Frozen parts list and purchased components.', claim: 'Nothing is claimable here. Procurement is not evidence.'},
  {index: '02', name: 'Integrate electronics', span: '1–2 months', output: 'Working sensor and power assemblies on the bench.', claim: 'Continuity, power-up and bench behaviour only.'},
  {index: '03', name: 'Fabricate buoy', span: '1 month', output: 'A sealed and mechanically stable physical prototype.', claim: 'Ingress and stability check results, not sea performance.'},
  {index: '04', name: 'Calibrate + test', span: '1–2 months', output: 'Calibration records and corrected readings against a reference.', claim: 'This is the gate: no accuracy claim may leave this stage.'},
  {index: '05', name: 'Coastal pilot', span: '2–3 months', output: 'A supervised local dataset from one identified site.', claim: 'Documented site conditions and uptime — not a public service.'},
  {index: '06', name: 'Train + evaluate', span: '1–2 months', output: 'A baseline-versus-model comparison with MAE, RMSE and bias.', claim: 'Prediction skill figures may be quoted only with those numbers.'},
  {index: '07', name: 'Demonstrate + report', span: '1 month', output: 'A validated prototype and the technical report.', claim: 'Only what the earlier stages actually measured.'}
];

// The preliminary funding plan from the DOST idea package (Slide 9). A planning
// range, and it says so on the page. "kind" drives the little filter on the
// Funding chapter: a panel member can separate parts that stay in the prototype
// from reusable tools and process costs.
export const funding = [
  {category: 'Sensors and embedded electronics', min: 15000, max: 22000, kind: 'installed'},
  {category: 'Bay Station computer, storage, LoRa networking and backhaul', min: 5000, max: 12000, kind: 'installed'},
  {category: 'Solar, battery, charging and protected distribution', min: 12000, max: 20000, kind: 'installed'},
  {category: 'Buoy body, structure, enclosure and marine connectors', min: 15000, max: 28000, kind: 'installed'},
  {category: 'Mooring, anchor, corrosion protection and safety hardware', min: 7000, max: 14000, kind: 'installed'},
  {category: 'Calibration, reference tools, fabrication and field trials', min: 10000, max: 20000, kind: 'reusable'},
  {category: 'Transport, documentation, spares and contingency', min: 8000, max: 15000, kind: 'process'}
];

// Formatting and totals live here so the figure under the table can never
// drift away from the categories above it. No locale-dependent formatting: the
// peso breakdown has to read the same on every machine.
//
// NOTE ON THE TOTAL: the seven categories above sum to 72,000-131,000. The
// source package is inconsistent with itself here - its table's summary row and
// its funding-breakdown graphic say 72,000-127,000, while its own spoken script
// says "thousand to one hundred thirty-one thousand" and its line items actually
// add up to 131,000. The line items are what a panel can check by hand, so the
// sum is what this page shows. Recorded rather than silently smoothed over.
const peso = value => `₱${String(value).replace(/\B(?=(\d{3})+(?!\d))/g, ',')}`;
export const pesoAmount = value => `${peso(value.min)} – ${peso(value.max)}`;
export function fundingRange(rows = funding) {
  const sum = key => rows.reduce((total, row) => total + row[key], 0);
  return `${peso(sum('min'))} – ${peso(sum('max'))}`;
}

// Labels for the funding filter, so the buttons and the table's Type column
// cannot describe the same category in two different ways. "Installed" covers
// both the buoy and the shore station: the test is whether the part stays with
// the delivered system or is a tool the team keeps for later tests.
export const fundingKinds = {
  installed: 'Installed',
  reusable: 'Reusable tool',
  process: 'Process / contingency'
};

// Who the pilot is meant to serve, and the honest limit on each claim. The DOST
// package insists on one verified beneficiary before any expansion, so every
// card ends with what still has to be confirmed.
export const beneficiaries = [
  {who: 'Coastal LGUs and disaster offices', value: 'A local observation history for planning, records and drills.', verify: 'One LGU confirms a specific data need and a pilot site.'},
  {who: 'Fisherfolk and small craft', value: 'Plain, local sea-condition information they can actually reach.', verify: 'The information is checked against what they already use.'},
  {who: 'Schools and marine researchers', value: 'A documented, reproducible platform students can build on.', verify: 'The methods and limits are published with the data.'},
  {who: 'Ports, tourism and environment groups', value: 'Awareness of equipment condition and long-term site trends.', verify: 'Uptime and maintenance cost are measured, not assumed.'}
];
export const chapterCount = chapters.length;
// The coast and the buoy's offshore relocation both span the radio -> shore run.
// Kept here so world.js has one place to ask instead of two copies of a range.
export const coastSpan = {from: CH.radio - .35, to: CH.shore + 1.15};
export const components = {
  pressure: {label: 'Underwater pressure', prefix: 'WATER_PRESSURE_SENSOR_ASSEMBLY', detail: 'Primary Phase 1 measurement. Pressure is the input for the pressure-derived estimated wave height; calibration is required before any accuracy claim.'},
  wind: {label: 'Wind observation', prefix: 'WIND_SPEED_DIRECTION_SENSOR', detail: 'Primary Phase 1 measurement: wind speed and direction at the buoy. Comparison against a reference anemometer is still pending.'},
  gps: {label: 'GPS / position', prefix: 'GNSS_GPS_ANTENNA', detail: 'Supporting telemetry: position, time and geofence persistence for system health and security. Quality checks are applied before alerts.'},
  battery: {label: 'Battery / energy storage', prefix: 'LIFEPO4_BATTERY_12V_ENVELOPE', detail: 'LiFePO4 battery stores solar energy for continuous operation during low light. Power budget validation is pending.'},
  solar: {label: 'Solar / power', prefix: 'DUAL_30W_SOLAR_ARRAY', detail: 'Dual solar panels supply power to the buoy. No measured output is claimed until the power budget is validated.'},
  esp32: {label: 'ESP32 controller', prefix: 'ESP32_CONTROLLER_ENVELOPE', detail: 'ESP32 firmware acquires sensor data, timestamps and validates values, then prepares LoRa telemetry frames. No mini PC or cellular modem on the buoy.'},
  lora: {label: 'LoRa transceiver', prefix: 'NAVIGATION_LIGHT', detail: 'LoRa radio link carries telemetry from buoy to shore Bay Station. Hardware selection and range are not yet validated.'}
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
