"""
Normalization helpers — Saudi-tuned.

Used by the data ingestion pipeline to clean rows before they enter the
lead graph. No external deps beyond stdlib.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Any
from urllib.parse import urlparse

EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
_NON_DIGIT = re.compile(r"\D+")
_WS_RE = re.compile(r"\s+")
_PUNCT_RE = re.compile(r"[،؛؟\.,;:!?\-_/\\()\[\]{}\"'`~]")


def normalize_company_name(name: str | None) -> str:
    """Lowercase, strip diacritics + Arabic punctuation, collapse whitespace."""
    if not name:
        return ""
    s = unicodedata.normalize("NFKC", str(name)).strip()
    # Strip Arabic diacritics (tashkeel) — U+064B..U+065F + U+0670
    s = re.sub(r"[ً-ٰٟ]", "", s)
    # Drop common business suffixes (Arabic + English)
    suffix_patterns = [
        r"\bشركة\b", r"\bمؤسسة\b", r"\bمكتب\b",
        r"\bllc\b", r"\binc\b", r"\bltd\b", r"\bco\.?\b",
        r"\bcompany\b", r"\bcorp\.?\b", r"\bgroup\b",
    ]
    for pat in suffix_patterns:
        s = re.sub(pat, "", s, flags=re.IGNORECASE)
    s = _PUNCT_RE.sub(" ", s)
    s = _WS_RE.sub(" ", s).strip().lower()
    return s


def normalize_domain(raw: str | None) -> str | None:
    """Extract bare domain from a URL or domain-like string."""
    if not raw:
        return None
    s = str(raw).strip().lower()
    if not s:
        return None
    if "://" not in s:
        s = "https://" + s
    try:
        host = urlparse(s).netloc or urlparse(s).path
    except Exception:
        return None
    host = host.split("/")[0].split(":")[0]
    if host.startswith("www."):
        host = host[4:]
    if not host or "." not in host:
        return None
    return host


def normalize_saudi_phone(raw: str | None) -> str | None:
    """Return +966XXXXXXXXX or None."""
    if not raw:
        return None
    digits = _NON_DIGIT.sub("", str(raw))
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
    if 10 <= len(digits) <= 15:
        return f"+{digits}"
    return None


def normalize_email(raw: str | None) -> str | None:
    if not raw:
        return None
    s = str(raw).strip().lower()
    return s if EMAIL_RE.match(s) else None


def fuzzy_company_key(name: str | None) -> str:
    """A short, dedupe-friendly key derived from normalize_company_name."""
    n = normalize_company_name(name)
    if not n:
        return ""
    # Drop generic words that hurt dedupe
    drop = {"the", "and", "for", "of", "al", "ال", "في", "و"}
    parts = [p for p in n.split() if p not in drop]
    return " ".join(parts)[:120]


def normalize_row(raw: dict[str, Any]) -> dict[str, Any]:
    """
    Normalize a raw inbound row into the canonical schema.

    Accepts loose keys (Arabic + English). Returns a dict with:
        company_name, normalized_name, domain, website, phone, email,
        city, country, sector, name (contact), role, source_url,
        google_place_id, raw_keys (list)
    """
    def pick(*keys: str) -> Any:
        for k in keys:
            v = raw.get(k)
            if v not in (None, ""):
                return v
        return None

    company = pick(
        "company", "company_name", "companyName", "name", "business_name",
        "اسم_الشركة", "اسم الشركة", "الشركة",
    )
    domain_raw = pick("domain", "website", "site", "url", "الموقع")
    domain = normalize_domain(domain_raw) if domain_raw else None
    phone = normalize_saudi_phone(pick("phone", "mobile", "tel", "whatsapp", "الهاتف", "الجوال"))
    email = normalize_email(pick("email", "Email", "البريد", "البريد_الإلكتروني"))
    city = pick("city", "City", "المدينة")
    country = pick("country", "Country", "الدولة") or "SA"
    sector = pick("sector", "industry", "category", "القطاع", "النشاط")
    name = pick("contact_name", "person", "lead", "الاسم")
    role = pick("role", "title", "position", "المسمى")
    source_url = pick("source_url", "source", "linkedin_url", "rabit", "الرابط")
    place_id = pick("place_id", "google_place_id", "googlePlaceId")

    return {
        "company_name": str(company).strip() if company else "",
        "normalized_name": fuzzy_company_key(company) if company else "",
        "domain": domain,
        "website": str(domain_raw).strip() if domain_raw else (f"https://{domain}" if domain else None),
        "phone": phone,
        "email": email,
        "city": str(city).strip() if city else None,
        "country": str(country).strip() if country else "SA",
        "sector": str(sector).strip() if sector else None,
        "contact_name": str(name).strip() if name else None,
        "role": str(role).strip() if role else None,
        "source_url": str(source_url).strip() if source_url else None,
        "google_place_id": str(place_id).strip() if place_id else None,
        "raw_keys": list(raw.keys()),
    }


def is_acceptable(normalized: dict[str, Any]) -> tuple[bool, str | None]:
    """
    Acceptance gate. A row is acceptable if it has at minimum:
      - company_name
      - at least one of: domain, phone, email, google_place_id
    Returns (ok, reason_if_not).
    """
    if not normalized.get("company_name"):
        return False, "missing_company_name"
    if not any(normalized.get(k) for k in ("domain", "phone", "email", "google_place_id")):
        return False, "no_contact_or_identifier"
    return True, None
