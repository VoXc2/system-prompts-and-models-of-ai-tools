"""Recommend sellable service from intake — deterministic, no live actions."""

from __future__ import annotations

from typing import Any

from auto_client_acquisition.service_tower.service_catalog import get_service_by_id, list_service_ids


def recommend_service(
    company_type: str,
    goal: str,
    has_contact_list: bool = False,
    channels: list[str] | None = None,
    budget_sar: int | None = None,
) -> dict[str, Any]:
    ct = (company_type or "").lower().strip()
    gl = (goal or "").lower().strip()
    ch = [c.lower() for c in (channels or [])]

    recommended = "first_10_opportunities"
    reasons: list[str] = []

    if "agency" in ct or "وكالة" in company_type:
        recommended = "agency_partner_program"
        reasons.append("وكالات: قناة توزيع + برنامج شركاء.")
    elif has_contact_list or "list" in gl or "csv" in gl or "قائمة" in goal:
        recommended = "list_intelligence"
        reasons.append("قائمة مرفوعة: ذكاء القوائم يقلل المخاطر أولاً.")
    elif "email" in gl or "بريد" in goal or "inbox" in gl:
        recommended = "email_revenue_rescue"
        reasons.append("هدف بريدي: إنقاذ فرص ضائعة بمسودات فقط.")
    elif "partner" in gl or "شراكة" in goal:
        recommended = "partner_sprint"
        reasons.append("هدف شراكات: سباق شركاء منظم.")
    elif "meeting" in gl or "اجتماع" in goal:
        recommended = "meeting_booking_sprint"
        reasons.append("تحويل prospects لاجتماعات بمسودات موافقة.")
    elif "linkedin" in gl or "لينكد" in goal:
        recommended = "linkedin_lead_gen_setup"
        reasons.append("لينكدإن: Lead Gen رسمي بدون أتمتة مخالفة.")
    elif "whatsapp" in gl or "واتساب" in goal or "whatsapp" in ch:
        recommended = "whatsapp_compliance_setup"
        reasons.append("واتساب: امتثال وopt-in قبل أي حملة.")
    elif "local" in gl or "عيادة" in goal or "متجر" in goal:
        recommended = "local_growth_os"
        reasons.append("نمو محلي: تقييمات + inbound + دفع draft.")
    elif budget_sar is not None and budget_sar < 1500:
        recommended = "free_growth_diagnostic"
        reasons.append("ميزانية منخفضة: تشخيص مجاني ثم ترقية.")

    svc = get_service_by_id(recommended)
    return {
        "recommended_service_id": recommended,
        "service": svc,
        "reasons_ar": reasons or ["أسرع إثبات قيمة: سباق ١٠ فرص."],
        "live_send": False,
        "demo": True,
    }


def build_intake_questions(service_id: str) -> dict[str, Any]:
    svc = get_service_by_id(service_id)
    if not svc:
        return {"service_id": service_id, "questions": [], "error": "unknown_service", "demo": True}
    qs: list[dict[str, str]] = []
    for inp in svc.get("inputs_required") or []:
        qs.append(
            {
                "field": inp,
                "prompt_ar": f"ما قيمة الحقل: {inp}؟",
                "required": "true",
            }
        )
    return {"service_id": service_id, "questions": qs, "demo": True}


def validate_service_inputs(service_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    svc = get_service_by_id(service_id)
    if not svc:
        return {"ok": False, "missing": ["unknown_service"], "demo": True}
    missing: list[str] = []
    for key in svc.get("inputs_required") or []:
        if key not in (payload or {}) or payload.get(key) in (None, "", []):
            missing.append(key)
    return {"ok": len(missing) == 0, "missing": missing, "demo": True}


def summarize_recommendation_ar(result: dict[str, Any]) -> str:
    rid = result.get("recommended_service_id") or "غير محدد"
    reasons = result.get("reasons_ar") or []
    tail = " ".join(reasons) if reasons else ""
    return f"التوصية: {rid}. {tail} لا يوجد إرسال حي من هذا المسار."


def start_service(service_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    """MVP: validate + return workflow handle — no side effects."""
    v = validate_service_inputs(service_id, payload or {})
    svc = get_service_by_id(service_id)
    return {
        "started": bool(v.get("ok")),
        "service_id": service_id,
        "validation": v,
        "workflow_ref": f"wf_{service_id}_demo" if v.get("ok") else None,
        "approval_required": True,
        "live_send": False,
        "service_snapshot": {"name_ar": (svc or {}).get("name_ar"), "risk_level": (svc or {}).get("risk_level")},
        "demo": True,
    }
