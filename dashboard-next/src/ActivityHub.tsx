import { useState } from "react";
import { Bell, Database } from "lucide-react";
import type { DashboardData } from "./types";
import AlertsPage from "./AlertsPage";
import LogsPage from "./LogsPage";

export default function ActivityHub({data}:{data:DashboardData}) {
  const [view,setView]=useState<"alerts"|"logs">("alerts");
  return <><div className="activity-switch" role="group" aria-label="Logs and alerts view">
    <button aria-pressed={view==="alerts"} className={view==="alerts"?"is-active":""} onClick={()=>setView("alerts")}><Bell/> Alerts</button>
    <button aria-pressed={view==="logs"} className={view==="logs"?"is-active":""} onClick={()=>setView("logs")}><Database/> Logs</button>
  </div>{view==="alerts"?<AlertsPage data={data}/>:<LogsPage/>}</>;
}
