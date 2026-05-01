"""LinkedIn-compliant strategy — Lead Gen, ads, manual tasks only."""

from __future__ import annotations

from typing import Any


def linkedin_do_not_do() -> list[str]:
    return [
        "scraping_profiles",
        "auto_dm",
        "auto_connect",
        "bulk_export_without_consent",
        "browser_automation_on_linkedin_feed",
    ]


def recommend_linkedin_strategy(segment: str, goal: str) -> dict[str, Any]:
    return {
        "strategy": "lead_gen_forms_first",
        "segment": segment,
        "goal": goal,
        "do_not_do": linkedin_do_not_do(),
        "summary_ar": "استخدم Lead Gen Forms والإعلانات والمهام اليدوية المعتمدة — لا scraping ولا رسائل آلية.",
        "demo": True,
    }


def build_lead_gen_form_plan(segment: str, offer: str, campaign_name: str) -> dict[str, Any]:
    return {
        "campaign_name": campaign_name or "dealix_pilot",
        "audience_hint": f"{segment} — أصحاب قرار في الخدمات B2B",
        "offer": offer,
        "hidden_fields_suggested": ["campaign_name", "sector", "sales_owner"],
        "next_steps_ar": [
            "أنشئ حملة Lead Gen في LinkedIn Campaign Manager.",
            "اربط الحقول المخفية بمصدر Dealix.",
            "لا تفعّل إرسالاً آلياً من Dealix إلى InMail بدون سياسة.",
        ],
        "demo": True,
    }


def build_manual_research_task(account: dict[str, Any], role: str) -> dict[str, Any]:
    return {
        "task_type": "manual_linkedin_lookup",
        "company": account.get("company"),
        "target_role": role,
        "instructions_ar": f"ابحث يدوياً عن {role} في {account.get('company')} — انسخ الرابط العام فقط، لا أتمتة.",
        "demo": True,
    }


def build_safe_connection_message(role: str, company: str, offer: str) -> dict[str, Any]:
    return {
        "message_ar": (
            f"تحية، أتابع عمل {company}. نعمل على {offer} لفرق المبيعات في السعودية. "
            f"إن كان عندكم اهتمام، أرسل ملخصاً قصيراً دون التزام."
        ),
        "approval_required": True,
        "channel": "linkedin_manual_only",
        "demo": True,
    }
