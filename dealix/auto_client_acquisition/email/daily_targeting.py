"""
Daily Targeting Agent — the autonomous revenue brain.

Runs every morning at 7am Asia/Riyadh (via /api/v1/automation/daily-targeting/run).

Process:
1. Pull candidates from Saudi directory accounts + Maps + previous queue.
2. Exclude opt_outs, suppressed, bounced, recently-contacted, high-risk, no allowed_use.
3. Enrich top scored candidates (crawl + tech detect + emails) — capped to budget.
4. Re-score with fresh signals.
5. Pick TOP 50 across diversified sectors.
6. For each: generate Khaliji email (LLM if Groq available, else template).
7. Queue with approval_required=True.
8. Return daily plan + exact follow-up schedule.

LLM usage:
- Personalization upgrade per account (one short LLM call to write angle).
- Reply classification on incoming emails.
- Both gracefully degrade to rules-mode if no LLM key.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any

from auto_client_acquisition.pipelines.scoring import (
    compute_data_quality,
    compute_lead_score,
)

log = logging.getLogger(__name__)


@dataclass
class DailyTargetingResult:
    generated_at: str
    target_date: str
    candidates_evaluated: int
    excluded_opt_out: int
    excluded_suppressed: int
    excluded_recently_contacted: int
    excluded_high_risk: int
    excluded_no_allowed_use: int
    excluded_personal_email_phone_only: int
    selected_count: int
    selected: list[dict[str, Any]] = field(default_factory=list)
    sector_split: dict[str, int] = field(default_factory=dict)
    daily_email_limit: int = 50
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "generated_at": self.generated_at,
            "target_date": self.target_date,
            "candidates_evaluated": self.candidates_evaluated,
            "excluded": {
                "opt_out": self.excluded_opt_out,
                "suppressed": self.excluded_suppressed,
                "recently_contacted": self.excluded_recently_contacted,
                "high_risk": self.excluded_high_risk,
                "no_allowed_use": self.excluded_no_allowed_use,
                "personal_email_only": self.excluded_personal_email_phone_only,
            },
            "selected_count": self.selected_count,
            "selected": self.selected,
            "sector_split": self.sector_split,
            "daily_email_limit": self.daily_email_limit,
            "notes": self.notes,
        }


# ── Sector-specific message angle map ─────────────────────────────
ANGLE_MAP: dict[str, str] = {
    "real_estate_developer": (
        "كل lead عقاري متأخر دقيقة = احتمال خسارة العميل لمنافس. Dealix يرد خلال 45 ثانية بالعربي الخليجي، "
        "يأخذ الميزانية + الموقع + الموعد، ويسلم العميل المؤهل لمندوبكم."
    ),
    "construction": (
        "بدل ما تضيع طلبات تسعير المشاريع بين واتساب + اتصالات + إيميلات، Dealix يجمع المواصفات + الميزانية + "
        "المهلة الزمنية لكل طلب، ويفرز الجاهز للتسعير عن الباقي."
    ),
    "hospitality": (
        "حجوزات MICE + إفطار/سحور + قاعات = leads عربية تحتاج رد فوري. Dealix يخدم العميل بالعربي ويحجز موعد معاينة."
    ),
    "events": (
        "كل lead لقاعة حفل = موسم. Dealix يرد فوراً، يأخذ التاريخ + العدد + الباقة، ويحجز معاينة في تقويم فريقكم."
    ),
    "logistics": (
        "RFQ شحن: العميل يطلب عرض، إذا تأخرتم 10 دقائق رحل لمنافس. Dealix يرد بالعربي خلال دقيقة، "
        "يجمع الوزن + الوجهة + التاريخ، ويفتح ticket في نظامكم."
    ),
    "restaurant": (
        "Dealix يرد على استفسارات التموين + الحجوزات + الفرنشايز بالعربي خلال 45 ثانية، ويفرز الجاد منها للإدارة."
    ),
    "saas": (
        "Dealix هو AI sales rep بالعربي الخليجي يتكامل مع HubSpot/Salesforce/Zoho. "
        "إذا تبيعون SaaS داخل السعودية، نضمن الرد على inbound leads خلال 45 ثانية."
    ),
    "marketing_agency": (
        "Dealix هو AI sales rep بالعربي يتكامل مع HubSpot/Salesforce/Zoho. كشركة تسويق سعودية، لكم خياران: "
        "تستخدمونه لعملائكم (resell) → 25% MRR شهرياً، أو تشترون لعملاء وكالتكم. كلاهما revenue share."
    ),
}


def angle_for(sector: str | None) -> str:
    if not sector:
        return "Dealix يرد على inbound leads بالعربي الخليجي خلال 45 ثانية."
    return ANGLE_MAP.get(sector.lower(),
                        "Dealix يرد على inbound leads بالعربي الخليجي خلال 45 ثانية.")


def opener_for(priority: str) -> str:
    return "السلام عليكم" if priority == "P0" else "مرحباً"


def render_email_template(account: dict[str, Any], priority: str) -> dict[str, str]:
    """Deterministic email template — used as fallback or LLM seed."""
    company = (account.get("company_name") or "فريقكم").strip()
    angle = angle_for(account.get("sector"))
    opener = opener_for(priority)
    cta = (
        "Pilot 7 أيام بـ 499 ريال — نشتغل على leadsكم نحن، تشوفون النتيجة، ثم تقرّرون. "
        "تناسبكم 20 دقيقة هذا الأسبوع؟"
    )
    body = (
        f"{opener} {company}،\n\n"
        f"{angle}\n\n"
        f"{cta}\n\n"
        "سامي\n"
        "Dealix — https://dealix.me\n"
        "📅 https://calendly.com/sami-assiri11/dealix-demo"
    )
    subject = f"Dealix — تجربة تأهيل عملاء لـ {company[:60]}"
    return {"subject_ar": subject, "body_ar": body}


async def llm_personalize(account: dict[str, Any], base_email: dict[str, str]) -> dict[str, str]:
    """
    Optional LLM upgrade — returns the personalized email if Groq available,
    else returns base unchanged. Single short call per account.
    """
    import asyncio
    has_llm = bool(
        os.getenv("GROQ_API_KEY") or os.getenv("ANTHROPIC_API_KEY") or os.getenv("OPENAI_API_KEY")
    )
    if not has_llm:
        return base_email
    try:
        from core.llm.router import get_router
        from core.llm.base import Message
    except Exception:
        return base_email

    prompt = (
        "أنت محرر إيميلات بيع B2B بالعربي الخليجي السعودي.\n"
        f"الشركة: {account.get('company_name')}\n"
        f"القطاع: {account.get('sector_ar') or account.get('sector')}\n"
        f"المدينة: {account.get('city_ar') or account.get('city')}\n"
        f"الإيميل المقترح:\n{base_email['body_ar']}\n\n"
        "حسّن جملة 'سبب التواصل' بحيث تذكر شيئاً محدداً عن نشاط الشركة المحتمل في القطاع/المدينة "
        "(مثلاً 'عقار في الرياض = مشاريع compounds + شقق سكنية' أو 'فندق في أبها = leads المواسم'). "
        "احتفظ بنفس الطول، نفس الخاتمة، نفس الـ CTA. لا تضف وعود غير مذكورة.\n"
        "أرجع فقط الـ body المحدّث بدون أي شرح."
    )
    try:
        router = get_router()
        resp = await asyncio.wait_for(
            router.complete([Message(role="user", content=prompt)], max_tokens=400, temperature=0.4),
            timeout=8.0,
        )
        new_body = (resp.content or "").strip()
        if 50 < len(new_body) < 2000 and "Dealix" in new_body:
            return {**base_email, "body_ar": new_body, "personalized_by_llm": "true"}
    except Exception as exc:  # noqa: BLE001
        log.warning("llm_personalize_failed account=%s err=%s",
                    account.get("company_name", "?"), exc)
    return base_email


def select_top_n_diversified(
    candidates: list[dict[str, Any]],
    *,
    target_count: int,
    sector_caps: dict[str, int] | None = None,
) -> list[dict[str, Any]]:
    """
    Pick top-N with sector diversity so we don't blast 50 emails to the same vertical.
    Default cap per sector: max(target_count // 4, 10) to ensure variety.
    """
    sector_caps = sector_caps or {}
    default_cap = max(target_count // 4, 10)
    chosen: list[dict[str, Any]] = []
    counts: dict[str, int] = {}
    # Sort by total_score desc, then DQ desc
    sorted_pool = sorted(
        candidates,
        key=lambda c: (-(c.get("total_score") or 0), -(c.get("data_quality_score") or 0)),
    )
    for c in sorted_pool:
        sec = (c.get("sector") or "other").lower()
        cap = sector_caps.get(sec, default_cap)
        if counts.get(sec, 0) >= cap:
            continue
        chosen.append(c)
        counts[sec] = counts.get(sec, 0) + 1
        if len(chosen) >= target_count:
            break
    return chosen


def compute_followup_schedule(send_date: datetime) -> dict[str, str]:
    """Return ISO-8601 timestamps for +2/+5/+10/+30 follow-ups."""
    return {
        "day_2": (send_date + timedelta(days=2)).isoformat(),
        "day_5": (send_date + timedelta(days=5)).isoformat(),
        "day_10": (send_date + timedelta(days=10)).isoformat(),
        "day_30_nurture": (send_date + timedelta(days=30)).isoformat(),
    }
