export type Alert = { code: string; severity: string; message: string };

export type Status = {
  system: string; sensorsOnline: number; sensorsExpected: number; lastUpdate: string;
  dataSource: string; windSpeed: number | null; windDirection: string | null;
  internalTemperature: number | null; alerts: Alert[];
};

export type Wave = {
  waveHeight: number | null; waveHeightState: string; pressure: number | null;
  recordedAt: string; valid: boolean;
  history: Array<{ recordedAt: string; waveHeight: number | null }>;
};

export type Gps = { valid: boolean; fix: string; satellites: number };
export type Battery = { percentage: number | null; status: string };
export type Solar = { power: number | null; status: string };
export type Prediction = {
  status: string; predictedWaveHeight: number | null; currentWaveHeight: number | null;
  seaCondition: string; confidence: number; horizonMinutes: number;
};

export type DashboardData = { status: Status; wave: Wave; gps: Gps; battery: Battery; solar: Solar; ai: Prediction };
