import { Activity, BatteryCharging, BellRing, DoorOpen, Droplets, MapPin, Radio, Sun, Thermometer, Waves, Wind } from "lucide-react";
import type { DashboardData } from "./types";

const age=(recordedAt:string)=>Math.max(0,Date.now()-Date.parse(recordedAt));
const updated=(value:number)=>value<5000?`${(value/1000).toFixed(1)} s ago`:`${Math.round(value/1000)} s ago`;

export default function SensorsPage({data}:{data:DashboardData}){
  const simulated=data.status.dataSource==="simulator",fault=data.status.sensorsOnline<data.status.sensorsExpected,packetAge=age(data.status.lastUpdate);
  const rows=[
    {name:"Bar02 pressure sensor",role:"Core · pressure-based wave estimation",icon:Waves,rate:"10 Hz target",value:`${data.wave.filteredPressure?.toFixed(2)??"--"} kPa filtered`,quality:data.wave.quality*100,calibration:data.wave.calibration},
    {name:"GPS receiver",role:"Core · position and security geofence",icon:MapPin,rate:"1 Hz target",value:`${data.gps.fix} · ${data.gps.satellites} satellites`,quality:data.gps.valid?92:0,calibration:"DEPLOYMENT REFERENCE REQUIRED"},
    {name:"Wind speed",role:"Anemometer pulse input",icon:Wind,rate:"1 Hz output",value:`${data.status.windSpeed?.toFixed(1)??"--"} km/h`,quality:fault?55:90,calibration:"PENDING FIELD REFERENCE"},
    {name:"Wind direction",role:"Vane through ADS1115",icon:Radio,rate:"4 Hz target",value:data.status.windDirection||"--",quality:fault?55:88,calibration:"PENDING DIRECTION TABLE"},
    {name:"DS18B20",role:"Supporting · sealed water temperature",icon:Thermometer,rate:"1 Hz target",value:`${data.current.environment.waterTemperature?.toFixed(1)??"--"} °C`,quality:90,calibration:"FIELD COMPARISON REQUIRED"},
    {name:"Conductivity sensor",role:"Supporting · salinity indicator",icon:Droplets,rate:"1 Hz target",value:`${data.current.environment.salinity?.toFixed(1)??"--"} ppt`,quality:72,calibration:"ESTIMATED · CALIBRATION REQUIRED"},
    {name:"Enclosure temperature",role:"System health · electronics enclosure",icon:Thermometer,rate:"1 Hz target",value:`${data.status.internalTemperature?.toFixed(1)??"--"} °C`,quality:94,calibration:"VERIFY AGAINST REFERENCE"},
    {name:"INA260 battery",role:"Battery branch power",icon:BatteryCharging,rate:"2 Hz target",value:`${data.battery.voltage?.toFixed(2)??"--"} V · ${data.battery.current?.toFixed(2)??"--"} A`,quality:data.battery.valid?93:0,calibration:"PENDING METER CHECK"},
    {name:"INA260 solar",role:"Solar branch power",icon:Sun,rate:"2 Hz target",value:`${data.solar.voltage?.toFixed(1)??"--"} V · ${data.solar.current?.toFixed(2)??"--"} A`,quality:data.solar.valid?91:0,calibration:"PENDING METER CHECK"},
    {name:"Tamper input",role:"Security · vibration/tamper detection",icon:BellRing,rate:"Debounced event",value:data.current.security.vibrationDetected?"DETECTED":"CLEAR",quality:90,calibration:"PERSISTENCE TEST REQUIRED"},
    {name:"Enclosure switch",role:"Security · reed/limit switch",icon:DoorOpen,rate:"Debounced event",value:data.current.security.enclosureOpen?"OPEN":"CLOSED",quality:92,calibration:"VERIFY INSTALLED POSITION"},
  ];
  return <section className="content engineering-page"><div className="page-head"><div><span>SENSOR ACQUISITION & QUALITY</span><h1>Sensor status</h1><p>Availability, configured sampling targets, calibration readiness, and signal quality.</p></div><em className={`sensor-chip ${fault?"is-warning":""}`}><i/> {data.status.sensorsOnline}/{data.status.sensorsExpected} CHANNELS REPORTING</em></div>
    <div className="truth-banner"><Activity/><span><b>{simulated?"SIMULATED SENSOR TELEMETRY":"LIVE SENSOR TELEMETRY"}</b>{simulated?"Values and quality scores are research-demo data; physical calibration is not yet complete.":"Calibration records must be checked before scientific use."}</span></div>
    <div className="sensor-grid">{rows.map(({name,role,icon:Icon,rate,value,quality,calibration})=><article className="panel sensor-detail" key={name}><header><Icon/><div><span>{role}</span><h2>{name}</h2></div><em className={quality>=80?"good":"warn"}>{quality?"REPORTING":"OFFLINE"}</em></header><strong>{value}</strong><dl><div><dt>Health</dt><dd>{quality>=80?"HEALTHY":"REVIEW"}</dd></div><div><dt>Sampling</dt><dd>{rate}</dd></div><div><dt>Last update</dt><dd>{updated(packetAge)}</dd></div><div><dt>Calibration</dt><dd>{calibration}</dd></div></dl><div className="quality-meter"><span>Signal quality <b>{Math.round(quality)}%</b></span><i><em style={{width:`${quality}%`}}/></i></div></article>)}</div>
  </section>;
}
