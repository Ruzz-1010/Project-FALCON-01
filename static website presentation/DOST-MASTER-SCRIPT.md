# FALCON-01 — DOST Presentation Master Script
**15 pages · present.html is the master · ~15 minutes + 5 min Q&A**
**Project FALCON-01 · Phase 1 Undergraduate Prototype · Fullbright College · 5 October 2026**

How to run it:
- Open `present.html` (not `index.html`) on the projector.
- Projector weak / bright room: open `present.html?big=1`.
- Keys: `Space / →` next · `←` back · `L` chapter list · `P` presenter mode · `Esc` exit inspection.
- All readings are SIMULATED. Say that out loud at least twice.

Team to name-drop once (ch.12, then close):
- Jhon Ruzzel Correa — Hardware + Power + LoRa firmware
- Mayla Bacaltos + Gina Caballero — Thesis papers (hati)
- Gwyn Isabel Enriquez — Edge + AI + Dashboard
- Sir Jam (papers) · Sir Jeff (hardware) · 3rd mentor TBD (SW/AI or DOST counterpart)

The one-sentence thesis: *"Affordable, documented, locally-evaluable coastal observation — integration and evaluation, not sensor invention."*

---

## 00 — THE OCEAN (1 min)
**On screen:** Hero + problem +Begin the journey.
**Say:**
> "Good morning. We are Project FALCON-01 from Fullbright College. Barangays need affordable wave and wind data. Commercial buoys are costly, proprietary, and maintenance-heavy. Phase 1 answers with a local-first, transparent, evaluable prototype — one sensing buoy at sea, one Bay Station on shore."
**Click:** `Begin the journey ↓`.
**Plain words if asked:** "Buoy = floating sensor platform. Heavy processing happens on shore, not at sea."

## 01 — OBJECTIVES (1 min)
**On screen:** Six objectives.
**Say:**
> "Phase 1 is integration and evaluation, not invention. One: serviceable solar buoy with passive mooring. Two: pressure + wind with supporting telemetry. Three: pressure-derived wave estimate with explicit calibration. Four: LoRa to shore for storage and dashboard. Five: evaluate accuracy, reliability, latency, power, usability. Six: short-term AI prediction versus a baseline — and we check numbers before we believe them."
**Do not claim:** any accuracy number here.

## 02 — FALCON BUOY (1.5 min, interactive)
**On screen:** 3D buoy + component picks.
**Say:**
> "This is FALCON-01. Buoy: ESP32, underwater pressure, wind speed + direction, GPS for position/time/geofence, battery + solar, LoRa. Shore: Bay Station mini PC. No mini PC, no cellular on the buoy."
**Demo:** Click one component pick (e.g. pressure) → inspection panel opens → `← Back to buoy`.
**Note on CAD:** "Legacy antenna names and an Orange Pi envelope remain in the supplied geometry — not V4.1 equipment. Mechanical revision pending."

## 03 — SENSORS (1 min)
**On screen:** Sensor menu + acquisition dock.
**Say:**
> "Two primaries: pressure for waves, wind speed/direction. Supporting: GPS, power, timestamps, security. Water temperature and salinity are out of Phase 1 scope — deliberate, to keep the build evaluable."
**Demo:** Click pressure → wind in the sensor menu. Read the one-line detail aloud.

## 04 — ESP32 SOFTWARE (1 min)
**On screen:** ESP32 chip diagram + telemetry frame.
**Say:**
> "The ESP32 reads sensors, stamps time, validates values, packs one clean FALCON-01 frame with quality flags — every 4.8-second cycle. Four inputs in parallel, one frame out to LoRa."
**Plain words:** "Small controller reads over and over, packs readings into one envelope."

