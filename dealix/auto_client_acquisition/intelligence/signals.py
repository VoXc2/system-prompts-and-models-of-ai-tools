"""
Buying Signal Detector — pure-function extractor that turns raw enrichment
data (website html, places info, tech stack hits, contact info) into a list
of typed buying-signals with confidence + source_url.

Signal types:
    website_form         — has /contact /demo form (= takes inbound)
    whatsapp_button      — wa.me link or WhatsApp widget present
    booking_link         — Calendly / direct booking pages
    pricing_page         — /pricing or /baqat exists
    careers_hiring       — /careers /jobs page or hiring text
    crm_in_use           — HubSpot/Salesforce/Zoho/Bitrix snippets
    payment_mena         — Moyasar/Tap/PayTabs/HyperPay snippets
    ecom_mena            — Salla/Zid/Shopify/WooCommerce
    chat_widget          — Intercom/Drift/Crisp/Tawk/WhatsApp
    ads_pixel            — Meta Pixel / GA4 / Google Tag
    high_review_count    — Google Maps reviews_count >= 50
    high_rating          — rating >= 4.3 with 20+ reviews
    multi_branch         — multiple cities / branches mentioned
    new_site_or_redirect — recent rebrand signal
    sector_urgency       — sector inherent: real_estate/events/logistics

Output: list[BuyingSignal] with type, confidence (0..1), value, source_url.
Used by scoring.compute_lead_score (intent_score + urgency_score lift).
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from typing import Any


# ── Sector urgency tiers (always-on signals derived from the sector itself) ─
HIGH_URGENCY_SECTORS = {
    "real_estate", "real_estate_developer", "events", "logistics",
    "hospitality", "hotel", "wedding_hall",
}
MEDIUM_URGENCY_SECTORS = {
    "restaurant", "cafe", "fitness_gym", "salon_spa",
    "training_center", "dental_clinic", "medical_clinic", "cosmetic_clinic",
}


@dataclass
class BuyingSignal:
    type: str
    value: str
    confidence: float  # 0.0..1.0
    source_url: str | None
    detected_via: str  # rule | wappalyzer | google_places | website_crawl

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# Patterns for HTML/markdown body
WHATSAPP_PATTERNS = [
    re.compile(r"wa\.me/", re.IGNORECASE),
    re.compile(r"api\.whatsapp\.com/send", re.IGNORECASE),
    re.compile(r"whatsapp\.com/send\?", re.IGNORECASE),
    re.compile(r"chat[-_]?on[-_]?whatsapp", re.IGNORECASE),
]
BOOKING_PATTERNS = [
    re.compile(r"calendly\.com", re.IGNORECASE),
    re.compile(r"meetings\.hubspot", re.IGNORECASE),
    re.compile(r"book[-_]?(?:now|appointment|demo)", re.IGNORECASE),
    re.compile(r"احجز|حجز[\s-]?موعد", re.IGNORECASE),
]
PRICING_PATTERNS = [
    re.compile(r"/pricing", re.IGNORECASE),
    re.compile(r"/plans?", re.IGNORECASE),
    re.compile(r"/baqat", re.IGNORECASE),  # باقات
    re.compile(r"الأسعار|باقات|الباقات", re.IGNORECASE),
]
CAREERS_PATTERNS = [
    re.compile(r"/careers", re.IGNORECASE),
    re.compile(r"/jobs", re.IGNORECASE),
    re.compile(r"الوظائف|توظيف|نبحث عن", re.IGNORECASE),
]
FORM_PATTERNS = [
    re.compile(r"<form\b", re.IGNORECASE),
    re.compile(r"تواصل معنا|راسلنا", re.IGNORECASE),
    re.compile(r"contact[-_ ]?(?:us|form)", re.IGNORECASE),
]
CRM_PATTERNS = {
    "hubspot": re.compile(r"hsforms?\.com|js\.hsforms\.net|hubspot\.com", re.IGNORECASE),
    "salesforce": re.compile(r"salesforce\.com|force\.com|pardot", re.IGNORECASE),
    "zoho": re.compile(r"zoho\.com/crm|zohopublic", re.IGNORECASE),
    "bitrix": re.compile(r"bitrix24", re.IGNORECASE),
}
PAYMENT_PATTERNS = {
    "moyasar": re.compile(r"moyasar\.com|moyasar\.js", re.IGNORECASE),
    "tap": re.compile(r"tap\.company", re.IGNORECASE),
    "paytabs": re.compile(r"paytabs\.com", re.IGNORECASE),
    "hyperpay": re.compile(r"hyperpay\.com", re.IGNORECASE),
}
ECOM_PATTERNS = {
    "salla": re.compile(r"salla\.sa|salla\.com", re.IGNORECASE),
    "zid": re.compile(r"zid\.sa|zid\.store", re.IGNORECASE),
    "shopify": re.compile(r"\.myshopify\.com|shopify-cdn", re.IGNORECASE),
    "woocommerce": re.compile(r"woocommerce", re.IGNORECASE),
}
CHAT_PATTERNS = {
    "intercom": re.compile(r"intercom\.io|intercomcdn", re.IGNORECASE),
    "drift": re.compile(r"drift\.com|driftt\.com", re.IGNORECASE),
    "crisp": re.compile(r"crisp\.chat", re.IGNORECASE),
    "tawk": re.compile(r"tawk\.to", re.IGNORECASE),
}
ADS_PATTERNS = {
    "meta_pixel": re.compile(r"facebook\.net/.+/fbevents\.js|connect\.facebook\.net", re.IGNORECASE),
    "ga4": re.compile(r"googletagmanager\.com/gtag/js|google-analytics\.com/analytics\.js", re.IGNORECASE),
    "google_tag": re.compile(r"googletagmanager\.com/gtm\.js", re.IGNORECASE),
    "tiktok_pixel": re.compile(r"analytics\.tiktok\.com/i18n/pixel", re.IGNORECASE),
    "snap_pixel": re.compile(r"sc-static\.net/scevent", re.IGNORECASE),
}


def detect_signals(
    *,
    sector: str | None,
    website_html: str | None = None,
    website_url: str | None = None,
    google_rating: float | None = None,
    google_reviews_count: int | None = None,
    tech_hits: list[dict[str, Any]] | None = None,
    branches_hint: int | None = None,
) -> list[BuyingSignal]:
    """
    Run all detectors over the available data. Returns a list of typed signals
    with confidence in [0, 1] and a source_url.

    All inputs are optional — missing data simply produces fewer signals.
    """
    signals: list[BuyingSignal] = []
    src = website_url or "internal:rule"

    # 1. Sector urgency (always-on)
    sec = (sector or "").lower()
    if sec in HIGH_URGENCY_SECTORS:
        signals.append(BuyingSignal("sector_urgency", f"high:{sec}", 0.85, None, "rule"))
    elif sec in MEDIUM_URGENCY_SECTORS:
        signals.append(BuyingSignal("sector_urgency", f"medium:{sec}", 0.55, None, "rule"))

    # 2. Website-based detections
    if website_html:
        body = website_html
        if any(p.search(body) for p in WHATSAPP_PATTERNS):
            signals.append(BuyingSignal("whatsapp_button", "detected", 0.9, src, "website_crawl"))
        if any(p.search(body) for p in BOOKING_PATTERNS):
            signals.append(BuyingSignal("booking_link", "detected", 0.85, src, "website_crawl"))
        if any(p.search(body) for p in PRICING_PATTERNS):
            signals.append(BuyingSignal("pricing_page", "detected", 0.7, src, "website_crawl"))
        if any(p.search(body) for p in CAREERS_PATTERNS):
            signals.append(BuyingSignal("careers_hiring", "detected", 0.7, src, "website_crawl"))
        if any(p.search(body) for p in FORM_PATTERNS):
            signals.append(BuyingSignal("website_form", "detected", 0.85, src, "website_crawl"))

        for name, pat in CRM_PATTERNS.items():
            if pat.search(body):
                signals.append(BuyingSignal("crm_in_use", name, 0.9, src, "website_crawl"))
        for name, pat in PAYMENT_PATTERNS.items():
            if pat.search(body):
                signals.append(BuyingSignal("payment_mena", name, 0.85, src, "website_crawl"))
        for name, pat in ECOM_PATTERNS.items():
            if pat.search(body):
                signals.append(BuyingSignal("ecom_mena", name, 0.9, src, "website_crawl"))
        for name, pat in CHAT_PATTERNS.items():
            if pat.search(body):
                signals.append(BuyingSignal("chat_widget", name, 0.8, src, "website_crawl"))
        for name, pat in ADS_PATTERNS.items():
            if pat.search(body):
                signals.append(BuyingSignal("ads_pixel", name, 0.8, src, "website_crawl"))

    # 3. Google Maps signals
    if google_reviews_count is not None and google_reviews_count >= 50:
        signals.append(BuyingSignal(
            "high_review_count", str(google_reviews_count),
            0.6 + min(0.3, google_reviews_count / 1000), None, "google_places",
        ))
    if google_rating is not None and google_rating >= 4.3 \
       and (google_reviews_count or 0) >= 20:
        signals.append(BuyingSignal(
            "high_rating", f"{google_rating}",
            0.7, None, "google_places",
        ))

    # 4. Multi-branch hint
    if branches_hint and branches_hint >= 2:
        signals.append(BuyingSignal(
            "multi_branch", str(branches_hint),
            min(0.95, 0.5 + 0.1 * branches_hint), None, "rule",
        ))

    # 5. Tech detector hits (already-detected by tech_detect.py)
    for t in tech_hits or []:
        cat = (t.get("category") or "").lower()
        name = t.get("name") or t.get("tool") or ""
        if cat in {"booking"}:
            signals.append(BuyingSignal("booking_link", name, 0.85, src, "tech_detect"))
        elif cat in {"crm"}:
            signals.append(BuyingSignal("crm_in_use", name, 0.85, src, "tech_detect"))
        elif cat in {"payment_mena"}:
            signals.append(BuyingSignal("payment_mena", name, 0.85, src, "tech_detect"))
        elif cat in {"ecom_mena"}:
            signals.append(BuyingSignal("ecom_mena", name, 0.85, src, "tech_detect"))
        elif cat in {"chat_mena", "chat"}:
            signals.append(BuyingSignal("chat_widget", name, 0.8, src, "tech_detect"))
        elif cat in {"analytics", "ads"}:
            signals.append(BuyingSignal("ads_pixel", name, 0.7, src, "tech_detect"))

    return signals


def signals_to_intent_lift(signals: list[BuyingSignal]) -> float:
    """
    Convert signal list → 0..30 lift on intent_score.
    Used by compute_lead_score to mix in fresh signal data.
    """
    if not signals:
        return 0.0
    lift = 0.0
    type_weights = {
        "whatsapp_button": 4.0,
        "booking_link": 4.0,
        "website_form": 3.0,
        "pricing_page": 2.5,
        "careers_hiring": 3.5,
        "crm_in_use": 3.0,
        "payment_mena": 2.5,
        "ecom_mena": 3.5,
        "chat_widget": 2.0,
        "ads_pixel": 2.0,
        "high_review_count": 3.0,
        "high_rating": 1.5,
        "multi_branch": 4.0,
        "sector_urgency": 5.0,
    }
    seen_types: set[str] = set()
    for s in signals:
        if s.type in seen_types:
            continue  # only first hit per type
        seen_types.add(s.type)
        lift += type_weights.get(s.type, 1.0) * s.confidence
    return min(30.0, lift)
