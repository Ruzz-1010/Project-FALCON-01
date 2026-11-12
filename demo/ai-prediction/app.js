/* FALCON-01 — manual AI forecast dashboard
 *
 * Nothing here runs on a timer. A reading is added only when the user sends a
 * min/max pair. The wave height used by the model is the paper's estimate:
 *
 *     H = max(eta) - min(eta)
 *
 * The forecast itself is the shared damped-linear-trend baseline in model.js.
 */
"use strict";

const state = {
  history: [],   // {t, v, lo, hi} — t in virtual seconds, v = H = hi - lo
  pending: [],   // {fromT, fromV, targetT, predicted}
  errors: [],    // {..., actualT, actual, error}
  horizon: 15,
};

const $ = id => document.getElementById(id);
const MIN_READINGS = 8;
const WAVE_MIN = -15, WAVE_MAX = 15;

/* --------------------------------------------------------------- readings */
function addReading(lo, hi) {
  lo = Math.max(WAVE_MIN, Math.min(WAVE_MAX, lo));
  hi = Math.max(WAVE_MIN, Math.min(WAVE_MAX, hi));
  if (hi < lo) { const swap = lo; lo = hi; hi = swap; }

  const t = state.history.length
    ? state.history[state.history.length - 1].t + SAMPLE_INTERVAL_S
    : SAMPLE_INTERVAL_S;
  const v = Math.max(0, Math.min(15, hi - lo));

  state.history.push({ t, v, lo, hi });
  if (state.history.length > 600) state.history.shift();

  /* A forecast is checked by the first reading at or after its target time. */
  for (let i = state.pending.length - 1; i >= 0; i--) {
    const p = state.pending[i];
    if (p.targetT > t) continue;
    state.pending.splice(i, 1);
    state.errors.unshift({ ...p, actualT: t, actual: v, error: Math.abs(p.predicted - v) });
    if (state.errors.length > 5) state.errors.pop();
  }

  /* Only make a forecast once the short history exists. */
  const recent = state.history.slice(-WINDOW);
  if (recent.length >= MIN_READINGS) {
    const pred = project(recent, state.horizon);
    state.pending.push({
      fromT: t, fromV: v,
      targetT: t + state.horizon * 60,
      predicted: pred.predicted,
    });
  }

  /* calc.html reads this; it never generates its own data. */
  try {
    localStorage.setItem("falcon-readings", JSON.stringify({
      horizon: state.horizon,
      history: state.history.slice(-60),
    }));
  } catch (e) { /* storage may be disabled */ }

  render();
}

function currentPrediction() {
  const recent = state.history.slice(-WINDOW);
  if (recent.length < MIN_READINGS) return null;
  const res = project(recent, state.horizon);
  return {
    ...res, horizon: state.horizon,
    targetT: recent[recent.length - 1].t + state.horizon * 60,
    points: recent,
  };
}

/* ------------------------------------------------------------------ chart */
const canvas = $("chart");
const ctx = canvas.getContext("2d");

function resize() {
  const dpr = Math.min(2, window.devicePixelRatio || 1);
  const r = canvas.getBoundingClientRect();
  canvas.width = Math.max(1, Math.round(r.width * dpr));
  canvas.height = Math.max(1, Math.round(r.height * dpr));
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
}
window.addEventListener("resize", () => { resize(); draw(); });

