"""CrawlerProvider chain — Firecrawl → RequestsBs4 (always)."""

from __future__ import annotations

import logging
import os
import re
from typing import Any, Protocol, runtime_checkable

import httpx

from auto_client_acquisition.providers.base import ProviderResult

log = logging.getLogger(__name__)

UA = "DealixBot/1.0 (+https://dealix.me) — public-pages only"

_SCRIPT_RE = re.compile(r"<(?:script|style)\b[^>]*>.*?</(?:script|style)>", re.IGNORECASE | re.DOTALL)
_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")
_TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)


def _html_to_text(html: str, max_chars: int = 12000) -> str:
    cleaned = _SCRIPT_RE.sub(" ", html or "")
    cleaned = _TAG_RE.sub(" ", cleaned)
    cleaned = _WS_RE.sub(" ", cleaned).strip()
    return cleaned[:max_chars]


@runtime_checkable
class CrawlerProvider(Protocol):
    name: str

    def is_available(self) -> bool: ...

    async def fetch(self, url: str, *, timeout: float = 12.0) -> ProviderResult: ...


class FirecrawlProvider:
    name = "firecrawl"

    def is_available(self) -> bool:
        return bool(os.getenv("FIRECRAWL_API_KEY", "").strip())

    async def fetch(self, url: str, *, timeout: float = 15.0) -> ProviderResult:
        api_key = os.getenv("FIRECRAWL_API_KEY", "").strip()
        if not api_key:
            return ProviderResult(provider=self.name, status="no_key")
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                r = await client.post(
                    "https://api.firecrawl.dev/v1/scrape",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    },
                    json={"url": url, "formats": ["markdown"], "onlyMainContent": True},
                )
        except Exception as exc:  # noqa: BLE001
            return ProviderResult(provider=self.name, status="http_error", error=str(exc))
        if r.status_code != 200:
            return ProviderResult(
                provider=self.name, status="http_error",
                error=f"HTTP {r.status_code}: {r.text[:200]}",
            )
        body = r.json() or {}
        data: dict[str, Any] = body.get("data") or body
        markdown = str(data.get("markdown") or "")[:12000]
        meta = data.get("metadata") or {}
        return ProviderResult(
            provider=self.name, status="ok",
            data={
                "url": url,
                "title": str(meta.get("title") or ""),
                "description": str(meta.get("description") or ""),
                "text": markdown, "html": None, "headers": {},
            },
        )


class RequestsBs4Provider:
    name = "requests_bs4"

    def is_available(self) -> bool:
        return True

    async def fetch(self, url: str, *, timeout: float = 12.0) -> ProviderResult:
        try:
            async with httpx.AsyncClient(
                timeout=timeout,
                headers={"User-Agent": UA, "Accept-Language": "ar,en"},
                follow_redirects=True,
            ) as client:
                r = await client.get(url)
        except httpx.TimeoutException as exc:
            return ProviderResult(provider=self.name, status="timeout", error=str(exc))
        except Exception as exc:  # noqa: BLE001
            return ProviderResult(provider=self.name, status="http_error", error=str(exc))
        if r.status_code >= 400:
            return ProviderResult(provider=self.name, status="http_error", error=f"HTTP {r.status_code}")
        html = r.text or ""
        text = _html_to_text(html)
        m = _TITLE_RE.search(html)
        title = (m.group(1) if m else "").strip()[:300]
        return ProviderResult(
            provider=self.name, status="ok",
            data={
                "url": str(r.url), "title": title, "description": "",
                "text": text, "html": html, "headers": dict(r.headers),
            },
        )


def get_crawler_chain() -> list[CrawlerProvider]:
    return [FirecrawlProvider(), RequestsBs4Provider()]


async def fetch_with_chain(url: str, *, timeout: float = 12.0) -> ProviderResult:
    last: ProviderResult | None = None
    for p in get_crawler_chain():
        if not p.is_available():
            continue
        result = await p.fetch(url, timeout=timeout)
        if result.status == "ok":
            return result
        last = result
    return last or ProviderResult(provider="none", status="empty")
