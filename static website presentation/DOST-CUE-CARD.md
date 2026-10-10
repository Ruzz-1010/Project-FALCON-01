# FALCON-01 — 1-Page Cue Card (Taglish, Pang-hawak)

<!-- FALCON-DOST-REVISION-NOTE:START -->
> **Current revision note (2026-10-10):** Use the DOST major revision baseline in [`docs/REVISION_2026-10-10.md`](../docs/REVISION_2026-10-10.md) unless this file is explicitly archived. The active proposal core is a compact ESP32-based buoy with **water pressure sensing, wind speed/direction sensing, GPS for exact position and security, battery + solar power, and Wi-Fi/LTE internet communication**. LoRa, large Bay Station hardware, tall tower layouts, and continuous every-second uploads are legacy or optional fallback assumptions.
<!-- FALCON-DOST-REVISION-NOTE:END -->

> Revision note 2026-10-10: use the smaller single-tube, event-driven cloud direction. Replace LoRa/Bay Station wording below with Wi-Fi for bench tests or 4G/LTE for a remote field path; summaries and alerts are uploaded from the ESP32 and buffered locally during outages.
**present.html · `present.html?big=1` sa projector · Space/→ next, ← back, P presenter mode · ~20 min · 6 October 2026**
**Full Taglish script: `DOST-MASTER-SCRIPT-TAGLISH.md`**
Thesis line: *“Affordable, documented, locally-evaluable — integration, hindi invention.”* | Laging sabihin: **“SIMULATED, hindi pa validated.”** (Ch.5,7,8,10)

| Ch. | Screen + CLICK | SABIHIN (1-2 lines) |
|---|---|---|
| 0 Ocean | Click `Begin the journey ↓` | “Bawat barangay dito, desisyon malapit sa tubig — wala halos isang numerong sinusukat. Mahal at sarado ang commercial buoy, kaya walang data. Ito ang gap. FALCON-01, Fullbright College: isang maliit na buoy + cloud dashboard, lokal at transparent.” |
| 1 Objectives | Open objectives list | “Phase 1 = integration + evaluation, hindi invention. 6 objectives: solar buoy, pressure+wind, wave estimate with calibration, event-driven cloud upload, evaluate lahat, AI vs baseline. Hindi tayo gagawa ng bagong sensor, buoy, o AI algorithm.” |
| 2 Buoy | Click 1 pick (Pressure) → `← Back` | “Ito FALCON-01: ESP32, pressure, required wind/GPS, battery+solar, local buffer, Wi-Fi for bench or 4G/LTE for field. Walang mini PC sa buoy — ESP32 lang ang controller. Bawat pyesa pinili dahil kayang bilhin, i-wire, at ayusin ng estudyante.” CAD note: legacy names, hindi V4.1. |
| 3 Sensors | Click Pressure → Wind | “Dalawa primary: pressure pang-alon, wind pang-hangin. GPS/power/security = supporting lang. Temp/salinity = out of scope, sinadya.” |
| 4 ESP32 ✂ | Point sa frame | “ESP32 nagbabasa locally, nagti-timestamp, nagva-validate, gumagawa ng 1–5 minute summary, at nagpapadala agad kung may validated event. Ang quality flags ang mahalaga — may marka ang sirang reading, hindi tahimik na ipapadala.” |
| 5 Event-driven Upload ★DEMO | `Interrupt Internet` → BUFFER ↑ → `Restore Internet` | “Buoy ESP32 → Wi-Fi/LTE → cloud/edge dashboard. Kapag walang internet, buffer muna with timestamps; pagbalik ng connection, upload queued summaries/events without duplicate records.” |
| 6 Cloud / Edge Service | `Inspect Bay Station` → click 2 stages → Exit | “Receive-Validate-Store-Process-AI-Display can run on laptop/edge/cloud. States: LIVE / SIMULATED / ESTIMATED / OFFLINE-BUFFERED.” |
| 7 Wave ✂ | Click 01→02→03 | “Pressure in, wave estimate out. Filter, baseline, depth, calibration → Hs. Relative units lang, hindi pa metres. Illustrative only.” |
| 8 AI | Explain only, no click | “Target 5/10/15 min ahead. Ngayon trend baseline pa lang, hindi trained model. Kailangan calibrated data + MAE/RMSE/bias. Persistence ang kalaban — kung hindi natin matalo, sasabihin natin.” |
| 9 Dashboard ★LIVE | Edge service muna, then click tabs sa live view | “Hindi picture — ito mismo ang dashboard, tumatakbo sa laptop na ito. Overview, Sensors, Motion, GPS, Logs&Alerts, Settings. SECURE/WARNING/ALERT/DISARMED. Normal alon ≠ alert.” Kung OFFLINE: Retry. |
| 10 Validation | Basahin Implemented vs Not yet | “Walang validated dito. Implemented = tumatakbo ang software, hindi ibig sabihin accurate. Test muna vs reference bago mag-number. Mas gusto naming honest na prototype kaysa magandang claim.” |
| 11 Scope | Point sa NO list + table | “HINDI tsunami/typhoon warning, hindi official, hindi pamalit sa gobyerno. Risks: power, waterproofing, internet outage, drift, false alerts — may mitigation lahat.” |
| 12 Roadmap+Team | Click G1→G5 isa-isa | “5-month/20-week bootcamp, hindi parts order. G4 ang accuracy gate. G1 Freeze, G2 Bench, G3 Calibrate, G4 Validation, G5 Trial+thesis. Team: Ruzzel-Hardware, Mayla+Gina-Papers, Gwyn-Edge/AI/Dash. Sir Jam, Sir Jeff, 3rd TBD/DOST.” |
| 13 Funding ★NUMBER | Filter All→Installed→Reusable | “1 pilot user muna, walang site pa. Innovation = murang integration + local evaluation, hindi bagong sensor/AI. ₱45k–65k, mid ~₱55k. Planning range lang, papalitan ng 3-supplier canvass.” |
| 14 Close ★ASK | Click `Experience again` kung Q&A | “Next: freeze BOM, pressure+calibration, event thresholds, cloud endpoint, reference data muna. Hingi namin — limang puntos: OJT host, mentor/bench, procurement with reduced-cost sensor options, calibration + site access, trial support + co-own data. Hindi forecast ang hinihingi namin — pagkakataong gumawa ng lokal na ebidensya. Salamat — FALCON Research Group, BS IT, Fullbright.” |