function draw() {
  const W = canvas.clientWidth, H = canvas.clientHeight;
  if (!W || !H) return;
  const padL = 46, padR = 74, padT = 20, padB = 34;
  ctx.clearRect(0, 0, W, H);

  const last = state.history[state.history.length - 1];
  const now = last ? last.t : 0;
  const t0 = Math.max(0, now - 60 * 60);
  const t1 = now + state.horizon * 60;

  if (!state.history.length) {
    ctx.fillStyle = "#7f9aab";
    ctx.font = "14px system-ui, sans-serif";
    ctx.textAlign = "center"; ctx.textBaseline = "middle";
    ctx.fillText("No readings yet — send the first min / max pair below.", W / 2, H / 2);
    return;
  }

  const pred = currentPrediction();
  const series = pred
    ? forecastSeries(pred.points, pred.horizon, pred.predicted, pred.confidence)
    : [];
  const shownErrors = state.errors.slice(0, 3);

  let maxV = 0.8;
  for (const p of state.history) if (p.t >= t0) maxV = Math.max(maxV, p.v);
  for (const e of shownErrors) maxV = Math.max(maxV, e.predicted, e.actual);
  for (const s of series) maxV = Math.max(maxV, s.hi);
  const yMax = Math.max(1.2, Math.ceil(maxV * 1.15 * 10) / 10);

  const X = t => padL + (t - t0) / Math.max(1, t1 - t0) * (W - padL - padR);
  const Y = v => H - padB - (v / yMax) * (H - padT - padB);

  /* horizontal grid and y labels */
  ctx.font = "11.5px ui-monospace, monospace";
  ctx.textBaseline = "middle";
  for (let i = 0; i <= 3; i++) {
    const v = yMax * i / 3, y = Y(v);
    ctx.strokeStyle = i === 0 ? "#1d4051" : "#122c39";
    ctx.beginPath(); ctx.moveTo(padL, y); ctx.lineTo(W - padR, y); ctx.stroke();
    ctx.fillStyle = "#5f7f90"; ctx.textAlign = "right";
    ctx.fillText(v.toFixed(1), padL - 8, y);
  }

  /* vertical time grid */
  ctx.textBaseline = "top";
  for (const rel of [-60, -45, -30, -15, 0]) {
    const t = now + rel * 60;
    if (t < t0) continue;
    const x = X(t);
    ctx.strokeStyle = rel === 0 ? "#2f6a82" : "#0f2632";
    ctx.beginPath(); ctx.moveTo(x, padT); ctx.lineTo(x, H - padB); ctx.stroke();
    ctx.fillStyle = rel === 0 ? "#8fb8cc" : "#5f7f90";
    ctx.textAlign = "center";
    ctx.fillText(rel === 0 ? "now" : `${rel} min`, x, H - padB + 9);
  }
  ctx.fillStyle = "#ffb98a"; ctx.textAlign = "center";
  ctx.fillText(`+${state.horizon} min`, X(t1), H - padB + 9);

  /* measured H readings */
  const hist = state.history.filter(p => p.t >= t0);
  if (hist.length > 1) {
    ctx.strokeStyle = "#5aa9c8"; ctx.lineWidth = 1.6;
    ctx.beginPath();
    hist.forEach((p, i) => i ? ctx.lineTo(X(p.t), Y(p.v)) : ctx.moveTo(X(p.t), Y(p.v)));
    ctx.stroke();
  }
  ctx.fillStyle = "#7fc3dc";
  for (const p of hist) {
    ctx.beginPath(); ctx.arc(X(p.t), Y(p.v), 2.2, 0, Math.PI * 2); ctx.fill();
  }
  ctx.lineWidth = 1;

  /* forecasts that have already been checked */
  for (const e of shownErrors) {
    const actualT = e.actualT == null ? e.targetT : e.actualT;
    ctx.strokeStyle = "rgba(255,138,61,0.55)";
    ctx.setLineDash([5, 4]); ctx.lineWidth = 1.8;
    ctx.beginPath();
    ctx.moveTo(X(e.fromT), Y(e.fromV));
    ctx.lineTo(X(e.targetT), Y(e.predicted));
    ctx.stroke();
    ctx.setLineDash([]); ctx.lineWidth = 1;

    if (actualT !== e.targetT) {
      ctx.strokeStyle = "rgba(255,138,61,0.28)"; ctx.setLineDash([2, 3]);
      ctx.beginPath();
      ctx.moveTo(X(e.targetT), Y(e.predicted));
      ctx.lineTo(X(actualT), Y(e.predicted));
      ctx.stroke();
      ctx.setLineDash([]);
    }

    const x = X(actualT);
    ctx.strokeStyle = "rgba(78,224,160,0.55)"; ctx.lineWidth = 2;
    ctx.beginPath(); ctx.moveTo(x, Y(e.predicted)); ctx.lineTo(x, Y(e.actual)); ctx.stroke();
    ctx.fillStyle = "#ffb98a";
    ctx.beginPath(); ctx.arc(X(e.targetT), Y(e.predicted), 3, 0, Math.PI * 2); ctx.fill();
    ctx.fillStyle = "#4ee0a0";
    ctx.beginPath(); ctx.arc(x, Y(e.actual), 4.5, 0, Math.PI * 2); ctx.fill();
    ctx.lineWidth = 1;
  }

  /* live forecast ahead */
  if (series.length > 1) {
    ctx.fillStyle = "rgba(255,217,138,0.15)";
    ctx.beginPath();
    ctx.moveTo(X(now), Y(last.v));
    series.forEach(s => ctx.lineTo(X(now + s.p * 60), Y(s.hi)));
    for (let i = series.length - 1; i >= 0; i--) {
      ctx.lineTo(X(now + series[i].p * 60), Y(series[i].lo));
    }
    ctx.closePath(); ctx.fill();

    ctx.strokeStyle = "#ff8a3d"; ctx.lineWidth = 2.5; ctx.setLineDash([7, 4]);
    ctx.beginPath();
    series.forEach((s, i) => {
      const x = X(now + s.p * 60), y = Y(s.v);
      i ? ctx.lineTo(x, y) : ctx.moveTo(x, y);
    });
    ctx.stroke(); ctx.setLineDash([]); ctx.lineWidth = 1;

    const end = series[series.length - 1];
    ctx.fillStyle = "#ff8a3d";
    ctx.beginPath(); ctx.arc(X(t1), Y(end.v), 4.5, 0, Math.PI * 2); ctx.fill();
    ctx.fillStyle = "#ffd0a8"; ctx.textAlign = "left"; ctx.textBaseline = "middle";
    ctx.font = "600 13px ui-monospace, monospace";
    ctx.fillText(fmt(end.v, 2) + " m", X(t1) + 9, Y(end.v));
  }

  /* label the newest check */
  if (shownErrors.length) {
    const e = shownErrors[0];
    const actualT = e.actualT == null ? e.targetT : e.actualT;
    const x = X(actualT), y = Y(e.actual);
    const label = `said ${fmt(e.predicted, 2)} · was ${fmt(e.actual, 2)}`;
    ctx.font = "600 12.5px ui-monospace, monospace";
    const w = ctx.measureText(label).width + 14;
    let bx = Math.min(x - w / 2, W - w - 4);
    bx = Math.max(padL, bx);
    const by = Math.max(padT, y - 34);
    ctx.fillStyle = "rgba(6,22,32,0.92)";
    ctx.strokeStyle = "rgba(78,224,160,0.45)";
    ctx.beginPath();
    if (ctx.roundRect) ctx.roundRect(bx, by, w, 21, 6); else ctx.rect(bx, by, w, 21);
    ctx.fill(); ctx.stroke();
    ctx.fillStyle = "#c8f5dc"; ctx.textAlign = "left"; ctx.textBaseline = "middle";
    ctx.fillText(label, bx + 7, by + 11);
  }
}

