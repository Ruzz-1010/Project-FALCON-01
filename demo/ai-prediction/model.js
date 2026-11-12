/* FALCON-01 — shared demo model
 *
 * A JavaScript port of edge/falcon_edge/forecast.py: a damped linear trend over
 * the recent wave-height history, plus the sea-condition classifier.
 *
 * The arithmetic here is expressed in minutes (x = minutes, m = m/min). It is
 * the same least-squares fit as the Python version, which works in seconds.
 */

const MODEL_NAME = "wave-short-term";
const MODEL_VERSION = "1.0.0-demo";
const SAMPLE_INTERVAL_S = 120;   // one buoy reading every 2 minutes
const WINDOW = 30;               // readings used for the fit (1 hour)
const SAMPLE_LABEL = "2 min";

const COND_TEXT = {
  CALM: "calm",
  MODERATE: "moderate",
  ROUGH: "rough",
};

function classify(h) { return h < 0.6 ? "CALM" : h < 2.5 ? "MODERATE" : "ROUGH"; }

function project(points, horizonMin) {
  const n = points.length;
  const origin = points[0].t;
  const xs = points.map(p => (p.t - origin) / 60);   // minutes
  const ys = points.map(p => p.v);                   // metres
  const sumX = xs.reduce((a, b) => a + b, 0);
  const sumY = ys.reduce((a, b) => a + b, 0);
  const mx = sumX / n;
  const my = sumY / n;

  let den = 0, num = 0;
  for (let i = 0; i < n; i++) { den += (xs[i] - mx) ** 2; num += (xs[i] - mx) * (ys[i] - my); }
  const slope = den === 0 ? 0 : num / den;           // m per minute
  const horizon = horizonMin;                        // minutes
  const damping = 1 / (1 + horizon / 5);             // 5 min = 300 s in the Python version
  const raw = ys[n - 1] + slope * horizon * damping;
  const maxChange = Math.max(0.08, ys[n - 1] * 0.35) * Math.pow(horizonMin / 15, 0.7);

  let projected = Math.min(ys[n - 1] + maxChange, Math.max(ys[n - 1] - maxChange, raw));
  projected = Math.max(0, Math.min(15, projected));

  const residuals = xs.map((x, i) => ys[i] - (my + slope * (x - mx)));
  const ssResid = residuals.reduce((a, r) => a + r * r, 0);
  const vol = Math.sqrt(ssResid / n);
  const confidenceRaw = 94 - vol / Math.max(my, 0.1) * 60 - horizonMin * 0.8;
  const confidence = Math.round(Math.max(35, Math.min(94, confidenceRaw)));

  const work = {
    n, origin, xs, ys, sumX, sumY, mx, my, num, den, slope, horizon, damping,
    yLast: ys[n - 1], raw, maxChange,
    lo: ys[n - 1] - maxChange, hi: ys[n - 1] + maxChange,
    ssResid, vol, confidenceRaw, confidence,
    startT: points[0].t, endT: points[n - 1].t,
  };

  return { predicted: projected, confidence, slope, damping, raw, maxChange, vol,
           limited: Math.abs(projected - raw) > 0.0005, samples: n, work };
}

/* --------------------------------------------------------------- helpers */
const fmt = (v, d = 2) => (v == null || Number.isNaN(v)) ? "–" : v.toFixed(d);
const clockLabel = t => {
  const m = Math.floor(t / 60);
  return m >= 60 ? `${Math.floor(m / 60)}h${String(m % 60).padStart(2, "0")}m` : `${m}m`;
};
const grp = v => Math.round(v).toLocaleString("en-US");
