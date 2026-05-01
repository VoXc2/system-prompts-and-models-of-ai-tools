"""
Google Places (Maps) connector — Saudi local lead engine.

Uses GOOGLE_MAPS_API_KEY env var (set in Railway).
Powers /leads/discover/local endpoint for clinics, real-estate, training,
agencies, restaurants, retail — fastest sectors to a paid pilot.

Docs:
- Text Search: https://developers.google.com/maps/documentation/places/web-service/text-search
- Place Details: https://developers.google.com/maps/documentation/places/web-service/details

Returns Saudi-normalized leads. Per Google Maps Platform terms, we store
place_id (allowed) + ephemeral details (refreshed on demand).
"""

from __future__ import annotations

import asyncio
import logging
import os
import re
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any

import httpx

log = logging.getLogger(__name__)

TEXT_SEARCH_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"
PLACE_DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"

# Saudi cities + region tuples for biased search
SAUDI_CITIES = {
    "riyadh": ("الرياض", "Riyadh"),
    "jeddah": ("جدة", "Jeddah"),
    "mecca": ("مكة", "Mecca"),
    "medina": ("المدينة", "Medina"),
    "dammam": ("الدمام", "Dammam"),
    "khobar": ("الخبر", "Khobar"),
    "dhahran": ("الظهران", "Dhahran"),
    "taif": ("الطائف", "Taif"),
    "abha": ("أبها", "Abha"),
    "tabuk": ("تبوك", "Tabuk"),
    "buraidah": ("بريدة", "Buraidah"),
    "khamis_mushait": ("خميس مشيط", "Khamis Mushait"),
    "hail": ("حائل", "Hail"),
    "najran": ("نجران", "Najran"),
    "jubail": ("الجبيل", "Jubail"),
    "yanbu": ("ينبع", "Yanbu"),
}

# Saudi-targeted industry → query patterns (Arabic + English)
INDUSTRY_QUERIES: dict[str, list[str]] = {
    "dental_clinic": ["عيادة أسنان", "مجمع طبي أسنان", "dental clinic"],
    "medical_clinic": ["عيادة طبية", "مجمع طبي", "polyclinic", "medical center"],
    "cosmetic_clinic": ["عيادة تجميل", "مركز تجميل", "cosmetic clinic", "aesthetic clinic"],
    "real_estate": ["مكتب عقار", "مكاتب عقارية", "real estate office"],
    "real_estate_developer": ["مطور عقاري", "real estate developer", "شركة تطوير عقاري"],
    "training_center": ["مركز تدريب", "مؤسسة تدريب", "training center"],
    "marketing_agency": ["وكالة تسويق", "وكالة تسويق رقمي", "digital marketing agency"],
    "law_firm": ["مكتب محاماة", "محامي", "law firm"],
    "accounting_firm": ["مكتب محاسبة", "محاسب قانوني", "accounting office"],
    "consulting_firm": ["شركة استشارات", "consulting", "management consulting"],
    "restaurant": ["مطعم", "restaurant"],
    "cafe": ["كوفي", "cafe", "coffee shop"],
    "retail_store": ["متجر", "retail shop"],
    "fitness_gym": ["نادي رياضي", "صالة رياضية", "gym", "fitness center"],
    "salon_spa": ["صالون", "spa", "salon"],
    "auto_dealer": ["معرض سيارات", "car dealer"],
    "logistics": ["شركة شحن", "logistics", "freight forwarder"],
    "construction": ["مقاولات", "شركة مقاولات", "construction company"],
    "interior_design": ["تصميم داخلي", "interior design"],
    "school_private": ["مدرسة خاصة", "private school"],
    "tourism_agency": ["وكالة سياحة", "travel agency"],
}

_NON_DIGIT = re.compile(r"\D+")


def _normalize_saudi_phone(raw: str | None) -> str | None:
    if not raw:
        return None
    digits = _NON_DIGIT.sub("", raw)
    if not digits:
        return None
    if digits.startswith("00966"):
        digits = digits[2:]
    if digits.startswith("966") and len(digits) >= 11:
        return f"+{digits[:12]}"
    if digits.startswith("05") and len(digits) == 10:
        return f"+966{digits[1:]}"
    if digits.startswith("5") and len(digits) == 9:
        return f"+966{digits}"
    if digits.startswith("0") and len(digits) == 10:
        return f"+966{digits[1:]}"
    if not raw.startswith("+"):
        return f"+{digits}"
    return raw.strip()


