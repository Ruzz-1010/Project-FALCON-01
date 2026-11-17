/* FALCON-01 — full calculation page
 *
 * Read-only: it takes the min/max pairs stored by the dashboard and recomputes
 * the forecast. It never simulates or generates readings.
 *
 * The first three steps follow the paper's pressure-derived wave-height
 * procedure; the remaining steps are the damped linear-trend baseline.
 */
"use strict";

const $ = id => document.getElementById(id);
const MIN_READINGS = 8;
let horizon = 15;

function showEmpty(count) {
  $("stat-n").textContent = count ? `${count} / ${MIN_READINGS}` : "–";
  $("stat-last").textContent = "–";
  $("stat-h").textContent = `${horizon} min`;
  $("stat-pred").textContent = "–";
  const need = Math.max(0, MIN_READINGS - count);
  $("working").className = "";
  $("working").innerHTML =
    phaseHTML("A", "Pressure → wave height", "Visible example for one 2-minute window", true) +
    stepHTML(1, "Find the pressure difference",
      `ΔP<sub>i</sub> = P<sub>i</sub> − P<sub>base</sub>`,
      `115.65 kPa − 115.15 kPa = <b>0.50 kPa = 500 Pa</b>`,
      "The output is still pressure. It is not wave height yet.") +
    stepHTML(2, "Convert pressure difference to movement",
      `η<sub>i</sub> = ΔP<sub>i</sub> / (ρ × g)`,
      `500 Pa / (1,025 kg/m³ × 9.81 m/s²) = <b>0.0497 m ≈ 0.05 m</b>`,
      "This produces one converted water-level movement in metres.") +
    stepHTML(3, "Compute wave height for the complete window",
      `H<sub>est</sub> = max(η<sub>i</sub>) − min(η<sub>i</sub>)`,
      `example: (+0.25 m) − (−0.25 m) = <b>0.50 m</b>`,
      "This final answer is the estimated wave height for one two-minute window.") +
    `<p class="bridge"><b>Prediction is not available yet.</b> ` +
    (count ? `${count} wave-height record(s) stored; add ${need} more.`
           : `Add at least ${MIN_READINGS} wave-height records on the console.`) +
    ` After that, this page will show the substituted 15-minute trend computation using your actual demo values.</p>`;
  $("sampleTable").innerHTML = `<p class="note">–</p>`;
  $("sums").hidden = true;
}

function loadReadings() {
  let payload = null;
  try { payload = JSON.parse(localStorage.getItem("falcon-readings") || "null"); } catch (e) { /* ignore */ }
  const history = payload && Array.isArray(payload.history) ? payload.history : [];
  if (history.length < MIN_READINGS) { showEmpty(history.length); return; }
  const recent = history.slice(-WINDOW);
  render(project(recent, horizon), recent);
}

/* ------------------------------------------------------ the worked steps */
function stepHTML(i, label, formula, sub, why) {
  return `<div class="step"><div class="lbl"><i>${i}</i>${label}</div>` +
         `<div class="formula">${formula}</div>` +
         `<div class="sub">${sub}</div>` +
         (why ? `<div class="why">${why}</div>` : "") + `</div>`;
}

function phaseHTML(tag, title, sub, first) {
  return `<div class="phase${first ? " first" : ""}"><span class="phase-tag">${tag}</span>` +
         `<div><b>${title}</b><small>${sub}</small></div></div>`;
}

const sgn = (v, d = 3) => (v >= 0 ? "+" : "−") + Math.abs(v).toFixed(d);
const signed2 = v => (v < 0 ? "−" : "") + Math.abs(v).toFixed(2);

