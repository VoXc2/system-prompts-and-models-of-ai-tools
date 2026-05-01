"""Kill feature: 10 فرص في 10 دقائق — تكوين deterministic من رادار + خطة أول 10."""

from __future__ import annotations

import hashlib
from typing import Any

from auto_client_acquisition.business.gtm_plan import first_10_customers_plan
from auto_client_acquisition.v3.market_radar import MarketSignal, rank_opportunities


# أنماط إشارات متنوعة لملء 10 فرص بشكل حتمي من مدخلات المستخدم
_SIGNAL_ROTATION: tuple[tuple[str, float, int, str], ...] = (
    ("hiring_sales", 88.0, 3, "وظائف مبيعات"),
    ("new_branch", 82.0, 5, "توسع/فرع"),
    ("booking_link", 78.0, 2, "رابط حجز"),
    ("website_updated", 72.0, 7, "تحديث موقع"),
    ("new_ad_activity", 70.0, 4, "نشاط إعلاني"),
    ("event_participation", 68.0, 6, "فعالية"),
    ("new_partnership", 66.0, 8, "شراكة"),
    ("new_product_launch", 74.0, 1, "إطلاق منتج"),
    ("review_spike", 62.0, 9, "تقييمات"),
    ("slow_response_risk", 65.0, 10, "مخاطرة بطء رد"),
)


def _slug_seed(parts: tuple[str, ...]) -> int:
    h = hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()
    return int(h[:8], 16)


def build_ten_opportunities(payload: dict[str, Any] | None) -> dict[str, Any]:
    """
    يُنشئ 10 فرص مرتبة مع Why Now ومسودة مقترحة — **بدون إرسال**.

    كل مسودة بحالة ``pending_approval`` و``approval_required: true``.
    """
    body = payload or {}
    company = str(body.get("company_name_or_url") or body.get("company") or "شركتك").strip()
    sector = str(body.get("sector") or "b2b_saas").strip().lower().replace(" ", "_")
    city = str(body.get("city") or "Riyadh").strip()
    offer = str(body.get("offer_one_liner") or body.get("offer") or "منصة إيرادات ونمو B2B").strip()
    goal = str(body.get("goal_meetings_or_replies") or body.get("goal") or "اجتماعات مؤهّلة").strip()

    seed = _slug_seed((company, sector, city, offer))
    plan = first_10_customers_plan()

    signals: list[MarketSignal] = []
    for i in range(10):
        st, strength, days_base, tag = _SIGNAL_ROTATION[(i + seed) % len(_SIGNAL_ROTATION)]
        # تنويع بسيط بالاسم حسب الفهرس
        display_company = f"{company} — عينة {i + 1} ({tag})" if i > 0 else company
        days_old = (days_base + (seed % 5) + i) % 14
        signals.append(
            MarketSignal(
                company=display_company,
                sector=sector,
                city=city,
                signal_type=st,
                strength=strength - (i % 3) * 2.0,
                days_old=days_old,
                evidence=f"synthetic_rank_{i}_seed_{seed % 10000}",
            )
        )

    ranked = rank_opportunities(signals, limit=10)
    opportunities: list[dict[str, Any]] = []
    for idx, row in enumerate(ranked):
        why = row.get("why_now_ar", "")
        draft = (
            f"السلام عليكم، لاحظنا مؤشراً لدى {row.get('company')} ({why[:80]}…). "
            f"نقدّم: {offer}. هل يمكننا ١٥ دقيقة هذا الأسبوع لمناقشة {goal}؟"
        )
        opportunities.append(
            {
                "rank": idx + 1,
                "company": row.get("company"),
                "sector": row.get("sector"),
                "city": row.get("city"),
                "signal": {
                    "signal_type": row.get("signal_type"),
                    "score": row.get("score"),
                    "why_now_ar": why,
                    "evidence": row.get("evidence"),
                },
                "risk_notes_ar": "تحقق يدوي من الإشارة؛ لا إرسال تلقائي؛ راعِ opt-in واتساب/بريد.",
                "proposed_channel": "email_or_whatsapp_template",
                "draft_message_ar": draft,
                "approval_status": "pending_approval",
                "approval_required": True,
            }
        )

    return {
        "feature": "10 فرص في 10 دقائق",
        "approval_required": True,
        "no_outbound_sent": True,
        "inputs_echo": {
            "company_name_or_url": company,
            "sector": sector,
            "city": city,
            "offer_one_liner": offer,
            "goal_meetings_or_replies": goal,
        },
        "first_10_plan_excerpt": {
            "pilot_offer_ar": plan.get("pilot_offer_ar"),
            "success_criteria": plan.get("success_criteria", [])[:2],
        },
        "opportunities": opportunities,
        "count": len(opportunities),
    }
