"""Contract / legal outline templates — not legal advice; approval required."""

from __future__ import annotations

from typing import Any


def list_contract_templates() -> dict[str, Any]:
    templates = [
        {
            "id": "pilot_agreement",
            "title_ar": "مسودة اتفاق Pilot",
            "outline_ar": ["نطاق الخدمة", "مدة التجربة", "القياس (Proof)", "PDPL ومصادر البيانات", "إيقاف فوري"],
            "legal_review_required": True,
            "approval_required": True,
            "not_legal_advice": True,
        },
        {
            "id": "dpa_pilot",
            "title_ar": "مسودة DPA تجريبية",
            "outline_ar": ["أدوار المعالج/المتحكم", "الاحتفاظ", "حقوق الأفراد", "الأمان", "نقل البيانات"],
            "legal_review_required": True,
            "approval_required": True,
            "not_legal_advice": True,
        },
        {
            "id": "referral_partner",
            "title_ar": "مسودة اتفاق إحالة/شريك",
            "outline_ar": ["نسبة الإحالة", "تسوية الفواتير", "العلامة التجارية", "سرية"],
            "legal_review_required": True,
            "approval_required": True,
            "not_legal_advice": True,
        },
    ]
    return {"templates": templates, "demo": True}
