# Project FALCON — DOST Idea Presentation Package

| Field | Value |
| --- | --- |
| Presentation type | Initial idea and funding presentation |
| Project | FALCON-01 — Fullbright College's AI-powered Live Coastal Observation Network |
| Institution | Fullbright College |
| Current stage | Software and engineering concept prototype |
| Funding purpose | Physical development, integration, calibration, and field validation |
| Prepared | 2026-08-15 |

## 1. Core Presentation Message

Project FALCON is a proposed affordable, solar-powered smart coastal observation
buoy. It is designed to collect localized wave-related measurements, process and
store data near the source, display present conditions through a responsive
dashboard, evaluate short-horizon wave prediction after local data collection,
and detect abnormal buoy displacement or system-health conditions.

The project is not being presented as a finished oceanographic product. The team
has developed the system architecture, dashboard, simulator, firmware foundation,
sensor and wiring plan, mechanical concepts, and technical documentation. Funding
will enable the team to purchase the selected components, fabricate the buoy,
integrate and calibrate the sensors, gather coastal data, train and validate the
prediction model, and conduct a supervised pilot deployment.

### Recommended opening statement

> Good day. We are the Project FALCON Research Group from Fullbright College.
> We are proposing an affordable, solar-powered smart coastal observation buoy
> designed to provide localized wave information through embedded sensing, edge
> computing, and a simple monitoring dashboard. We have completed the system
> concept and software demonstration. We are seeking development support to build,
> calibrate, and validate the physical prototype in a controlled coastal setting.

## 2. Ten-Slide Pitch Deck

### Slide 1 — Project Title

**PROJECT FALCON**  
Fullbright College's AI-powered Live Coastal Observation Network

**One-line description:** An affordable solar-powered coastal buoy for localized
wave monitoring, edge data processing, short-horizon prediction research, and
buoy health and displacement alerts.

**Visuals:** Project logo, clean buoy render, and one dashboard screenshot.

**Speaker note:** Introduce the team, school, project name, and the single problem
the proposal addresses. Avoid starting with component specifications.

**Taglish presentation script:**

> Magandang araw po. Kami po ang Project FALCON Research Group mula sa
> Fullbright College. Ang FALCON ay nangangahulugang Fullbright College's
> AI-powered Live Coastal Observation Network. Ang proposal namin ay isang
> affordable at solar-powered smart coastal buoy na ginawa para sa localized
> wave monitoring. Layunin nitong mangolekta ng coastal data, ipakita ito sa
> isang madaling maintindihang dashboard, at magsilbing research platform para
> sa short-term wave prediction at system protection. Sa presentation na ito,
> ipapakita namin ang problemang gusto naming tugunan, paano gagana ang system,
> ano na ang nagawa namin, at ano ang kailangan upang mabuo at ma-validate ang
> physical prototype.

### Slide 2 — The Problem

- Coastal decisions benefit from timely and location-specific sea-condition data.
- Professional oceanographic systems can be difficult for small institutions to
  acquire, operate, and maintain.
- Generic forecasts may not represent conditions at a specific near-shore site.
- Connectivity, energy, maintenance, and equipment security complicate continuous
  coastal monitoring.

**Speaker note:** Connect the problem to a specific intended Palawan user or pilot
site once stakeholder confirmation is available. Do not claim that no monitoring
exists; state that affordable localized access is limited for the intended user.

**Taglish presentation script:**

> Ang pangunahing problemang nakita namin ay ang limitadong access sa affordable
> at location-specific coastal information. May mga official forecast at
> professional monitoring systems na po, pero maaaring maging mahal at mahirap
> i-deploy o i-maintain ang specialized equipment para sa maliit na institution
> o local coastal group. Maaari ring magkaiba ang actual near-shore condition sa
> isang specific location kumpara sa mas malawak na forecast area. Bukod dito,
> kailangan ding solusyunan ang intermittent connectivity, limited power,
> maintenance, at possibility ng abnormal displacement o pagkawala ng buoy.
> Hindi po namin sinasabing walang existing monitoring; ang target gap namin ay
> affordable at localized observation para sa intended pilot user.

### Slide 3 — Proposed Solution

Project FALCON combines:

- wave-related sensors and system-health monitors;
- an ESP32 for reliable sensor acquisition and diagnostics;
- an Orange Pi Zero 3 for local storage, processing, API, and model inference;
- solar power with battery storage;
- a responsive local dashboard;
- offline buffering for intermittent connectivity; and
- GPS/IMU-assisted abnormal-displacement alerts.

