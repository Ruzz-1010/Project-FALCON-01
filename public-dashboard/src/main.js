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
const markers = new Map();
let selectedId = "FALCON-01";

const palawanBounds = L.latLngBounds([8.55, 117.35], [12.35, 120.7]);
const testStations = [
  { id: "FALCON-T02", name: "FALCON-T02", place: "Napsan Test Site, Puerto Princesa", point: [9.77, 118.64], condition: "Moderate", wave: 0.72, wind: 14.1, direction: "NE" },
  { id: "FALCON-T03", name: "FALCON-T03", place: "Dumaran Test Site, Palawan", point: [10.53, 119.77], condition: "Calm", wave: 0.42, wind: 8.3, direction: "E" },
  { id: "FALCON-T04", name: "FALCON-T04", place: "Roxas Test Site, Palawan", point: [10.32, 119.35], condition: "Moderate", wave: 1.08, wind: 16.4, direction: "ENE" }
];

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
  map = L.map("map", { zoomControl: true, preferCanvas: true, maxBounds: palawanBounds, maxBoundsViscosity: 1, minZoom: 8, zoomSnap: 0.5 })
    .fitBounds(palawanBounds, { padding: [8, 8] });
  L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: "&copy; OpenStreetMap contributors",
    crossOrigin: true
  }).on("load", () => { mapStatusEl.textContent = "MAP ONLINE"; })
    .on("tileerror", () => { mapStatusEl.textContent = "MAP UNAVAILABLE"; })
    .addTo(map);
}

function renderCard(station) {
  stationNameEl.textContent = station.name;
  stationPlaceEl.textContent = station.place;
  stationLinkEl.textContent = station.online ? "REPORTING" : "TEST DATA";
  stationLinkEl.classList.toggle("is-online", station.online);
  conditionEl.className = `condition is-${station.condition.toLowerCase()}`;
  conditionEl.querySelector("strong").textContent = station.condition;
  conditionEl.querySelector("p").textContent = station.wave == null
    ? "No valid wave estimate is available."
    : `${station.wave.toFixed(2)} m pressure-derived wave estimate`;
  windEl.textContent = station.wind == null ? "Unavailable" : `${station.wind.toFixed(1)} km/h ${station.direction || ""}`;
  updatedEl.textContent = station.updated;
}

function showStation(station) {
  selectedId = station.id;
  renderCard(station);
  const marker = markers.get(station.id);
  if (marker) map.panTo(marker.getLatLng());
}

function displayStations(status, wave, gps) {
  const currentWave = wave.valid ? wave.waveHeight : null;
  const online = status.system === "ONLINE";
  const liveStation = {
    id: "FALCON-01", name: "FALCON-01", place: gps.deploymentName || "Puerto Princesa Test Site, Palawan",
    point: gps.valid && gps.latitude != null && gps.longitude != null ? [gps.latitude, gps.longitude] : [9.7421, 118.7353],
    condition: conditionOf(currentWave), wave: currentWave, wind: status.windSpeed, direction: status.windDirection,
    online, updated: status.lastUpdate ? new Date(status.lastUpdate).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) : "Unavailable"
  };
  const stations = [liveStation, ...testStations.map((station) => ({ ...station, online: false, updated: "Test dataset" }))];
  const isDemo = String(status.dataSource || "").toLowerCase() === "simulator";
  statusEl.textContent = isDemo ? "DEMO DATA" : online ? "LIVE DATA" : "OFFLINE";
  statusEl.className = `data-status ${online ? "is-online" : "is-offline"}`;
  stations.forEach((station) => {
    const existing = markers.get(station.id);
    if (!existing) {
      const next = L.marker(station.point, { icon: markerIcon(station.condition), zIndexOffset: 500 }).addTo(map);
      next.bindTooltip(`${station.name} · ${station.online ? "reporting" : "test station"}`, { direction: "top", offset: [0, -16] });
      next.on("click", () => showStation(station));
      markers.set(station.id, next);
    } else {
      existing.setLatLng(station.point);
      existing.setIcon(markerIcon(station.condition));
      existing.off("click").on("click", () => showStation(station));
    }
  });
  renderCard(stations.find((station) => station.id === selectedId) || liveStation);
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
    displayStations(status, wave, gps);
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
