#!/usr/bin/env python3
"""Placeholder until embedding worker + Supabase upsert is wired (staging)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from auto_client_acquisition.v3.project_intelligence import build_index_summary, scan_project  # noqa: E402


def main() -> int:
    docs = scan_project(_REPO)
    summary = build_index_summary(docs)
    print("EMBEDDINGS_PIPELINE_PLACEHOLDER")
    print("Next: choose embedding model (see docs/EMBEDDINGS_PIPELINE.md + SUPABASE_PROJECT_MEMORY_SETUP.md)")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    print("STATUS: no_vectors_uploaded")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
