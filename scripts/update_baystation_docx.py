"""Apply adviser/Bay-Station consistency corrections to BayStation.docx.

Uses only the Python standard library so it can run on the Linux Mint project
machine without python-docx. The original package structure and embedded figures
are preserved.
"""

from __future__ import annotations

import shutil
import tempfile
import zipfile
import re
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
DOCX = ROOT / "THESIS DOCUMENTATION" / "BayStation.docx"
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
DC = "{http://purl.org/dc/elements/1.1/}"
CP = "{http://schemas.openxmlformats.org/package/2006/metadata/core-properties}"
DCTERMS = "{http://purl.org/dc/terms/}"


REPLACEMENTS = {
    "LTE/cellular primary data telemetry with optional LoRa fallback":
        "LoRa primary buoy telemetry to the barangay-hall Bay Station with SIM/4G/5G Internet backhaul",
    "LTE/cellular primary or LoRa fallback":
        "LoRa primary buoy telemetry with SIM/4G/5G Bay Station Internet backhaul",
    "The deployed path attempts LTE/cellular first when a supported network is available.":
        "The buoy transmits over LoRa to the barangay-hall Bay Station. The Bay Station uses SIM/4G/5G as its Internet backhaul for cloud upload and authorized remote access.",
    "The ESP32 attempts LTE first, then a verified shore LoRa gateway; if both links are unavailable, it continues sensing/security and buffers telemetry for retransmission after reconnection.":
        "The ESP32 transmits over LoRa to the verified barangay-hall gateway; if the LoRa path is unavailable, it continues sensing/security and buffers telemetry for retransmission after reconnection.",
    "The exact LTE modem, optional LoRa module/gateway, protocols, and network providers remain subject to component and site-coverage selection.":
        "The exact LoRa module/gateway, SIM/4G/5G Bay Station modem/provider, cloud endpoint, protocols, and site-coverage selection remain subject to approval.",
    "LTE/cellular + AI PREDICTION ARCHITECTURE":
        "LORA PRIMARY + BAY STATION INTERNET BACKHAUL + AI PREDICTION ARCHITECTURE",
    "LTE/cellular telemetry hardware with an optional LoRa fallback radio":
        "LoRa telemetry hardware; SIM/4G/5G Internet is provided at the shore Bay Station",
    "cellular telemetry":
        "LoRa telemetry with Bay Station Internet backhaul",
    "cellular telemetry;":
        "LoRa buoy telemetry with Bay Station Internet backhaul;",
    "cellular telemetry; the Bay Station":
        "LoRa buoy telemetry to the Bay Station; the Bay Station",
    "LTE/cellular modem and optional LoRa gateway integration":
        "LoRa buoy radio and Bay Station SIM/4G/5G backhaul integration",
    "LTE modem, optional LoRa fallback, optional LoRa radio/gateway, and communication interfaces":
        "LoRa radio/gateway, Bay Station SIM/4G/5G modem, cloud endpoint, and communication interfaces",
    "LTE/cellular telemetry hardware":
        "LTE/cellular telemetry hardware with an optional LoRa fallback radio",
    "LTE/cellular data telemetry":
        "LTE/cellular primary data telemetry with optional LoRa fallback",
    "The exact final mini PC and cellular modem are subject to component approval.":
           "The exact final mini PC, LTE modem and optional LoRa fallback, optional LoRa radio/gateway, and communication interfaces are subject to component approval.",
    "The ESP32 continues sensing and security if cellular connectivity or the Bay Station is unavailable.":
        "The ESP32 attempts LTE first, then a verified shore LoRa gateway; if both links are unavailable, it continues sensing/security and buffers telemetry for retransmission after reconnection.",
    "If the cellular link is unavailable, the buoy continues sensing and security functions and retains a short-term telemetry buffer for retransmission after reconnection.":
        "The ESP32 attempts LTE first, then a verified shore LoRa gateway; if both links are unavailable, it continues sensing/security and buffers telemetry for retransmission after reconnection.",
    "The exact modem protocol and network provider remain subject to component and site-coverage selection.":
        "The exact LTE modem, optional LoRa module/gateway, protocols, and network providers remain subject to component and site-coverage selection.",
    "LTE/cellular modem integration":
        "LTE/cellular modem and optional LoRa gateway integration",
    "LTE modem":
        "LTE modem and optional LoRa fallback",
    "Cellular provider selection depends on deployment-site coverage.":
        "Cellular provider selection and optional LoRa gateway placement depend on deployment-site coverage, radio range, and line-of-sight testing.",
    "The buoy contains only the ESP32 controller, approved sensors, LTE/cellular telemetry hardware, battery/solar power subsystem, and security electronics.":
        "The buoy contains only the ESP32 controller, pressure and wind sensors, supporting GPS/power/security telemetry, LTE/cellular hardware, and the battery/solar subsystem.",
    "Many low-cost monitoring prototypes demonstrate sensors and dashboards but do not provide a complete serviceable platform that combines traceable pressure-based wave estimation, local environmental data, power autonomy, local data retention, and basic anti-theft/tamper awareness.":
        "Many low-cost monitoring prototypes demonstrate sensors and dashboards but do not provide a complete serviceable platform that combines traceable pressure-based wave estimation, wind monitoring, power autonomy, local data retention, and basic anti-theft/tamper awareness.",
    "1. Integrate pressure, GPS, wind, environmental, power, system-health, and security channels using documented interfaces and calibration states.":
        "1. Integrate pressure and wind channels using documented interfaces and calibration states, with GPS, power, timestamp, and security values retained as supporting telemetry.",
    "Phase 1 covers a single near-shore prototype, passive single-anchor mooring, ESP32-based onboard acquisition, LTE/cellular data telemetry, pressure-based estimated wave height, core/supporting environmental readings, onboard power monitoring, basic security, short-term outage buffering, and a shore-based Bay Station mini PC that hosts processing, storage, API services, the browser dashboard, alerts, and AI short-term wave-height prediction.":
        "Phase 1 covers a single near-shore prototype, passive single-anchor mooring, ESP32-based acquisition, LTE/cellular data telemetry, pressure-based estimated wave height, wind speed/direction, supporting telemetry, basic security, short-term outage buffering, and a shore-based Bay Station mini PC that hosts processing, storage, API services, the browser dashboard, alerts, and AI short-term wave-height prediction.",
    "Sealed DS18B20\nWater temperature; reference comparison required":
        "Supporting GPS/power/security telemetry\nPosition, operational state, and power context; not a primary measurement",
    "Sealed DS18B20":
        "Supporting GPS/power/security telemetry",
    "Water temperature; reference comparison required":
        "Position, operational state, and power context; not a primary measurement",
    "7.1 Water Temperature Monitoring":
        "7.1 Primary Wave and Wind Measurement",
    "FALCON includes a sealed DS18B20 supporting sensor that reports water temperature in degrees Celsius. This channel provides environmental context and does not constitute laboratory-grade water-quality analysis.":
        "FALCON's required measurement scope is limited to pressure-derived wave estimation and wind speed/direction. Water temperature and other environmental channels are excluded from Phase 1.",
    "Sealed DS18B20\nWater temperature (°C), timestamp, validity, and freshness":
        "Wind speed/direction\nPrimary wind measurement with timestamp, validity, and freshness",
    "Water temperature (°C), timestamp, validity, and freshness":
        "Wind speed/direction timestamp, validity, and freshness",
    "The dashboard displays this channel under Water. Exact model identification, sampling, freshness, validity, and reference-comparison status remain available in expanded technical details.":
        "The dashboard displays wave/pressure and wind channels as the primary measurements. Supporting telemetry remains available in expanded technical details.",
    "1. Overview: one large estimated-wave chart with a clearly labeled AI comparison line, a separate short-term prediction card, and one Station Status summary for wind, pressure, GPS security, battery, solar, and water/enclosure temperature.":
        "1. Overview: one large estimated-wave chart with a clearly labeled AI comparison line, a separate short-term prediction card, and one Station Status summary for wind, pressure, supporting GPS/security, and power telemetry.",
    "4. Complete pressure/environment/security calibration and controlled reference tests.":
        "4. Complete pressure/wind calibration and controlled reference tests, with supporting security checks.",
    "The expected output is a documented, serviceable research prototype consisting of a low-power solar buoy sensing node and a shore-based Bay Station. The buoy provides traceable coastal readings, pressure-based estimated wave height inputs, GPS/security awareness, and cellular telemetry; the Bay Station provides persistent records, processing, alerts, and a usable dashboard.":
        "The expected output is a documented, serviceable research prototype consisting of a low-power solar buoy sensing node and a shore-based Bay Station. The buoy provides pressure-derived wave estimates, wind observations, supporting GPS/security telemetry, and cellular telemetry; the Bay Station provides persistent records, processing, alerts, and a usable dashboard.",
    "3. Bench-integrate Bar02, GPS, wind, DS18B20, power/security channels, ESP32, and the selected cellular modem.":
        "3. Bench-integrate Bar02 and wind channels, then verify the supporting GPS, power, security, ESP32, and cellular telemetry interfaces.",
    "The Sensors page does not display one card per physical device. Individual devices are grouped into six user-facing categories: (1) Wave & Pressure, (2) GPS & Security, (3) Wind, (4) Water, (5) Power, and (6) System.":
        "The Sensors page does not display one card per physical device. Individual devices are grouped into three user-facing categories: (1) Wave & Pressure, (2) Wind, and (3) Supporting Telemetry.",
    "3. Sensors: six grouped user-facing cards—Wave & Pressure, GPS & Security, Wind, Water, Power, and System.":
        "3. Sensors: three grouped user-facing cards—Wave & Pressure, Wind, and Supporting Telemetry.",
    "Pressure, GPS, wind, water, power, and security sensors":
        "Pressure and wind sensors, with supporting GPS, power, and security telemetry",
    "Acquire sealed-probe water temperature with explicit validity and freshness states.":
        "Acquire pressure and wind measurements with explicit validity, calibration, and freshness states.",
    "DS18B20 reference comparison, stale/disconnect tests, and correct dashboard labels.":
        "Pressure-reference and wind-instrument comparison, stale/disconnect tests, and correct dashboard labels.",
    "V3.6 — MINI PC BAY STATION + AI PREDICTION ARCHITECTURE":
        "V3.7 — SHORE BAY STATION + LTE/CELLULAR + AI PREDICTION ARCHITECTURE",
    "Design and Development of a Solar-Powered Smart Coastal Observation Buoy with Shore-Based AI for Real-Time Coastal Monitoring and Short-Term Wave-Height Prediction":
        "Design and Development of a Solar-Powered Smart Coastal Observation Buoy with Shore-Based AI for Near-Real-Time Coastal Monitoring and Short-Term Wave-Height Prediction",
    "ControllerESP32 DevKitDeterministic sensor acquisition and serial telemetry":
        "ControllerESP32 DevKitDeterministic sensor acquisition, validation, buffering, and versioned telemetry framing",
    "Deterministic sensor acquisition and serial telemetry":
        "Deterministic sensor acquisition, validation, buffering, and versioned telemetry framing",
    "29 August 2026": "30 August 2026",
    "8. Compare results with a documented reference method and report MAE, RMSE, bias, repeatability, and limitations.":
        "8.2 Reference validation. Compare the pressure-based estimate with a time-aligned documented reference method and report MAE, RMSE, bias, repeatability, and limitations.",
    "Settings is a compact header icon. AI short-term wave-height prediction is a core Bay Station feature and is presented in the Overview through a visually separate forecast segment so users can distinguish historical/estimated values from predicted values.":
        "Settings is a compact header icon. AI short-term wave-height prediction is a core Bay Station feature. Overview uses a clearly labeled red historical AI-comparison line and a separate numeric future-prediction card so users can distinguish model output from pressure-derived estimates.",
    "1. Overview: one large estimated-wave chart plus a clearly separated short-term AI prediction segment and one Station Status summary for wind, pressure, GPS security, battery, solar, and water/enclosure temperature.":
        "1. Overview: one large estimated-wave chart with a clearly labeled AI comparison line, a separate short-term prediction card, and one Station Status summary for wind, pressure, GPS security, battery, solar, and water/enclosure temperature.",
    "The dashboard shall visually separate historical/estimated measurements from future AI predictions. Suggested convention: solid line for measured/pressure-derived history, a clear NOW marker, and dashed line for AI-predicted future values.":
        "The dashboard shall visually distinguish pressure-derived history from AI output. The approved Overview uses a muted solid line for the pressure-derived estimate, a labeled red line for historical model comparison, and a separate numeric card for the future prediction horizon.",
    "This V3.6 Mini PC Bay Station + AI revision supersedes conflicting V2, earlier V3, and onboard-computer descriptions.":
        "This V3.7 Shore Bay Station + LTE/Cellular + AI revision supersedes conflicting V2, earlier V3, and onboard-computer descriptions.",
    "The pressure sensor shall be rigidly mounted below the normal waterline at a known submerged depth on a protected fixed bracket or lower structural member. It shall not hang freely from the mooring chain or rope because uncontrolled sensor movement would add measurement noise and make installation depth uncertain.":
        "The pressure-sensor reference frame and mounting method remain an adviser approval gate. Controlled testing shall compare the approved buoy-mounted or stabilized mooring-referenced arrangement against an independent time-aligned wave reference. The sensor shall never hang freely; its depth, orientation, bracket, motion relative to the water surface, cable routing, and resulting measurement limitations must be documented.",
    "The exact final mini PC, LTE modem and optional LoRa fallback and optional LoRa fallback, optional LoRa radio/gateway, and communication interfaces are subject to component approval.":
        "The exact final mini PC, LTE modem, optional LoRa radio/gateway, and communication interfaces are subject to component approval.",
    "The exact LTE modem and optional LoRa fallback and optional LoRa fallback, optional LoRa module/gateway, protocols, and network providers remain subject to component and site-coverage selection.":
        "The exact LTE modem, optional LoRa module/gateway, protocols, and network providers remain subject to component and site-coverage selection.",
}

