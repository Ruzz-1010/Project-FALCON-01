# FALCON-01 — DOST Presentation Master Script
**15 pages · present.html is the master · ~20 minutes + 5 min Q&A**
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

## Why 20 minutes, and how to protect it

| Block | Pages | Minutes |
|---|---|---|
| Open, problem, objectives | 00–01 | 3.0 |
| The system (buoy → shore) | 02–06 | 7.0 |
| Evidence and limits | 07–11 | 5.0 |
| Plan, money, the ask | 12–14 | 5.0 |
| **Total** | | **20.0** |

**CUT LIST — if the panel is running short, drop these three, in this order:**
1. **Page 04 (ESP32 software)** — skip the diagram; one sentence: *"A small controller reads the sensors, checks the values, and packs one frame every 4.8 seconds."*
2. **Page 07 (wave estimate)** — point at it only: *"Pressure in, estimated wave height out. Illustrative — relative units, not metres yet."*
3. **Page 09 (dashboard)** — do not click the tabs; say the four names and move on.

Never cut pages 05, 08, 10, 12 or 13. Those carry the demo, the honesty, the plan and the number.

---

## 00 — THE OCEAN (1.5 min — the hook)
**On screen:** Hero + problem + Begin the journey.
**Say:**
> "Every barangay on this coast makes decisions near water — where to fish, when to send a boat out, when to pull one in. Almost none of them have a single measured number about that water.
>
> Commercial wave buoys exist. They are expensive, closed, and heavy to maintain. So the default answer today is no data at all.
>
> That is the gap we are asking you to help close. We are Project FALCON-01 from Fullbright College. Phase 1 answers with a local-first, transparent, evaluable prototype — one sensing buoy at sea, one Bay Station on shore."
**Click:** `Begin the journey ↓`.
**Plain words if asked:** "Buoy = floating sensor platform. Heavy processing happens on shore, not at sea."

## 01 — OBJECTIVES (1.5 min)
**On screen:** Six objectives.
**Say:**
> "Phase 1 is integration and evaluation, not invention. One: serviceable solar buoy with passive mooring. Two: pressure + wind with supporting telemetry. Three: pressure-derived wave estimate with explicit calibration. Four: LoRa to shore for storage and dashboard. Five: evaluate accuracy, reliability, latency, power, usability. Six: short-term AI prediction versus a baseline — and we check numbers before we believe them.
>
> Say it plainly now, because it shapes everything after: we are not inventing a sensor, a buoy, or an AI algorithm. We are proving that established parts, put together affordably and documented honestly, can produce evidence a local user can actually trust."
**Do not claim:** any accuracy number here.

## 02 — FALCON BUOY (2 min, interactive)
**On screen:** 3D buoy + component picks.
**Say:**
> "This is FALCON-01. Buoy: ESP32, underwater pressure, wind speed + direction, GPS for position/time/geofence, battery + solar, LoRa. Shore: Bay Station mini PC. No mini PC, no cellular on the buoy — nothing at sea does heavy work.
>
> Every part here was chosen for one reason: a student can buy it, wire it, document it, and repair it."
**Demo:** Click one component pick (e.g. pressure) → inspection panel opens → `← Back to buoy`.
**Note on CAD:** "Legacy antenna names and an Orange Pi envelope remain in the supplied geometry — not V4.1 equipment. Mechanical revision pending."

## 03 — SENSORS (1 min)
**On screen:** Sensor menu + acquisition dock.
**Say:**
> "Two primaries: pressure for waves, wind speed/direction. Supporting: GPS, power, timestamps, security. Water temperature and salinity are out of Phase 1 scope — deliberate, to keep the build evaluable."
**Demo:** Click pressure → wind in the sensor menu. Read the one-line detail aloud.

## 04 — ESP32 SOFTWARE (1.5 min — first cut candidate)
**On screen:** ESP32 chip diagram + telemetry frame.
**Say:**
> "The ESP32 reads sensors, stamps time, validates values, packs one clean FALCON-01 frame with quality flags — every 4.8-second cycle. Four inputs in parallel, one frame out to LoRa.
>
> The quality flags matter more than the readings. A reading that fails validation is marked, not silently sent. That is how you keep an archive honest."
**Plain words:** "Small controller reads over and over, packs readings into one envelope."

## 05 — LORA LINK (2 min, interactive — the crowd pleaser)
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

