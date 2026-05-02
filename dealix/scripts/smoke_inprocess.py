#!/usr/bin/env python3
"""HTTP smoke without a TCP server — uses ASGITransport (CI-friendly)."""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import httpx  # noqa: E402

from api.main import create_app  # noqa: E402


PATHS = [
    "/",
    "/health",
    "/api/v1/personal-operator/daily-brief",
    "/api/v1/personal-operator/launch-report",
    "/api/v1/v3/command-center/snapshot",
    "/api/v1/business/pricing",
    "/api/v1/innovation/growth-missions",
    "/api/v1/innovation/command-feed/demo",
    "/api/v1/services/catalog",
    "/api/v1/launch/go-no-go",
    "/api/v1/launch/scorecard",
    "/api/v1/revenue-launch/offer",
    "/api/v1/revenue-launch/offer?lang=en",
    "/api/v1/revenue-launch/payment/manual-flow",
    "/api/v1/operator/bundles",
    "/api/v1/operator/proof-pack/demo",
    "/api/v1/operator/whatsapp/daily-brief",
    "/api/v1/operator/tools/matrix",
    "/api/v1/revenue-os/company-os/command-feed/demo",
    "/api/v1/cards/feed?role=ceo",
    "/api/v1/cards/feed?role=sales_manager",
    "/api/v1/cards/whatsapp/daily-brief?role=growth_manager",
    "/api/v1/revenue-os/company-os/work-units/demo",
    "/api/v1/revenue-os/company-os/self-improvement/weekly-report",
    "/api/v1/customer-ops/onboarding/checklist",
    "/api/v1/customer-ops/support/sla",
    "/api/v1/customer-ops/connectors/status",
]


async def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, OSError):
        pass
    app = create_app()
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        failed = 0
        for path in PATHS:
            r = await client.get(path)
            line = f"{r.status_code} {path}"
            print(line)
            if r.status_code != 200:
                failed += 1
                print(r.text[:400], file=sys.stderr)
            else:
                try:
                    snippet = json.dumps(r.json(), ensure_ascii=False)[:400]
                except Exception:
                    snippet = r.text[:200]
                print(snippet.encode("utf-8", errors="replace").decode("utf-8", errors="replace"))
        if failed:
            print(f"SMOKE_FAIL {failed} endpoints", file=sys.stderr)
            return 1
    print("SMOKE_INPROCESS_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
