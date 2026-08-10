import type { DashboardData } from "./types";

async function get<T>(path: string): Promise<T> {
  const response = await fetch(path, { cache: "no-store" });
  if (!response.ok) throw new Error(`${path} returned ${response.status}`);
  return response.json() as Promise<T>;
}

export async function getOverview(): Promise<DashboardData> {
  const [status, wave, gps, battery, solar, ai] = await Promise.all([
    get<DashboardData["status"]>("/status"), get<DashboardData["wave"]>("/wave"),
    get<DashboardData["gps"]>("/gps"), get<DashboardData["battery"]>("/battery"),
    get<DashboardData["solar"]>("/solar"), get<DashboardData["ai"]>("/ai?horizon=10")
  ]);
  return { status, wave, gps, battery, solar, ai };
}
