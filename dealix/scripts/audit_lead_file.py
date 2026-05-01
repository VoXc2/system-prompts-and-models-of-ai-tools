#!/usr/bin/env python3
"""
audit_lead_file.py — Local audit of a CSV/JSON lead file BEFORE you ingest it.

Reports:
    - row count
    - per-field fill rate
    - normalized phone success rate (Saudi)
    - email validity rate
    - domain extractability
    - estimated dedup risk inside the file
    - flags for risky fields (personal-only contacts, no source URL)

Use this to evaluate purchased datasets BEFORE you pay or upload.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

# Make local imports work without installing the package
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from auto_client_acquisition.pipelines.normalize import (  # noqa: E402
    fuzzy_company_key,
    is_acceptable,
    normalize_email,
    normalize_domain,
    normalize_row,
    normalize_saudi_phone,
)


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
        raise SystemExit("JSON must be list or {rows: [...]}")
    if path.suffix.lower() in {".csv", ".tsv"}:
        delim = "\t" if path.suffix.lower() == ".tsv" else ","
        with path.open(encoding="utf-8-sig", newline="") as f:
            return [dict(r) for r in csv.DictReader(f, delimiter=delim)]
    raise SystemExit(f"unsupported: {path.suffix}")


def pct(n: int, d: int) -> str:
    return f"{(n / d * 100):.1f}%" if d else "0.0%"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--show-rejects", type=int, default=5,
                    help="Show first N rejected rows (default 5)")
    args = ap.parse_args()

    p = Path(args.file)
    if not p.exists():
        print(f"file not found: {p}", file=sys.stderr)
        return 2

    rows = parse_file(p)
    n = len(rows)
    if not n:
        print("empty file", file=sys.stderr)
        return 2

    field_present: Counter[str] = Counter()
    for r in rows:
        for k, v in r.items():
            if v not in (None, ""):
                field_present[k] += 1

    accepted = 0
    rejected: list[tuple[dict, str]] = []
    phones_normalized = 0
    emails_valid = 0
    domains_extractable = 0
    # Match server-side dedupe: collide on ANY of domain/phone/email/place_id/name+city
    by_domain: Counter[str] = Counter()
    by_phone: Counter[str] = Counter()
    by_email: Counter[str] = Counter()
    by_place: Counter[str] = Counter()
    by_name_city: Counter[str] = Counter()

    for r in rows:
        nr = normalize_row(r)
        if nr.get("phone"):
            phones_normalized += 1
        if nr.get("email"):
            emails_valid += 1
        if nr.get("domain"):
            domains_extractable += 1
        ok, why = is_acceptable(nr)
        if ok:
            accepted += 1
            d_val = nr.get("domain")
            if d_val:
                by_domain[d_val] += 1
            p_val = nr.get("phone")
            if p_val:
                by_phone[p_val] += 1
            e_val = nr.get("email")
            if e_val:
                by_email[e_val] += 1
            pid_val = nr.get("google_place_id")
            if pid_val:
                by_place[pid_val] += 1
            nk_val = nr.get("normalized_name")
            if nk_val:
                city = (nr.get("city") or "").strip().lower()
                by_name_city[f"{nk_val}|{city}"] += 1
        else:
            rejected.append((r, why or ""))

    def _dup_count(c: Counter[str]) -> int:
        return sum(v - 1 for v in c.values() if v > 1)

    dup_by_kind = {
        "domain": _dup_count(by_domain),
        "phone": _dup_count(by_phone),
        "email": _dup_count(by_email),
        "place_id": _dup_count(by_place),
        "name+city": _dup_count(by_name_city),
    }
    dup_keys = sum(dup_by_kind.values())
    unique_keys = (
        len(by_domain) + len(by_phone) + len(by_email)
        + len(by_place) + len(by_name_city)
    )

    print(f"\n📂 {p.name}")
    print(f"   rows: {n}")
    print(f"   acceptable (has company + 1+ identifier): {accepted} ({pct(accepted, n)})")
    print(f"   rejected: {len(rejected)} ({pct(len(rejected), n)})")
    print(f"   phones normalized to +966: {phones_normalized} ({pct(phones_normalized, n)})")
    print(f"   valid emails: {emails_valid} ({pct(emails_valid, n)})")
    print(f"   extractable domains: {domains_extractable} ({pct(domains_extractable, n)})")
    print(f"   dedup risk: {dup_keys} duplicate-key collisions across {unique_keys} unique keys")
    for kind, count in dup_by_kind.items():
        if count:
            print(f"     · {kind}: {count} collision(s)")

    print("\n📊 field fill rate:")
    for k, c in field_present.most_common(20):
        print(f"   {k:30s} {pct(c, n)} ({c})")

    if rejected and args.show_rejects > 0:
        print(f"\n❌ first {min(args.show_rejects, len(rejected))} rejected rows:")
        for r, why in rejected[: args.show_rejects]:
            print(f"   - reason={why}  row={json.dumps(r, ensure_ascii=False)[:160]}")

    print("\n💡 recommendation:")
    if accepted / n < 0.5:
        print("   ⚠️  acceptance rate < 50% — file is low quality. Re-request from vendor.")
    elif accepted / n < 0.8:
        print("   ⚠️  acceptance rate 50-80% — usable but expect rejection on import.")
    else:
        print("   ✅ acceptance rate ≥ 80% — file is healthy to import.")

    if dup_keys / max(unique_keys, 1) > 0.2:
        print("   ⚠️  high in-file duplicate ratio — run dedupe before any outreach.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
