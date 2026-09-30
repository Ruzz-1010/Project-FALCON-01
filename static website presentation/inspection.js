export const inspections = {
  pressure: {name:'Underwater Pressure', function:'Measures underwater pressure variation for the documented wave-estimation method.', data:['Pressure','Timestamp','Quality state','Calibration status'], flow:['PRESSURE','PROCESSING','ESTIMATED WAVE HEIGHT'], status:'CALIBRATION REQUIRED', note:'HPT604 deployment candidate. Pressure is not a direct wave-height measurement.'},
  wind: {name:'Wind Observation', function:'Measures wind speed and direction for coastal environmental observations.', data:['Wind speed','Wind direction','Timestamp','Sensor quality'], flow:['WIND SENSOR','ESP32'], status:'VALIDATION PENDING', note:'Environmental context—not automatically an AI input.'},
  gps: {name:'GPS / Position', function:'Provides position and timing for location-aware monitoring and security.', data:['Latitude','Longitude','GPS quality / status','Timestamp'], flow:['GPS','ESP32','SECURITY LOGIC'], status:'VALIDATION PENDING', note:'Normal GPS scatter is not theft. Quality checks and persistence are required.'},
  battery: {name:'Battery / Energy Storage', function:'Stores solar energy and supplies power to the buoy electronics when solar input is unavailable or insufficient.', data:['Battery state','Solar / charging state','System health'], flow:['SOLAR','BATTERY','ELECTRONICS'], status:'ENERGY STORAGE / MONITORING', note:'LiFePO4 battery is the energy-storage element. Energy performance remains subject to measured validation.'},
  solar: {name:'Solar / Power', function:'Provides and monitors energy for the buoy electronics.', data:['Battery state','Solar / power status','Voltage / current','Energy telemetry','System health'], flow:['SOLAR','BATTERY','ELECTRONICS'], status:'NO MEASURED POWER CLAIM', note:'Energy flow is conceptual. No measured values are invented.'},
  esp32: {name:'ESP32 Controller', function:'Acquires, timestamps and validates sensor data; builds telemetry packets and buffers them during LoRa outages.', data:['Sensor records','Timestamp / quality','Telemetry packet','Buffered records'], flow:['SENSORS','ESP32','PACKET','LoRa'], status:'BUOY-SIDE CONTROLLER', note:'Inspecting the control enclosure, not an exposed circuit board. Main processing and AI remain on shore.'}
};
export function easeInspection(value){const t=Math.max(0,Math.min(1,value));return t*t*t*(t*(t*6-15)+10);}
export function inspectionDistance(size,aspect){return Math.max(.48,size*.9/Math.tan(21*Math.PI/180)/Math.min(1,aspect));}
export function inspectionFrame(center,size,aspect,mobile,currentEye=null){
  const distance=inspectionDistance(size,aspect);
  // Approach from the viewer's current side of the model so inspection feels like
  // a continuous camera move instead of a jump to an arbitrary compass direction.
  let direction=currentEye
    ? currentEye.map((v,i)=>v-center[i])
    : [center[0],.3,center[2]];
  if(Math.hypot(...direction)<.1)direction=[1,.35,1];
  const length=Math.hypot(...direction);direction=direction.map(v=>v/length);
  const right=[direction[2],0,-direction[0]],r=Math.max(.001,Math.hypot(...right));
  const eye=center.map((v,i)=>v+direction[i]*distance);
  const aim=center.map((v,i)=>v+(mobile&&i===1?-distance*.08:0));
  return {distance,eye,aim};
}
