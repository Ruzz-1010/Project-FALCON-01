"use strict";

const POLL_INTERVAL_MS = 2000;
const MAX_CHART_POINTS = 60;
const EDGE_API_URL = window.location.port === "8765" ? "" : "http://127.0.0.1:8765";
const PRESENTATION_CONTROLS = true;
const ALERT_NOTIFICATION_COOLDOWN_MS = 60000;
const readings = [];
const DEMO_DATA = {
  system: "ONLINE",
  monitoring: true,
  temperature: 28.4,
  battery: 87,
  seaCondition: "CALM",
  waveLevel: 0.4,
  tilt: 1.8,
  uptime: 42672,
  clients: 3,
  gps: "3D FIX · 12 SAT",
  solar: "CHARGING",
  security: "ARMED"
};
const elements = {
  systemStatus: document.getElementById("systemStatus"),
  systemIndicator: document.getElementById("systemIndicator"),
  lastUpdated: document.getElementById("lastUpdated"),
  clients: document.getElementById("clients"),
  monitoringStatus: document.getElementById("monitoringStatus"),
  monitoringButton: document.getElementById("monitoringButton"),
  restartButton: document.getElementById("restartButton"),
  temperature: document.getElementById("temperature"),
  environmentTemperature: document.getElementById("environmentTemperature"),
  batteryValue: document.getElementById("batteryValue"),
  powerBattery: document.getElementById("powerBattery"),
  powerBatteryBar: document.getElementById("powerBatteryBar"),
  seaCondition: document.getElementById("seaCondition"),
  motionSeaCondition: document.getElementById("motionSeaCondition"),
  tilt: document.getElementById("tilt"),
  motionTilt: document.getElementById("motionTilt"),
  waveLevel: document.getElementById("waveLevel"),
  motionWave: document.getElementById("motionWave"),
  uptime: document.getElementById("uptime"),
  gpsStatus: document.getElementById("gpsStatus"),
  solarStatus: document.getElementById("solarStatus"),
  securityStatus: document.getElementById("securityStatus"),
  actionMessage: document.getElementById("actionMessage"),
  chart: document.getElementById("trendChart"),
  chartEmpty: document.getElementById("chartEmpty"),
  viewTitle: document.getElementById("viewTitle"),
  menuButton: document.getElementById("menuButton"),
  sidebarScrim: document.getElementById("sidebarScrim")
};
elements.dataModeBadge = document.getElementById("dataModeBadge");
elements.scenarioSelect = document.getElementById("scenarioSelect");
elements.activityList = document.getElementById("activityList");
elements.activityStatus = document.getElementById("activityStatus");
elements.forecastHorizon = document.getElementById("forecastHorizon");
elements.forecastGrid = document.getElementById("forecastGrid");
elements.forecastNote = document.getElementById("forecastNote");
elements.modelScore = document.getElementById("modelScore");
elements.metricGrid = document.getElementById("metricGrid");
elements.evaluationRows = document.getElementById("evaluationRows");
elements.validationChart = document.getElementById("validationChart");
elements.notificationButton = document.getElementById("notificationButton");
elements.notificationCount = document.getElementById("notificationCount");
[
  "salinity", "airTemperature", "humidity", "pressure", "waterLevel", "windSpeed", "windCondition",
  "roll", "pitch", "yaw", "coordinates", "anchorDistance", "driftStatus", "surfaceSpeed",
  "batteryVoltage", "batteryCurrent", "solarVoltage", "chargingCurrent", "enclosureTemperature",
  "enclosureCondition", "batteryTemperature", "intakeFanRpm", "exhaustFanRpm", "sensorHealth",
  "storageUsage", "memoryUsage", "cpuLoad"
].forEach((id) => { elements[id] = document.getElementById(id); });

const viewTitles = {
  overview: "Station overview",
  environment: "Environmental monitoring",
  motion: "Motion monitoring",
  navigation: "Navigation",
  power: "Power monitoring",
  cooling: "Cooling system",
  diagnostics: "Diagnostics",
  activity: "Station activity"
};

let pollTimer = null;
let pollInFlight = false;
let messageTimer = null;
let demoMonitoring = true;
let latestForecast = null;
let latestValidation = null;
let alertBaselineReady = false;
let lastSeenAlertId = 0;
let unreadAlertCount = 0;
const lastNotificationByCode = new Map();

