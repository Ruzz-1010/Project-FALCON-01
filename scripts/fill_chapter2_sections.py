#!/usr/bin/env python3
"""Fill the empty Chapter 2 sections of Project_FALCON_Chapters_1_and_2_Final.docx.

Sections filled (per the adviser to-do note in
``THESIS DOCUMENTATION/Mga-Gagaawin-mo-Correa.docx``):

  2.2 additions : conceptual framework, system overview, system design and
                  architecture (hardware block diagram), software architecture
                  diagram, hardware-software integration diagram, system flow
                  chart, testing-rubric cross reference
  2.3           : Data Collection Methods        (was "Lagyan mo to")
  2.4           : Software and Tools Used        (was "Lagyan mo to")
  2.5           : Development Procedures         (was "Lagyan mo to")
  2.6           : Testing and Evaluation         (was "Lagyan mo to")

The script is idempotent: it only writes into a section whose body is still the
placeholder line or is otherwise empty. Running it twice will not duplicate text.

Wording follows docs/REVISION_2026-10-10.md: everything physical is stated as
proposed, planned, estimated, pending, or to be validated. Nothing is described
as field-deployed or production-ready.
"""

from __future__ import annotations

import sys
from pathlib import Path

import docx
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.text.paragraph import Paragraph

ROOT = Path(__file__).resolve().parents[1]
DOCX = ROOT / "THESIS DOCUMENTATION" / "Project_FALCON_Chapters_1_and_2_Final.docx"

PLACEHOLDER = "lagyan mo to"
ARIAL = "Arial"

# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------


def para_by_text(doc, needle: str, start: int = 0) -> Paragraph | None:
    for p in doc.paragraphs[start:]:
        if p.text.strip().lower().startswith(needle.lower()):
            return p
    return None


def body_is_empty(par: Paragraph) -> bool:
    """True when the paragraph right after a heading is a placeholder or nothing."""
    nxt = next_sibling_par(par)
    if nxt is None:
        return True
    text = nxt.text.strip().lower()
    return not text or text == PLACEHOLDER


def next_sibling_par(par: Paragraph) -> Paragraph | None:
    el = par._p.getnext()
    while el is not None and el.tag.endswith("}p"):
        return Paragraph(el, par._parent)
    return None


def drop(par: Paragraph) -> None:
    par._p.getparent().remove(par._p)


def set_style(par: Paragraph, style: str) -> Paragraph:
    par.style = style
    for run in par.runs:
        run.font.name = ARIAL
    return par


def new_par_after(anchor, text="", style="Normal", align=None, bold=False):
    """Insert a paragraph directly after ``anchor`` and return it."""
    p = OxmlElement("w:p")
    anchor._p.addnext(p)
    par = Paragraph(p, anchor._parent)
    par.style = style
    if align is not None:
        par.alignment = align
    if text:
        run = par.add_run(text)
        run.font.name = ARIAL
        if bold:
            run.bold = True
    return par


def emit(doc, anchor, blocks):
    """Insert a list of blocks after ``anchor``, chaining so order is preserved."""
    for block in blocks:
        kind = block[0]
        if kind == "p":
            _, text, style, align, bold = block
            anchor = new_par_after(anchor, text, style, align, bold)
        elif kind == "fig":
            anchor = new_par_after(
                anchor, block[1], "Normal", WD_ALIGN_PARAGRAPH.CENTER, False
            )
        elif kind == "tbl":
            _, headers, rows = block
            table = doc.add_table(rows=1, cols=len(headers))
            try:
                table.style = "Table Grid"
            except KeyError:
                pass
            table.alignment = WD_TABLE_ALIGNMENT.CENTER
            for i, h in enumerate(headers):
                cell = table.rows[0].cells[i]
                cell.text = ""
                run = cell.paragraphs[0].add_run(h)
                run.font.name = ARIAL
                run.bold = True
            for row in rows:
                cells = table.add_row().cells
                for i, val in enumerate(row):
                    cells[i].text = ""
                    run = cells[i].paragraphs[0].add_run(str(val))
                    run.font.name = ARIAL
            anchor._p.addnext(table._tbl)
            anchor = new_par_after(anchor, "", "Normal")
    return anchor


