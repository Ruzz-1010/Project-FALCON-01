export type Alert = { code: string; severity: string; message: string };

export type Status = {
  system: string; sensorsOnline: number; sensorsExpected: number; lastUpdate: string;
  dataSource: string; windSpeed: number | null; windDirection: string | null;
  internalTemperature: number | null; alerts: Alert[];
  intakeFanRpm: number | null; exhaustFanRpm: number | null;
  sensorHistory: Array<{recordedAt:string;windSpeed:number|null;internalTemperature:number|null}>;
  monitoring:boolean; uptimeSeconds:number; esp32:string; miniPc:string; uart:string; api:string;
  cpuUsage:number|null; memoryUsage:number|null; storageUsage:number|null; wifiSignalDbm:number|null;
  version:string; dashboardVersion:string; lastError:string|null; activeAlertCount:number;
};

export type Wave = {
  waveHeight: number | null; waveHeightState: string; pressure: number | null;
  recordedAt: string; valid: boolean; roll: number | null; pitch: number | null;
  yaw: number | null; waveMotion: number | null; quality: number;
  history: Array<{ recordedAt: string; waveHeight: number | null }>;
};

export type Gps = {
  valid: boolean; fix: string; satellites: number; recordedAt: string;
  latitude: number | null; longitude: number | null; horizontalAccuracyMeters: number | null;
  referenceLatitude: number; referenceLongitude: number; deploymentName: string;
  deploymentReferenceState: string; anchorDistanceMeters: number | null; driftStatus: string;
  headingDegrees: number | null; surfaceSpeedKnots: number | null; signalQuality: string;
};
export type Battery = { percentage: number | null; status: string; valid:boolean; recordedAt:string; voltage:number|null; current:number|null; direction:string; temperature:number|null; estimatedRuntimeHours:number|null; powerConsumptionWatts:number|null; history:Array<{recordedAt:string;percentage:number|null;voltage:number|null}> };
export type Solar = { power: number | null; status: string; valid:boolean; recordedAt:string; voltage:number|null; current:number|null; charging:boolean };
export type Prediction = {
  status: string; predictedWaveHeight: number | null; currentWaveHeight: number | null;
  seaCondition: string; confidence: number; horizonMinutes: number; change: number | null;
  direction: string; targetAt: string | null; model: string; modelVersion: string;
  sampleCount: number; dataSource: string; unavailableReason: string | null;
  explanation?: {
    method: string; input: string; steps: string[];
    details: { validSamples: number; sampleWindowSeconds: number; trendMetersPerMinute: number; rawProjection: number; maximumAllowedChange: number; limitApplied: boolean; residualVolatility: number; dampingFactor: number };
  };
};

export type ScenarioState = { available: boolean; active: string | null; scenarios: string[]; appliedAt?: string; aiState?: string };

export type DashboardData = { status: Status; wave: Wave; gps: Gps; battery: Battery; solar: Solar; ai: Prediction };
