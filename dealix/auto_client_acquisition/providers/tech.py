"""TechProvider chain — internal Saudi-tuned detector → Wappalyzer (optional)."""

from __future__ import annotations

import logging
import os
from typing import Any, Protocol, runtime_checkable

import httpx

from auto_client_acquisition.connectors.tech_detect import detect_stack
from auto_client_acquisition.providers.base import ProviderResult

log = logging.getLogger(__name__)


@runtime_checkable
class TechProvider(Protocol):
    name: str

    def is_available(self) -> bool: ...

    async def detect(self, url: str) -> ProviderResult: ...


class InternalTechProvider:
    name = "internal"

    def is_available(self) -> bool:
        return True

    async def detect(self, url: str) -> ProviderResult:
        try:
            result = await detect_stack(url)
        except Exception as exc:  # noqa: BLE001
            return ProviderResult(provider=self.name, status="http_error", error=str(exc))
        if not isinstance(result, dict):
            return ProviderResult(
                provider=self.name, status="ok",
                data={"url": url, "detections": [], "raw": result},
            )
        return ProviderResult(provider=self.name, status="ok", data=result)


class WappalyzerProvider:
    name = "wappalyzer"

    def is_available(self) -> bool:
        return bool(os.getenv("WAPPALYZER_API_KEY", "").strip())

    async def detect(self, url: str) -> ProviderResult:
        api_key = os.getenv("WAPPALYZER_API_KEY", "").strip()
        if not api_key:
            return ProviderResult(provider=self.name, status="no_key")
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                r = await client.get(
                    "https://api.wappalyzer.com/v2/lookup/",
                    params={"urls": url}, headers={"x-api-key": api_key},
                )
        except Exception as exc:  # noqa: BLE001
            return ProviderResult(provider=self.name, status="http_error", error=str(exc))
        if r.status_code != 200:
            return ProviderResult(
                provider=self.name, status="http_error",
                error=f"HTTP {r.status_code}: {r.text[:200]}",
            )
        items = r.json() or []
        first: dict[str, Any] = items[0] if items else {}
        return ProviderResult(
            provider=self.name, status="ok",
            data={"url": url, "technologies": first.get("technologies") or [], "raw": first},
        )


def get_tech_chain() -> list[TechProvider]:
    return [InternalTechProvider(), WappalyzerProvider()]


async def detect_with_chain(url: str) -> ProviderResult:
    chain = get_tech_chain()
    primary = await chain[0].detect(url)
    if not chain[1].is_available():
        return primary
    secondary = await chain[1].detect(url)
    if secondary.status != "ok":
        return primary
    merged: dict[str, Any] = dict(primary.data or {})
    merged["wappalyzer"] = secondary.data
    return ProviderResult(provider="internal+wappalyzer", status="ok", data=merged)
