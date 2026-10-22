#!/usr/bin/env python3
"""Structural and formatting repairs for Project_FALCON_Chapters_1_and_2_Final.docx.

Repairs applied, all identified by the Chapter 2 verification pass:

  1. Numbered section headings that were still styled ``Normal`` are promoted to
     ``Heading 2`` (x.y) or ``Heading 3`` (x.y.z) so they appear in the TOC.
  2. Chapter 1 headings that had no section number receive one
     (1.1 Background of the Study, 1.1.1 International Context, ...).
  3. Four body paragraphs that were styled ``Heading 2`` are returned to
     ``Normal``; they were polluting the heading outline.
  4. The Acknowledgment section's raw template instructions are replaced with an
     actual acknowledgement written by role, because the approval sheet still
     carries placeholder names.
  5. Figure numbering is made sequential: Figure 1 -> Figure 1.1, and the
     Figure 2.4 that appears before Figure 2.2 -> Figure 2.1.
  6. "4. Presentation Layer" is made consistent with its three sibling items.

Idempotent: every edit is guarded so a second run changes nothing.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import docx
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.text.paragraph import Paragraph

ROOT = Path(__file__).resolve().parents[1]
DOCX = ROOT / "THESIS DOCUMENTATION" / "Project_FALCON_Chapters_1_and_2_Final.docx"
ARIAL = "Arial"

PROMOTE = [
    ("1.3 Review of Related Studies", "Heading 2"),
    ("1.3.1 Local Studies", "Heading 3"),
    ("1.3.2 Foreign Studies", "Heading 3"),
    ("1.3.3 Synthesis of Gaps", "Heading 3"),
    ("1.4 Theoretical and Conceptual Framework", "Heading 2"),
    ("1.4.1 Theoretical Framework", "Heading 3"),
    ("1.4.2 Legal Basis", "Heading 3"),
    ("1.4.3 Conceptual Paradigm", "Heading 3"),
    ("1.5 Significance of the Study", "Heading 2"),
    ("1.6 Statement of the Problem", "Heading 2"),
    ("2.1.1 Design and Development Research", "Heading 3"),
    ("2.1.2 Experimental Evaluation", "Heading 3"),
    ("2.1.3 Iterative Development Methodology", "Heading 3"),
    ("2.2 System Architecture / Framework", "Heading 2"),
    ("2.2.1 System Architecture (Logical Separation)", "Heading 3"),
    ("2.2.2 Cloud Architecture (Deployment Environment)", "Heading 3"),
    ("2.3 Data Collection Methods", "Heading 2"),
    ("2.4 Software and Tools Used", "Heading 2"),
    ("2.5 Development Procedures", "Heading 2"),
    ("2.6 Testing and Evaluation", "Heading 2"),
]

RENUMBER_CH1 = [
    ("Background of the Study", "1.1 Background of the Study"),
    ("International Context", "1.1.1 International Context"),
    ("National Context", "1.1.2 National Context"),
    ("Local Context", "1.1.3 Local Context"),
]

FIGURE_RENUMBER = [
    ("Figure 1.", "Figure 1.1."),
    ("Figure 2.4. Iterative Project Development Process",
     "Figure 2.1. Iterative Project Development Process"),
]

ACK_REPLACEMENTS = [
    (
        "Begin the acknowledgment section",
        "The researchers sincerely thank their thesis adviser for the guidance, "
        "patience, and critical review given throughout the preparation of this "
        "study, and for the many corrections that improved both the design and the "
        "writing of this proposal.",
    ),
    (
        "Acknowledge first your thesis adviser",
        "They also express their gratitude to the Dean, the Chairperson, and the "
        "members of the panel for the questions, observations, and recommendations "
        "raised during the defense, which directly shaped the direction of the "
        "revised design and the testing plan described in this manuscript.",
    ),
    (
        "Include recognition of the research instructor",
        "The researchers thank the research instructor for the methods, the "
        "documentation practices, and the evaluation approach taught during the "
        "course, and they thank those who agreed to participate in the planned "
        "activities and to share their time in support of the completion of this "
        "study.",
    ),
    (
        "Lastly, express gratitude to your relatives",
        "Finally, the researchers thank their families and relatives for the moral "
        "support, patience, and encouragement that made it possible to continue this "
        "work to its present stage.",
    ),
]


def find_par(doc, predicate):
    for p in doc.paragraphs:
        if predicate(p.text.strip()):
            return p
    return None


def set_text(par: Paragraph, text: str, style: str | None = None) -> bool:
    if style is not None:
        par.style = style
    if par.text.strip() == text:
        return False
    for run in list(par.runs):
        run._r.getparent().remove(run._r)
    run = par.add_run(text)
    run.font.name = ARIAL
    return True


def demote_long_headings(doc) -> int:
    """Return body paragraphs that were mistakenly styled as Heading 2.

    Only ``Heading 2`` is considered. Cover-page and front-matter text may
    legitimately be a long ``Heading 1`` (the thesis title), so it must not be
    touched here.
    """
    fixed = 0
    for p in doc.paragraphs:
        if p.style.name == "Heading 2" and len(p.text.strip()) > 120:
            p.style = "Normal"
            p.alignment = None
            fixed += 1
    return fixed


def restore_cover_title(doc) -> bool:
    """Keep the thesis title on the cover page styled as a heading."""
    p = find_par(doc, lambda t: t.startswith("Design and Development of Project FALCON"))
    if p is None:
        return False
    if p.style.name == "Heading 1":
        return False
    p.style = "Heading 1"
    for r in p.runs:
        r.font.name = ARIAL
    return True


def main() -> int:
    if not DOCX.exists():
        print(f"missing: {DOCX}")
        return 1
    doc = docx.Document(DOCX)
    print(f"opened {DOCX.name} ({len(doc.paragraphs)} paragraphs)")
    changed = []

    # 1. promote numbered headings out of Normal
    hits = 0
    for text, style in PROMOTE:
        p = find_par(doc, lambda t, n=text: t == n)
        if p is None:
            print(f"  ! heading not found: {text}")
            continue
        if p.style.name != style:
            p.style = style
            for r in p.runs:
                r.font.name = ARIAL
            hits += 1
    if hits:
        changed.append(f"{hits} heading styles promoted")

    # 2. give the unnumbered Chapter 1 headings their numbers
    hits = 0
    for old, new in RENUMBER_CH1:
        p = find_par(doc, lambda t, o=old: t == o)
        if p is None:
            continue
        if set_text(p, new, "Heading 2" if new.count(".") == 1 else "Heading 3"):
            hits += 1
    if hits:
        changed.append(f"{hits} Chapter 1 headings numbered")

    # 3. demote prose that was styled as a heading
    hits = demote_long_headings(doc)
    if hits:
        changed.append(f"{hits} body paragraphs demoted from Heading 2")
    if restore_cover_title(doc):
        changed.append("cover-page thesis title restored to Heading 1")

    # 4. replace the Acknowledgment template instructions
    hits = 0
    for prefix, text in ACK_REPLACEMENTS:
        p = find_par(doc, lambda t, pre=prefix: t.startswith(pre))
        if p is None:
            continue
        if set_text(p, text, "Normal"):
            p.alignment = None
            hits += 1
    if hits:
        changed.append(f"{hits} acknowledgment placeholders replaced")

    # 5. sequential figure numbering (replace only the leading figure label)
    hits = 0
    for old_prefix, new_prefix in FIGURE_RENUMBER:
        p = find_par(
            doc,
            lambda t, o=old_prefix: t.startswith(o) and not t.startswith(new_prefix),
        )
        if p is None:
            print(f"  . figure caption already numbered or absent: {old_prefix}")
            continue
        full = p.text.strip()
        if set_text(p, new_prefix + full[len(old_prefix):]):
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            hits += 1
    if hits:
        changed.append(f"{hits} figure captions renumbered")

    # 6. make the fourth presentation-layer item match its siblings
    p = find_par(doc, lambda t: t == "4. Presentation Layer")
    if p is not None:
        p.style = "List Paragraph"
        if set_text(p, "Presentation Layer"):
            changed.append("presentation-layer list item made consistent")

    if not changed:
        print("  no changes needed (already formatted)")
    else:
        for c in changed:
            print(f"  - {c}")

    doc.save(DOCX)
    print(f"saved {DOCX.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
