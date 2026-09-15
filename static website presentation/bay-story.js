export const baySteps={
  station:{title:'FALCON-01 Bay Station',detail:'Receives buoy observations and runs local storage, processing and the shore-based interface.',note:'Illustrative cutaway. Equipment model and final installation layout are not yet specified.'},
  rx:{title:'LoRa receiver',detail:'Receives telemetry transmitted from the offshore buoy. A cable carries the received records into the station.',note:'One shore-mounted pole and compact receiver. Internet backhaul is separate.'},
  validate:{title:'Authenticate / validate',detail:'Checks station identity, message format, timestamps and quality before accepting telemetry.',note:'A software stage on the shore computer; security validation remains to be demonstrated.'},
  sqlite:{title:'SQLite / local storage',detail:'Stores raw and processed records locally, preserving their timestamps and quality flags.',note:'Local storage supports retention when shore Internet is unavailable.'},
  processing:{title:'Processing',detail:'Quality-checks observations and derives the pressure-based estimated wave-height statistic.',note:'Calibration and deployment validation remain required.'},
  ai:{title:'AI prediction',detail:'Produces a short-term prediction from versioned, calibrated wave-height data.',note:'Shore-side software. This animation is illustrative, not a validated model result.'},
  dashboard:{title:'Dashboard / alerts',detail:'Presents current observations, system state and authorized alerts.',note:'Local display first; authorized remote access uses shore Internet backhaul.'}
};
export const bayPipeline=['rx','validate','sqlite','processing','ai','dashboard'];
export function arrivalPhase(time,online=true){
  if(!online)return {receiver:false,cable:null,stage:-1};
  const phase=((time*.405)%1+1)%1;
  return {receiver:phase<.1,cable:phase>=.1&&phase<.42?(phase-.1)/.32:null,stage:phase>=.42?Math.min(5,Math.floor((phase-.42)/.58*6)):-1};
}
