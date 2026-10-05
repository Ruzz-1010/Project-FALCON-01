// Sixteen chapters. The first ten carry the DOST draft slides as a spatial
// journey (offshore -> buoy -> shore) so the original CAD stays the
// centrepiece; the next five are the wrap-up: evidence, boundaries, plan,
// cost and close; the last is a dedicated finale animation page.
export const chapters = ['Ocean', 'Objectives', 'FALCON buoy', 'Sensors', 'Software', 'LoRa link', 'Bay Station', 'Wave estimate', 'AI prediction', 'Dashboard', 'Validation & Status', 'Scope & Risks', 'Roadmap & Team', 'Impact & Funding', 'Acknowledgement', 'Finale'];

// Named chapter indices. The 3D choreography in world.js and the paging engine
// in main.js both read these instead of magic numbers, so inserting or moving a
// chapter can never silently re-point a camera pose at the wrong scene.
// Chapters 0–9 keep their exact original numbers, which the CAD choreography
// was tuned against; 10–14 are the merged wrap-up chapters; 15 is the
// dedicated finale animation page (added 2026-10-09, nothing renumbered).
export const CH = {
  ocean: 0, objectives: 1, buoy: 2, sensors: 3, controller: 4, radio: 5, shore: 6,
  waves: 7, prediction: 8, dashboard: 9, validation: 10, risks: 11,
  roadmap: 12, funding: 13, connected: 14, finale: 15
};

// Five bootcamp gates over 5 months (20 weeks), adviser-directed focused
// execution. Half-OJT half-thesis with dorm bootcamp; DOST as OJT host.
// Durations are planning ranges, not field results.
export const phases = [
  {index: '01', name: 'Freeze + procure', span: 'Month 1 · Wks 1-4', output: 'Frozen parts list, ordered sensors/power/LoRa/BayStation; barangay-hall permits + reference access.', claim: 'Nothing is claimable here. Procurement is not evidence.'},
  {index: '02', name: 'Bench integration', span: 'Month 2 · Wks 5-8', output: 'ESP32 + pressure + wind one at a time, then GPS/INA260/security; rails, protection, connectors verified.', claim: 'Continuity, power-up and bench behaviour only.'},
  {index: '03', name: 'Calibrate + software', span: 'Month 3 · Wks 9-12', output: 'Pressure baseline/depth/coeffs, wind cal; serial/API/SQLite/stale/security-persistence; LoRa gateway + Bay SIM backhaul + outage recovery.', claim: 'Corrected readings vs reference only; no field claim yet.'},
  {index: '04', name: 'Controlled validation', span: 'Month 4 · Wks 13-16', output: 'Tank/pool wave vs reference (MAE/RMSE/bias); geofence/tamper false-positive tests; 24h power log + 72h solar; waterproofing.', claim: 'This is the gate: no accuracy figure leaves this stage.'},
  {index: '05', name: 'Coastal trial + thesis', span: 'Month 5 · Wks 17-20', output: 'Supervised pilot dataset; AI baseline vs persistence on chronological held-out; updated BOM/drawings/limitations; DOST + thesis report.', claim: 'Only what the earlier stages actually measured.'}
];

// Bootcamp execution model shown on the Roadmap chapter.
export const execution = {
  model: 'Bootcamp dorm · half-OJT half-thesis · DOST as OJT host',
  weekly: 'AM OJT tasks · PM thesis block · Sat build day · Sun docs/rest',
  team: [
    {name: 'Jhon Ruzzel Correa', role: 'Hardware + Power + LoRa firmware'},
    {name: 'Mayla Bacaltos', role: 'Thesis paper (co-lead)'},
    {name: 'Gina Caballero', role: 'Thesis paper (co-lead)'},
    {name: 'Gwyn Isabel Enriquez', role: 'Edge + AI + Dashboard'}
  ],
  mentors: [
    {name: 'Sir Jam', role: 'Papers adviser · Gates 1 & 5'},
    {name: 'Sir Jeff', role: 'Hardware adviser · Gates 2 & 4'},
    {name: 'TBD · sourcing', role: 'Software/AI or DOST counterpart · Gate 3'}
  ]
};

// Adviser-approved planning range PHP 110,000–150,000 (midpoint ~₱130,000).
// "kind" drives the filter: installed stays with the delivered system,
// reusable are tools kept for later tests, process covers trials/contingency.
// Planning range only — replaced with 3-supplier quotations before submission.
export const funding = [
  {category: 'Sensors and embedded electronics (pressure, wind, ESP32, GPS)', min: 22000, max: 26000, kind: 'installed'},
  {category: 'Bay Station computer, LoRa gateway, SIM backhaul + antennas', min: 19000, max: 25000, kind: 'installed'},
  {category: 'Solar 60W, battery 20–30Ah, MPPT + protected distribution', min: 17000, max: 22000, kind: 'installed'},
  {category: 'Buoy body Ø650mm, keel, ballast, enclosure + marine connectors', min: 19000, max: 25000, kind: 'installed'},
  {category: 'Single-anchor mooring, corrosion protection + safety hardware', min: 8000, max: 14000, kind: 'installed'},
  {category: 'Calibration, reference rental, fabrication + supervised trials', min: 14000, max: 20000, kind: 'reusable'},
  {category: 'Transport, documentation, spares + contingency', min: 11000, max: 18000, kind: 'process'}
];

// Formatting and totals live here so the figure under the table can never
// drift away from the categories above it. No locale-dependent formatting: the
// peso breakdown has to read the same on every machine.
//
// NOTE ON THE TOTAL: the seven categories above sum to 110,000–150,000
// (midpoint ~130,000). Landed cost includes 20–30% shipping/tax/markup on
// imported modules; LoRa gateway + mini-PC + SIM are now budgeted (were TBD).
// Reusable tools are separated from installed parts before submission.
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