/* -------------------------------------------------------------------- UI */
function updateUI() {
  const pred = currentPrediction();
  const last = state.history[state.history.length - 1];

  if (last) {
    $("reading").innerHTML = `${fmt(last.v, 2)}<small>m</small>`;
    $("readingNote").innerHTML =
      `reading ${state.history.length} at ${clockLabel(last.t)} · H = max − min`;
    $("readingDelta").innerHTML =
      `min <b>${signed2(last.lo)} m</b> · max <b>${signed2(last.hi)} m</b> → ` +
      `H = <b>${fmt(last.v, 2)} m</b>`;
  } else {
    $("reading").textContent = "–";
    $("readingNote").textContent = "no reading yet — send the first min / max pair";
    $("readingDelta").textContent = "H = max − min";
  }

  if (!pred) {
    $("forecast").textContent = "–";
    $("condition").textContent = "—";
    $("condition").className = "cond COLLECTING";
    $("forecastWhen").textContent = state.horizon + " min ahead";
    $("trendLine").textContent = state.history.length < MIN_READINGS
      ? `Waiting for ${MIN_READINGS - state.history.length} more reading(s).`
      : "Waiting for readings.";
    $("confidence").textContent = "–";
    $("confBar").style.width = "0%";
  } else {
    const w = pred.work;
    const cls = classify(pred.predicted);
    $("forecast").innerHTML = `${fmt(pred.predicted, 2)}<small>m</small>`;
    $("condition").textContent = `${cls} SEA`;
    $("condition").className = "cond " + cls;
    $("forecastWhen").textContent = `in ${pred.horizon} minutes`;
    const absT = Math.abs(pred.slope);
    $("trendLine").innerHTML = absT < 0.0005
      ? `Last ${w.n} readings: <b>steady</b>`
      : `Last ${w.n} readings: sea is <b>${pred.slope > 0 ? "building" : "easing"}</b> ` +
        `${absT.toFixed(3)} m per minute`;
    $("confidence").textContent = `${pred.confidence}%`;
    $("confBar").style.width = pred.confidence + "%";
  }

  $("clock").textContent = `readings sent: ${state.history.length} · ` +
    (pred ? `next forecast target ${clockLabel(pred.targetT)}` : "no forecast yet");

  $("unlockNote").textContent = state.history.length < MIN_READINGS
    ? `Waiting for ${MIN_READINGS - state.history.length} more reading(s). Nothing is generated for you.`
    : "Forecast unlocked. Every new pair updates the model; nothing runs on a timer.";

  const tbody = $("errors");
  if (!state.errors.length) {
    tbody.innerHTML = `<tr><td colspan="4" class="cap">no checks yet</td></tr>`;
    $("avg").innerHTML = ""; $("evalLine").innerHTML = "";
  } else {
    tbody.innerHTML = state.errors.map(e => {
      const ok = e.error <= 0.10;
      const when = e.actualT == null ? e.targetT : e.actualT;
      return `<tr><td>${clockLabel(when)}</td><td>${fmt(e.predicted, 2)} m</td>` +
             `<td>${fmt(e.actual, 2)} m</td>` +
             `<td class="${ok ? "good" : "bad"}">${fmt(e.error, 2)} m</td></tr>`;
    }).join("");

    const n = state.errors.length;
    const mae = state.errors.reduce((a, e) => a + Math.abs(e.predicted - e.actual), 0) / n;
    const rmse = Math.sqrt(state.errors.reduce((a, e) => a + e.error * e.error, 0) / n);
    const bias = state.errors.reduce((a, e) => a + (e.predicted - e.actual), 0) / n;
    $("avg").innerHTML = `Average miss: <b>${mae.toFixed(2)} m</b> over ${n} check(s)`;
    $("evalLine").innerHTML =
      `MAE <b>${mae.toFixed(2)} m</b> · RMSE <b>${rmse.toFixed(2)} m</b> · ` +
      `mean bias <b>${bias.toFixed(2)} m</b> (persistence = hold at the last reading)`;
  }

  renderWorking(pred);
}

