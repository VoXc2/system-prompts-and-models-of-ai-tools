#!/usr/bin/env python3
"""جلب ملخص أسبوعي لدفتر الإثبات من API (للمؤسس/CS).

Usage:
  set BASE_URL=https://api.dealix.me
  set API_KEY=your_x_api_key   # إذا كان الخادم يفرض API_KEYS
  python scripts/fetch_proof_ledger_weekly.py

  python scripts/fetch_proof_ledger_weekly.py --tenant default
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import httpx  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default=os.environ.get("BASE_URL", "http://localhost:8000").rstrip("/"))
    parser.add_argument("--tenant", default=os.environ.get("PROOF_LEDGER_TENANT", "default"))
    args = parser.parse_args()

    url = f"{args.base_url}/api/v1/innovation/proof-ledger/report/week"
    headers: dict[str, str] = {}
    key = os.environ.get("API_KEY", "").strip()
    if key:
        headers["X-API-Key"] = key

    try:
        r = httpx.get(url, params={"tenant_id": args.tenant}, headers=headers, timeout=60.0)
    except httpx.RequestError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if r.status_code != 200:
        print(r.text[:500], file=sys.stderr)
        return 1

    try:
        print(json.dumps(r.json(), ensure_ascii=False, indent=2))
    except Exception:
        print(r.text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