def P(text, style="Normal", align=None, bold=False):
    return ("p", text, style, align, bold)


def FIG(caption):
    return ("fig", caption, None, None, False)


def TBL(headers, rows):
    return ("tbl", headers, rows)


# --------------------------------------------------------------------------
# 2.2 additions — the deliverables the adviser listed but that were missing
# --------------------------------------------------------------------------

BLOCKS_22 = [
    P("2.2.3 Conceptual Framework of the Design", "Heading 3"),
    P(
        "The design of Project FALCON follows a systems input-process-output model. "
        "The input stage consists of the physical quantities observed by the buoy: "
        "water pressure, wind speed and wind direction, GPS position, and the "
        "battery and solar power state. The process stage is carried out by the "
        "ESP32 controller, which acquires each channel, checks it against expected "
        "ranges, establishes short-window baselines, detects when a validated "
        "threshold is crossed, buffers records locally, and schedules what is sent "
        "and when. The output stage is the cloud service, which stores the received "
        "records, estimates wave height from the pressure channel, presents the "
        "results on the dashboard, raises alerts, and produces the short-term "
        "wave-height estimate. A feedback path returns configuration, calibration "
        "values, and revision decisions to the input and process stages so that the "
        "next cycle operates against updated limits. Figure 1.1 in Chapter 1 presents "
        "the same model as a conceptual paradigm; this section describes how that "
        "paradigm is realized as a physical and software structure."
    ),
    P(
        "The framework deliberately separates sensing from transmission. Sensing is "
        "continuous and local, while transmission is conditional. This separation is "
        "what allows the buoy to use a smaller battery and a smaller solar array than "
        "a continuously reporting station would require, and it is the main reason the "
        "proposed unit can stay within the low-cost target band."
    ),
    P("2.2.4 System Overview", "Heading 3"),
    P(
        "Project FALCON is proposed as a compact, solar-powered coastal observation "
        "buoy. Its body carries a float, a sealed electronics enclosure, a mast that "
        "supports the solar panel and the wind sensor, a protected stilling tube that "
        "shields the water-pressure sensor from direct impact, and a mooring arrangement "
        "with chain and anchor. The electronics enclosure is a sealed, low-profile "
        "volume that houses the ESP32 controller, the power regulation and charge "
        "control stage, the battery, the GPS antenna, the internet antenna, and the "
        "local data buffer. No single-board computer, mini computer, or gateway is "
        "installed on or powered by the buoy."
    ),
    P(
        "Functionally the system is organized into four layers: the Data Acquisition "
        "Layer, the Communication Layer, the Cloud Application and Data Layer, and the "
        "Presentation Layer. A solar and battery subsystem supplies the first layer. "
        "The buoy communicates with the cloud over Wi-Fi during laboratory and "
        "near-shore work and over a 4G/LTE module during a remote trial. The LTE path "
        "connects directly to the Internet and to the cloud endpoint; the design does "
        "not depend on a shore-side relay station, and LoRa remains only an optional "
        "fallback if Internet access is not viable at a given site. The physical layout, "
        "the software decomposition, and the interface between them are shown in "
        "Figures 2.3, 2.4, and 2.5."
    ),
    P("2.2.5 System Design and Architecture", "Heading 3"),
    P(
        "The hardware architecture groups the proposed equipment into four blocks: the "
        "sensing block, the controller block, the power block, and the communication "
        "block, plus the mechanical body that carries them. The sensing block holds the "
        "water-pressure transmitter with its current-loop interface, the combined "
        "anemometer and wind vane, and the GPS receiver. The controller block is the "
        "ESP32, which reads every channel, performs engineering-unit and range checks, "
        "runs event detection, and manages the local buffer. The power block consists "
        "of the solar panel, the charge controller, the battery, the fuse and protection "
        "stage, and the voltage measurement used for battery monitoring. The "
        "communication block is the ESP32 Wi-Fi interface for bench work and the "
        "4G/LTE module for a remote trial. Figure 2.3 presents this decomposition."
    ),
    FIG("Figure 2.3. Proposed Hardware Block Diagram of Project FALCON"),
    P(
        "The software architecture separates the buoy firmware from the cloud service "
        "and from the dashboard. Buoy firmware is organized around deterministic "
        "acquisition, validation, event detection, telemetry framing, buffering, and "
        "upload scheduling. The cloud service is organized around authenticated "
        "ingestion, storage, pressure processing and wave estimation, alerting, the "
        "REST API, and the optional isolated prediction task. The dashboard consumes "
        "only the API and never reads a sensor directly, so a presentation defect "
        "cannot affect acquisition. Figure 2.4 presents this decomposition."
    ),
    FIG("Figure 2.4. Proposed Software Architecture of Project FALCON"),
    P(
        "The hardware-software integration diagram in Figure 2.5 shows where each "
        "software task attaches to a physical interface. Pressure enters through the "
        "analog front end of the current-loop interface, wind speed and direction "
        "enter through their analog or pulse inputs, GPS arrives over a serial link, "
        "and battery and solar voltage arrive through the monitoring divider or monitor "
        "device. The ESP32 drives the charge-control and protection state indirectly "
        "through measurement rather than control, and it reaches the cloud through "
        "either the Wi-Fi radio or the LTE module. Every boundary shown is a selection "
        "or approval gate: the exact current-loop parts, the exact LTE board, and the "
        "cloud endpoint remain to be confirmed against datasheets and a real "
        "subscription before fabrication."
    ),
    FIG("Figure 2.5. Proposed Hardware-Software Integration Diagram"),
    P("2.2.6 System Flow Chart", "Heading 3"),
    P(
        "Figure 2.6 shows the end-to-end flow of the proposed system from the moment a "
        "physical quantity is observed to the moment a user reviews it. The sequence "
        "begins with sensing, continues through validation and baseline comparison, "
        "branches according to whether a threshold was crossed, and ends either with a "
        "scheduled summary or an immediate event packet. If the Internet path is "
        "unavailable the flow diverts to the local buffer and rejoins after "
        "reconnection. The chart also shows that live monitoring, wave estimation, and "
        "alerting continue even when the prediction task is disabled or unavailable."
    ),
    FIG("Figure 2.6. System Flow Chart of Project FALCON"),
    P(
        "Testing rubrics that apply to the whole design are stated once, in Section 2.6.3, "
        "rather than repeated here, so that each requirement, metric, and weight is "
        "defined in a single place."
    ),
]

