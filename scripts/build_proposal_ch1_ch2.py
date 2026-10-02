"""Build a combined Chapters 1-2 proposal DOCX for Project FALCON.

Stdlib-only (no python-docx): a .docx is a zip of WordprocessingML parts.
Content is read from THESIS DOCUMENTATION/_extract.json, produced by the
extraction step. Figure images are copied from Chapter2_Methodology_first.docx.
"""

from __future__ import annotations

import html
import json
import re
import struct
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
THESIS = ROOT / "THESIS DOCUMENTATION"

_TXT = re.compile(r"<w:t(?:\s[^>]*)?>(.*?)</w:t>", re.S)


def _celltext(xml: str) -> str:
    xml = re.sub(r"<w:tab\b[^>]*/>", "\t", xml)
    parts = []
    for par in re.split(r"</w:p>", xml):
        t = "".join(_TXT.findall(par))
        if t.strip():
            parts.append(html.unescape(t).strip())
    return " ".join(parts)


def extract_blocks(path: Path) -> list:
    """Return ordered [{t:p|tbl,...}] blocks from a .docx."""
    z = zipfile.ZipFile(path)
    xml = z.read("word/document.xml").decode("utf-8", "ignore")
    body = re.search(r"<w:body>(.*)</w:body>", xml, re.S)
    b = body.group(1) if body else xml
    items = []
    for m in re.finditer(r"<w:(p|tbl)(?:\s[^>]*)?>.*?</w:\1>", b, re.S):
        frag = m.group(0)
        if m.group(1) == "p":
            style = re.search(r'<w:pStyle w:val="([^"]+)"', frag)
            items.append({"t": "p", "style": style.group(1) if style else "",
                          "text": _celltext(frag),
                          "img": ("<w:drawing" in frag or "<w:pict" in frag)})
        else:
            rows = []
            for tr in re.finditer(r"<w:tr(?:\s[^>]*)?>.*?</w:tr>", frag, re.S):
                rows.append([_celltext(tc.group(0)) for tc in re.finditer(r"<w:tc(?:\s[^>]*)?>.*?</w:tc>", tr.group(0), re.S)])
            items.append({"t": "tbl", "rows": rows})
    return items


CH1 = extract_blocks(THESIS / "Chapter1_Introduction_first.docx")
CH2 = extract_blocks(THESIS / "Chapter2_Methodology_first.docx")
RRL = extract_blocks(THESIS / "Project_FALCON_RRL.docx")

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
WP = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
PIC = "http://schemas.openxmlformats.org/drawingml/2006/picture"
EMU_PER_PX = 9525
MAX_W = int(6.2 * 914400)


def esc(s: str) -> str:
    return html.escape(s, quote=False)


def run(text, bold=False, italic=False, size=None) -> str:
    rpr = ""
    if bold:
        rpr += "<w:b/>"
    if italic:
        rpr += "<w:i/>"
    if size:
        rpr += f'<w:sz w:val="{size*2}"/><w:szCs w:val="{size*2}"/>'
    return f'<w:r>{("<w:rPr>"+rpr+"</w:rPr>") if rpr else ""}<w:t xml:space="preserve">{esc(text)}</w:t></w:r>'


def p(text="", style=None, bold=False, italic=False, align=None, size=None, space_after=120) -> str:
    ppr = "<w:pPr>"
    if style:
        ppr += f'<w:pStyle w:val="{style}"/>'
    ppr += f'<w:spacing w:after="{space_after}"/>'
    if align:
        ppr += f'<w:jc w:val="{align}"/>'
    ppr += "</w:pPr>"
    return f"<w:p>{ppr}{run(text, bold, italic, size) if text else ''}</w:p>"


def h1(t): return p(t, style="Heading1", space_after=200)
def h2(t): return p(t, style="Heading2", space_after=160)
def h3(t): return p(t, style="Heading3", space_after=120)
def cap(t): return p(t, italic=True, size=10, align="center", space_after=160)
def page_break(): return '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'