**Speaker note:** Explain the system in plain language: measure, validate, store,
analyze, display, and alert.

**Taglish presentation script:**

> Ang proposed solution namin ay Project FALCON. May sensors ito para sa buoy
> motion, water pressure, wind, GPS position, power, at system health. Ang ESP32
> ang regular na kumukuha at nagva-validate ng sensor readings. Pagkatapos,
> ipinapasa ang data sa Orange Pi Zero 3, na siyang magse-save ng records,
> magpapatakbo ng local services, at eventually ng validated prediction model.
> Makikita ng user ang information sa responsive dashboard gamit ang laptop,
> tablet, o phone. Solar-powered din ang design at may local data buffering para
> hindi agad mawala ang observations kapag mahina o walang Internet. May proposed
> GPS at IMU logic din para matukoy ang abnormal movement ng buoy.

### Slide 4 — How It Works

```text
Wave, motion, wind, GPS, power and health sensors
                         |
                         v
              ESP32 acquisition layer
                         |
                    USB / UART
                         v
          Orange Pi Zero 3 edge computer
             |          |          |
          Storage    Processing    Local API
             \          |          /
                         v
                 FALCON dashboard
```

**Speaker note:** The ESP32 handles deterministic sensing. The Orange Pi handles
heavier software. Essential data remain local, so continuous cloud access is not
required for the core prototype.

**Taglish presentation script:**

> Ganito po ang magiging flow ng system. Una, kumukuha ng measurements ang wave,
> motion, wind, GPS, power, at health sensors. Pangalawa, binabasa at chine-check
> ito ng ESP32 bago i-package bilang telemetry. Pangatlo, ipinapadala ang data sa
> Orange Pi sa pamamagitan ng USB o UART. Ang Orange Pi naman ang responsible sa
> local database, signal processing, API, dashboard, at future model inference.
> Sa huli, makikita ng user ang current measurements, history, alerts, at model
> output sa FALCON dashboard. Local-first po ang architecture, kaya hindi kailangan
> ng continuous cloud connection para gumana ang pangunahing monitoring workflow.

### Slide 5 — Current Progress

**Already developed:**

- responsive multi-page dashboard;
- coherent sensor and fault simulator;
- ESP32 firmware foundation and captive portal;
- versioned ESP32-to-edge telemetry contract;
- Python edge service, local database, API, alerts, and forecast presentation;
- wiring diagrams and Wokwi visual baseline;
- parametric mechanical concepts and Revision 5 buoy baseline;
- hardware bill of materials, power calculations, test plan, and documentation.

**Current verification:**

- ESP32 firmware builds successfully;
- 18 edge-service automated tests pass; and
- Dashboard Next production build passes.

**Not yet completed:** physical sensor integration, assembled marine power system,
field-trained AI, calibration, and marine deployment validation.

**Taglish presentation script:**

> Sa current stage, hindi na lang po ito drawing o raw idea. May working responsive
> dashboard, sensor at fault simulator, ESP32 firmware foundation, telemetry
> protocol, Python edge service, local database, API, alerts, wiring diagrams,
> mechanical concepts, bill of materials, at testing documentation na kami.
> Na-build na rin nang successful ang ESP32 firmware at dashboard, at pumapasa ang
> automated edge-service tests. Pero gusto naming maging transparent: simulated
> data pa ang ginagamit sa demonstration. Hindi pa assembled ang complete physical
> buoy, hindi pa integrated at calibrated ang actual sensors, at hindi pa
> field-trained o safety-validated ang AI. Iyon po mismo ang development stage na
> gusto naming pondohan at maisagawa nang tama.

### Slide 6 — Innovation and Differentiation

- Affordable and modular student-scale architecture.
- Local edge processing instead of mandatory cloud dependence.
- Focused wave-monitoring scope rather than uncontrolled sensor expansion.
- Dashboard transparency: input quality, prediction horizon, model version,
  recent error, and uncertainty are intended to accompany model output.
- Combined monitoring of observations, energy, position, and system health.
- Reproducible documentation for future school and community research.

**Defensible novelty statement:**

> FALCON's innovation is the validated integration and local adaptation of its
> sensing, edge-computing, energy, prediction, and protection subsystems—not the
> invention of an individual sensor, buoy, or machine-learning algorithm.

**Taglish presentation script:**

