"""Incident router — triage P0/P1 incidents with audit + response plan."""

from __future__ import annotations

from typing import Any

INCIDENT_SEVERITIES: tuple[dict[str, Any], ...] = (
    {
        "id": "SEV1",
        "label_ar": "حرج جداً — تسريب أمان / إرسال خاطئ / تعطل كامل",
        "first_action_minutes": 15,
        "communication_cadence_minutes": 30,
    },
    {
        "id": "SEV2",
        "label_ar": "خدمة مهمة معطلة لعدد كبير من العملاء",
        "first_action_minutes": 30,
        "communication_cadence_minutes": 60,
    },
    {
        "id": "SEV3",
        "label_ar": "خدمة معطلة لعميل واحد أو degraded performance",
        "first_action_minutes": 120,
        "communication_cadence_minutes": 240,
    },
)


def triage_incident(
    *,
    title: str,
    description: str = "",
    affected_customers: int = 1,
    has_data_leak: bool = False,
    has_unauthorized_send: bool = False,
) -> dict[str, Any]:
    """Triage an incident → severity + first actions + comms cadence."""
    if has_data_leak or has_unauthorized_send:
        sev = "SEV1"
        reason_ar = (
            "تسريب أمان أو إرسال غير معتمد — أعلى أولوية."
        )
    elif affected_customers >= 5:
        sev = "SEV2"
        reason_ar = f"عدد العملاء المتأثرين: {affected_customers} ≥ 5."
    else:
        sev = "SEV3"
        reason_ar = "حدث محدود التأثير."

    severity = next(
        (dict(s) for s in INCIDENT_SEVERITIES if s["id"] == sev),
        dict(INCIDENT_SEVERITIES[2]),
    )

    return {
        "title": title[:120],
        "description": description[:500],
        "severity": sev,
        "reason_ar": reason_ar,
        "severity_details": severity,
        "affected_customers": affected_customers,
        "has_data_leak": has_data_leak,
        "has_unauthorized_send": has_unauthorized_send,
        "approval_required": True,
        "live_send_allowed": False,
    }


def build_incident_response_plan(
    *,
    severity: str = "SEV3",
) -> dict[str, Any]:
    """Build the canonical incident response plan (Arabic)."""
    common_steps = [
        "1. تجميد الـ live actions على القناة المعنية فوراً.",
        "2. إخطار المؤسس + on-call operator.",
        "3. إنشاء incident channel مع timeline.",
        "4. مراجعة Action Ledger للأفعال المرتبطة.",
        "5. إذا تسريب: إخطار العملاء المتأثرين خلال 72 ساعة (PDPL).",
    ]

    if severity == "SEV1":
        plan = common_steps + [
            "6. تواصل مباشر مع المؤسس + خلية أزمة.",
            "7. كتابة post-mortem خلال 24 ساعة.",
            "8. مراجعة قانونية إن لزم.",
        ]
    elif severity == "SEV2":
        plan = common_steps + [
            "6. تحديث العملاء المتأثرين كل 60 دقيقة.",
            "7. post-mortem خلال 48 ساعة.",
        ]
    else:
        plan = common_steps + [
            "6. تحديث العميل المتأثر مع كل خطوة.",
            "7. post-mortem اختياري.",
        ]

    return {
        "severity": severity,
        "plan_ar": plan,
        "approval_required": True,
        "live_send_allowed": False,
    }
