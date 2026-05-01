"""Opportunity factory — turn signals into opportunity cards using Targeting OS."""

from __future__ import annotations

from typing import Any

from auto_client_acquisition.targeting_os import (
    map_buying_committee,
    recommend_accounts,
)


def build_opportunity_factory_demo(
    *,
    sector: str = "training",
    city: str = "Riyadh",
    limit: int = 5,
) -> dict[str, Any]:
    """
    Build demo opportunities for a (sector, city).

    Each opportunity includes account fit + buying committee + recommended channel.
    """
    accounts_data = recommend_accounts(
        sector=sector, city=city, limit=limit,
    )
    committee = map_buying_committee(sector=sector, company_size="small")

    enriched = []
    for acct in accounts_data["accounts"]:
        enriched.append({
            "company": acct.get("name"),
            "fit_score": acct.get("fit_score"),
            "tier": acct.get("tier"),
            "why_now_ar": acct.get("why_now_ar"),
            "best_angle_ar": acct.get("best_angle_ar"),
            "recommended_channel": acct.get("recommended_channel"),
            "primary_decision_maker": committee["primary_decision_maker"],
            "approval_required": True,
            "live_send_allowed": False,
        })

    return {
        "sector": sector,
        "city": city,
        "count": len(enriched),
        "opportunities": enriched,
        "buying_committee_template": committee,
        "do_not_do_ar": [
            "لا scraping LinkedIn ولا auto-DM.",
            "لا cold WhatsApp.",
            "لا تواصل بدون موافقة المالك.",
        ],
    }