# --------------------------------------------------------------------------
# 2.3 Data Collection Methods
# --------------------------------------------------------------------------

BLOCKS_23 = [
    P(
        "This section defines what the buoy records, how often it records it, and under "
        "what conditions a record is transmitted. Five groups of data are collected. "
        "Table 1 states the source, the collection basis, and the intended use of each "
        "group."
    ),
    TBL(
        ["Data group", "Source on the buoy", "Collection basis", "Intended use"],
        [
            [
                "Water pressure",
                "Submersible pressure transmitter through the current-loop interface",
                "Continuous local sampling at a fixed short interval; raw samples retained",
                "Primary input for pressure-derived wave-height estimation",
            ],
            [
                "Wind speed and direction",
                "Combined anemometer and wind vane, or the selected lower-cost alternative",
                "Continuous local sampling at the same fixed interval",
                "Environmental context and threshold-based alerting",
            ],
            [
                "Position and security",
                "GPS receiver over serial link",
                "Sampled at the same interval and compared against the last known position",
                "Exact position, displacement monitoring, geofence and recovery support",
            ],
            [
                "Battery and solar state",
                "Battery monitor or voltage divider on the power stage",
                "Sampled at the same interval",
                "Runtime validation, low-battery alerting, and power budget evidence",
            ],
            [
                "System and connection state",
                "Firmware health flags, sensor health, and link status",
                "Evaluated at each cycle",
                "Diagnostics, data-quality labelling, and outage reporting",
            ],
        ],
    ),
    P(
        "Collection on the buoy is continuous, but transmission is conditional. The "
        "system does not upload one record per wave, because the ocean is never still "
        "and a normal wave must never be treated as a reportable event. Instead the "
        "ESP32 compares each new reading against a short-window baseline and transmits "
        "only in three situations. First, it sends a regular one-minute summary every "
        "one to five minutes during normal operation. Second, it sends an immediate "
        "packet when water pressure, wind speed or direction, GPS displacement, buoy "
        "tilt, battery or solar status, sensor health, or connection state crosses a "
        "validated threshold. Third, it sends queued records after the Internet path is "
        "restored. Each queued record keeps its original timestamp so that the stored "
        "series remains continuous."
    ),
    P(
        "While the Wi-Fi or LTE path is unavailable, records are written to the local "
        "buffer, which is a microSD card or the ESP32 flash ring buffer depending on the "
        "selected configuration. Losing the Internet path therefore delays a record "
        "rather than destroying it. Every value carries or inherits a timestamp, a "
        "source, a quality state, and a unit; a value that cannot be produced is stored "
        "as null rather than as a zero or a guess."
    ),
    P(
        "Raw pressure samples are retained locally in addition to the derived summary "
        "values. This is intentional: the raw series is what allows the wave-height "
        "estimation method to be recalculated and compared against an independent "
        "reference later, without having to repeat the field work. The collection rules "
        "described here are the design as proposed; the interval, the thresholds, and "
        "the buffer capacity are all calibration and approval items and remain to be "
        "validated on the bench before any field trial."
    ),
]

