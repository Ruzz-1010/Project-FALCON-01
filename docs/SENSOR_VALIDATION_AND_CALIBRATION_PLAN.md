# Project FALCON Sensor Validation and Calibration Test Plan

Revision: 1.0  
Date: 2026-08-31  
Status: pre-hardware validation protocol; acceptance limits are Phase 1 engineering targets pending adviser approval and physical test evidence

## 1. Purpose

This plan defines how Project FALCON sensors, security inputs, telemetry, pressure-derived wave estimates, and system behavior will be tested before deployment. It converts the component decisions in [SENSOR_SELECTION_BASELINE.md](SENSOR_SELECTION_BASELINE.md) into repeatable procedures, recording sheets, and pass/fail gates.

A successful software build, simulated dashboard, schematic, PCB render, or single sensor reading is not calibration evidence. Only dated tests using identified hardware, recorded raw data, known references, and stated acceptance criteria may be reported as validation.

## 2. Test principles

1. Preserve raw readings; never retain only rounded dashboard values.
2. Record the firmware commit, algorithm version, hardware revision, sensor serial/SKU, operator, location, date, sample rate, units, environment, and reference instrument.
3. Calibrate using one data set and verify using a separate repeated data set.
4. Report error, repeatability, missing samples, spikes, drift, and recovery—not only average values.
5. Do not change coefficients solely to make a graph appear smoother.
6. Mark simulated, bench, controlled-water, shore, and field data distinctly.
7. Treat all numeric limits below as proposed Phase 1 acceptance targets until the adviser approves them and reference-equipment capability is confirmed.

## 3. Readiness levels

| Level | Meaning | Required evidence |
| --- | --- | --- |
| L0 — Documentation | Exact part and intended interface recorded | Datasheet, pinout, limitation and test plan |
| L1 — Bench detected | Device communicates and faults are observable | Identity/address scan, raw data, disconnect/reconnect test |
| L2 — Reference checked | Reading compared against a suitable reference | Calibration sheet, repeated points, error calculation |
| L3 — Integrated | Device works with the full ESP32 and telemetry stack | Concurrent-sensor log, power and recovery evidence |
| L4 — Controlled environment | Installed assembly survives representative controlled tests | Leak, thermal, motion, network and endurance reports |
| L5 — Supervised field trial | System operates at the intended site under supervision | Field log, reference comparison, alarms, maintenance and incident record |

No component may be described as deployment-validated below L5.

## 4. Required equipment

| Equipment | Minimum use | Requirement |
| --- | --- | --- |
| Digital multimeter | Voltage, continuity and current reference | Recently checked against a known source; record model and last calibration/check date |
| Adjustable DC supply with current limit | Controlled power and brownout tests | Suitable voltage/current range; current limit verified before connection |
| Electronic load or characterized resistive loads | INA260 and power-rail tests | Cover idle, normal and near-maximum expected load without exceeding ratings |
| Reference thermometer | Water/enclosure temperature comparison | Stated accuracy should be better than the project target; record certificate or specification |
| Water container and depth scale | Static pressure/depth test | Rigid scale, stable sensor position, temperature recorded, no trapped air |
| Reference pressure instrument, if available | Pressure comparison | Known range and uncertainty; otherwise report the water-column method and its limits |
| Reference anemometer and compass | Wind comparison/alignment | Known resolution/accuracy; tests performed in steady conditions |
| GPS-capable reference or surveyed point | GPS scatter/context | Record its uncertainty; do not assume phone GPS is a precision reference |
| Oscilloscope or logic analyzer | Bus, pulse and UART diagnostics | Recommended for noise, timing, pulse bounce and logic-level verification |
| Stopwatch/time source | latency, sampling and outage timing | Time synchronized with data logger when possible |
| Scale and measuring tools | enclosure/prototype inspection | Caliper/tape appropriate to required resolution |
| Leak-test materials | bulkhead and enclosure checks | Dry indicators or absorbent witness material; safe test setup |

## 5. Common pre-test checklist

