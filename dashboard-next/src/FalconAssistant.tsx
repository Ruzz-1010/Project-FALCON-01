import { type CSSProperties, type PointerEvent, useMemo, useState } from "react";
import { MessageCircle, Send, Sparkles, X } from "lucide-react";
import type { DashboardData } from "./types";

type Question="status"|"alerts"|"power"|"wave";
const labels:Record<Question,string>={status:"How is the station?",alerts:"Explain alerts",power:"Check power",wave:"Explain wave height"};
const number=(value:number|null|undefined,digits=1)=>value==null?"unavailable":value.toFixed(digits);

export default function FalconAssistant({data}:{data:DashboardData}){
  const [open,setOpen]=useState(false),[message,setMessage]=useState("Hello! Ask me about the latest FALCON station readings."),[typing,setTyping]=useState(false),[reaction,setReaction]=useState(false);
  const answers=useMemo<Record<Question,string>>(()=>({
    status:`The station is ${data.status.system.toLowerCase()}. Estimated wave height is ${number(data.wave.waveHeight,2)} meters, wind is ${number(data.status.windSpeed)} kilometers per hour, and GPS is ${data.current.security.state.toLowerCase()}.`,
    alerts:data.status.alerts.length?`There ${data.status.alerts.length===1?"is":"are"} ${data.status.alerts.length} active ${data.status.alerts.length===1?"alert":"alerts"}. ${data.status.alerts.slice(0,2).map(item=>item.message).join(" ")}`:"There are no active alerts. No condition currently needs operator attention.",
    power:`Battery is ${number(data.battery.percentage,0)} percent and ${data.battery.status.toLowerCase()}. Solar is ${data.solar.status.toLowerCase()} at about ${number(data.solar.power)} watts.`,
    wave:`The current pressure-based estimate is ${number(data.wave.waveHeight,2)} meters. It is a monitoring estimate from the underwater pressure sensor, not an official marine forecast.`
  }),[data]);
  const ask=(question:Question)=>{setTyping(true);setReaction(true);window.setTimeout(()=>{setMessage(answers[question]);setTyping(false)},420);window.setTimeout(()=>setReaction(false),900)};
  const toggle=()=>{setOpen(value=>!value);setReaction(true);window.setTimeout(()=>setReaction(false),900)};
  const track=(event:PointerEvent<HTMLButtonElement>)=>{const box=event.currentTarget.getBoundingClientRect(),x=(event.clientX-box.left)/box.width-.5,y=(event.clientY-box.top)/box.height-.5;event.currentTarget.style.setProperty("--look-x",`${x*5}px`);event.currentTarget.style.setProperty("--look-y",`${y*3}px`)};
  return <div className={`falcon-helper ${open?"is-open":""} ${reaction?"is-reacting":""}`}>
    {open&&<section className="falcon-chat" aria-label="FALCON Assistant">
      <header><span><Sparkles/><b>FALCON Assistant</b><small>Simple station guide</small></span><button onClick={()=>setOpen(false)} aria-label="Close assistant"><X/></button></header>
      <div className="falcon-message"><img src="/falcon-assistant-v1.png" alt=""/><p>{typing?<span className="falcon-typing"><i/><i/><i/></span>:message}</p></div>
      <div className="falcon-questions">{(Object.keys(labels) as Question[]).map(question=><button key={question} onClick={()=>ask(question)}>{labels[question]}</button>)}</div>
      <footer><span><MessageCircle/> Current station data</span><Send/></footer>
    </section>}
    <button className="falcon-peek" onClick={toggle} onPointerMove={track} onPointerLeave={event=>{event.currentTarget.style.removeProperty("--look-x");event.currentTarget.style.removeProperty("--look-y")}} aria-expanded={open} aria-label={open?"Close FALCON Assistant":"Open FALCON Assistant"} style={{"--look-x":"0px","--look-y":"0px"} as CSSProperties}>
      <span className="falcon-greeting">{open?"Hello!":"Need help?"}</span><span className="falcon-character"><img src="/falcon-assistant-v1.png" alt="FALCON Assistant"/><i className="falcon-lid left"/><i className="falcon-lid right"/><i className="falcon-beacon"/></span>
    </button>
  </div>;
}