# --------------------------------------------------------------------------
# 2.4 Software and Tools Used
# --------------------------------------------------------------------------

BLOCKS_24 = [
    P(
        "This section lists the equipment, the mechanical body, and the software used "
        "to build and operate Project FALCON. Every item is recorded together with its "
        "role so that the selection can be reviewed against the low-cost requirement. "
        "The equipment list is a proposed configuration: exact part numbers, prices, "
        "and supplier quotations remain procurement-gate items, and no item is "
        "described here as purchased, assembled, or field-verified."
    ),
    P("2.4.1 Hardware and Mechanical Body", "Heading 3"),
    P(
        "The mechanical body carries every other component and is treated as part of the "
        "hardware specification rather than as a separate subject. Its elements are the "
        "float, the sealed electronics enclosure, the mast and solar bracket, the "
        "protected stilling tube for the pressure sensor, and the mooring chain and "
        "anchor. The enclosure volume is sized to hold the controller, the power stage, "
        "the battery, the antennas, and the buffer with room for cable routing and "
        "sealing."
    ),
    TBL(
        ["Hardware element", "Proposed specification or class", "Role in the system"],
        [
            [
                "Buoy body and float",
                "Compact can or catamaran form with closed-cell flotation",
                "Provides buoyancy, carries the mast and instruments, and holds the low centre of gravity required for stability",
            ],
            [
                "Electronics enclosure",
                "Sealed low-profile housing with cable glands and a bolted hatch",
                "Protects the controller, power stage, battery, antennas, and buffer from seawater and spray",
            ],
            [
                "Controller",
                "ESP32 development board",
                "Reads every sensor channel, validates data, detects events, buffers records, and schedules uploads",
            ],
            [
                "Water-pressure sensor",
                "Holykell HPT604 Type A or an equivalent low-range submersible transmitter, vented gauge, 4-20 mA output",
                "Primary input for pressure-derived wave-height estimation",
            ],
            [
                "Pressure interface",
                "Precision shunt, RC filter, and clamp protection, or an equivalent analogue front end",
                "Converts the 4-20 mA loop into a voltage the ESP32 can read",
            ],
            [
                "Wind sensor",
                "Combined anemometer and wind vane, separate cup and vane, or the selected lower-cost alternative",
                "Measures wind speed and wind direction for monitoring and alerting",
            ],
            [
                "GPS receiver",
                "NEO-6M or a similar low-cost module",
                "Provides exact position, displacement monitoring, and recovery support",
            ],
            [
                "Solar panel",
                "Small panel sized from the measured load, mounted on a tilted bracket",
                "Recharges the battery during daylight operation",
            ],
            [
                "Charge controller and regulation",
                "PWM or MPPT charge controller with fuse and buck or boost regulation",
                "Regulates charging and protects the battery and the loads",
            ],
            [
                "Battery",
                "LiFePO4 or lithium-ion pack sized from measured modem duty",
                "Supplies the system through darkness and through LTE transmission peaks",
            ],
            [
                "Battery monitoring",
                "Battery monitor or a voltage-divider fallback",
                "Reports state of charge and supports runtime validation and low-battery alerts",
            ],
            [
                "Internet module",
                "ESP32 Wi-Fi for bench and near-shore work; A7670E, SIM7600, or equivalent 4G/LTE board with antenna and SIM for a remote trial",
                "Carries summaries and event packets directly to the cloud endpoint",
            ],
            [
                "Local buffer",
                "microSD module with an 8-32 GB card, or the ESP32 flash ring buffer",
                "Preserves records and original timestamps during an Internet outage",
            ],
            [
                "Mast, bracket, and mooring",
                "Support mast, solar bracket, chain, connector, and anchor",
                "Presents the wind sensor and panel clear of the water and holds the buoy on station",
            ],
        ],
    ),
    P("2.4.2 Back-End Software", "Heading 3"),
    P(
        "The back end performs everything that must happen between the arrival of a "
        "packet and the availability of a reading to a user. It accepts authenticated "
        "ingestion, detects stale data, filters pressure and derives wave height, logs "
        "events, stores records, exposes the REST API, and hosts the alert rules. Any "
        "prediction work is executed as an isolated task so that a slow or failed "
        "prediction can never block acquisition, storage, or the live reading."
    ),
    TBL(
        ["Back-end component", "Role"],
        [
            ["Ingestion endpoint", "Accepts authenticated summary and event packets from the buoy and rejects malformed or unauthorised frames"],
            ["Data validation", "Checks range, timestamp ordering, source, and quality state before a record is accepted into storage"],
            ["Storage", "Keeps the received series, derived wave-height values, events, alerts, and configuration history"],
            ["Pressure processing", "Applies filtering and the wave-height estimation method to the pressure channel and labels the output as an estimate"],
            ["REST API", "Serves the dashboard and other clients with grouped, timestamped readings"],
            ["Alert service", "Evaluates threshold rules and raises, clears, and records alerts with their triggering value"],
            ["Prediction service", "Optional isolated short-term wave-height estimate; disabled or unavailable state must not affect monitoring"],
        ],
    ),
    P("2.4.3 Front-End Software", "Heading 3"),
    P(
        "The front end is a responsive web dashboard with four primary pages in a fixed "
        "order: Overview, Buoy Motion, Sensors, and Logs and Alerts. Settings remains a "
        "compact header action rather than a fifth page. GPS position and security "
        "details are grouped under Sensors and summarised on Overview."
    ),
    TBL(
        ["Dashboard page", "What it presents"],
        [
            ["Overview", "Current conditions, estimated wave height, wind summary, power state, connectivity, and the short-term estimate with its state and input label"],
            ["Buoy Motion", "Visualisation of pressure-derived buoy movement as a presentation view; it does not require an inertial sensor"],
            ["Sensors", "Per-channel readings with units, source, quality state, and GPS position and security details"],
            ["Logs and Alerts", "Event history, alert history with triggering values, and connection or health records"],
        ],
    ),
    P("2.4.4 Development and Support Tools", "Heading 3"),
    TBL(
        ["Tool", "Purpose"],
        [
            ["PlatformIO or the Arduino environment", "Building, flashing, and debugging the ESP32 firmware"],
            ["C / C++ for the firmware", "Implementing acquisition, validation, event detection, buffering, and upload scheduling"],
            ["Python with a web framework", "Implementing the ingestion endpoint, validation, processing, and API"],
            ["SQLite or an equivalent database", "Storing readings, derived values, events, and configuration history"],
            ["JavaScript with a component framework", "Building the four-page dashboard"],
            ["Chart rendering library", "Rendering time-series and condition views in the dashboard"],
            ["Git", "Version control and change traceability"],
            ["Documentation and diagram tools", "Producing the figures, tables, and reports used in this study"],
            ["Serial monitor and test runner", "Bench observation of firmware behaviour and repeatable automated tests"],
        ],
    ),
]

