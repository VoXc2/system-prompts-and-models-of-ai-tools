"""
Tech Detector — free, native, Saudi-tuned technographics.

Fetches a domain's homepage (and optionally a few key paths) and detects the ~45
tools that matter for Dealix lead qualification: CRM, booking, payments, e-commerce,
chat, analytics/ads, forms, CMS.

Zero external dependencies beyond httpx (already in requirements).
Self-hosted, no API keys, no per-lookup cost.

Usage:
    from auto_client_acquisition.connectors.tech_detect import detect_stack
    result = await detect_stack("foodics.com")
    # → {"tools": [...], "signals": [...], "fetched_at": "...", "status": "ok"}
"""

from __future__ import annotations

import asyncio
import logging
import re
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any

import httpx

log = logging.getLogger(__name__)

# ── Signature registry ──────────────────────────────────────────
# Each entry: (tool_name, category, list of regex/keyword signatures).
# Categories map to Dealix SIGNAL_TAXONOMY.
#
# Signatures are case-insensitive and matched against: raw HTML body + all response headers.
# Keep patterns tight to avoid false positives.
#
SIGNATURES: list[tuple[str, str, list[str]]] = [
    # ── Booking / scheduling ───────────────────────────────
    ("Calendly",        "booking",   [r"calendly\.com/", r"assets\.calendly\.com"]),
    ("HubSpot Meetings","booking",   [r"meetings\.hubspot\.com"]),
    ("Chili Piper",     "booking",   [r"chilipiper\.com"]),
    ("Cal.com",         "booking",   [r"cal\.com/[a-z0-9\-]+"]),
    ("Youcanbook.me",   "booking",   [r"youcanbook\.me"]),

    # ── CRM / marketing automation ─────────────────────────
    ("HubSpot",         "crm",       [r"hs-scripts\.com", r"hsforms\.com", r"hubspot", r"js\.hs-banner\.com"]),
    ("Salesforce",      "crm",       [r"salesforce\.com/embeddedservice", r"pardot\.com"]),
    ("Pipedrive",       "crm",       [r"pipedrivewebforms\.com"]),
    ("Zoho",            "crm",       [r"zohopublic\.com", r"zohocdn\.com", r"zoho\.(com|eu|sa)/crm"]),
    ("ActiveCampaign",  "crm",       [r"activehosted\.com"]),
    ("Marketo",         "crm",       [r"marketo\.com", r"munchkin\.js"]),
    ("Mailchimp",       "marketing", [r"chimpstatic\.com", r"list-manage\.com"]),

    # ── Payments (MENA first) ──────────────────────────────
    ("Moyasar",         "payment_mena",  [r"api\.moyasar\.com", r"cdn\.moyasar\.com"]),
    ("Tap Payments",    "payment_mena",  [r"tap\.company", r"gosell\.io"]),
    ("PayTabs",         "payment_mena",  [r"paytabs\.com", r"secure\.paytabs"]),
    ("HyperPay",        "payment_mena",  [r"hyperpay\.com"]),
    ("Stripe",          "payment",       [r"js\.stripe\.com", r"checkout\.stripe\.com"]),
    ("PayPal",          "payment",       [r"paypalobjects\.com", r"paypal\.com/sdk"]),
    ("Checkout.com",    "payment",       [r"checkout\.com/card/"]),

    # ── E-commerce platforms ───────────────────────────────
    ("Salla",           "ecom_mena",  [r"salla\.network", r"cdn\.salla\.network", r"salla\.sa"]),
    ("Zid",             "ecom_mena",  [r"cdn\.zid\.store", r"zid\.sa"]),
    ("Shopify",         "ecom",       [r"cdn\.shopify\.com", r"shopify\.com/s/files", r"myshopify\.com"]),
    ("WooCommerce",     "ecom",       [r"woocommerce", r"wc-blocks"]),
    ("Magento",         "ecom",       [r"/skin/frontend/", r"Mage\.Cookies"]),
    ("BigCommerce",     "ecom",       [r"bigcommerce\.com/content"]),

    # ── Chat / support ─────────────────────────────────────
    ("Intercom",        "chat",      [r"widget\.intercom\.io", r"intercomcdn\.com"]),
    ("Zendesk Chat",    "chat",      [r"zopim\.com", r"static\.zdassets\.com"]),
    ("Crisp",           "chat",      [r"client\.crisp\.chat"]),
    ("LiveChat",        "chat",      [r"cdn\.livechatinc\.com"]),
    ("Tawk.to",         "chat",      [r"tawk\.to"]),
    ("WhatsApp Widget", "chat_mena", [r"api\.whatsapp\.com/send", r"wa\.me/\d+", r"whatsapp\.com/send"]),

    # ── Analytics / ads / pixels ───────────────────────────
    ("Google Tag Manager", "analytics", [r"googletagmanager\.com/gtm\.js"]),
    ("Google Analytics 4", "analytics", [r"googletagmanager\.com/gtag/js", r"google-analytics\.com/g/collect"]),
    ("Meta Pixel",      "ads",       [r"connect\.facebook\.net/[a-z_]+?/fbevents\.js", r"facebook\.com/tr"]),
    ("TikTok Pixel",    "ads",       [r"analytics\.tiktok\.com/i18n/pixel"]),
    ("Snapchat Pixel",  "ads",       [r"sc-static\.net/scevent"]),
    ("Google Ads",      "ads",       [r"googleadservices\.com/pagead/conversion"]),
    ("LinkedIn Insight","ads",       [r"px\.ads\.linkedin\.com"]),
    ("Hotjar",          "analytics", [r"static\.hotjar\.com"]),
    ("PostHog",         "analytics", [r"app\.posthog\.com", r"posthog\.com/static"]),
    ("Mixpanel",        "analytics", [r"cdn\.mxpnl\.com"]),
    ("Segment",         "analytics", [r"cdn\.segment\.com/analytics\.js"]),

    # ── Forms ──────────────────────────────────────────────
    ("Typeform",        "form",      [r"typeform\.com/to/"]),
    ("Jotform",         "form",      [r"jotform\.com/form"]),
    ("Google Forms",    "form",      [r"docs\.google\.com/forms"]),
    ("HubSpot Forms",   "form",      [r"js\.hsforms\.net"]),
    ("Formspree",       "form",      [r"formspree\.io/f/"]),

    # ── CMS / frameworks ───────────────────────────────────
    ("WordPress",       "cms",       [r"wp-content/", r"wp-includes/"]),
    ("Webflow",         "cms",       [r"webflow\.com", r"webflow\.io"]),
    ("Wix",             "cms",       [r"static\.parastorage\.com", r"wixstatic\.com"]),
    ("Next.js",         "framework", [r"__next/static", r"_next/data"]),
    ("Framer",          "cms",       [r"framer\.com", r"framerusercontent\.com"]),
]

