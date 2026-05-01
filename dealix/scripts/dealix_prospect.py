#!/usr/bin/env python3
"""
Dealix Prospect CLI — run tech detection + lead scoring on any domain or CSV.

Usage:
  # Single domain
  python scripts/dealix_prospect.py foodics.com

  # Bulk from CSV (CSV must have a 'domain' column)
  python scripts/dealix_prospect.py --csv leads.csv --out enriched.csv

  # Bulk via live Dealix API
  python scripts/dealix_prospect.py --api https://web-dealix.up.railway.app foodics.com salla.sa

Works offline (no API keys) — uses the Dealix native tech detector.
Outputs: JSON to stdout, or CSV with added columns if --out given.
"""
from __future__ import annotations

import argparse
import asyncio
import csv
import json
import sys
from pathlib import Path

# Project root on path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

try:
    from auto_client_acquisition.connectors.tech_detect import detect_stack
except ImportError as exc:
    print(f"ERROR: {exc}. Run from project root or install project.", file=sys.stderr)
    sys.exit(2)


async def detect_one(domain: str, timeout: float = 10.0) -> dict:
    r = await detect_stack(domain, timeout=timeout, extra_paths=["/careers", "/about"])
    return r.to_dict()


async def detect_api(domain: str, api_base: str) -> dict:
    import httpx
    async with httpx.AsyncClient() as c:
        r = await c.post(
            f"{api_base.rstrip('/')}/api/v1/prospect/enrich-tech",
            json={"domain": domain},
            timeout=30.0,
        )
        return r.json()


async def run_bulk(domains: list[str], concurrency: int, api_base: str | None) -> dict[str, dict]:
    sem = asyncio.Semaphore(concurrency)

    async def _one(d: str) -> tuple[str, dict]:
        async with sem:
            try:
                if api_base:
                    res = await detect_api(d, api_base)
                else:
                    res = await detect_one(d)
                return d, res
            except Exception as exc:  # noqa: BLE001
                return d, {"status": "error", "error": str(exc), "domain": d}

    pairs = await asyncio.gather(*(_one(d) for d in domains))
    return dict(pairs)


def _read_csv_domains(path: Path) -> list[tuple[int, dict]]:
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    if not rows:
        return []
    # Find domain column: exact 'domain', or first col containing 'domain'
    fieldnames = list(rows[0].keys())
    col = next(
        (c for c in fieldnames if c.lower() == "domain"),
        next((c for c in fieldnames if "domain" in c.lower()), None),
    )
    if not col:
        print(f"ERROR: CSV has no 'domain' column. Columns: {fieldnames}", file=sys.stderr)
        sys.exit(3)
    out: list[tuple[int, dict]] = []
    for i, row in enumerate(rows):
        d = (row.get(col) or "").strip()
        if d and "." in d:
            out.append((i, row))
    return out


def _flatten(detection: dict) -> dict:
    tools = [t.get("name", "") for t in detection.get("tools", []) or []]
    signals = [s.get("evidence", "") for s in detection.get("signals", []) or []]
    return {
        "tech_status": detection.get("status", ""),
        "tech_tools": "; ".join(tools[:8]),
        "tech_signals": "; ".join(signals[:5]),
        "tech_tools_count": len(tools),
    }


async def _main(args: argparse.Namespace) -> int:
    api_base = args.api or None

    # Source: CSV or positional args
    if args.csv:
        csv_path = Path(args.csv)
        if not csv_path.exists():
            print(f"ERROR: {csv_path} not found", file=sys.stderr)
            return 3
        pairs = _read_csv_domains(csv_path)
        print(f"found {len(pairs)} domains in {csv_path}", file=sys.stderr)
        domains = [p[1]["domain"] if "domain" in p[1] else next((v for k, v in p[1].items() if "domain" in k.lower()), "") for p in pairs]
        domains = [d for d in domains if d]
    else:
        domains = args.domains

    if not domains:
        print("ERROR: no domains provided. Pass args or use --csv", file=sys.stderr)
        return 1

    print(f"enriching {len(domains)} domain(s) using {'Dealix API' if api_base else 'local detector'}...", file=sys.stderr)
    results = await run_bulk(domains, concurrency=args.concurrency, api_base=api_base)

    if args.csv and args.out:
        # Re-read CSV and write augmented copy
        with open(args.csv, newline="") as f:
            reader = csv.DictReader(f)
            original_rows = list(reader)
            fieldnames = list(original_rows[0].keys())

        new_fields = ["tech_status", "tech_tools", "tech_signals", "tech_tools_count"]
        for nf in new_fields:
            if nf not in fieldnames:
                fieldnames.append(nf)

        for row in original_rows:
            d = row.get("domain") or next((v for k, v in row.items() if "domain" in k.lower()), None)
            d = (d or "").strip()
            res = results.get(d, {})
            row.update(_flatten(res))

        out_path = Path(args.out)
        with open(out_path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            w.writerows(original_rows)
        print(f"✓ wrote {out_path}  ({len(original_rows)} rows)", file=sys.stderr)
        return 0

    # Default: JSON to stdout
    if len(results) == 1:
        _, v = next(iter(results.items()))
        print(json.dumps(v, indent=2, ensure_ascii=False))
    else:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    return 0


def main():
    ap = argparse.ArgumentParser(
        prog="dealix-prospect",
        description="Dealix Prospector CLI — tech detection + lead scoring for Saudi B2B",
    )
    ap.add_argument("domains", nargs="*", help="one or more domains (e.g. foodics.com salla.sa)")
    ap.add_argument("--csv", help="CSV file with a 'domain' column to enrich")
    ap.add_argument("--out", help="output CSV path (with --csv) — adds tech_status/tech_tools/tech_signals/tech_tools_count")
    ap.add_argument("--api", help="use live Dealix API instead of local (e.g. https://web-dealix.up.railway.app)")
    ap.add_argument("--concurrency", type=int, default=5, help="parallelism (1-10)")
    args = ap.parse_args()
    sys.exit(asyncio.run(_main(args)))


if __name__ == "__main__":
    main()
