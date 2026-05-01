"""GTM plans and scripts — deterministic artifacts."""

from __future__ import annotations

from typing import Any


def first_10_customers_plan() -> dict[str, Any]:
    return {
        "who": [
            "B2B founders in Riyadh/Jeddah with outbound pain",
            "SMB revenue leaders in clinics, logistics, training",
            "Agencies wanting a differentiated Saudi stack",
        ],
        "how_to_find": [
            "Warm intros from Sami network",
            "LinkedIn lists + manual verify (no cold WhatsApp)",
            "Sector events + follow-up drafts",
        ],
        "qualification": [
            "Has ICP clarity or willing to define in onboarding",
            "Uses WhatsApp for business conversations",
            "Willing to pilot with weekly proof pack",
        ],
        "pilot_offer_ar": "تجربة 7 أيام لمشغّل المؤسس + تقرير جاهزية + 10 فرص مؤهلة تجريبياً.",
        "success_criteria": [
            "Weekly active review of daily brief",
            ">=3 approved drafts / week OR 1 booked meeting / month",
            "Documented ROI story",
        ],
        "actions": [
            "Build list of 30 targets, close 10 pilots",
            "Run demo using command center snapshot + market radar",
            "Send WhatsApp-style approval cards in demo only",
        ],
    }


def first_100_customers_plan() -> dict[str, Any]:
    return {
        "channel_mix": [
            "Founder content (Arabic case studies)",
            "Partner agencies (15–30% rev share band)",
            "Referrals from pilots",
            "Select webinars (PDPL-safe outreach)",
        ],
        "partnerships": ["Regional CRM implementers", "Supabase consultants", "GTM freelancers"],
        "referral_loop": "Give pilots a structured referral incentive after proof pack month 2.",
        "notes": ["Cold email only with suppression lists + compliance review."],
    }


def channel_strategy() -> dict[str, Any]:
    return {
        "primary": "founder_led_outbound_plus_partners",
        "secondary": "community_whatsapp_opt_in",
        "avoid": ["cold_whatsapp_broadcasts", "unchecked_scraped_lists"],
    }


def partner_strategy() -> dict[str, Any]:
    return {
        "agency": {"rev_share_pct_range": [15, 30], "setup_fee_sar_range": [3000, 25000]},
        "technology": ["Supabase partners for memory hardening"],
        "positioning_ar": "الشريك يبيع التنفيذ؛ Dealix يبيع المنصة والاشتراك.",
    }


def founder_led_sales_script() -> dict[str, Any]:
    return {
        "discovery_questions": [
            "من أهم 3 قرارات إيرادات هذا الأسبوع؟",
            "كيف تتابع واتساب اليوم بدون فوضى؟",
            "وش يثبت للإدارة أن التسويق نجح؟",
        ],
        "demo_story_ar": "أعرض: رادار السوق → فرصة → مسودة عربية → زر موافقة → تقرير جاهزية.",
        "objections": {
            "crm": "Dealix ليس بديل CRM بالكامل؛ هو طبقة إيرادات وفهم سياق فوق أدواتكم.",
            "price": "نبدأ بمشغّل المؤسس أو pilot بسيط ثم نربط الأداء بالنتائج.",
            "ai_failed_before": "هنا التنفيذ مسودة + موافقة + تتبع؛ لا إرسال تلقائي خارجي.",
        },
        "pilot_framing_ar": "أسبوعان: موجز يومي + 10 فرص + تقرير جاهزية + مسودات بموافقة.",
    }
