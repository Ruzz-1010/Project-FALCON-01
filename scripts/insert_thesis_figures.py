#!/usr/bin/env python3
"""Insert the generated Chapter 2 figures into the thesis DOCX.

Each PNG produced by ``scripts/make_thesis_figures.py`` is placed in its own
paragraph immediately ABOVE the matching caption paragraph, centred, and scaled
so that it is never wider than 6.0 in nor taller than 5.2 in.

Idempotent: if a caption already has an image directly above it, the figure is
skipped, so the script can be re-run safely.

The DOCX is not rebuilt from a template; only the figure paragraphs are added,
so the user's existing content and formatting are preserved.
"""

from __future__ import annotations

import sys
from pathlib import Path

import docx
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.shared import Inches, Pt
from docx.text.paragraph import Paragraph
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
DOCX = ROOT / "THESIS DOCUMENTATION" / "Project_FALCON_Chapters_1_and_2_Final.docx"
FIGDIR = Path("/tmp/opencode/figs/out")

MAX_W = 6.0
MAX_H = 5.2

# caption text -> png stem
FIGURES = [
    ("Figure 2.2. System Architecture of Project FALCON", "fig-2-2-system-architecture"),
    ("Figure 2.3. Proposed Hardware Block Diagram of Project FALCON", "fig-2-3-hardware-block"),
    ("Figure 2.4. Proposed Software Architecture of Project FALCON", "fig-2-4-software-architecture"),
    ("Figure 2.5. Proposed Hardware-Software Integration Diagram", "fig-2-5-hw-sw-integration"),
    ("Figure 2.6. System Flow Chart of Project FALCON", "fig-2-6-system-flow"),
    ("Figure 2.7. Pressure Data Processing Flowchart", "fig-2-7-pressure-flow"),
    ("Figure 2.8. AI Prediction Model Workflow", "fig-2-8-ai-workflow"),
    ("Figure 2.9. Testing and Validation Workflow", "fig-2-9-testing-workflow"),
]

DRAWING = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}drawing"


def find_caption(doc, text: str) -> Paragraph | None:
    for p in doc.paragraphs:
        if p.text.strip() == text:
            return p
    return None


def prev_par(par: Paragraph) -> Paragraph | None:
    el = par._p.getprevious()
    while el is not None and el.tag.endswith("}p"):
        return Paragraph(el, par._parent)
    return None


def has_image(par: Paragraph) -> bool:
    return par._p.find(f".//{DRAWING}") is not None


def image_width(png: Path) -> float:
    with Image.open(png) as im:
        w, h = im.size
    aspect = w / h
    return round(min(MAX_W, MAX_H * aspect), 2)


def insert_image_before(caption: Paragraph, png: Path) -> None:
    p = OxmlElement("w:p")
    caption._p.addprevious(p)
    para = Paragraph(p, caption._parent)
    para.style = "Normal"
    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    para.paragraph_format.space_before = Pt(6)
    para.paragraph_format.space_after = Pt(2)
    run = para.add_run()
    run.add_picture(str(png), width=Inches(image_width(png)))


def main() -> int:
    if not DOCX.exists():
        print(f"missing: {DOCX}")
        return 1
    missing = [p.stem for _, p_ in FIGURES for p in [Path(p_)] if not (FIGDIR / f"{p.stem}.png").exists()]
    if missing:
        print(f"missing PNGs in {FIGDIR}: {missing}")
        print("run scripts/make_thesis_figures.py and convert the SVGs first")
        return 1

    doc = docx.Document(DOCX)
    print(f"opened {DOCX.name} ({len(doc.paragraphs)} paragraphs)")
    done = skipped = 0
    for caption_text, stem in FIGURES:
        cap = find_caption(doc, caption_text)
        if cap is None:
            print(f"  ! caption not found: {caption_text}")
            continue
        prev = prev_par(cap)
        if prev is not None and has_image(prev):
            skipped += 1
            print(f"  . {stem}: already present")
            continue
        insert_image_before(cap, FIGDIR / f"{stem}.png")
        done += 1
        print(f"  + {stem} -> {image_width(FIGDIR / f'{stem}.png')} in")

    if not done and not skipped:
        print("  nothing inserted")
    doc.save(DOCX)
    print(f"saved {DOCX.name} (inserted {done}, skipped {skipped})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
