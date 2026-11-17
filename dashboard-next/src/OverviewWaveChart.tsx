import { useEffect, useRef, useState } from "react";
import type { DashboardData } from "./types";
import { recentWaveSession } from "./waveHistory";

type Point = { time: number; value: number; lower?: number; upper?: number };

const pad2 = (value: number) => String(value).padStart(2, "0");
const clock = (time: number) => {
  const date = new Date(time);
  return `${pad2(date.getHours())}:${pad2(date.getMinutes())}`;
};
const linePath = (points: number[][]) =>
  points.length < 2 ? "" : points.map(([x, y], index) => `${index === 0 ? "M" : "L"} ${x} ${y}`).join(" ");

/** Short chart label: kPa readings sit near 100, so keep two decimals; metres need two as well. */
const label = (value: number, unit: "m" | "kPa") => `${value.toFixed(2)} ${unit}`;

export default function OverviewWaveChart({ data }: { data: DashboardData }) {
  const [selected, setSelected] = useState<number | null>(null);
  const history = recentWaveSession(data.wave.history);
  const host = useRef<HTMLDivElement>(null);
  const [width, setWidth] = useState(760);

  useEffect(() => {
    const node = host.current;
    if (!node) return;
    const observer = new ResizeObserver(([entry]) => setWidth(Math.max(420, Math.round(entry.contentRect.width))));
    observer.observe(node);
    return () => observer.disconnect();
  }, [history.length >= 2]);

  if (history.length < 2)
    return (
      <div className="falcon-chart-empty">
        Collecting recent wave readings. Older sessions remain in Logs &amp; Alerts.
      </div>
    );

  const measured: Point[] = history.map((row) => ({ time: Date.parse(row.recordedAt), value: row.waveHeight }));
  const now = measured[measured.length - 1].time;
  const ready = data.ai.status === "READY" && data.ai.predictedWaveHeight != null;
  const horizon = data.ai.horizonMinutes || 15;

  const forecast: Point[] = ready
    ? (data.ai.forecastSeries || [])
        .map((row) => ({
          time: Date.parse(row.at),
          value: row.predictedWaveHeight,
          lower: row.lowerBound,
          upper: row.upperBound,
        }))
        .filter((row) => Number.isFinite(row.time) && Number.isFinite(row.value) && row.time >= now - 30_000)
        .sort((a, b) => a.time - b.time)
    : [];
  const hasForecast = forecast.length > 1;
  const end = hasForecast ? forecast[forecast.length - 1].time : now;

  // The AI also re-estimates the readings it already saw. Drawing those past
  // estimates together with the forecast gives one continuous predicted line
  // that runs beside the measured line, so the two can be compared directly.
  const pastPrediction: Point[] = data.ai.status === "READY"
    ? (data.ai.historicalPredictionSeries || [])
        .map((row) => ({ time: Date.parse(row.at), value: row.predictedWaveHeight }))
        .filter(
          (row) =>
            Number.isFinite(row.time) &&
            Number.isFinite(row.value) &&
            row.time >= measured[0].time - 1000 &&
            row.time <= now + 1000,
        )
        .sort((a, b) => a.time - b.time)
    : [];


  const values = [...measured.map((row) => row.value)];
  pastPrediction.forEach((row) => values.push(row.value));
  forecast.forEach((row) => {
    values.push(row.value);
    if (row.lower != null) values.push(row.lower);
    if (row.upper != null) values.push(row.upper);
  });
  const low = Math.min(...values);
  const high = Math.max(...values);
  const spread = Math.max(0.2, high - low);
  const rawStep = (spread * 1.35) / 5;
  const magnitude = 10 ** Math.floor(Math.log10(rawStep));
  const step = ([1, 2, 2.5, 5, 10].find((value) => value * magnitude >= rawStep) ?? 10) * magnitude;
  const min = Math.max(0, Math.floor((low - spread * 0.18) / step) * step);
  const max = Math.max(min + step, Math.ceil((high + spread * 0.2) / step) * step);
  const range = max - min;
  const ticks = Array.from({ length: Math.round(range / step) + 1 }, (_, index) => min + index * step);
  const decimals = Math.max(0, -Math.floor(Math.log10(step)));

  const left = width < 560 ? 40 : 48;
  const right = width - (width < 560 ? 62 : 88);
  const top = 28;
  const bottom = 216;
  const toY = (value: number) => bottom - ((value - min) / range) * (bottom - top);

  // The forecast is only a short tail on the right. The measured session owns
  // the plot, so the AI part is capped in pixels, not as a share of the times.
  const startTime = measured[0].time;
  const measuredSpan = Math.max(1, now - startTime);
  const forecastSpan = Math.max(0, end - now);
  const plotWidth = right - left;
  const maxForecastWidth = Math.min(plotWidth * 0.24, 190);
  const naturalForecastWidth = forecastSpan > 0
    ? plotWidth * (forecastSpan / (measuredSpan + forecastSpan))
    : 0;
  const forecastWidth = Math.min(naturalForecastWidth, maxForecastWidth);
  const splitX = right - forecastWidth;
  const nowX = splitX;
  const forecastCompressed = forecastSpan > 0 && naturalForecastWidth - forecastWidth > 1;
  const toX = (time: number) =>
    time <= now
      ? left + ((time - startTime) / measuredSpan) * (splitX - left)
      : splitX + ((time - now) / Math.max(1, forecastSpan)) * (right - splitX);

  const measuredPoints = measured.map((row) => [toX(row.time), toY(row.value)]);
  const forecastPoints = forecast.map((row) => [toX(row.time), toY(row.value)]);
  const pastPoints = pastPrediction.map((row) => [toX(row.time), toY(row.value)]);

  // One predicted line: the AI's past estimates up to now, then the forecast.
  const aiLine = pastPoints.length > 1 ? [...pastPoints, ...forecastPoints] : forecastPoints;
  const band = forecast.filter((row) => row.lower != null && row.upper != null);
  const bandPath = band.length > 1
    ? [
        `M ${toX(band[0].time)} ${toY(band[0].upper!)}`,
        ...band.slice(1).map((row) => `L ${toX(row.time)} ${toY(row.upper!)}`),
        ...band.slice().reverse().map((row) => `L ${toX(row.time)} ${toY(row.lower!)}`),
        "Z",
      ].join(" ")
    : "";

  const index = Math.min(selected ?? measured.length - 1, measured.length - 1);
  const active = measured[index];
  const activeX = toX(active.time);
  const activeY = toY(active.value);
  const activeLabel = selected === null || index === measured.length - 1 ? "right now" : clock(active.time);
  const tooltipWidth = 108;
  const tooltipX = selected === null
    ? Math.max(left + 4, activeX - tooltipWidth - 16)
    : Math.min(Math.max(activeX - tooltipWidth / 2, left + 4), right - tooltipWidth - 4);
  const tooltipY = activeY - 58 < top + 4 ? activeY + 16 : activeY - 58;

  const endValue = forecast.length ? forecast[forecast.length - 1].value : null;
  const endY = endValue != null ? toY(endValue) : 0;
  const historyTicks = Array.from({ length: 4 }, (_, tick) => startTime + (measuredSpan * tick) / 3);
  const futureMid = now + forecastSpan / 2;

  const pick = (clientX: number, bounds: DOMRect) => {
    const position = ((clientX - bounds.left) / bounds.width) * width;
    const target = position <= splitX
      ? startTime + ((position - left) / Math.max(1, splitX - left)) * measuredSpan
      : startTime + measuredSpan;
    setSelected(
      measured.reduce(
        (nearest, row, rowIndex) =>
          Math.abs(row.time - target) < Math.abs(measured[nearest].time - target) ? rowIndex : nearest,
        0,
      ),
    );
  };

  return (
    <div className="falcon-chart">
      <div className="falcon-chart-legend">
        <span className="is-current"><i />Pressure-derived estimate</span>
        <span className="is-ai"><i />Trend-baseline estimate</span>
      </div>
      <div className="falcon-chart-canvas" ref={host}>
        <svg
          viewBox={`0 0 ${width} 272`}
          role="group"
          tabIndex={0}
          aria-label="Pressure-derived wave-height history with the FALCON 15-minute research estimate. Use the left and right arrow keys to inspect readings; Escape returns to the latest."
          onPointerMove={(event) => pick(event.clientX, event.currentTarget.getBoundingClientRect())}
          onPointerLeave={() => setSelected(null)}
          onKeyDown={(event) => {
            if (event.key === "Escape") return setSelected(null);
            if (event.key !== "ArrowLeft" && event.key !== "ArrowRight") return;
            event.preventDefault();
            setSelected(Math.max(0, Math.min(measured.length - 1, index + (event.key === "ArrowLeft" ? -1 : 1))));
          }}
        >
          <defs>
            <linearGradient id="falcon-measured-fill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#2f6fd0" stopOpacity="0.14" />
              <stop offset="100%" stopColor="#2f6fd0" stopOpacity="0" />
            </linearGradient>
            <clipPath id="falcon-measured-clip">
              <rect x={left} y={top} width={Math.max(0, nowX - left)} height={bottom - top} />
            </clipPath>
          </defs>

          {hasForecast && (
            <g className="falcon-chart-future">
              <rect x={nowX} y={top - 10} width={Math.max(0, right - nowX)} height={bottom - top + 10} />
            </g>
          )}

          {ticks.map((value) => (
            <g key={value}>
              <line className="falcon-grid" x1={left} y1={toY(value)} x2={right} y2={toY(value)} />
              <text className="falcon-axis" x={left - 10} y={toY(value) + 4} textAnchor="end">
                {value.toFixed(decimals)}
              </text>
            </g>
          ))}

          <text className="falcon-axis" x={left - 10} y={top - 12} textAnchor="end">m</text>

          <path
            className="falcon-measured-area"
            d={`${linePath(measuredPoints)} L ${measuredPoints[measuredPoints.length - 1][0]} ${bottom} L ${measuredPoints[0][0]} ${bottom} Z`}
            clipPath="url(#falcon-measured-clip)"
          />
          {bandPath && <path className="falcon-band" d={bandPath} />}
          {aiLine.length > 1 && <path className="falcon-ai" d={linePath(aiLine)} />}
          <path className="falcon-measured" d={linePath(measuredPoints)} />

          <line className="falcon-now" x1={nowX} y1={top - 8} x2={nowX} y2={bottom} />
          <text className="falcon-now-label" x={nowX} y={top - 16} textAnchor="middle">now</text>

          <circle className="falcon-now-dot" cx={nowX} cy={measuredPoints[measuredPoints.length - 1][1]} r="4.6" />

          {endValue != null && forecastPoints.length > 0 && (
            <g className="falcon-end">
              <circle cx={right} cy={endY} r="4" />
              <text x={right + 10} y={endY - 3}>{label(endValue, "m")}</text>
              <text className="is-sub" x={right + 10} y={endY + 12}>Baseline in {horizon} min</text>
            </g>
          )}

          {historyTicks.map((time, tick) => (
            <g key={tick}>
              <line className="falcon-tick" x1={toX(time)} y1={bottom} x2={toX(time)} y2={bottom + 5} />
              <text
                className="falcon-axis"
                x={toX(time)}
                y={bottom + 20}
                textAnchor={tick === 0 ? "start" : tick === historyTicks.length - 1 ? "end" : "middle"}
              >
                {clock(time)}
              </text>
            </g>
          ))}
          {hasForecast && (
            <g>
              <line className="falcon-tick" x1={toX(futureMid)} y1={bottom} x2={toX(futureMid)} y2={bottom + 5} />
              <text className="falcon-axis" x={toX(futureMid)} y={bottom + 20} textAnchor="middle">
                +{Math.round(horizon / 2)} min
              </text>
            </g>
          )}

          <line className="falcon-cursor" x1={activeX} y1={activeY + 6} x2={activeX} y2={bottom} />
          <circle className="falcon-cursor-dot" cx={activeX} cy={activeY} r="3.4" />

          <g className={`falcon-tooltip ${selected === null ? "is-current" : ""}`} style={{ display: selected === null && width < 560 ? "none" : undefined }}>
            <rect x={tooltipX} y={tooltipY} width={tooltipWidth} height={42} rx="9" />
            <text className="is-value" x={tooltipX + 11} y={tooltipY + 19}>{label(active.value, "m")}</text>
            <text className="is-time" x={tooltipX + 11} y={tooltipY + 33}>{activeLabel}</text>
          </g>

          <text className="falcon-footnote" x={left} y={bottom + 38}>
            Latest session{forecastCompressed?" · forecast compressed":""} · auto scale {min.toFixed(decimals)}–{max.toFixed(decimals)} m
          </text>        </svg>
      </div>
    </div>
  );
}
