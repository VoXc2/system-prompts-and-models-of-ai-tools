"""
Dealix Lead Intelligence Engine — مصادر متعددة، دمج، إزالة تكرار، استيراد ملفات.
يستخدم واجهات رسمية (Google Places، SerpAPI، Google CSE، Bing) — لا كشط غير مصرّح به لـ LinkedIn؛
إشارات LinkedIn تُستخرج من نتائج بحث الويب العامة فقط (عناوين/مقتطفات).
"""

from __future__ import annotations

import asyncio
import csv
import io
import json
import logging
import re
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)

# ── Normalization ─────────────────────────────────────────────


def _norm_phone(p: str) -> str:
    if not p:
        return ""
    return re.sub(r"\D", "", p)


def _domain(url: str) -> str:
    if not url:
        return ""
    u = url.lower().strip()
    u = re.sub(r"^https?://(www\.)?", "", u)
    return u.split("/")[0]


def merge_dedupe(rows: list[dict]) -> list[dict]:
    """إزالة التكرار حسب الهاتف ثم النطاق ثم الاسم."""
    seen: set[str] = set()
    out: list[dict] = []
    for r in rows:
        ph = _norm_phone(r.get("phone") or "")
        dm = _domain(r.get("website") or "")
        nm = (r.get("name") or "").strip().lower()
        key = ph or (f"dom:{dm}" if dm else "") or (f"name:{nm}" if nm else "")
        if not key:
            key = f"row:{uuid.uuid4().hex[:12]}"
        if key in seen:
            continue
        seen.add(key)
        out.append(r)
    return out


# ── Google Places (Text Search + Details) ───────────────────


async def places_text_search(
    query: str,
    city: str,
    max_results: int,
    api_key: str,
) -> list[dict]:
    """بحث نصي في Google Places + تفاصيل الهاتف والموقع."""
    if not api_key:
        return []

    results: list[dict] = []
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    search_query = f"{query} في {city} السعودية"

    try:
        async with httpx.AsyncClient(timeout=25) as client:
            params: dict[str, str | int] = {
                "query": search_query,
                "key": api_key,
                "language": "ar",
                "region": "sa",
            }
            resp = await client.get(url, params=params)
            data = resp.json()
            places = data.get("results", [])[:max_results]

            for place in places:
                place_id = place.get("place_id", "")
                phone, website = "", ""
                if place_id:
                    dresp = await client.get(
                        "https://maps.googleapis.com/maps/api/place/details/json",
                        params={
                            "place_id": place_id,
                            "fields": "formatted_phone_number,international_phone_number,website,url",
                            "key": api_key,
                        },
                    )
                    det = dresp.json().get("result", {})
                    phone = det.get("international_phone_number") or det.get("formatted_phone_number") or ""
                    website = det.get("website", "")

                results.append(
                    {
                        "id": str(uuid.uuid4())[:10],
                        "source": "google_maps",
                        "name": place.get("name", ""),
                        "phone": phone.replace(" ", "") if phone else "",
                        "address": place.get("formatted_address", ""),
                        "city": city,
                        "rating": float(place.get("rating") or 0),
                        "website": website,
                        "maps_url": place.get("url", ""),
                        "snippet": "",
                        "confidence": 0.95 if phone else 0.5,
                        "status": "new",
                    }
                )
    except Exception as e:
        logger.exception("places_text_search: %s", e)

    return results


# ── SerpAPI (Google web, Google Maps engine) ─────────────────


async def serpapi_google_organic(q: str, hl: str = "ar", gl: str = "sa", num: int = 10) -> list[dict]:
    key = get_settings().SERPAPI_KEY or ""
    if not key:
        return []
    out: list[dict] = []
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.get(
                "https://serpapi.com/search.json",
                params={
                    "engine": "google",
                    "q": q,
                    "hl": hl,
                    "gl": gl,
                    "num": min(num, 20),
                    "api_key": key,
                },
            )
            data = r.json()
            for item in data.get("organic_results", [])[:num]:
                out.append(
                    {
                        "id": str(uuid.uuid4())[:10],
                        "source": "serp_google",
                        "name": item.get("title", "")[:200],
                        "phone": "",
                        "website": item.get("link", ""),
                        "address": "",
                        "city": "",
                        "rating": 0,
                        "snippet": item.get("snippet", ""),
                        "confidence": 0.55,
                        "status": "new",
                    }
                )
    except Exception as e:
        logger.warning("serpapi_google_organic: %s", e)
    return out


