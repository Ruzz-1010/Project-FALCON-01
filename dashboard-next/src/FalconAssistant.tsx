import { useMemo, useState } from "react";
import { Bot, MessageCircle, Send, Sparkles, X } from "lucide-react";
import type { DashboardData } from "./types";

type Question="status"|"alerts"|"battery"|"wave";

const prompts:Record<Question,string>={status:"How is the station?",alerts:"Explain active alerts",battery:"Check battery and solar",wave:"Explain the wave reading"};
const value=(number:number|null|undefined,digits=1)=>number==null?"unavailable":number.toFixed(digits);

export default function FalconAssistant({data}:{data:DashboardData}){
  const [open,setOpen]=useState(false),[answer,setAnswer]=useState("Hello! I can explain the latest FALCON readings in simple terms."),[typing,setTyping]=useState(false);
  const answers=useMemo<Record<Question,string>>(()=>({
    status:`The station is ${data.status.system.toLowerCase()}. The latest estimated wave height is ${value(data.wave.waveHeight,2)} meters, wind is ${value(data.status.windSpeed)} kilometers per hour, and GPS status is ${data.current.security.state.toLowerCase()}.`,
    alerts:data.status.alerts.length?`There ${data.status.alerts.length===1?"is":"are"} ${data.status.alerts.length} active ${data.status.alerts.length===1?"alert":"alerts"}. ${data.status.alerts.slice(0,2).map(item=>item.message).join(" ")}`:"There are no active alerts. The dashboard has not detected a condition that currently needs operator attention.",
    battery:`Battery is at ${value(data.battery.percentage,0)} percent and its status is ${data.battery.status.toLowerCase()}. Solar input is ${data.solar.status.toLowerCase()} at approximately ${value(data.solar.power)} watts.`,
    wave:`The pressure-based estimated wave height is ${value(data.wave.waveHeight,2)} meters. This is calculated from the underwater pressure sensor and should be treated as a monitoring estimate, not an official marine forecast.`
  }),[data]);
  const ask=(question:Question)=>{setTyping(true);setAnswer("");window.setTimeout(()=>{setAnswer(answers[question]);setTyping(false)},450)};
  return <div className={`falcon-assistant ${open?"is-open":""}`}>
    {open&&<section className="assistant-dialog" aria-label="FALCON Assistant">
      <header><span><Sparkles/><b>FALCON Assistant</b><small>Station guide</small></span><button onClick={()=>setOpen(false)} aria-label="Close assistant"><X/></button></header>
      <div className="assistant-conversation"><div className="assistant-mini"><Bot/></div><p>{typing?<span className="typing"><i/><i/><i/></span>:answer}</p></div>
      <div className="assistant-prompts">{(Object.keys(prompts) as Question[]).map(key=><button key={key} onClick={()=>ask(key)}>{prompts[key]}</button>)}</div>
      <footer><span><MessageCircle/> Uses current station readings</span><Send/></footer>
    </section>}
    <button className="assistant-launcher" onClick={()=>setOpen(value=>!value)} aria-label={open?"Close FALCON Assistant":"Open FALCON Assistant"} aria-expanded={open}>
      <span className="assistant-speech">{open?"I'm ready!":"Need help?"}</span>
      <span className="assistant-mascot" aria-hidden="true">
        <i className="antenna"/><i className="ear left"/><i className="ear right"/>
        <span className="assistant-face"><i className="eye left"/><i className="eye right"/><i className="smile"/></span>
        <span className="assistant-body"><b>F</b></span>
        <i className="arm left"/><i className="arm right"><i className="hand">●</i></i>
      </span>
    </button>
  </div>;
}
