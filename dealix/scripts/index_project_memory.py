#!/usr/bin/env python3
"""Scan the repo, summarize index stats, optional keyword query, optional JSON output.

No Supabase credentials required. If SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are set,
prints a notice that upload is not implemented yet.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from auto_client_acquisition.v3.project_intelligence import (
    build_index_summary,
    naive_search,
    scan_project,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Dealix local project index")
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument("--out", default=None, help="Write JSON summary (e.g. .dealix/project_index.json)")
    parser.add_argument("--query", default=None, help="Keyword search over indexed files")
    args = parser.parse_args()

    if os.environ.get("SUPABASE_URL") and os.environ.get("SUPABASE_SERVICE_ROLE_KEY"):
        print("Supabase upload not implemented yet (local index only).")

    root = (Path(args.root) if Path(args.root).is_absolute() else _REPO_ROOT / args.root).resolve()
    documents = scan_project(root)
    summary = build_index_summary(documents)
    print(json.dumps(summary, indent=2, ensure_ascii=False))

    if args.query:
        hits = naive_search(documents, args.query, limit=20)
        print(f"\n-- query: {args.query!r} ({len(hits)} hits) --")
        for row in hits[:15]:
            print(f"{row['score']:4d}  {row['path']}")

    if args.out:
        out_path = Path(args.out)
        if not out_path.is_absolute():
            out_path = _REPO_ROOT / out_path
        out_path.parent.mkdir(parents=True, exist_ok=True)
        payload: dict = {"summary": summary}
        if args.query:
            payload["query"] = args.query
            payload["hits"] = naive_search(documents, args.query, limit=50)
        out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
