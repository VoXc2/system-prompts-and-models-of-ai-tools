"""Revenue DNA snapshot — structured JSON."""

from __future__ import annotations

from typing import Any


def build_revenue_dna(context: dict[str, Any] | None) -> dict[str, Any]:
    ctx = context or {}
    return {
        "primary_motion_ar": str(ctx.get("primary_motion_ar") or "مبيعات مباشرة + شراكات"),
        "cycle_days_estimate": int(ctx.get("cycle_days_estimate") or 45),
        "channels_weight": {"whatsapp": 0.2, "email": 0.35, "meetings": 0.45},
        "risk_notes_ar": str(ctx.get("risk_notes_ar") or "تأخر الموافقات الداخلية لدى العميل."),
        "demo": True,
    }