**✂ = CUT LIST kung maikli ang oras:** 04 (diagram lang, 1 pangungusap) → 07 (ituro lang) → 09 (huwag i-click, pangalan lang). Huwag kailanman putulin: 05, 08, 10, 12, 13.

**Q&A — 8 teknikal, kabisaduhin:**
1. Accurate? → “Not yet, Gate 04 vs reference, MAE/RMSE/bias.”
2. Bakit cloud/Wi-Fi/LTE? → “Para mas simple ang architecture kung may internet. ESP32 pa rin ang local sampler; summary/event packets lang ang pinapadala para tipid data at battery.”
3. Tsunami? → “Out of scope, hindi official.”
4. Saan deploy? → “Wala pa, 1 LGU + 1 need + 1 site muna.”
5. Bakit 45-65k? → “Drum hull + refurb PC + no SIM + borrowed reference. Event-driven TX = maliit na power. Mid 55k.”
6. Kaya 5 months? → “Oo kung frozen scope, week 1 procurement. 4 months stretch.”
7. Invention? → “Hindi. Integration + evaluation ang ambag.”
8. Naputol internet? → “Nagba-buffer with timestamps, replay, reject duplicates — hindi nawawala ang event history habang offline.”

**Q&A — 3 tanong ng DOST, ito ang nagpapasya:**
9. **Bakit kayo?** → “May gumaganang path na, hindi drawing: firmware shell, captive portal, framing, edge/cloud service (simulator, SQLite, REST, dashboard), wave path, geofence, offline buffer. Tatlong estudyante, walang pondo. Ang binibili ng pondo: hardware, calibration reference, supervised sea trial.”
10. **Kaya ba ng team?** → “4 estudyante, nakatakda na ang hati: Ruzzel-hardware/power/ESP32-cloud path, Gwyn-edge/AI/dashboard, Mayla+Gina-papers/evaluation. 2 adviser + 1 bakanteng seat (SW/AI o DOST). Kulang: wala pang nakapag-sea deployment — kaya gated ang plano at kasama ang mentor sa ask.”
11. **Kanino ang IP/data?** → “IP sa team at Fullbright — thesis work. Bukas kami sa co-ownership ng dataset kasama ang LGU/DOST: timestamped, quality-flagged, may docs at limitations. Dataset na kami lang ang makakabasa ay walang halaga.”

**Check bago umakyat:** [ ] big=1 tested [ ] na-try Interrupt/Inspect [ ] edge service running + 09 live OK [ ] "simulated" nasabi 4x [ ] timer 20:00 [ ] na-rehearse ang Q9-11 [ ] natapos sa ₱45k-65k + 5-puntong ask
