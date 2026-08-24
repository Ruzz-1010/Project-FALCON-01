from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "THESIS DOCUMENTATION" / "PROJECT FALCON-01.docx"
OUTPUT = ROOT / "THESIS DOCUMENTATION" / "PROJECT FALCON-01 - CURRENT V2 REVISED.docx"


def set_cell_shading(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    tc_pr.append(shd)


def set_repeat_table_header(row):
    tr_pr = row._tr.get_or_add_trPr()
    repeat = OxmlElement("w:tblHeader")
    repeat.set(qn("w:val"), "true")
    tr_pr.append(repeat)


def add_table(doc, headers, rows, widths=None):
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Table Grid"
    header = table.rows[0]
    set_repeat_table_header(header)
    for index, text in enumerate(headers):
        header.cells[index].text = text
        set_cell_shading(header.cells[index], "D9EAF7")
        for run in header.cells[index].paragraphs[0].runs:
            run.bold = True
    for values in rows:
        cells = table.add_row().cells
        for index, value in enumerate(values):
            cells[index].text = str(value)
    if widths:
        for row in table.rows:
            for index, width in enumerate(widths):
                row.cells[index].width = Inches(width)
    doc.add_paragraph()
    return table


def add_bullets(doc, items):
    for item in items:
        doc.add_paragraph(item, style="List Bullet")


def add_numbered(doc, items):
    for item in items:
        doc.add_paragraph(item, style="List Number")


def add_heading(doc, text, level=1):
    return doc.add_heading(text, level=level)


def add_body(doc, text, bold_prefix=None):
    paragraph = doc.add_paragraph()
    if bold_prefix and text.startswith(bold_prefix):
        paragraph.add_run(bold_prefix).bold = True
        paragraph.add_run(text[len(bold_prefix):])
    else:
        paragraph.add_run(text)
    return paragraph


def add_page_number(section):
    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = footer.add_run("Page ")
    field = OxmlElement("w:fldSimple")
    field.set(qn("w:instr"), "PAGE")
    run._r.addnext(field)


def configure_document(doc):
    styles = doc.styles
    styles["Normal"].font.name = "Arial"
    styles["Normal"].font.size = Pt(11)
    styles["Normal"].paragraph_format.space_after = Pt(6)
    styles["Normal"].paragraph_format.line_spacing = 1.15
    for name, size, color in (
        ("Title", 22, "123A5A"),
        ("Heading 1", 16, "123A5A"),
        ("Heading 2", 13, "1D5A7A"),
        ("Heading 3", 11, "1D5A7A"),
    ):
        style = styles[name]
        style.font.name = "Arial"
        style.font.size = Pt(size)
        style.font.color.rgb = __import__("docx").shared.RGBColor.from_string(color)
    for section in doc.sections:
        section.top_margin = Inches(0.75)
        section.bottom_margin = Inches(0.75)
        section.left_margin = Inches(0.85)
        section.right_margin = Inches(0.85)
        add_page_number(section)


def build_document():
    if not SOURCE.exists():
        raise FileNotFoundError(SOURCE)
    if OUTPUT.exists():
        raise FileExistsError(f"Refusing to overwrite existing revised thesis: {OUTPUT}")

    doc = Document()
    configure_document(doc)

    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title.add_run(
        "PROJECT FALCON-01\n"
        "Design and Development of an AI-Assisted Solar-Powered Coastal "
        "Observation Buoy for Local Wave Monitoring"
    )
    run.bold = True
    run.font.name = "Arial"
    run.font.size = Pt(20)
    run.font.color.rgb = __import__("docx").shared.RGBColor(18, 58, 90)
    subtitle = doc.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    subtitle.add_run(
        "Current Revision 5 / Thesis Documentation Update\n"
        "Fullbright College\n24 August 2026"
    ).font.size = Pt(12)
    doc.add_paragraph()
    note = doc.add_paragraph()
    note.alignment = WD_ALIGN_PARAGRAPH.CENTER
    note.add_run(
        "Status: Phase 1 research prototype. Simulator and presentation pipeline "
        "operational; physical marine validation and field-trained AI pending."
    ).italic = True
    doc.add_page_break()

    add_heading(doc, "Document Control", 1)
    add_table(doc, ["Field", "Current value"], [
        ("Project", "FALCON-01 — Fullbright College's AI-powered Live Coastal Observation Network"),
        ("Document", "Current V2 revised thesis documentation"),
        ("Mechanical baseline", "Revision 5 traditional single-body rounded-keel buoy"),
        ("Embedded controller", "ESP32 DevKit / ESP-WROOM-32 class"),
        ("Edge computer", "Orange Pi Zero 3, 4 GB target; development laptop currently used"),
        ("Dashboard", "Dashboard Next, React/TypeScript, served locally by the edge service"),
        ("AI status", "Transparent presentation forecast; final field-trained model pending"),
        ("Source authority", "Repository PROJECT_CONTEXT.md v4.0 and CURRENT_PROJECT_DOCUMENTATION.md"),
    ], widths=[2.0, 4.8])

    add_heading(doc, "Executive Summary", 1)
    add_body(doc, (
        "Project FALCON-01 is a local-first, solar-powered coastal observation buoy "
        "prototype designed to collect wave-related measurements, estimate wave height "
        "from synchronized pressure and motion data, store evidence locally, and present "
        "system status through a responsive dashboard. The current Revision 5 design uses "
        "a compact traditional single-body HDPE float with a rounded underwater keel, low "
        "ballast, single-point mooring, tapered aluminum tower, two opposed 30 W solar "
        "panels, an elevated sealed electronics pod, and a serviceable sensor platform."
    ))
    add_body(doc, (
        "The system separates deterministic sensor acquisition from higher-level edge "
        "processing. The ESP32 performs acquisition, validation, diagnostics, and telemetry "
        "framing. The Orange Pi Zero 3 is the selected edge host for local storage, REST API "
        "services, alerts, wave processing, AI inference, explainability output, and dashboard "
        "hosting. During development, the same edge software runs on a laptop and uses a "
        "coherent simulator until physical sensors are fully integrated and calibrated."
    ))
    add_body(doc, (
        "Phase 1 AI is intentionally narrow. It predicts wave height five to fifteen minutes "
        "ahead and classifies sea condition as Calm, Moderate, or Rough. The repository "
        "currently contains a damped-trend presentation model that demonstrates the complete "
        "data pipeline, history, confidence indicators, and dashboard behavior. It is not yet "
        "a field-trained or safety-validated forecasting model. Final performance claims will "
        "require synchronized pressure/IMU trials, chronological model evaluation, baseline "
        "comparison, and documented errors."
    ))

    add_heading(doc, "1. Background and Rationale", 1)
    add_body(doc, (
        "Philippine coastal communities depend on localized sea information for education, "
        "research, fishing, small-vessel planning, and coastal management. Professional wave "
        "buoys provide high-quality measurements but are often expensive and difficult for "
        "student teams or small institutions to acquire and maintain. Low-cost IoT prototypes "
        "are more accessible, but many stop at sensor display and do not preserve auditable "
        "data, expose measurement quality, or evaluate short-horizon prediction at the edge."
    ))
    add_body(doc, (
        "FALCON addresses this integration gap through a reproducible student-scale platform. "
        "Its contribution is not the invention of a new buoy, sensor, or AI algorithm; it is "
        "the locally adapted integration and evaluation of marine sensing, embedded control, "
        "edge computing, renewable power, mechanical packaging, explainable prediction, and "
        "a human-readable local dashboard."
    ))

    add_heading(doc, "2. Statement of the Problem", 1)
    add_body(doc, "This study seeks to answer the following questions:")
    add_numbered(doc, [
        "How can a compact solar-powered coastal buoy be designed for serviceability, stability, and supervised near-shore deployment?",
        "How can synchronized pressure, motion, position, wind, power, and enclosure-temperature data be acquired and quality-checked locally?",
        "How accurately can calibrated pressure and IMU data support a defined wave-height estimate under controlled and near-shore trials?",
        "Which lightweight method provides the best five- and fifteen-minute wave-height prediction performance on unseen chronological data while remaining suitable for an Orange Pi Zero 3?",
        "How effectively can the local dashboard distinguish measured, estimated, simulated, and predicted information while exposing system health and AI limitations?",
    ])

    add_heading(doc, "3. Research Gap and Contribution", 1)
    add_body(doc, (
        "The reviewed gap is not a lack of commercial smart buoys or wave-prediction models. "
        "It is the limited availability of affordable, reproducible, locally validated systems "
        "that integrate the entire chain from sensor quality and mechanical response to edge "
        "storage, prediction, explainability, maintenance, and user presentation. FALCON's "
        "defensible contribution is the evaluation of that complete chain for a defined local "
        "coastal use case."
    ))

    add_heading(doc, "4. Objectives", 1)
    add_heading(doc, "4.1 General Objective", 2)
    add_body(doc, (
        "To design, develop, and evaluate Project FALCON-01 as a solar-powered, local-first "
        "coastal observation buoy for wave monitoring and AI-assisted short-term wave-height "
        "prediction."
    ))
    add_heading(doc, "4.2 Specific Objectives", 2)
    add_numbered(doc, [
        "Develop the Revision 5 single-body buoy, tapered tower, ballast, mooring, sealed electronics pod, and two-panel solar structure as a serviceable CAD prototype.",
        "Implement ESP32 sensor diagnostics, acquisition interfaces, validity states, and versioned telemetry.",
        "Implement a local Orange Pi edge service for ingestion, SQLite persistence, APIs, alerts, prediction history, and dashboard hosting.",
        "Estimate wave height using a documented, calibrated combination of pressure and IMU evidence.",
        "Develop and evaluate a lightweight five- and fifteen-minute wave-height prediction method against persistence and statistical baselines.",
        "Classify sea condition as Calm, Moderate, or Rough using controlled thresholds and hysteresis.",
        "Evaluate sensing, prediction, dashboard, power, ingress, thermal, stability, mooring, and supervised deployment performance.",
    ])

    add_heading(doc, "5. Current Revision and Legacy Corrections", 1)
    add_table(doc, ["Old thesis statement", "Current Revision 5 baseline"], [
        ("Four stabilizer buoys and support arms", "Removed. Traditional single-body rounded-keel float with low ballast and single-point mooring."),
        ("One generic solar panel / broad array", "Two opposed 30 W panels on a compact tapered tower; 60 W supervised-test baseline."),
        ("Generic Mini PC", "Orange Pi Zero 3, 4 GB selected as the edge target; laptop used during development."),
        ("Broad weather and water-quality sensor suite", "Focused Phase 1 sensors only; water-quality sensing is outside scope."),
        ("Humidity and leak sensors installed", "Not in the approved current installed baseline. MCP9808 measures enclosure temperature."),
        ("Two open-air cooling zones", "One sealed pod with closed internal recirculation, airflow guides, sealed thermal bridge, and rear external finned heat sink."),
        ("Many AI outputs including tide, wind warning, health and anomalies", "AI limited to wave-height prediction and Calm/Moderate/Rough classification."),
        ("AI already operationally accurate", "Presentation model only; field-trained model and safety validation pending."),
    ], widths=[2.7, 4.1])

    add_heading(doc, "6. Scope and Delimitations", 1)
    add_heading(doc, "6.1 Included in Phase 1", 2)
    add_bullets(doc, [
        "Supervised near-shore coastal monitoring prototype.",
        "Pressure- and IMU-supported wave-height estimation after calibration.",
        "Five- and fifteen-minute AI-assisted wave-height prediction research.",
        "Calm, Moderate, and Rough sea-condition classification.",
        "GPS position and displacement context, wind context, power monitoring, and enclosure temperature.",
        "Local storage, REST API, responsive dashboard, alerts, logs, and data export.",
        "Solar power, sealed electronics packaging, thermal management, ballast, and single-point mooring concepts.",
    ])
    add_heading(doc, "6.2 Explicitly Outside Phase 1", 2)
    add_bullets(doc, [
        "Official weather, storm, typhoon, tsunami, tide, or ocean-current prediction.",
        "Water-quality prediction or pH, turbidity, salinity, and dissolved-oxygen deployment.",
        "Camera AI, computer vision, autonomous navigation, and automatic anchor deployment.",
        "Cloud-dependent AI, satellite service, production fleet management, and mobile applications.",
        "Unattended operational deployment before calibration, ingress, power, thermal, mooring, and safety tests pass.",
    ])

    add_heading(doc, "7. System Architecture", 1)
    add_body(doc, "The approved end-to-end data path is:")
    flow = doc.add_paragraph()
    flow.alignment = WD_ALIGN_PARAGRAPH.CENTER
    flow.add_run(
        "Sensors → ESP32 validation → USB/UART telemetry → Orange Pi edge service → "
        "SQLite → Wave processing → AI prediction → Explainable AI → REST API → Dashboard"
    ).bold = True
    add_table(doc, ["Layer", "Primary responsibility"], [
        ("Sensing", "Acquire motion, pressure, GPS, wind, power, solar, and enclosure-temperature evidence."),
        ("ESP32", "Time-sensitive acquisition, diagnostics, basic validation, health state, and telemetry framing."),
        ("Edge host", "Ingestion, secondary validation, SQLite persistence, wave processing, alerts, AI, XAI, APIs, and dashboard hosting."),
        ("Dashboard", "Present current state, source labels, histories, system health, alerts, predictions, and limitations."),
    ], widths=[1.4, 5.4])

    add_heading(doc, "8. Mechanical Architecture — Revision 5", 1)
    add_bullets(doc, [
        "Approximately 650 mm HDPE main float with a commercial marine profile.",
        "Rounded/tapered underwater keel to improve traditional single-body stability and reduce exposed appendages.",
        "Low adjustable ballast to lower the center of gravity and support self-righting behavior.",
        "Single-point mooring and anchor connection for controlled movement.",
        "Main buoy frame tied to the lower structural ring through external vertical supports.",
        "Tapered marine-grade aluminum tower with front maintenance gate.",
        "Two opposed 30 W solar panels with compact structural supports.",
        "Elevated rectangular marine electronics pod with front service door, raised sealing lip, dual EPDM gasket paths, compression latches, and downward cable interface.",
    ])
    add_body(doc, (
        "Fusion 360 components are parametric design and packaging references. Final wall "
        "thicknesses, fasteners, welds, buoyancy, stability, fatigue, lifting points, corrosion "
        "protection, and purchased-part clearances require engineering verification before fabrication."
    ))

    add_heading(doc, "9. Electronics Placement and Maintenance", 1)
    add_table(doc, ["Zone", "Current payload and intent"], [
        ("Lower power deck", "LiFePO4 battery/BMS, Orange Pi or Mini PC envelope, MPPT, DC conversion, protected power equipment; heavy items kept low."),
        ("Upper control deck", "ESP32, communications, sensor interfaces, distribution, and low-current control equipment."),
        ("Front service side", "Gasketed removable door aligned with the tower maintenance gate."),
        ("Rear thermal side", "Horizontal internal fans/guides, vertical sealed thermal bridge, and external eight-fin heat sink; kept opposite the front door."),
    ], widths=[1.6, 5.2])

    add_heading(doc, "10. Sealed Thermal Management", 1)
    add_body(doc, (
        "The electronics pod does not use an outside-air intake or exhaust. Two horizontal "
        "80 mm internal fans recirculate the same dry enclosure air. Lower and upper airflow "
        "guides reduce short-circuit recirculation and direct heat toward a vertical aluminum "
        "thermal bridge at the rear wall. The bridge transfers heat through a clamped, sealed "
        "interface to a rear external heat-sink base with eight projecting fins. Outside air "
        "passes only around the external fins; salt air does not enter the electronics volume."
    ))
    add_body(doc, (
        "The MCP9808 is the approved enclosure-temperature input. Fan switching must use a "
        "proper driver rather than an ESP32 GPIO load. Thermal pads, component contact, heat-"
        "sink size, sealing, galvanic isolation, salt-fog resistance, solar heat soak, and fan "
        "failure behavior require physical tests."
    ))

    add_heading(doc, "11. Hardware and Sensors", 1)
    add_table(doc, ["Function", "Selected device", "Interface / note"], [
        ("Motion/orientation", "Adafruit BNO085", "SPI; selected, physical validation pending"),
        ("Water pressure", "Blue Robotics Bar02", "I2C 0x76; shallow-wave candidate; sealing/calibration required"),
        ("Position/time", "Adafruit Ultimate GPS class", "UART2; exact purchased revision pending"),
        ("Battery monitor", "INA260", "I2C 0x40"),
        ("Solar monitor", "Second INA260", "I2C 0x41; address jumper required"),
        ("Enclosure temperature", "MCP9808", "I2C 0x18; cooling-policy input"),
        ("Wind direction", "ADS1115 + vane ladder", "I2C 0x48, A0"),
        ("Wind speed/direction", "SparkFun SEN-15901 prototype kit", "Pulse + resistor ladder; marine durability unproven"),
        ("Optional water temperature", "Sealed DS18B20", "OneWire; optional and separately validated"),
    ], widths=[1.5, 2.0, 3.3])

    add_heading(doc, "12. Power Architecture", 1)
    add_body(doc, (
        "The current baseline uses two 30 W solar panels, a LiFePO4-compatible MPPT charge "
        "controller, a 12.8 V 20 Ah LiFePO4 battery, a main fuse and disconnect, and separate "
        "regulated branches for the Orange Pi and ESP32/sensors. Sixty watts is the current "
        "supervised-test solar configuration; higher capacity remains desirable if measured "
        "loads and cloudy-day recovery require it."
    ))
    add_body(doc, (
        "The 20 Ah battery stores approximately 256 Wh nominal and about 205 Wh at an 80% "
        "usable assumption. Runtime and autonomy values remain calculations until exact parts "
        "are purchased and complete 24/72-hour endurance and recharge tests are performed."
    ))

    add_heading(doc, "13. Software and Communication Architecture", 1)
    add_table(doc, ["Component", "Current function"], [
        ("ESP32 firmware", "Captive portal, diagnostics, sensor interfaces, validity states, monitoring controls, and versioned telemetry."),
        ("Transport", "USB/UART newline-delimited JSON preferred for the prototype; local Wi-Fi/HTTP is a development alternate."),
        ("Edge service", "Simulator or hardware data source, alerts, SQLite, AI/backtesting, REST API, logs, and static dashboard serving."),
        ("Dashboard Next", "React/TypeScript interface for Overview, Wave AI, Motion, GPS, Power, System Health, Alerts, Logs, and Settings."),
    ], widths=[1.6, 5.2])
    add_body(doc, "Approved and development API routes include:")
    api = doc.add_paragraph()
    api.style = "No Spacing"
    api.add_run(
        "GET /status, /wave, /gps, /battery, /solar, /ai?horizon=5, "
        "/ai?horizon=15, /prediction?horizon=10, /logs; POST /restart, /calibrate"
    ).font.name = "Consolas"

    add_heading(doc, "14. Artificial Intelligence and Its Functions", 1)
    add_heading(doc, "14.1 Approved AI Responsibilities", 2)
    add_numbered(doc, [
        "Predict wave height five to fifteen minutes ahead.",
        "Classify the current or predicted sea condition as Calm, Moderate, or Rough.",
    ])
    add_body(doc, (
        "The AI does not predict weather, typhoons, storms, tides, ocean currents, water "
        "quality, equipment maintenance, navigation actions, or fish activity. GPS, battery, "
        "solar, and enclosure temperature support system operation but are not separate AI "
        "prediction targets."
    ))

    add_heading(doc, "14.2 How the AI Pipeline Functions", 2)
    add_numbered(doc, [
        "Acquire synchronized Bar02 pressure, BNO085 motion/orientation, timestamps, and validity states through the ESP32.",
        "Reject malformed, stale, discontinuous, missing, or uncalibrated inputs instead of fabricating a prediction.",
        "Convert validated pressure and motion evidence into a documented recent wave-height history.",
        "Create time-window features such as recent level, trend, variability, motion features, and data-quality indicators. Validated wind may be used as optional context.",
        "Run the selected lightweight model on the Orange Pi for the requested five- or fifteen-minute horizon.",
        "Apply documented output limits and compute a quality/confidence indicator from input completeness, residual variability, horizon, and recent validation behavior.",
        "Classify the resulting sea state as Calm, Moderate, or Rough using approved thresholds and hysteresis.",
        "Store the prediction, model version, timestamp, horizon, sample count, and later actual measurement for backtesting.",
        "Publish the result through GET /ai and display measured/estimated values separately from predicted values on the dashboard.",
    ])

    add_heading(doc, "14.3 Current AI Implementation", 2)
    add_body(doc, (
        "The current repository uses a damped linear-trend presentation forecast over recent "
        "wave-height history. It supports UI development, API integration, prediction storage, "
        "explainability, scenario testing, and rolling comparison with later values. It must be "
        "labeled SIMULATED or PRESENTATION MODEL where appropriate. It is not the final trained "
        "field model and its simulator performance must not be reported as field accuracy."
    ))

    add_heading(doc, "14.4 Explainable AI (XAI)", 2)
    add_body(doc, "For each ready presentation prediction, the system can expose:")
    add_bullets(doc, [
        "number and duration of valid recent samples;",
        "recent wave-height trend in meters per minute;",
        "raw projection, damping factor, and any maximum-change clamp;",
        "residual signal variability used by the confidence indicator;",
        "selected prediction horizon and model version; and",
        "the exact thresholds used for Calm, Moderate, and Rough classification.",
    ])
    add_body(doc, (
        "Confidence is a documented quality indicator, not automatically a probability. The AI "
        "is advisory research output and does not directly control buoy hardware or replace "
        "government maritime advisories."
    ))

    add_heading(doc, "14.5 Final Model Development and Evaluation", 2)
    add_numbered(doc, [
        "Collect synchronized physical pressure, IMU, reference-wave, calibration, and environmental records.",
        "Preserve chronological order and prevent future-data leakage.",
        "Establish persistence, moving-average, and simple trend/statistical baselines.",
        "Compare lightweight regression or time-series candidates suitable for the Orange Pi.",
        "Freeze one model, preprocessing schema, calibration version, and dataset identifier.",
        "Report MAE, RMSE where appropriate, bias, valid-prediction coverage, inference time, and results separately at five and fifteen minutes.",
        "Report classification accuracy, per-class precision/recall when sample size supports it, confusion matrix, and threshold/hysteresis behavior.",
        "Document missing-data behavior, model limitations, drift monitoring, and retraining controls.",
    ])

    add_heading(doc, "15. Dashboard Functions", 1)
    add_bullets(doc, [
        "Mission-control overview with explicit source and readiness labels.",
        "Wave AI page separating observed/estimated history from future prediction.",
        "Motion/orientation and 3D buoy response visualization.",
        "GPS reference point, geofence, drift context, and recovery support.",
        "Battery, solar, enclosure temperature, and verified fan-state views.",
        "Sensor availability, alerts, searchable logs, and CSV/JSON export.",
        "Normal, Rough Sea, Low Battery, Overheating, and Sensor Fault simulator scenarios.",
    ])
    add_body(doc, (
        "Simulator data must remain labeled SIMULATED. Sensor-derived wave height remains "
        "ESTIMATED until field validation, and future values remain PREDICTED. The dashboard "
        "must not display unavailable predictions as real measurements."
    ))

    add_heading(doc, "16. Research and Validation Methodology", 1)
    add_table(doc, ["Test area", "Required evidence"], [
        ("Sensor calibration", "Offsets, scale, timestamps, temperature effects, repeatability, and reference comparison."),
        ("Wave estimation", "Controlled tank/near-shore comparison against staff gauge, synchronized video, reference pressure logger, or validated wave instrument."),
        ("AI", "Chronological train/validation/test periods, baselines, 5/15-minute metrics, confidence behavior, and failure cases."),
        ("Power", "Measured load table, startup peaks, charging recovery, 24/72-hour endurance, low-voltage behavior, and fan energy use."),
        ("Mechanical", "Loaded displacement, center of gravity, freeboard, self-righting tendency, wave response, lifting and recovery."),
        ("Ingress/thermal", "IP-style spray/immersion checks, gasket compression, condensation review, solar heat soak, fan failure, and salt-fog exposure."),
        ("Mooring", "Anchor/line sizing, swivel and chafe, excursion radius, retrieval, and supervised site trial."),
        ("Dashboard", "API accuracy, source labels, responsive usability, alert behavior, export integrity, and scenario recovery."),
    ], widths=[1.4, 5.4])

    add_heading(doc, "17. Current Implementation Status", 1)
    add_table(doc, ["Subsystem", "Status", "Limitation"], [
        ("ESP32 firmware", "Buildable foundation", "Production sensor drivers and physical wiring validation incomplete."),
        ("Edge simulator/service", "Implemented", "Simulator is not ocean evidence."),
        ("SQLite/API", "Implemented prototype", "Physical serial integration and long-duration tests pending."),
        ("Dashboard Next", "Implemented development UI", "Values primarily simulator-driven today."),
        ("AI presentation model", "Implemented", "Not field-trained or safety validated."),
        ("Mechanical CAD", "Extensive parametric Revision 5", "Manufacturing and marine structural verification pending."),
        ("Power", "Calculated baseline", "Exact purchased products and endurance testing pending."),
        ("Marine trials", "Not started", "Ingress, calibration, stability, mooring, and supervised trials required."),
    ], widths=[1.7, 1.6, 3.5])

    add_heading(doc, "18. Safety, Ethics, and Claim Boundaries", 1)
    add_bullets(doc, [
        "Do not use simulator or presentation-model output for maritime safety decisions.",
        "Do not describe FALCON as a replacement for PAGASA, NAMRIA, professional wave buoys, or certified navigation aids.",
        "Do not claim AI accuracy before field-data evaluation and baseline comparison.",
        "Protect personal/location data and restrict maintenance controls to trusted local users.",
        "Fuse the battery near its positive terminal and never drive fans or loads directly from ESP32 GPIO pins.",
        "Do not deploy unattended until electrical, ingress, thermal, mechanical, mooring, calibration, endurance, and recovery tests pass.",
    ])

    add_heading(doc, "19. Significance of the Study", 1)
    add_body(doc, (
        "FALCON provides Fullbright College with an interdisciplinary platform for embedded "
        "systems, IoT, local networking, data engineering, web development, mechanical design, "
        "renewable power, and experimentally evaluated machine learning. For coastal partners, "
        "the prototype may support localized research and situational awareness after validation. "
        "For future researchers, its modular repository, explicit interfaces, test plan, and claim "
        "boundaries provide a reproducible foundation rather than an unsupported feature list."
    ))

    add_heading(doc, "20. Remaining Work", 1)
    add_numbered(doc, [
        "Purchase and photograph exact boards, connectors, fans, power products, and mechanical hardware.",
        "Bench-test each sensor and populate only validated telemetry measurements.",
        "Complete USB/UART integration and reconnect/fault testing on the Orange Pi.",
        "Update CAD envelopes using measured purchased-part dimensions and confirm service clearances.",
        "Complete power protection, endurance, charging-recovery, and thermal tests.",
        "Perform controlled pressure/IMU wave-estimation calibration with a synchronized reference.",
        "Collect sufficient chronological coastal data and evaluate candidate models against baselines.",
        "Complete ingress, salt-fog, structural, stability, mooring, retrieval, and supervised sea trials.",
        "Update the thesis Results and Discussion only with measured evidence and documented limitations.",
    ])

    add_heading(doc, "21. Conclusion", 1)
    add_body(doc, (
        "The current Project FALCON-01 is a focused Revision 5 research prototype rather than "
        "a general-purpose environmental AI buoy. Its architecture is technically coherent: "
        "the ESP32 acquires and validates data, the Orange Pi stores and processes it locally, "
        "the dashboard exposes evidence and system health, and the AI scope remains limited to "
        "short-horizon wave-height prediction and three-class sea-state classification. The "
        "project's final value will depend on disciplined calibration, baseline comparison, "
        "marine testing, and honest separation of implemented software, simulated evidence, "
        "planned hardware, and validated results."
    ))

    add_heading(doc, "Revision History", 1)
    add_table(doc, ["Version", "Date", "Change"], [
        ("Legacy", "Before 2026-08-24", "Original thesis draft with Revision 4 stabilizers, broad sensors, and unsupported AI scope."),
        ("V2 Revised", "2026-08-24", "Aligned thesis with current Revision 5 mechanical, hardware, thermal, dashboard, software, and focused AI/XAI scope."),
    ], widths=[1.0, 1.5, 4.3])

    add_heading(doc, "Internal Project References", 1)
    add_bullets(doc, [
        "docs/PROJECT_CONTEXT.md — engineering authority and approved scope.",
        "docs/CURRENT_PROJECT_DOCUMENTATION.md — consolidated implementation state.",
        "docs/AI.md — AI responsibilities, inputs, outputs, evaluation, XAI, and safety limits.",
        "docs/HARDWARE.md and docs/HARDWARE_BOM.md — selected hardware and procurement status.",
        "docs/MECHANICAL.md and fusion360/ — current CAD architecture and generator scripts.",
        "docs/DASHBOARD.md, docs/API.md, and docs/ORANGE_PI_EDGE.md — UI and edge-service contracts.",
        "docs/TEST_PLAN.md and docs/CALIBRATION_GUIDE.md — required validation evidence.",
    ])

    doc.save(OUTPUT)
    return OUTPUT


if __name__ == "__main__":
    print(build_document())
