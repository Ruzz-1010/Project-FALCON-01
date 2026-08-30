import { BrainCircuit, Cpu, Database, Gauge, LayoutDashboard, Radio, Server, SlidersHorizontal, Waves } from "lucide-react";
const nodes=[
  {name:"Sensors",detail:"Motion · pressure · wind · GPS · power",icon:Waves},
  {name:"ESP32",detail:"Acquisition · checks · telemetry framing",icon:Cpu},
  {name:"Bay Station",detail:"Shore processing · storage · AI · dashboard",icon:Server},
  {name:"SQLite",detail:"Telemetry · alerts · predictions · events",icon:Database},
  {name:"Feature engineering",detail:"Validated windows · trends · quality gates",icon:SlidersHorizontal},
  {name:"AI prediction",detail:"5 / 10 / 15 minute research horizons",icon:BrainCircuit},
  {name:"Explainable AI",detail:"Inputs · method · confidence · uncertainty",icon:Gauge},
  {name:"Dashboard",detail:"Measured · estimated · predicted · simulated",icon:LayoutDashboard},
];
export default function ArchitecturePage(){return <section className="content engineering-page"><div className="page-head"><div><span>TRACEABLE DATA PIPELINE</span><h1>AI architecture</h1><p>The existing local-first workflow from physical sensing to transparent research output.</p></div><em className="sensor-chip"><i/> CURRENT ARCHITECTURE</em></div><div className="architecture-chain">{nodes.map(({name,detail,icon:Icon},index)=><div className="architecture-node" key={name}><article className="panel"><Icon/><span>STAGE {String(index+1).padStart(2,"0")}</span><h2>{name}</h2><p>{detail}</p></article>{index<nodes.length-1&&<i>↓</i>}</div>)}</div><article className="panel future-interfaces"><Radio/><div><span>FUTURE INTERFACES · NOT IMPLEMENTED</span><h2>Cloud sync · LTE · satellite · remote monitoring · additional sensors</h2><p>Extension boundaries are reserved after the local system is calibrated and validated. Core acquisition remains independent of optional remote services.</p></div></article></section>}
