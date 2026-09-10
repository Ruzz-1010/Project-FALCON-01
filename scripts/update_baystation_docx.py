"""Compatibility entry point for rebuilding the canonical BayStation.docx."""

from pathlib import Path
import runpy


if __name__ == "__main__":
    runpy.run_path(
        str(Path(__file__).with_name("build_baystation_thesis.py")),
        run_name="__main__",
    )
