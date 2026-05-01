#!/usr/bin/env python3
"""Write docs/LAUNCH_READINESS_REPORT.md from build_launch_report()."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from auto_client_acquisition.personal_operator.launch_report import build_launch_report, launch_report_markdown_ar


def main() -> None:
    repo = _REPO_ROOT
    report_path = repo / "docs" / "LAUNCH_READINESS_REPORT.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    md = launch_report_markdown_ar(build_launch_report())
    report_path.write_text(md, encoding="utf-8")
    print(f"Wrote {report_path}")


if __name__ == "__main__":
    main()
