"""Compatibility entry point for the current Project FALCON thesis.

The former V2 generator contained superseded BNO085, fixed-CAD, solar, and AI
claims. Existing shortcuts may keep using this filename, but it now generates
the implementation-aligned V3 document.
"""

from pathlib import Path
import runpy


if __name__ == "__main__":
    runpy.run_path(str(Path(__file__).with_name("update_v3_documentation.py")), run_name="__main__")
