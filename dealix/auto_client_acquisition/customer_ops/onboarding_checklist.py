"""Onboarding checklist for pilots (deterministic, no external calls)."""

from __future__ import annotations

from typing import Any


def build_onboarding_checklist(service_id: str | None = None) -> dict[str, Any]:
    sid = (service_id or "growth_starter").strip() or "growth_starter"
    return {
        "service_id": sid,
        "steps_ar": [
            "تأكيد الهدف (عملاء جدد / قائمة / شراكات / تشغيل يومي).",
            "جمع بيانات الشركة: القطاع، المدينة، العرض، رابط الموقع.",
            "تحديد القنوات المتاحة (إيميل، واتساب opt-in، CRM، نماذج).",
            "رفع قائمة اختيارية أو تأكيد عدم وجود قائمة.",
            "مراجعة سياسة الموافقات وعدم الإرسال الحي الافتراضي.",
            "تشغيل أول مهمة (تشخيص أو 10 فرص أو List Intelligence).",
            "تسليم أول Proof Pack أو ملخص أثر خلال النافذة المتفق عليها.",
        ],
        "approval_required": True,
        "live_send_default": False,
    }
