"""Deterministic research brief — no web calls."""

from __future__ import annotations

from typing import Any


def build_service_research_brief(service_id: str) -> dict[str, Any]:
    return {
        "service_id": service_id,
        "hypotheses_ar": [
            "تحسين رسالة الـ CTA يزيد الردود.",
            "تقليل المتابعات يقلل الشكاوى.",
        ],
        "experiments_ar": ["A/B لنبرة سعودية قصيرة", "تغيير ترتيب القنوات في الخطة"],
        "demo": True,
    }


def generate_feature_hypotheses(service_id: str) -> list[str]:
    return [f"{service_id}: إضافة checklist امتثال", f"{service_id}: تقرير مقارنة منافسين"]


def recommend_next_experiments(service_id: str) -> list[str]:
    return [f"{service_id}: تجربة سعر Pilot أعلى قليلاً", f"{service_id}: دمج Proof مع targeting"]


def build_monthly_service_review(service_id: str) -> dict[str, Any]:
    return {
        "service_id": service_id,
        "review_ar": [
            "ماذا تحسّن؟",
            "ماذا أوقفنا؟",
            "ما التجربة القادمة؟",
        ],
        "demo": True,
    }