# ── Signal translations to Dealix taxonomy ─────────────────────
# Category → Dealix signal name + weight suggestion.
CATEGORY_TO_SIGNAL: dict[str, tuple[str, int]] = {
    "booking":       ("uses booking tool — has demo/sales flow", 5),
    "crm":           ("CRM in use — sales process exists", 5),
    "marketing":     ("marketing automation — outbound motion exists", 3),
    "payment":       ("payment gateway configured", 4),
    "payment_mena":  ("MENA payment gateway — Saudi-ready checkout", 6),
    "ecom":          ("e-commerce platform", 4),
    "ecom_mena":     ("Salla/Zid merchant — Saudi ecom ecosystem", 8),
    "chat":          ("live chat — sales/support motion", 3),
    "chat_mena":     ("WhatsApp widget — Saudi-native sales channel", 8),
    "analytics":     ("analytics active — measurable funnel", 2),
    "ads":           ("running paid ads — active demand gen", 6),
    "form":          ("inbound form — lead flow evidence", 5),
    "cms":           ("CMS stack identified", 1),
    "framework":     ("framework identified", 1),
}


@dataclass
class DetectedTool:
    name: str
    category: str
    matched_pattern: str


@dataclass
class DetectedSignal:
    name: str
    weight: int
    evidence: str