- [ ] Test ID and objective assigned.
- [ ] Approved schematic/pinout and hardware revision identified.
- [ ] Sensor SKU/revision/serial or unique asset ID recorded.
- [ ] Reference instrument and its accuracy recorded.
- [ ] Connectors, polarity, logic voltage, pull-ups, fuses and current limit checked.
- [ ] Raw logging enabled with timestamps, validity flags and units.
- [ ] Dashboard values clearly marked `LIVE`, `SIMULATED`, `STALE`, `INVALID`, or `OFFLINE`.
- [ ] Safe stopping condition and maximum rating defined.
- [ ] Photos of setup and installation captured.
- [ ] Operator and witness identified.

## 6. Pressure sensor and wave-height validation

### 6.1 Bar02 R2 identification and interface test

1. Photograph both sides, cable, connector, sensing gel and package label.
2. Verify supply and I2C logic levels before connecting.
3. Run an I2C scan and record the detected address; do not assume `0x76` without evidence.
4. Log at least 10 minutes in stable air and report mean, standard deviation, range, invalid samples and resets.
5. Disconnect and reconnect the sensor while logging. The system must report a fault/stale state rather than continue displaying an apparently live value.

**Proposed pass:** correct identification; no overvoltage; at least 99% valid samples during the stable bench run; disconnection detected within two normal reporting intervals; automatic or documented manual recovery succeeds.

### 6.2 Static water-column comparison

Use at least five increasing depths and then repeat them in decreasing order. Suggested points are 0, 0.10, 0.25, 0.50 and 1.00 m if the tank and sensor range safely allow them.

1. Measure from a fixed datum to the sensing face.
2. Remove trapped bubbles and keep the sensor orientation consistent.
3. Allow the water and sensor to stabilize at each point.
4. Log at least 60 seconds per point, including raw pressure and sensor temperature.
5. Calculate reference gauge pressure using `P = rho × g × h`, documenting assumed/measured water density, gravitational acceleration and depth uncertainty.
6. Fit offset/scale only from the calibration run.
7. Repeat the sequence as an independent verification run without changing coefficients.
8. Report residual error, hysteresis between increasing/decreasing depth, repeatability and uncertainty.

**Proposed pass target:** verification error no greater than the larger of ±1.0 kPa or ±2% of reference over the tested range; repeat-point spread no greater than 1.0 kPa; no unexplained discontinuity. This is a project target, not a manufacturer guarantee, and may be tightened only after reference capability is established.

### 6.3 Dynamic pressure-to-wave scenario test

Perform controlled oscillation tests before any open-water claim. Use a wave tank, vertically driven sensor fixture, or buoy-in-tank arrangement with independently recorded displacement/video scale.

| Scenario | Controlled condition | Evidence required |
| --- | --- | --- |
| Still water | No intentional movement for 10 min | Baseline stability, false-wave output and noise |
| Small regular motion | Known approximately sinusoidal vertical motion | Raw pressure and reference displacement synchronized in time |
| Medium regular motion | Larger safe amplitude at two periods | Estimated height, period and phase behavior |
| Irregular motion | Mixed amplitudes/periods | Robustness, spikes and quality flags |
| Sudden handling | Lift, impact or cable movement | Invalid/tamper classification; must not be treated as a normal wave |
| Sensor blocked/bubbled | Temporarily obstructed or trapped air under supervision | Fault/quality response and recovery |

Use a predeclared processing window and algorithm version. Compare estimated wave height with reference peak-to-trough displacement for each independent trial.

**Proposed controlled-test pass:** median absolute wave-height error ≤0.10 m or ≤15% of reference, whichever is larger; period error ≤10% for regular tests; ≥95% of valid windows produce a result; disturbed/blocked scenarios are flagged rather than silently accepted. Final field acceptance must be based on adviser-approved comparison with a suitable reference instrument.

### 6.4 Bar02 deployment limitation gate

The Bar02 rear electronics must stay dry, and its gel sensor must receive the manufacturer-required daily drying interval. Before a long-duration deployment, the team must document either:

- a retrieval/service schedule that gives at least two hours of drying every day; or
- a different continuously submersible pressure sensor approved through the same validation process.

