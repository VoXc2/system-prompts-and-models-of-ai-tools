"""B2B email drafts — approval-first, no misleading subjects."""

from __future__ import annotations

from typing import Any


def draft_b2b_email(contact: dict[str, Any], offer: str, why_now: str, *, tone: str = "professional_saudi") -> dict[str, Any]:
    name = str(contact.get("name") or "فريق العمل")
    co = str(contact.get("company") or "شركتكم")
    return {
        "subject_ar": f"فكرة سريعة لـ {co} — {offer[:40]}",
        "body_ar": (
            f"السلام عليكم {name}،\n\n"
            f"لاحظنا: {why_now}\n"
            f"نقدّم {offer} بمسار مسودات + موافقة قبل أي إرسال جماعي.\n\n"
            f"هل يناسبكم ردّ قصير خلال الأسبوع؟\n\n"
            f"مع تحيات فريق Dealix"
        ),
        "tone": tone,
        "approval_required": True,
        "demo": True,
    }


def include_unsubscribe_footer(body: str) -> str:
    footer = "\n\n---\nلإلغاء الاشتراك أو طلب عدم التواصل: ردّ بكلمة «توقف»."
    return body + footer


def recommend_pacing(domain_reputation: str) -> dict[str, Any]:
    rep = (domain_reputation or "unknown").lower()
    daily = 20 if rep == "strong" else 8 if rep == "medium" else 3
    return {"max_daily_drafts": daily, "note_ar": "تدرّج في الحجم لحماية سمعة النطاق.", "demo": True}


def score_email_risk(contact: dict[str, Any], message: str) -> dict[str, Any]:
    score = 25
    if "ضمان" in message or "100%" in message:
        score += 40
    if classify_unknown(contact):
        score += 20
    return {"risk_score": min(100, score), "needs_review": score > 50, "demo": True}


def build_followup_sequence(contact: dict[str, Any], offer: str) -> list[dict[str, Any]]:
    return [
        {"day_offset": 3, "draft_ar": f"متابعة خفيفة بخصوص {offer} — هل نرسل مثالاً؟", "approval_required": True},
        {"day_offset": 7, "draft_ar": "إغلاق لطيف: نتوفر عند الحاجة.", "approval_required": True},
    ]


def classify_unknown(contact: dict[str, Any]) -> bool:
    src = str(contact.get("source") or "").lower()
    return src in ("", "unknown", "unknown_source", "cold_list")