function render() {
  draw();
  updateUI();
}

/* ------------------------------------------------------ detailed calculation */
const grp2 = v => Math.round(v).toLocaleString("en-US");
const sgn2 = v => (v >= 0 ? "+" : "−") + Math.abs(v).toFixed(3);
const signed2 = v => (v < 0 ? "−" : "") + Math.abs(v).toFixed(2);

function stepHTML(i, label, formula, sub, why) {
  return `<div class="step"><div class="lbl"><i>${i}</i>${label}</div>` +
         `<div class="formula">${formula}</div>` +
         `<div class="sub">${sub}</div>` +
         (why ? `<div class="why">${why}</div>` : "") + `</div>`;
}

function renderWorking(pred) {
  const host = $("working"), tbl = $("sampleTable");
  if (!pred || !pred.work) {
    host.innerHTML = `<p class="cap">Send at least ${MIN_READINGS} readings — the calculation appears here.</p>`;
    tbl.innerHTML = `<p class="cap">–</p>`;
    return;
  }

  const w = pred.work;
  const h = pred.horizon;
  const pair = pred.points[pred.points.length - 1];
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
      `${Math.round((w.endT - w.startT) / 60)} min (${clockLabel(w.startT)} → ${clockLabel(w.endT)})`,
    "Only the newest readings are used, so the trend describes the sea now."));

  out.push(stepHTML(3, "Means of the window",
    `x̄ = Σx / n &nbsp;·&nbsp; ȳ = Σy / n`,
    `x̄ = ${grp2(w.sumX)} / ${w.n} = <b>${w.mx.toFixed(2)} min</b> · ` +
      `ȳ = ${w.sumY.toFixed(3)} / ${w.n} = <b>${w.my.toFixed(3)} m</b>`));

  out.push(stepHTML(4, "Slope of the trend (least squares)",
    `m = Σ(xᵢ − x̄)(yᵢ − ȳ) / Σ(xᵢ − x̄)²`,
    `m = ${w.num.toFixed(3)} / ${grp2(w.den)} = <b>${w.slope.toFixed(4)} m/min</b>`,
    "The straight line closest to all readings — the current rise or fall."));

  out.push(stepHTML(5, "Look-ahead time",
    `T = horizon`,
    `T = <b>${h} min</b>`));

  out.push(stepHTML(6, "Damping factor",
    `d = 1 / (1 + T / 5)      (5 min = 300 s)`,
    `d = 1 / (1 + ${h}/5) = 1 / ${(1 + h / 5).toFixed(2)} = <b>${w.damping.toFixed(3)}</b>`,
    "The further ahead we look, the less the model trusts today's trend."));

  out.push(stepHTML(7, "Raw projection",
    `ŷ_raw = y_last + m · T · d`,
    `ŷ_raw = ${w.yLast.toFixed(3)} + ${w.slope.toFixed(4)} × ${h} × ${w.damping.toFixed(3)} = <b>${w.raw.toFixed(3)} m</b>`));

  out.push(stepHTML(8, "Change limit",
    `L = max(0.08, 0.35 · y_last) · (horizon / 15)^0.7`,
    `L = max(0.08, 0.35 × ${w.yLast.toFixed(3)}) × (${h}/15)^0.7 = <b>${w.maxChange.toFixed(3)} m</b> ` +
      `→ allowed ${w.lo.toFixed(3)} … ${w.hi.toFixed(3)} m`,
    "A hard guard: one forecast may not jump further than this, even when the fit is noisy."));

  out.push(stepHTML(9, "Final forecast",
    `ŷ = clamp(ŷ_raw, y_last − L, y_last + L, 0, 15)`,
    `ŷ = clamp(${w.raw.toFixed(3)}, ${w.lo.toFixed(3)}, ${w.hi.toFixed(3)}) = <b>${pred.predicted.toFixed(3)} m</b> ` +
      (pred.limited ? `<span style="color:#ff9c9c">← limit applied</span>` : `← inside the limit`)));

  out.push(stepHTML(10, "Spread of the readings",
    `σ = √( Σ(yᵢ − (ȳ + m(xᵢ − x̄)))² / n )`,
    `σ = √(${w.ssResid.toFixed(4)} / ${w.n}) = <b>${w.vol.toFixed(4)} m</b>`,
    "How far the readings sit off the fitted line — a small σ means a steady, well-behaved sea."));

  out.push(stepHTML(11, "Confidence",
    `c = 94 − (σ / max(ȳ, 0.1)) · 60 − 0.8 · horizon`,
    `c = 94 − (${w.vol.toFixed(4)} / ${Math.max(w.my, 0.1).toFixed(3)}) × 60 − 0.8 × ${h} ` +
      `= ${w.confidenceRaw.toFixed(1)} → <b>${w.confidence}%</b> (clamped to 35–94%)`));

  out.push(stepHTML(12, "Sea condition",
    `CALM if ŷ < 0.6 · MODERATE if 0.6 ≤ ŷ < 2.5 · ROUGH if ŷ ≥ 2.5`,
    `ŷ = ${pred.predicted.toFixed(2)} m → <b>${classify(pred.predicted)}</b>`));

  host.innerHTML = out.join("");

  const n = w.n;
  const picks = [...new Set([0, 1, Math.round(n * 0.25), Math.round(n * 0.5), n - 2, n - 1])]
    .filter(i => i >= 0 && i < n).sort((a, b) => a - b);
  let rows = "";
  for (const i of picks) {
    const dx = w.xs[i] - w.mx, dy = w.ys[i] - w.my;
    rows += `<tr><td>${clockLabel(w.startT + w.xs[i] * 60)}</td>` +
            `<td>${w.ys[i].toFixed(2)}</td>` +
            `<td>${sgn2(dx)}</td><td>${sgn2(dy)}</td>` +
            `<td>${sgn2(dx * dy)}</td><td>${(dx * dx).toFixed(0)}</td></tr>`;
  }
  rows += `<tr class="sum"><td>Σ · all ${n} readings</td><td>–</td><td>0</td><td>0</td>` +
          `<td>${w.num.toFixed(2)}</td><td>${grp2(w.den)}</td></tr>`;

  tbl.innerHTML = `<table class="samples">
      <thead><tr><th>time</th><th>y (m)</th><th>x−x̄</th><th>y−ȳ</th><th>(x−x̄)(y−ȳ)</th><th>(x−x̄)²</th></tr></thead>
      <tbody>${rows}</tbody>
    </table>
    <p class="cap" style="margin:8px 0 0">${picks.length} of ${n} readings listed; sums run over all of them.
    x is minutes, y is metres and <b>y = H = max − min</b> for each 2-minute window.</p>`;
}

