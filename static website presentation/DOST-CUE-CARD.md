# FALCON-01 — 1-Page Cue Card (Taglish, Pang-hawak)
**present.html · `present.html?big=1` sa projector · Space/→ next, ← back, P presenter mode**
Thesis line: *“Affordable, documented, locally-evaluable — integration, hindi invention.”* | Laging sabihin: **“SIMULATED, hindi pa validated.”** (Ch.5,7,8,10)

| Ch. | Screen + CLICK | SABIHIN (1-2 lines) |
|---|---|---|
| 0 Ocean | Click `Begin the journey ↓` | “Good morning, Project FALCON-01, Fullbright College. Barangay need murang wave/wind data. Sagot namin: 1 buoy sa dagat + 1 Bay Station sa shore.” |
| 1 Objectives | Open objectives list | “Phase 1 = integration + evaluation, hindi invention. 6 objectives: solar buoy, pressure+wind, wave estimate with calibration, LoRa to shore, evaluate lahat, AI vs baseline.” |
| 2 Buoy | Click 1 pick (Pressure) → `← Back` | “Ito FALCON-01: ESP32, pressure, wind speed/direction, GPS, battery+solar, LoRa. Walang mini PC/cellular sa buoy — nasa shore ang bigat.” CAD note: legacy names, hindi V4.1. |
| 3 Sensors | Click Pressure → Wind | “Dalawa primary: pressure pang-alon, wind pang-hangin. GPS/power/security = supporting lang. Temp/salinity = out of scope, sinadya.” |
| 4 ESP32 | Point sa frame | “ESP32 nagbabasa, nagti-timestamp, nagva-validate, nagpa-pack ng 1 frame every 4.8s. 4 inputs, 1 frame to LoRa.” |
| 5 LoRa ★DEMO | `Interrupt LoRa` → BUFFER ↑ → `Restore LoRa` | “Buoy → LoRa → Bay Station. SIM nasa Bay Station lang. Sense-Frame-Cross-Buffer-RX-Insight. Walang range guarantee.” |
| 6 Bay Station | `Inspect Bay Station` → click 2 stages → Exit | “Isang shore computer lang: Receive-Validate-Store-Process-AI-Display. States: LIVE / SIMULATED / ESTIMATED.” |
| 7 Wave | Click 01→02→03 | “Pressure in, wave estimate out. Filter, baseline, depth, calibration → Hs. Relative units lang, hindi pa metres. Illustrative only.” |
| 8 AI | Click `Run prediction` | “Target 5/10/15 min ahead. Ngayon trend baseline pa lang, hindi trained model. Kailangan calibrated data + MAE/RMSE/bias.” |
| 9 Dashboard | Click Overview→Motion→Logs | “4 pages: Overview, Motion, Sensors, Logs&Alerts. SECURE/WARNING/ALERT/DISARMED. Normal alon ≠ alert — kailangan false-positive test.” |
| 10 Validation | Basahin Implemented vs Not yet | “Walang validated dito. Implemented = tumatakbo ang software, hindi ibig sabihin accurate. Test muna vs reference bago mag-number.” |
| 11 Scope | Point sa NO list + table | “HINDI tsunami/typhoon warning, hindi official, hindi pamalit sa gobyerno. Risks: power, waterproofing, LoRa, drift, false alerts — may mitigation lahat.” |
| 12 Roadmap+Team | Click G1→G5 isa-isa | “5-month/20-week bootcamp, hindi parts order. G4 ang accuracy gate. G1 Freeze, G2 Bench, G3 Calibrate, G4 Validation, G5 Trial+thesis. Team: Ruzzel-Hardware, Mayla+Gina-Papers, Gwyn-Edge/AI/Dash. Sir Jam, Sir Jeff, 3rd TBD/DOST.” |
| 13 Funding ★NUMBER | Filter All→Installed→Reusable | “1 pilot user muna, walang site pa. Innovation = murang integration + local evaluation, hindi bagong sensor/AI. ₱90k–150k, mid ~₱115k. Planning range lang, papalitan ng 3-supplier canvass.” |
| 14 Close | Click `Experience again` kung Q&A | “Next: freeze BOM, pressure+calibration, LoRa integration, reference data muna. Hingi namin: procurement, fabrication, calibration access, supervised testing, mentorship. Para makagawa ng local evidence. Salamat — FALCON Research Group, BS IT, Fullbright.” |

**Q&A (8 sagot, kabisaduhin):**
1. Accurate? → “Not yet, Gate 04 vs reference, MAE/RMSE/bias.”
2. Bakit LoRa? → “Power+cost+coverage. 4G nasa Bay Station.”
3. Tsunami? → “Out of scope, hindi official.”
4. Saan deploy? → “Wala pa, 1 LGU + 1 need + 1 site muna.”
5. Bakit 90-150k? → “Landed cost + LoRa/mini-PC/SIM + trials. Mid 115k.”
6. Kaya 5 months? → “Oo kung frozen scope, week 1 procurement. 4 months stretch.”
7. Invention? → “Hindi. Integration + evaluation ang ambag.”
8. Naputol LoRa? → “Nagba-buffer with timestamps, replay, reject duplicates — na-demo sa Ch.5.”

**Check bago umakyat:** [ ] big=1 tested [ ] na-try Interrupt/Inspect/Run [ ] “simulated” nasabi 4x [ ] natapos sa ₱90k-150k + ask
