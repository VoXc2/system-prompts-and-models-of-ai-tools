"""Account-first targeting — يبحث عن الشركات المناسبة قبل الأشخاص."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

# Signals that indicate a company is "in market" right now.
ACCOUNT_SIGNALS_AR: dict[str, str] = {
    "hiring_sales": "توظيف مبيعات",
    "new_branch": "فرع جديد",
    "website_updated": "تحديث الموقع",
    "active_ads": "إعلانات نشطة",
    "event_participation": "مشاركة في فعاليات",
    "google_reviews": "تقييمات Google نشطة",
    "booking_link": "صفحة حجز/طلب",
    "crm_visible": "بيانات CRM متوفرة",
    "growing_team": "نمو الفريق",
    "partner_potential": "إمكانية شراكة",
    "expansion_news": "أخبار توسع",
    "leadership_change": "تغيير قيادي",
}


@dataclass(frozen=True)
class AccountSignal:
    """A single buying-readiness signal on a company."""
    key: str
    label_ar: str
    weight: int  # 1..10
    why_ar: str

    def to_dict(self) -> dict[str, object]:
        return {
            "key": self.key, "label_ar": self.label_ar,
            "weight": self.weight, "why_ar": self.why_ar,
        }


# Default signal weights — can be overridden per sector.
_DEFAULT_WEIGHTS: dict[str, int] = {
    "hiring_sales": 9,
    "new_branch": 8,
    "expansion_news": 9,
    "active_ads": 7,
    "growing_team": 7,
    "leadership_change": 8,
    "booking_link": 5,
    "website_updated": 4,
    "google_reviews": 5,
    "crm_visible": 3,
    "event_participation": 6,
    "partner_potential": 6,
}


def _signal_objs(signals: dict[str, bool] | list[str]) -> list[AccountSignal]:
    out: list[AccountSignal] = []
    if isinstance(signals, list):
        signals = {s: True for s in signals}
    for key, val in signals.items():
        if not val or key not in ACCOUNT_SIGNALS_AR:
            continue
        out.append(AccountSignal(
            key=key,
            label_ar=ACCOUNT_SIGNALS_AR[key],
            weight=_DEFAULT_WEIGHTS.get(key, 3),
            why_ar=f"إشارة: {ACCOUNT_SIGNALS_AR[key]}",
        ))
    return out


def score_account_fit(account: dict[str, Any]) -> dict[str, Any]:
    """Score an account 0..100 based on its signals + sector+size match."""
    signals = _signal_objs(account.get("signals", {}))
    base = sum(s.weight for s in signals)
    score = min(100, base * 4)  # ~25 weight points = max 100
    if account.get("sector_match"):
        score = min(100, score + 10)
    if account.get("city_match"):
        score = min(100, score + 5)

    if score >= 70:
        tier = "hot"
    elif score >= 40:
        tier = "warm"
    elif score >= 15:
        tier = "watching"
    else:
        tier = "cold"

    return {
        "score": score,
        "tier": tier,
        "signals": [s.to_dict() for s in signals],
        "signal_count": len(signals),
    }


def explain_why_now(account: dict[str, Any]) -> str:
    """Build an Arabic 'why now' line from an account's signals."""
    signals = _signal_objs(account.get("signals", {}))
    if not signals:
        return "لا توجد إشارات شراء واضحة الآن — متابعة دورية مقترحة."
    top = sorted(signals, key=lambda s: -s.weight)[:2]
    labels = " + ".join(s.label_ar for s in top)
    company = account.get("name") or "الشركة"
    return f"{company} تظهر إشارات: {labels}. نافذة فرصة مناسبة الآن."


def recommend_account_source_strategy(account: dict[str, Any]) -> dict[str, Any]:
    """Recommend safe sources for reaching this account's decision-makers."""
    has_crm = bool(account.get("crm_visible"))
    has_ads = bool(account.get("active_ads"))
    has_events = bool(account.get("event_participation"))

    primary = []
    if has_crm:
        primary.append("crm_customer")
    primary.append("website_form")
    primary.append("linkedin_lead_form")

    if has_ads:
        primary.append("ads_retargeting")
    if has_events:
        primary.append("event_lead")

    return {
        "primary_sources": primary,
        "blocked_sources": ["scraped_email", "scraped_phone", "purchased_list"],
        "notes_ar": (
            "ابدأ بمصادر مصرّح بها: قوائم العميل، Lead Gen Forms، "
            "نماذج الموقع، شركاء، أحداث. لا scraping ولا قوائم مشتراة."
        ),
    }


def recommend_accounts(
    sector: str,
    city: str,
    *,
    offer: str = "",
    goal: str = "fill_pipeline",
    limit: int = 10,
    seed_signals: list[str] | None = None,
) -> dict[str, Any]:
    """
    Generate a deterministic list of recommended target accounts.

    This is a structural template — production reads from real data sources
    (Google Maps, CRM, web forms, etc). The output shape stays identical.
    """
    seed_signals = seed_signals or [
        "hiring_sales", "new_branch", "active_ads",
        "growing_team", "booking_link", "google_reviews",
    ]
    sector_label_ar = {
        "training": "التدريب", "saas": "البرمجيات", "real_estate": "العقار",
        "retail": "التجزئة", "healthcare": "الرعاية الصحية",
        "logistics": "اللوجستيات", "fintech": "الفنتك",
        "agency": "الوكالات", "education": "التعليم",
    }.get(sector.lower(), sector)

    accounts: list[dict[str, Any]] = []
    n = max(1, min(limit, 25))
    for i in range(n):
        # Spread signals across accounts deterministically.
        my_signals = {seed_signals[(i + j) % len(seed_signals)]: True
                      for j in range(2 + (i % 3))}
        acct = {
            "name": f"شركة {sector_label_ar} #{i + 1} في {city}",
            "sector": sector,
            "city": city,
            "signals": my_signals,
            "sector_match": True,
            "city_match": True,
        }
        scored = score_account_fit(acct)
        sources = recommend_account_source_strategy(acct)
        acct.update({
            "fit_score": scored["score"],
            "tier": scored["tier"],
            "why_now_ar": explain_why_now(acct),
            "primary_sources": sources["primary_sources"],
            "best_angle_ar": (
                f"عرض Pilot 7 أيام لاستخراج 10 فرص في قطاع {sector_label_ar}."
                if not offer else
                f"العرض المقترح: {offer}."
            ),
            "recommended_channel": (
                "email_first"
                if "crm_visible" in my_signals
                else "linkedin_lead_form_first"
            ),
            "risk_level": "low" if scored["score"] >= 50 else "medium",
        })
        accounts.append(acct)

    accounts = rank_accounts(accounts)
    return {
        "sector": sector, "city": city, "goal": goal, "offer": offer,
        "total": len(accounts),
        "accounts": accounts,
        "do_not_do_ar": [
            "لا scraping للبيانات.",
            "لا cold WhatsApp.",
            "لا auto-DM على LinkedIn.",
            "لا charge بدون موافقة.",
        ],
    }


def rank_accounts(accounts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Sort accounts by fit_score desc; stable for ties."""
    return sorted(accounts, key=lambda a: -int(a.get("fit_score", 0)))
