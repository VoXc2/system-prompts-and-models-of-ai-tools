"""Service wizard — يوصي بالخدمة المناسبة من إجابات بسيطة."""

from __future__ import annotations

from typing import Any

from .service_catalog import ALL_SERVICES, get_service


def recommend_service(
    *,
    company_type: str = "",
    goal: str = "fill_pipeline",
    has_contact_list: bool = False,
    channels: list[str] | None = None,
    budget_sar: int = 1000,
) -> dict[str, Any]:
    """
    Recommend the best-fit service based on inputs. Deterministic.
    """
    channels = channels or []
    company_type_lc = (company_type or "").lower()

    chosen_id: str
    reason: str

    # Highest priority first.
    if "agency" in company_type_lc or "وكالة" in company_type:
        chosen_id = "agency_partner_program" if budget_sar >= 10_000 else "partner_sprint"
        reason = "وكالة → برنامج شريك أو سبرنت شراكات."
    elif has_contact_list:
        chosen_id = "list_intelligence"
        reason = "العميل لديه قائمة → ابدأ بـ List Intelligence."
    elif "founder" in company_type_lc or "مؤسس" in company_type:
        chosen_id = "self_growth_operator"
        reason = "مؤسس بدون فريق نمو → Self-Growth Operator."
    elif "executive" in company_type_lc or "ceo" in company_type_lc:
        chosen_id = "executive_growth_brief"
        reason = "CEO/تنفيذي → موجز نمو يومي."
    elif "whatsapp" in company_type_lc or "واتساب" in company_type:
        chosen_id = "whatsapp_compliance_setup"
        reason = "حالة واتساب عشوائية → امتثال أولاً."
    elif goal == "rescue_lost_revenue":
        chosen_id = "email_revenue_rescue"
        reason = "الهدف استعادة إيراد ضائع → Email Revenue Rescue."
    elif goal == "book_meetings":
        chosen_id = "meeting_booking_sprint"
        reason = "الهدف اجتماعات → Meeting Booking Sprint."
    elif goal == "expand_partners":
        chosen_id = "partner_sprint"
        reason = "الهدف شراكات → Partner Sprint."
    elif budget_sar >= 2999:
        chosen_id = "growth_os_monthly"
        reason = "الميزانية شهرية → Growth OS."
    else:
        chosen_id = "first_10_opportunities_sprint"
        reason = "الافتراضي: ابدأ بـ 10 فرص في 10 دقائق."

    service = get_service(chosen_id)
    return {
        "recommended_service_id": chosen_id,
        "service": service.to_dict() if service else None,
        "reason_ar": reason,
        "next_step_ar": (
            "املأ نموذج الـ intake، وسنبدأ خلال 24 ساعة عمل."
        ),
    }


def build_intake_questions(service_id: str) -> dict[str, Any]:
    """Return intake questions for a service. Empty if service unknown."""
    s = get_service(service_id)
    if s is None:
        return {"error": f"unknown service: {service_id}", "questions": []}

    base_q = [
        {"key": "company_name", "label_ar": "اسم الشركة", "required": True},
        {"key": "sector", "label_ar": "القطاع", "required": True},
        {"key": "city", "label_ar": "المدينة", "required": True},
        {"key": "decision_maker_name", "label_ar": "اسم صانع القرار", "required": True},
        {"key": "decision_maker_role", "label_ar": "المسمى الوظيفي", "required": True},
    ]
    extra = []
    if "uploaded_csv" in s.inputs_required:
        extra.append({"key": "uploaded_csv", "label_ar": "ملف CSV", "required": True})
    if "offer" in s.inputs_required:
        extra.append({"key": "offer", "label_ar": "وصف العرض", "required": True})
    if "goal" in s.inputs_required:
        extra.append({"key": "goal", "label_ar": "الهدف الأساسي", "required": True})
    if "channels_available" in s.inputs_required:
        extra.append({"key": "channels", "label_ar": "القنوات المتاحة", "required": False})

    return {
        "service_id": service_id,
        "service_name_ar": s.name_ar,
        "questions": base_q + extra,
        "approval_required": True,
    }


def validate_service_inputs(
    service_id: str, payload: dict[str, Any],
) -> dict[str, Any]:
    """Validate intake payload against service requirements."""
    s = get_service(service_id)
    if s is None:
        return {"valid": False, "errors_ar": [f"خدمة غير معروفة: {service_id}"]}

    errors: list[str] = []
    for required in s.inputs_required:
        if required in ("uploaded_csv", "offer", "goal", "channels_available",
                        "ICP", "calendar_link", "company_profile",
                        "current_practice", "ad_budget", "client_count",
                        "partner_goal", "team_size", "channels", "agency_profile",
                        "prospect_list", "gmail_label", "contact_list",
                        "goals", "sector", "city"):
            if not payload.get(required):
                errors.append(f"الحقل ناقص: {required}")

    return {
        "valid": not errors,
        "errors_ar": errors,
        "service_id": service_id,
    }


def summarize_recommendation_ar(result: dict[str, Any]) -> str:
    """Build a one-paragraph Arabic recommendation summary."""
    sid = result.get("recommended_service_id", "?")
    reason = result.get("reason_ar", "")
    svc = result.get("service") or {}
    name = svc.get("name_ar", sid)
    outcome = svc.get("outcome_ar", "")
    return (
        f"الخدمة المقترحة: {name}. السبب: {reason} "
        f"المخرجات: {outcome}"
    )
