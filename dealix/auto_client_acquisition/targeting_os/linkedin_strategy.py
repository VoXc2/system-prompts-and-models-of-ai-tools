"""LinkedIn strategy — Lead Forms + manual research + Ads, NO scraping/auto-DM."""

from __future__ import annotations

from typing import Any


def linkedin_do_not_do() -> list[str]:
    """The hard 'NEVER' list for LinkedIn — encoded explicitly so tests can lock it."""
    return [
        "scrape_profiles",
        "auto_connect",
        "auto_dm",
        "browser_automation",
        "fake_engagement",
        "download_contacts_from_linkedin",
        "buy_scraped_leads",
        "use_unauthorized_extensions",
    ]


def recommend_linkedin_strategy(
    segment: str, *, goal: str = "fill_pipeline",
) -> dict[str, Any]:
    """
    Recommend a compliant LinkedIn strategy for a segment.

    Always picks Lead Gen Forms / manual / Ads — never scraping/auto-DM.
    """
    return {
        "segment": segment,
        "goal": goal,
        "primary": "lead_gen_forms",
        "secondary": ["linkedin_ads", "manual_account_research", "content_engagement"],
        "do_not_do": linkedin_do_not_do(),
        "rationale_ar": (
            "لينكدإن يحظر crawlers/bots/extensions التي تسحب البيانات أو ترسل/توجّه "
            "رسائل أو تصنع تفاعلاً غير أصيل؛ لذلك نعتمد فقط على Lead Gen Forms، "
            "الإعلانات، والبحث اليدوي المعتمد."
        ),
    }


def build_lead_gen_form_plan(
    segment: str, offer: str, *, campaign_name: str = "",
) -> dict[str, Any]:
    """Build a structured Lead Gen Form campaign plan."""
    name = campaign_name or f"{segment} — {offer or 'Pilot'}"
    return {
        "campaign_name": name,
        "audience_ar": (
            f"المستهدفون: {segment} — أصحاب القرار في القطاع المحدد، "
            "السعودية والخليج، حجم 11-200 موظف."
        ),
        "offer_ar": offer or "Pilot 7 أيام لاستخراج 10 فرص B2B + رسائل عربية + Proof Pack.",
        "lead_magnet_ar": (
            "Free Growth Diagnostic — تقرير من 5 صفحات: 3 فرص + رسالة عربية + خطة 7 أيام."
        ),
        "form_fields_required": ["full_name", "company_name", "work_email", "role"],
        "hidden_fields": [
            {"name": "campaign_name", "value": name},
            {"name": "sector", "value": segment},
            {"name": "sales_owner", "value": "{{owner}}"},
            {"name": "ad_set", "value": "{{ad_set_id}}"},
        ],
        "approval_required": True,
        "notes_ar": (
            "الـ hidden fields ضرورية لمعرفة مصدر كل lead و ربطه بالـCRM. "
            "كل lead من Lead Form يدخل Dealix كـ source=linkedin_lead_form (آمن)."
        ),
    }


def build_manual_research_task(
    account: dict[str, Any], *, role: str = "head_of_sales",
) -> dict[str, Any]:
    """Build a manual LinkedIn research task — for a human, not automation."""
    company = account.get("name", "?")
    return {
        "task_type": "manual_linkedin_research",
        "company": company,
        "target_role": role,
        "instructions_ar": [
            f"افتح صفحة شركة {company} على LinkedIn يدوياً.",
            f"حدد الشخص الذي يحمل دور {role}.",
            "لا تستخدم أي extension أو bot لاستخراج البيانات.",
            "سجّل اسم الشخص + مسماه فقط — لا تنسخ أي معلومات إضافية.",
            "أضف الاسم في Dealix كـ source=manual_research → سيدخل needs_review.",
        ],
        "approval_required": True,
        "completion_minutes": 5,
    }


def build_safe_connection_message(
    role: str, company: str, *, offer: str = "",
) -> dict[str, Any]:
    """
    Build a safe connection-request message for LinkedIn (manual send by user).

    Never auto-sends. Always returns draft with approval_required=True.
    """
    role_ar = role
    body_ar = (
        f"هلا، تابعت أعمال {company} مؤخراً وعجبني التوسع. "
        f"أعمل على Dealix كمدير نمو عربي للشركات السعودية. "
        f"يناسبك نتعارف هنا؟"
    )
    if offer:
        body_ar += f" وفي حال فيه فرصة لـ{offer}، أكون سعيد أشاركك أمثلة."

    return {
        "channel": "linkedin_connection_request",
        "target_role": role_ar,
        "target_company": company,
        "body_ar": body_ar[:280],   # LinkedIn note limit
        "approval_required": True,
        "live_send_allowed": False,
        "send_method": "manual_only",
        "notes_ar": (
            "هذه مسودة. أرسلها يدوياً من حسابك على LinkedIn. "
            "Dealix لا يرسل تلقائياً ولا يستخدم أي extension أو bot."
        ),
    }