> Ang innovation ng FALCON ay hindi nakabase sa claim na kami ang nakaimbento ng
> buoy, sensor, o AI algorithm. Ang contribution namin ay ang validated integration
> at local adaptation ng mga subsystem na ito sa isang affordable at modular
> platform. Local ang processing kaya hindi mandatory ang cloud. Focused ang sensor
> scope para manageable ang calibration, cost, at energy. Intended din na malinaw
> sa dashboard kung simulated, measured, estimated, o predicted ang isang value.
> Kasama rin sa iisang platform ang wave monitoring, energy status, position,
> system health, at abnormal-displacement alerts. Ang magiging sukatan ng novelty
> namin ay hindi dami ng features, kundi kung maayos, reproducible, at validated
> ang pagsasama ng mga ito para sa local use case.

### Slide 7 — Intended Beneficiaries and Value

Potential beneficiaries include:

- coastal local government and disaster-management offices;
- fisherfolk and small-craft communities;
- schools and marine researchers;
- ports, coastal tourism operators, and environmental organizations.

Potential value includes localized observation history, accessible visualization,
research data, equipment-health awareness, and a platform that can be improved by
future student teams.

**Important:** Identify one primary beneficiary before the presentation whenever
possible. A stakeholder interview or support letter will strengthen this slide.

**Taglish presentation script:**

> Ang possible beneficiaries ng project ay coastal LGUs at disaster-management
> offices, fisherfolk at small-craft communities, schools at marine researchers,
> ports, tourism operators, at environmental organizations. Makakatulong ang
> FALCON sa pagkakaroon ng localized observation history, mas accessible na data
> visualization, research dataset, at awareness sa condition ng equipment.
> Gayunman, hindi namin gustong sabihing para agad ito sa lahat. Bago ang actual
> pilot, pipili kami ng isang primary beneficiary at specific site sa Palawan,
> aalamin ang tunay nilang information needs, at ia-adjust ang deployment at
> dashboard ayon sa responsible at realistic na use case.

### Slide 8 — Development Plan

| Phase | Main output | Indicative duration |
| --- | --- | ---: |
| 1. Final design and procurement | Frozen parts list and purchased components | 1 month |
| 2. Electronics integration | Working sensor and power assemblies | 1–2 months |
| 3. Buoy fabrication | Sealed and stable physical prototype | 1 month |
| 4. Calibration and controlled tests | Calibration records and corrected data | 1–2 months |
| 5. Coastal pilot and data collection | Supervised local dataset | 2–3 months |
| 6. Model training and evaluation | Baseline comparison and validated results | 1–2 months |
| 7. Final demonstration and reporting | Validated prototype and technical report | 1 month |

Estimated development period: approximately **8–12 months**, subject to procurement,
weather, permits, site access, and the amount of data required.

**Taglish presentation script:**

> Kapag nabigyan ng support, hahatiin namin ang development sa malinaw na phases.
> Magsisimula kami sa final design at procurement, kasunod ang electronics at
> sensor integration. Pagkatapos ay fabrication at sealing ng buoy, calibration,
> at controlled testing. Kapag pumasa sa basic safety at reliability tests, saka
> kami magsasagawa ng supervised coastal pilot at data collection. Ang collected
> at validated data ang gagamitin sa model training at baseline comparison.
> Magtatapos ang project sa final system evaluation, demonstration, at technical
> reporting. Ang realistic estimate namin ay eight to twelve months, dahil maaari
> itong maapektuhan ng procurement, weather, permits, site access, at sapat na data.

### Slide 9 — Preliminary Funding Plan

| Category | Preliminary amount |
| --- | ---: |
| Sensors and embedded electronics | PHP 15,000–22,000 |
| Edge computer, storage, and networking | PHP 5,000–8,000 |
| Solar, battery, charging, and protected distribution | PHP 12,000–20,000 |
| Buoy body, structure, enclosure, and marine connectors | PHP 15,000–28,000 |
| Mooring, anchor, corrosion protection, and safety hardware | PHP 7,000–14,000 |
| Calibration, reference tools, fabrication, and field trials | PHP 10,000–20,000 |
| Transport, documentation, spares, and contingency | PHP 8,000–15,000 |
| **Indicative development request** | **PHP 72,000–127,000** |

This is a planning range, not a supplier quotation. Before submission, replace
estimates with current quotations and separate reusable tools from installed parts.
The lower raw-component estimate in the technical BOM does not include all field
testing, fabrication, transport, spares, and contingency costs.

