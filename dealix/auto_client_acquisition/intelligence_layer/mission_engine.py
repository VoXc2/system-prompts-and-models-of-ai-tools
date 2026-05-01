"""Intelligence Mission Engine — 7 outcome-shaped growth missions."""

from __future__ import annotations

from typing import Any

from auto_client_acquisition.intelligence_layer.growth_brain import GrowthBrain


INTEL_MISSIONS: tuple[dict[str, Any], ...] = (
    {
        "id": "first_10_opportunities",
        "title_ar": "10 فرص في 10 دقائق",
        "goal_ar": "اكتشاف 10 شركات سعودية + رسائل عربية + موافقة + متابعة أسبوع.",
        "kill_metric": "ten_drafts_approved",
        "required_integrations": ("whatsapp",),
        "safety_rules_ar": ("لا cold WhatsApp بدون lawful basis",),
        "success_metrics": ("approve_rate ≥ 50%", "first_reply ≤ 24h"),
    },
    {
        "id": "revenue_leak_rescue",
        "title_ar": "أنقذ الإيراد الضائع",
        "goal_ar": "اقرأ Email/CRM/WhatsApp → استخرج leads ضائعة → drafts متابعة.",
        "kill_metric": "leads_revived",
        "required_integrations": ("gmail", "crm"),
        "safety_rules_ar": ("approval لكل follow-up",),
        "success_metrics": ("rescued_leads ≥ 5", "rescued_pipeline_sar ≥ 30000"),
    },
    {
        "id": "partnership_sprint",
        "title_ar": "ابدأ قناة شراكات",
        "goal_ar": "تحديد + التواصل مع 5 شركاء محتملين خلال 14 يوم.",
        "kill_metric": "partner_intros_replied",
        "required_integrations": ("gmail", "google_calendar"),
        "safety_rules_ar": ("لا outreach شخصي بدون warm context",),
        "success_metrics": ("intros_replied ≥ 2", "first_partner_meeting ≤ 14d"),
    },
    {
        "id": "customer_reactivation",
        "title_ar": "استرجع العملاء الخاملين",
        "goal_ar": "ارفع قائمة قدامى → صنّفهم → رسائل عودة بـ payment link.",
        "kill_metric": "reactivated_customers",
        "required_integrations": ("whatsapp", "moyasar"),
        "safety_rules_ar": ("Opt-in موثق فقط",),
        "success_metrics": ("reactivated ≥ 10", "revenue_sar ≥ 25000"),
    },
    {
        "id": "meeting_booking_sprint",
        "title_ar": "احجز 3 اجتماعات",
        "goal_ar": "Top-10 leads → agenda → موافقة → calendar drafts.",
        "kill_metric": "meetings_confirmed",
        "required_integrations": ("google_calendar", "whatsapp"),
        "safety_rules_ar": ("لا insert بدون OAuth + ضغطة المستخدم",),
        "success_metrics": ("meetings_confirmed ≥ 3 / 5d",),
    },
    {
        "id": "ai_visibility_sprint",
        "title_ar": "AEO Sprint — اظهر في إجابات AI",
        "goal_ar": "تحليل ظهور الشركة + خطة محتوى 30 يوم لـ ChatGPT/Gemini/Perplexity.",
        "kill_metric": "questions_visible",
        "required_integrations": ("google_business_profile",),
        "safety_rules_ar": ("لا scraping خارج المسموح",),
        "success_metrics": ("question_visibility_lift ≥ 30%",),
    },
    {
        "id": "competitive_response",
        "title_ar": "الرد على حركة منافس",
        "goal_ar": "رصد price change/offer/hiring → ردود + حملات + ROI breakdown.",
        "kill_metric": "competitor_signals_resolved",
        "required_integrations": (),
        "safety_rules_ar": ("لا تشهير", "لا اتهام عام",),
        "success_metrics": ("retention_lift", "win_rate_lift"),
    },
)


def list_intel_missions() -> dict[str, Any]:
    return {
        "count": len(INTEL_MISSIONS),
        "missions": list(INTEL_MISSIONS),
        "kill_feature_id": "first_10_opportunities",
    }


def recommend_missions(brain: GrowthBrain | None = None, *, limit: int = 3) -> dict[str, Any]:
    """Pick top-N missions for this customer based on brain state."""
    if brain is None:
        recommended = list(INTEL_MISSIONS)[:limit]
    else:
        # Simple heuristic: kill feature first, then prioritize by integrations
        ranked: list[tuple[dict, float]] = []
        for m in INTEL_MISSIONS:
            score = 50.0
            if m["id"] == "first_10_opportunities":
                score += 50  # always priority for new customers
            req = set(m["required_integrations"])
            connected = set(brain.channels_connected)
            if req.issubset(connected):
                score += 20
            else:
                score -= 10 * (len(req - connected))
            if "fill_pipeline" in brain.growth_priorities and m["id"] in (
                "first_10_opportunities", "revenue_leak_rescue"
            ):
                score += 15
            if "build_partner_channel" in brain.growth_priorities and m["id"] == "partnership_sprint":
                score += 15
            ranked.append((m, score))
        ranked.sort(key=lambda x: x[1], reverse=True)
        recommended = [m for m, _ in ranked[:limit]]
    return {
        "recommended": recommended,
        "rationale_ar": "تم الترتيب حسب priorities العميل + القنوات المربوطة.",
    }
