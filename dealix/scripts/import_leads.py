#!/usr/bin/env python3
"""
import_leads.py — POST a CSV/JSON file to /api/v1/data/import.

Usage:
    python scripts/import_leads.py <file.csv|file.json> --source-name "X" \
        --source-type owned|public|paid|partner|google_maps|google_search|manual \
        [--allowed-use "..."] [--risk-level low|medium|high] \
        [--api https://api.dealix.me]

The file is parsed locally; we send the rows as JSON to the API. Server
stores raw rows + creates a RawLeadImport. Then call /normalize → /dedupe → /enrich.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import httpx


def parse_file(path: Path) -> list[dict]:
    if path.suffix.lower() in {".json", ".jsonl"}:
        text = path.read_text(encoding="utf-8")
        if path.suffix.lower() == ".jsonl":
            return [json.loads(line) for line in text.splitlines() if line.strip()]
        data = json.loads(text)
        if isinstance(data, list):
            return data
        if isinstance(data, dict) and "rows" in data:
            return data["rows"]
        raise SystemExit("JSON must be a list of dicts or {rows: [...]}")
    if path.suffix.lower() in {".csv", ".tsv"}:
        delim = "\t" if path.suffix.lower() == ".tsv" else ","
        with path.open(encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f, delimiter=delim)
            return [dict(r) for r in reader]
    raise SystemExit(f"Unsupported file type: {path.suffix}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--source-name", required=True)
    ap.add_argument("--source-type", required=True,
                    choices=["owned", "public", "paid", "partner",
                             "google_maps", "google_search", "manual"])
    ap.add_argument("--allowed-use", default="business_contact_research_only")
    ap.add_argument("--consent-status", default="unknown")
    ap.add_argument("--risk-level", default="medium",
                    choices=["low", "medium", "high"])
    ap.add_argument("--api", default="https://api.dealix.me")
    ap.add_argument("--imported-by", default="cli")
    ap.add_argument("--notes", default="")
    ap.add_argument("--auto-pipeline", action="store_true",
                    help="After import, also call normalize → dedupe → enrich")
    args = ap.parse_args()

    p = Path(args.file)
    if not p.exists():
        print(f"file not found: {p}", file=sys.stderr)
        return 2

    rows = parse_file(p)
    if not rows:
        print("no rows parsed", file=sys.stderr)
        return 2

    payload = {
        "source_name": args.source_name,
        "source_type": args.source_type,
        "allowed_use": args.allowed_use,
        "consent_status": args.consent_status,
        "risk_level": args.risk_level,
        "file_name": p.name,
        "imported_by": args.imported_by,
        "notes": args.notes,
        "rows": rows,
    }
    api = args.api.rstrip("/")
    print(f"→ POST {api}/api/v1/data/import  rows={len(rows)}")
    with httpx.Client(timeout=60) as client:
        r = client.post(f"{api}/api/v1/data/import", json=payload)
        r.raise_for_status()
        out = r.json()
        print(json.dumps(out, ensure_ascii=False, indent=2))

        if args.auto_pipeline and out.get("import_id"):
            iid = out["import_id"]
            for step in ("normalize", "dedupe", "enrich"):
                print(f"\n→ POST {api}/api/v1/data/import/{iid}/{step}")
                rr = client.post(f"{api}/api/v1/data/import/{iid}/{step}", json={})
                print(json.dumps(rr.json(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
