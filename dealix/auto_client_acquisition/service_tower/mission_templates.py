"""Mission templates — يحوّل الخدمة إلى workflow قابل للتشغيل."""

from __future__ import annotations

from typing import Any

from .service_catalog import get_service

# Map service → growth mission ID (in intelligence_layer.mission_engine).
_SERVICE_TO_MISSION: dict[str, str] = {
    "free_growth_diagnostic": "first_10_opportunities",
    "list_intelligence": "first_10_opportunities",
    "first_10_opportunities_sprint": "first_10_opportunities",
    "self_growth_operator": "first_10_opportunities",
    "growth_os_monthly": "first_10_opportunities",
    "email_revenue_rescue": "revenue_leak_rescue",
    "meeting_booking_sprint": "meeting_booking_sprint",
    "partner_sprint": "partnership_sprint",
    "agency_partner_program": "partnership_sprint",
    "whatsapp_compliance_setup": "first_10_opportunities",
    "linkedin_lead_gen_setup": "first_10_opportunities",
    "executive_growth_brief": "first_10_opportunities",
}


def get_default_mission_steps(service_id: str) -> list[dict[str, Any]]:
    """Return default workflow steps for a service."""
    s = get_service(service_id)
    if s is None:
        return []
    steps: list[dict[str, Any]] = []
    for i, name in enumerate(s.workflow_steps):
        steps.append({
            "order": i + 1,
            "step_id": name,
            "label_ar": _STEP_LABELS_AR.get(name, name),
            "approval_required": name in {
                "approval", "execution_or_export", "drafting",
            },
            "live_action": False,
        })
    return steps


_STEP_LABELS_AR: dict[str, str] = {
    "intake": "جمع المدخلات",
    "data_check": "فحص جودة البيانات",
    "targeting": "تحديد الأهداف",
    "contactability": "تقييم إمكانية التواصل",
    "strategy": "استراتيجية القناة",
    "drafting": "صياغة المسودات",
    "approval": "اعتماد بشري",
    "execution_or_export": "تنفيذ/تصدير",
    "tracking": "متابعة النتائج",
    "proof": "Proof Pack",
    "upsell": "ترقية الخدمة",
    "agency_onboarding": "إعداد الوكالة",
    "client_diagnostic": "تشخيص عميل الوكالة",
    "proposal": "عرض",
    "pilot": "Pilot",
    "proof_pack": "Proof Pack",
    "revenue_share": "Revenue Share",
    "aggregate": "تجميع الإشارات",
    "prioritize": "ترتيب الأولويات",
    "deliver": "تسليم الموجز",
}


def build_service_workflow(service_id: str) -> dict[str, Any]:
    """Build the full Arabic workflow for a service."""
    s = get_service(service_id)
    if s is None:
        return {"error": f"unknown service: {service_id}"}

    steps = get_default_mission_steps(service_id)
    return {
        "service_id": service_id,
        "service_name_ar": s.name_ar,
        "workflow_steps": steps,
        "deliverables_ar": list(s.deliverables_ar),
        "approval_policy": s.approval_policy,
        "live_send_allowed": False,
        "estimated_completion_days": (
            7 if s.pricing_model == "sprint"
            else 30 if s.pricing_model == "monthly"
            else 1
        ),
        "linked_growth_mission": _SERVICE_TO_MISSION.get(service_id),
    }


def map_service_to_growth_mission(service_id: str) -> str | None:
    """Return the growth-mission ID linked to a service (or None)."""
    return _SERVICE_TO_MISSION.get(service_id)
