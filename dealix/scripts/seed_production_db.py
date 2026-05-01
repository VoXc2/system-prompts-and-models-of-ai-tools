#!/usr/bin/env python3
"""
Seed production Postgres with SAUDI_LEAD_GRAPH_MASTER.csv via the live /api/v1/leads endpoint.

Usage:
    python scripts/seed_production_db.py
    python scripts/seed_production_db.py --api https://web-dealix.up.railway.app --csv docs/ops/lead_machine/SAUDI_LEAD_GRAPH_MASTER.csv

Skips HIGH / BLOCKED / HOLD_FOR_APPROVAL rows for compliance.
"""

from __future__ import annotations
import argparse
import asyncio
import csv
import sys
from pathlib import Path

import httpx


async def seed(api_base: str, csv_path: Path) -> tuple[int, int, list]:
    ok = 0
    skipped = 0
    failed: list[tuple[str, int | str, str]] = []

    with open(csv_path) as f:
        rows = list(csv.DictReader(f))

    async with httpx.AsyncClient() as client:
        for i, r in enumerate(rows):
            risk = (r.get("risk_score") or "").upper()
            if risk in ("HIGH", "BLOCKED"):
                skipped += 1
                continue
            if "HOLD" in (r.get("recommended_action", "") or ""):
                skipped += 1
                continue

            name = (r.get("decision_roles") or "Unknown").strip() or "Unknown"
            payload = {
                "company": r["company"][:200],
                "name": name[:200],
                "sector": (r.get("sector", "")[:64] or None),
                "region": r.get("country", "") or "Saudi Arabia",
                "source": "manual",
                "locale": "ar",
                "message": (
                    f"{r.get('first_message_angle','')} | "
                    f"priority={r.get('priority','')} | "
                    f"opportunity={r.get('opportunity_type','')} | "
                    f"offer={r.get('offer_recommended','')}"
                )[:500],
            }
            try:
                resp = await client.post(
                    f"{api_base.rstrip('/')}/api/v1/leads",
                    json=payload,
                    timeout=15,
                )
                if resp.status_code in (200, 201):
                    ok += 1
                else:
                    failed.append((r["company"], resp.status_code, resp.text[:120]))
            except Exception as e:
                failed.append((r["company"], "exc", str(e)[:80]))

            if i % 20 == 0 and i > 0:
                print(
                    f"  progress {i+1}/{len(rows)}: ok={ok} skipped={skipped} failed={len(failed)}",
                    file=sys.stderr,
                )

    return ok, skipped, failed


def main():
    ap = argparse.ArgumentParser(description="Seed Dealix production DB from Saudi Lead Graph CSV")
    ap.add_argument("--api", default="https://web-dealix.up.railway.app", help="API base URL")
    ap.add_argument(
        "--csv",
        default="docs/ops/lead_machine/SAUDI_LEAD_GRAPH_MASTER.csv",
        help="Path to SAUDI_LEAD_GRAPH_MASTER.csv",
    )
    args = ap.parse_args()

    csv_path = Path(args.csv)
    if not csv_path.exists():
        print(f"ERROR: {csv_path} not found", file=sys.stderr)
        sys.exit(1)

    print(f"→ seeding {args.api} from {csv_path}", file=sys.stderr)
    ok, skipped, failed = asyncio.run(seed(args.api, csv_path))

    print(f"\n✓ uploaded: {ok}")
    print(f"✓ skipped (HIGH/BLOCKED/HOLD): {skipped}")
    print(f"✓ failed: {len(failed)}")
    if failed[:3]:
        print("\nsample failures:")
        for name, code, msg in failed[:3]:
            print(f"  {name}: {code} — {msg}")


if __name__ == "__main__":
    main()
