"""سجل إثبات تجريبي — deterministic."""

from __future__ import annotations


def build_demo_proof_ledger() -> dict[str, object]:
    """أحداث توضيحية مع تقدير إيراد مؤثر بالريال (تقديرات عرض فقط)."""
    events: list[dict[str, object]] = [
        {
            "event_type": "draft_approved",
            "ts": "2026-04-28T09:15:00Z",
            "revenue_influenced_sar_estimate": 0,
            "notes_ar": "موافقة على مسودة قطاع عقار — لا إيراد بعد.",
        },
        {
            "event_type": "positive_reply",
            "ts": "2026-04-29T11:40:00Z",
            "revenue_influenced_sar_estimate": 12000,
            "notes_ar": "رد يطلب عرضاً مختصراً؛ احتمال متوسط.",
        },
        {
            "event_type": "meeting_booked",
            "ts": "2026-04-30T14:05:00Z",
            "revenue_influenced_sar_estimate": 45000,
            "notes_ar": "اجتماع أسبوعي مع قرار شراء محتمل.",
        },
        {
            "event_type": "compliance_block",
            "ts": "2026-05-01T08:00:00Z",
            "revenue_influenced_sar_estimate": 0,
            "notes_ar": "إيقاف إرسال جماعي؛ تجنب مخاطرة تنظيمية.",
        },
    ]
    return {"events": events, "demo": True}
