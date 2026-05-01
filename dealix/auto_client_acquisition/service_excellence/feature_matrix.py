"""Feature matrix per service — must_have / advanced / premium / future."""

from __future__ import annotations

from typing import Any

from auto_client_acquisition.service_tower import get_service

# 12 must-have features every premium Dealix service should ship with.
DEFAULT_MUST_HAVE: tuple[dict[str, object], ...] = (
    {"name_ar": "Self-Serve Intake", "value_ar": "العميل يبدأ بدون مكالمة.",
     "complexity": 2, "risk": 1, "proof_metric": "intake_completion_rate"},
    {"name_ar": "AI Recommendation",
     "value_ar": "النظام يوصي بالخدمة المناسبة من إجابات بسيطة.",
     "complexity": 3, "risk": 2, "proof_metric": "wizard_acceptance_rate"},
    {"name_ar": "Data Quality Check",
     "value_ar": "لا يستخدم بيانات سيئة.",
     "complexity": 3, "risk": 4, "proof_metric": "data_quality_score"},
    {"name_ar": "Contactability / Risk Gate",
     "value_ar": "يمنع التواصل الخطر تلقائياً.",
     "complexity": 4, "risk": 8, "proof_metric": "risks_blocked"},
    {"name_ar": "Channel Strategy",
     "value_ar": "يختار القناة الأفضل لكل contact.",
     "complexity": 4, "risk": 5, "proof_metric": "channel_success_rate"},
    {"name_ar": "Arabic Contextual Drafting",
     "value_ar": "رسائل سعودية، ليست ترجمة.",
     "complexity": 5, "risk": 3, "proof_metric": "saudi_tone_score"},
    {"name_ar": "Approval Cards",
     "value_ar": "CEO/Growth Manager يوافق من واتساب.",
     "complexity": 3, "risk": 2, "proof_metric": "approval_rate"},
    {"name_ar": "Execution Mode",
     "value_ar": "draft/export/approved فقط — لا live بدون env flag.",
     "complexity": 3, "risk": 9, "proof_metric": "live_send_violations"},
    {"name_ar": "Proof Pack",
     "value_ar": "تقرير قيمة محسوب.",
     "complexity": 4, "risk": 1, "proof_metric": "proof_pack_delivered"},
    {"name_ar": "Learning Loop",
     "value_ar": "يتعلم من Accept/Skip/Edit.",
     "complexity": 5, "risk": 2, "proof_metric": "accept_rate_30d"},
    {"name_ar": "Upsell Path",
     "value_ar": "يقود للخدمة الأعلى.",
     "complexity": 2, "risk": 1, "proof_metric": "upsell_conversion_rate"},
    {"name_ar": "Service Score",
     "value_ar": "يقيس نجاح الخدمة نفسها.",
     "complexity": 3, "risk": 1, "proof_metric": "service_excellence_score"},
)

# Service-specific premium features.
_PREMIUM_BY_SERVICE: dict[str, list[dict[str, object]]] = {
    "growth_os_monthly": [
        {"name_ar": "Daily Autopilot", "value_ar": "تشغيل ذاتي يومي.",
         "complexity": 6, "risk": 4, "proof_metric": "daily_decisions_made"},
        {"name_ar": "Revenue Leak Detector",
         "value_ar": "كشف التسريبات تلقائياً.",
         "complexity": 5, "risk": 2, "proof_metric": "leaks_detected"},
        {"name_ar": "Founder Shadow Board",
         "value_ar": "موجز أسبوعي مركّب.",
         "complexity": 4, "risk": 1, "proof_metric": "weekly_briefs_delivered"},
    ],
    "agency_partner_program": [
        {"name_ar": "Co-Branded Proof Pack", "value_ar": "Proof بعلامة الوكالة.",
         "complexity": 4, "risk": 2, "proof_metric": "co_branded_proofs"},
        {"name_ar": "Revenue Share Dashboard",
         "value_ar": "لوحة مشاركة الإيرادات.",
         "complexity": 5, "risk": 3, "proof_metric": "agency_revenue_sar"},
    ],
}


def build_feature_matrix(service_id: str) -> dict[str, Any]:
    """Build the full feature matrix for a service."""
    s = get_service(service_id)
    if s is None:
        return {"error": f"unknown service: {service_id}"}
    must_have = [dict(f) for f in DEFAULT_MUST_HAVE]
    premium = list(_PREMIUM_BY_SERVICE.get(service_id, []))
    return {
        "service_id": service_id,
        "service_name_ar": s.name_ar,
        "must_have": must_have,
        "advanced": premium,
        "premium": premium,
        "future": [],
        "total_features": len(must_have) + len(premium),
    }


def classify_features(service_id: str) -> dict[str, list[str]]:
    """Classify a service's features into tiers."""
    matrix = build_feature_matrix(service_id)
    if "error" in matrix:
        return {}
    return {
        "must_have": [str(f["name_ar"]) for f in matrix["must_have"]],
        "advanced": [str(f["name_ar"]) for f in matrix["advanced"]],
        "premium": [str(f["name_ar"]) for f in matrix["premium"]],
    }


def recommend_missing_features(service_id: str) -> list[dict[str, Any]]:
    """Recommend features the service may be missing."""
    matrix = build_feature_matrix(service_id)
    if "error" in matrix:
        return []
    # If the service has fewer than 12 must-haves, suggest the rest.
    if len(matrix["must_have"]) >= 12:
        return []
    return [{"name_ar": "Add to advanced tier",
             "rationale_ar": "خدمة قوية تستفيد من ميزات advanced."}]


def prioritize_features(features: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Order features by (lower complexity, lower risk, higher impact)."""
    return sorted(
        features,
        key=lambda f: (
            int(f.get("complexity", 9)),
            int(f.get("risk", 9)),
        ),
    )
