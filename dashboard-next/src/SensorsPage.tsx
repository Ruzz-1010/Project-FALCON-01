import { Activity, BatteryCharging, ChevronDown, MapPin, Radio, Waves, Wind, X } from "lucide-react";
import { useState } from "react";
import type { DashboardData } from "./types";

type GroupStatus = "HEALTHY" | "WARNING" | "REVIEW" | "OFFLINE";
type Detail = { label: string; value: string };
type Metric = { label: string; value: string; note?: string };
type SensorGroup = {
  id: string;
  title: string;
  description: string;
  purpose: string;
  icon: typeof Waves;
  status: GroupStatus;
  metrics: Metric[];
  details: Detail[];
  calibration?: boolean;
};

const elapsed = (recordedAt: string) => Math.max(0, Date.now() - Date.parse(recordedAt));
const updated = (milliseconds: number) =>
  milliseconds < 5000 ? `${(milliseconds / 1000).toFixed(1)} s ago` : `${Math.round(milliseconds / 1000)} s ago`;
const n = (value: number | null | undefined, digits = 1, unit = "") =>
  value == null ? "Unavailable" : `${value.toFixed(digits)}${unit}`;
const health = (valid: boolean, quality = 100): GroupStatus =>
  !valid ? "OFFLINE" : quality < 60 ? "WARNING" : quality < 80 ? "REVIEW" : "HEALTHY";
const statusLabel = (status: GroupStatus) =>
  status === "HEALTHY" ? "OK" : status === "OFFLINE" ? "OFFLINE" : "CHECK";
const statusWord = (status: GroupStatus) =>
  status === "HEALTHY"
    ? "Working normally"
    : status === "OFFLINE"
      ? "No signal"
      : "Needs a check";

