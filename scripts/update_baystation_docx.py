"""Apply adviser/Bay-Station consistency corrections to BayStation.docx.

Uses only the Python standard library so it can run on the Linux Mint project
machine without python-docx. The original package structure and embedded figures
are preserved.
"""

from __future__ import annotations

import shutil
import tempfile
import zipfile
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