function validNumber(value, fallback = 0) {
  const number = Number(value);
  return Number.isFinite(number) ? number : fallback;
}

function validText(value, fallback = "UNAVAILABLE") {
  return typeof value === "string" && value.trim() ? value.trim() : fallback;
}

function formatUptime(value) {
  const total = Math.max(0, Math.floor(validNumber(value)));
  const hours = Math.floor(total / 3600);
  const minutes = Math.floor((total % 3600) / 60);
  return `${hours}h ${minutes}m ${total % 60}s`;
}

function showMessage(message, type = "info") {
  clearTimeout(messageTimer);
  elements.actionMessage.textContent = message;
  elements.actionMessage.dataset.type = type;
  elements.actionMessage.classList.add("is-visible");
  messageTimer = setTimeout(() => elements.actionMessage.classList.remove("is-visible"), 4500);
}

function updateNotificationButton() {
  const supported = "Notification" in window;
  const enabled = supported && Notification.permission === "granted";
  elements.notificationButton.classList.toggle("is-enabled", enabled);
  elements.notificationButton.classList.toggle("has-alerts", unreadAlertCount > 0);
  elements.notificationCount.hidden = unreadAlertCount === 0;
  elements.notificationCount.textContent = unreadAlertCount > 99 ? "99+" : String(unreadAlertCount);
  elements.notificationButton.title = !supported ? "Browser notifications are unavailable" : enabled ? "System notifications enabled" : "Enable system alert notifications";
  elements.notificationButton.setAttribute("aria-label", elements.notificationButton.title);
}

async function handleNotificationButton() {
  unreadAlertCount = 0;
  updateNotificationButton();
  setView("activity");
  if (!("Notification" in window)) {
    showMessage("This browser does not support system notifications.", "error");
    return;
  }
  if (Notification.permission === "default") {
    const permission = await Notification.requestPermission();
    updateNotificationButton();
    showMessage(permission === "granted" ? "System alert notifications enabled." : "Notification permission was not enabled.", permission === "granted" ? "success" : "error");
  } else if (Notification.permission === "denied") {
    showMessage("Notifications are blocked. Enable them in the browser site settings.", "error");
  }
}

function processAlertNotifications(items) {
  if (!Array.isArray(items)) return;
  if (items.length === 0) {
    alertBaselineReady = true;
    return;
  }
  const maximumId = Math.max(...items.map((item) => Number(item.id) || 0));
  if (!alertBaselineReady) {
    lastSeenAlertId = maximumId;
    alertBaselineReady = true;
    return;
  }
  const fresh = items.filter((item) => (Number(item.id) || 0) > lastSeenAlertId);
  lastSeenAlertId = Math.max(lastSeenAlertId, maximumId);
  if (!fresh.length) return;
  const newestByCode = new Map();
  fresh.forEach((item) => newestByCode.set(item.code, item));
  const now = Date.now();
  const actionable = [...newestByCode.values()].filter((item) => now - (lastNotificationByCode.get(item.code) || 0) >= ALERT_NOTIFICATION_COOLDOWN_MS);
  if (!actionable.length) return;
  actionable.forEach((item) => lastNotificationByCode.set(item.code, now));
  unreadAlertCount = Math.min(999, unreadAlertCount + actionable.length);
  updateNotificationButton();
  const topAlert = actionable.find((item) => item.severity === "critical") || actionable[0];
  showMessage(`${topAlert.severity === "critical" ? "CRITICAL" : "WARNING"}: ${topAlert.message}`, "error");
  if (!("Notification" in window) || Notification.permission !== "granted") return;
  actionable.forEach((item) => {
    const notification = new Notification(`FALCON ${item.severity === "critical" ? "Critical Alert" : "Warning"}`, {
      body: item.message,
      icon: "/falcon-logo.jpg",
      tag: `falcon-${item.code}`,
      renotify: true
    });
    notification.onclick = () => { window.focus(); setView("activity"); notification.close(); };
  });
}

