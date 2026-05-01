"""
City Heatmap — Saudi-specific buying intent by city.

Aggregates signals per city + per sector. Renders as the heatmap on the
Command Center's Saudi Buying Intent Map tile.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

from auto_client_acquisition.market_intelligence.signal_detectors import SignalDetection

SAUDI_CITIES: tuple[str, ...] = (
    "الرياض",
    "جدة",
    "الدمام",
    "الخبر",
    "مكة",
    "المدينة",
    "أبها",
    "القصيم",
    "تبوك",
    "حائل",
)


@dataclass
class CityHeat:
    """Heat for a city = volume + diversity of signals."""

    city: str
    n_companies: int
    n_signals: int
    n_sectors: int
    heat_score: int  # 0..100
    bucket: str      # cool / warm / hot / blazing
    top_sector: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "city": self.city,
            "n_companies": self.n_companies,
            "n_signals": self.n_signals,
            "n_sectors": self.n_sectors,
            "heat_score": self.heat_score,
            "bucket": self.bucket,
            "top_sector": self.top_sector,
        }


def _bucket(score: int) -> str:
    if score >= 80:
        return "blazing"
    if score >= 50:
        return "hot"
    if score >= 25:
        return "warm"
    return "cool"


def build_city_heatmap(
    *,
    signals_by_company: dict[str, list[SignalDetection]],
    company_metadata: dict[str, dict[str, str]],
) -> list[CityHeat]:
    """
    Build heatmap from per-company signals + company metadata
    (which gives us the city + sector for each company).

    company_metadata: {company_id: {"city": "...", "sector": "..."}}
    """
    by_city: dict[str, dict[str, Any]] = defaultdict(
        lambda: {"companies": set(), "signals": 0, "sectors": defaultdict(int)}
    )
    for company_id, signals in signals_by_company.items():
        meta = company_metadata.get(company_id) or {}
        city = meta.get("city")
        sector = meta.get("sector")
        if not city:
            continue
        by_city[city]["companies"].add(company_id)
        by_city[city]["signals"] += len(signals)
        if sector:
            by_city[city]["sectors"][sector] += len(signals)

    heatmaps: list[CityHeat] = []
    for city, data in by_city.items():
        n_companies = len(data["companies"])
        n_signals = data["signals"]
        sectors = data["sectors"]
        n_sectors = len(sectors)
        # Heat score: log-ish — 50 signals across 5 sectors ≈ 100
        score = min(100, int(n_signals * 1.5 + n_sectors * 8))
        top_sector = max(sectors.items(), key=lambda x: x[1])[0] if sectors else None
        heatmaps.append(CityHeat(
            city=city,
            n_companies=n_companies,
            n_signals=n_signals,
            n_sectors=n_sectors,
            heat_score=score,
            bucket=_bucket(score),
            top_sector=top_sector,
        ))
    heatmaps.sort(key=lambda h: h.heat_score, reverse=True)
    return heatmaps


def top_hot_cities(*, heatmaps: list[CityHeat], n: int = 5) -> list[CityHeat]:
    return [h for h in heatmaps if h.bucket in ("hot", "blazing")][:n]