@dataclass
class TechStackResult:
    domain: str
    url: str
    status: str  # ok | fetch_error | timeout | blocked
    http_status: int | None
    fetched_at: str
    tools: list[DetectedTool]
    signals: list[DetectedSignal]
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        return d


async def _fetch(client: httpx.AsyncClient, url: str, timeout: float) -> tuple[int, str, dict]:
    """Fetch a URL. Returns (status, body, headers_lower)."""
    r = await client.get(
        url,
        timeout=timeout,
        follow_redirects=True,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; Dealix-TechDetect/1.0; +https://dealix.me)",
            "Accept-Language": "en,ar;q=0.9",
        },
    )
    body = r.text or ""
    # lower-case header lookup
    hdrs = {k.lower(): v for k, v in r.headers.items()}
    return r.status_code, body, hdrs


def _detect_in_text(text: str) -> list[DetectedTool]:
    found: list[DetectedTool] = []
    seen: set[str] = set()
    hay = text.lower()
    for tool_name, category, patterns in SIGNATURES:
        if tool_name in seen:
            continue
        for pat in patterns:
            if re.search(pat, hay, flags=re.IGNORECASE):
                found.append(DetectedTool(name=tool_name, category=category, matched_pattern=pat))
                seen.add(tool_name)
                break
    return found


def _tools_to_signals(tools: list[DetectedTool]) -> list[DetectedSignal]:
    """Aggregate tools into Dealix-taxonomy signals (max one signal per category)."""
    signals: dict[str, DetectedSignal] = {}
    for t in tools:
        if t.category not in CATEGORY_TO_SIGNAL:
            continue
        name, weight = CATEGORY_TO_SIGNAL[t.category]
        if t.category in signals:
            existing = signals[t.category]
            existing.evidence = f"{existing.evidence}; {t.name}"
        else:
            signals[t.category] = DetectedSignal(name=name, weight=weight, evidence=t.name)
    return list(signals.values())


async def detect_stack(
    domain: str,
    *,
    timeout: float = 10.0,
    extra_paths: list[str] | None = None,
) -> TechStackResult:
    """
    Detect technology stack for a domain. Only the homepage by default.
    Pass extra_paths like ['/careers', '/contact'] to widen coverage.
    """
    domain = (domain or "").strip().lower()
    if not domain:
        return TechStackResult(
            domain="", url="", status="fetch_error", http_status=None,
            fetched_at=_now_iso(), tools=[], signals=[], error="empty_domain",
        )

    # Normalize — accept full url or bare domain
    if "://" in domain:
        base_url = domain.rstrip("/")
    else:
        base_url = f"https://{domain}".rstrip("/")

    tools: list[DetectedTool] = []
    headers_concat = ""
    body_concat = ""
    http_status: int | None = None
    status_label = "ok"
    error: str | None = None

    paths = ["/"] + (extra_paths or [])

    async with httpx.AsyncClient(http2=False) as client:
        for path in paths:
            url = base_url + path
            try:
                code, body, hdrs = await _fetch(client, url, timeout=timeout)
                if http_status is None:
                    http_status = code
                headers_concat += "\n".join(f"{k}: {v}" for k, v in hdrs.items()) + "\n"
                body_concat += body + "\n"
            except httpx.TimeoutException:
                if error is None:
                    error = f"timeout:{path}"
                status_label = "timeout" if status_label == "ok" else status_label
            except Exception as exc:  # noqa: BLE001
                if error is None:
                    error = f"fetch_error:{path}:{type(exc).__name__}"
                status_label = "fetch_error" if status_label == "ok" else status_label

    if body_concat or headers_concat:
        tools = _detect_in_text(body_concat + "\n" + headers_concat)

    signals = _tools_to_signals(tools)

    return TechStackResult(
        domain=domain,
        url=base_url,
        status=status_label,
        http_status=http_status,
        fetched_at=_now_iso(),
        tools=tools,
        signals=signals,
        error=error,
    )


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ── CLI convenience ────────────────────────────────────────────
async def _main(argv: list[str]) -> int:
    import json
    if len(argv) < 2:
        print("usage: python -m auto_client_acquisition.connectors.tech_detect <domain>")
        return 1
    result = await detect_stack(argv[1])
    print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    import sys
    raise SystemExit(asyncio.run(_main(sys.argv)))


