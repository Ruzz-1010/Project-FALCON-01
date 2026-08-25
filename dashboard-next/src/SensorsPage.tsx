import { Activity, Anchor, BatteryCharging, MapPin, Radio, Sun, Thermometer, Waves, Wind } from "lucide-react";
import type { DashboardData } from "./types";

const age=(recordedAt:string)=>Math.max(0,Date.now()-Date.parse(recordedAt));
const updated=(value:number)=>value<5000?`${(value/1000).toFixed(1)} s ago`:`${Math.round(value/1000)} s ago`;

export default function SensorsPage({data}:{data:DashboardData}){
  const simulated=data.status.dataSource==="simulator",fault=data.status.sensorsOnline<data.status.sensorsExpected,packetAge=age(data.status.lastUpdate);
  const rows=[
    {name:"Mooring tension sensor",role:"Anchor-chain load measurement",icon:Anchor,rate:"RATE UNDER REVIEW",value:"NOT YET CONNECTED",quality:0,calibration:"TYPE, RANGE & MOUNTING PENDING"},
    {name:"Bar02 pressure",role:"Water-pressure input",icon:Waves,rate:"10 Hz target",value:`${data.wave.pressure?.toFixed(2)??"--"} kPa`,quality:data.wave.quality*100,calibration:"PENDING DEPTH REFERENCE"},
    {name:"GPS receiver",role:"Position and displacement",icon:MapPin,rate:"1 Hz target",value:`${data.gps.fix} · ${data.gps.satellites} satellites`,quality:data.gps.valid?92:0,calibration:"REFERENCE POINT REQUIRED"},
    {name:"Wind speed",role:"Anemometer pulse input",icon:Wind,rate:"1 Hz output",value:`${data.status.windSpeed?.toFixed(1)??"--"} km/h`,quality:fault?55:90,calibration:"PENDING FIELD REFERENCE"},
    {name:"Wind direction",role:"Vane through ADS1115",icon:Radio,rate:"4 Hz target",value:data.status.windDirection||"--",quality:fault?55:88,calibration:"PENDING DIRECTION TABLE"},
    {name:"MCP9808",role:"Electronics-pod temperature",icon:Thermometer,rate:"1 Hz target",value:`${data.status.internalTemperature?.toFixed(1)??"--"} °C`,quality:94,calibration:"FACTORY · VERIFY"},
    {name:"INA260 battery",role:"Battery branch power",icon:BatteryCharging,rate:"2 Hz target",value:`${data.battery.voltage?.toFixed(2)??"--"} V · ${data.battery.current?.toFixed(2)??"--"} A`,quality:data.battery.valid?93:0,calibration:"PENDING METER CHECK"},
    {name:"INA260 solar",role:"Solar branch power",icon:Sun,rate:"2 Hz target",value:`${data.solar.voltage?.toFixed(1)??"--"} V · ${data.solar.current?.toFixed(2)??"--"} A`,quality:data.solar.valid?91:0,calibration:"PENDING METER CHECK"},
  ];
  return <section className="content engineering-page"><div className="page-head"><div><span>SENSOR ACQUISITION & QUALITY</span><h1>Sensor status</h1><p>Availability, configured sampling targets, calibration readiness, and signal quality.</p></div><em className={`sensor-chip ${fault?"is-warning":""}`}><i/> {data.status.sensorsOnline}/{data.status.sensorsExpected} CHANNELS REPORTING</em></div>
    <div className="truth-banner"><Activity/><span><b>{simulated?"SIMULATED SENSOR TELEMETRY":"LIVE SENSOR TELEMETRY"}</b>{simulated?"Values and quality scores are research-demo data; physical calibration is not yet complete.":"Calibration records must be checked before scientific use."}</span></div>
    <div className="sensor-grid">{rows.map(({name,role,icon:Icon,rate,value,quality,calibration})=><article className="panel sensor-detail" key={name}><header><Icon/><div><span>{role}</span><h2>{name}</h2></div><em className={quality>=80?"good":"warn"}>{quality?"REPORTING":"OFFLINE"}</em></header><strong>{value}</strong><dl><div><dt>Health</dt><dd>{quality>=80?"HEALTHY":"REVIEW"}</dd></div><div><dt>Sampling</dt><dd>{rate}</dd></div><div><dt>Last update</dt><dd>{updated(packetAge)}</dd></div><div><dt>Calibration</dt><dd>{calibration}</dd></div></dl><div className="quality-meter"><span>Signal quality <b>{Math.round(quality)}%</b></span><i><em style={{width:`${quality}%`}}/></i></div></article>)}</div>
  </section>;
}