async def serpapi_google_maps(q: str, ll: str = "@24.7136,46.6753,12z", num: int = 15) -> list[dict]:
    """SerpAPI google_maps engine — نتائج أعمال من الخريطة."""
    key = get_settings().SERPAPI_KEY or ""
    if not key:
        return []
    out: list[dict] = []
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.get(
                "https://serpapi.com/search.json",
                params={
                    "engine": "google_maps",
                    "q": q,
                    "ll": ll,
                    "type": "search",
                    "api_key": key,
                },
            )
            data = r.json()
            for loc in data.get("local_results", [])[:num]:
                phone = loc.get("phone", "") or ""
                out.append(
                    {
                        "id": str(uuid.uuid4())[:10],
                        "source": "serp_google_maps",
                        "name": loc.get("title", ""),
                        "phone": re.sub(r"\s+", "", phone),
                        "website": loc.get("website", "") or "",
                        "address": loc.get("address", ""),
                        "city": "",
                        "rating": float(loc.get("rating") or 0),
                        "snippet": loc.get("type", "") or "",
                        "maps_url": "",
                        "confidence": 0.88 if phone else 0.6,
                        "status": "new",
                    }
                )
    except Exception as e:
        logger.warning("serpapi_google_maps: %s", e)
    return out


# ── Google Programmable Search (Custom Search JSON API) ─────


async def google_custom_search(q: str, num: int = 10) -> list[dict]:
    s = get_settings()
    cx = (s.GOOGLE_CSE_ID or "").strip()
    key = (s.GOOGLE_CSE_API_KEY or s.GOOGLE_API_KEY or "").strip()
    if not cx or not key:
        return []
    out: list[dict] = []
    try:
        async with httpx.AsyncClient(timeout=25) as client:
            r = await client.get(
                "https://www.googleapis.com/customsearch/v1",
                params={
                    "key": key,
                    "cx": cx,
                    "q": q,
                    "num": min(num, 10),
                    "lr": "lang_ar",
                    "cr": "countrySA",
                },
            )
            data = r.json()
            for item in data.get("items", [])[:num]:
                out.append(
                    {
                        "id": str(uuid.uuid4())[:10],
                        "source": "google_cse",
                        "name": item.get("title", "")[:200],
                        "phone": "",
                        "website": item.get("link", ""),
                        "address": "",
                        "city": "",
                        "rating": 0,
                        "snippet": item.get("snippet", ""),
                        "confidence": 0.5,
                        "status": "new",
                    }
                )
    except Exception as e:
        logger.warning("google_custom_search: %s", e)
    return out


# ── Bing Web Search (Azure) ────────────────────────────────────


async def bing_web_search(q: str, count: int = 10) -> list[dict]:
    key = (get_settings().AZURE_BING_SEARCH_KEY or "").strip()
    if not key:
        return []
    out: list[dict] = []
    try:
        async with httpx.AsyncClient(timeout=25) as client:
            r = await client.get(
                "https://api.bing.microsoft.com/v7.0/search",
                params={"q": q, "count": min(count, 20), "mkt": "ar-SA"},
                headers={"Ocp-Apim-Subscription-Key": key},
            )
            data = r.json()
            for item in data.get("webPages", {}).get("value", [])[:count]:
                out.append(
                    {
                        "id": str(uuid.uuid4())[:10],
                        "source": "bing_web",
                        "name": item.get("name", "")[:200],
                        "phone": "",
                        "website": item.get("url", ""),
                        "address": "",
                        "city": "",
                        "rating": 0,
                        "snippet": item.get("snippet", ""),
                        "confidence": 0.48,
                        "status": "new",
                    }
                )
    except Exception as e:
        logger.warning("bing_web_search: %s", e)
    return out


# ── LinkedIn signals (public SERP only) ──────────────────────


async def linkedin_public_signals(sector: str, city: str, role: str = "مدير") -> list[dict]:
    """إشارات من عناوين نتائج البحث العامة — ليس ملفات تعريف كاملة."""
    q = f'site:linkedin.com/in {role} {sector} {city}'
    rows = await serpapi_google_organic(q, num=12)
    for r in rows:
        r["source"] = "linkedin_serp_signal"
        if "linkedin.com/in/" in (r.get("website") or ""):
            r["confidence"] = min(0.72, float(r.get("confidence") or 0.5) + 0.15)
    return rows


# ── CSV / structured file ingest ───────────────────────────────