## 05 — LORA LINK (1.5 min, interactive — the crowd pleaser)
**On screen:** OBSERVE → PACKAGE → LoRa TX → LoRa RX → SHORE + 6-step strip.
**Say:**
> "Buoy ESP32 → LoRa → Bay Station. SIM/4G/5G backhaul lives at the Bay Station only. Six steps: Sense, Frame, Cross, Buffer, Shore RX, Insight."
**Demo:** Click `Interrupt LoRa` → show BUOY BUFFER counting, SHORE STALE → click `Restore LoRa` → replay with original timestamps, duplicate IDs rejected.
**Say the limit:** "Hardware, legal band, and site coverage pending. No range guarantee."

## 06 — BAY STATION (1.5 min, interactive)
**On screen:** Shore pipeline LoRa RX → VALIDATE → STORE → PROCESS → AI → DISPLAY.
**Say:**
> "One shared shore computer does everything: LoRa receive, validate, SQLite store, processing, AI, dashboard. Internet stays on shore."
**Demo:** `Inspect the Bay Station` → click 2 stages (e.g. LoRa receiver → AI prediction) → `← Exit inspection`.
**States to name:** LIVE / SIMULATED / ESTIMATED on the grouped telemetry endpoint.

## 07 — WAVE ESTIMATE (1 min)
**On screen:** RAW PRESSURE → PROCESSED → ESTIMATE Hs + depth section.
**Say:**
> "Pressure in, estimated wave height out. Quality check, filter, baseline removal, depth response, calibration → estimated Hs. Depth matters — the sensor sits below the waterline."
**Say the limit:** "Illustrative only. Depth correction, calibration, and reference comparison are not done. No metres claim — relative units only."

## 08 — AI PREDICTION (1 min, interactive)
**On screen:** History + AI vs persistence + Run prediction.
**Say:**
> "Target: 5, 10, 15 minutes ahead. Today it's a transparent trend baseline, not a trained model. Evaluation needs calibrated data, chronological train/val/test split, MAE/RMSE/bias."
**Demo:** `Run prediction` → cyan AI trace extends vs dotted persistence.
**Say:** "Accuracy and skill remain unvalidated."

## 09 — DASHBOARD (1 min)
**On screen:** 4 tabs — Overview, Buoy Motion, Sensors, Logs & Alerts.
**Say:**
> "Four pages: Overview, Buoy Motion, Sensors, Logs & Alerts. Security states SECURE / WARNING / ALERT / DISARMED. Normal wave motion must not raise an alert — false-positive testing is required before any alarm claim."
**Demo:** Click Overview → Motion → Logs. Point at `SIMULATED PREVIEW`.

## 10 — VALIDATION & STATUS (1 min — honesty chapter)
**Say:**
> "Nothing here is claimed as validated. Bench sensor tests, pressure-to-wave vs reference, wind vs reference anemometer, GPS geofence, vibration/tamper, power budget — plus LoRa loss/latency/range/buffering, dashboard usability, AI vs baseline. Implemented means the software path runs. It does not mean the measurement is accurate."
**Implemented:** firmware shell, captive portal, framing, Bay service prototype (simulator, SQLite, REST, dashboard), wave-estimate sim, geofence sim.
**Not yet:** final sensor models + cal coeffs, real GPS/tamper, LoRa hardware + range, field-trained AI.

## 11 — SCOPE & RISKS (45 sec — safety chapter)
**Say:**
> "What it does not do: no tsunami prediction, no typhoon prediction, no official warnings, no navigation control, no lab-grade water quality. Not a replacement for government monitoring."
**Risks → mitigations:** Power → measured budget. Waterproofing → bench + staged deployment. LoRa range → documented range test first. Calibration drift → routine + reference. False alerts → false-positive testing.

