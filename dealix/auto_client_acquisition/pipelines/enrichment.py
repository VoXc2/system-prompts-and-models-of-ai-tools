"""
Full enrichment pipeline — composes provider chains.

Steps (each step degrades gracefully if its provider is missing):
    1. Domain normalization
    2. Optional Google CSE search for homepage / contact / pricing
    3. Crawler fetch (Firecrawl → requests_bs4)
    4. Tech detection (internal → +Wappalyzer)
    5. Public contact extraction
    6. Email intel (Hunter/Abstract — only if domain + key)
    7. Lead scoring + DQ scoring
    8. Channel recommendation

Returns a flat dict for storage in lead_scores / signals.
"""

from __future__ import annotations

import logging
from typing import Any

from auto_client_acquisition.connectors.tech_detect import extract_contact_info
from auto_client_acquisition.pipelines.normalize import normalize_domain
from auto_client_acquisition.pipelines.scoring import (
    ScoreBreakdown,
    compute_data_quality,
    compute_lead_score,
)
from auto_client_acquisition.providers.crawler import fetch_with_chain
from auto_client_acquisition.providers.email_intel import find_emails_with_chain
from auto_client_acquisition.providers.search import search_with_chain
from auto_client_acquisition.providers.tech import detect_with_chain

log = logging.getLogger(__name__)


async def enrich_account(
    account: dict[str, Any],
    *,
    enrichment_level: str = "standard",  # basic / standard / deep
) -> dict[str, Any]:
    """
    Enrich a single normalized account.

    Args:
        account: dict from pipelines.normalize.normalize_row OR an existing
                 AccountRecord-shaped dict. Must have at minimum company_name.
        enrichment_level:
            basic    → tech detect + extract_contact_info
            standard → +crawler text + Google CSE for homepage if missing
            deep     → +email intel domain search

    Returns: dict with keys:
        account, technologies, signals, contacts, score, dq_score,
        recommended_channel, providers_used, status
    """
    domain = account.get("domain") or normalize_domain(account.get("website"))
    company = account.get("company_name") or ""
    providers_used: list[str] = []
    technologies: list[dict[str, Any]] = []
    signals: list[dict[str, Any]] = []
    contacts: list[dict[str, Any]] = []
    crawl_text: str = ""
    crawl_title: str = ""

    # Step 1: discover homepage if no domain
    if not domain and enrichment_level in ("standard", "deep") and company:
        srch = await search_with_chain(f"{company} الموقع الرسمي", num=3, lang="ar")
        providers_used.append(f"search:{srch.provider}")
        if srch.status == "ok" and srch.data:
            for r in srch.data.get("results", []):
                d = normalize_domain(r.get("link"))
                if d and "facebook" not in d and "linkedin" not in d:
                    domain = d
                    account["domain"] = d
                    account["website"] = f"https://{d}"
                    account["best_source"] = srch.provider
                    break

    # Step 2: crawl homepage (text-only)
    if domain and enrichment_level in ("standard", "deep"):
        crawl = await fetch_with_chain(f"https://{domain}", timeout=10.0)
        providers_used.append(f"crawler:{crawl.provider}")
        if crawl.status == "ok" and crawl.data:
            crawl_text = (crawl.data.get("text") or "")[:6000]
            crawl_title = crawl.data.get("title") or ""

    # Step 3: tech detection
    if domain:
        tech = await detect_with_chain(f"https://{domain}")
        providers_used.append(f"tech:{tech.provider}")
        if tech.status == "ok" and tech.data:
            tools = tech.data.get("tools") or tech.data.get("technologies") or []
            for t in tools:
                if isinstance(t, dict):
                    technologies.append({
                        "name": t.get("name") or t.get("tool"),
                        "category": t.get("category"),
                        "source": tech.provider,
                    })
            for s in tech.data.get("signals") or []:
                if isinstance(s, dict):
                    signals.append({
                        "signal_type": "tech",
                        "signal_value": s.get("name") or s.get("description") or str(s),
                        "confidence": float(s.get("confidence", 0.7)),
                        "source_url": f"https://{domain}",
                    })

    # Step 4: public contact extraction
    if domain:
        try:
            contact_info = await extract_contact_info(domain)
            providers_used.append("contact_extract:internal")
            for e in contact_info.get("emails", []):
                contacts.append({"type": "email", "value": e, "source": "public_pages"})
            for ph in contact_info.get("phones", []):
                contacts.append({"type": "phone", "value": ph, "source": "public_pages"})
            for wa in contact_info.get("whatsapp", []):
                contacts.append({"type": "whatsapp", "value": wa, "source": "public_pages"})
            for li in contact_info.get("linkedin", []):
                contacts.append({"type": "linkedin", "value": li, "source": "public_pages"})
        except Exception as exc:  # noqa: BLE001
            log.warning("contact_extract_failed domain=%s err=%s", domain, exc)

    # Step 5: email intel (deep only)
    if domain and enrichment_level == "deep":
        ei = await find_emails_with_chain(domain, limit=5)
        providers_used.append(f"email_intel:{ei.provider}")
        if ei.status == "ok" and ei.data:
            for em in ei.data.get("emails", []):
                if isinstance(em, dict) and em.get("value"):
                    contacts.append({
                        "type": "email",
                        "value": em["value"],
                        "role": em.get("position"),
                        "name": (
                            f"{em.get('first_name', '')} {em.get('last_name', '')}"
                        ).strip() or None,
                        "source": ei.provider,
                    })

    # Step 6: scoring
    score: ScoreBreakdown = compute_lead_score(
        {**account, "signals": signals},
        signals=signals,
        technologies=technologies,
    )
    dq_score, dq_reasons = compute_data_quality({
        **account,
        "signals": signals,
        "email": account.get("email") or next(
            (c["value"] for c in contacts if c["type"] == "email"), None
        ),
        "phone": account.get("phone") or next(
            (c["value"] for c in contacts if c["type"] == "phone"), None
        ),
    })

    return {
        "account": account,
        "domain": domain,
        "title": crawl_title,
        "summary": crawl_text[:600] if crawl_text else "",
        "technologies": technologies,
        "signals": signals,
        "contacts": contacts,
        "score": {
            "fit": score.fit,
            "intent": score.intent,
            "urgency": score.urgency,
            "risk": score.risk,
            "total": score.total,
            "priority": score.priority,
            "recommended_channel": score.recommended_channel,
            "reason": score.reason,
        },
        "data_quality": {"score": dq_score, "reasons": dq_reasons},
        "recommended_channel": score.recommended_channel,
        "providers_used": providers_used,
        "status": "ok",
    }