def parse_leads_csv(content: bytes, encoding: str = "utf-8-sig") -> tuple[list[dict], list[str]]:
    """يستخرج صفوفاً موحّدة من CSV — أعمدة مرنة."""
    text = content.decode(encoding, errors="replace")
    f = io.StringIO(text)
    sample = text[:4096]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t")
    except Exception:
        dialect = csv.excel
    reader = csv.DictReader(f, dialect=dialect)
    if not reader.fieldnames:
        return [], ["لا توجد أعمدة في الملف"]

    # تطبيع أسماء الأعمدة
    alias = {
        "company": "name",
        "company_name": "name",
        "اسم الشركة": "name",
        "الشركة": "name",
        "name": "name",
        "phone": "phone",
        "mobile": "phone",
        "هاتف": "phone",
        "جوال": "phone",
        "website": "website",
        "url": "website",
        "الموقع": "website",
        "city": "city",
        "المدينة": "city",
        "email": "email",
        "البريد": "email",
        "sector": "sector",
        "القطاع": "sector",
    }

    rows: list[dict] = []
    warnings: list[str] = []
    for raw in reader:
        row: dict[str, Any] = {}
        for k, v in raw.items():
            if k is None:
                continue
            ks = k.strip()
            key = alias.get(ks) or alias.get(ks.lower()) or ks.lower()
            if v:
                row[key] = str(v).strip()
        if not row.get("name") and not row.get("phone"):
            continue
        row.setdefault("source", "file_import")
        row.setdefault("id", str(uuid.uuid4())[:10])
        row.setdefault("status", "new")
        row.setdefault("confidence", 0.9 if row.get("phone") else 0.4)
        rows.append(row)

    if not rows:
        warnings.append("لم يُستخرج صف صالح — تأكد من أعمدة اسم أو هاتف")
    return rows, warnings


# ── Unified orchestration ─────────────────────────────────────


ALL_SOURCES = (
    "maps",
    "serp_google",
    "serp_maps",
    "google_cse",
    "bing",
    "linkedin_signals",
)


async def run_unified_lead_search(
    query: str,
    city: str,
    sector: str = "",
    sources: Optional[list[str]] = None,
    max_per_source: int = 12,
) -> dict[str, Any]:
    s = get_settings()
    maps_key = (s.GOOGLE_MAPS_API_KEY or s.GOOGLE_API_KEY or "").strip()
    src = [x for x in (sources or list(ALL_SOURCES)) if x in ALL_SOURCES]
    if not src:
        src = ["maps", "serp_google"]

    tasks: list[Any] = []
    labels: list[str] = []

    if "maps" in src and maps_key:
        tasks.append(places_text_search(query, city, max_per_source, maps_key))
        labels.append("maps")

    combined_q = f"{query} {city} السعودية"
    if "serp_google" in src:
        tasks.append(serpapi_google_organic(combined_q, num=max_per_source))
        labels.append("serp_google")

    if "serp_maps" in src:
        tasks.append(serpapi_google_maps(f"{query} {city}", num=max_per_source))
        labels.append("serp_maps")

    if "google_cse" in src:
        tasks.append(google_custom_search(combined_q, num=max_per_source))
        labels.append("google_cse")

    if "bing" in src:
        tasks.append(bing_web_search(combined_q, count=max_per_source))
        labels.append("bing")

    if "linkedin_signals" in src:
        tasks.append(linkedin_public_signals(sector or query, city))
        labels.append("linkedin_signals")

    if not tasks:
        return {
            "ok": True,
            "prospects": [],
            "total": 0,
            "sources_requested": src,
            "sources_ran": [],
            "message": "لا مفاتيح API مفعّلة — عيّن GOOGLE_MAPS_API_KEY أو GOOGLE_API_KEY و/أو SERPAPI_KEY في البيئة.",
            "disclaimer": "استخدم البيانات وفق سياسات المزودين وخصوصية الأفراد والشركات.",
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    raw_lists = await asyncio.gather(*tasks, return_exceptions=True)
    merged: list[dict] = []
    ran: list[str] = []
    for label, res in zip(labels, raw_lists):
        if isinstance(res, Exception):
            logger.warning("source %s failed: %s", label, res)
            continue
        ran.append(label)
        merged.extend(res)

    merged = merge_dedupe(merged)
    # ترتيب حسب الثقة
    merged.sort(key=lambda x: float(x.get("confidence") or 0), reverse=True)

    cap = min(300, len(merged))
    return {
        "ok": True,
        "prospects": merged[:cap],
        "total": len(merged),
        "sources_requested": src,
        "sources_ran": ran,
        "disclaimer": "استخدم البيانات وفق سياسات المزودين؛ إشارات LinkedIn من نتائج بحث عامة فقط.",
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def engine_capabilities() -> dict[str, Any]:
    s = get_settings()
    return {
        "google_places": bool((s.GOOGLE_MAPS_API_KEY or s.GOOGLE_API_KEY or "").strip()),
        "serpapi": bool((s.SERPAPI_KEY or "").strip()),
        "google_cse": bool((s.GOOGLE_CSE_ID or "").strip() and (s.GOOGLE_CSE_API_KEY or s.GOOGLE_API_KEY or "").strip()),
        "bing": bool((s.AZURE_BING_SEARCH_KEY or "").strip()),
        "sources": list(ALL_SOURCES),
    }