# --------------------------------------------------------------------------
# 2.5 Development Procedures
# --------------------------------------------------------------------------

BLOCKS_25 = [
    P(
        "Development follows the staged sequence described in Section 2.1: requirements "
        "analysis, system design, system development and integration, testing and "
        "evaluation, and revision. This section states the concrete procedures carried "
        "out inside those stages for the two data paths that require the most "
        "explanation: the processing of pressure data into an estimated wave height, and "
        "the short-term prediction workflow that consumes those estimates."
    ),
    P(
        "Before any procedure is executed, the team records the configuration under test, "
        "the firmware and software version, and the instruments used. Bench procedures "
        "are carried out indoors on a stable supply; controlled-water procedures are "
        "carried out in a container or tank with a measured water column; and any "
        "near-shore activity is planned and supervised, with no deployment during severe "
        "weather, in a navigation channel, or without an approved mooring plan. Results "
        "are recorded whether they are favourable or not, and no procedure is reported "
        "as passed without a stored record."
    ),
    P("2.5.1 Pressure Data Processing Flowchart", "Heading 3"),
    P(
        "The pressure path converts a raw current-loop reading into a labelled wave-height "
        "estimate. The sequence is shown in Figure 2.7 and proceeds as follows: acquire "
        "the analogue value; convert the loop current to pressure using the calibrated "
        "span; convert pressure to a water-column height using the known fluid density; "
        "remove the sensor installation offset to obtain a depth reference; apply the "
        "selected filtering step to reduce noise without erasing wave motion; compare "
        "against the short-window baseline; derive the wave-height estimate from the "
        "variation about that baseline; attach timestamp, source, units, and quality "
        "state; and store the result as an estimate. If any check fails, the value is "
        "marked with a non-good quality state and stored as null rather than being "
        "silently replaced. The output is always labelled as an estimate, because the "
        "calibration and the comparison against an independent reference are both "
        "validation items that are not yet complete."
    ),
    FIG("Figure 2.7. Pressure Data Processing Flowchart"),
    P("2.5.2 AI Prediction Model Workflow", "Heading 3"),
    P(
        "The prediction workflow is shown in Figure 2.8. It begins with the stored series "
        "of estimated wave heights, applies a preparation step that removes non-good "
        "records and enforces a minimum history before any estimate is produced, and then "
        "produces a five-, ten-, or fifteen-minute short-term estimate together with an "
        "expected condition label and a confidence indicator. When fewer than eight valid "
        "records are available the workflow returns a collecting state instead of an "
        "estimate, so that the dashboard never presents an invented value."
    ),
    P(
        "The present implementation is a transparent damped-trend research baseline. It is "
        "implemented software, but it is not yet a trained or field-validated model and it "
        "is not an official marine forecast. Reaching a state where prediction accuracy "
        "may be reported requires calibrated live data, an explicit separation of training, "
        "validation, and test sets, comparison against the current baseline, and recorded "
        "mean absolute error, root mean squared error, and bias. Until those steps are "
        "complete, the workflow is documented as proposed and its output is presented as "
        "a research estimate with its state and input label visible."
    ),
    FIG("Figure 2.8. AI Prediction Model Workflow"),
]

