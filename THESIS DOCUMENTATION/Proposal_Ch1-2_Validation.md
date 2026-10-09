# Proposal Validation — Chapters 1 & 2

> Architecture revision note 2026-10-09: update Chapters 1 and 2 around the event-driven Wi-Fi/LTE cloud path, compact reference-style buoy, reduced battery, and revised sensor alternatives. The validation findings below remain useful as template checks but do not constitute approval of the revised hardware.

Scope: `Chapter1_Introduction_first.docx` and `Chapter2_Methodology_first.docx`
Benchmark: official template `REVISED-CAPSTONE-IT_CS-PROPOSAL_4.pdf`
Date: 2026-10-02

---

## 1. Template compliance (section-by-section)

| Template section | Draft file / heading | Status |
| --- | --- | --- |
| 1.1 Background of the Study | Chapter 1 — 1.1 | PASS |
| 1.1.1 International Context | Chapter 1 — 1.1.1 | PASS |
| 1.1.2 National Context | Chapter 1 — 1.1.2 | PASS |
| 1.1.3 Local Context | Chapter 1 — 1.1.3 | PASS |
| 1.2 Review of Related Literature | Chapter 1 — 1.2 | PASS |
| 1.3 Review of Related Studies | Chapter 1 — 1.3 | PASS |
| 1.4 Theoretical and Conceptual Framework | Chapter 1 — 1.4 | PASS |
| 1.5 Significance of the Study | Chapter 1 — 1.5 | PASS |
| 1.6 Statement of the Problem | Chapter 1 — 1.6 | PASS |
| 1.7 (template repeats 1.4 title — likely a typo) | Chapter 1 — 1.7 Scope & Definition of Terms | PASS (draft's reading is correct; confirm with adviser) |
| 2.1 Research Design / Project Development Methodology | Chapter 2 — 2.1 | PASS |
| 2.2 System Architecture / Framework | Chapter 2 — 2.2 | PASS |
| 2.3 Data Collection Methods | Chapter 2 — 2.3 | PASS |
| 2.4 Software and Tools Used | Chapter 2 — 2.4 | PASS |
| 2.5 Development Procedures | Chapter 2 — 2.5 | PASS |
| 2.6 Testing and Evaluation | Chapter 2 — 2.6 | PASS |
| 2.7 Ethical Considerations | Chapter 2 — 2.7 | PASS |

Both chapters match the required proposal skeleton exactly.

---

## 2. Chapter 1 — Introduction

### Passed
- Follows the template order and sub-sections exactly.
- **Citation integrity: clean.** Every in-text citation resolves to the reference list
  (Ardhuin 2019, Cho 2021, Dreyer 2026, Fan 2020, Grare 2021, Liu 2024, Martins 2022,
  Mo 2024, Raja Ali 2026, Skalvik 2023, Song 2023, Williams 2025, Zhang 2020, Zhou 2022,
  PAGASA n.d., NAMRIA 2025).
- **5–7 year rule: satisfied.** All listed references are 2019–2026; foundational works
  older than the window are explicitly excluded from the list and only acknowledged as
  background in the text.
- 1.7 carries an explicit TEMPLATE NOTE explaining the template's duplicated heading — good
  transparency for the adviser.
- Statement of the Problem lists one general problem + 6 specific questions, and maps them
  one-to-one to Chapter 2, Table 1.

### Issues / to-do
1. **[Low] Two named products are uncited:** "Datawell Directional Waverider" and "NexSens"
   are named as benchmarks with no reference. Add manufacturer/data-sheet citations or mark
   them clearly as illustrative examples.
2. **[Low] Figures not yet inserted:** Section 1.4 has a `[FIGURE PLACEHOLDER]` for Figure 1
   (IPO framework). Insert the actual diagram and confirm it matches Chapter 2, Figure 1.
3. **[Low] Table numbering collision:** Chapter 1 has "Table 1" (system comparison) and
   Chapter 2 has "Table 1" (objective instruments). Acceptable if numbering is chapter-scoped,
   but confirm the school convention (chapter-scoped vs continuous).

**Verdict: Chapter 1 is essentially proposal-ready** (pending figure insertion and the two
product citations).

---

## 3. Chapter 2 — Methodology

### Passed
- Structure matches 2.1–2.7 exactly.
- Strong, honest research-design narrative: developmental/design-and-development + mixed
  methods, iterative–incremental cycles, explicit IPO framework, five-layer architecture with
  documented failure behavior.
- Excellent honesty discipline (measured / estimated / predicted / simulated states).
- Evaluation matrix, controlled test scenarios (P-01, C-01, I-01, G-01, T-01, A-01, B-01, R-01),
  and AI chronological hold-out protocol are all present and appropriate.
- All in-text citations are 2019–2026 (within the 5–7 year window).

### Issues / to-do (by priority)
1. **[High] No reference list + orphan citations.** Chapter 2 has no References section of its
   own, and 10 in-text citations have no matching entry anywhere:
   Rojas 2025, Meulé 2024, Knight 2021, Suwardiyanto 2024, Bekiryazıcı 2025, **Chan 2026**,
   Wiranata & Widodo 2026, Mohammadi 2024, Holykell n.d., Blue Robotics n.d.
   - Knight 2021, Holykell n.d., and Blue Robotics n.d. already exist as full entries inside
     `BayStation.docx` — copy them across.
   - Rojas, Meulé, Suwardiyanto, Bekiryazıcı, Chan, Wiranata & Widodo, Mohammadi must be
     sourced or removed.
2. **[High] No methodological framework citation.** 2.1 cites domain papers only. Name and cite
   the research-design authority you follow (e.g., Richey & Klein for DDR; Creswell & Plano
   Clark for mixed methods; or the school-mandated model).
3. **[Medium] Participants/sampling unspecified.** Usability testing names no sample size,
   sampling technique, or criteria. State N (repo plan says ≥5 representative users) and method.
4. **[Medium] Acceptance thresholds are circular.** 2.6 release conditions say "adviser-approved
   threshold met" with no numbers. Pull the concrete targets from
   `docs/SENSOR_VALIDATION_AND_CALIBRATION_PLAN.md` (±1.0 kPa or 2%; wave error ≤0.10 m or 15%;
   AI must beat persistence by an approved margin).
5. **[Medium] Reference/calibration instrument not named** in 2.3 — identify the actual reference
   (water-column method, reference pressure instrument, reference anemometer).
6. **[Medium] Limited statistical rigor.** Reports MAE/RMSE/bias but no inferential tests,
   confidence intervals, effect sizes, or sample-size justification.
7. **[Low] Instrument reliability** — expert validation is mentioned; add reliability testing
   (test–retest / Cronbach's α) and triangulation.
8. **[Low] Data privacy law** — cite RA 10173 (Data Privacy Act of 2012) and note any ethics
   review; aligns with template Appendices C/D/E including the Certificate of Tool Validation.

---

## 4. Priority action checklist

- [ ] Add the Chapter 2 reference list (unified with Chapter 1) and close the 10 orphan citations.
- [ ] Add a methodological-framework citation in 2.1.
- [ ] State participant count and sampling method in 2.6.
- [ ] Replace "adviser-approved threshold met" with the numeric targets from the calibration plan.
- [ ] Name the independent reference/calibration instrument in 2.3.
- [ ] Add RA 10173 and ethics-review statement in 2.7.
- [ ] Insert the Chapter 1 Figure 1 and cite Datawell/NexSens in 1.3.
- [ ] Confirm with the adviser: 1.7 interpretation, table/figure numbering convention, and
      citation style (APA vs IEEE).
