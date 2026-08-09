"use strict";

const $ = (id) => document.getElementById(id);
const history = [];
const supportingHistory = [];
const predictionLog = [];
let latestAlerts = [];
let latestWaveSnapshot = null;
let latestAiSnapshot = null;
let lastLogsLoad = 0;
let currentView = "overview";
let unread = 0;
let knownAlerts = new Set();
let pollBusy = false;
let waveHistoryHydrated = false;
let supportingHistoryHydrated = false;
let firstTelemetryReceived=false;
let gpsMap=null,buoyMapMarker=null,deploymentMapMarker=null,anchorMapCircle=null,driftMapLine=null,mapHasCentered=false;
const scenarioLabels={normal:"NORMAL OPERATION",rough_sea:"ROUGH SEA",low_battery:"LOW BATTERY",overheating:"INTERNAL OVERHEATING",sensor_fault:"WAVE SENSOR FAILURE"};

const titles = {overview:"Mission control",wave:"Wave intelligence",motion:"Buoy motion",gps:"GPS and drift",power:"Power system",system:"System health",activity:"Alerts and events",logs:"Operational logs",settings:"Station settings"};
const number = (value, digits = 1) => typeof value === "number" && Number.isFinite(value) ? value.toFixed(digits) : "--";
const statusClass = (value) => ["ONLINE","NORMAL","CONNECTED","SECURE","CHARGING","READY"].includes(value) ? "good-text" : ["CRITICAL","OFFLINE","DISCONNECTED","ROUGH"].includes(value) ? "bad-text" : "warn-text";
function continuousWaveSegment(items,maxJump=.85){const valid=items.filter(item=>Number.isFinite(item.waveHeight)),segment=[];let newer=null;for(let index=valid.length-1;index>=0;index--){const item=valid[index];if(newer!==null&&Math.abs(item.waveHeight-newer)>maxJump)break;segment.unshift(item);newer=item.waveHeight;}return segment;}

function setView(view) {
  currentView = view;
  document.querySelectorAll("[data-page]").forEach((node) => node.classList.toggle("is-active", node.dataset.page === view));
  document.querySelectorAll("[data-view]").forEach((node) => node.classList.toggle("is-active", node.dataset.view === view));
  $("pageTitle").textContent = titles[view] || "FALCON-01";
  document.body.classList.remove("sidebar-open");
  if (view === "activity") { unread = 0; updateNotificationBadge(); }
  if (view === "wave" && latestAiSnapshot) requestAnimationFrame(()=>drawWaveAiChart(latestAiSnapshot.predictedWaveHeight));
  if (view === "gps" && gpsMap) requestAnimationFrame(()=>gpsMap.invalidateSize());
  if (view === "logs") renderLogs();
  window.dispatchEvent(new Event("resize"));
}

let pageTransitionBusy=false,pendingPageView=null;
const wait=(duration)=>new Promise((resolve)=>setTimeout(resolve,duration));
async function navigateTo(view){
  if(!titles[view]||view===currentView)return;
  if(!firstTelemetryReceived){location.hash=view;setView(view);return;}
  if(pageTransitionBusy){pendingPageView=view;return;}
  pageTransitionBusy=true;document.body.classList.add("is-page-transitioning");
  const layer=$("pageTransition"),reduced=matchMedia("(prefers-reduced-motion: reduce)").matches,duration=reduced?250:6000,revealAt=Math.round(duration*.78);
  $("transitionPageName").textContent=titles[view];layer.setAttribute("aria-hidden","false");layer.classList.remove("is-active");void layer.offsetWidth;layer.classList.add("is-active");
  await wait(revealAt);location.hash=view;setView(view);await wait(duration-revealAt);
  layer.classList.remove("is-active");layer.setAttribute("aria-hidden","true");document.body.classList.remove("is-page-transitioning");pageTransitionBusy=false;
  if(pendingPageView){const next=pendingPageView;pendingPageView=null;navigateTo(next);}
}
document.querySelectorAll("[data-view]").forEach((button) => button.addEventListener("click", () => navigateTo(button.dataset.view)));
document.querySelectorAll("[data-view]").forEach((button)=>{const label=button.querySelector("b")?.textContent||"Dashboard page";button.dataset.label=label;button.title=label;});
document.querySelectorAll("[data-view],#themeToggle,#notificationButton,#menuButton,#sidebarToggle").forEach((control)=>control.addEventListener("click",()=>{control.classList.remove("icon-activated");void control.offsetWidth;control.classList.add("icon-activated");control.addEventListener("animationend",()=>control.classList.remove("icon-activated"),{once:true});}));
$("menuButton").addEventListener("click", () => document.body.classList.toggle("sidebar-open"));
$("sidebarScrim").addEventListener("click", () => document.body.classList.remove("sidebar-open"));
const sidebarCollapsed=localStorage.getItem("falcon-sidebar-collapsed")==="true";document.body.classList.toggle("sidebar-collapsed",sidebarCollapsed);
function updateSidebarToggle(){const collapsed=document.body.classList.contains("sidebar-collapsed");$("sidebarToggle").setAttribute("aria-label",collapsed?"Expand sidebar":"Collapse sidebar");$("sidebarToggle").title=collapsed?"Expand sidebar":"Collapse sidebar";}
$("sidebarToggle").addEventListener("click",()=>{document.body.classList.toggle("sidebar-collapsed");localStorage.setItem("falcon-sidebar-collapsed",String(document.body.classList.contains("sidebar-collapsed")));updateSidebarToggle();window.dispatchEvent(new Event("resize"));});updateSidebarToggle();

const savedTheme = localStorage.getItem("falcon-theme") || "dark";
document.documentElement.dataset.theme = savedTheme;
$("themeToggle").addEventListener("click", () => {
  const next = document.documentElement.dataset.theme === "light" ? "dark" : "light";
  document.documentElement.dataset.theme = next;
  localStorage.setItem("falcon-theme", next);
  drawTrend();
});

function toast(message, type = "success") {
  const node = $("toast"); node.textContent = message; node.dataset.type = type; node.classList.add("is-visible");
  clearTimeout(toast.timer); toast.timer = setTimeout(() => node.classList.remove("is-visible"), 3000);
}

