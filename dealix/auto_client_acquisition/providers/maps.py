"""MapsProvider chain — Google Places → SerpApi → Apify → Static."""

from __future__ import annotations

import logging
import os
from typing import Protocol, runtime_checkable

from auto_client_acquisition.connectors.google_maps import discover_local
from auto_client_acquisition.providers.base import ProviderResult

log = logging.getLogger(__name__)


@runtime_checkable
class MapsProvider(Protocol):
    name: str

    def is_available(self) -> bool: ...

    async def discover(
        self, *, industry: str, city: str, max_results: int = 20,
        page_token: str | None = None, hydrate_details: bool = True,
        custom_query: str | None = None,
    ) -> ProviderResult: ...


class GooglePlacesProvider:
    name = "google_places"

    def is_available(self) -> bool:
        return bool(os.getenv("GOOGLE_MAPS_API_KEY", "").strip())

    async def discover(
        self, *, industry: str, city: str, max_results: int = 20,
        page_token: str | None = None, hydrate_details: bool = True,
        custom_query: str | None = None,
    ) -> ProviderResult:
        resp = await discover_local(
            industry=industry, city=city, max_results=max_results,
            page_token=page_token, hydrate_details=hydrate_details,
            custom_query=custom_query,
        )
        if resp.status == "ok":
            return ProviderResult(provider=self.name, status="ok", data=resp.to_dict())
        return ProviderResult(provider=self.name, status=resp.status, error=resp.error)


class SerpApiMapsProvider:
    name = "serpapi_maps"

    def is_available(self) -> bool:
        return bool(os.getenv("SERPAPI_API_KEY", "").strip())

    async def discover(self, **_: object) -> ProviderResult:
        return ProviderResult(
            provider=self.name, status="unsupported",
            error="SerpApi adapter not yet implemented — stub only.",
        )


class ApifyMapsProvider:
    name = "apify_maps"

    def is_available(self) -> bool:
        return bool(os.getenv("APIFY_TOKEN", "").strip())

    async def discover(self, **_: object) -> ProviderResult:
        return ProviderResult(
            provider=self.name, status="unsupported",
            error="Apify adapter not yet implemented — stub only.",
        )


class StaticMapsProvider:
    name = "static_fallback"

    def is_available(self) -> bool:
        return True

    async def discover(
        self, *, industry: str, city: str, max_results: int = 20,
        page_token: str | None = None, hydrate_details: bool = True,
        custom_query: str | None = None,
    ) -> ProviderResult:
        return ProviderResult(
            provider=self.name, status="ok",
            data={
                "industry": industry, "city": city,
                "query_used": custom_query or industry, "total": 0, "results": [],
                "hint": "No MapsProvider configured. Set GOOGLE_MAPS_API_KEY (Places API enabled).",
            },
        )


def get_maps_chain() -> list[MapsProvider]:
    return [
        GooglePlacesProvider(), SerpApiMapsProvider(),
        ApifyMapsProvider(), StaticMapsProvider(),
    ]


async def discover_with_chain(
    *, industry: str, city: str, max_results: int = 20,
    page_token: str | None = None, hydrate_details: bool = True,
    custom_query: str | None = None,
) -> ProviderResult:
    last: ProviderResult | None = None
    for p in get_maps_chain():
        if not p.is_available():
            continue
        result = await p.discover(
            industry=industry, city=city, max_results=max_results,
            page_token=page_token, hydrate_details=hydrate_details,
            custom_query=custom_query,
        )
        if result.status == "ok":
            return result
        last = result
        log.info("maps_chain_fallback_from=%s status=%s", p.name, result.status)
    return last or ProviderResult(provider="none", status="empty")