Failure to close this gate blocks an unattended long-duration deployment claim.

## 7. Supporting telemetry boundary

Water temperature and other environmental sensors are excluded from the Phase 1
measurement claim. GPS, battery/solar readings, timestamps, and optional security
inputs are supporting telemetry only. Validate them for availability, stale-state
handling, power impact, and security behavior as needed for system operation; do
not report them as additional environmental research outputs.

## 8. Wind validation

### 8.1 Wind speed

1. Mount the anemometer in unobstructed flow beside the reference instrument.
2. Verify zero-speed behavior and manually confirm each reed closure.
3. Collect at least five steady speed levels covering the realistic range, with three repeated runs per level.
4. Record pulse count, time window, calculated speed, reference speed, direction, turbulence and mounting geometry.
5. Inspect cable movement, bounce, low-speed startup and recovery after stopping.

**Proposed pass:** no pulses while stationary for 10 minutes; no missed/duplicate closures during slow manual rotation; mean error ≤max(1.0 km/h, 10% of reference) over the validated range.

### 8.2 Wind direction

1. Mechanically mark the vane reference and align it using a compass correction documented for the site.
2. Test all supported direction positions in increasing and decreasing rotation.
3. Record ADC voltage/code, classified direction, reference angle and boundary behavior.
4. Repeat while other I2C/ADC sensors and the cellular modem operate.

**Proposed pass:** all eight principal directions classified correctly during repeated tests; no adjacent-code oscillation after the defined debounce/filter interval when the vane is held still. Sixteen-position reporting may be used only if the physical unit demonstrates it reliably.

## 9. GPS and geofence validation

### 9.1 Receiver tests

- Cold start in open sky: five trials.
- Warm start: five trials.
- Stationary logging: at least 60 minutes at the intended antenna location.
- Partial-obstruction trial: representative tower/enclosure installation.
- Antenna disconnect/reconnect and receiver restart.

Record time to first valid fix, satellites, fix quality, latitude/longitude, invalid samples and recovery time.

### 9.2 Geofence design

Calculate distance of every stationary fix from the test-location median or surveyed reference. Set the geofence radius only after measuring the 95th and 99th percentile stationary errors. The alarm must also use persistence rather than a single outlying fix.

**Proposed pass:** ≥95% valid fixes during the open-sky stationary run after acquisition; no geofence alarm during the full stationary test; movement beyond the configured radius plus uncertainty margin generates an alarm only after the approved persistence interval; loss of GPS generates a distinct `GPS unavailable` status, not a false movement alarm.

## 10. Battery and solar INA260 validation

For each INA260 channel, test at zero/idle, normal and near-maximum expected current without exceeding the breakout, wiring, connector, source or load ratings.

1. Confirm address and current direction.
2. Measure bus voltage with the reference DMM and current with a suitable reference method.
3. Log at least 30 paired samples at each level.
4. Repeat after 15 minutes at the highest normal continuous load.
5. Record connector and board temperature where practical.
6. Test open-circuit, reverse/invalid measurement state where safe, restart and address conflict.

**Proposed pass:** voltage error ≤max(0.10 V, 2%); current error ≤max(0.10 A, 3%) across the validated project range; correct sign/direction; no unsafe heating, reset or address loss. These system-level limits include wiring and reference uncertainty and do not replace manufacturer ratings.

## 11. Security-input validation

### 11.1 Enclosure contact

Test closed, opening, partially aligned, cable disconnected, contact bounce, ESP32 restart, and repeated open/close cycles.

**Proposed pass:** stable correct state; deliberate opening detected within 2 seconds; no false opening during 30 minutes of representative vibration; cable fault produces a detectable fault/open state when fail-safe wiring is used.

### 11.2 Optional LIS3DH tamper input

If approved, first record ordinary motion profiles during controlled buoy oscillation. Then separately record deliberate tilt, impact, lifting and sustained movement. Select thresholds from held-out trials, not from the same samples used to tune them.

**Proposed pass:** 100% of defined deliberate tamper trials detected within the approved persistence period and no more than one false tamper alarm in a 24-hour supervised representative-motion test. If this cannot be achieved, omit the accelerometer from Phase 1 security.