function setSyncing(active){$("syncProgress").classList.toggle("is-active",active);}
function finishBoot(){if(firstTelemetryReceived)return;firstTelemetryReceived=true;document.body.classList.add("is-ready");document.body.classList.remove("is-booting");setTimeout(()=>$("bootScreen")?.remove(),550);}
function setButtonBusy(button,busy,label="Working"){if(!button)return;if(busy){button.dataset.originalLabel=button.textContent;button.textContent=label;button.classList.add("is-loading");button.disabled=true;}else{button.textContent=button.dataset.originalLabel||button.textContent;button.classList.remove("is-loading");button.disabled=false;}}

function updateNotificationBadge() {
  $("notificationCount").hidden = unread === 0;
  $("notificationCount").textContent = String(unread);
  $("notificationButton").classList.toggle("has-alerts", unread > 0);
}

$("notificationButton").addEventListener("click", async () => {
  if (!("Notification" in window)) return toast("Browser notifications are unavailable.", "error");
  const permission = await Notification.requestPermission();
  toast(permission === "granted" ? "Notifications enabled." : "Notification permission not enabled.", permission === "granted" ? "success" : "error");
});

async function json(path, options = {}) {
  const response = await fetch(path, {...options, cache:"no-store", headers:{"Content-Type":"application/json", ...(options.headers || {})}});
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(payload?.error?.message || payload?.error || `${response.status}`);
  return payload;
}

function renderStatus(status) {
  const online = status.system === "ONLINE";
  $("systemStatus").textContent = status.system;
  $("systemStatus").className = statusClass(status.system);
  $("sensorSummary").textContent = `${status.sensorsOnline}/${status.sensorsExpected} approved sensors online`;
  $("lastUpdate").textContent = status.lastUpdate ? new Date(status.lastUpdate).toLocaleTimeString() : "--:--:--";
  $("dataSource").textContent = String(status.dataSource || "unknown").toUpperCase();
  $("edgeState").textContent = online ? "EDGE ONLINE" : "EDGE DEGRADED";
  $("liveBadge").innerHTML = `<i></i>${online ? "LIVE" : "DEGRADED"}`;
  $("liveBadge").classList.toggle("is-offline", !online);
  $("windSummary").textContent = `${number(status.windSpeed)} km/h · ${status.windDirection || "--"}`;
  $("temperatureSummary").textContent = `${number(status.internalTemperature)} °C`;
  $("windChartValue").textContent = `${number(status.windSpeed)} km/h`;
  $("temperatureChartValue").textContent = `${number(status.internalTemperature)} °C`;
  if(!supportingHistoryHydrated&&Array.isArray(status.sensorHistory)&&status.sensorHistory.length){supportingHistory.splice(0,supportingHistory.length,...status.sensorHistory.map(item=>({time:new Date(item.recordedAt),wind:item.windSpeed,temperature:item.internalTemperature,pressure:null,battery:null})));supportingHistoryHydrated=true;}
  else {supportingHistory.push({time:new Date(status.lastUpdate||Date.now()),wind:status.windSpeed,temperature:status.internalTemperature,pressure:null,battery:null});if(supportingHistory.length>60)supportingHistory.shift();}
  window.falconDigitalTwin?.setTelemetry({enclosureTemperature:status.internalTemperature || 0});
  $("esp32Status").textContent = status.esp32; $("miniPcStatus").textContent = status.miniPc;
  $("uartStatus").textContent = status.uart; $("apiStatusDetail").textContent = status.api;
  $("apiStatus").textContent = `API ${status.api}`; $("uptime").textContent = formatUptime(status.uptimeSeconds);
  $("systemSource").textContent = String(status.dataSource).toUpperCase();
  $("topSystemHealth").textContent=status.system;$("homeWindDirection").textContent=status.windDirection||"--";$("homeInternalTemp").textContent=`${number(status.internalTemperature)} °C`;
  const enclosureTemp=Number(status.internalTemperature),intakeRpm=Number(status.intakeFanRpm),exhaustRpm=Number(status.exhaustFanRpm);
  const coolingState=!Number.isFinite(enclosureTemp)?"UNAVAILABLE":enclosureTemp>=55?"CRITICAL":enclosureTemp>=45?"ELEVATED":"NORMAL";
  $("powerInternalTemperature").textContent=Number.isFinite(enclosureTemp)?`${number(enclosureTemp,1)} °C`:"--";
  $("powerThermalCondition").textContent=coolingState==="NORMAL"?"Enclosure temperature nominal":coolingState==="ELEVATED"?"Cooling load elevated":coolingState==="CRITICAL"?"High-temperature warning":"Temperature sensor unavailable";
  $("powerTemperatureBar").style.width=`${Math.max(0,Math.min(100,(enclosureTemp||0)/70*100))}%`;
  $("intakeFanRpm").textContent=Number.isFinite(intakeRpm)?`${number(intakeRpm,0)} RPM`:"-- RPM";$("exhaustFanRpm").textContent=Number.isFinite(exhaustRpm)?`${number(exhaustRpm,0)} RPM`:"-- RPM";
  $("intakeFanState").textContent=Number.isFinite(intakeRpm)&&intakeRpm>300?"RUNNING":"NO TELEMETRY";$("exhaustFanState").textContent=Number.isFinite(exhaustRpm)&&exhaustRpm>300?"RUNNING":"NO TELEMETRY";
  $("coolingStatus").textContent=coolingState;$("coolingStatus").className=`tag ${coolingState==="NORMAL"?"tag-good":coolingState==="CRITICAL"?"tag-danger":"tag-warn"}`;
  [["systemCpu","systemCpuBar",status.cpuUsage],["systemRam","systemRamBar",status.memoryUsage],["systemStorage","systemStorageBar",status.storageUsage]].forEach(([label,bar,value])=>{$(label).textContent=`${number(value,0)}%`;$(bar).style.width=`${Math.max(0,Math.min(100,value||0))}%`;});$("systemWifi").textContent=`${status.wifiSignalDbm??"--"} dBm`;
  renderAlerts(status.alerts || []);
}

function formatUptime(seconds) { const value = Math.max(0, Number(seconds) || 0); return `${Math.floor(value/3600)}h ${Math.floor(value%3600/60)}m ${Math.floor(value%60)}s`; }