/* ---------------------------------------------------------------- wiring */
function readPair() {
  const lo = Number($("minValue").value);
  const hi = Number($("maxValue").value);
  const valid = Number.isFinite(lo) && Number.isFinite(hi);
  const a = valid ? Math.min(lo, hi) : 0;
  const b = valid ? Math.max(lo, hi) : 0;
  return { lo: a, hi: b, valid, h: Math.max(0, b - a) };
}

function updatePairPreview() {
  const p = readPair();
  if (!p.valid) {
    $("pairPreview").textContent = "Enter two numbers for the 2-minute window.";
    return;
  }
  $("pairPreview").innerHTML =
    `H = ${signed2(p.hi)} − ${p.lo < 0 ? `(${signed2(p.lo)})` : signed2(p.lo)} = ` +
    `<b style="color:var(--green)">${p.h.toFixed(2)} m</b>`;
}

$("sendReading").addEventListener("click", () => {
  const p = readPair();
  if (!p.valid) return;
  addReading(p.lo, p.hi);
});

document.querySelectorAll(".preset").forEach(btn => {
  btn.addEventListener("click", () => {
    const p = {
      calm: [-0.20, 0.20],
      rough: [-1.50, 1.50],
      squall: [-2.10, 2.10],
      drop: [-0.10, 0.10],
    }[btn.dataset.preset];
    if (!p) return;
    $("minValue").value = p[0].toFixed(2);
    $("maxValue").value = p[1].toFixed(2);
    updatePairPreview();
  });
});

$("minValue").addEventListener("input", updatePairPreview);
$("maxValue").addEventListener("input", updatePairPreview);

document.querySelectorAll(".horizon").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".horizon").forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
    state.horizon = Number(btn.dataset.h);
    state.pending.length = 0;
    render();
  });
});

$("reset").addEventListener("click", () => {
  state.history.length = 0;
  state.pending.length = 0;
  state.errors.length = 0;
  state.horizon = 15;
  document.querySelectorAll(".horizon").forEach(b =>
    b.classList.toggle("active", b.dataset.h === "15"));
  $("minValue").value = "-0.18";
  $("maxValue").value = "0.22";
  updatePairPreview();
  try { localStorage.removeItem("falcon-readings"); } catch (e) { /* ignore */ }
  render();
});

/* ----------------------------------------------------------------- start */
resize();
updatePairPreview();
render();
