import type { AlertRecord, DashboardData, ScenarioState } from "./types";

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
export async function setScenario(scenario: string): Promise<ScenarioState> {
  const response = await fetch("/api/scenario", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ scenario }) });
  if (!response.ok) throw new Error(`Scenario update returned ${response.status}`);
  return response.json() as Promise<ScenarioState>;
}