function renderWave(wave) {
  latestWaveSnapshot=wave;
  $("waveNow").textContent = number(wave.waveHeight, 2); $("waveState").textContent = wave.waveHeightState || "UNAVAILABLE";
  $("pressureSummary").textContent = `${number(wave.pressure)} kPa`; $("roll").textContent = `${number(wave.roll)}°`;
  $("pressureChartValue").textContent = `${number(wave.pressure)} kPa`;
  if(Array.isArray(wave.history)&&supportingHistory.length){wave.history.slice(-supportingHistory.length).forEach((item,index)=>{const target=supportingHistory[supportingHistory.length-Math.min(wave.history.length,supportingHistory.length)+index];if(target)target.pressure=item.waterPressure;});}
  else if(supportingHistory.length)supportingHistory[supportingHistory.length-1].pressure=wave.pressure;
  $("pitch").textContent = `${number(wave.pitch)}°`; $("yaw").textContent = `${number(wave.yaw)}°`;
  $("waveMotion").textContent = `${number(wave.waveMotion)}°`;
  if(wave.valid){if(!waveHistoryHydrated&&Array.isArray(wave.history)&&wave.history.length){const segment=continuousWaveSegment(wave.history);history.splice(0,history.length,...segment.map(item=>({wave:item.waveHeight,predicted:null,time:new Date(item.recordedAt)})));waveHistoryHydrated=true;}else{const previous=history.at(-1)?.wave;if(Number.isFinite(previous)&&Math.abs(wave.waveHeight-previous)>.85)history.length=0;history.push({wave:wave.waveHeight,predicted:null,time:wave.recordedAt?new Date(wave.recordedAt):new Date()});if(history.length>60)history.shift();}$("chartCurrent").textContent=`${number(wave.waveHeight,2)} m`;drawTrend();}
  window.falconDigitalTwin?.setTelemetry({roll:wave.roll || 0,pitch:wave.pitch || 0,yaw:wave.yaw || 0,wave:wave.waveHeight || 0,rough:(wave.waveHeight || 0) >= 2.5});
}

function renderWaveUnavailable() {
  $("waveNow").textContent="--";$("waveState").textContent="SENSOR UNAVAILABLE";$("pressureSummary").textContent="Check wave sensor";
  $("chartCurrent").textContent="-- m";window.falconDigitalTwin?.setTelemetry({fault:true,scenario:"sensor_fault"});
}

function renderAi(ai) {
  latestAiSnapshot=ai;
  const ready = ai.status === "READY";
  $("wavePredicted").textContent = ready ? number(ai.predictedWaveHeight, 2) : "--";
  $("chartForecast").textContent = ready ? `${number(ai.predictedWaveHeight,2)} m` : "-- m";
  $("predictionState").textContent = `${ai.status} · ${ai.horizonMinutes} MIN`;
  $("seaCondition").textContent = ai.seaCondition || "UNAVAILABLE";
  $("seaCondition").className = statusClass(ai.seaCondition);
  $("confidenceSummary").textContent = ready ? `${ai.confidence}% model confidence` : "Confidence unavailable";
  $("aiCurrent").textContent = ready ? `${number(ai.currentWaveHeight,2)} m` : "--";
  $("aiPredicted").textContent = ready ? `${number(ai.predictedWaveHeight,2)} m` : "--";
  $("aiChange").textContent = ready ? `${ai.change >= 0 ? "+" : ""}${number(ai.change,2)} m` : "--";
  $("aiDirection").textContent = (ai.direction || "--").toUpperCase(); $("aiConfidence").textContent = ready ? `${ai.confidence}%` : "--";
  $("aiCondition").textContent = ai.seaCondition || "--"; $("aiTarget").textContent = ai.targetAt ? new Date(ai.targetAt).toLocaleTimeString([], {hour:"2-digit",minute:"2-digit"}) : "--";
  $("aiSamples").textContent = `${ai.sampleCount} samples`; $("modelName").textContent = ai.model; $("modelVersion").textContent = ai.modelVersion;
  $("modelSource").textContent = String(ai.dataSource).toUpperCase(); $("modelCurrentState").textContent = ai.status;
  $("modelStatus").textContent = ai.status; $("modelStatus").className = `tag ${ready ? "tag-good" : "tag-warn"}`;
  $("forecastNote").textContent = ready ? `Current ${number(ai.currentWaveHeight,2)} m versus predicted ${number(ai.predictedWaveHeight,2)} m at ${ai.horizonMinutes} minutes. Presentation model only; not validated for safety decisions.` : `Prediction unavailable: ${ai.unavailableReason || "collecting history"}.`;
  $("storyInput").textContent=Number.isFinite(ai.currentWaveHeight)?`Current wave: ${number(ai.currentWaveHeight,2)} m · ${ai.sampleCount} samples`:`Wave sensor data unavailable`;
  $("storyAnalysis").textContent=ready?`Trend detected: ${(ai.direction||"stable").toUpperCase()} · change ${ai.change>=0?"+":""}${number(ai.change,2)} m`:`Need ${Math.max(0,8-(ai.sampleCount||0))} more valid samples`;
  $("storyResult").textContent=ready?`${number(ai.predictedWaveHeight,2)} m`:"-- m";
  $("storyMeaning").textContent=ready?`Current: ${number(ai.currentWaveHeight,2)} m · ${ai.direction.toUpperCase()} trend`:`FALCON needs more valid wave readings.`;
  $("storyConfidence").textContent=ready?`${ai.confidence}%`:"--%";
  $("predictionTimeSimple").textContent=`Next ${ai.horizonMinutes} minutes`;
  $("predictionStatusSimple").textContent=ready?ai.seaCondition:"Unavailable";
  $("predictionStatusSimple").className=ready?statusClass(ai.seaCondition):"warn-text";
  $("homeAiConfidence").textContent=ready?`${ai.confidence}%`:"--%";$("homeAiStatus").textContent=ai.status;
  if(ready){predictionLog.push({recordedAt:ai.generatedAt,current:ai.currentWaveHeight,predicted:ai.predictedWaveHeight,horizon:ai.horizonMinutes,condition:ai.seaCondition,confidence:ai.confidence,source:ai.dataSource});if(predictionLog.length>60)predictionLog.shift();}
  const movement=ai.direction==="up"?"increase":ai.direction==="down"?"decrease":"remain nearly stable";
  $("plainLanguageResult").textContent=ready?`Based on ${ai.sampleCount} recent wave samples, FALCON expects the wave height to ${movement} from ${number(ai.currentWaveHeight,2)} m to ${number(ai.predictedWaveHeight,2)} m within ${ai.horizonMinutes} minutes. This corresponds to ${ai.seaCondition} sea conditions.`:`No prediction is being shown because ${ai.unavailableReason||"the model is still collecting valid samples"}.`;
  const nativeDetails=ai.explanation?.details;
  const legacyReady=ready&&!nativeDetails;
  const fallbackTrend=ready&&Number.isFinite(ai.change) ? ai.change/Math.max(1,ai.horizonMinutes) : null;
  const details=nativeDetails||{
    validSamples:ai.sampleCount||0,
    sampleWindowSeconds:Math.max(0,(ai.sampleCount||1)-1)*2,
    trendMetersPerMinute:fallbackTrend,
    rawProjection:ai.predictedWaveHeight,
    maximumAllowedChange:Number.isFinite(ai.currentWaveHeight)?Math.max(.08,ai.currentWaveHeight*.35)*(ai.horizonMinutes/15)**.7:null,
    limitApplied:null,
    residualVolatility:null,
    dampingFactor:1/(1+(ai.horizonMinutes*60)/300)
  };
  $("explainSamples").textContent=`${details.validSamples} valid wave samples analyzed`;
  $("explainProjection").textContent=`${ai.horizonMinutes}-minute projection · damping ${number(details.dampingFactor,3)}`;
  $("explainOutput").textContent=ready ? `${number(ai.predictedWaveHeight,2)} m · ${ai.seaCondition}` : "Output currently unavailable";
  $("evidenceWindow").textContent=`${number(details.sampleWindowSeconds,1)} seconds${legacyReady?" · estimated":""}`;
  $("evidenceTrend").textContent=Number.isFinite(details.trendMetersPerMinute)?`${details.trendMetersPerMinute>=0?"+":""}${number(details.trendMetersPerMinute,4)} m/min${legacyReady?" · output-derived":""}`:"Unavailable";
  $("evidenceRaw").textContent=Number.isFinite(details.rawProjection)?`${number(details.rawProjection,3)} m${legacyReady?" · legacy output":""}`:"Unavailable";
  $("evidenceLimit").textContent=Number.isFinite(details.maximumAllowedChange)?`±${number(details.maximumAllowedChange,3)} m`:"Not reported";
  $("evidenceLimitState").textContent=details.limitApplied===true?"Applied · raw output was constrained":details.limitApplied===false?"Not applied · raw output was plausible":"Calculated safeguard · restart service to verify application";
  $("evidenceVolatility").textContent=Number.isFinite(details.residualVolatility)?`${number(details.residualVolatility,4)} m`:"Not exposed by loaded service";
  $("evidenceDamping").textContent=`${number(details.dampingFactor,3)}${legacyReady?" · calculated":""}`;
  if(legacyReady){$("forecastNote").textContent=`Legacy backend detected: prediction is available, but native evidence fields are missing. Values marked estimated or output-derived are UI compatibility calculations. Restart the edge service to load the full explainability model.`;$("modelStatus").textContent="RESTART SERVICE";$("modelStatus").className="tag tag-warn";}
  renderWaveIntelligence(ai,details);
  renderLogs();
  if (history.length) { history[history.length - 1].predicted = ai.predictedWaveHeight; drawTrend(); }
}