function setView(viewName) {
  const nextView = viewTitles[viewName] ? viewName : "overview";
  document.querySelectorAll("[data-page]").forEach((view) => {
    view.classList.toggle("is-active", view.dataset.page === nextView);
  });
  document.querySelectorAll("[data-view]").forEach((button) => {
    const active = button.dataset.view === nextView;
    button.classList.toggle("is-active", active);
    if (active) button.setAttribute("aria-current", "page");
    else button.removeAttribute("aria-current");
  });
  elements.viewTitle.textContent = viewTitles[nextView];
  if (nextView === "activity" && unreadAlertCount > 0) {
    unreadAlertCount = 0;
    updateNotificationButton();
  }
  document.body.classList.remove("sidebar-open");
  if (nextView === "overview") requestAnimationFrame(drawChart);
}

function addReading(temperature, wave) {
  readings.push({temperature, wave});
  if (readings.length > MAX_CHART_POINTS) readings.shift();
  elements.chartEmpty.hidden = readings.length > 1;
  drawChart();
}

function drawSeries(context, values, min, max, width, height, color) {
  const range = Math.max(max - min, 1);
  context.beginPath();
  values.forEach((value, index) => {
    const x = (index / Math.max(values.length - 1, 1)) * width;
    const y = height - ((value - min) / range) * height;
    if (index === 0) context.moveTo(x, y);
    else context.lineTo(x, y);
  });
  context.strokeStyle = color;
  context.lineWidth = 2;
  context.lineJoin = "round";
  context.stroke();
}

function drawChart() {
  if (!elements.chart || readings.length < 2) return;
  const context = elements.chart.getContext("2d");
  const bounds = elements.chart.getBoundingClientRect();
  if (!context || bounds.width < 20 || bounds.height < 20) return;

  const ratio = Math.min(window.devicePixelRatio || 1, 2);
  elements.chart.width = Math.floor(bounds.width * ratio);
  elements.chart.height = Math.floor(bounds.height * ratio);
  context.scale(ratio, ratio);
  context.clearRect(0, 0, bounds.width, bounds.height);

  const inset = {left: 8, top: 10, right: 8, bottom: 12};
  const width = bounds.width - inset.left - inset.right;
  const height = bounds.height - inset.top - inset.bottom;
  context.save();
  context.translate(inset.left, inset.top);

  context.strokeStyle = "rgba(184,217,224,.09)";
  context.lineWidth = 1;
  for (let row = 0; row <= 4; row += 1) {
    const y = (height / 4) * row;
    context.beginPath();
    context.moveTo(0, y);
    context.lineTo(width, y);
    context.stroke();
  }

  const temperatures = readings.map((reading) => reading.temperature);
  const waves = readings.map((reading) => reading.wave);
  const tempMin = Math.min(...temperatures) - 1;
  const tempMax = Math.max(...temperatures) + 1;
  const waveMax = Math.max(1, ...waves) * 1.15;
  drawSeries(context, temperatures, tempMin, tempMax, width, height, "#4fd5e7");
  drawSeries(context, waves, 0, waveMax, width, height, "#efba67");
  context.restore();
}