### 11.3 Buzzer

Test only after an exact buzzer and driver are approved. Verify GPIO isolation, driver temperature, supply dip, duty cycle, sound level at a documented distance, alarm cancellation, and nuisance behavior.

## 12. LoRa telemetry and buffering

The LoRa buoy-to-barangay-hall path must pass:

- regional band, gateway placement, antenna and line-of-sight verification at the intended site;
- idle, receive and transmit current measurements for the buoy radio and gateway;
- 30 forced LoRa-loss/reconnect cycles;
- packet delivery observation at representative distances and obstructions;
- packet duplication, ordering and timestamp checks;
- local buffering during at least a 30-minute outage;
- ordered upload after reconnection without losing the original sample time;
- a continuous 24-hour bench soak, followed by a supervised 72-hour integrated trial.

**Proposed pass:** no ESP32 or modem brownout; ≥99% of generated test records eventually received after planned outages; no duplicate record accepted by the database; reconnect succeeds in at least 29 of 30 automated cycles, with the remaining cycle recoverable by the documented watchdog procedure.

### 12.1 SIM/4G/5G Bay Station Internet backhaul

Install the selected SIM/4G/5G modem/router at the barangay-hall Bay Station. Record
provider, signal/availability, data plan, antenna placement, registration time,
backhaul latency, data usage, firewall/TLS controls, cloud endpoint, and remote-access
permissions. Test cloud synchronization and remote access during ordinary service,
weak signal, modem restart, and Internet outage. SIM/4G/5G is the Bay Station Internet
backhaul, not the buoy telemetry path.

**Proposed pass:** LoRa delivers telemetry to the verified barangay-hall gateway;
the Bay Station uploads and exposes authorized remote data over its SIM/4G/5G
backhaul; the buoy buffers records if LoRa fails and the Bay Station queues cloud
uploads if Internet fails. The test must report packet loss, latency, duplicate
handling, gateway/modem restart recovery, and timestamp preservation.

## 13. Integrated system scenarios

| ID | Scenario | Expected behavior |
| --- | --- | --- |
| SYS-01 | Normal calm operation | Valid pressure estimate, wind, GPS, temperature and power records; no alarm |
| SYS-02 | Moderate controlled wave motion | Pressure-derived estimate changes smoothly; raw data retained; condition threshold works |
| SYS-03 | Rough/out-of-range controlled input | Warning shown; values remain labeled with quality/validity; no fabricated data |
| SYS-04 | Pressure sensor disconnected | Wave estimate becomes unavailable/stale; other sensors remain operational |
| SYS-05 | GPS fix lost | `GPS unavailable`; no false geofence movement alarm |
| SYS-06 | Enclosure opened | Security event timestamped and delivered/buffered; other acquisition continues |
| SYS-07 | LoRa outage | Samples buffered locally with original timestamps; Bay Station dashboard indicates delayed/offline data |
| SYS-08 | LoRa recovery | Buffered records uploaded to the Bay Station once, in traceable order; live reporting resumes |
| SYS-09 | Battery low / solar absent | Warning thresholds operate; no immediate corrupt shutdown; event recorded |
| SYS-10 | Sensor returns invalid/spike | Invalid value rejected or flagged; graph does not imply a verified extreme wave |
| SYS-11 | ESP32 restart | Reset reason recorded; sensors reinitialize; no duplicate identity/time corruption |
| SYS-12 | Bay Station unavailable | Buoy continues safe acquisition/buffering; recovers when service returns |
| SYS-13 | Bay Station Internet outage | Local ingestion/storage/dashboard continue; cloud upload and remote access queue or show unavailable |
| SYS-14 | Bay Station Internet recovery | Queued cloud records synchronize once and authorized remote access resumes |

## 14. AI wave-prediction validation

The required AI feature predicts future estimated wave height at the Bay Station. It must be evaluated separately from the physical pressure-to-wave conversion.