function renderGps(gps) {
  const fix = gps.valid ? `${gps.fix} FIX · ${gps.satellites} SAT` : "NO FIX"; $("gpsSummary").textContent = fix;
  $("gpsFix").textContent = fix; $("gpsFixDetail").textContent = gps.fix; $("satellites").textContent = gps.satellites;
  $("gpsAccuracy").textContent = gps.horizontalAccuracyMeters == null ? "--" : `${number(gps.horizontalAccuracyMeters)} m`;
  $("anchorDistance").textContent = gps.anchorDistanceMeters == null ? "--" : `${number(gps.anchorDistanceMeters)} m`;
  $("driftStatus").textContent = gps.driftStatus; $("driftStatus").className = statusClass(gps.driftStatus);
  $("deploymentPoint").textContent=gps.deploymentName||"Puerto Princesa City, Palawan Coast";
  $("deploymentReferenceState").textContent=(gps.deploymentReferenceState||"DEMO_REFERENCE").replaceAll("_"," ");
  updateGpsMap(gps);
  $("coordinates").textContent = gps.valid ? `${gps.latitude.toFixed(4)}° N, ${gps.longitude.toFixed(4)}° E` : "Coordinates unavailable";
  $("gpsSignalQuality").textContent=gps.signalQuality||"--";$("gpsHeading").textContent=Number.isFinite(gps.headingDegrees)?`${number(gps.headingDegrees,1)}°`:"--";$("gpsDriftSpeed").textContent=Number.isFinite(gps.surfaceSpeedKnots)?`${number(gps.surfaceSpeedKnots,2)} kn`:"--";
  const lock=gps.valid?`${gps.fix} · ${gps.satellites} SAT`:"NO FIX";$("topGpsLock").textContent=lock;$("homeGpsLock").textContent=lock;
}