## 07 — WAVE ESTIMATE (1 min — second cut candidate)
**On screen:** RAW PRESSURE → PROCESSED → ESTIMATE Hs + depth section.
**Say:**
> "Pressure in, estimated wave height out. Quality check, filter, baseline removal, depth response, calibration → estimated Hs. Depth matters — the sensor sits below the waterline."
**Say the limit:** "Illustrative only. Depth correction, calibration, and reference comparison are not done. No metres claim — relative units only."

## 08 — AI PREDICTION (1.5 min, interactive)
**On screen:** History + AI vs persistence + Run prediction.
**Say:**
> "Target: 5, 10, 15 minutes ahead. Today it's a transparent trend baseline, not a trained model. The evaluation plan is what we are asking you to fund: calibrated data, a chronological train/val/test split, and MAE / RMSE / bias against persistence.
>
> Persistence is the honest opponent — 'tomorrow looks like today' is hard to beat. If our model cannot beat it, we will say so."
**Demo:** `Run prediction` → cyan AI trace extends vs dotted persistence.
**Say:** "Accuracy and skill remain unvalidated."

## 09 — DASHBOARD (1 min — third cut candidate)
**On screen:** 4 tabs — Overview, Buoy Motion, Sensors, Logs & Alerts.
**Say:**
> "Four pages: Overview, Buoy Motion, Sensors, Logs & Alerts. Security states SECURE / WARNING / ALERT / DISARMED. Normal wave motion must not raise an alert — false-positive testing is required before any alarm claim."
**Demo:** Click Overview → Motion → Logs. Point at `SIMULATED PREVIEW`.

## 10 — VALIDATION & STATUS (1.5 min — honesty chapter)
**Say:**
> "Nothing here is claimed as validated. Bench sensor tests, pressure-to-wave vs reference, wind vs reference anemometer, GPS geofence, vibration/tamper, power budget — plus LoRa loss/latency/range/buffering, dashboard usability, AI vs baseline. Implemented means the software path runs. It does not mean the measurement is accurate."
**Implemented:** firmware shell, captive portal, framing, Bay service prototype (simulator, SQLite, REST, dashboard), wave-estimate sim, geofence sim.
**Not yet:** final sensor models + cal coeffs, real GPS/tamper, LoRa hardware + range, field-trained AI.
**Say this line, slowly:** "We would rather show you an honest prototype than an impressive claim."

## 11 — SCOPE & RISKS (1 min — safety chapter)
**Say:**
> "What it does not do: no tsunami prediction, no typhoon prediction, no official warnings, no navigation control, no lab-grade water quality. Not a replacement for government monitoring."
**Risks → mitigations:** Power → measured budget. Waterproofing → bench + staged deployment. LoRa range → documented range test first. Calibration drift → routine + reference. False alerts → false-positive testing.

## 12 — ROADMAP & TEAM (2 min — the ask setup)
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

## 13 — IMPACT & FUNDING (2 min — the number)
**Say:**
> "First pilot serves one verified user before expansion. LGUs, fisherfolk, schools/researchers, ports/tourism — each with something still to confirm. No site or beneficiary confirmed yet."
**Innovation line (say verbatim):** "Affordable, documented integration and local evaluation of established sensing, LoRa, shore processing, solar, security, and transparent prediction — not a new sensor, buoy, or AI algorithm."
**Budget — planning range only, not a quotation:**
> "₱90,000 to ₱150,000. Midpoint ~₱115,000 covers import markup, one calibration trial, spares. ₱90k minimum-viable, ₱150k comfortable with contingency. Replaced with 3-supplier canvass before submission."
**7 lines (filter live):** Sensors/embedded 18–26k · Bay+LoRa+SIM 15–25k · Solar/battery/MPPT 14–22k · Hull/keel/enclosure 15–25k · Mooring 7–14k · Calibration/trials 12–20k · Transport/spares/contingency 9–18k.
**Delivers:** one integrated prototype, calibrated subsystems, dashboard + archive, coastal-test results, baseline-vs-model evaluation, reusable docs + datasets.

## 14 — CLOSE (1 min — the ask)
**Say:**
> "Next: freeze BOM per redesign baseline, physical pressure acquisition + calibration routine, LoRa buoy + gateway integration, controlled reference data before any performance claim.
>
> What we are asking for is narrow and concrete: procurement, fabrication, calibration access, supervised testing, and mentorship.
>
> We are not asking you to accept an untested forecast. We are asking for the opportunity to generate local evidence — a number a barangay here can use, and defend, because it was measured here.
>
> Thank you — Project FALCON Research Group, BS IT, Fullbright College."
**Click:** `Experience it again ↗` if Q&A wants a revisit.

