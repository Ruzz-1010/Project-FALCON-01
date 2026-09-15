export const baySteps={
  computer:{title:'Bay Station computer',detail:'Local ingestion, validation, SQLite storage, processing and prediction run on this shore computer.',note:'Illustrative mini PC. Software functions share this computer; final equipment selection is pending.'},
  station:{title:'FALCON-01 Bay Station',detail:'Receives buoy observations and runs local storage, processing and the shore-based interface.',note:'Illustrative cutaway. Equipment model and final installation layout are not yet specified.'},
  rx:{title:'LoRa receiver',detail:'Receives telemetry from the offshore buoy through the outdoor antenna connection and passes records to the Bay Station computer.',note:'The indoor radio and cabling are illustrative. Internet backhaul is separate.'},
  validate:{title:'Authenticate / validate',detail:'Checks station identity, message format, timestamps and quality before accepting telemetry.',note:'A software stage on the shore computer; security validation remains to be demonstrated.'},
  sqlite:{title:'SQLite / local storage',detail:'Stores raw and processed records locally, preserving their timestamps and quality flags.',note:'Software on the same Bay Station computer—not a separate SQLite appliance.'},
  processing:{title:'Processing',detail:'Quality-checks observations and derives the pressure-based estimated wave-height statistic.',note:'Calibration and deployment validation remain required.'},
  ai:{title:'AI prediction',detail:'Produces a short-term prediction from versioned, calibrated wave-height data.',note:'Runs on this same computer. Predicted future wave height is distinct from the current pressure-derived estimate. Results shown are illustrative.'},
  dashboard:{title:'Dashboard / alerts',detail:'Presents current observations, system state and authorized alerts.',note:'Local display first; authorized remote access uses shore Internet backhaul.'}
};
export const bayPipeline=['rx','validate','sqlite','processing','ai','dashboard'];
export function arrivalPhase(time,online=true){
  if(!online)return {receiver:false,cable:null,stage:-1};
  const phase=((time*.405)%1+1)%1;
  return {receiver:phase<.1,cable:phase>=.1&&phase<.42?(phase-.1)/.32:null,stage:phase>=.42?Math.min(5,Math.floor((phase-.42)/.58*6)):-1};
}