def table(rows) -> str:
    if not rows:
        return ""
    ncols = max(len(r) for r in rows)
    grid = "".join('<w:gridCol w:w="%d"/>' % (9360 // ncols) for _ in range(ncols))
    borders = "<w:tblBorders>" + "".join(
        f'<w:{e} w:val="single" w:sz="6" w:space="0" w:color="9CA3AF"/>'
        for e in ("top", "left", "bottom", "right", "insideH", "insideV")
    ) + "</w:tblBorders>"
    out = ['<w:tbl><w:tblPr><w:tblW w:w="9360" w:type="dxa"/>' + borders + "</w:tblPr>"]
    out.append(f"<w:tblGrid>{grid}</w:tblGrid>")
    for ri, row in enumerate(rows):
        out.append("<w:tr>")
        for ci in range(ncols):
            cell = row[ci] if ci < len(row) else ""
            shd = '<w:shd w:val="clear" w:fill="EAF3F6"/>' if ri == 0 else ""
            out.append(
                "<w:tc><w:tcPr>" + shd
                + '<w:tcMar><w:top w:w="60" w:type="dxa"/><w:left w:w="90" w:type="dxa"/>'
                + '<w:bottom w:w="60" w:type="dxa"/><w:right w:w="90" w:type="dxa"/></w:tcMar>'
                + "</w:tcPr>" + p(cell, bold=(ri == 0), size=10, space_after=0) + "</w:tc>"
            )
        out.append("</w:tr>")
    out.append("</w:tbl>")
    return "".join(out)


def fix_rrl(text: str) -> str:
    rep = [
        (r"ESP32[–-]\s*Orange Pi or Raspberry Pi architecture", "ESP32 buoy with a shore-based Bay Station architecture"),
        (r"ESP32[–-]\s*Orange Pi architecture", "ESP32 buoy with a shore-based Bay Station architecture"),
        (r"ESP32\s*[–-]\s*Orange Pi", "ESP32 buoy and shore-based Bay Station"),
        (r"Orange Pi architecture", "Bay Station architecture"),
        (r"BNO085-class inertial measurement unit", "inertial measurement unit (excluded from the Phase 1 scope; retained as background only)"),
        (r"BNO085", "inertial measurement unit"),
    ]
    for a, b in rep:
        text = re.sub(a, b, text)
    return text


body = []

# ---------------- Title block
body.append(p("PROJECT FALCON", style="Title", align="center", size=22))
body.append(p(
    "Design and Development of a Solar-Powered Smart Coastal Observation Buoy with a "
    "Shore-Based Bay Station for Pressure-Derived Wave Monitoring and AI-Assisted "
    "Short-Term Prediction", align="center", bold=True, size=13))
body.append(p("A Capstone Proposal — Chapters 1 and 2", align="center", italic=True, size=12))
body.append(p("Project FALCON Research Group", align="center", size=11))
body.append(p("Bachelor of Science in Information Technology, Fullbright College", align="center", size=11))
body.append(p("October 2026 — proposal stage; hardware integration and field validation pending", align="center", size=10))
body.append(page_break())

# ================================================= CHAPTER 1
body.append(h1("CHAPTER 1 — INTRODUCTION"))
body.append(h2("1.1 Background of the Study"))
body.append(p(CH1[5]["text"]))
body.append(p(CH1[6]["text"], italic=True, size=10))
body.append(h3("1.1.1 International Context"))
body.append(p(CH1[8]["text"])); body.append(p(CH1[9]["text"]))
body.append(h3("1.1.2 National Context"))
body.append(p(CH1[11]["text"])); body.append(p(CH1[12]["text"]))
body.append(h3("1.1.3 Local Context"))
body.append(p(CH1[14]["text"])); body.append(p(CH1[15]["text"]))

body.append(h2("1.2 Review of Related Literature"))
body.append(p("This section synthesizes related literature thematically. Full discussion and the "
               "complete reference list appear in the References section at the end of this document."))
rrl_sections = [
    (16, 19, "1.2.1 Low-Cost and Autonomous Marine Monitoring Platforms"),
    (20, 24, "1.2.2 Motion-Based and Pressure-Assisted Wave Measurement"),
    (25, 28, "1.2.3 Solar Energy, Edge Computing, and Data Quality"),
    (29, 32, "1.2.4 Coastal Communications and Position Monitoring"),
    (33, 38, "1.2.5 Short-Horizon Wave Prediction and Explainability"),
    (39, 42, "1.2.6 Philippine and Palawan Context"),
]
for start, end, title in rrl_sections:
    body.append(h3(title))
    for i in range(start, end + 1):
        if RRL[i]["t"] == "p" and RRL[i]["text"]:
            body.append(p(fix_rrl(RRL[i]["text"])))

body.append(h2("1.3 Review of Related Studies"))
body.append(p(CH1[25]["text"]))
body.append(cap(CH1[26]["text"]))
body.append(table(CH1[27]["rows"]))
body.append(p(CH1[28]["text"]))
body.append(p(CH1[29]["text"]))
body.append(h3("1.3.1 Synthesis and Research Gap"))
body.append(p(fix_rrl(RRL[44]["text"])))
body.append(p(fix_rrl(RRL[45]["text"])))
for i in range(46, 53):
    body.append(p("• " + fix_rrl(RRL[i]["text"]), space_after=40))
body.append(p(fix_rrl(RRL[53]["text"]), italic=True))
body.append(p(fix_rrl(RRL[71]["text"])))

body.append(h2("1.4 Theoretical and Conceptual Framework"))
body.append(p(CH1[31]["text"]))
body.append(p(CH1[32]["text"], italic=True))
body.append(p(CH1[33]["text"]))
body.append(h2("1.5 Significance of the Study"))
for i in range(35, 39):
    body.append(p(CH1[i]["text"]))
body.append(h2("1.6 Statement of the Problem"))
body.append(p(CH1[40]["text"])); body.append(p(CH1[41]["text"]))
for i in range(42, 48):
    body.append(p(CH1[i]["text"], space_after=60))
body.append(p(CH1[48]["text"]))
body.append(h2("1.7 Scope and Delimitations; Definition of Terms"))
body.append(p("Scope and Delimitations", bold=True))
body.append(p(CH1[52]["text"]))
body.append(p("Definition of Operational Terms", bold=True))
for i in range(54, 62):
    body.append(p(CH1[i]["text"], space_after=60))

body.append(page_break())

# ================================================= CHAPTER 2 (iterate ALL blocks)
body.append(h1("CHAPTER 2 — METHODOLOGY"))
CH2_IMG = set(i for i, it in enumerate(CH2) if it.get("img"))
eval_thresholds = {
    "Pressure / wave": "Median absolute wave-height error ≤ 0.10 m or ≤ 15% of reference, whichever is larger; period error ≤ 10% for regular tests; ≥ 95% valid windows.",
    "Wind": "Mean error ≤ max(1.0 km/h, 10% of reference); all eight principal directions classified correctly.",
    "LoRa / backhaul": "≥ 99% of test records received after planned outages; no duplicate records; reconnect in ≥ 29 of 30 cycles.",
    "Power": "Measured margin meets deployment target under measured load; autonomy and reduced-sun recovery verified.",
    "Security": "No more than one false tamper alarm in a 24-hour supervised representative-motion test.",
    "Dashboard": "At least 5 representative users; ≥ 80% complete each task correctly on the first attempt.",
    "AI": "Held-out MAE improves on the persistence baseline by an adviser-approved margin.",
}
for i, it in enumerate(CH2):
    if it["t"] == "tbl":
        rows = [r[:] for r in it["rows"]]
        if rows and rows[0][:2] == ["Area", "Primary metrics / evidence"]:
            for r in rows[1:]:
                if r and r[0] in eval_thresholds:
                    r[2] = eval_thresholds[r[0]]
        body.append(table(rows))
        continue
    txt = it["text"]; style = it.get("style", "")
    if not txt and not it.get("img"):
        continue
    if style == "Heading1":
        continue  # replaced by our own CHAPTER 2 heading
    if style == "Heading2":
        body.append(h2(txt)); continue
    if it.get("img"):
        continue  # images inserted after captions below
    if re.match(r"^Figure \d+\.", txt):
        body.append(cap(txt)); continue
    if re.match(r"^Table \d+\.", txt):
        body.append(cap(txt)); continue
    # apply content fixes
    if i == 2:
        body.append(p(txt))
        body.append(p("The research follows an established design-and-development and mixed-methods "
                      "orientation (Creswell & Creswell, 2023; Richey & Klein, 2007), combining iterative "
                      "artifact development with quantitative measurement and qualitative usability feedback."))
        continue
    if i == 22:
        body.append(p(txt + " For this study the independent references are (a) a measured water-column "
                      "depth series using a rigid scale and a reference pressure source for the pressure "
                      "channel, and (b) a reference anemometer and compass for the wind channel. Where a "
                      "certified reference is unavailable, the water-column method and its stated uncertainty "
                      "are reported instead, and no accuracy claim is made."))
        continue
    if i == 62:
        body.append(p(txt + " The study complies with the Philippine Data Privacy Act of 2012 (Republic "
                      "Act No. 10173), collecting only the minimum necessary information, obtaining informed "
                      "consent, and applying reasonable organizational and technical safeguards to personal "
                      "data; any human-participant activity is subject to adviser and institutional ethics review."))
        continue
    body.append(p(txt))

# ---------------- Editorial notes
body.append(page_break())
body.append(h1("EDITORIAL NOTES (remove before submission)"))
body.append(p("1. Methodological framework: confirm with the adviser that the cited framework "
              "(Creswell & Creswell, 2023; Richey & Klein, 2007) is the expected model."))
body.append(p("2. These in-text citations still have no verified source and must be added or removed: "
              "Bekiryazıcı et al. (2025); Chan et al. (2026); Meulé et al. (2024); Mohammadi et al. (2024); "
              "Rojas et al. (2025); Suwardiyanto et al. (2024); Wiranata & Widodo (2026)."))
body.append(p("3. Embedded RRL text: outdated Orange Pi and BNO085 references were corrected to the current "
              "ESP32 + shore Bay Station baseline; review the embedded literature section once more."))
body.append(p("4. Section 1.4 still needs its IPO figure; Chapter 2 figures were carried over from the source."))

# ---------------- References
body.append(page_break())
body.append(h1("REFERENCES"))
REFS = [
    "Ardhuin, F., Stopa, J. E., Chapron, B., Collard, F., Husson, R., Jensen, R. E., Johannessen, J., Mouche, A., Passaro, M., Quartly, G. D., Swail, V., & Young, I. (2019). Observing sea states. Frontiers in Marine Science, 6, Article 124. https://doi.org/10.3389/fmars.2019.00124",
    "Blue Robotics. (n.d.). Bar high-resolution depth/pressure sensors guide. https://bluerobotics.com/learn/bar-sensors-guide/",
    "Cho, J., Kim, M. W., Kim, Y., Park, J.-S., Lee, D.-H., Kim, Y., & Kim, J. J. (2021). Seawater battery-based wireless marine buoy system with battery degradation prediction and multiple power optimization capabilities. IEEE Access, 9, 104104-104114. https://doi.org/10.1109/ACCESS.2021.3098846",
    "Creswell, J. W., & Creswell, J. D. (2023). Research design: Qualitative, quantitative, and mixed methods approaches (6th ed.). SAGE.",
    "Dreyer, L. W., Pferscher, A., Sieve, R., Rabault, J., Jensen, A., Johnsen, E. B., & Hope, G. (2026). OLB: An open LoRa buoy for coastal water measurements [Preprint]. arXiv. https://doi.org/10.48550/arXiv.2601.05615",
    "Fan, S., Xiao, N., & Dong, S. (2020). A novel model to predict significant wave height based on long short-term memory network. Ocean Engineering, 205, Article 107298. https://doi.org/10.1016/j.oceaneng.2020.107298",
    "Grare, L., Statom, N. M., Pizzo, N., & Lenain, L. (2021). Instrumented Wave Gliders for air-sea interaction and upper ocean research. Frontiers in Marine Science, 8, Article 664728. https://doi.org/10.3389/fmars.2021.664728",
    "Holykell. (n.d.). HPT604 Type A level sensor datasheet. https://www.holykell.com/wp-content/uploads/2023/08/HPT604A-Level-sensor-Datasheet-Holykell-V26-CS-1.pdf",
    "Knight, P. J., Bird, C. O., Sinclair, A., Higham, J., & Plater, A. J. (2021). Beach deployment of a low-cost GNSS buoy for determining sea-level and wave characteristics. Geosciences, 11(12), Article 494. https://doi.org/10.3390/geosciences11120494",
    "Liu, Y., Ning, C., Zhang, Q., Yuan, G., & Li, C. (2024). Research on ocean buoy attitude prediction model based on multi-dimensional feature fusion. Frontiers in Marine Science, 11, Article 1517170. https://doi.org/10.3389/fmars.2024.1517170",
    "Martins, K., Blenkinsopp, C. E., & Zang, J. (2022). Measuring free surface elevation of shoaling waves with pressure transducers. Continental Shelf Research, 245, Article 104803. https://doi.org/10.1016/j.csr.2022.104803",
    "Mo, J., Wang, X., Huang, S., & Wang, R. (2024). Advance in significant wave height prediction: A comprehensive survey. Complex System Modeling and Simulation, 4(4), 402-439. https://doi.org/10.23919/CSMS.2024.0019",
    "National Mapping and Resource Information Authority. (2025). NAMRIA annual report 2025. https://www.namria.gov.ph/",
    "Philippine Atmospheric, Geophysical and Astronomical Services Administration. (n.d.). Marine Meteorological Service Section: Functions and services. https://www.pagasa.dost.gov.ph/",
    "Raja Ali, H. A. K., Alajuri, M. H. S., & Harahap, B. I. H. (2026). Implementation of IoT-based buoy position monitoring using GSM technology with SIM7000E module. Transactions on Maritime Science, 15(1). https://doi.org/10.7225/toms.v15.n01.002",
    "Richey, R. C., & Klein, J. D. (2007). Design and development research. Routledge.",
    "Skalvik, A. M., Saetre, C., Froysa, K.-E., Bjork, R. N., & Tengberg, A. (2023). Challenges, limitations, and measurement strategies to ensure data quality in deep-sea sensors. Frontiers in Marine Science, 10, Article 1152236. https://doi.org/10.3389/fmars.2023.1152236",
    "Song, T., Wang, J., Huo, J., Wei, W., Han, R., Xu, D., & Meng, F. (2023). Prediction of significant wave height based on EEMD and deep learning. Frontiers in Marine Science, 10, Article 1089357. https://doi.org/10.3389/fmars.2023.1089357",
    "Williams, Z., Soto Calvo, M. A., Lee, H. S., Aljber, M., & Jeong, J.-S. (2025). A low-cost autonomous multi-functional buoy for ocean currents and seawater parameter monitoring, and particle tracking. Journal of Marine Science and Engineering, 13(9), Article 1629. https://doi.org/10.3390/jmse13091629",
    "Zhang, H., Zhang, D., & Zhang, A. (2020). An innovative multifunctional buoy design for monitoring continuous environmental dynamics at Tianjin Port. IEEE Access, 8, 171820-171833. https://doi.org/10.1109/ACCESS.2020.3024020",
    "Zhou, F., Zhang, R., & Zhang, S. (2022). Measurement principle and technology of miniaturized strapdown inertial wave sensor. Frontiers in Marine Science, 9, Article 991996. https://doi.org/10.3389/fmars.2022.991996",
]
for r in sorted(REFS, key=lambda s: s.lower()):
    body.append(p(r, space_after=100))

# ---------------- figure extraction (Chapter 2)
src = zipfile.ZipFile(THESIS / "Chapter2_Methodology_first.docx")
docxml = src.read("word/document.xml").decode("utf-8", "ignore")
rels = src.read("word/_rels/document.xml.rels").decode("utf-8", "ignore")
rel_map = dict(re.findall(r'Id="(rId\d+)"[^>]*Target="([^"]+)"', rels))
img_targets = []
for m in re.finditer(r'<w:drawing\b.*?</w:drawing>', docxml, re.S):
    rid = re.search(r'r:embed="(rId\d+)"', m.group(0))
    if rid and rid.group(1) in rel_map:
        tgt = rel_map[rid.group(1)]
        img_targets.append("word/" + tgt.replace("word/", "").lstrip("/"))


def png_size(b):
    if b[:8] == b"\x89PNG\r\n\x1a\n":
        return struct.unpack(">II", b[16:24])
    return (600, 400)


rel_xml = ['<Relationship Id="rIdStyles" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>']
media_parts = {}
final = []
img_i = 0
for el in body:
    visible = re.sub(r"<[^>]+>", "", el).strip()
    if re.match(r"^Figure \d+\.", visible) and img_i < len(img_targets):
        data = src.read(img_targets[img_i])
        fname = f"figure{img_i+1}.png"
        media_parts[f"word/media/{fname}"] = data
        wpx, hpx = png_size(data)
        cx, cy = wpx * EMU_PER_PX, hpx * EMU_PER_PX
        if cx > MAX_W:
            cy = int(cy * MAX_W / cx); cx = MAX_W
        rid = f"rIdImg{img_i+1}"
        rel_xml.append(f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/{fname}"/>')
        final.append(
            "<w:p><w:pPr><w:jc w:val=\"center\"/></w:pPr><w:r><w:drawing>"
            f'<wp:inline distT="0" distB="0" distL="0" distR="0">'
            f'<wp:extent cx="{cx}" cy="{cy}"/><wp:docPr id="{img_i+1}" name="Figure {img_i+1}"/>'
            f'<a:graphic xmlns:a="{A}"><a:graphicData uri="{PIC}">'
            f'<pic:pic xmlns:pic="{PIC}"><pic:nvPicPr><pic:cNvPr id="{img_i+1}" name="{fname}"/><pic:cNvPicPr/></pic:nvPicPr>'
            f'<pic:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
            f'<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>'
            f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic>'
            f"</a:graphicData></a:graphic></wp:inline></w:drawing></w:r></w:p>"
        )
        img_i += 1
    final.append(el)
body = final

# ---------------- package
sect = ('<w:sectPr><w:pgSz w:w="12240" w:h="15840"/>'
        '<w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" w:header="720" w:footer="720" w:gutter="0"/>'
        "</w:sectPr>")
document_xml = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                f'<w:document xmlns:w="{W}" xmlns:r="{R}" xmlns:wp="{WP}" xmlns:a="{A}" xmlns:pic="{PIC}">'
                "<w:body>" + "".join(body) + sect + "</w:body></w:document>")

STYLES = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
          f'<w:styles xmlns:w="{W}">'
          "<w:docDefaults><w:rPrDefault><w:rPr>"
          '<w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/><w:sz w:val="22"/><w:szCs w:val="22"/>'
          "</w:rPr></w:rPrDefault><w:pPrDefault/></w:docDefaults>"
          '<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/>'
          '<w:pPr><w:spacing w:after="120" w:line="276" w:lineRule="auto"/></w:pPr></w:style>'
          '<w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/>'
          '<w:pPr><w:spacing w:after="160"/></w:pPr><w:rPr><w:b/></w:rPr></w:style>'
          '<w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/>'
          '<w:pPr><w:spacing w:before="240" w:after="160"/><w:outlineLvl w:val="0"/></w:pPr>'
          '<w:rPr><w:b/><w:sz w:val="32"/><w:color w:val="12304A"/></w:rPr></w:style>'
          '<w:style w:type="paragraph" w:styleId="Heading2"><w:name w:val="heading 2"/>'
          '<w:pPr><w:spacing w:before="200" w:after="120"/><w:outlineLvl w:val="1"/></w:pPr>'
          '<w:rPr><w:b/><w:sz w:val="26"/><w:color w:val="0F766E"/></w:rPr></w:style>'
          '<w:style w:type="paragraph" w:styleId="Heading3"><w:name w:val="heading 3"/>'
          '<w:pPr><w:spacing w:before="160" w:after="100"/><w:outlineLvl w:val="2"/></w:pPr>'
          '<w:rPr><w:b/><w:sz w:val="23"/><w:color w:val="1F2937"/></w:rPr></w:style>'
          "</w:styles>")

CONTENT_TYPES = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                 '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                 '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
                 '<Default Extension="xml" ContentType="application/xml"/>'
                 '<Default Extension="png" ContentType="image/png"/>'
                 '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
                 '<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>'
                 '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>'
                 '<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>'
                 "</Types>")