@dataclass
class LocalLead:
    place_id: str
    name: str
    address: str
    phone: str | None
    website: str | None
    rating: float | None
    ratings_count: int | None
    types: list[str]
    business_status: str | None
    lat: float | None
    lng: float | None
    city_query: str | None = None
    industry: str | None = None
    google_maps_url: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class LocalDiscoveryResponse:
    industry: str
    city: str
    query_used: str
    total: int
    results: list[LocalLead] = field(default_factory=list)
    next_page_token: str | None = None
    fetched_at: str = ""
    status: str = "ok"
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "industry": self.industry,
            "city": self.city,
            "query_used": self.query_used,
            "total": self.total,
            "results": [r.to_dict() for r in self.results],
            "next_page_token": self.next_page_token,
            "fetched_at": self.fetched_at,
            "status": self.status,
            "error": self.error,
        }


_DETAIL_FIELDS = ",".join([
    "name",
    "formatted_address",
    "international_phone_number",
    "formatted_phone_number",
    "website",
    "rating",
    "user_ratings_total",
    "types",
    "business_status",
    "geometry/location",
    "place_id",
    "url",
    "opening_hours",
])


async def _fetch_place_details(
    client: httpx.AsyncClient,
    api_key: str,
    place_id: str,
    *,
    timeout: float = 10.0,
) -> dict[str, Any] | None:
    params = {
        "place_id": place_id,
        "fields": _DETAIL_FIELDS,
        "key": api_key,
        "language": "ar",
        "region": "sa",
    }
    try:
        r = await client.get(PLACE_DETAILS_URL, params=params, timeout=timeout)
    except Exception as exc:  # noqa: BLE001
        log.warning("place_details_error place_id=%s err=%s", place_id, exc)
        return None
    if r.status_code != 200:
        return None
    payload = r.json() or {}
    if payload.get("status") != "OK":
        return None
    return payload.get("result") or None