function renderStatus(data) {
  const monitoring = data.monitoring === true;
  const temperature = validNumber(data.temperature);
  const waveValid = typeof data.waveLevel === "number" && Number.isFinite(data.waveLevel);
  const wave = validNumber(data.waveLevel);
  const tilt = validNumber(data.tilt);
  const battery = Math.max(0, Math.min(100, validNumber(data.battery)));
  const seaCondition = validText(data.seaCondition);

  elements.systemStatus.textContent = validText(data.system, "ONLINE");
  elements.systemIndicator.classList.remove("is-offline");
  elements.systemIndicator.innerHTML = "<i></i>LOCAL";
  elements.clients.textContent = Math.max(0, Math.floor(validNumber(data.clients)));
  elements.lastUpdated.textContent = new Date().toLocaleTimeString();
  elements.monitoringStatus.textContent = monitoring ? "ACTIVE" : "STOPPED";
  elements.monitoringButton.textContent = monitoring ? "Stop monitoring" : "Start monitoring";
  elements.temperature.textContent = temperature.toFixed(1);
  elements.environmentTemperature.textContent = temperature.toFixed(1);
  elements.batteryValue.textContent = `${Math.round(battery)}%`;
  elements.powerBattery.textContent = `${Math.round(battery)}%`;
  elements.powerBatteryBar.style.width = `${battery}%`;
  elements.seaCondition.textContent = seaCondition;
  elements.motionSeaCondition.textContent = seaCondition;
  elements.tilt.textContent = `${tilt.toFixed(1)}\u00B0`;
  elements.motionTilt.textContent = `${tilt.toFixed(1)}\u00B0`;
  elements.waveLevel.textContent = waveValid ? `${wave.toFixed(1)} m` : "-- m";
  elements.motionWave.textContent = waveValid ? `${wave.toFixed(1)} m` : "-- m";
  elements.uptime.textContent = formatUptime(data.uptime);
  elements.gpsStatus.textContent = validText(data.gps, "WAITING FOR GPS");
  elements.solarStatus.textContent = validText(data.solar, "STANDBY");
  elements.securityStatus.textContent = validText(data.security);
  elements.salinity.textContent = validNumber(data.salinity, 33.8).toFixed(1);
  elements.airTemperature.textContent = validNumber(data.airTemperature, 30.1).toFixed(1);
  elements.humidity.textContent = validNumber(data.humidity, 78).toFixed(0);
  elements.pressure.textContent = validNumber(data.pressure, 1009).toFixed(1);
  elements.waterLevel.textContent = validNumber(data.waterLevel, 1.42).toFixed(2);
  const windSpeed = validNumber(data.windSpeed, 8.6);
  elements.windSpeed.textContent = windSpeed.toFixed(1);
  elements.windCondition.textContent = windSpeed >= 30 ? "● STRONG WIND" : windSpeed >= 15 ? "● MODERATE BREEZE" : "● LIGHT BREEZE";
  elements.windCondition.style.color = windSpeed >= 30 ? "var(--coral)" : windSpeed >= 15 ? "var(--amber)" : "var(--green)";
  elements.roll.textContent = `${validNumber(data.roll, tilt).toFixed(1)}° starboard`;
  elements.pitch.textContent = `${validNumber(data.pitch, .9).toFixed(1)}° bow`;
  elements.yaw.textContent = `${validNumber(data.yaw, 41.6).toFixed(1)}° NE`;
  const latitude = validNumber(data.latitude, 16.6687);
  const longitude = validNumber(data.longitude, 120.3240);
  elements.coordinates.textContent = `${latitude.toFixed(4)}° N, ${longitude.toFixed(4)}° E`;
  const anchorDistance = validNumber(data.anchorDistance, 3.4);
  elements.anchorDistance.textContent = `${anchorDistance.toFixed(1)} m from center`;
  elements.driftStatus.textContent = anchorDistance > 20 ? "DRIFT WARNING" : "Secure";
  elements.driftStatus.className = anchorDistance > 20 ? "warn-text" : "good-text";
  elements.surfaceSpeed.textContent = `${validNumber(data.surfaceSpeed, .12).toFixed(2)} knots`;
  elements.batteryVoltage.textContent = `${validNumber(data.batteryVoltage, 12.7).toFixed(2)} V`;
  elements.batteryCurrent.textContent = `${validNumber(data.batteryCurrent, -.82).toFixed(2)} A`;
  elements.solarVoltage.textContent = `${validNumber(data.solarVoltage, 18.4).toFixed(1)} V`;
  const chargingCurrent = validNumber(data.chargingCurrent, 2.16);
  elements.chargingCurrent.textContent = `${chargingCurrent >= 0 ? "+" : ""}${chargingCurrent.toFixed(2)} A`;
  const enclosureTemperature = validNumber(data.enclosureTemperature, 34.2);
  elements.enclosureTemperature.textContent = enclosureTemperature.toFixed(1);
  elements.enclosureCondition.textContent = enclosureTemperature >= 50 ? "● OVERHEATING" : "● NORMAL";
  elements.enclosureCondition.style.color = enclosureTemperature >= 50 ? "var(--coral)" : "var(--green)";
  elements.batteryTemperature.textContent = validNumber(data.batteryTemperature, 31.7).toFixed(1);
  elements.intakeFanRpm.textContent = Math.round(validNumber(data.intakeFanRpm, 1240)).toLocaleString();
  elements.exhaustFanRpm.textContent = Math.round(validNumber(data.exhaustFanRpm, 1180)).toLocaleString();
  elements.sensorHealth.textContent = data.scenario === "sensor_fault" ? "7 of 8 online" : "8 of 8 online";
  elements.sensorHealth.className = data.scenario === "sensor_fault" ? "warn-text" : "good-text";
  elements.storageUsage.textContent = `${Math.round(validNumber(data.storageUsage, 29))}%`;
  elements.memoryUsage.textContent = `${Math.round(validNumber(data.memoryUsage, 42))}%`;
  elements.cpuLoad.textContent = `${Math.round(validNumber(data.cpuLoad, 18))}%`;
  if (waveValid) addReading(temperature, wave);
}

