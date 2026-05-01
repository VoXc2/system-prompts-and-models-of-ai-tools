"""
Dealix provider adapters — chains with env-gated fallbacks.

Mental model:
    SearchProvider:  google_cse → tavily → static
    MapsProvider:    google_places → serpapi → apify → static
    CrawlerProvider: firecrawl → requests_bs4 (always)
    TechProvider:    internal (always) → wappalyzer (optional)
    EmailIntelProv:  hunter → abstract → noop
"""

from auto_client_acquisition.providers.base import (
    ProviderResult,
    ProviderUnavailable,
)
from auto_client_acquisition.providers.search import (
    GoogleCSEProvider,
    SearchProvider,
    StaticSearchProvider,
    TavilyProvider,
    get_search_chain,
    search_with_chain,
)
from auto_client_acquisition.providers.maps import (
    ApifyMapsProvider,
    GooglePlacesProvider,
    MapsProvider,
    SerpApiMapsProvider,
    StaticMapsProvider,
    discover_with_chain,
    get_maps_chain,
)
from auto_client_acquisition.providers.crawler import (
    CrawlerProvider,
    FirecrawlProvider,
    RequestsBs4Provider,
    fetch_with_chain,
    get_crawler_chain,
)
from auto_client_acquisition.providers.tech import (
    InternalTechProvider,
    TechProvider,
    WappalyzerProvider,
    detect_with_chain,
    get_tech_chain,
)
from auto_client_acquisition.providers.email_intel import (
    AbstractEmailProvider,
    EmailIntelProvider,
    HunterProvider,
    NoopEmailIntelProvider,
    find_emails_with_chain,
    get_email_intel_chain,
    verify_with_chain,
)

__all__ = [
    "ProviderResult", "ProviderUnavailable",
    "SearchProvider", "GoogleCSEProvider", "TavilyProvider", "StaticSearchProvider",
    "get_search_chain", "search_with_chain",
    "MapsProvider", "GooglePlacesProvider", "SerpApiMapsProvider", "ApifyMapsProvider",
    "StaticMapsProvider", "get_maps_chain", "discover_with_chain",
    "CrawlerProvider", "FirecrawlProvider", "RequestsBs4Provider",
    "get_crawler_chain", "fetch_with_chain",
    "TechProvider", "InternalTechProvider", "WappalyzerProvider",
    "get_tech_chain", "detect_with_chain",
    "EmailIntelProvider", "HunterProvider", "AbstractEmailProvider",
    "NoopEmailIntelProvider", "get_email_intel_chain",
    "find_emails_with_chain", "verify_with_chain",
]
