"""SearchProvider chain — Google CSE → Tavily → Static fallback."""

from __future__ import annotations

import logging
import os
from typing import Any, Protocol, runtime_checkable

import httpx

from auto_client_acquisition.connectors.google_search import google_search
from auto_client_acquisition.providers.base import ProviderResult, now_iso

log = logging.getLogger(__name__)


@runtime_checkable
class SearchProvider(Protocol):
    name: str

    def is_available(self) -> bool: ...

    async def search(
        self, query: str, *, num: int = 10,
        site: str | None = None, lang: str | None = None,
    ) -> ProviderResult: ...


class GoogleCSEProvider:
    name = "google_cse"

    def is_available(self) -> bool:
        return bool(
            os.getenv("GOOGLE_SEARCH_API_KEY", "").strip()
            and os.getenv("GOOGLE_SEARCH_CX", "").strip()
        )

    async def search(
        self, query: str, *, num: int = 10,
        site: str | None = None, lang: str | None = None,
    ) -> ProviderResult:
        resp = await google_search(query, num=num, site=site, lang=lang)
        if resp.status == "ok":
            return ProviderResult(
                provider=self.name, status="ok",
                data={
                    "query": resp.query,
                    "total_results": resp.total_results,
                    "results": [r.to_dict() for r in resp.results],
                },
            )
        return ProviderResult(provider=self.name, status=resp.status, error=resp.error)


class TavilyProvider:
    name = "tavily"

    def is_available(self) -> bool:
        return bool(os.getenv("TAVILY_API_KEY", "").strip())

    async def search(
        self, query: str, *, num: int = 10,
        site: str | None = None, lang: str | None = None,
    ) -> ProviderResult:
        api_key = os.getenv("TAVILY_API_KEY", "").strip()
        if not api_key:
            return ProviderResult(provider=self.name, status="no_key")
        q = f"{query} site:{site}" if site else query
        payload: dict[str, Any] = {
            "api_key": api_key, "query": q,
            "max_results": max(1, min(20, int(num))),
            "search_depth": "basic",
        }
        try:
            async with httpx.AsyncClient(timeout=12.0) as client:
                r = await client.post("https://api.tavily.com/search", json=payload)
        except Exception as exc:  # noqa: BLE001
            return ProviderResult(provider=self.name, status="http_error", error=str(exc))
        if r.status_code != 200:
            return ProviderResult(
                provider=self.name, status="http_error",
                error=f"HTTP {r.status_code}: {r.text[:200]}",
            )
        data = r.json() or {}
        items = data.get("results") or []
        return ProviderResult(
            provider=self.name, status="ok",
            data={
                "query": q, "total_results": len(items),
                "results": [
                    {
                        "title": str(it.get("title") or ""),
                        "link": str(it.get("url") or ""),
                        "snippet": str(it.get("content") or "")[:500],
                        "display_link": str(it.get("url") or ""),
                        "formatted_url": str(it.get("url") or ""),
                    }
                    for it in items
                ],
            },
        )


class StaticSearchProvider:
    name = "static_fallback"

    def is_available(self) -> bool:
        return True

    async def search(
        self, query: str, *, num: int = 10,
        site: str | None = None, lang: str | None = None,
    ) -> ProviderResult:
        return ProviderResult(
            provider=self.name, status="ok",
            data={
                "query": query, "total_results": 0, "results": [],
                "hint": "No SearchProvider configured. Set GOOGLE_SEARCH_API_KEY+CX or TAVILY_API_KEY.",
            },
        )


def get_search_chain() -> list[SearchProvider]:
    return [GoogleCSEProvider(), TavilyProvider(), StaticSearchProvider()]


async def search_with_chain(
    query: str, *, num: int = 10,
    site: str | None = None, lang: str | None = None,
) -> ProviderResult:
    last: ProviderResult | None = None
    for p in get_search_chain():
        if not p.is_available():
            continue
        result = await p.search(query, num=num, site=site, lang=lang)
        if result.status == "ok":
            return result
        last = result
        log.info("search_chain_fallback_from=%s status=%s", p.name, result.status)
    return last or ProviderResult(provider="none", status="empty", fetched_at=now_iso())