export default function SensorsPage({ data }: { data: DashboardData }) {
  const [expanded, setExpanded] = useState<Set<string>>(new Set());
  const simulated = data.status.dataSource === "simulator";
  const packetAge = elapsed(data.status.lastUpdate);
  const stale = packetAge > Math.max(10000, data.status.lastPacketAgeMs || 0);
  const securityWarning =
    data.current.security.vibrationDetected ||
    data.current.security.enclosureOpen ||
    data.current.security.geofenceState !== "SECURE";

  const pressureHealth = health(data.wave.valid, data.wave.quality * 100);
  const pressureStatus: GroupStatus =
    pressureHealth === "HEALTHY" && data.wave.calibration.includes("REQUIRED") ? "REVIEW" : pressureHealth;
  const gpsStatus: GroupStatus = !data.gps.valid ? "OFFLINE" : securityWarning ? "WARNING" : "HEALTHY";
  const windStatus: GroupStatus =
    data.status.windSpeed == null || !data.status.windDirection ? "OFFLINE" : "HEALTHY";
  const powerStatus: GroupStatus =
    !data.battery.valid || !data.solar.valid
      ? "OFFLINE"
      : data.battery.percentage != null && data.battery.percentage < 25
        ? "WARNING"
        : "HEALTHY";
  const systemStatus: GroupStatus =
    data.status.system !== "ONLINE"
      ? "OFFLINE"
      : stale || data.status.sensorsOnline < data.status.sensorsExpected
        ? "WARNING"
        : "HEALTHY";

  const lastSecurity = data.status.alerts.find((alert) =>
    /GEOFENCE|TAMPER|ENCLOSURE|VIBRATION/i.test(`${alert.code} ${alert.message}`),
  );

  const groups: SensorGroup[] = [
    {
      id: "wave",
      title: "Wave & Pressure",
      description: "Pressure-based wave estimate. HPT604 replacement selected; hardware integration pending.",
      purpose: "Shows the current pressure-derived wave estimate.",
      icon: Waves,
      status: pressureStatus,
      metrics: [
        { label: "Estimated Wave Height", value: n(data.wave.waveHeight, 2, " m") },
        { label: "Pressure", value: n(data.wave.filteredPressure, 2, " kPa") },
      ],
      calibration: data.wave.calibration.includes("REQUIRED"),
      details: [
        { label: "Replacement sensor", value: "Holykell HPT604 Type A (provisional)" },
        { label: "Proposed interface", value: "4–20 mA via ADS1115; not yet integrated" },
        { label: "Deployment approval", value: "Pending supplier confirmation for continuous seawater immersion" },
        { label: "Hardware verification", value: simulated ? "Demo data — no physical sensor verified" : "Sensor model not verified by telemetry" },
        { label: "Raw pressure", value: n(data.wave.rawPressure, 2, " kPa") },
        { label: "Filtered pressure", value: n(data.wave.filteredPressure, 2, " kPa") },
        { label: "Estimated wave height", value: n(data.wave.waveHeight, 2, " m") },
        { label: "Health", value: pressureStatus },
        { label: "Sampling", value: `${n(data.status.samplingFrequencyHz, 1, " Hz")} measured · 10 Hz target` },
        { label: "Last update", value: updated(packetAge) },
        { label: "Calibration", value: data.wave.calibration },
        { label: "Signal quality", value: `${Math.round(data.wave.quality * 100)}%` },
        { label: "Data mode", value: simulated ? "SIMULATED" : "LIVE" },
      ],
    },
    {
      id: "gps",
      title: "GPS & Security",
      description: "Position, deployment boundary, and enclosure security.",
      purpose: "Shows whether the buoy is in its safe area and sealed.",
      icon: MapPin,
      status: gpsStatus,
      metrics: [
        { label: "GPS", value: data.gps.fix },
        { label: "Deployment Distance", value: n(data.current.security.distanceMeters ?? data.gps.anchorDistanceMeters, 1, " m") },
        { label: "Geofence", value: data.current.security.geofenceState },
        { label: "Tamper", value: data.current.security.vibrationDetected || data.current.security.enclosureOpen ? "DETECTED" : "CLEAR" },
      ],
      details: [
        { label: "GPS receiver", value: data.gps.valid ? "REPORTING" : "OFFLINE" },
        { label: "Latitude", value: n(data.gps.latitude, 6) },
        { label: "Longitude", value: n(data.gps.longitude, 6) },
        { label: "Satellites", value: String(data.gps.satellites) },
        { label: "GPS fix", value: data.gps.fix },
        { label: "Deployment distance", value: n(data.current.security.distanceMeters ?? data.gps.anchorDistanceMeters, 1, " m") },
        { label: "Geofence", value: data.current.security.geofenceState },
        { label: "Vibration / tamper", value: data.current.security.vibrationDetected ? "DETECTED" : "CLEAR" },
        { label: "Enclosure tamper", value: data.current.security.enclosureOpen ? "OPEN" : "CLOSED" },
        { label: "Buzzer", value: data.current.security.buzzerActive ? "ACTIVE" : "OFF" },
        { label: "Last security event", value: lastSecurity?.message || "No active security event" },
        { label: "Signal quality", value: data.gps.signalQuality },
        { label: "Last update", value: updated(elapsed(data.gps.recordedAt)) },
      ],
    },
    {
      id: "wind",
      title: "Wind",
      description: "Current wind speed and direction at the station.",
      purpose: "Shows the wind measured at the buoy.",
      icon: Wind,
      status: windStatus,
      metrics: [
        { label: "Speed", value: n(data.status.windSpeed, 1, " km/h") },
        { label: "Direction", value: data.status.windDirection || "Unavailable" },
      ],
      details: [
        { label: "Anemometer", value: data.status.windSpeed == null ? "OFFLINE" : "HEALTHY" },
        { label: "Direction vane", value: data.status.windDirection ? "HEALTHY" : "OFFLINE" },
        { label: "Wind speed", value: n(data.status.windSpeed, 1, " km/h") },
        { label: "Wind direction", value: data.status.windDirection || "Unavailable" },
        { label: "ADC interface", value: "Configured; verify selected hardware" },
        { label: "Sampling", value: "1 Hz output target" },
        { label: "Calibration", value: "PENDING FIELD REFERENCE" },
        { label: "Last update", value: updated(packetAge) },
      ],
    },
    {
      id: "power",
      title: "Power",
      description: "Battery condition and available solar charging input.",
      purpose: "Shows whether the buoy has energy to keep reporting.",
      icon: BatteryCharging,
      status: powerStatus,
      metrics: [
        { label: "Battery", value: n(data.battery.percentage, 0, "%"), note: `${n(data.battery.voltage, 2, " V")} · ${n(data.battery.current, 2, " A")}` },
        { label: "Solar", value: data.solar.status, note: `${n(data.solar.voltage, 1, " V")} · ${n(data.solar.current, 2, " A")}` },
      ],
      details: [
        { label: "Battery voltage", value: n(data.battery.voltage, 2, " V") },
        { label: "Battery current", value: n(data.battery.current, 2, " A") },
        { label: "Battery percentage", value: n(data.battery.percentage, 0, "%") },
        { label: "Solar voltage", value: n(data.solar.voltage, 1, " V") },
        { label: "Solar current", value: n(data.solar.current, 2, " A") },
        { label: "Charging state", value: data.solar.charging ? "CHARGING" : "NOT CHARGING" },
        { label: "Battery monitor", value: `INA260 · ${data.battery.valid ? "HEALTHY" : "OFFLINE"}` },
        { label: "Solar monitor", value: `INA260 · ${data.solar.valid ? "HEALTHY" : "OFFLINE"}` },
        { label: "Calibration", value: "PENDING METER CHECK" },
        { label: "Last update", value: updated(Math.min(elapsed(data.battery.recordedAt), packetAge)) },
      ],
    },
    {
      id: "system",
      title: "System",
      description: "Buoy controller, Bay Station, storage, and reporting health.",
      purpose: "Checks that the controller, storage, and reporting link are working.",
      icon: Radio,
      status: systemStatus,
      metrics: [
        { label: "ESP32 buoy", value: data.current.health.esp32 },
        { label: "Bay Station", value: data.current.health.edgeComputer },
        { label: "Enclosure Temp.", value: n(data.status.internalTemperature, 1, " °C") },
        { label: "Enclosure", value: data.current.security.enclosureOpen ? "OPEN" : "CLOSED" },
        { label: "Sensors", value: `${data.status.sensorsOnline} / ${data.status.sensorsExpected} ONLINE` },
      ],
      details: [
        { label: "ESP32 buoy controller", value: data.current.health.esp32 },
        { label: "Shore Bay Station", value: data.current.health.edgeComputer },
        { label: "Enclosure temperature", value: n(data.status.internalTemperature, 1, " °C") },
        { label: "Enclosure switch", value: data.current.security.enclosureOpen ? "OPEN" : "CLOSED" },
        { label: "API health", value: data.current.health.api },
        { label: "Database health", value: data.current.health.database },
        { label: "Sensor count", value: `${data.status.sensorsOnline} / ${data.status.sensorsExpected} online` },
        { label: "Stale sensors", value: stale ? "DATA MAY BE STALE" : "NONE DETECTED" },
        { label: "Last data packet", value: updated(packetAge) },
      ],
    },
  ];

  const counts = groups.reduce(
    (result, group) => ({ ...result, [group.status]: result[group.status] + 1 }),
    { HEALTHY: 0, WARNING: 0, REVIEW: 0, OFFLINE: 0 } as Record<GroupStatus, number>,
  );
  const toggle = (id: string) =>
    setExpanded((current) => {
      const next = new Set(current);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });

  return (
    <section className="content sensor-cards-page">
      <div className="page-head">
        <div>
          <span>CHECK THE BUOY</span>
          <p>Each card shows the latest reading and whether it needs attention. Open details only when troubleshooting or checking the setup.</p>
        </div>
        <em className={`sensor-chip ${simulated ? "is-warning" : ""}`}>
          <i /> {simulated ? "SIMULATED" : "LIVE"}
        </em>
      </div>

      <div className="sensor-summary" aria-label="Sensor health summary">
        <div>
          <Activity />
          <span>Sensor status</span>
        </div>
        <dl>
          <div className="is-ok"><dt>OK</dt><dd>{counts.HEALTHY}</dd></div>
          <div className="is-check"><dt>Check</dt><dd>{counts.REVIEW + counts.WARNING}</dd></div>
          <div className="is-offline"><dt>Offline</dt><dd>{counts.OFFLINE}</dd></div>
        </dl>
      </div>

      <div className="sensor-card-grid">
        {groups.map((group) => {
          const Icon = group.icon;
          const isOpen = expanded.has(group.id);
          return (
            <article
              className={`sensor-card status-${group.status.toLowerCase()} ${isOpen ? "is-expanded" : ""}`}
              key={group.id}
            >
              <header className="sensor-card-head">
                <span className="sensor-card-icon"><Icon /></span>
                <div className="sensor-card-title">
                  <h2>{group.title}</h2>
                  <p>{group.purpose}</p>
                </div>
                <em className="sensor-card-status">
                  {statusLabel(group.status)}
                  <small>{statusWord(group.status)}</small>
                </em>
              </header>

              <div className={`sensor-card-metrics count-${group.metrics.length}`}>
                {group.metrics.map((metric) => (
                  <div className="sensor-metric" key={metric.label}>
                    <span>{metric.label}</span>
                    <strong>{metric.value}</strong>
                    {metric.note && <small>{metric.note}</small>}
                  </div>
                ))}
              </div>

              {group.calibration && (
                <span className="calibration-badge">Calibration required before field use</span>
              )}

              <button
                className="sensor-details-toggle"
                onClick={() => toggle(group.id)}
                aria-expanded={isOpen}
                aria-controls={`${group.id}-details`}
              >
                <span>{isOpen ? "Hide details" : "View details"}</span>
                <ChevronDown />
              </button>

              {isOpen && (
                <div className="sensor-technical" id={`${group.id}-details`}>
                  <div className="sensor-technical-head">
                    <strong>Sensor details</strong>
                    <button
                      type="button"
                      className="sensor-technical-close"
                      onClick={() => toggle(group.id)}
                      aria-label={`Close ${group.title} details`}
                    >
                      <X />
                    </button>
                  </div>
                  <p className="sensor-technical-note">{group.description}</p>
                  <dl className="sensor-technical-grid">
                    {group.details.map((detail) => (
                      <div key={detail.label}>
                        <dt>{detail.label}</dt>
                        <dd>{detail.value}</dd>
                      </div>
                    ))}
                  </dl>
                </div>
              )}
            </article>
          );
        })}
      </div>
    </section>
  );
}
