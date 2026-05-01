"""Illustrative unit economics — replace with real cohort data later."""

from __future__ import annotations

from typing import Any


def estimate_gross_margin() -> dict[str, Any]:
    return {
        "assumption": "SaaS gross margin target 75–85% after infra + support",
        "demo_value": 0.78,
        "notes_ar": "تكلفة LLM والبنية تدخل في COGS عند التوسع؛ راقبها أسبوعياً.",
    }


def estimate_cac_payback() -> dict[str, Any]:
    return {
        "months_range": [4, 9],
        "drivers": ["founder-led CAC low early", "partner rev share increases blended CAC"],
    }


def estimate_ltv() -> dict[str, Any]:
    return {
        "months_retention_base": 14,
        "expansion_uplift_pct": 25,
        "notes_ar": "LTV يتحسن مع proof pack وتمديد الاشتراك + الإضافات الأدائية.",
    }


def estimate_mrr_path() -> dict[str, Any]:
    return {
        "phase_private_beta": "10 customers × blended ARPU",
        "phase_paid_pilot": "5 paying × Growth OS average",
        "phase_public": "self-serve + inside sales",
        "disclaimer": "Modeling only — not a forecast commitment.",
    }