function renderAlerts(items) {
  if (!elements.activityList) return;
  elements.activityList.replaceChildren();
  if (!Array.isArray(items) || items.length === 0) {
    const row = document.createElement("div");
    row.className = "activity-empty";
    const copy = document.createElement("div");
    const title = document.createElement("strong");
    const description = document.createElement("p");
    title.textContent = "No safety alerts recorded";
    description.textContent = "Select a test scenario below to verify the monitoring pipeline.";
    copy.append(title, description);
    row.append(copy);
    elements.activityList.append(row);
    elements.activityStatus.textContent = "ALL CLEAR";
    elements.activityStatus.className = "tag tag-good";
    return;
  }

  items.slice(0, 30).forEach((item) => {
    const row = document.createElement("div");
    const time = document.createElement("time");
    const dot = document.createElement("i");
    const copy = document.createElement("div");
    const title = document.createElement("strong");
    const description = document.createElement("p");
    const meta = document.createElement("span");
    const date = new Date(item.recordedAt);
    time.textContent = Number.isNaN(date.getTime()) ? "--:--" : date.toLocaleTimeString([], {hour: "2-digit", minute: "2-digit"});
    dot.className = `event-dot ${item.severity === "critical" ? "critical" : "warn"}`;
    title.textContent = String(item.code || "SENSOR_ALERT").replaceAll("_", " ");
    description.textContent = item.message || "Sensor threshold triggered.";
    meta.textContent = `Sample #${item.telemetryId || "--"}`;
    copy.append(title, description);
    row.append(time, dot, copy, meta);
    elements.activityList.append(row);
  });
  const hasCritical = items.some((item) => item.severity === "critical");
  elements.activityStatus.textContent = hasCritical ? "CRITICAL ALERT" : `${items.length} ALERTS`;
  elements.activityStatus.className = hasCritical ? "tag tag-critical" : "tag tag-warn";
}

function renderForecast(forecast) {
  latestForecast = forecast;
  const horizon = elements.forecastHorizon.value;
  const predictions = forecast && forecast.horizons ? forecast.horizons[horizon] : null;
  elements.forecastGrid.replaceChildren();
  ["waveLevel", "windSpeed", "waterLevel", "temperature", "battery"].forEach((field) => {
    const prediction = predictions && predictions[field];
    const card = document.createElement("div");
    const label = document.createElement("span");
    const value = document.createElement("strong");
    const confidence = document.createElement("small");
    label.textContent = prediction ? prediction.label : field.replace(/([A-Z])/g, " $1");
    value.textContent = prediction ? `${prediction.value} ` : "-- ";
    const unit = document.createElement("em");
    unit.textContent = prediction ? prediction.unit : "";
    value.append(unit);
    confidence.textContent = prediction ? `${prediction.confidence}% MODEL CONFIDENCE` : "COLLECTING HISTORY";
    card.append(label, value, confidence);
    elements.forecastGrid.append(card);
  });
  elements.forecastNote.textContent = `${forecast.status || "COLLECTING"} · ${forecast.sampleCount || 0} samples · ${forecast.model || "model warming up"}. Presentation forecast only; not validated for safety decisions.`;
}

function drawValidationChart() {
  const rows = latestValidation && latestValidation.comparisons;
  if (!elements.validationChart || !Array.isArray(rows) || rows.length < 2) return;
  const context = elements.validationChart.getContext("2d");
  const bounds = elements.validationChart.getBoundingClientRect();
  if (!context || bounds.width < 20 || bounds.height < 20) return;
  const ratio = Math.min(window.devicePixelRatio || 1, 2);
  elements.validationChart.width = Math.floor(bounds.width * ratio);
  elements.validationChart.height = Math.floor(bounds.height * ratio);
  context.scale(ratio, ratio);
  context.clearRect(0, 0, bounds.width, bounds.height);
  const allValues = rows.flatMap((row) => [row.actual, row.predicted]);
  const minimum = Math.min(...allValues) - .03;
  const maximum = Math.max(...allValues) + .03;
  context.strokeStyle = "rgba(164,207,211,.08)";
  for (let index = 0; index <= 3; index += 1) {
    const y = 8 + ((bounds.height - 16) / 3) * index;
    context.beginPath(); context.moveTo(0, y); context.lineTo(bounds.width, y); context.stroke();
  }
  const plot = (key, color, dashed) => {
    context.beginPath();
    rows.forEach((row, index) => {
      const x = (index / (rows.length - 1)) * bounds.width;
      const y = bounds.height - 8 - ((row[key] - minimum) / Math.max(maximum - minimum, .01)) * (bounds.height - 16);
      if (index === 0) context.moveTo(x, y); else context.lineTo(x, y);
    });
    context.setLineDash(dashed ? [5, 4] : []);
    context.strokeStyle = color; context.lineWidth = 2; context.stroke(); context.setLineDash([]);
  };
  plot("actual", "#50e3c2", false);
  plot("predicted", "#f2b96d", true);
}

