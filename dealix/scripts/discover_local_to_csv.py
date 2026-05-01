#!/usr/bin/env python3
"""
discover_local_to_csv.py — Pull a Saudi local sector × city from
/api/v1/leads/discover/local and dump it as CSV ready for upload via /data/import.

Usage:
    python scripts/discover_local_to_csv.py dental_clinic riyadh \
        [--api https://api.dealix.me] [--max 20] [--out riyadh_dentists.csv]
"""

from __future__ import annotations

import argparse
import csv
import sys

import httpx


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("industry")
    ap.add_argument("city")
    ap.add_argument("--api", default="https://api.dealix.me")
    ap.add_argument("--max", type=int, default=20)
    ap.add_argument("--no-details", action="store_true")
    ap.add_argument("--custom-query")
    ap.add_argument("--out")
    args = ap.parse_args()

    api = args.api.rstrip("/")
    body = {
        "industry": args.industry,
        "city": args.city,
        "max_results": args.max,
        "hydrate_details": not args.no_details,
    }
    if args.custom_query:
        body["custom_query"] = args.custom_query

    out_path = args.out or f"{args.industry}_{args.city}.csv"

    print(f"→ POST {api}/api/v1/leads/discover/local", file=sys.stderr)
    with httpx.Client(timeout=60) as client:
        r = client.post(f"{api}/api/v1/leads/discover/local", json=body)
        r.raise_for_status()
        payload = r.json()

    inner = (payload.get("data") or payload) if "data" in payload else payload
    results = inner.get("results", [])
    if not results:
        print(f"no results — status={payload.get('status')} chain={payload.get('chain')}",
              file=sys.stderr)
        return 1

    with open(out_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "company_name", "address", "phone", "website", "rating",
                "ratings_count", "place_id", "city", "industry",
                "google_maps_url", "lat", "lng",
            ],
        )
        writer.writeheader()
        for r in results:
            writer.writerow({
                "company_name": r.get("name", ""),
                "address": r.get("address", ""),
                "phone": r.get("phone", ""),
                "website": r.get("website", ""),
                "rating": r.get("rating", ""),
                "ratings_count": r.get("ratings_count", ""),
                "place_id": r.get("place_id", ""),
                "city": args.city,
                "industry": args.industry,
                "google_maps_url": r.get("google_maps_url", ""),
                "lat": r.get("lat", ""),
                "lng": r.get("lng", ""),
            })
    print(f"wrote {len(results)} rows → {out_path}")
    print("\nNext: import to Dealix:")
    print(f"    python scripts/import_leads.py {out_path} \\")
    print(f"        --source-name 'maps_{args.industry}_{args.city}' \\")
    print(f"        --source-type google_maps --auto-pipeline")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