**Taglish presentation script:**

> Para sa preliminary funding plan, ang indicative development request ay mula
> seventy-two thousand hanggang one hundred twenty-seven thousand pesos. Hindi
> lang po ito presyo ng sensors. Kasama rito ang embedded electronics, Orange Pi,
> solar at battery system, marine enclosure at structure, mooring at anchor,
> calibration or reference tools, fabrication, field testing, transport, spare
> parts, at contingency. Planning range pa lamang ito at papalitan namin ng actual
> supplier quotations bago ang formal procurement. Hihiwalay rin namin ang
> reusable tools sa components na permanenteng mai-install sa prototype para
> transparent at madaling i-review ang budget.

### Slide 10 — Expected Result and Request

At the end of funded development, the team intends to deliver:

- one integrated and documented physical prototype;
- calibrated sensor and power subsystems;
- local dashboard and data archive;
- controlled and supervised coastal-test results;
- baseline-versus-model prediction evaluation;
- power, communication, ingress, stability, and alert-test reports; and
- reproducible source code, wiring, BOM, and operating documentation.

**Funding request:** component procurement, fabrication, calibration access,
supervised field testing, and technical mentorship.

**Recommended closing statement:**

> We are not asking you to accept an untested prediction as an operational
> product. We are asking for the opportunity to turn a documented and working
> software concept into a calibrated physical prototype, generate local evidence,
> and determine its real technical and community value through responsible testing.

**Taglish presentation script:**

> Kapag natapos ang funded development, target naming ma-deliver ang isang
> integrated at documented physical prototype, calibrated sensors at power
> subsystem, local dashboard at data archive, supervised coastal-test results,
> model-versus-baseline evaluation, at reports para sa power, communication,
> waterproofing, stability, at alert performance. Kasama rin ang reproducible
> source code, wiring, bill of materials, at operating documentation. Ang hinihingi
> naming support ay para sa component procurement, fabrication, calibration,
> supervised field testing, at technical mentorship. Hindi po namin hinihinging
> tanggapin agad ang untested AI bilang operational forecast. Ang hinihingi namin
> ay pagkakataong gawing calibrated at evidence-based physical prototype ang
> working concept na na-develop na namin. Maraming salamat po, at handa kaming
> sagutin ang inyong mga tanong.

## 3. Dashboard Demonstration Script

Target duration: **3–5 minutes**.

1. Open the Overview page and identify the simulator source label.
2. Explain that the present values demonstrate the intended telemetry pipeline.
3. Open Wave AI and show measured history, the present boundary, and forecast side.
4. State clearly that the forecast is a presentation model, not a field-trained AI.
5. Open Motion to demonstrate orientation and sea visualization.
6. Open GPS and explain the proposed reference point, geofence, and drift logic.
7. Open Power to show battery, solar, temperature, and energy monitoring.
8. Trigger one simulator fault scenario and show how the dashboard displays alerts.
9. Return to Overview and explain what funding enables next: actual components,
   calibrated inputs, field data, trained model, and validation.

### Demonstration disclosure

Say this before or during the demo:

> The dashboard is connected to our operational edge-service simulator. The
> simulator produces coherent test telemetry so we can validate the interface,
> database, API, alerts, and workflow before risking physical hardware. These are
> not live ocean measurements. Actual measurement and AI validation are part of
> the proposed funded development.

### Demo preparation

- Start the edge service and dashboard before entering the room.
- Keep a local copy; do not depend on venue Internet.
- Test the projector resolution and browser zoom.
- Disable unrelated notifications.
- Prepare screenshots or a short screen recording as backup.
- Keep the normal scenario selected at the start.
- Never hide the SIMULATOR label.

## 4. Likely Panel Questions and Suggested Answers

### Is the system already working?

The software pipeline, simulator, firmware foundation, dashboard, local API, and
technical designs are working. The complete physical buoy and sensor measurements
are not yet integrated. Funding is being requested for that development and
validation stage.

### Is the AI already accurate?

Not yet. The current graph is a transparent presentation forecast used to test the
software workflow. A valid model requires calibrated local field data, chronological
testing, comparison with simple baselines, and reported error and uncertainty.

### Why use AI if ordinary forecasting methods exist?

The project will first compare persistence, moving average, regression, and compact
machine-learning models. AI will only be retained if it provides consistent measured
improvement while meeting edge-device constraints. The project does not assume that
a complex model is automatically better.