function renderValidation(validation) {
  latestValidation = validation;
  elements.modelScore.textContent = validation.overallScore == null ? "--" : `${validation.overallScore}/100`;
  const wave = validation.metrics && validation.metrics.waveLevel;
  elements.metricGrid.replaceChildren();
  const cards = [
    ["Wave MAE", wave ? `${wave.mae} ${wave.unit}` : "--", "Average absolute error"],
    ["Direction accuracy", wave ? `${wave.directionAccuracy}%` : "--", "Rise/fall prediction"],
    ["Evaluated samples", wave ? String(wave.evaluatedSamples) : "--", validation.method || "Rolling backtest"]
  ];
  cards.forEach(([labelText, valueText, noteText]) => {
    const card = document.createElement("div");
    const label = document.createElement("span"); const value = document.createElement("strong"); const note = document.createElement("small");
    label.textContent = labelText; value.textContent = valueText; note.textContent = noteText; card.append(label, value, note); elements.metricGrid.append(card);
  });
  elements.evaluationRows.replaceChildren();
  const rows = Array.isArray(validation.comparisons) ? validation.comparisons.slice(-5).reverse() : [];
  if (!rows.length) {
    const empty = document.createElement("div"); empty.className = "evaluation-empty"; empty.textContent = "Waiting for enough historical samples..."; elements.evaluationRows.append(empty);
  } else {
    rows.forEach((item) => {
      const row = document.createElement("div");
      const date = new Date(item.recordedAt);
      [date.toLocaleTimeString([], {hour: "2-digit", minute: "2-digit", second: "2-digit"}), `${item.predicted} m`, `${item.actual} m`, `${item.error} m`].forEach((text) => {
        const cell = document.createElement("span"); cell.textContent = text; row.append(cell);
      });
      elements.evaluationRows.append(row);
    });
  }
  requestAnimationFrame(drawValidationChart);
}

function seedDemoTrend() {
  const temperatures = [27.9,28.0,28.1,28.0,28.2,28.3,28.2,28.4,28.5,28.4,28.3,28.4,28.6,28.5,28.4,28.4];
  const waves = [.32,.38,.36,.44,.41,.47,.39,.35,.43,.48,.45,.39,.42,.37,.41,.40];
  temperatures.forEach((temperature, index) => readings.push({temperature, wave: waves[index]}));
}

async function requestJson(path, options = {}) {
  const response = await fetch(path, {...options, cache: "no-store"});
  if (!response.ok) throw new Error(`Request failed (${response.status})`);
  return response.json();
}