DUPLICATE = "Current Data uses the received estimate; Calm, Moderate, Rough, and Pressure Offline are clearly labeled local presentation presets that never modify stored or live telemetry."


def paragraph_text(paragraph: ET.Element) -> str:
    return "".join(node.text or "" for node in paragraph.iter(W + "t"))


def set_paragraph_text(paragraph: ET.Element, text: str) -> None:
    texts = list(paragraph.iter(W + "t"))
    if not texts:
        run = ET.SubElement(paragraph, W + "r")
        texts = [ET.SubElement(run, W + "t")]
    texts[0].text = text
    for node in texts[1:]:
        node.text = ""


def set_multiline_paragraph(paragraph: ET.Element, lines: list[str]) -> None:
    properties = paragraph.find(W + "pPr")
    for child in list(paragraph):
        if child is not properties:
            paragraph.remove(child)
    run = ET.SubElement(paragraph, W + "r")
    for index, line in enumerate(lines):
        if index:
            ET.SubElement(run, W + "br")
        ET.SubElement(run, W + "t").text = line


def update_document(xml: bytes) -> bytes:
    root = ET.fromstring(xml)
    for paragraph in root.iter(W + "p"):
        text = paragraph_text(paragraph)
        if text.startswith("V3.7 — SHORE BAY STATION") and "Undergraduate Thesis Documentation" in text:
            set_multiline_paragraph(paragraph, [
                "V3.7 — SHORE BAY STATION + LTE/CELLULAR + AI PREDICTION ARCHITECTURE",
                "Undergraduate Thesis Documentation",
                "30 August 2026",
            ])
            continue
        updated = text
        for old, new in REPLACEMENTS.items():
            if old in updated:
                updated = updated.replace(old, new)
        updated = re.sub(
            r"optional LoRa fallback(?: and optional LoRa fallback)+, optional LoRa module/gateway",
            "optional LoRa fallback, optional LoRa module/gateway",
            updated,
        )
        updated = re.sub(
            r"LTE modem(?: and optional LoRa fallback)+, optional LoRa (radio/gateway|module/gateway)",
            r"LTE modem, optional LoRa \1",
            updated,
        )
        if updated.count(DUPLICATE) > 1:
            updated = updated.replace(DUPLICATE + " " + DUPLICATE + " " + DUPLICATE, DUPLICATE)
            while updated.count(DUPLICATE) > 1:
                first = updated.find(DUPLICATE)
                second = updated.find(DUPLICATE, first + len(DUPLICATE))
                updated = updated[:second] + updated[second + len(DUPLICATE):]
        if updated != text:
            if updated.startswith("V3.7 — SHORE BAY STATION") and "Undergraduate Thesis Documentation" in updated:
                set_multiline_paragraph(paragraph, [
                    "V3.7 — SHORE BAY STATION + LTE/CELLULAR + AI PREDICTION ARCHITECTURE",
                    "Undergraduate Thesis Documentation",
                    "30 August 2026",
                ])
            else:
                set_paragraph_text(paragraph, updated.strip())
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def update_core(xml: bytes) -> bytes:
    root = ET.fromstring(xml)
    values = {
        DC + "title": "Project FALCON-01 — Bay Station V3.7 Documentation",
        DC + "subject": "Adviser-aligned shore Bay Station, LTE/cellular, pressure-wave, and AI architecture",
        DC + "description": "Canonical V3.7 Bay Station documentation aligned with repository master context v7.0.",
        CP + "revision": "22",
        DCTERMS + "modified": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    }
    for tag, value in values.items():
        node = root.find(tag)
        if node is None:
            node = ET.SubElement(root, tag)
        node.text = value
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def main() -> None:
    if not DOCX.exists():
        raise SystemExit(f"Missing {DOCX}")
    with tempfile.TemporaryDirectory(prefix="falcon-baystation-") as directory:
        output = Path(directory) / DOCX.name
        with zipfile.ZipFile(DOCX, "r") as source, zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as target:
            for item in source.infolist():
                payload = source.read(item.filename)
                if item.filename == "word/document.xml":
                    payload = update_document(payload)
                elif item.filename == "docProps/core.xml":
                    payload = update_core(payload)
                target.writestr(item, payload)
        shutil.copy2(output, DOCX)
    print(f"Updated {DOCX}")


if __name__ == "__main__":
    main()
