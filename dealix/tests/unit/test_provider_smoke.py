"""
Smoke tests for the provider adapter chains.

These tests run without any external API keys — they exercise:
- Static fallback behavior
- is_available() gating
- ProviderResult shape
- Chain ordering

Pyests for live providers are gated by env-key presence.
"""

from __future__ import annotations

import os

import pytest

from auto_client_acquisition.providers.base import ProviderResult
from auto_client_acquisition.providers.search import (
    GoogleCSEProvider, StaticSearchProvider, TavilyProvider,
    get_search_chain, search_with_chain,
)
from auto_client_acquisition.providers.maps import (
    ApifyMapsProvider, GooglePlacesProvider, SerpApiMapsProvider,
    StaticMapsProvider, discover_with_chain, get_maps_chain,
)
from auto_client_acquisition.providers.crawler import (
    FirecrawlProvider, RequestsBs4Provider, get_crawler_chain,
)
from auto_client_acquisition.providers.tech import (
    InternalTechProvider, WappalyzerProvider, get_tech_chain,
)
from auto_client_acquisition.providers.email_intel import (
    AbstractEmailProvider, HunterProvider, NoopEmailIntelProvider,
    get_email_intel_chain,
)


# ── ProviderResult shape ─────────────────────────────────────────
def test_provider_result_shape():
    pr = ProviderResult(provider="x", status="ok", data={"a": 1})
    d = pr.to_dict()
    assert set(d.keys()) == {"provider", "status", "data", "error", "fetched_at"}
    assert d["provider"] == "x"
    assert d["status"] == "ok"


# ── SearchProvider chain ─────────────────────────────────────────
def test_search_chain_order():
    chain = get_search_chain()
    assert isinstance(chain[0], GoogleCSEProvider)
    assert isinstance(chain[1], TavilyProvider)
    assert isinstance(chain[-1], StaticSearchProvider)


def test_static_search_always_available():
    assert StaticSearchProvider().is_available() is True


@pytest.mark.asyncio
async def test_static_search_returns_ok_empty():
    result = await StaticSearchProvider().search("dealix saudi")
    assert result.status == "ok"
    assert result.data["results"] == []
    assert "hint" in result.data


@pytest.mark.asyncio
async def test_search_with_chain_no_keys_returns_static():
    # Force no keys
    keys = ("GOOGLE_SEARCH_API_KEY", "GOOGLE_SEARCH_CX", "TAVILY_API_KEY")
    saved = {k: os.environ.pop(k, None) for k in keys}
    try:
        result = await search_with_chain("test query")
        assert result.status == "ok"
        assert result.provider == "static_fallback"
    finally:
        for k, v in saved.items():
            if v is not None:
                os.environ[k] = v


# ── MapsProvider chain ───────────────────────────────────────────
def test_maps_chain_order():
    chain = get_maps_chain()
    assert isinstance(chain[0], GooglePlacesProvider)
    assert isinstance(chain[1], SerpApiMapsProvider)
    assert isinstance(chain[2], ApifyMapsProvider)
    assert isinstance(chain[-1], StaticMapsProvider)


@pytest.mark.asyncio
async def test_static_maps_returns_hint():
    result = await StaticMapsProvider().discover(
        industry="dental_clinic", city="riyadh",
    )
    assert result.status == "ok"
    assert result.data["total"] == 0
    assert "GOOGLE_MAPS_API_KEY" in result.data["hint"]


@pytest.mark.asyncio
async def test_discover_with_chain_no_keys():
    keys = ("GOOGLE_MAPS_API_KEY", "SERPAPI_API_KEY", "APIFY_TOKEN")
    saved = {k: os.environ.pop(k, None) for k in keys}
    try:
        result = await discover_with_chain(industry="dental_clinic", city="riyadh")
        assert result.status == "ok"
        assert result.provider == "static_fallback"
    finally:
        for k, v in saved.items():
            if v is not None:
                os.environ[k] = v


# ── CrawlerProvider chain ────────────────────────────────────────
def test_crawler_chain_has_always_available_fallback():
    chain = get_crawler_chain()
    assert isinstance(chain[0], FirecrawlProvider)
    assert isinstance(chain[-1], RequestsBs4Provider)
    assert chain[-1].is_available() is True


# ── TechProvider chain ───────────────────────────────────────────
def test_tech_chain_internal_always_first():
    chain = get_tech_chain()
    assert isinstance(chain[0], InternalTechProvider)
    assert chain[0].is_available() is True
    assert isinstance(chain[1], WappalyzerProvider)


# ── EmailIntelProvider chain ─────────────────────────────────────
def test_email_intel_chain_order():
    chain = get_email_intel_chain()
    assert isinstance(chain[0], HunterProvider)
    assert isinstance(chain[1], AbstractEmailProvider)
    assert isinstance(chain[-1], NoopEmailIntelProvider)
    assert chain[-1].is_available() is True


@pytest.mark.asyncio
async def test_noop_email_verify_uses_regex_only():
    result = await NoopEmailIntelProvider().verify("not-an-email")
    assert result.status == "ok"
    assert result.data["valid"] is False

    result = await NoopEmailIntelProvider().verify("sami@dealix.me")
    assert result.status == "ok"
    assert result.data["valid"] is True


# ── Live providers (gated) ───────────────────────────────────────
@pytest.mark.asyncio
@pytest.mark.skipif(
    not (os.getenv("GOOGLE_SEARCH_API_KEY") and os.getenv("GOOGLE_SEARCH_CX")),
    reason="GOOGLE_SEARCH_API_KEY+CX not set",
)
async def test_google_cse_live():
    result = await GoogleCSEProvider().search("dealix saudi B2B", num=3)
    assert result.status == "ok"
    assert isinstance(result.data["results"], list)


@pytest.mark.asyncio
@pytest.mark.skipif(
    not os.getenv("GOOGLE_MAPS_API_KEY"),
    reason="GOOGLE_MAPS_API_KEY not set",
)
async def test_google_places_live():
    result = await GooglePlacesProvider().discover(
        industry="dental_clinic", city="riyadh",
        max_results=3, hydrate_details=False,
    )
    assert result.status == "ok"
    assert "results" in result.data