async function updateDashboard() {
  if (pollInFlight) return;
  pollInFlight = true;
  try {
    const [edgeSnapshot, alertHistory, scenarioStatus, forecast, validation] = await Promise.all([
      requestJson(`${EDGE_API_URL}/api/latest`),
      requestJson(`${EDGE_API_URL}/api/alerts?limit=30`),
      requestJson(`${EDGE_API_URL}/api/scenario`),
      requestJson(`${EDGE_API_URL}/api/forecast`),
      requestJson(`${EDGE_API_URL}/api/forecast/validation`)
    ]);
    renderStatus({...DEMO_DATA, ...edgeSnapshot.data});
    renderAlerts(alertHistory.items);
    processAlertNotifications(alertHistory.items);
    if (scenarioStatus.available) elements.scenarioSelect.value = scenarioStatus.active;
    renderForecast(forecast);
    renderValidation(validation);
    elements.systemStatus.textContent = "EDGE ONLINE";
    elements.systemIndicator.classList.remove("is-offline");
    elements.systemIndicator.innerHTML = "<i></i>EDGE LIVE";
    elements.dataModeBadge.textContent = "EDGE DATA";
  } catch (error) {
    const drift = Math.sin(Date.now() / 9000);
    renderStatus({
      ...DEMO_DATA,
      temperature: DEMO_DATA.temperature + drift * .2,
      waveLevel: DEMO_DATA.waveLevel + Math.abs(drift) * .08,
      tilt: DEMO_DATA.tilt + drift * .4
    });
    elements.systemStatus.textContent = "DEMO FALLBACK";
    elements.systemIndicator.classList.add("is-offline");
    elements.systemIndicator.innerHTML = "<i></i>EDGE OFFLINE";
    elements.dataModeBadge.textContent = "FALLBACK DATA";
  } finally {
    pollInFlight = false;
    clearTimeout(pollTimer);
    pollTimer = setTimeout(updateDashboard, POLL_INTERVAL_MS);
  }
}

async function toggleMonitoring() {
  if (PRESENTATION_CONTROLS) {
    demoMonitoring = !demoMonitoring;
    renderStatus({...DEMO_DATA, monitoring: demoMonitoring});
    showMessage(demoMonitoring ? "Demo monitoring started." : "Demo monitoring paused.", "success");
    return;
  }
  const previousLabel = elements.monitoringButton.textContent;
  elements.monitoringButton.disabled = true;
  elements.monitoringButton.textContent = "Working...";
  try {
    const data = await requestJson("/api/monitoring/toggle", {method: "POST"});
    if (typeof data.monitoring !== "boolean") throw new Error("Invalid response");
    showMessage(data.monitoring ? "Monitoring started." : "Monitoring stopped.", "success");
    await updateDashboard();
  } catch (error) {
    elements.monitoringButton.textContent = previousLabel;
    showMessage("Unable to change monitoring status.", "error");
  } finally {
    elements.monitoringButton.disabled = false;
  }
}

async function restartDevice() {
  if (PRESENTATION_CONTROLS) {
    showMessage("Restart is disabled while presentation mode is active.");
    return;
  }
  if (!window.confirm("Restart FALCON-01 now?")) return;
  elements.restartButton.disabled = true;
  elements.restartButton.textContent = "Restarting...";
  try {
    const data = await requestJson("/api/restart", {method: "POST"});
    if (data.restarting !== true) throw new Error("Invalid response");
    showMessage("FALCON-01 is restarting. Reconnect in a few seconds.", "success");
  } catch (error) {
    showMessage("The connection closed while the device restarted.");
  } finally {
    setTimeout(() => {
      elements.restartButton.disabled = false;
      elements.restartButton.textContent = "Restart ESP32";
    }, 5000);
  }
}

async function changeScenario() {
  const scenario = elements.scenarioSelect.value;
  elements.scenarioSelect.disabled = true;
  try {
    await requestJson(`${EDGE_API_URL}/api/scenario`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({scenario})
    });
    showMessage(`Test scenario changed to ${elements.scenarioSelect.options[elements.scenarioSelect.selectedIndex].text}.`, "success");
    setTimeout(updateDashboard, 550);
  } catch (error) {
    showMessage("Unable to change the virtual sensor scenario.", "error");
  } finally {
    elements.scenarioSelect.disabled = false;
  }
}

document.querySelectorAll("[data-view]").forEach((button) => {
  button.addEventListener("click", () => setView(button.dataset.view));
});
elements.menuButton.addEventListener("click", () => document.body.classList.add("sidebar-open"));
elements.sidebarScrim.addEventListener("click", () => document.body.classList.remove("sidebar-open"));
elements.monitoringButton.addEventListener("click", toggleMonitoring);
elements.restartButton.addEventListener("click", restartDevice);
elements.scenarioSelect.addEventListener("change", changeScenario);
elements.forecastHorizon.addEventListener("change", () => {
  if (latestForecast) renderForecast(latestForecast);
});
elements.notificationButton.addEventListener("click", handleNotificationButton);
window.addEventListener("resize", () => { drawChart(); drawValidationChart(); });
updateNotificationButton();
seedDemoTrend();
renderStatus(DEMO_DATA);
setView("overview");
updateDashboard();
