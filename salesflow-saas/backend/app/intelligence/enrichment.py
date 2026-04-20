"""
Enrichment Layer — Company + Person + Intent signals
Enriches LeadCandidates with additional data from multiple sources.
Designed to plug in Apollo/PDL/Clay APIs via env vars when available.
"""
import os
import re
import json
import time
import urllib.request
import urllib.parse
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field, asdict

from app.intelligence.discovery import LeadCandidate, extract_emails_from_text, detect_signals


@dataclass
class EnrichedLead:
    """Fully enriched lead — ready for scoring"""
    # Identity
    id: str = ""
    company_name: str = ""
    company_name_ar: str = ""
    domain: str = ""
    website: str = ""

    # Company facts
    industry: str = ""
    industry_ar: str = ""
    company_size: str = ""
    employee_count: int = 0
    founded_year: int = 0
    annual_revenue_sar: float = 0.0
    headquarters: str = ""
    region: str = ""
    description: str = ""
    description_ar: str = ""

    # Technology stack (signals for fit)
    tech_stack: List[str] = field(default_factory=list)
    uses_crm: bool = False
    uses_erp: bool = False

    # Contact
    contact_name: str = ""
    contact_title: str = ""
    contact_title_ar: str = ""
    contact_email: str = ""
    contact_phone: str = ""
    contact_linkedin: str = ""
    decision_maker_score: int = 0   # 0-100: how likely this person makes the buy decision

    # Intent signals
    signals: List[str] = field(default_factory=list)
    intent_keywords: List[str] = field(default_factory=list)
    recent_news: List[str] = field(default_factory=list)
    open_jobs_count: int = 0
    open_jobs_relevant: List[str] = field(default_factory=list)

    # Enrichment metadata
    enrichment_source: str = "web"    # web | apollo | pdl | clay
    enrichment_confidence: float = 0.5
    enriched_at: str = ""

    # Original discovery data
    source: str = ""
    source_url: str = ""
    raw_snippet: str = ""
    trigger: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# Title → Seniority mapping (Arabic + English)
TITLE_SENIORITY = {
    "ceo": 100, "chief executive": 100, "الرئيس التنفيذي": 100, "المدير العام": 100,
    "coo": 95, "chief operating": 95, "المدير التشغيلي": 95,
    "cro": 95, "chief revenue": 95,
    "cfo": 90, "chief financial": 90,
    "vp": 85, "vice president": 85, "نائب الرئيس": 85,
    "head of": 80, "رئيس قسم": 80,
    "director": 75, "مدير": 70,
    "manager": 55, "مشرف": 40,
    "executive": 65, "تنفيذي": 65,
}

TECH_KEYWORDS = [
    "salesforce", "sap", "oracle", "hubspot", "zoho", "dynamics", "pipedrive",
    "نت سويت", "odoo", "quickbooks", "workday", "servicenow",
    "jira", "slack", "teams", "whatsapp business",
]

CRM_KEYWORDS = ["salesforce", "hubspot", "zoho crm", "dynamics crm", "pipedrive", "crm"]
ERP_KEYWORDS = ["sap", "oracle", "odoo", "netsuite", "dynamics erp", "erp"]


def infer_seniority_score(title: str) -> int:
    title_lower = title.lower()
    for kw, score in TITLE_SENIORITY.items():
        if kw in title_lower:
            return score
    return 30


def infer_tech_stack(text: str) -> List[str]:
    text_lower = text.lower()
    return [tech for tech in TECH_KEYWORDS if tech in text_lower]


def estimate_company_size(text: str) -> str:
    """Try to extract company size from text"""
    patterns = [
        (r'(\d{1,5})\s*\+?\s*(employees|موظف|staff)', lambda m: int(m.group(1))),
        (r'(small|صغير)', lambda m: 0),
        (r'(medium|متوسط)', lambda m: 150),
        (r'(large|كبير|enterprise)', lambda m: 1000),
    ]
    for pattern, extractor in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                count = extractor(match)
                if count < 50: return "1-50"
                elif count < 200: return "50-200"
                elif count < 1000: return "200-1000"
                else: return "1000+"
            except Exception:
                pass
    return "unknown"