function updateGpsMap(gps) {
  if(!gps.valid||!Number.isFinite(gps.latitude)||!Number.isFinite(gps.longitude)||!window.L)return;
  const position=[gps.latitude,gps.longitude];
  const reference=[Number.isFinite(gps.referenceLatitude)?gps.referenceLatitude:gps.latitude,Number.isFinite(gps.referenceLongitude)?gps.referenceLongitude:gps.longitude];
  if(!gpsMap){
    gpsMap=L.map("gpsMap",{zoomControl:true,attributionControl:true,preferCanvas:true}).setView(reference,17);
    const tiles=L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png",{maxZoom:19,attribution:'&copy; OpenStreetMap contributors'}).addTo(gpsMap);
    tiles.on("tileerror",()=>{$("mapOffline").hidden=false;});
    tiles.on("load",()=>{$("mapOffline").hidden=true;});
    const buoyIcon=L.divIcon({className:"map-div-icon",html:'<span class="buoy-map-marker"><i></i></span>',iconSize:[32,32],iconAnchor:[16,16]});
    const baseIcon=L.divIcon({className:"map-div-icon",html:'<span class="deployment-map-marker"></span>',iconSize:[22,22],iconAnchor:[11,11]});
    buoyMapMarker=L.marker(position,{icon:buoyIcon,zIndexOffset:500}).addTo(gpsMap).bindTooltip("FALCON-01 · live GPS",{direction:"top",offset:[0,-14]});
    deploymentMapMarker=L.marker(reference,{icon:baseIcon}).addTo(gpsMap).bindTooltip("Puerto Princesa demo deployment point");
    anchorMapCircle=L.circle(reference,{radius:10,color:"#71d89b",weight:2,dashArray:"6 6",fillColor:"#71d89b",fillOpacity:.06}).addTo(gpsMap);
    driftMapLine=L.polyline([reference,position],{color:"#efba67",weight:2,dashArray:"5 7"}).addTo(gpsMap);
    requestAnimationFrame(()=>gpsMap.invalidateSize());
  }
  buoyMapMarker.setLatLng(position);deploymentMapMarker.setLatLng(reference);anchorMapCircle.setLatLng(reference);driftMapLine.setLatLngs([reference,position]);
  if(!mapHasCentered){gpsMap.fitBounds(L.latLngBounds([reference,position]).pad(5),{maxZoom:18});mapHasCentered=true;}
}

function renderBattery(data) {
  $("batterySummary").textContent = `${number(data.percentage,0)}% · ${data.status}`; $("batteryPercent").textContent = `${number(data.percentage,0)}%`;
  $("batteryBar").style.width = `${Math.max(0,Math.min(100,data.percentage || 0))}%`; $("batteryVoltage").textContent = `${number(data.voltage,2)} V`;
  $("batteryCurrent").textContent = `${number(data.current,2)} A`; $("batteryDirection").textContent = data.direction;
  $("powerStatus").textContent = data.status; window.falconDigitalTwin?.setTelemetry({battery:data.percentage || 0});
  $("batteryRuntime").textContent=Number.isFinite(data.estimatedRuntimeHours)?`${number(data.estimatedRuntimeHours,1)} hours`:"--";$("batteryTemperature").textContent=Number.isFinite(data.temperature)?`${number(data.temperature,1)} °C`:"--";$("powerConsumption").textContent=Number.isFinite(data.powerConsumptionWatts)?`${number(data.powerConsumptionWatts,1)} W`:"--";
  $("batteryChartValue").textContent = `${number(data.percentage,0)}%`;
  if(Array.isArray(data.history)&&supportingHistory.length){data.history.slice(-supportingHistory.length).forEach((item,index)=>{const target=supportingHistory[supportingHistory.length-Math.min(data.history.length,supportingHistory.length)+index];if(target)target.battery=item.percentage;});}
  else if(supportingHistory.length)supportingHistory[supportingHistory.length-1].battery=data.percentage;
}

function renderSolar(data) {
  $("solarSummary").textContent = `${data.status} · ${number(data.power)} W`; $("solarPower").textContent = `${number(data.power)} W`;
  $("solarVoltage").textContent = `${number(data.voltage)} V`; $("solarCurrent").textContent = `${number(data.current,2)} A`; $("solarCharging").textContent = data.status;
}

function renderAlerts(alerts) {
  latestAlerts=alerts;
  const keys = new Set(alerts.map((item) => item.code)); const newItems = alerts.filter((item) => !knownAlerts.has(item.code));
  knownAlerts = keys;
  if (newItems.length && currentView !== "activity") { unread += newItems.length; updateNotificationBadge(); if (Notification.permission === "granted") newItems.forEach((item) => new Notification(`FALCON ${item.severity.toUpperCase()}`, {body:item.message})); }
  const list = $("activityList"); list.innerHTML = "";
  if (!alerts.length) { list.innerHTML = '<div class="activity-empty"><strong>No active alerts</strong><p>All approved monitoring channels are within configured limits.</p></div>'; $("activityStatus").textContent = "ALL CLEAR"; $("activityStatus").className = "tag tag-good"; }
  else { alerts.forEach((item) => { const row=document.createElement("div"); row.className=`activity-item is-${item.severity}`; row.innerHTML=`<div><strong>${item.code.replaceAll("_"," ")}</strong><p>${item.message}</p></div><time>${item.severity.toUpperCase()}</time>`; list.appendChild(row); }); $("activityStatus").textContent=`${alerts.length} ACTIVE`; $("activityStatus").className="tag tag-warn"; }
  $("homeLatestAlert").textContent=alerts.length?alerts[0].code.replaceAll("_"," "):"None";
  window.falconDigitalTwin?.setTelemetry({fault:alerts.some((item)=>item.code.includes("INVALID")),scenario:alerts.some((item)=>item.code.includes("INVALID"))?"sensor_fault":"normal"});
}