ROOT_RELS = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
             '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
             '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
             '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>'
             '<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>'
             "</Relationships>")

DOC_RELS = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            + "".join(rel_xml) + "</Relationships>")

CORE = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
        'xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" '
        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
        "<dc:title>Project FALCON — Proposal Chapters 1 and 2</dc:title>"
        "<dc:creator>Project FALCON Research Group</dc:creator>"
        '<dcterms:created xsi:type="dcterms:W3CDTF">2026-10-02T00:00:00Z</dcterms:created>'
        "</cp:coreProperties>")

APP = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
       '<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties">'
       "<Application>Freebuff</Application></Properties>")

OUT = THESIS / "Project_FALCON_Proposal_Ch1-2.docx"
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("[Content_Types].xml", CONTENT_TYPES)
    z.writestr("_rels/.rels", ROOT_RELS)
    z.writestr("word/document.xml", document_xml)
    z.writestr("word/styles.xml", STYLES)
    z.writestr("word/_rels/document.xml.rels", DOC_RELS)
    z.writestr("docProps/core.xml", CORE)
    z.writestr("docProps/app.xml", APP)
    for name, data in media_parts.items():
        z.writestr(name, data)

print(f"Wrote {OUT}")
print(f"size={OUT.stat().st_size} bytes, images={len(media_parts)}, refs={len(REFS)}, body_elements={len(body)}")
