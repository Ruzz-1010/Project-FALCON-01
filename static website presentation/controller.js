export const controllerInputs=['PRESSURE','WIND','GPS','POWER / HEALTH'];

export function controllerStep(time){
  const normalized=Math.max(0,time)/4.8;
  const cycle=Math.floor(normalized+1e-10);
  const phase=Math.max(0,normalized-cycle);
  return {
    input: -1,   // -1 = all inputs fire simultaneously
    sequence: cycle + 1,
    phase,
    stage: phase < .4  ? 'ACQUIRE'
         : phase < .58 ? 'TIMESTAMP'
         : phase < .74 ? 'VALIDATE'
         : phase < .86 ? 'PACKAGE'
         : 'TO LoRa'
  };
}

export function createController(root){
  const svg = root.querySelector('svg');
  const paths = [...svg.querySelectorAll('.traces path')];

  // Remove old animated trace-packets group (we drive pulses manually)
  const oldPackets = svg.querySelector('.trace-packets');
  if (oldPackets) oldPackets.remove();

  // Redirect the output path to FRAME label position
  if (paths[4]) paths[4].setAttribute('d', 'M465 235H560V420H360V452');

  // Move the output label
  const output = svg.querySelector('text:last-child');
  if (output) {
    output.textContent = 'FRAME ↓';
    output.setAttribute('x', '580');
    output.setAttribute('y', '405');
  }

  // --- Create 4 input pulses (one per input path) ---
  const ns = 'http://www.w3.org/2000/svg';
  const inputPulses = paths.slice(0, 4).map(() => {
    const c = document.createElementNS(ns, 'circle');
    c.setAttribute('r', '4');
    c.classList.add('controller-pulse');
    c.style.opacity = '0';
    svg.append(c);
    return c;
  });

  // --- Create 1 output pulse (LoRa path) ---
  const outputPulse = document.createElementNS(ns, 'circle');
  outputPulse.setAttribute('r', '4');
  outputPulse.classList.add('controller-pulse');
  outputPulse.style.opacity = '0';
  svg.append(outputPulse);

  const status = svg.querySelectorAll('text')[1];
  const labels = [...svg.querySelectorAll('text')].slice(2, 6);
  const code = root.querySelector('#packet-frame');
  let previous = '';

  function draw(time){
    const s = controllerStep(time);
    const incoming  = s.phase < .4;
    const outgoing  = s.phase >= .86;
    const processing = !incoming && !outgoing;

    // --- Input pulses (all 4 fire together) ---
    if (incoming) {
      const fraction = Math.min(1, s.phase / .4);
      inputPulses.forEach((pulse, i) => {
        const path = paths[i];
        const point = path.getPointAtLength(path.getTotalLength() * fraction);
        pulse.setAttribute('cx', point.x);
        pulse.setAttribute('cy', point.y);
        pulse.style.opacity = '1';
      });
      labels.forEach(l => l.classList.add('input-arrived'));
    } else {
      inputPulses.forEach(p => { p.style.opacity = '0'; });
      labels.forEach(l => l.classList.toggle('input-arrived', processing));
    }

    // --- Output pulse (single, on LoRa path) ---
    if (outgoing) {
      const fraction = Math.min(1, (s.phase - .86) / .14);
      const path = paths[4];
      const point = path.getPointAtLength(path.getTotalLength() * fraction);
      outputPulse.setAttribute('cx', point.x);
      outputPulse.setAttribute('cy', point.y);
      outputPulse.style.opacity = '1';
    } else {
      outputPulse.style.opacity = '0';
    }

    // --- Chip state ---
    root.classList.toggle('processing', processing);
    if (status) status.textContent = s.stage;

    // --- Console text ---
    const key = s.sequence + ':' + s.stage;
    if (key !== previous) {
      previous = key;
      const stamp = new Date(s.sequence * 4800).toISOString().slice(11, 23);
      if (s.phase < .86) {
        code.textContent =
          `ALL INPUTS → ${s.stage.toLowerCase()}\nFrame ${String(s.sequence).padStart(4, '0')} · preparing…`;
      } else {
        code.textContent =
          `FALCON-01 · seq ${String(s.sequence).padStart(4, '0')}\n${stamp} demo time · schema v1`;
      }
      const outEl = root.querySelector('.controller-output');
      if (outEl) outEl.textContent = outgoing
        ? 'SIMULATED · FRAME → TO LoRa'
        : 'SIMULATED · assembling telemetry';
    }
  }

  draw(0);
  return { draw };
}