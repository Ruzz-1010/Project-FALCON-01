/* FALCON-01 — full calculation page
 *
 * Read-only: it takes the min/max pairs stored by the dashboard and recomputes
 * the forecast. It never simulates or generates readings.
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
  $("working").innerHTML =
    `<p class="note">No calculation yet. ` +
    (count ? `${count} reading(s) stored; send ${need} more.`
           : `Send at least ${MIN_READINGS} readings on the demo page.`) +
    ` The calculation appears here automatically after that.</p>`;
  $("sampleTable").innerHTML = `<p class="note">–</p>`;
}

function loadReadings() {
  let payload = null;
  try { payload = JSON.parse(localStorage.getItem("falcon-readings") || "null"); } catch (e) { /* ignore */ }
  const history = payload && Array.isArray(payload.history) ? payload.history : [];
  if (payload && [5, 10, 15].includes(Number(payload.horizon))) horizon = Number(payload.horizon);
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

const sgn = (v, d = 3) => (v >= 0 ? "+" : "−") + Math.abs(v).toFixed(d);
const signed2 = v => (v < 0 ? "−" : "") + Math.abs(v).toFixed(2);

function render(pred, points) {
  const w = pred.work;
  const pair = points[points.length - 1];

  $("stat-n").textContent = `${w.n}`;
  $("stat-last").textContent = `${fmt(w.yLast, 2)} m`;
  $("stat-h").textContent = `${horizon} min`;
  $("stat-pred").textContent = `${fmt(pred.predicted, 2)} m`;

  const out = [];
  out.push(stepHTML(1, "Wave height for one 2-minute window",
    `H = max(η) − min(η)`,
    pair && pair.lo != null
      ? `latest pair: H = ${signed2(pair.hi)} − ${pair.lo < 0 ? `(${signed2(pair.lo)})` : signed2(pair.lo)} = <b>${pair.v.toFixed(3)} m</b>`
      : `latest reading: H = <b>${w.yLast.toFixed(3)} m</b>`,
    "The buoy sends only the lowest and highest water level in the window; their difference is the pressure-derived estimate used by the model."));

  out.push(stepHTML(2, "Window of readings",
    `n = min(history, ${WINDOW})`,
    `n = <b>${w.n}</b> readings · one every ${SAMPLE_LABEL} · span ` +
      `${Math.round((w.endT - w.startT) / 60)} min ` +
      `(${clockLabel(w.startT)} → ${clockLabel(w.endT)})`,
    "Only the newest readings are used, so the trend describes the sea now."));

  out.push(stepHTML(3, "Means of the window",
    `x̄ = Σx / n &nbsp;·&nbsp; ȳ = Σy / n`,
    `x̄ = ${grp(w.sumX)} / ${w.n} = <b>${w.mx.toFixed(2)} min</b> · ` +
      `ȳ = ${w.sumY.toFixed(3)} / ${w.n} = <b>${w.my.toFixed(3)} m</b>`));

  out.push(stepHTML(4, "Slope of the trend (least squares)",
    `m = Σ(xᵢ − x̄)(yᵢ − ȳ) / Σ(xᵢ − x̄)²`,
    `m = ${w.num.toFixed(3)} / ${grp(w.den)} = <b>${w.slope.toFixed(4)} m/min</b>`,
    "This is the straight line that sits closest to all the readings — the current rise or fall."));

  out.push(stepHTML(5, "Look-ahead time",
    `T = horizon`,
    `T = <b>${horizon} min</b>`));

  out.push(stepHTML(6, "Damping factor",
    `d = 1 / (1 + T / 5)      (5 min = 300 s)`,
    `d = 1 / (1 + ${horizon}/5) = 1 / ${(1 + horizon / 5).toFixed(2)} = <b>${w.damping.toFixed(3)}</b>`,
    "The further ahead we look, the less the model trusts today's trend."));

  out.push(stepHTML(7, "Raw projection",
    `ŷ_raw = y_last + m · T · d`,
    `ŷ_raw = ${w.yLast.toFixed(3)} + ${w.slope.toFixed(4)} × ${horizon} × ${w.damping.toFixed(3)} ` +
      `= <b>${w.raw.toFixed(3)} m</b>`));

  out.push(stepHTML(8, "Change limit",
    `L = max(0.08, 0.35 · y_last) · (horizon / 15)^0.7`,
    `L = max(0.08, 0.35 × ${w.yLast.toFixed(3)}) × (${horizon}/15)^0.7 = <b>${w.maxChange.toFixed(3)} m</b> ` +
      `→ allowed ${w.lo.toFixed(3)} … ${w.hi.toFixed(3)} m`,
    "A hard guard: one forecast may not jump further than this, even when the fit is noisy."));

  out.push(stepHTML(9, "Final forecast",
    `ŷ = clamp(ŷ_raw, y_last − L, y_last + L, 0, 15)`,
    `ŷ = clamp(${w.raw.toFixed(3)}, ${w.lo.toFixed(3)}, ${w.hi.toFixed(3)}) = ` +
      `<b>${pred.predicted.toFixed(3)} m</b> ` +
      (pred.limited ? `<span style="color:#ff9c9c">← limit applied</span>` : `← inside the limit`)));

  out.push(stepHTML(10, "Spread of the readings",
    `σ = √( Σ(yᵢ − (ȳ + m(xᵢ − x̄)))² / n )`,
    `σ = √(${w.ssResid.toFixed(4)} / ${w.n}) = <b>${w.vol.toFixed(4)} m</b>`,
    "How far the readings sit off the fitted line — a small σ means a steady, well-behaved sea."));

  out.push(stepHTML(11, "Confidence",
    `c = 94 − (σ / max(ȳ, 0.1)) · 60 − 0.8 · horizon`,
    `c = 94 − (${w.vol.toFixed(4)} / ${Math.max(w.my, 0.1).toFixed(3)}) × 60 − 0.8 × ${horizon} ` +
      `= ${w.confidenceRaw.toFixed(1)} → <b>${w.confidence}%</b> (clamped to 35–94%)`));

  out.push(stepHTML(12, "Sea condition",
    `CALM if ŷ &lt; 0.6 · MODERATE if 0.6 ≤ ŷ &lt; 2.5 · ROUGH if ŷ ≥ 2.5`,
    `ŷ = ${pred.predicted.toFixed(2)} m → <b>${classify(pred.predicted)}</b>`));

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
      <thead><tr><th>time</th><th>y (m)</th><th>x−x̄</th><th>y−ȳ</th><th>(x−x̄)(y−ȳ)</th><th>(x−x̄)²</th></tr></thead>
      <tbody>${rows}</tbody>
    </table>
    <p class="note">${picks.length} of ${n} readings are listed; the sums run over all of them. x is in
    minutes and y in metres, with <b>y = H = max − min</b> for each 2-minute window. The bottom row is the
    total that feeds the slope in step 4.</p>`;
}

window.addEventListener("storage", e => {
  if (e.key === "falcon-readings") loadReadings();
});
loadReadings();