### How will wave height be measured?

The study will investigate synchronized buoy motion and water-pressure observations.
Raw acceleration or pressure will not be called wave height directly. Orientation,
gravity, filtering, drift, water depth, hull response, and mooring effects must be
considered and compared with a reference method during controlled testing.

### Why ESP32 and Orange Pi?

The ESP32 is appropriate for predictable sensor acquisition and basic safety logic.
The Orange Pi provides Linux-based storage, API, dashboard, and lightweight model
processing. Separating the roles improves maintainability and allows core acquisition
to continue independently of higher-level services.

### Will it work without Internet?

Core sensing, local storage, processing, and local dashboard access are designed to
work without cloud service. Long-distance remote access still depends on the final
communication method and site coverage. Data will be buffered locally during outages.

### How is it different from existing buoys?

FALCON does not claim to replace professional buoys. Its intended contribution is an
affordable, documented, locally validated integration of wave-related sensing, edge
processing, transparent prediction research, energy monitoring, and displacement
alerts for an educational and community-oriented use case.

### How will you prevent false theft alarms?

A single GPS threshold is insufficient. The proposed logic combines a sustained
geofence breach, displacement behavior, GPS quality, unusual IMU motion, and time
persistence. Normal anchor swing, receiver noise, strong waves, authorized handling,
anchor drag, and simulated removal will be included in testing.

### Can it replace PAGASA warnings?

No. FALCON is a research and local decision-support prototype. It is not a certified
weather-warning or navigational instrument. Official warnings remain authoritative.

### Why should this project be funded now?

The concept has progressed beyond an unsupported idea: architecture, firmware
foundation, simulator, edge service, dashboard, wiring, mechanical concepts, test
plans, and documentation already exist. Funding directly unlocks the missing evidence:
physical integration, calibration, local data, and supervised field validation.

### What happens after the funded prototype?

The team will document performance and limitations, preserve the source and datasets,
train future researchers, and pursue partnership with an appropriate coastal user.
Expansion to additional environmental sensors will only follow successful validation
of the focused Phase 1 system.

## 5. Presenter Rules

### Always say

- proposed, prototype, intended, to be evaluated, or to be validated;
- simulated telemetry when showing the current dashboard;
- local decision-support and research platform;
- accuracy will be measured against reference observations; and
- official warnings remain authoritative.

### Do not claim

- that current dashboard values are live ocean data;
- that the AI is already trained or accurate;
- direct wave height from raw accelerometer or pressure values;
- 24/7 field autonomy before endurance testing;
- typhoon, tsunami, or storm prediction;
- certified navigation or public-safety capability;
- guaranteed one-kilometer communication range; or
- that FALCON replaces professional monitoring agencies.

## 6. Materials Checklist

- [ ] Ten-slide presentation exported for offline viewing
- [ ] Working local dashboard and edge simulator
- [ ] Backup dashboard screenshots or screen recording
- [ ] One-page project summary
- [ ] Simplified system architecture diagram
- [ ] Buoy mechanical render
- [ ] Wiring overview
- [ ] Preliminary budget with quotations when available
- [ ] Development timeline
- [ ] Team member names, roles, and short qualifications
- [ ] Laptop charger, video adapter, extension cord, and offline copies
- [ ] Contact details and funding request
- [ ] Optional stakeholder interview or letter of support

## 7. Team Speaking Assignment Template

| Presenter | Assigned content | Target time |
| --- | --- | ---: |
| Member 1 | Opening, problem, and beneficiaries | 2 minutes |
| Member 2 | Solution and architecture | 2 minutes |
| Member 3 | Dashboard demonstration | 3–5 minutes |
| Member 4 | Development plan, budget, and request | 2 minutes |
| All members | Questions and answers | As allotted |

Keep the main presentation within **10–12 minutes** unless the organizers provide
a different limit. Assign one member to control the laptop and one to monitor time.

## 8. Final Preparation Priorities

1. Confirm the presentation duration, available equipment, and whether a template
   or submission format is required.
2. Identify the primary Palawan beneficiary or pilot site.
3. Obtain current supplier quotations for major components and fabrication.
4. Select the strongest dashboard and CAD visuals.
5. Rehearse the simulator disclosure and funding request.
6. Practice answering questions without overstating the current AI or hardware state.
7. Prepare both editable and PDF/offline presentation copies.
