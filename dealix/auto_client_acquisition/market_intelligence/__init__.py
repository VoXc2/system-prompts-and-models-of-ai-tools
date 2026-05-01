"""
Saudi Market Intelligence — live signal detectors + sector/city radar.

Detectors are pure functions over raw observations (jobs feeds, website
diffs, ad activity, tender feeds, social activity). Each returns
SignalDetection objects that flow into the Why-Now? engine and the
Daily Growth Run workflow.
"""

from auto_client_acquisition.market_intelligence.signal_detectors import (
    SIGNAL_TYPES,
    SignalDetection,
    detect_ads_signal,
    detect_funding_signal,
    detect_hiring_signal,
    detect_tender_signal,
    detect_website_change,
)
from auto_client_acquisition.market_intelligence.sector_pulse import (
    SectorPulse,
    build_sector_pulse,
    rank_hot_sectors,
)
from auto_client_acquisition.market_intelligence.city_heatmap import (
    CityHeat,
    build_city_heatmap,
    top_hot_cities,
)
from auto_client_acquisition.market_intelligence.opportunity_feed import (
    Opportunity,
    build_opportunity_feed,
)

__all__ = [
    "SIGNAL_TYPES",
    "SignalDetection",
    "detect_hiring_signal",
    "detect_website_change",
    "detect_ads_signal",
    "detect_funding_signal",
    "detect_tender_signal",
    "SectorPulse",
    "build_sector_pulse",
    "rank_hot_sectors",
    "CityHeat",
    "build_city_heatmap",
    "top_hot_cities",
    "Opportunity",
    "build_opportunity_feed",
]
