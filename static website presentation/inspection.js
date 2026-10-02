export const inspections = {
  pressure: {name:'Underwater Pressure', function:'Senses pressure under the water. That reading travels to shore, where it becomes an estimated wave height.', data:['Pressure','Timestamp','Quality state','Calibration status'], flow:['PRESSURE','SHORE PROCESSING','ESTIMATED WAVE HEIGHT'], status:'CALIBRATION REQUIRED', note:'HPT604 deployment candidate. Pressure is the input—not a direct wave-height reading.'},
  wind: {name:'Wind Observation', function:'Measures wind speed and direction at the buoy.', data:['Wind speed','Wind direction','Timestamp','Sensor quality'], flow:['WIND SENSOR','ESP32'], status:'VALIDATION PENDING', note:'Wind is a primary Phase 1 measurement; comparison against a reference is still pending.'},
  gps: {name:'GPS / Position', function:'Provides position and timing for the system.', data:['Latitude','Longitude','GPS quality / status','Timestamp'], flow:['GPS','ESP32','SECURITY LOGIC'], status:'VALIDATION PENDING', note:'Normal GPS scatter is not theft. Quality checks and persistence come first.'},
  battery: {name:'Battery / Energy Storage', function:'Stores solar energy and powers the buoy electronics when the sun is low.', data:['Battery state','Solar / charging state','System health','Timestamp'], flow:['SOLAR','BATTERY','ELECTRONICS'], status:'ENERGY STORAGE / MONITORING', note:'LiFePO4 battery is the energy-storage element. Performance still needs measured validation.'},
  solar: {name:'Solar / Power', function:'Collects and monitors the energy that runs the buoy.', data:['Battery state','Solar / power status','Voltage / current','Energy telemetry'], flow:['SOLAR','BATTERY','ELECTRONICS'], status:'NO MEASURED POWER CLAIM', note:'Energy flow is conceptual. No measured value is invented.'},
  esp32: {name:'ESP32 Controller', function:'Reads the sensors, checks timestamps and quality, and prepares LoRa telemetry.', data:['Sensor records','Timestamp / quality','Telemetry packet','Buffered records'], flow:['SENSORS','ESP32','PACKET','LoRa'], status:'BUOY-SIDE CONTROLLER', note:'Inspecting the actual control enclosure. Main processing and AI remain on shore.'},
  lora: {name:'LoRa Transceiver', function:'Provides radio link from buoy to shore Bay Station for telemetry.', data:['Link state','Packet sequence','Buffer depth','RSSI'], flow:['ESP32','LoRa TX','LoRa RX','BAY STATION'], status:'ILLUSTRATIVE PLACEMENT', note:'Illustrative placement uses the NAVIGATION_LIGHT model from the upper equipment deck. No field range or hardware claim.'}
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