function drawTrend() {
  const canvas=$("trendChart"), ctx=canvas.getContext("2d"), box=canvas.getBoundingClientRect(), ratio=Math.min(devicePixelRatio||1,2);
  canvas.width=Math.max(1,box.width*ratio); canvas.height=Math.max(1,box.height*ratio); ctx.scale(ratio,ratio); ctx.clearRect(0,0,box.width,box.height);
  $("chartEmpty").hidden=history.length>1; if(history.length<2)return;
  const forecast=history.at(-1).predicted, values=history.map(x=>x.wave).concat(Number.isFinite(forecast)?[forecast]:[]), rawMin=Math.min(...values),rawMax=Math.max(...values),pad=Math.max((rawMax-rawMin)*.3,.08),min=Math.max(0,rawMin-pad),max=rawMax+pad;
  const left=46,right=18,top=12,bottom=28,width=box.width-left-right,height=box.height-top-bottom, styles=getComputedStyle(document.documentElement), muted=styles.getPropertyValue("--muted").trim()||"#8da5aa",grid=styles.getPropertyValue("--line").trim()||"rgba(255,255,255,.1)";
  ctx.font='10px "Segoe UI",sans-serif';ctx.fillStyle=muted;ctx.textAlign="right";ctx.textBaseline="middle";
  for(let i=0;i<=4;i++){const y=top+height*i/4,value=max-(max-min)*i/4;ctx.strokeStyle=grid;ctx.lineWidth=1;ctx.beginPath();ctx.moveTo(left,y);ctx.lineTo(left+width,y);ctx.stroke();ctx.fillText(`${value.toFixed(1)} m`,left-8,y);}
  const timeLabels=[0,Math.floor((history.length-1)/2),history.length-1];ctx.textBaseline="bottom";timeLabels.forEach((index)=>{const x=left+index/Math.max(1,history.length)*width*.86;ctx.textAlign=index===0?"left":"center";ctx.fillText(history[index].time.toLocaleTimeString([],{hour:"2-digit",minute:"2-digit",second:"2-digit"}),x,box.height);});ctx.textAlign="right";ctx.fillText("+15 min",left+width,box.height);
  const point=(index,value)=>({x:left+index/Math.max(1,history.length)*width*.86,y:top+height-(value-min)/Math.max(.01,max-min)*height});
  const gradient=ctx.createLinearGradient(0,top,0,top+height);gradient.addColorStop(0,"rgba(79,213,231,.25)");gradient.addColorStop(1,"rgba(79,213,231,0)");ctx.beginPath();history.forEach((row,index)=>{const p=point(index,row.wave);index?ctx.lineTo(p.x,p.y):ctx.moveTo(p.x,p.y);});const last=point(history.length-1,history.at(-1).wave);ctx.lineTo(last.x,top+height);ctx.lineTo(left,top+height);ctx.closePath();ctx.fillStyle=gradient;ctx.fill();
  ctx.beginPath();history.forEach((row,index)=>{const p=point(index,row.wave);index?ctx.lineTo(p.x,p.y):ctx.moveTo(p.x,p.y);});ctx.strokeStyle="#4fd5e7";ctx.lineWidth=2.5;ctx.stroke();ctx.fillStyle="#4fd5e7";ctx.beginPath();ctx.arc(last.x,last.y,4,0,Math.PI*2);ctx.fill();
  if(Number.isFinite(forecast)){const target={x:left+width,y:top+height-(forecast-min)/Math.max(.01,max-min)*height};ctx.save();ctx.setLineDash([7,6]);ctx.beginPath();ctx.moveTo(last.x,last.y);ctx.lineTo(target.x,target.y);ctx.strokeStyle="#efba67";ctx.lineWidth=2.5;ctx.stroke();ctx.restore();ctx.fillStyle="#efba67";ctx.beginPath();ctx.arc(target.x,target.y,5,0,Math.PI*2);ctx.fill();ctx.fillStyle=muted;ctx.textAlign="right";ctx.textBaseline="bottom";ctx.fillText(`${forecast.toFixed(2)} m`,target.x-7,target.y-7);}
}

function renderWaveIntelligence(ai,details){
  const ready=ai.status==="READY",current=ai.currentWaveHeight,predicted=ai.predictedWaveHeight,mid=ready?current+(predicted-current)*Math.min(1,5/ai.horizonMinutes):null;
  $("reasoningState").textContent=ready?"COMPLETE":"COLLECTING";$("reasoningState").className=`tag ${ready?"tag-good":"tag-warn"}`;
  const first=supportingHistory[0]||{},last=supportingHistory.at(-1)||{},pressureChange=Number.isFinite(first.pressure)&&Number.isFinite(last.pressure)?last.pressure-first.pressure:null,windChange=Number.isFinite(first.wind)&&Number.isFinite(last.wind)?last.wind-first.wind:null;
  $("reasonPressure").textContent=pressureChange==null?"Water-pressure trend is still collecting.":`Water pressure ${Math.abs(pressureChange)<.05?"remained stable":pressureChange>0?"increased":"decreased"} by ${Math.abs(pressureChange).toFixed(2)} kPa across recent samples.`;
  $("reasonWind").textContent=windChange==null?"Wind-speed trend is still collecting.":`Wind speed ${Math.abs(windChange)<.2?"remained stable":windChange>0?"increased":"decreased"} from ${number(first.wind)} to ${number(last.wind)} km/h.`;
  const motion=Math.sqrt((latestWaveSnapshot?.roll||0)**2+(latestWaveSnapshot?.pitch||0)**2);$("reasonMotion").textContent=`Buoy oscillation is ${motion>8?"strong":motion>3?"elevated":"within normal range"} at ${number(motion,2)}° combined roll/pitch.`;
  $("reasonHistory").textContent=`Historical window contains ${ai.sampleCount||0} valid wave samples with a ${(ai.direction||"unknown").toUpperCase()} trend.`;
  $("reasoningPrediction").textContent=ready?`${number(predicted,2)} meters · ${ai.seaCondition}`:"Prediction unavailable";$("reasoningHorizon").textContent=ready?`Expected within ${ai.horizonMinutes} minutes`:`Need ${Math.max(0,8-(ai.sampleCount||0))} more valid samples`;
  $("confidenceLarge").textContent=ready?`${ai.confidence}%`:"--%";const label=!ready?"Collecting":ai.confidence>=80?"High confidence":ai.confidence>=60?"Moderate confidence":"Low confidence";$("confidenceLabel").textContent=label;$("confidenceBar").style.width=ready?`${ai.confidence}%`:"0%";$("confidenceReason").textContent=!ready?"Insufficient valid history.":ai.confidence>=80?"Recent signals are stable and the trend fit has low disagreement.":ai.confidence>=60?"Prediction is usable for presentation, with moderate signal variation.":"Sensor disagreement or high signal volatility reduced confidence.";
  $("timelineNow").textContent=Number.isFinite(current)?`${number(current,2)} m`:"-- m";$("timelineFive").textContent=Number.isFinite(mid)?`${number(mid,2)} m`:"-- m";$("timelineTargetLabel").textContent=`${ai.horizonMinutes} MIN`;$("timelineTarget").textContent=ready?`${number(predicted,2)} m`:"-- m";
  $("accuracySamples").textContent=ai.sampleCount||0;$("accuracyConfidence").textContent=ready?`${ai.confidence}%`:"--";$("signalAgreement").textContent=ready?(ai.confidence>=80?"STRONG":ai.confidence>=60?"MODERATE":"LOW"):"COLLECTING";$("accuracySource").textContent=String(ai.dataSource||"--").toUpperCase();drawWaveAiChart(predicted);
}