async def discover_local(
    industry: str,
    city: str,
    *,
    max_results: int = 20,
    page_token: str | None = None,
    hydrate_details: bool = True,
    custom_query: str | None = None,
    timeout: float = 12.0,
) -> LocalDiscoveryResponse:
    api_key = os.getenv("GOOGLE_MAPS_API_KEY", "").strip()
    fetched_at = datetime.now(timezone.utc).isoformat()

    if not api_key:
        return LocalDiscoveryResponse(
            industry=industry,
            city=city,
            query_used="",
            total=0,
            fetched_at=fetched_at,
            status="no_key",
            error="GOOGLE_MAPS_API_KEY not set in environment",
        )

    city_pair = SAUDI_CITIES.get(city.lower())
    if city_pair:
        city_ar, _city_en = city_pair
    else:
        city_ar = city

    if custom_query:
        query = f"{custom_query} {city_ar}"
    else:
        patterns = INDUSTRY_QUERIES.get(industry.lower())
        if not patterns:
            return LocalDiscoveryResponse(
                industry=industry, city=city, query_used="", total=0,
                fetched_at=fetched_at, status="unknown_industry",
                error=f"Industry '{industry}' not in INDUSTRY_QUERIES. "
                      f"Pass custom_query, or pick from: {sorted(INDUSTRY_QUERIES.keys())}",
            )
        query = f"{patterns[0]} {city_ar}"

    base_params: dict[str, Any] = {
        "query": query,
        "key": api_key,
        "language": "ar",
        "region": "sa",
    }
    if page_token:
        base_params["pagetoken"] = page_token

    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(TEXT_SEARCH_URL, params=base_params, timeout=timeout)
            if r.status_code != 200:
                return LocalDiscoveryResponse(
                    industry=industry, city=city, query_used=query, total=0,
                    fetched_at=fetched_at, status="http_error",
                    error=f"HTTP {r.status_code}: {r.text[:300]}",
                )
            data = r.json() or {}
            api_status = data.get("status")
            if api_status not in {"OK", "ZERO_RESULTS"}:
                return LocalDiscoveryResponse(
                    industry=industry, city=city, query_used=query, total=0,
                    fetched_at=fetched_at, status="http_error",
                    error=f"Places API status={api_status}: {data.get('error_message', '')}",
                )

            raw_results: list[dict[str, Any]] = data.get("results") or []
            next_token = data.get("next_page_token")

            if next_token and len(raw_results) < max_results:
                await asyncio.sleep(2.1)
                r2 = await client.get(
                    TEXT_SEARCH_URL,
                    params={"pagetoken": next_token, "key": api_key},
                    timeout=timeout,
                )
                if r2.status_code == 200:
                    d2 = r2.json() or {}
                    if d2.get("status") == "OK":
                        raw_results.extend(d2.get("results") or [])
                        next_token = d2.get("next_page_token")

            raw_results = raw_results[:max_results]

            details_map: dict[str, dict[str, Any]] = {}
            if hydrate_details and raw_results:
                tasks = [
                    _fetch_place_details(client, api_key, p.get("place_id", ""), timeout=timeout)
                    for p in raw_results
                    if p.get("place_id")
                ]
                fetched = await asyncio.gather(*tasks, return_exceptions=False)
                for det in fetched:
                    if det and det.get("place_id"):
                        details_map[det["place_id"]] = det

    except httpx.TimeoutException as exc:
        return LocalDiscoveryResponse(
            industry=industry, city=city, query_used=query, total=0,
            fetched_at=fetched_at, status="timeout", error=str(exc),
        )
    except Exception as exc:  # noqa: BLE001
        log.exception("places_text_search_error q=%r", query)
        return LocalDiscoveryResponse(
            industry=industry, city=city, query_used=query, total=0,
            fetched_at=fetched_at, status="http_error", error=str(exc),
        )

    leads: list[LocalLead] = []
    for p in raw_results:
        place_id = str(p.get("place_id") or "")
        det = details_map.get(place_id) or {}
        geom = (det.get("geometry") or {}).get("location") or (
            (p.get("geometry") or {}).get("location") or {}
        )
        phone_raw = (
            det.get("international_phone_number")
            or det.get("formatted_phone_number")
            or None
        )
        leads.append(
            LocalLead(
                place_id=place_id,
                name=str(det.get("name") or p.get("name") or ""),
                address=str(det.get("formatted_address") or p.get("formatted_address") or ""),
                phone=_normalize_saudi_phone(phone_raw),
                website=str(det.get("website")) if det.get("website") else None,
                rating=float(p.get("rating")) if p.get("rating") is not None else None,
                ratings_count=int(p.get("user_ratings_total"))
                if p.get("user_ratings_total") is not None else None,
                types=list(p.get("types") or det.get("types") or []),
                business_status=str(det.get("business_status") or p.get("business_status") or "")
                or None,
                lat=float(geom["lat"]) if isinstance(geom, dict) and "lat" in geom else None,
                lng=float(geom["lng"]) if isinstance(geom, dict) and "lng" in geom else None,
                city_query=city,
                industry=industry,
                google_maps_url=str(det.get("url")) if det.get("url") else None,
            )
        )

    return LocalDiscoveryResponse(
        industry=industry, city=city, query_used=query,
        total=len(leads), results=leads, next_page_token=next_token,
        fetched_at=fetched_at, status="ok",
    )


async def _main(argv: list[str]) -> int:
    import json
    if len(argv) < 3:
        print("usage: python -m auto_client_acquisition.connectors.google_maps "
              "<industry> <city> [--max=20] [--no-details] [--custom='free text']")
        print(f"Industries: {sorted(INDUSTRY_QUERIES.keys())}")
        print(f"Cities: {sorted(SAUDI_CITIES.keys())}")
        return 1
    industry = argv[1]
    city = argv[2]
    max_results = 20
    hydrate = True
    custom = None
    for a in argv[3:]:
        if a.startswith("--max="):
            max_results = int(a.split("=", 1)[1])
        elif a == "--no-details":
            hydrate = False
        elif a.startswith("--custom="):
            custom = a.split("=", 1)[1]
    resp = await discover_local(
        industry, city, max_results=max_results,
        hydrate_details=hydrate, custom_query=custom,
    )
    print(json.dumps(resp.to_dict(), ensure_ascii=False, indent=2))
    return 0 if resp.status == "ok" else 2


if __name__ == "__main__":
    import sys
    raise SystemExit(asyncio.run(_main(sys.argv)))
