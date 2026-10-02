export const baySteps={
  computer:{title:'Bay Station computer',detail:'Shore computer receives, stores and processes buoy data for prediction and dashboard.',note:'Illustrative equipment. Final selection pending.'},
  station:{title:'FALCON-01 Bay Station',detail:'Receives buoy messages and runs local storage, processing and interface.',note:'Illustrative cutaway. Layout not finalized.'},
  rx:{title:'LoRa receiver',detail:'Receives buoy telemetry via antenna and passes records to computer.',note:'Radio and cabling illustrative. Internet backhaul separate.'},
  validate:{title:'Authenticate / validate',detail:'Checks station identity, message format, timestamps and quality.',note:'Software stage. Security validation pending.'},
  sqlite:{title:'SQLite / local storage',detail:'Stores raw and processed records with timestamps and quality flags.',note:'Software on same computer, not separate appliance.'},
  processing:{title:'Processing',detail:'Quality-checks observations and derives pressure-based estimated wave height.',note:'Calibration and validation required.'},
  ai:{title:'AI prediction',detail:'Produces short-term prediction from quality-checked estimated wave height.',note:'Runs on same computer. Results illustrative, model not validated.'},
  dashboard:{title:'Dashboard / alerts',detail:'Shows observations, system state and authorized alerts.',note:'Local display first. Remote access via shore Internet backhaul.'}
};
export const bayPipeline=['rx','validate','sqlite','processing','ai','dashboard'];
export function arrivalPhase(time,online=true){
  if(!online)return {receiver:false,cable:null,stage:-1};
  const phase=((time*.405)%1+1)%1;
  return {receiver:phase<.1,cable:phase>=.1&&phase<.42?(phase-.1)/.32:null,stage:phase>=.42?Math.min(5,Math.floor((phase-.42)/.58*6)):-1};
}