function drawWaveAiChart(predicted){
  const canvas=$("waveAiChart");if(!canvas||history.length<2)return;const box=canvas.getBoundingClientRect();if(!box.width)return;const ratio=Math.min(devicePixelRatio||1,2),ctx=canvas.getContext("2d"),styles=getComputedStyle(document.documentElement);canvas.width=box.width*ratio;canvas.height=box.height*ratio;ctx.scale(ratio,ratio);ctx.clearRect(0,0,box.width,box.height);const vals=history.map(x=>x.wave).concat(Number.isFinite(predicted)?[predicted]:[]),min=Math.max(0,Math.min(...vals)-.15),max=Math.max(...vals)+.15,left=44,right=18,top=10,bottom=25,w=box.width-left-right,h=box.height-top-bottom,y=v=>top+h-(v-min)/Math.max(.01,max-min)*h;
  ctx.font='9px "Segoe UI",sans-serif';ctx.fillStyle=styles.getPropertyValue("--muted");ctx.textAlign="right";ctx.textBaseline="middle";for(let i=0;i<=4;i++){const py=top+h*i/4,value=max-(max-min)*i/4;ctx.strokeStyle=styles.getPropertyValue("--line");ctx.beginPath();ctx.moveTo(left,py);ctx.lineTo(left+w,py);ctx.stroke();ctx.fillText(`${value.toFixed(1)}m`,left-6,py);}
  const pts=history.map((item,index)=>({x:left+index/Math.max(1,history.length)*w*.85,y:y(item.wave)}));const fill=ctx.createLinearGradient(0,top,0,top+h);fill.addColorStop(0,"rgba(79,213,231,.24)");fill.addColorStop(1,"rgba(79,213,231,0)");ctx.beginPath();pts.forEach((p,i)=>i?ctx.lineTo(p.x,p.y):ctx.moveTo(p.x,p.y));ctx.lineTo(pts.at(-1).x,top+h);ctx.lineTo(pts[0].x,top+h);ctx.closePath();ctx.fillStyle=fill;ctx.fill();ctx.beginPath();pts.forEach((p,i)=>i?ctx.lineTo(p.x,p.y):ctx.moveTo(p.x,p.y));ctx.strokeStyle="#4fd5e7";ctx.lineWidth=2.4;ctx.stroke();if(Number.isFinite(predicted)){const a=pts.at(-1),b={x:left+w,y:y(predicted)};ctx.save();ctx.setLineDash([7,6]);ctx.beginPath();ctx.moveTo(a.x,a.y);ctx.lineTo(b.x,b.y);ctx.strokeStyle="#efba67";ctx.stroke();ctx.restore();ctx.fillStyle="#efba67";ctx.beginPath();ctx.arc(b.x,b.y,5,0,Math.PI*2);ctx.fill();}
}

function renderLogs(){
  if(!$("logsTableBody"))return;$("logWaveCount").textContent=history.length;$("logPredictionCount").textContent=predictionLog.length;$("logAlertCount").textContent=latestAlerts.length;$("logDataSource").textContent=$("dataSource").textContent;
  const rows=predictionLog.slice(-60).reverse();$("logsTableBody").innerHTML=rows.length?rows.map(row=>`<tr><td>${new Date(row.recordedAt).toLocaleString()}</td><td>${number(row.current,2)} m</td><td>${number(row.predicted,2)} m</td><td>${row.horizon} min</td><td>${row.condition}</td><td>${row.confidence}%</td><td>${String(row.source).toUpperCase()}</td></tr>`).join(""):'<tr><td colspan="7">Collecting operational records...</td></tr>';
}

async function loadServerLogs(){
  if(Date.now()-lastLogsLoad<10000)return;lastLogsLoad=Date.now();try{const payload=await json("/logs?limit=60");if(Array.isArray(payload.predictions)&&payload.predictions.length){predictionLog.splice(0,predictionLog.length,...payload.predictions.slice().reverse().map(item=>({recordedAt:item.generatedAt,current:item.currentWaveHeight,predicted:item.predictedWaveHeight,horizon:item.horizonMinutes,condition:item.seaCondition,confidence:item.confidence,source:item.dataSource})));}renderLogs();}catch(error){console.warn("Server logs unavailable; using session history.",error);}
}

function exportLogs(format){
  const rows=predictionLog.slice();if(!rows.length)return toast("No prediction records available to export.","error");const content=format==="json"?JSON.stringify(rows,null,2):["recordedAt,currentWave,predictedWave,horizonMinutes,condition,confidence,source",...rows.map(r=>[r.recordedAt,r.current,r.predicted,r.horizon,r.condition,r.confidence,r.source].join(","))].join("\n"),blob=new Blob([content],{type:format==="json"?"application/json":"text/csv"}),link=document.createElement("a");link.href=URL.createObjectURL(blob);link.download=`falcon-predictions.${format}`;link.click();URL.revokeObjectURL(link.href);toast(`${format.toUpperCase()} export created.`);
}