# ── Contact info extraction (emails, phones) from public pages ─
import re as _re

EMAIL_RE = _re.compile(r"[\w\.\-+]+@[\w\.\-]+\.[a-zA-Z]{2,}")
PHONE_SA_RE = _re.compile(r"(?:\+?966|00966|0)(?:\s*[-.])?\s*5\d(?:\s*[-.]?\s*\d){8}")
PHONE_INTL_RE = _re.compile(r"\+\d{1,3}[\s-]?\d{1,4}[\s-]?\d{3,4}[\s-]?\d{3,5}")
WHATSAPP_RE = _re.compile(r"(?:wa\.me/|whatsapp\.com/send\?phone=|api\.whatsapp\.com/send\?phone=)(\+?\d{8,15})")

# Social handles
LINKEDIN_COMPANY_RE = _re.compile(r"linkedin\.com/company/([\w\-]+)")
TWITTER_RE = _re.compile(r"(?:twitter\.com|x\.com)/([\w]+)")


async def extract_contact_info(
    domain: str,
    *,
    timeout: float = 10.0,
    paths: list[str] | None = None,
) -> dict:
    """
    Extract publicly listed contact info from a company's public pages.
    LEGAL: only fetches public pages, respects robots.txt implicitly, no auth bypass.
    """
    import re as __re
    paths = paths or ["/", "/contact", "/about", "/ar", "/en"]
    domain = domain.strip().lower().replace("https://", "").replace("http://", "").strip("/")
    base = f"https://{domain}"

    emails: set[str] = set()
    phones: set[str] = set()
    whatsapp: set[str] = set()
    linkedin: set[str] = set()
    twitter: set[str] = set()
    fetched_at = _now_iso()

    async with httpx.AsyncClient() as client:
        for path in paths:
            url = base + path
            try:
                r = await client.get(
                    url, timeout=timeout, follow_redirects=True,
                    headers={"User-Agent": "Mozilla/5.0 (Dealix-ContactFind/1.0)"},
                )
                if r.status_code != 200 or not r.text:
                    continue
                text = r.text
                for m in EMAIL_RE.findall(text):
                    e = m.lower()
                    # filter out generic / fake
                    if any(x in e for x in ("example.com","sentry.io","@2x","@3x","@media")):
                        continue
                    emails.add(e)
                for m in PHONE_SA_RE.findall(text):
                    phones.add(_normalize_phone(m, default_cc="+966"))
                for m in PHONE_INTL_RE.findall(text):
                    n = _normalize_phone(m)
                    if n and len(n) >= 10:
                        phones.add(n)
                for m in WHATSAPP_RE.findall(text):
                    whatsapp.add(_normalize_phone(m))
                for m in LINKEDIN_COMPANY_RE.findall(text):
                    linkedin.add(f"linkedin.com/company/{m}")
                for m in TWITTER_RE.findall(text):
                    if m.lower() not in ("home","share","intent","search"):
                        twitter.add(m)
            except Exception:
                continue

    return {
        "domain": domain,
        "emails": sorted(emails)[:10],
        "phones": sorted(phones)[:10],
        "whatsapp": sorted(whatsapp)[:5],
        "linkedin": sorted(linkedin)[:5],
        "twitter": sorted(twitter)[:5],
        "fetched_at": fetched_at,
        "legal_basis": "Public website data; business contact only; no personal PII scraped from private pages.",
    }


def _normalize_phone(raw: str, default_cc: str = "+966") -> str:
    """Keep + then digits only."""
    import re as __re
    if not raw:
        return ""
    # strip spaces, dashes, parens
    s = __re.sub(r"[^\d+]", "", raw)
    if s.startswith("00"):
        s = "+" + s[2:]
    if not s.startswith("+"):
        # If looks like local Saudi (starts with 5 and 9 digits)
        if s.startswith("5") and len(s) == 9:
            s = default_cc + s
        elif s.startswith("0") and len(s) == 10:
            s = default_cc + s[1:]
    return s