function render(pred, points) {
  const w = pred.work;
  const pair = points[points.length - 1];

  $("working").className = "";
  $("sums").hidden = false;
  $("stat-n").textContent = `${w.n}`;
  $("stat-last").textContent = `${fmt(w.yLast, 2)} m`;
  $("stat-h").textContent = `${horizon} min`;
  $("stat-pred").textContent = `${fmt(pred.predicted, 2)} m`;

  const out = [];

  /* -------------------------------------------------- A. paper formula */
  out.push(phaseHTML("A", "Pressure → wave height", "Paper · pressure-derived estimate", true));

  out.push(stepHTML(1, "Pressure change at the sensor",
    `ΔP<sub>i</sub> = P<sub>i</sub> − P<sub>base</sub>`,
    `Example: 115.65 kPa − 115.15 kPa = <b>0.50 kPa = 500 Pa</b>`,
    "This is the first computation. The two-minute window initially produces pressure in kPa; this step changes it to a pressure difference in Pa."));

  out.push(stepHTML(2, "Pressure change → water-level displacement",
    `η<sub>i</sub> = ΔP<sub>i</sub> / (ρ × g)`,
    `Example: 500 Pa / (1,025 kg/m³ × 9.81 m/s²) = <b>0.0497 m ≈ 0.05 m</b>`,
    "Only here does the pressure difference become an estimated movement in metres."));

  out.push(stepHTML(3, "Wave height for one 2-minute window",
    `H<sub>est</sub> = max(η<sub>i</sub>) − min(η<sub>i</sub>)`,
    pair && pair.lo != null
      ? `latest pair: H = ${signed2(pair.hi)} − ${pair.lo < 0 ? `(${signed2(pair.lo)})` : signed2(pair.lo)} = <b>${pair.v.toFixed(3)} m</b>`
      : `latest reading: H = <b>${w.yLast.toFixed(3)} m</b>`,
    "This is the final computation after all readings in the two-minute window are converted to η values. The console starts here because its input is already the lowest and highest converted values."));

  out.push(`<p class="bridge">The console starts at <b>step 3</b> — every pair you add is already the
    lowest / highest η of one 2-minute record. Steps 1–2 are how the pressure sensor produces those values.
    The forecast below is the paper's <b>damped linear-trend baseline</b>, the comparison method — not the
    trained AI model.</p>`);

  /* ------------------------------------------- B. damped trend baseline */
  out.push(phaseHTML("B", "Wave height → 15-minute estimate", "Transparent trend baseline", false));

  out.push(stepHTML(4, "Choose the recent wave-height records",
    `n = ${w.n} recent records`,
    `latest H<sub>est</sub> = <b>${w.yLast.toFixed(3)} m</b> · time span = ` +
      `<b>${Math.round((w.endT - w.startT) / 60)} min</b>`,
    "These are completed two-minute wave-height records, not raw pressure samples."));

  out.push(stepHTML(5, "Find the direction of change",
    `m = Σ[(x<sub>i</sub> − x̄)(y<sub>i</sub> − ȳ)] / Σ[(x<sub>i</sub> − x̄)²]`,
    `m = ${w.num.toFixed(3)} / ${grp(w.den)} = <b>${w.slope.toFixed(4)} m/min</b>`,
    "A positive m means the estimated waves are increasing; a negative m means they are decreasing."));

  out.push(stepHTML(6, "Reduce the trend for a 15-minute look-ahead",
    `d = 1 / (1 + T / 5)`,
    `d = 1 / (1 + ${horizon}/5) = <b>${w.damping.toFixed(3)}</b>`,
    "Damping prevents the latest trend from being extended too strongly into the future."));

  out.push(stepHTML(7, "Compute the 15-minute estimate",
    `ŷ<sub>raw</sub> = y<sub>last</sub> + (m × T × d)`,
    `ŷ<sub>raw</sub> = ${w.yLast.toFixed(3)} + (${w.slope.toFixed(4)} × ${horizon} × ${w.damping.toFixed(3)}) ` +
      `= <b>${w.raw.toFixed(3)} m</b>`,
    "This is the transparent trend estimate before applying the allowed-change limit."));

  out.push(stepHTML(8, "Apply the allowed-change limit",
    `ŷ = clamp(ŷ<sub>raw</sub>, ${w.lo.toFixed(3)}, ${w.hi.toFixed(3)})`,
    `final 15-minute estimate = <b>${pred.predicted.toFixed(3)} m</b> ` +
      (pred.limited ? `<span style="color:#ff9c9c">· limit applied</span>` : `· raw estimate accepted`),
    "The limit blocks an unrealistic jump caused by a short or noisy record."));

  out.push(stepHTML(9, "Label the estimated sea condition",
    `Calm: ŷ &lt; 0.60 m · Moderate: 0.60–2.49 m · Rough: ŷ ≥ 2.50 m`,
    `ŷ = ${pred.predicted.toFixed(2)} m → <b>${classify(pred.predicted)}</b>`,
    "This label describes the demo estimate only and is not an official marine advisory."));

  $("working").innerHTML = out.join("");

  const n = w.n;
  const picks = [...new Set([0, 1, Math.round(n * 0.25), Math.round(n * 0.5), n - 2, n - 1])]
    .filter(i => i >= 0 && i < n).sort((a, b) => a - b);
  let rows = "";
  for (const i of picks) {
    const dx = w.xs[i] - w.mx, dy = w.ys[i] - w.my;
    rows += `<tr><td>${clockLabel(w.startT + w.xs[i] * 60)}</td>` +
            `<td>${w.ys[i].toFixed(2)}</td>` +
            `<td>${sgn(dx)}</td><td>${sgn(dy)}</td>` +
            `<td>${sgn(dx * dy)}</td><td>${(dx * dx).toFixed(0)}</td></tr>`;
  }
  rows += `<tr class="sum"><td>Σ · all ${n} readings</td><td>–</td><td>0</td><td>0</td>` +
          `<td>${w.num.toFixed(2)}</td><td>${grp(w.den)}</td></tr>`;

  $("sampleTable").innerHTML = `<table>
      <thead><tr><th>time</th><th>y (m)</th><th>dx</th><th>dy</th><th>dx·dy</th><th>dx²</th></tr></thead>
      <tbody>${rows}</tbody>
    </table>
    <p class="note">${picks.length} of ${n} readings are listed; the sums run over all of them. x is in
    minutes and y in metres, with <b>y = H<sub>est</sub> = highest − lowest</b>. Here
    <b>dx = x − x̄</b> and <b>dy = y − ȳ</b>. The bottom row is the total that feeds the slope in step 6.</p>`;
}

window.addEventListener("storage", e => {
  if (e.key === "falcon-readings") loadReadings();
});
loadReadings();
