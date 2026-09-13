export const sensors=[
  {id:'pressure',name:'Underwater pressure',part:'Holykell HPT604 Type A',purpose:'Measures underwater pressure variation, not wave height directly.',data:'4–20 mA → protected receiver → pressure record',location:'Rigid submerged mount at a documented depth',state:'Deployment candidate · calibration required',validation:'Exact 0–2 mH₂O vented-gauge configuration and continuous seawater suitability require supplier confirmation and tests.',prefix:'WATER_PRESSURE_SENSOR_ASSEMBLY',path:'Pressure processing at the Bay Station'},
  {id:'wind',name:'Wind speed & direction',part:'SparkFun SEN-15901 prototype',purpose:'Observes local wind speed and direction as environmental context.',data:'Speed pulses and vane direction',location:'Top sensor array',state:'Prototype selection · validation pending',validation:'Reference comparison, vane alignment, low-speed startup and marine durability tests pending. Not a guaranteed AI input.',prefix:'WIND_SPEED_DIRECTION_SENSOR',path:'ESP32 → LoRa → supporting observations'},
  {id:'gps',name:'GPS & position',part:'Adafruit Ultimate GPS PID 746 prototype',purpose:'Provides position, time support and geofence context.',data:'Position and quality information',location:'Top GNSS antenna area',state:'Supporting telemetry · validation pending',validation:'GPS scatter is not proof of theft. Require fix-quality checks, persistence and maintenance state.',prefix:'GNSS_GPS_ANTENNA',path:'ESP32 security → event logs'},
  {id:'esp32',name:'ESP32 controller',part:'ESP32 DevKit',purpose:'Acquires, timestamps, checks and frames sensor records.',data:'Station ID, packet ID, timestamp, schema and quality flags',location:'Electronics pod envelope in supplied CAD',state:'Firmware prototype · integration pending',validation:'Authentication, buffering capacity, watchdog and retransmission require implementation/recovery tests.',prefix:'ESP32_CONTROLLER_ENVELOPE',path:'Sensors → ESP32 → LoRa. No main AI or dashboard onboard.'},
  {id:'lora',name:'LoRa telemetry',part:'Radio and antenna model TBD',purpose:'Transmits compact sensor packets to the shore receiver.',data:'Primary buoy-to-shore telemetry',location:'Final radio and antenna allocation pending',state:'Hardware selection pending',validation:'Legal band, protocol, antenna and site coverage survey pending. Legacy LTE/Wi‑Fi CAD antenna names are not proof of LoRa installation.',prefix:'',path:'Buoy radio → shore receiver, not directly to cloud'},
  {id:'solar',name:'Solar power',part:'Two 30 W panels · planning reference',purpose:'Harvests energy through charge/power management.',data:'Solar voltage/current from one INA260 channel',location:'Opposite sides of the supplied mast/truss',state:'Planning values · not measured',validation:'Preserved original CAD orientation. Verify exact panel, regulator, mounting and measured charging behavior.',prefix:'DUAL_30W_SOLAR_ARRAY',path:'Sun → controller → battery → buoy electronics'},
  {id:'battery',name:'Battery & power monitoring',part:'12.8 V, 20 Ah planning example',purpose:'Stores energy for buoy sensing and radio operation.',data:'Battery voltage/current via second INA260 channel',location:'Battery envelope in supplied electronics layout',state:'Capacity example · not yet measured',validation:'Actual placement, battery/BMS, peak load, endurance and protection need approval. Shore computer power is separate.',prefix:'LIFEPO4_BATTERY_12V_ENVELOPE',path:'Battery → ESP32 + sensors + LoRa'},
  {id:'tamper',name:'Security & enclosure health',part:'Tamper input, enclosure switch and local buzzer',purpose:'Distinguishes persistent abnormal access from normal motion; monitors enclosure health.',data:'SECURE / WARNING / ALERT / DISARMED',location:'Enclosure; exact sensor installation pending',state:'Design requirement · validation pending',validation:'No guessed switch position: select final parts, debounce and persistence rules. Enclosure temperature is supporting health, not water temperature.',prefix:'REV5_RECTANGULAR_MARINE_ELECTRONICS_POD',path:'Local alarm → packet → Bay Station alert log'},
];
export const stages=[
 ['Sun charges buoy','Solar energy passes through power management into the battery. These are planned operating relationships, not an endurance result.'],
 ['Sensors activate','Pressure and wind are primary observations; GPS, power and security provide context.'],
 ['Pressure waveform','The animation uses illustrative samples, not calibrated underwater measurements.'],
 ['Wind observation','Speed and direction are contextual telemetry, not automatically AI features.'],
 ['ESP32 acquisition','Acquire, timestamp, validate and assign quality flags.'],
 ['Telemetry packet','Attach station ID, sequence, original time, schema version and source.'],
 ['LoRa to shore','A packet travels from the buoy transmitter to the shore receiver. No Internet cloud in this link.'],
 ['Bay Station receives','The receiver passes the packet to the shore computer. Final hardware/interface TBD.'],
 ['SQLite record','Authenticate, validate and reject duplicates before retaining original data.'],
 ['Pressure processing','Remove the slow component, filter, correct depth response and calibrate. Method parameters remain open.'],
 ['Estimated Hs','Compute the selected wave statistic over a defined observation window. Hs is the recommended target.'],
 ['Historical sequence','Prepare a quality-controlled time series and evaluate against non-AI baselines.'],
 ['Ten-minute prediction','A future estimate is produced on shore. This demonstration is not a trained field model.'],
 ['Dashboard update','Present estimated and predicted values separately, with source and freshness labels.'],
 ['Security status','Apply GPS quality, persistence and maintenance state before an alert decision.'],
 ['Operator guidance','The rule-based assistant explains the state. It does not control equipment or issue official warnings.'],
];
export const pipeline=['Underwater pressure','Raw signal','Quality check','Remove static / slow component','Filter band','Depth / frequency correction','Calibration','Wave statistic','Estimated Hs'];
export const scenarios={
 normal:{title:'Normal path',message:'Illustrative telemetry is received and displayed locally. All values remain SIMULATED.',lora:true,internet:true,pressure:true,ai:true,security:'SECURE'},
 pressure:{title:'P-01 · Pressure disconnected',message:'Wave estimate and prediction withheld. Invalid pressure is not replaced with zero. Fault logged.',lora:true,internet:true,pressure:false,ai:false,security:'SECURE'},
 lora:{title:'C-01 · LoRa outage',message:'ESP32 keeps sensing and queues packets with original timestamps. Bay Station values become STALE; no fresh forecast.',lora:false,internet:true,pressure:true,ai:false,security:'SECURE'},
 internet:{title:'I-01 · Internet outage',message:'LoRa reception, local SQLite, processing, AI, dashboard and alerts continue. Cloud sync is queued; remote access is OFFLINE.',lora:true,internet:false,pressure:true,ai:true,security:'SECURE'},
 gps:{title:'G-01 · GPS scatter',message:'WARNING → quality and persistence check → SECURE if the deviation does not persist. No immediate theft alert.',lora:true,internet:true,pressure:true,ai:true,security:'WARNING'},
 tamper:{title:'T-01 · Armed enclosure opening',message:'Persistent opening → ALERT → local buzzer → Bay Station event log. Debounce timing must be validated.',lora:true,internet:true,pressure:true,ai:true,security:'ALERT'},
 ai:{title:'A-01 · AI unavailable',message:'Prediction UNAVAILABLE. Pressure/wind monitoring, SQLite and local dashboard continue.',lora:true,internet:true,pressure:true,ai:false,security:'SECURE'},
 battery:{title:'B-01 · Reduced sunlight',message:'Power warning → defined safe-operating policy → recovery logging. Final limits require measured energy tests.',lora:true,internet:true,pressure:true,ai:true,security:'SECURE'},
 restart:{title:'R-01 · Bay Station restart',message:'Local services temporarily OFFLINE. Design expectation: restart services, retain SQLite records and reconcile buffered packets.',lora:false,internet:false,pressure:true,ai:false,security:'UNAVAILABLE'},
 maintenance:{title:'Maintenance mode',message:'Authorized maintenance is DISARMED, not ALERT. Log entry/exit and restore protection when servicing ends.',lora:true,internet:true,pressure:true,ai:true,security:'DISARMED'},
};
export type Scenario=keyof typeof scenarios;
export const validation=[
 ['Pressure / wave','MAE, RMSE, bias, repeatability, reference comparison and gaps','Defined wave statistic and accepted reference performance'],
 ['Wind','Reference error, direction, low-speed startup, repeatability','Approved acceptance limits met'],
 ['LoRa / backhaul','Packet delivery, latency, range, reconnect, duplicates, backlog recovery','Site-tested path and outage recovery'],
 ['Power','Average and peak W, Wh/day, autonomy, reduced-sun recovery','Measured margin meets deployment target'],
 ['Security','True/false alerts, delay and GPS scatter','Acceptable false-alert behavior'],
 ['Dashboard','Task completion, errors, time, comprehension, readability','Adviser-approved usability threshold'],
 ['AI','MAE, RMSE, bias, persistence skill, inference time, size, availability, error by sea condition','Untouched chronological test evaluation'],
 ['Mechanical','Stability, ingress, corrosion control, retrieval','No unresolved critical safety issue'],
];
export const milestones=[
 ['M1','Scope freeze','Signed architecture, site/use case, wave statistic and AI target','Adviser approval record'],
 ['M2','Component freeze','Exact BOM, datasheets, pinout, LoRa and Bay Station selection','Selection register complete'],
 ['M3','Bench integration','Calibrated sensors and packet path','Bench logs and acceptance sheets'],
 ['M4','Controlled water test','Wave reference, wind, security and power dataset','Synchronized traceable records'],
 ['M5','Software evaluation','Usability and AI baseline/model results','Metrics and held-out evaluation'],
 ['M6','Final revision','Thesis, presentation, BOM, diagrams, dataset and limitations','Adviser-approved release'],
];
