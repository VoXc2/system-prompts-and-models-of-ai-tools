#!/usr/bin/env python3
"""HTTP smoke against a running Dealix API (default http://127.0.0.1:8001)."""

from __future__ import annotations

import argparse
import json
import sys

import httpx


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--base-url", default="http://127.0.0.1:8001")
    args = p.parse_args()
    base = args.base_url.rstrip("/")
    paths = [
        "/",
        "/health",
        "/api/v1/personal-operator/daily-brief",
        "/api/v1/personal-operator/launch-report",
        "/api/v1/v3/command-center/snapshot",
    ]
    ok = 0
    with httpx.Client(timeout=10.0) as client:
        for path in paths:
            url = f"{base}{path}"
            try:
                r = client.get(url)
            except httpx.ConnectError as exc:
                print(f"SKIP {url} connect_error: {exc}", file=sys.stderr)
                print("NOT_RUN: start server with: uvicorn api.main:app --host 127.0.0.1 --port 8001")
                return 3
            st = r.status_code
            print(f"{st} {path}")
            if st == 200:
                try:
                    print(json.dumps(r.json(), ensure_ascii=False)[:500])
                except Exception:
                    print(r.text[:300])
                ok += 1
            else:
                print(r.text[:500], file=sys.stderr)
    if ok == len(paths):
        print("SMOKE_OK")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
