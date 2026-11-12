/* FALCON-01 — simple wave forecast dashboard
 *
 * Nothing runs on a timer. A reading is added only when the user sends a
 * lowest / highest pair. The wave height is the paper's estimate:
 *
 *     H = highest - lowest
 *
 * The forecast itself is the shared damped-linear-trend baseline in model.js.
 */
"use strict";

const state = {
  history: [],   // {t, v, lo, hi} — t in seconds, v = H = hi - lo
  pending: [],   // forecasts waiting for their 15-minute check
  errors: [],    // completed checks, newest first
};

const $ = id => document.getElementById(id);
const MIN_READINGS = 8;
const HORIZON_MIN = 15;
const MAX_H = 15;

/* --------------------------------------------------------------- readings */
function addReading(lo, hi) {
  const last = state.history[state.history.length - 1];
  const t = last ? last.t + SAMPLE_INTERVAL_S : 0;
  const v = Math.max(0, Math.min(MAX_H, hi - lo));

  state.history.push({ t, v, lo, hi });
  if (state.history.length > 600) state.history.shift();

  /* A forecast is checked by the first reading at or after its target. */
  for (let i = state.pending.length - 1; i >= 0; i--) {
    const p = state.pending[i];
    if (p.targetT > t) continue;
    state.pending.splice(i, 1);
    state.errors.unshift({
      ...p,
      actualT: t,
      actual: v,
      error: Math.abs(p.predicted - v),
    });
    if (state.errors.length > 5) state.errors.pop();
  }

  /* Only start forecasting once the short history exists. */
  const recent = state.history.slice(-WINDOW);
  if (recent.length >= MIN_READINGS) {
    const res = project(recent, HORIZON_MIN);
    state.pending.push({
      fromT: t,
      fromV: v,
      targetT: t + HORIZON_MIN * 60,
      predicted: res.predicted,
    });
  }

  /* calc.html reads this; it never generates its own data. */
  try {
    localStorage.setItem("falcon-readings", JSON.stringify({
      horizon: HORIZON_MIN,
      history: state.history.slice(-60),
    }));
  } catch (e) { /* storage may be disabled */ }

  render();
}

function currentPrediction() {
  const recent = state.history.slice(-WINDOW);
  if (recent.length < MIN_READINGS) return null;
  const res = project(recent, HORIZON_MIN);
  return {
    ...res,
    horizon: HORIZON_MIN,
    targetT: recent[recent.length - 1].t + HORIZON_MIN * 60,
    points: recent,
  };
}

