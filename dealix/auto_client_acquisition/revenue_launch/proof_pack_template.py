"""Proof Pack template for private beta pilots."""

from __future__ import annotations

from typing import Any


def build_private_beta_proof_pack() -> dict[str, Any]:
    return {
        "sections_ar": [
            "ملخص الأسبوع",
            "الفرص المقترحة والمعتمدة/المتخطاة",
            "المسودات التي أُنشئت",
            "المخاطر التي تم كشفها أو منعها",
            "الاجتماعات المقترحة (مسودات فقط إن وُجدت)",
            "الخطوة التالية والترقية المقترحة",
        ],
        "metrics_keys": [
            "opportunities_count",
            "drafts_created",
            "approvals_pending",
            "risks_flagged",
            "meetings_suggested",
        ],
        "demo": True,
    }


def build_client_summary(metrics: dict[str, Any] | None = None) -> dict[str, Any]:
    m = metrics or {}
    return {
        "one_line_ar": (
            f"تمت معالجة {m.get('opportunities_count', 0)} فرصة تقريباً مع "
            f"{m.get('drafts_created', 0)} مسودة — المخاطر المسجلة: {m.get('risks_flagged', 0)}."
        ),
        "demo": True,
    }


def build_next_step_recommendation() -> dict[str, Any]:
    return {
        "next_step_ar": "إذا ارتفعت جودة القائمة: انتقل إلى Growth OS Pilot أو ذكاء قوائم أوسع.",
        "demo": True,
    }
