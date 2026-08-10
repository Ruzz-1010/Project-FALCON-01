import type { AlertRecord, DashboardData, LogsPayload, ScenarioState } from "./types";

async function get<T>(path: string): Promise<T> {
  const response = await fetch(path, { cache: "no-store" });
  if (!response.ok) throw new Error(`${path} returned ${response.status}`);
  return response.json() as Promise<T>;
}

async function getWave(): Promise<DashboardData["wave"]> {
  const response = await fetch("/wave", { cache: "no-store" });
  const payload = await response.json() as DashboardData["wave"];
  if (!response.ok && response.status !== 503) throw new Error(`/wave returned ${response.status}`);
  return payload;
}

export async function getOverview(horizon = 10): Promise<DashboardData> {
  const [status, wave, gps, battery, solar, ai] = await Promise.all([
    get<DashboardData["status"]>("/status"), getWave(),
    get<DashboardData["gps"]>("/gps"), get<DashboardData["battery"]>("/battery"),
    get<DashboardData["solar"]>("/solar"), get<DashboardData["ai"]>(`/ai?horizon=${horizon}`)
  ]);
  return { status, wave, gps, battery, solar, ai };
}

export const getScenario = () => get<ScenarioState>("/api/scenario");
export async function getAlerts(limit=100):Promise<AlertRecord[]>{return (await get<{items:AlertRecord[]}>(`/api/alerts?limit=${limit}`)).items;}
export const getLogs=(limit=100)=>get<LogsPayload>(`/logs?limit=${limit}`);
async function post<T>(path:string,body:Record<string,unknown>):Promise<T>{const response=await fetch(path,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)});const payload=await response.json();if(!response.ok)throw new Error(payload.message||`${path} returned ${response.status}`);return payload as T;}
export const requestRestart=(target:"esp32"|"service"|"mini-pc")=>post<{accepted:boolean;target:string;status:string}>("/restart",{target,reason:"dashboard authorized maintenance"});
export const startCalibration=(sensor:string)=>post<{accepted:boolean;sensor:string;status:string;calibrationId:string}>("/calibrate",{sensor,operation:"start",reference:null});
export async function setScenario(scenario: string): Promise<ScenarioState> {
  const response = await fetch("/api/scenario", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ scenario }) });
  if (!response.ok) throw new Error(`Scenario update returned ${response.status}`);
  return response.json() as Promise<ScenarioState>;
}
