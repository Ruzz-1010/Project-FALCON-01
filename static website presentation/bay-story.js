export const baySteps={
  computer:{title:'Bay Station computer',detail:'This shore computer receives the buoy’s data, stores it, processes it, and prepares the prediction and dashboard.',note:'Illustrative shore computer. Final equipment selection is still pending.'},
  station:{title:'FALCON-01 Bay Station',detail:'Receives the buoy’s messages and runs the local storage, processing, and interface.',note:'Illustrative cutaway. The final installation layout is not yet specified.'},
  rx:{title:'LoRa receiver',detail:'Receives the buoy’s telemetry through the outdoor antenna and passes each record to the computer.',note:'The indoor radio and cabling are illustrative. Internet backhaul is separate.'},
  validate:{title:'Authenticate / validate',detail:'Checks the station identity, message format, timestamps, and quality before accepting any data.',note:'A software stage on the shore computer; security validation still needs to be demonstrated.'},
  sqlite:{title:'SQLite / local storage',detail:'Stores raw and processed records locally, keeping their original timestamps and quality flags.',note:'Software on the same shore computer—not a separate appliance.'},
  processing:{title:'Processing',detail:'Quality-checks the observations and derives the pressure-based estimated wave height.',note:'Calibration and deployment validation are still required.'},
  ai:{title:'AI prediction',detail:'Produces a short-term prediction from versioned, quality-checked estimated wave-height data.',note:'Runs on this same computer. The predicted value is separate from the current estimate. Calibration and model evaluation are not completed; results shown are illustrative.'},
  dashboard:{title:'Dashboard / alerts',detail:'Shows current observations, system state, and authorized alerts.',note:'Local display first; authorized remote access uses the shore Internet backhaul.'}
};
export const bayPipeline=['rx','validate','sqlite','processing','ai','dashboard'];
export function arrivalPhase(time,online=true){
  if(!online)return {receiver:false,cable:null,stage:-1};
  const phase=((time*.405)%1+1)%1;
  return {receiver:phase<.1,cable:phase>=.1&&phase<.42?(phase-.1)/.32:null,stage:phase>=.42?Math.min(5,Math.floor((phase-.42)/.58*6)):-1};
}