---

## Q&A CHEAT SHEET (~5 min)

### Technical (the original eight)
1. **"Accurate ba?"** — "Not yet. No accuracy claim until Gate 04 vs reference with MAE/RMSE/bias."
2. **"Bakit LoRa, hindi 4G sa buoy?"** — "Power + cost + offshore coverage. 4G backhaul stays at Bay Station."
3. **"Bakit hindi tsunami/typhoon warning?"** — "Out of scope by design. Not an official system, no such claim."
4. **"Saan ide-deploy?"** — "No site confirmed. One LGU + one need + one pilot site, verified first."
5. **"Bakit 90–150k?"** — "Landed cost with 20–30% markup, LoRa/mini-PC/SIM now included, plus trials + contingency. Mid 115k defensible."
6. **"Kaya ba 4–5 months?"** — "5 months credible if scope frozen, procurement week 1, parallel permits. 4 months stretch."
7. **"Invention niyo ba sensor/AI?"** — "No. Contribution is affordable integration + local evaluation + transparent methods."
8. **"Paano kung maputol LoRa?"** — "Buoy buffers with original timestamps, replays, rejects duplicates. Demoed live on page 05."

### The three DOST judges actually ask
9. **"Bakit kayo ang dapat bigyan? Ano ang kaya niyo na wala sa iba?"**
> "Because a working path already exists — not a drawing. Before this presentation you can already run: the ESP32 firmware shell with a captive portal, the telemetry frame with quality flags, the Bay Station service with simulator, SQLite store, REST API and dashboard, the wave-estimate path, geofence logic, and the LoRa buffering you saw fail and recover on page 05.
>
> Three students built that with no funding. What funding buys is not the ability to start. It is the sensor hardware, the calibration reference, and the supervised sea trial that turn a running path into a measured one."

10. **"Kaya ba ng team niyo? Ilan kayo, at ano ang eksaktong gagawin ng bawat isa?"**
> "Four students, and the split is already fixed. Jhon Ruzzel Correa owns hardware, power and LoRa firmware. Gwyn Isabel Enriquez owns edge, AI and dashboard. Mayla Bacaltos and Gina Caballero split the thesis papers and the evaluation records.
>
> Two advisers — Sir Jam for papers, Sir Jeff for hardware — and a third seat reserved for a software/AI mentor or a DOST counterpart. We are also proposing this as an OJT placement with DOST as host, half-OJT, half-thesis, so the work continues on a schedule instead of stopping at the semester.
>
> Where we fall short: none of us has done a sea deployment before. That is exactly why the plan is gated — gate 02 bench, gate 04 controlled validation — and why the mentorship seat is part of the ask."

11. **"Kanino ang IP, at kanino ang data?"**
> "The intellectual property stays with the student team and Fullbright College — this is thesis work. Where we are deliberately open is the data.
>
> We propose co-ownership of the collected datasets with the partner LGU or DOST, and the archive is designed to be shareable: timestamped, quality-flagged, with the methods and limitations documented alongside it. A local dataset that only we can read is not worth collecting.
>
> If a partner wants something different, we would rather agree it in writing before deployment than assume it now."

---

## THE ASK — say these five, in this order
1. **Accept Project FALCON-01 as a DOST OJT placement** — dorm-based, half-OJT, half-thesis.
2. **Mentorship seat** — one software/AI or coastal-science mentor, plus the third adviser seat.
3. **Procurement and fabrication support** — the ₱90,000–₱150,000 planning range for parts, hull, mooring and calibration.
4. **Calibration and site access** — a reference instrument and permission for a supervised tank or pool trial.
5. **Trial support and data co-ownership** — supervised coastal testing, and shared ownership of the resulting dataset.

## PRESENTER CHECKLIST
- [ ] `present.html?big=1` tested on projector · phone QA done
- [ ] Interrupt-LoRa + Bay inspect + Run prediction clicked once before show
- [ ] 3rd mentor line updated in `story.js` if named
- [ ] Say "simulated, not validated" on pages 05, 07, 08, 10
- [ ] Rehearse the three DOST questions (9, 10, 11) out loud — they are the ones that decide
- [ ] Timer: full run in 20:00, with the cut list ready if the panel runs short
- [ ] End on funding total ₱90,000–₱150,000 + the five-point ask