# --------------------------------------------------------------------------
# 2.6 Testing and Evaluation
# --------------------------------------------------------------------------

BLOCKS_26 = [
    P(
        "Testing establishes whether the proposed system behaves as specified; evaluation "
        "converts those observations into a comparable judgement. The two are kept "
        "separate on purpose so that a passing observation and a satisfactory score are "
        "not confused with one another. All methods below are proposed methods and all "
        "acceptance values are proposed targets; none of them has been executed as a "
        "completed validation at the time of writing."
    ),
    P("2.6.1 Testing and Validation Workflow", "Heading 3"),
    P(
        "Figure 2.9 shows the ordered workflow. The configuration under test is recorded, "
        "the equipment is inspected and the enclosure is leak-checked, the sensors are "
        "calibrated or compared against a reference, the system is exercised on a bench "
        "supply, a controlled-water test is carried out with a measured water column, the "
        "communication and power paths are exercised under their own conditions, and the "
        "results are scored against the criteria in Section 2.6.3. Any failure returns the "
        "work to the design, calibration, or firmware stage and the workflow is repeated. "
        "Calibration data and verification data are kept separate so that a method is not "
        "evaluated against the same records used to tune it."
    ),
    FIG("Figure 2.9. Testing and Validation Workflow"),
    P("2.6.2 Testing Methods", "Heading 3"),
    TBL(
        ["Testing method", "What is exercised", "Record produced"],
        [
            [
                "Enclosure and leak inspection",
                "Sealing of the enclosure, cable glands, and hatch before and after immersion",
                "Inspection record and any observed water ingress",
            ],
            [
                "Static depth calibration",
                "Pressure sensor against a measured water column at known depths",
                "Calibration curve, offset, and residual error",
            ],
            [
                "Controlled stilling-tube response",
                "Response of the protected sensor mount to a known water-level change",
                "Response trace used to label the wave-height estimate",
            ],
            [
                "Wind sensor comparison",
                "Wind speed and direction against a reference anemometer and vane",
                "Comparison readings and observed deviation",
            ],
            [
                "Power endurance test",
                "Operation from the battery through a simulated dark period while transmitting",
                "Current draw, voltage trace, and achieved runtime",
            ],
            [
                "Communication test",
                "Summary and event delivery over Wi-Fi and over the LTE path, including outage and recovery",
                "Packets sent, packets received, latency, and queued-record delivery",
            ],
            [
                "Event detection test",
                "Threshold crossing, debounce, and suppression of ordinary wave movement",
                "Triggered events with triggering values and false-trigger count",
            ],
            [
                "Buffer and recovery test",
                "Local recording during an Internet outage and replay after reconnection",
                "Records preserved, original timestamps retained, and duplicates",
            ],
            [
                "Dashboard usability review",
                "Whether a reviewer can find current conditions, an alert, and a history entry",
                "Task completion observations and structured feedback",
            ],
        ],
    ),
    P("2.6.3 Evaluation Criteria and Testing Rubrics", "Heading 3"),
    P(
        "Wave-height accuracy is evaluated against an independent reference instrument. "
        "For a reference series y and an estimated series y-hat over n paired records, the "
        "metrics are:"
    ),
    P(
        "Mean Absolute Error:   MAE = (1 / n) * SUM | y(i) - y_hat(i) |"
    ),
    P(
        "Root Mean Squared Error:   RMSE = SQRT( (1 / n) * SUM ( y(i) - y_hat(i) )^2 )"
    ),
    P("Mean Bias:   MB = (1 / n) * SUM ( y(i) - y_hat(i) )"),
    P(
        "Mean Absolute Percentage Error:   MAPE = (100 / n) * SUM | y(i) - y_hat(i) | / | y(i) |"
    ),
    P(
        "Communication and data handling are evaluated with simple ratios. Data "
        "completeness is the number of expected records received divided by the number of "
        "records expected, multiplied by one hundred. Packet delivery ratio is the number "
        "of packets received divided by the number of packets sent, multiplied by one "
        "hundred. Power endurance is reported as the achieved runtime in hours against the "
        "designed runtime, together with the average system current that produced it."
    ),
    P(
        "Table 2 states the proposed evaluation metrics and the targets against which each "
        "will be judged. These targets are planning values used to organise the work; they "
        "are not measured results."
    ),
    TBL(
        ["Evaluation criterion", "Metric", "Proposed target", "Evidence required"],
        [
            [
                "Wave-height estimation accuracy",
                "MAE and RMSE against the reference instrument",
                "To be set with the adviser after the reference method is confirmed",
                "Paired reference and estimated series with both calibration and verification records",
            ],
            [
                "Estimation bias",
                "Mean bias",
                "Near zero, with the sign and magnitude reported",
                "Signed residual series over the verification set",
            ],
            [
                "Data completeness",
                "Received records / expected records * 100",
                "Not to be claimed until the collection interval is fixed",
                "Storage extracts compared against the expected schedule",
            ],
            [
                "Communication reliability",
                "Packet delivery ratio and queued-record delivery after recovery",
                "Full delivery of queued records after every simulated outage",
                "Sent and received packet logs with original timestamps",
            ],
            [
                "Event detection correctness",
                "True triggers versus false triggers",
                "No upload caused by ordinary wave movement alone",
                "Event log with triggering values and suppression records",
            ],
            [
                "Power endurance",
                "Achieved runtime against designed runtime",
                "Designed runtime met through a simulated dark period",
                "Voltage and current traces with the transmission schedule",
            ],
            [
                "Prediction usefulness",
                "MAE, RMSE, and bias against the held-out set",
                "Must outperform the damped-trend baseline before any accuracy claim",
                "Versioned evaluation record with training, validation, and test separation",
            ],
            [
                "Usability",
                "Structured task-completion feedback",
                "Reviewer completes each task without assistance",
                "Completed rubric forms and observed task outcomes",
            ],
        ],
    ),
    P(
        "Table 3 converts these criteria into a weighted scoring rubric so that a single "
        "overall judgement can be recorded for each test round. The weights are proposed "
        "and may be revised by the adviser; the score is reported alongside its "
        "underlying metric so that a total never hides a failing measurement."
    ),
    TBL(
        ["Rubric criterion", "Weight", "Scoring basis"],
        [
            ["Measurement accuracy", "30%", "Reported from the wave-height error metrics in Table 2"],
            ["Communication reliability", "20%", "Reported from packet delivery and queued-record delivery"],
            ["Power performance", "20%", "Reported from achieved runtime against designed runtime"],
            ["Data integrity and event correctness", "15%", "Reported from completeness, timestamp retention, and false-trigger count"],
            ["Usability and documentation", "15%", "Reported from the structured task-completion rubric"],
        ],
    ),
    P(
        "Each test round is recorded as a dated entry containing the configuration, the "
        "software version, the metrics obtained, the target applied, and the resulting "
        "pass, conditional, or fail status. A conditional or fail status returns the work "
        "to the relevant development stage. No test round may be reported as a field "
        "result until the enclosure, power, calibration, and communication gates have "
        "been closed on the bench and the trial plan has been approved."
    ),
]

# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------


def prev_sibling_par(par: Paragraph) -> Paragraph | None:
    el = par._p.getprevious()
    while el is not None and el.tag.endswith("}p"):
        return Paragraph(el, par._parent)
    return None


def fill_section(doc, heading_text: str, blocks, label: str) -> bool:
    heading = para_by_text(doc, heading_text)
    if heading is None:
        print(f"  [{label}] HEADING NOT FOUND: {heading_text!r}")
        return False
    if not body_is_empty(heading):
        print(f"  [{label}] already filled - skipped")
        return False
    nxt = next_sibling_par(heading)
    if nxt is not None and nxt.text.strip().lower() == PLACEHOLDER:
        drop(nxt)
    emit(doc, heading, blocks)
    print(f"  [{label}] filled ({len(blocks)} blocks)")
    return True


def main() -> int:
    if not DOCX.exists():
        print(f"missing: {DOCX}")
        return 1
    doc = docx.Document(DOCX)
    print(f"opened {DOCX.name} ({len(doc.paragraphs)} paragraphs)")

    # 2.2 additions go immediately before the 2.3 heading.
    h23 = para_by_text(doc, "2.3 Data Collection Methods")
    if h23 is None:
        print("  [2.2] 2.3 heading not found - cannot place additions")
    elif para_by_text(doc, "2.2.3 Conceptual Framework") is not None:
        print("  [2.2] already filled - skipped")
    else:
        anchor = prev_sibling_par(h23)
        if anchor is None:
            print("  [2.2] no paragraph before 2.3 heading")
        else:
            emit(doc, anchor, BLOCKS_22)
            print(f"  [2.2] filled ({len(BLOCKS_22)} blocks)")

    fill_section(doc, "2.3 Data Collection Methods", BLOCKS_23, "2.3")
    fill_section(doc, "2.4 Software and Tools Used", BLOCKS_24, "2.4")
    fill_section(doc, "2.5 Development Procedures", BLOCKS_25, "2.5")
    fill_section(doc, "2.6 Testing and Evaluation", BLOCKS_26, "2.6")

    doc.save(DOCX)
    print(f"saved {DOCX.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())



