"use strict";

const POLL_INTERVAL_MS = 2000;
const elements = {
  systemStatus: document.getElementById("systemStatus"),
  systemIndicator: document.getElementById("systemIndicator"),
  clients: document.getElementById("clients"),
  uptime: document.getElementById("uptime"),
  temperature: document.getElementById("temperature"),
  tilt: document.getElementById("tilt"),
  waveLevel: document.getElementById("waveLevel"),
  seaCondition: document.getElementById("seaCondition"),
  gpsStatus: document.getElementById("gpsStatus"),
  solarStatus: document.getElementById("solarStatus"),
  securityStatus: document.getElementById("securityStatus"),
  monitoringStatus: document.getElementById("monitoringStatus"),
  monitoringButton: document.getElementById("monitoringButton"),
  restartButton: document.getElementById("restartButton"),
  batteryValue: document.getElementById("batteryValue"),
  batteryBar: document.getElementById("batteryBar"),
  batteryRing: document.querySelector(".battery-ring"),
  lastUpdated: document.getElementById("lastUpdated"),
  actionMessage: document.getElementById("actionMessage")
};

let pollTimer = null;
let pollInFlight = false;
let messageTimer = null;

function validNumber(value, fallback = 0) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : fallback;
}

function validText(value, fallback = "UNAVAILABLE") {
  return typeof value === "string" && value.trim() ? value.trim() : fallback;
}

function formatUptime(value) {
  const totalSeconds = Math.max(0, Math.floor(validNumber(value)));
  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = totalSeconds % 60;
  return `${hours}h ${minutes}m ${seconds}s`;
}

function setBatteryDisplay(value) {
  const percent = Math.max(0, Math.min(100, validNumber(value)));
  const degrees = percent * 3.6;
  elements.batteryValue.textContent = `${Math.round(percent)}%`;
  elements.batteryBar.style.width = `${percent}%`;
  elements.batteryRing.style.background =
    `conic-gradient(var(--cyan) 0deg, var(--cyan) ${degrees}deg, ` +
    `rgba(255, 255, 255, 0.08) ${degrees}deg)`;
}

function showMessage(message, type = "info") {
  clearTimeout(messageTimer);
  elements.actionMessage.textContent = message;
  elements.actionMessage.dataset.type = type;
  elements.actionMessage.classList.add("is-visible");
  messageTimer = setTimeout(() => elements.actionMessage.classList.remove("is-visible"), 4500);
}

function renderStatus(data) {
  const monitoring = data.monitoring === true;
  elements.systemStatus.textContent = validText(data.system, "ONLINE");
  elements.systemIndicator.classList.remove("is-offline");
  elements.clients.textContent = Math.max(0, Math.floor(validNumber(data.clients)));
  elements.uptime.textContent = formatUptime(data.uptime);
  elements.temperature.textContent = validNumber(data.temperature).toFixed(1);
  elements.tilt.textContent = `${validNumber(data.tilt).toFixed(1)}\u00B0`;
  elements.waveLevel.textContent = `${validNumber(data.waveLevel).toFixed(1)} m`;
  elements.seaCondition.textContent = validText(data.seaCondition);
  elements.gpsStatus.textContent = validText(data.gps);
  elements.solarStatus.textContent = validText(data.solar);
  elements.securityStatus.textContent = validText(data.security);
  elements.monitoringStatus.textContent = monitoring ? "ACTIVE" : "STOPPED";
  elements.monitoringButton.textContent = monitoring ? "Stop Monitoring" : "Start Monitoring";
  setBatteryDisplay(data.battery);
  elements.lastUpdated.textContent = new Date().toLocaleTimeString();
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
    elements.lastUpdated.textContent = "Update failed";
  } finally {
    pollInFlight = false;
    clearTimeout(pollTimer);
    pollTimer = setTimeout(updateDashboard, POLL_INTERVAL_MS);
  }
}

async function toggleMonitoring() {
  elements.monitoringButton.disabled = true;
  const previousLabel = elements.monitoringButton.textContent;
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
    showMessage("The connection closed while the device restarted.", "info");
  } finally {
    setTimeout(() => {
      elements.restartButton.disabled = false;
      elements.restartButton.textContent = "Restart ESP32";
    }, 5000);
  }
}

elements.monitoringButton.addEventListener("click", toggleMonitoring);
elements.restartButton.addEventListener("click", restartDevice);
updateDashboard();