def fetch_company_website_data(domain: str) -> Dict[str, Any]:
    """Try to fetch company website and extract key signals"""
    if not domain:
        return {}
    try:
        url = f"https://{domain}"
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (compatible; DealixBot/1.0)"}
        )
        with urllib.request.urlopen(req, timeout=6) as resp:
            html = resp.read().decode('utf-8', errors='ignore')[:15000]

        emails = extract_emails_from_text(html)
        tech_stack = infer_tech_stack(html)
        signals = detect_signals(html)
        size = estimate_company_size(html)

        # Extract title/description
        title_match = re.search(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
        desc_match = re.search(
            r'<meta\s+name=["\']description["\'][^>]*content=["\']([^"\']+)["\']',
            html, re.IGNORECASE
        )

        return {
            "page_title": re.sub(r'<[^>]+>', '', title_match.group(1)).strip() if title_match else "",
            "description": desc_match.group(1).strip() if desc_match else "",
            "emails": emails[:3],
            "tech_stack": tech_stack,
            "signals": signals,
            "company_size": size,
        }
    except Exception:
        return {}


def search_company_news(company_name: str) -> List[str]:
    """Quick news search for a company name"""
    try:
        query = urllib.parse.quote(f"{company_name} news 2025 2026")
        url = f"https://html.duckduckgo.com/html/?q={query}"
        req = urllib.request.Request(
            url, headers={"User-Agent": "Mozilla/5.0 (compatible; DealixBot/1.0)"}
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
        snippets = re.findall(r'<a class="result__snippet"[^>]*>(.*?)</a>', html)
        return [re.sub(r'<[^>]+>', '', s).strip() for s in snippets[:4]]
    except Exception:
        return []


def enrich_candidate(candidate: LeadCandidate) -> EnrichedLead:
    """
    Enrich a LeadCandidate with website data, news, and inferred signals.
    Falls back gracefully when data unavailable.
    """
    enriched = EnrichedLead(
        id=candidate.id,
        company_name=candidate.company_name,
        domain=candidate.domain,
        website=f"https://{candidate.domain}" if candidate.domain else "",
        source=candidate.source,
        source_url=candidate.source_url,
        raw_snippet=candidate.raw_snippet,
        trigger=candidate.trigger,
        signals=candidate.signals.copy(),
        contact_email=candidate.contact_email,
        contact_phone=candidate.contact_phone,
        contact_linkedin=candidate.contact_linkedin,
        enriched_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    )

    # Fetch website data
    if candidate.domain:
        site_data = fetch_company_website_data(candidate.domain)
        enriched.description = site_data.get("description", "")
        enriched.tech_stack = site_data.get("tech_stack", [])
        enriched.uses_crm = any(t in site_data.get("tech_stack", []) for t in CRM_KEYWORDS)
        enriched.uses_erp = any(t in site_data.get("tech_stack", []) for t in ERP_KEYWORDS)
        enriched.company_size = site_data.get("company_size", "unknown")
        # Merge signals
        for sig in site_data.get("signals", []):
            if sig not in enriched.signals:
                enriched.signals.append(sig)
        # Extract emails if not already present
        if not enriched.contact_email and site_data.get("emails"):
            enriched.contact_email = site_data["emails"][0]

    # Fetch news
    if candidate.company_name:
        enriched.recent_news = search_company_news(candidate.company_name)
        # Detect signals in news
        for news_item in enriched.recent_news:
            for sig in detect_signals(news_item):
                if sig not in enriched.signals:
                    enriched.signals.append(sig)

    # Infer decision maker score
    enriched.decision_maker_score = infer_seniority_score(candidate.contact_title)

    # Confidence based on available data
    data_points = sum([
        bool(enriched.domain),
        bool(enriched.contact_email),
        bool(enriched.description),
        bool(enriched.signals),
        bool(enriched.recent_news),
    ])
    enriched.enrichment_confidence = min(1.0, 0.3 + (data_points * 0.14))
    enriched.enrichment_source = "web"

    return enriched


def enrich_batch(candidates: List[LeadCandidate], delay: float = 0.5) -> List[EnrichedLead]:
    """Enrich a list of candidates with rate limiting"""
    enriched_leads = []
    for candidate in candidates:
        enriched = enrich_candidate(candidate)
        enriched_leads.append(enriched)
        time.sleep(delay)
    return enriched_leads
