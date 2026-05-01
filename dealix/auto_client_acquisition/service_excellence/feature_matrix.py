"""Per-service feature tiers — deterministic."""

from __future__ import annotations

from typing import Any

from auto_client_acquisition.service_tower.service_catalog import get_service_by_id

_BASE_FEATURES: list[dict[str, Any]] = [
    {
        "id": "intake_self_serve",
        "name_ar": "استقبال ذاتي",
        "tier": "must_have",
        "value_ar": "يبدأ العميل بدون احتكاك.",
        "complexity": "low",
        "risk": "low",
        "proof_metric": "completion_rate",
        "launch_priority": 1,
    },
    {
        "id": "contactability_gate",
        "name_ar": "بوابة contactability",
        "tier": "must_have",
        "value_ar": "يمنع التواصل الخطر.",
        "complexity": "medium",
        "risk": "low",
        "proof_metric": "blocked_risk_count",
        "launch_priority": 1,
    },
    {
        "id": "approval_cards",
        "name_ar": "كروت موافقة",
        "tier": "must_have",
        "value_ar": "لا إرسال خارجي بدون قرار بشري.",
        "complexity": "low",
        "risk": "low",
        "proof_metric": "approval_rate",
        "launch_priority": 1,
    },
    {
        "id": "proof_pack",
        "name_ar": "Proof Pack",
        "tier": "must_have",
        "value_ar": "يثبت العائد أسبوعياً.",
        "complexity": "medium",
        "risk": "low",
        "proof_metric": "revenue_influenced_sar",
        "launch_priority": 2,
    },
    {
        "id": "channel_mix",
        "name_ar": "مزج قنوات آمن",
        "tier": "advanced",
        "value_ar": "إيميل أولاً، واتساب بموافقة/opt-in.",
        "complexity": "high",
        "risk": "medium",
        "proof_metric": "meetings_booked",
        "launch_priority": 3,
    },
    {
        "id": "research_lab_hook",
        "name_ar": "ربط مختبر تحسين",
        "tier": "premium",
        "value_ar": "backlog تحسين أسبوعي.",
        "complexity": "medium",
        "risk": "low",
        "proof_metric": "experiment_win_rate",
        "launch_priority": 4,
    },
]


def build_feature_matrix(service_id: str) -> dict[str, Any]:
    svc = get_service_by_id(service_id)
    feats = list(_BASE_FEATURES)
    if svc and svc.get("risk_level") == "high":
        feats.append(
            {
                "id": "extra_compliance_review",
                "name_ar": "مراجعة امتثال إضافية",
                "tier": "must_have",
                "value_ar": "خدمة عالية المخاطر.",
                "complexity": "medium",
                "risk": "high",
                "proof_metric": "compliance_checks",
                "launch_priority": 1,
            }
        )
    return {"service_id": service_id, "features": feats, "demo": True}


def classify_features(service_id: str) -> dict[str, list[str]]:
    fm = build_feature_matrix(service_id)
    buckets: dict[str, list[str]] = {"must_have": [], "advanced": [], "premium": [], "future": []}
    for f in fm.get("features") or []:
        tier = str(f.get("tier") or "must_have")
        if tier not in buckets:
            tier = "must_have"
        buckets[tier].append(str(f.get("id")))
    return buckets


def recommend_missing_features(service_id: str) -> list[str]:
    """Stub: suggest future items."""
    return ["connector_webhooks", "durable_workflows"] if service_id == "growth_os" else []


def prioritize_features(features: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(features or [], key=lambda f: int(f.get("launch_priority", 99)))
