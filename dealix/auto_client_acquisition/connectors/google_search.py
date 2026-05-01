"""
Google Custom Search connector — free tier 100 queries/day.

Uses GOOGLE_SEARCH_API_KEY + GOOGLE_SEARCH_CX env vars (set in Railway).
Returns structured search results for ICP-driven lead discovery.

Docs: https://developers.google.com/custom-search/v1/overview
"""

from __future__ import annotations

import asyncio
import logging
import os
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any

import httpx

log = logging.getLogger(__name__)

ENDPOINT = "https://www.googleapis.com/customsearch/v1"
MAX_RESULTS_PER_QUERY = 10  # Google CSE max per request


@dataclass
class SearchResult:
    title: str
    link: str
    snippet: str
    display_link: str
    formatted_url: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SearchResponse:
    query: str
    total_results: int | None
    search_time: float | None
    results: list[SearchResult]
    fetched_at: str
    status: str  # ok | no_keys | http_error | timeout
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "query": self.query,
            "total_results": self.total_results,
            "search_time": self.search_time,
            "results": [r.to_dict() for r in self.results],
            "fetched_at": self.fetched_at,
            "status": self.status,
            "error": self.error,
        }


async def google_search(
    query: str,
    *,
    num: int = 10,
    start: int = 1,
    site: str | None = None,
    lang: str | None = None,
    timeout: float = 10.0,
) -> SearchResponse:
    """
    Run a Google Custom Search query.

    Args:
        query: search terms
        num: max 10 per request (CSE limit)
        start: 1-indexed offset (for pagination: 1, 11, 21, ...)
        site: optional domain restriction (e.g. "linkedin.com")
        lang: optional language code ("ar", "en")
    """
    api_key = os.getenv("GOOGLE_SEARCH_API_KEY", "").strip()
    cx = os.getenv("GOOGLE_SEARCH_CX", "").strip()

    fetched_at = datetime.now(timezone.utc).isoformat()

    if not api_key or not cx:
        return SearchResponse(
            query=query,
            total_results=None,
            search_time=None,
            results=[],
            fetched_at=fetched_at,
            status="no_keys",
            error="GOOGLE_SEARCH_API_KEY or GOOGLE_SEARCH_CX not set in environment",
        )

    # Normalize query (optional site restriction)
    q = query.strip()
    if site:
        q = f"{q} site:{site}"

    params: dict[str, Any] = {
        "key": api_key,
        "cx": cx,
        "q": q,
        "num": max(1, min(MAX_RESULTS_PER_QUERY, int(num))),
        "start": max(1, int(start)),
    }
    if lang:
        params["lr"] = f"lang_{lang}"

    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(ENDPOINT, params=params, timeout=timeout)
    except httpx.TimeoutException as exc:
        return SearchResponse(
            query=q, total_results=None, search_time=None, results=[],
            fetched_at=fetched_at, status="timeout", error=str(exc),
        )
    except Exception as exc:  # noqa: BLE001
        log.exception("google_search_network_error q=%r", q)
        return SearchResponse(
            query=q, total_results=None, search_time=None, results=[],
            fetched_at=fetched_at, status="http_error", error=str(exc),
        )

    if r.status_code != 200:
        detail = r.text[:500] if r.text else f"HTTP {r.status_code}"
        log.warning("google_search_http_error status=%s body=%s", r.status_code, detail)
        return SearchResponse(
            query=q, total_results=None, search_time=None, results=[],
            fetched_at=fetched_at, status="http_error",
            error=f"HTTP {r.status_code}: {detail}",
        )

    data = r.json()
    items = data.get("items") or []
    search_info = data.get("searchInformation") or {}

    results = [
        SearchResult(
            title=str(it.get("title") or ""),
            link=str(it.get("link") or ""),
            snippet=str(it.get("snippet") or "").replace("\n", " ").strip(),
            display_link=str(it.get("displayLink") or ""),
            formatted_url=str(it.get("formattedUrl") or it.get("link") or ""),
        )
        for it in items
    ]

    total = search_info.get("totalResults")
    try:
        total_int = int(total) if total is not None else None
    except (ValueError, TypeError):
        total_int = None

    return SearchResponse(
        query=q,
        total_results=total_int,
        search_time=float(search_info.get("searchTime") or 0) or None,
        results=results,
        fetched_at=fetched_at,
        status="ok",
    )


# ── CLI ─────────────────────────────────────────────────────────
async def _main(argv: list[str]) -> int:
    import json
    if len(argv) < 2:
        print("usage: python -m auto_client_acquisition.connectors.google_search '<query>' [--site=example.com] [--num=10] [--lang=ar]")
        return 1

    query = argv[1]
    site = None
    num = 10
    lang = None
    for a in argv[2:]:
        if a.startswith("--site="):
            site = a.split("=", 1)[1]
        elif a.startswith("--num="):
            num = int(a.split("=", 1)[1])
        elif a.startswith("--lang="):
            lang = a.split("=", 1)[1]

    resp = await google_search(query, num=num, site=site, lang=lang)
    print(json.dumps(resp.to_dict(), ensure_ascii=False, indent=2))
    return 0 if resp.status == "ok" else 2


if __name__ == "__main__":
    import sys
    raise SystemExit(asyncio.run(_main(sys.argv)))