## 12 — ROADMAP & TEAM (1.5 min — the ask setup)
**On screen:** 5-gate rail + team grid. Click each gate.
**Say:**
> "Funding is for a sequenced 5-month / 20-week bootcamp build, not a parts order. Gate 04 is the accuracy gate — no accuracy figure leaves it."
- **G1 Freeze+procure (M1):** frozen BOM, permits. "Procurement is not evidence."
- **G2 Bench (M2):** one sensor at a time, rails + protection.
- **G3 Calibrate+software (M3):** coeffs, API/SQLite, LoRa gateway + SIM + outage recovery.
- **G4 Controlled validation (M4):** tank/pool vs reference, MAE/RMSE/bias, 24h power + 72h solar.
- **G5 Coastal trial + thesis (M5):** supervised pilot, AI vs persistence on held-out, report.
**Team:** read the 4 names + 2 advisers + "3rd TBD — SW/AI or DOST counterpart."
**Bootcamp:** "Dorm, half-OJT half-thesis, DOST as OJT host. AM OJT, PM thesis, Sat build, Sun docs. 4 months is the stretch goal."

## 13 — IMPACT & FUNDING (1.5 min — the number)
**Say:**
> "First pilot serves one verified user before expansion. LGUs, fisherfolk, schools/researchers, ports/tourism — each with something still to confirm. No site or beneficiary confirmed yet."
**Innovation line (say verbatim):** "Affordable, documented integration and local evaluation of established sensing, LoRa, shore processing, solar, security, and transparent prediction — not a new sensor, buoy, or AI algorithm."
**Budget — planning range only, not a quotation:**
> "₱90,000 to ₱150,000. Midpoint ~₱115,000 covers import markup, one calibration trial, spares. ₱90k minimum-viable, ₱150k comfortable with contingency. Replaced with 3-supplier canvass before submission."
**7 lines (filter live):** Sensors/embedded 18–26k · Bay+LoRa+SIM 15–25k · Solar/battery/MPPT 14–22k · Hull/keel/enclosure 15–25k · Mooring 7–14k · Calibration/trials 12–20k · Transport/spares/contingency 9–18k.
**Delivers:** one integrated prototype, calibrated subsystems, dashboard + archive, coastal-test results, baseline-vs-model evaluation, reusable docs + datasets.

## 14 — CLOSE (30 sec)
**Say:**
> "Next: freeze BOM per redesign baseline, physical pressure acquisition + calibration routine, LoRa buoy + gateway integration, controlled reference data before any performance claim. We ask for procurement, fabrication, calibration access, supervised testing, and mentorship — the opportunity to generate local evidence, not acceptance of an untested forecast. Thank you — Project FALCON Research Group, BS IT, Fullbright College."
**Click:** `Experience it again ↗` if Q&A wants a revisit.

---

## Q&A CHEAT SHEET (5 min)
1. **"Accurate ba?"** — "Not yet. No accuracy claim until Gate 04 vs reference with MAE/RMSE/bias."
2. **"Bakit LoRa, hindi 4G sa buoy?"** — "Power + cost + offshore coverage. 4G backhaul stays at Bay Station."
3. **"Bakit hindi tsunami/typhoon warning?"** — "Out of scope by design. Not an official system, no such claim."
4. **"Saan ide-deploy?"** — "No site confirmed. One LGU + one need + one pilot site, verified first."
5. **"Bakit 90–150k?"** — "Landed cost with 20–30% markup, LoRa/mini-PC/SIM now included, plus trials + contingency. Mid 115k defensible."
6. **"Kaya ba 4–5 months?"** — "5 months credible if scope frozen, procurement week 1, parallel permits. 4 months stretch."
7. **"Invention niyo ba sensor/AI?"** — "No. Contribution is affordable integration + local evaluation + transparent methods."
8. **"Paano kung maputol LoRa?"** — "Buoy buffers with original timestamps, replays, rejects duplicates. Demoed live on page 05."

## PRESENTER CHECKLIST
- [ ] `present.html?big=1` tested on projector · phone QA done
- [ ] Interrupt-LoRa + Bay inspect + Run prediction clicked once before show
- [ ] 3rd mentor line updated in `story.js` if named
- [ ] Say "simulated, not validated" on pages 05, 07, 08, 10
- [ ] End on funding total ₱90,000–₱150,000 + the ask