function readingsUntilFirstCheck() {
  const last = state.history[state.history.length - 1];
  const first = state.pending[0];
  if (!last || !first) return 0;
  return Math.max(1, Math.ceil((first.targetT - last.t) / SAMPLE_INTERVAL_S));
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
  const padL = 44, padR = 64, padT = 18, padB = 32;
  ctx.clearRect(0, 0, W, H);

  if (!state.history.length) {
    ctx.fillStyle = "#7f9aab";
    ctx.font = "14px system-ui, sans-serif";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText("Add your first reading to start the chart.", W / 2, H / 2);
    return;
  }

  const points = state.history.slice(-WINDOW);
  const firstT = points[0].t;
  const now = points[points.length - 1].t;
  const targetT = now + HORIZON_MIN * 60;
  const span = Math.max(1, targetT - firstT);

  const pred = currentPrediction();
  const shownErrors = state.errors.slice(0, 2);

  let maxV = 0.8;
  for (const p of points) maxV = Math.max(maxV, p.v);
  if (pred) maxV = Math.max(maxV, pred.predicted);
  for (const e of shownErrors) maxV = Math.max(maxV, e.predicted, e.actual);
  const yMax = Math.max(0.8, Math.ceil(maxV * 1.15 * 10) / 10);

  const X = t => padL + (t - firstT) / span * (W - padL - padR);
  const Y = v => H - padB - (v / yMax) * (H - padT - padB);

  /* horizontal grid and height labels */
  ctx.font = "11.5px ui-monospace, monospace";
  ctx.textBaseline = "middle";
  for (let i = 0; i <= 3; i++) {
    const v = yMax * i / 3, y = Y(v);
    ctx.strokeStyle = i === 0 ? "#1d4051" : "#122c39";
    ctx.beginPath(); ctx.moveTo(padL, y); ctx.lineTo(W - padR, y); ctx.stroke();
    ctx.fillStyle = "#5f7f90"; ctx.textAlign = "right";
    ctx.fillText(v.toFixed(1), padL - 8, y);
  }

  /* time markers: now and the forecast target */
  ctx.textBaseline = "top";
  for (const [t, label, strong] of [[now, "now", true], [targetT, `+${HORIZON_MIN} min`, false]]) {
    const x = X(t);
    ctx.strokeStyle = strong ? "#2f6a82" : "#3b5563";
    ctx.setLineDash(strong ? [] : [3, 4]);
    ctx.beginPath(); ctx.moveTo(x, padT); ctx.lineTo(x, H - padB); ctx.stroke();
    ctx.setLineDash([]);
    ctx.fillStyle = strong ? "#8fb8cc" : "#ffb98a";
    ctx.textAlign = "center";
    ctx.fillText(label, x, H - padB + 9);
  }

  /* measured readings */
  if (points.length > 1) {
    ctx.strokeStyle = "#5aa9c8";
    ctx.lineWidth = 2;
    ctx.beginPath();
    points.forEach((p, i) => i ? ctx.lineTo(X(p.t), Y(p.v)) : ctx.moveTo(X(p.t), Y(p.v)));
    ctx.stroke();
  }
  ctx.fillStyle = "#7fc3dc";
  for (const p of points) {
    ctx.beginPath(); ctx.arc(X(p.t), Y(p.v), 2.6, 0, Math.PI * 2); ctx.fill();
  }
  ctx.lineWidth = 1;

  /* forecasts that have already been checked */
  for (const e of shownErrors) {
    const x = X(e.actualT);
    ctx.strokeStyle = "rgba(78,224,160,0.6)";
    ctx.lineWidth = 2;
    ctx.beginPath(); ctx.moveTo(x, Y(e.predicted)); ctx.lineTo(x, Y(e.actual)); ctx.stroke();
    ctx.lineWidth = 1;

    ctx.fillStyle = "#ffb98a";
    ctx.beginPath(); ctx.arc(X(e.targetT), Y(e.predicted), 3.2, 0, Math.PI * 2); ctx.fill();

    ctx.fillStyle = "#4ee0a0";
    ctx.strokeStyle = "#061620";
    ctx.lineWidth = 2;
    ctx.beginPath(); ctx.arc(x, Y(e.actual), 5, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
    ctx.lineWidth = 1;
  }

  /* live forecast */
  if (pred) {
    ctx.strokeStyle = "#ff8a3d";
    ctx.lineWidth = 2.5;
    ctx.setLineDash([7, 4]);
    ctx.beginPath();
    ctx.moveTo(X(now), Y(pred.points[pred.points.length - 1].v));
    ctx.lineTo(X(targetT), Y(pred.predicted));
    ctx.stroke();
    ctx.setLineDash([]);
    ctx.lineWidth = 1;

    ctx.fillStyle = "#ff8a3d";
    ctx.beginPath(); ctx.arc(X(targetT), Y(pred.predicted), 4.5, 0, Math.PI * 2); ctx.fill();

    ctx.fillStyle = "#ffd0a8";
    ctx.textAlign = "left";
    ctx.textBaseline = "middle";
    ctx.font = "600 13px ui-monospace, monospace";
    ctx.fillText(fmt(pred.predicted, 2) + " m", X(targetT) + 9, Y(pred.predicted));
  }
}

/* -------------------------------------------------------------------- UI */
function renderProgress(count) {
  $("dots").innerHTML = Array.from({ length: MIN_READINGS }, (_, i) =>
    `<i class="${i < count ? (count >= MIN_READINGS ? "all" : "on") : ""}"></i>`).join("");

  const shown = Math.min(count, MIN_READINGS);
  let text;
  if (count === 0) text = `0 of ${MIN_READINGS} readings — add one to begin`;
  else if (count < MIN_READINGS) {
    const left = MIN_READINGS - count;
    text = `${shown} of ${MIN_READINGS} readings — ${left} more to unlock`;
  } else {
    text = `${MIN_READINGS} of ${MIN_READINGS} readings — forecast unlocked ✓`;
  }
  $("progressText").textContent = text;
  $("progressText").classList.toggle("done", count >= MIN_READINGS);
}

function updateUI() {
  const pred = currentPrediction();
  const last = state.history[state.history.length - 1];
  const count = state.history.length;

  if (last) {
    $("reading").innerHTML = `${fmt(last.v, 2)}<small>m</small>`;
    $("readingNote").innerHTML =
      `Reading ${count} · lowest <b>${fmt(last.lo, 2)} m</b> · ` +
      `highest <b>${fmt(last.hi, 2)} m</b>`;
  } else {
    $("reading").textContent = "–";
    $("readingNote").textContent = "No readings yet.";
  }

  if (pred) {
    const cls = classify(pred.predicted);
    $("forecast").innerHTML = `${fmt(pred.predicted, 2)}<small>m</small>`;
    $("condition").hidden = false;
    $("condition").textContent = cls;
    $("condition").className = "pill " + cls;
    $("forecastNote").innerHTML = `Based on <b>${pred.work.n}</b> readings.`;
  } else {
    $("forecast").textContent = "–";
    $("condition").hidden = true;
    const need = Math.max(0, MIN_READINGS - count);
    $("forecastNote").textContent = `Locked — ${need} more reading${need === 1 ? "" : "s"} needed.`;
  }

  renderProgress(count);

  const tbody = $("errors");
  if (!state.errors.length) {
    $("scoreBody").hidden = true;
    $("verdict").textContent = pred
      ? `No check yet. The first check appears after about ${readingsUntilFirstCheck()} more readings.`
      : "No checks yet. A forecast is checked when the reading 15 minutes later arrives.";
  } else {
    $("scoreBody").hidden = false;
    const latest = state.errors[0];
    $("verdict").innerHTML =
      `The forecast said <b>${fmt(latest.predicted, 2)} m</b>. ` +
      `The reading 15 minutes later was <b>${fmt(latest.actual, 2)} m</b>. ` +
      `Off by: <b>${fmt(latest.error, 2)} m</b>.`;

    tbody.innerHTML = state.errors.map(e =>
      `<tr><td>${fmt(e.predicted, 2)} m</td>` +
      `<td>${fmt(e.actual, 2)} m</td>` +
      `<td>${fmt(e.error, 2)} m</td></tr>`).join("");

    const n = state.errors.length;
    const mae = state.errors.reduce((a, e) => a + e.error, 0) / n;
    $("avg").innerHTML =
      `Average miss: <b>${mae.toFixed(2)} m</b> over ${n} check${n === 1 ? "" : "s"}.`;
  }
}

function render() {
  draw();
  updateUI();
}

/* ---------------------------------------------------------------- wiring */
function readPair() {
  const loRaw = $("minValue").value.trim();
  const hiRaw = $("maxValue").value.trim();
  const lo = Number(loRaw);
  const hi = Number(hiRaw);
  const filled = loRaw !== "" && hiRaw !== "";

  let message = "";
  if (!filled) message = "Enter both water levels.";
  else if (!Number.isFinite(lo) || !Number.isFinite(hi)) message = "Enter a number in both boxes.";
  else if (lo < 0 || hi < 0) message = "Water levels cannot be negative here.";
  else if (hi < lo) message = "Highest must be at least the lowest.";

  return { lo, hi, valid: !message, h: Math.max(0, hi - lo), message };
}

function updatePairPreview() {
  const p = readPair();
  $("pairHeight").textContent = p.valid ? p.h.toFixed(2) : "–";
  $("pairError").textContent = p.message;
  $("pairError").hidden = p.valid;
  $("sendReading").disabled = !p.valid;
}

$("sendReading").addEventListener("click", () => {
  const p = readPair();
  if (!p.valid) return;
  addReading(p.lo, p.hi);
});

document.querySelectorAll(".preset").forEach(btn => {
  btn.addEventListener("click", () => {
    const pair = {
      calm: ["0.15", "0.55"],
      rough: ["0.20", "3.20"],
      squall: ["0.30", "4.50"],
    }[btn.dataset.preset];
    if (!pair) return;
    $("minValue").value = pair[0];
    $("maxValue").value = pair[1];
    updatePairPreview();
  });
});

$("minValue").addEventListener("input", updatePairPreview);
$("maxValue").addEventListener("input", updatePairPreview);
for (const id of ["minValue", "maxValue"]) {
  $(id).addEventListener("keydown", e => {
    if (e.key !== "Enter") return;
    e.preventDefault();
    $("sendReading").click();
  });
}

$("reset").addEventListener("click", () => {
  state.history.length = 0;
  state.pending.length = 0;
  state.errors.length = 0;
  $("minValue").value = "0.10";
  $("maxValue").value = "0.50";
  updatePairPreview();
  try { localStorage.removeItem("falcon-readings"); } catch (e) { /* ignore */ }
  render();
});

/* ----------------------------------------------------------------- start */
resize();
updatePairPreview();
render();
