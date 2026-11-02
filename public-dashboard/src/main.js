const byId = (id) => document.getElementById(id);
const statusEl = byId("data-status");
const mapStatusEl = byId("map-status");
const stationNameEl = byId("station-name");
const stationPlaceEl = byId("station-place");
const stationLinkEl = byId("station-link");
const conditionEl = byId("condition");
const windEl = byId("wind");
const updatedEl = byId("updated");

let map;
let marker;

function conditionOf(height) {
  if (typeof height !== "number") return "Unavailable";
  if (height < 0.6) return "Calm";
  if (height < 2.5) return "Moderate";
  return "Rough";
}

function markerIcon(condition) {
  return L.divIcon({
    className: "",
    html: `<span class="station-pin is-${condition.toLowerCase()}"><i></i></span>`,
    iconSize: [38, 38],
    iconAnchor: [19, 19]
  });
}

function initializeMap() {
  map = L.map("map", { zoomControl: true, preferCanvas: true }).setView([10.25, 118.8], 8);
  L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: "&copy; OpenStreetMap contributors",
    crossOrigin: true
  }).on("load", () => { mapStatusEl.textContent = "MAP ONLINE"; })
    .on("tileerror", () => { mapStatusEl.textContent = "MAP UNAVAILABLE"; })
    .addTo(map);
}

function displayStation(status, wave, gps) {
  const currentWave = wave.valid ? wave.waveHeight : null;
  const condition = conditionOf(currentWave);
  const online = status.system === "ONLINE";
  stationNameEl.textContent = "FALCON-01";
  stationPlaceEl.textContent = gps.deploymentName || "Palawan coastal monitoring area";
  stationLinkEl.textContent = online ? "REPORTING" : "OFFLINE";
  stationLinkEl.classList.toggle("is-online", online);
  conditionEl.className = `condition is-${condition.toLowerCase()}`;
  conditionEl.querySelector("strong").textContent = condition;
  conditionEl.querySelector("p").textContent = currentWave == null
    ? "No valid wave estimate is available."
    : `${currentWave.toFixed(2)} m pressure-derived wave estimate`;
  windEl.textContent = status.windSpeed == null ? "Unavailable" : `${status.windSpeed.toFixed(1)} km/h ${status.windDirection || ""}`;
  updatedEl.textContent = status.lastUpdate ? new Date(status.lastUpdate).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) : "Unavailable";
  const isDemo = String(status.dataSource || "").toLowerCase() === "simulator";
  statusEl.textContent = isDemo ? "DEMO DATA" : online ? "LIVE DATA" : "OFFLINE";
  statusEl.className = `data-status ${online ? "is-online" : "is-offline"}`;

  if (!gps.valid || gps.latitude == null || gps.longitude == null) return;
  const point = [gps.latitude, gps.longitude];
  if (!marker) {
    marker = L.marker(point, { icon: markerIcon(condition), zIndexOffset: 500 }).addTo(map);
    marker.bindTooltip("FALCON-01 · select for latest condition", { direction: "top", offset: [0, -16] });
    marker.on("click", () => map.panTo(point));
    map.setView(point, 10);
  } else {
    marker.setLatLng(point);
    marker.setIcon(markerIcon(condition));
  }
}

async function load() {
  try {
    const [status, wave, gps] = await Promise.all(
      ["/status", "/wave", "/gps"].map(async (path) => {
        const response = await fetch(path, { cache: "no-store" });
        if (!response.ok) throw new Error(`${path} returned ${response.status}`);
        return response.json();
      })
    );
    displayStation(status, wave, gps);
  } catch (error) {
    statusEl.textContent = "OFFLINE";
    statusEl.className = "data-status is-offline";
    stationLinkEl.textContent = "OFFLINE";
    conditionEl.querySelector("strong").textContent = "Unavailable";
    conditionEl.querySelector("p").textContent = "The public station feed is temporarily unavailable.";
  }
}

initializeMap();
load();
window.setInterval(load, 5000);
