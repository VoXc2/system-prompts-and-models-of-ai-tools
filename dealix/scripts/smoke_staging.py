#!/usr/bin/env python3
"""Smoke critical GET endpoints against a real staging base URL.

Usage:
  set STAGING_BASE_URL=https://your-app.onrender.com   # no trailing slash
  python scripts/smoke_staging.py

Or:
  python scripts/smoke_staging.py --base-url https://your-app.onrender.com

Never commit real URLs or secrets. Exit code 1 if any request fails.

If staging enforces API keys, set STAGING_API_KEY (sent as X-API-Key).
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

# Keep aligned with scripts/smoke_inprocess.py (GET only).
PATHS = [
    "/",
    "/health",
    "/api/v1/personal-operator/daily-brief",
    "/api/v1/personal-operator/launch-report",
    "/api/v1/v3/command-center/snapshot",
    "/api/v1/business/pricing",
    "/api/v1/innovation/growth-missions",
    "/api/v1/innovation/command-feed/demo",
]


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, OSError):
        pass

    parser = argparse.ArgumentParser(description="HTTP smoke against staging URL")
    parser.add_argument(
        "--base-url",
        default=os.environ.get("STAGING_BASE_URL", "").strip().rstrip("/"),
        help="Staging origin (or set STAGING_BASE_URL)",
    )
    args = parser.parse_args()
    base = args.base_url
    if not base:
        print("ERROR: set STAGING_BASE_URL or pass --base-url", file=sys.stderr)
        return 2

    timeout = float(os.environ.get("STAGING_SMOKE_TIMEOUT", "30"))
    headers: dict[str, str] = {}
    api_key = os.environ.get("STAGING_API_KEY", "").strip()
    if api_key:
        headers["X-API-Key"] = api_key

    failed = 0
    with httpx.Client(timeout=timeout, follow_redirects=True, headers=headers or None) as client:
        for path in PATHS:
            url = f"{base}{path}"
            try:
                r = client.get(url)
            except httpx.RequestError as exc:
                print(f"FAIL {path} error={exc}", file=sys.stderr)
                failed += 1
                continue
            print(f"{r.status_code} {path}")
            if r.status_code != 200:
                failed += 1
                print(r.text[:400], file=sys.stderr)
            else:
                try:
                    print(json.dumps(r.json(), ensure_ascii=False)[:300])
                except Exception:
                    print(r.text[:120])

    if failed:
        print(f"SMOKE_STAGING_FAIL {failed} endpoints", file=sys.stderr)
        return 1
    print("SMOKE_STAGING_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
