// Page 01 targets come from the supplied CAD hierarchy, never from hand-placed offsets.
export const instrumentPrefixes={
  pressure:'WATER_PRESSURE_SENSOR_ASSEMBLY',wind:'WIND_SPEED_DIRECTION_SENSOR',
  gps:'GNSS_GPS_ANTENNA',solar:'SOLAR_30W_01_EAST_+X',battery:'LIFEPO4_BATTERY_12V_ENVELOPE',esp32:'ESP32_CONTROLLER_ENVELOPE'
};
export function instrumentTargets(root){
  const result=new Map();
  for(const [id,prefix] of Object.entries(instrumentPrefixes)){const aliases=id==='battery'?[prefix,'LIFEPO4_BATTERY','BATTERY_12V','BATTERY']: [prefix];root.traverse(object=>{if(!result.has(id)){const name=object.name.toUpperCase();if(aliases.some(alias=>name.startsWith(alias)))result.set(id,object);}});}
  return result;
}
export const instrumentInfo={
  pressure:{name:'Underwater pressure',function:'Measures pressure variation for pressure-derived estimated wave height.',data:['Pressure','Time / quality','Calibration state'],flow:['PRESSURE','SHORE PROCESSING','ESTIMATED WAVE HEIGHT'],status:'CALIBRATION REQUIRED',note:'HPT604 deployment candidate. Pressure is the input—not a direct wave-height reading.'},
  wind:{name:'Wind observation',function:'Measures wind speed and direction around the buoy.',data:['Wind speed','Wind direction','Time / quality'],flow:['WIND','ESP32'],status:'PRIMARY MEASUREMENT',note:'A primary Phase 1 measurement. Comparison against a reference anemometer is still pending.'},
  gps:{name:'GPS / position',function:'Provides position and timing for location-aware monitoring.',data:['Position','Time','Fix quality'],flow:['GPS','ESP32'],status:'POSITION / TIME',note:'GPS scatter alone is not a security incident.'},
  solar:{name:'Solar / power',function:'Supplies solar energy and supports power-system monitoring.',data:['Voltage / current','Battery / solar status','System health'],flow:['SOLAR','BATTERY','ELECTRONICS'],status:'ENERGY SUPPLY / MONITORING',note:'Inspecting one actual panel of the two-panel array. No measured output is claimed.'},
  battery:{name:'Battery / energy storage',function:'Stores solar energy and supplies power to the buoy electronics when solar input is unavailable or insufficient.',data:['Battery state','Solar / charging state','System health'],flow:['SOLAR','BATTERY','ELECTRONICS'],status:'ENERGY STORAGE / MONITORING',note:'LiFePO4 battery is the energy-storage element. Energy performance remains subject to measured validation.'},
  esp32:{name:'ESP32 controller',function:'Acquires sensor records, checks timestamps and quality, and prepares LoRa telemetry.',data:['Sensor records','Telemetry packets','Outage buffer'],flow:['SENSORS','ESP32','LoRa'],status:'SENSING / CONTROL / TELEMETRY',note:'Controller is inside this actual enclosure. The exterior stays intact; no invented exposed board.'}
};
