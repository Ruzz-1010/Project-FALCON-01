/* FALCON-01 — wave forecast console
 *
 * Nothing runs on a timer. A reading is added only when the user sends a
 * lowest / highest pair. The wave height is the paper's estimate:
 *
 *     H_est = max(eta) - min(eta) = highest - lowest
 *
 * The forecast itself is the shared damped-linear-trend baseline in model.js,
 * the paper's comparison method (not the trained AI model).
 */
"use strict";

const state = {
  history: [],   // {t, v, lo, hi} — t in seconds, v = H = hi - lo
  pending: [],   // forecasts waiting for their 15-minute check
  checks: [],    // completed checks, newest first
};

const $ = id => document.getElementById(id);
const MIN_READINGS = 8;
const HORIZON_MIN = 15;
const MAX_LEVEL = 15;

let shownForecast = null;

/* --------------------------------------------------------------- readings */
function addReading(lo, hi) {
  const last = state.history[state.history.length - 1];
  const t = last ? last.t + SAMPLE_INTERVAL_S : 0;
  const v = Math.max(0, Math.min(MAX_LEVEL, hi - lo));

  state.history.push({ t, v, lo, hi });
  if (state.history.length > 600) state.history.shift();

  /* A forecast is checked by the first reading at or after its target. */
  for (let i = state.pending.length - 1; i >= 0; i--) {
    const p = state.pending[i];
    if (p.targetT > t) continue;
    state.pending.splice(i, 1);
    state.checks.unshift({
      ...p,
      actualT: t,
      actual: v,
      error: Math.abs(p.predicted - v),
    });
    if (state.checks.length > 5) state.checks.pop();
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

function readingsUntilNextCheck() {
  const last = state.history[state.history.length - 1];
  const first = state.pending[0];
  if (!last || !first) return 0;
  return Math.max(1, Math.ceil((first.targetT - last.t) / SAMPLE_INTERVAL_S));
}

/* ------------------------------------------------------------------ chart */
const canvas = $("chart");
const ctx = canvas.getContext("2d");

const C = {
  grid: "rgba(160,196,205,.10)",
  gridBase: "rgba(160,196,205,.22)",
  axisInk: "#5b707a",
  axisInkSoft: "#8298a2",
  reading: "#63a9b2",
  readingDot: "#8fd3d9",
  forecast: "#c39b5f",
  forecastInk: "#e2c79a",
  actual: "#7fbf96",
  now: "rgba(99,169,178,.45)",
  target: "rgba(195,155,95,.4)",
};

function niceStep(value) {
  const pow = Math.pow(10, Math.floor(Math.log10(value)));
  const norm = value / pow;
  const mult = norm <= 1 ? 1 : norm <= 2 ? 2 : norm <= 5 ? 5 : 10;
  return mult * pow;
}

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
  const padL = 42, padR = 62, padT = 18, padB = 32;
  ctx.clearRect(0, 0, W, H);

  if (!state.history.length) return;

  const points = state.history.slice(-WINDOW);
  const firstT = points[0].t;
  const now = points[points.length - 1].t;
  const targetT = now + HORIZON_MIN * 60;
  const span = Math.max(1, targetT - firstT);

  const pred = currentPrediction();
  const shownChecks = state.checks.slice(0, 2);

  let maxV = 0;
  for (const p of points) maxV = Math.max(maxV, p.v);
  if (pred) maxV = Math.max(maxV, pred.predicted);
  for (const c of shownChecks) maxV = Math.max(maxV, c.predicted, c.actual);

  const targetMax = Math.max(0.6, maxV * 1.12);
  const step = niceStep(targetMax / 5);
  const intervals = Math.ceil(targetMax / step);
  const yMax = step * intervals;
  const tickDigits = step < 1 ? 1 : 0;

  const X = t => padL + (t - firstT) / span * (W - padL - padR);
  const Y = v => H - padB - (v / yMax) * (H - padT - padB);

  /* horizontal grid and height labels */
  ctx.font = "10.5px 'IBM Plex Mono', ui-monospace, monospace";
  ctx.textBaseline = "middle";
  for (let i = 0; i <= intervals; i++) {
    const v = step * i, y = Y(v);
    ctx.strokeStyle = i === 0 ? C.gridBase : C.grid;
    ctx.lineWidth = 1;
    ctx.beginPath(); ctx.moveTo(padL, y); ctx.lineTo(W - padR, y); ctx.stroke();
    ctx.fillStyle = C.axisInk; ctx.textAlign = "right";
    ctx.fillText(v.toFixed(tickDigits), padL - 8, y);
  }
  ctx.textAlign = "left";
  ctx.textBaseline = "top";
  ctx.fillStyle = C.axisInk;
  ctx.fillText("m", 10, 1);

  /* time markers: now and the forecast target */
  const marker = (t, label, strong) => {
    const x = X(t);
    ctx.strokeStyle = strong ? C.now : C.target;
    ctx.setLineDash(strong ? [] : [3, 4]);
    ctx.beginPath(); ctx.moveTo(x, padT); ctx.lineTo(x, H - padB); ctx.stroke();
    ctx.setLineDash([]);
    ctx.fillStyle = strong ? C.axisInkSoft : C.forecast;
    ctx.textAlign = "center";
    ctx.fillText(label, Math.min(Math.max(x, padL + 16), W - padR + 16), H - padB + 9);
  };
  marker(now, "now", true);
  if (pred) marker(targetT, `+${HORIZON_MIN} min`, false);

  /* measured readings */
  if (points.length > 1) {
    const grad = ctx.createLinearGradient(0, padT, 0, H - padB);
    grad.addColorStop(0, "rgba(99,169,178,.22)");
    grad.addColorStop(1, "rgba(99,169,178,0)");
    ctx.fillStyle = grad;
    ctx.beginPath();
    points.forEach((p, i) => {
      const x = X(p.t), y = Y(p.v);
      i ? ctx.lineTo(x, y) : ctx.moveTo(x, y);
    });
    ctx.lineTo(X(now), H - padB);
    ctx.lineTo(X(firstT), H - padB);
    ctx.closePath();
    ctx.fill();

    ctx.strokeStyle = C.reading;
    ctx.lineWidth = 1.8;
    ctx.beginPath();
    points.forEach((p, i) => i ? ctx.lineTo(X(p.t), Y(p.v)) : ctx.moveTo(X(p.t), Y(p.v)));
    ctx.stroke();
  }
  ctx.fillStyle = C.readingDot;
  for (const p of points) {
    ctx.beginPath(); ctx.arc(X(p.t), Y(p.v), 2.5, 0, Math.PI * 2); ctx.fill();
  }
  ctx.lineWidth = 1;

  /* forecasts that have already been checked */
  for (const c of shownChecks) {
    const x = X(c.actualT);
    ctx.strokeStyle = "rgba(127,191,150,.55)";
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(X(c.targetT), Y(c.predicted));
    ctx.lineTo(x, Y(c.actual));
    ctx.stroke();
    ctx.lineWidth = 1;

    ctx.fillStyle = C.forecast;
    ctx.beginPath(); ctx.arc(X(c.targetT), Y(c.predicted), 3, 0, Math.PI * 2); ctx.fill();

    ctx.fillStyle = C.actual;
    ctx.strokeStyle = "#08131a";
    ctx.lineWidth = 2;
    ctx.beginPath(); ctx.arc(x, Y(c.actual), 4.6, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
    ctx.lineWidth = 1;
  }

  /* live forecast */
  if (pred) {
    ctx.strokeStyle = C.forecast;
    ctx.lineWidth = 2;
    ctx.setLineDash([6, 4]);
    ctx.beginPath();
    ctx.moveTo(X(now), Y(pred.points[pred.points.length - 1].v));
    ctx.lineTo(X(targetT), Y(pred.predicted));
    ctx.stroke();
    ctx.setLineDash([]);
    ctx.lineWidth = 1;

    ctx.fillStyle = C.forecast;
    ctx.beginPath(); ctx.arc(X(targetT), Y(pred.predicted), 4, 0, Math.PI * 2); ctx.fill();

    ctx.fillStyle = C.forecastInk;
    ctx.textAlign = "left";
    ctx.textBaseline = "middle";
    ctx.font = "600 12.5px 'IBM Plex Mono', ui-monospace, monospace";
    ctx.fillText(fmt(pred.predicted, 2) + " m", X(targetT) + 8, Y(pred.predicted));
  }
}

/* -------------------------------------------------------------------- UI */
function renderProgress(count) {
  const filled = Math.min(count, MIN_READINGS);
  $("dots").innerHTML = Array.from({ length: MIN_READINGS }, (_, i) => {
    const on = i < filled;
    const cls = on ? (count >= MIN_READINGS ? "all" : "on") : "";
    return `<i class="${cls}"></i>`;
  }).join("");

  $("progressCount").textContent = `${filled} / ${MIN_READINGS}`;

  let text;
  if (count === 0) text = "Add one reading to begin";
  else if (count < MIN_READINGS) {
    const left = MIN_READINGS - count;
    text = `${count} of ${MIN_READINGS} readings — ${left} more to unlock`;
  } else {
    const next = readingsUntilNextCheck();
    text = next
      ? `Forecast unlocked — next check in ${next} reading${next === 1 ? "" : "s"}`
      : "Forecast unlocked — add readings to check it";
  }
  const el = $("progressText");
  el.textContent = text;
  el.classList.toggle("done", count >= MIN_READINGS);
}

function updateForecast(pred, last) {
  const locked = !pred;
  $("forecastLocked").hidden = !locked;
  $("forecastLive").hidden = locked;
  $("condition").hidden = locked;
  $("trendNote").hidden = locked;

  if (locked) {
    const need = Math.max(0, MIN_READINGS - state.history.length);
    $("lockRemaining").textContent = String(need);
    return;
  }

  const value = fmt(pred.predicted, 2);
  if (value !== shownForecast) {
    const el = $("forecast");
    el.firstElementChild.textContent = value;
    el.classList.remove("bump");
    void el.offsetWidth;
    el.classList.add("bump");
    shownForecast = value;
  }

  const cls = classify(pred.predicted);
  $("condition").textContent = cls;
  $("condition").className = "condition " + cls;

  const delta = pred.predicted - last.v;
  const trend = $("trendNote");
  if (delta > 0.02) {
    trend.textContent = "Rising";
    trend.className = "trend rising";
  } else if (delta < -0.02) {
    trend.textContent = "Falling";
    trend.className = "trend falling";
  } else {
    trend.textContent = "Steady";
    trend.className = "trend steady";
  }

  $("forecastNote").innerHTML = `Trend baseline · <b>${pred.work.n}</b> readings · ${HORIZON_MIN} min ahead`;
}

function updateScore(pred) {
  const has = state.checks.length > 0;
  $("scoreEmpty").hidden = has;
  $("scoreBody").hidden = !has;

  if (!has) {
    if (pred) {
      const next = readingsUntilNextCheck();
      $("scoreEmptyNote").textContent =
        `First check in ${next} more reading${next === 1 ? "" : "s"}.`;
    } else {
      $("scoreEmptyNote").textContent =
        "A forecast is checked by the reading at +15 minutes.";
    }
    return;
  }

  const latest = state.checks[0];
  const n = state.checks.length;
  const mae = state.checks.reduce((a, c) => a + c.error, 0) / n;

  $("scoreValue").textContent = fmt(latest.error, 2);
  $("scoreForecast").textContent = `${fmt(latest.predicted, 2)} m`;
  $("scoreActual").textContent = `${fmt(latest.actual, 2)} m`;
  $("scoreAvg").textContent =
    `MAE ${fmt(mae, 2)} m over ${n} check${n === 1 ? "" : "s"}.`;
}

function updateReadouts() {
  const last = state.history[state.history.length - 1];
  if (last) {
    $("reading").innerHTML = `${fmt(last.v, 2)}<small>m</small>`;
    $("readingPair").innerHTML = `${fmt(last.lo, 2)} / ${fmt(last.hi, 2)}<small>m</small>`;
    $("readingCount").textContent = String(state.history.length);
  } else {
    $("reading").textContent = "—";
    $("readingPair").textContent = "—";
    $("readingCount").textContent = "0";
  }
}

function updateUI() {
  const pred = currentPrediction();
  const last = state.history[state.history.length - 1];
  const count = state.history.length;

  $("chartEmpty").hidden = count > 0;
  renderProgress(count);
  updateForecast(pred, last);
  updateReadouts();
  updateScore(pred);
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
  else if (hi > MAX_LEVEL || lo > MAX_LEVEL) message = `Keep both levels at ${MAX_LEVEL} m or below.`;
  else if (hi < lo) message = "Highest must be at least the lowest.";

  return { lo, hi, valid: !message, h: Math.max(0, hi - lo), message };
}

function updatePairPreview() {
  const p = readPair();
  $("pairHeight").textContent = p.valid ? p.h.toFixed(2) : "—";
  $("pairError").textContent = p.message;
  $("pairError").hidden = p.valid;
  $("sendReading").disabled = !p.valid;
}

$("readingForm").addEventListener("submit", e => {
  e.preventDefault();
  const p = readPair();
  if (!p.valid) {
    updatePairPreview();
    $("minValue").focus();
    return;
  }
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

$("reset").addEventListener("click", () => {
  state.history.length = 0;
  state.pending.length = 0;
  state.checks.length = 0;
  shownForecast = null;
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
if (document.fonts && document.fonts.ready) {
  document.fonts.ready.then(() => { resize(); draw(); });
}