function drawMiniCharts() {
  const styles=getComputedStyle(document.documentElement), grid=styles.getPropertyValue("--line"), series=[
    ["windChart","wind","#4fd5e7"],["pressureChart","pressure","#71d89b"],
    ["batteryChart","battery","#efba67"],["temperatureChart","temperature","#ee7a72"]
  ];
  series.forEach(([id,key,color])=>{
    const canvas=$(id),box=canvas.getBoundingClientRect(); if(!box.width)return;
    const ratio=Math.min(devicePixelRatio||1,2),ctx=canvas.getContext("2d");canvas.width=box.width*ratio;canvas.height=box.height*ratio;ctx.scale(ratio,ratio);ctx.clearRect(0,0,box.width,box.height);
    ctx.strokeStyle=grid;ctx.lineWidth=1;for(let i=1;i<3;i++){ctx.beginPath();ctx.moveTo(0,box.height*i/3);ctx.lineTo(box.width,box.height*i/3);ctx.stroke();}
    const points=supportingHistory.map((row,index)=>({index,value:row[key]})).filter(point=>Number.isFinite(point.value));if(points.length<2)return;
    const values=points.map(point=>point.value),min=Math.min(...values),max=Math.max(...values),padding=Math.max((max-min)*.2,.05),chartHeight=box.height-24;
    const coordinates=points.map(point=>({x:point.index/Math.max(1,supportingHistory.length-1)*box.width,y:chartHeight-((point.value-(min-padding))/Math.max(.01,max-min+padding*2))*(chartHeight-12)+6}));
    const fill=ctx.createLinearGradient(0,0,0,chartHeight);fill.addColorStop(0,`${color}38`);fill.addColorStop(1,`${color}00`);ctx.beginPath();coordinates.forEach((point,i)=>i?ctx.lineTo(point.x,point.y):ctx.moveTo(point.x,point.y));ctx.lineTo(coordinates.at(-1).x,chartHeight);ctx.lineTo(coordinates[0].x,chartHeight);ctx.closePath();ctx.fillStyle=fill;ctx.fill();
    ctx.beginPath();ctx.strokeStyle=color;ctx.lineWidth=2.2;coordinates.forEach((point,i)=>i?ctx.lineTo(point.x,point.y):ctx.moveTo(point.x,point.y));ctx.stroke();const last=coordinates.at(-1);ctx.fillStyle=color;ctx.beginPath();ctx.arc(last.x,last.y,3.5,0,Math.PI*2);ctx.fill();
    ctx.fillStyle=styles.getPropertyValue("--muted");ctx.font='9px "Segoe UI",sans-serif';ctx.textBaseline="bottom";ctx.textAlign="left";ctx.fillText(`MIN ${min.toFixed(key==="battery"?0:1)}`,2,box.height);ctx.textAlign="right";ctx.fillText(`MAX ${max.toFixed(key==="battery"?0:1)}`,box.width-2,box.height);
  });
}

async function poll() {
  if(pollBusy)return; pollBusy=true;setSyncing(true);
  try {
    const horizon=$("forecastHorizon").value;
    const [status,wave,gps,battery,solar,ai]=await Promise.all([json("/status"),json("/wave").catch(()=>null),json("/gps").catch(()=>null),json("/battery").catch(()=>null),json("/solar").catch(()=>null),json(`/ai?horizon=${horizon}`)]);
    renderStatus(status);if(wave)renderWave(wave);else renderWaveUnavailable();if(gps)renderGps(gps);if(battery)renderBattery(battery);if(solar)renderSolar(solar);renderAi(ai);drawMiniCharts();loadServerLogs();finishBoot();
  } catch(error) { $("edgeState").textContent="EDGE OFFLINE";$("liveBadge").textContent="OFFLINE";$("liveBadge").classList.add("is-offline");if(!firstTelemetryReceived)$("bootMessage").textContent="Waiting for local edge service…";console.error(error); }
  finally {pollBusy=false;setSyncing(false);}
}

$("forecastHorizon").addEventListener("change",poll);
async function syncScenario() { try { const state=await json("/api/scenario"); if(state.available&&state.active){$("scenarioSelect").value=state.active;$("scenarioState").textContent=scenarioLabels[state.active]||state.active.toUpperCase();} } catch(error){ console.warn("Scenario control unavailable",error); } }
function resetPresentationHistory(){history.length=0;supportingHistory.length=0;predictionLog.length=0;waveHistoryHydrated=false;supportingHistoryHydrated=false;latestAiSnapshot=null;$("chartEmpty").hidden=false;$("chartEmpty").textContent="Building scenario-specific history...";drawTrend();drawMiniCharts();}
$("scenarioSelect").addEventListener("change",async(event)=>{const select=event.target;select.disabled=true;try{const state=await json("/api/scenario",{method:"POST",body:JSON.stringify({scenario:select.value})});resetPresentationHistory();$("scenarioState").textContent=scenarioLabels[state.active]||state.active.toUpperCase();toast(`${scenarioLabels[state.active]} applied · Wave AI is rebuilding scenario-specific history.`);await poll();}catch(error){toast(error.message,"error");await syncScenario();}finally{select.disabled=false;}});
$("restartButton").addEventListener("click",async()=>{const button=$("restartButton");setButtonBusy(button,true,"Restarting");try{await json("/restart",{method:"POST",body:JSON.stringify({target:"esp32",reason:"dashboard authorized maintenance"})});toast("ESP32 restart request logged.");}catch(error){toast(error.message,"error");}finally{setButtonBusy(button,false);}});
$("calibrateButton").addEventListener("click",async()=>{const button=$("calibrateButton");setButtonBusy(button,true,"Calibrating");try{const sensor=$("calibrationSensor").value;await json("/calibrate",{method:"POST",body:JSON.stringify({sensor,operation:"start",reference:null})});toast(`${sensor} calibration started.`);}catch(error){toast(error.message,"error");}finally{setButtonBusy(button,false);}});
$("exportCsvButton").addEventListener("click",()=>exportLogs("csv"));$("exportJsonButton").addEventListener("click",()=>exportLogs("json"));
$("settingsRestartButton").addEventListener("click",()=>$("restartButton").click());
$("saveSettingsButton").addEventListener("click",()=>{const sampling=$("samplingRate").value,horizon=$("predictionInterval").value;localStorage.setItem("falcon-sampling-rate",sampling);localStorage.setItem("falcon-prediction-horizon",horizon);$("forecastHorizon").value=horizon;toast("Local dashboard preferences saved.");poll();});
window.addEventListener("resize",()=>{drawTrend();drawMiniCharts();});
const initialView=location.hash.slice(1);if(titles[initialView])setView(initialView);
const savedHorizon=localStorage.getItem("falcon-prediction-horizon");if(["5","10","15"].includes(savedHorizon)){$("forecastHorizon").value=savedHorizon;$("predictionInterval").value=savedHorizon;}
syncScenario();poll();setInterval(poll,2000);
