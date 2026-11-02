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
  { id: "FALCON-T02", name: "FALCON-T02", place: "Dumaran Test Site, Palawan", point: [10.52223748292728, 119.76123377734405], baseWave: 0.72, baseWind: 14.1, direction: "NE" },
  { id: "FALCON-T03", name: "FALCON-T03", place: "Roxas Test Site, Palawan", point: [10.312598851769618, 119.35198018029728], baseWave: 0.42, baseWind: 8.3, direction: "E" },
  { id: "FALCON-T04", name: "FALCON-T04", place: "San Vicente Test Site, Palawan", point: [10.60851878308501, 119.31754027686037], baseWave: 1.08, baseWind: 16.4, direction: "ENE" }
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
  stationLinkEl.textContent = station.simulated ? "SIMULATED LIVE" : station.online ? "REPORTING" : "OFFLINE";
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

function simulatedLiveStation(station, index, now) {
  const phase = now / 6000 + index * 1.83;
  const wave = Math.max(0.1, station.baseWave + Math.sin(phase) * 0.12 + Math.cos(phase * 0.43) * 0.04);
  const wind = Math.max(0, station.baseWind + Math.sin(phase * 0.72) * 1.8);
  return {
    ...station,
    wave,
    wind,
    condition: conditionOf(wave),
    online: true,
    simulated: true,
    updated: new Date(now).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" })
  };
}

function displayStations(status, wave, gps) {
  const currentWave = wave.valid ? wave.waveHeight : null;
  const online = status.system === "ONLINE";
  const liveStation = {
    id: "FALCON-01", name: "FALCON-01", place: "Puerto Princesa City Test Site, Palawan",
    point: [9.748333625985389, 118.78411811953949],
    condition: conditionOf(currentWave), wave: currentWave, wind: status.windSpeed, direction: status.windDirection,
    online, simulated: String(status.dataSource || "").toLowerCase() === "simulator",
    updated: status.lastUpdate ? new Date(status.lastUpdate).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" }) : "Unavailable"
  };
  const stations = [liveStation, ...testStations.map((station, index) => simulatedLiveStation(station, index, Date.now()))];
  const isDemo = String(status.dataSource || "").toLowerCase() === "simulator";
  statusEl.textContent = isDemo ? "DEMO DATA" : online ? "LIVE DATA" : "OFFLINE";
  statusEl.className = `data-status ${online ? "is-online" : "is-offline"}`;
  stations.forEach((station) => {
    const existing = markers.get(station.id);
    if (!existing) {
      const next = L.marker(station.point, { icon: markerIcon(station.condition), zIndexOffset: 500 }).addTo(map);
      next.bindTooltip(`${station.name} · ${station.simulated ? "simulated live feed" : "reporting"}`, { direction: "top", offset: [0, -16] });
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
