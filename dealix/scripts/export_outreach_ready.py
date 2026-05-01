#!/usr/bin/env python3
"""
export_outreach_ready.py — Pull outreach-ready leads from /api/v1/outreach/prepare-from-data
and dump them as CSV/JSON for Sami's manual outreach.

Usage:
    python scripts/export_outreach_ready.py [--api https://api.dealix.me] \
        [--priority P0,P1] [--max 50] [--out outreach_ready.csv]
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import httpx


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--api", default="https://api.dealix.me")
    ap.add_argument("--priority", default="P0,P1")
    ap.add_argument("--max", type=int, default=50)
    ap.add_argument("--out", default="outreach_ready.csv")
    ap.add_argument("--persist", action="store_true",
                    help="Also create OutreachQueueRecord rows on the server")
    args = ap.parse_args()

    body = {
        "priority": args.priority.split(","),
        "max_accounts": args.max,
        "persist": args.persist,
    }
    api = args.api.rstrip("/")
    print(f"→ POST {api}/api/v1/outreach/prepare-from-data", file=sys.stderr)
    with httpx.Client(timeout=60) as client:
        r = client.post(f"{api}/api/v1/outreach/prepare-from-data", json=body)
        r.raise_for_status()
        out = r.json()

    ready = out.get("ready", [])
    out_path = Path(args.out)
    if out_path.suffix.lower() in {".json", ".jsonl"}:
        out_path.write_text(
            json.dumps(out, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    else:
        with out_path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "account_id", "company", "channel", "priority", "score",
                    "approval_required", "due_at", "message",
                ],
            )
            writer.writeheader()
            for entry in ready:
                writer.writerow({
                    "account_id": entry.get("account_id"),
                    "company": entry.get("company"),
                    "channel": entry.get("channel"),
                    "priority": entry.get("priority"),
                    "score": entry.get("score"),
                    "approval_required": entry.get("approval_required"),
                    "due_at": entry.get("due_at"),
                    "message": (entry.get("message") or "").replace("\n", " ⏎ "),
                })

    print(json.dumps({
        "ready_count": out.get("ready_count"),
        "needs_review_count": out.get("needs_review_count"),
        "blocked_count": out.get("blocked_count"),
        "persisted": out.get("persisted"),
        "wrote": str(out_path),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
