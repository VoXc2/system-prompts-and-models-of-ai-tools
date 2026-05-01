"""Recommend target accounts from sector/city/goal — deterministic demo accounts."""

from __future__ import annotations

from typing import Any

_SIGNALS = (
    "hiring_sales",
    "website_updated",
    "google_reviews_active",
    "booking_link",
    "growing_team",
)


def recommend_accounts(
    sector: str,
    city: str,
    offer: str,
    goal: str,
    *,
    limit: int = 10,
) -> dict[str, Any]:
    sector_ar = sector or "خدمات B2B"
    city_ar = city or "الرياض"
    base = [
        {
            "company": f"شركة ألفا — {sector_ar}",
            "city": city_ar,
            "fit_score": 88,
            "why_now_ar": "إعلان وظائف مبيعات + صفحة خدمات محدثة.",
            "best_channel": "email_first",
            "risk_level": "low",
            "signals": ["hiring_sales", "website_updated"],
        },
        {
            "company": f"مؤسسة بيتا — {sector_ar}",
            "city": city_ar,
            "fit_score": 82,
            "why_now_ar": "تقييمات Google نشطة — فرصة سمعة محلية.",
            "best_channel": "google_business_draft",
            "risk_level": "low",
            "signals": ["google_reviews_active", "booking_link"],
        },
        {
            "company": f"مجموعة جاما — {sector_ar}",
            "city": "جدة",
            "fit_score": 76,
            "why_now_ar": "توسع فريق — احتمال شراء أدوات نمو.",
            "best_channel": "linkedin_lead_form",
            "risk_level": "medium",
            "signals": ["growing_team"],
        },
    ]
    accounts = []
    for i in range(max(1, min(limit, 20))):
        a = dict(base[i % len(base)])
        a["id"] = f"acct_demo_{i+1}"
        a["company"] = f"{a['company']} ({i+1})"
        a["offer_fit_ar"] = f"العرض «{offer or 'Growth OS'}» مناسب لهدف «{goal or 'نمو'}»."
        accounts.append(a)
    return {"accounts": accounts[:limit], "count": len(accounts[:limit]), "demo": True}


def score_account_fit(account: dict[str, Any]) -> int:
    return int(account.get("fit_score") or 70)


def explain_why_now(account: dict[str, Any]) -> str:
    return str(account.get("why_now_ar") or "إشارات سوق عامة — راجع التفاصيل قبل التواصل.")


def recommend_account_source_strategy(account: dict[str, Any]) -> dict[str, Any]:
    ch = str(account.get("best_channel") or "email_first")
    return {
        "account_id": account.get("id"),
        "recommended_first_touch": ch,
        "steps_ar": [
            "تحقق من المصدر والـ opt-in.",
            "جهّز مسودة بريد عبر المنصة.",
            "لا واتساب بارد بدون علاقة.",
        ],
        "demo": True,
    }


def rank_accounts(accounts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(accounts, key=lambda x: -score_account_fit(x))
