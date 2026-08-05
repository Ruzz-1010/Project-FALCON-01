"use strict";

const POLL_INTERVAL_MS = 2000;
const MAX_CHART_POINTS = 60;
const readings = [];
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
  elements.waveLevel.textContent = `${wave.toFixed(1)} m`;
  elements.motionWave.textContent = `${wave.toFixed(1)} m`;
  elements.uptime.textContent = formatUptime(data.uptime);
  elements.gpsStatus.textContent = validText(data.gps, "WAITING FOR GPS");
  elements.solarStatus.textContent = validText(data.solar, "STANDBY");
  elements.securityStatus.textContent = validText(data.security);
  addReading(temperature, wave);
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
    renderStatus(await requestJson("/api/status"));
  } catch (error) {
    elements.systemStatus.textContent = "CONNECTION LOST";
    elements.systemIndicator.classList.add("is-offline");
    elements.systemIndicator.innerHTML = "<i></i>OFFLINE";
    elements.lastUpdated.textContent = "Update failed";
  } finally {
    pollInFlight = false;
    clearTimeout(pollTimer);
    pollTimer = setTimeout(updateDashboard, POLL_INTERVAL_MS);
  }
}

async function toggleMonitoring() {
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

document.querySelectorAll("[data-view]").forEach((button) => {
  button.addEventListener("click", () => setView(button.dataset.view));
});
elements.menuButton.addEventListener("click", () => document.body.classList.add("sidebar-open"));
elements.sidebarScrim.addEventListener("click", () => document.body.classList.remove("sidebar-open"));
elements.monitoringButton.addEventListener("click", toggleMonitoring);
elements.restartButton.addEventListener("click", restartDevice);
window.addEventListener("resize", drawChart);
setView("overview");
updateDashboard();