1. Freeze the input schema, sampling interval, prediction horizon and model version.
2. Split data chronologically into training, validation and held-out test periods to prevent future-data leakage.
3. Compare the model with a persistence baseline that predicts the latest valid wave height.
4. Report MAE, RMSE, bias, sample count, missing-data behavior and performance by calm/moderate/rough condition.
5. Evaluate sensor outage, delayed telemetry, spikes and values outside the training range.
6. Display prediction as a separate labeled series and never substitute it for the current measured/estimated series.

**Release target:** the AI must improve held-out MAE over the persistence baseline by an adviser-approved margin; until a margin is approved, report both results without claiming superiority. If inputs are stale or invalid, prediction must be unavailable or clearly low-confidence—not fabricated.

## 15. Endurance, environmental and usability gates

- 24-hour full bench soak with all sensors and telemetry active.
- Supervised 72-hour integrated trial before longer field work.
- Enclosure leak test before installing powered electronics.
- Thermal test at expected solar and modem load.
- Connector/cable strain and repeated service-cycle inspection.
- Salt-exposure/corrosion inspection appropriate to prototype materials.
- Dashboard test with intended older/non-technical operators: task completion, label comprehension, text visibility, alarm recognition and number of clicks.

**Proposed usability pass:** at least five representative users can identify current wave estimate, wind, GPS status, battery condition and active alerts without assistance; ≥80% complete each task correctly on the first attempt; all critical text remains readable at the target display and browser zoom.

## 16. Test record template

| Field | Entry |
| --- | --- |
| Test ID / procedure revision |  |
| Date, start/end time and location |  |
| Operator / witness |  |
| Git commit / firmware / algorithm version |  |
| Hardware and PCB revision |  |
| Sensor manufacturer, SKU, revision, serial/asset ID |  |
| Reference instrument, serial and stated uncertainty |  |
| Supply voltage/current limit |  |
| Environmental conditions |  |
| Sample rate / duration / units |  |
| Raw-data filename and checksum |  |
| Calibration coefficients/configuration |  |
| Acceptance criteria |  |
| Result and calculated error |  |
| Pass / Fail / Blocked |  |
| Deviations, anomalies and corrective action |  |
| Operator and reviewer signatures |  |

### Measurement table

| Timestamp | Test point/reference | Raw sensor value | Corrected value | Error | Validity/quality | Notes |
| --- | ---: | ---: | ---: | ---: | --- | --- |
|  |  |  |  |  |  |  |

## 17. Final deployment release checklist

- [ ] Every required sensor reached at least L4 and has an approved L5 field-trial plan.
- [ ] No excluded environmental sensor is included in the Phase 1 procurement or validation release.
- [ ] Bar02 drying/service limitation closed or sensor replaced.
- [ ] Pressure-to-wave method independently validated and labeled as an estimate.
- [ ] GPS geofence based on measured site scatter and persistence.
- [ ] Wind calibration and marine maintenance interval recorded.
- [ ] INA260 current paths, ranges and thermal behavior verified.
- [ ] Security false-alarm evidence accepted.
- [ ] LTE coverage, peak power, reconnect and buffering accepted.
- [ ] Power budget, autonomy and solar recovery verified using measured loads.
- [ ] Enclosure ingress, thermal, strain-relief and corrosion checks passed.
- [ ] Dashboard usability tested with representative users.
- [ ] AI held-out evaluation and failure behavior documented.
- [ ] All failures have closure evidence and reviewer approval.

## 18. Approval

| Role | Name | Signature | Date | Decision |
| --- | --- | --- | --- | --- |
| Student researcher |  |  |  |  |
| Hardware reviewer |  |  |  |  |
| Software/AI reviewer |  |  |  |  |
| Thesis adviser |  |  |  | Approve / Revise / Reject |

## 19. Related documents

- [SENSOR_SELECTION_BASELINE.md](SENSOR_SELECTION_BASELINE.md)
- [HARDWARE.md](HARDWARE.md)
- [HARDWARE_BOM.md](HARDWARE_BOM.md)
- [PINOUT.md](PINOUT.md)
- [TEST_PLAN.md](TEST_PLAN.md)
- [CALIBRATION_GUIDE.md](CALIBRATION_GUIDE.md)
- [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md)

