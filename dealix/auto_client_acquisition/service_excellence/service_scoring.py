"""Service Excellence Score 0–100 — launch readiness."""

from __future__ import annotations

from typing import Any

from auto_client_acquisition.service_tower.service_catalog import get_service_by_id


def _clamp(n: int, lo: int = 0, hi: int = 10) -> int:
    return max(lo, min(hi, n))


def score_clarity(service: dict[str, Any]) -> int:
    return 9 if service.get("outcome_ar") else 4


def score_speed_to_value(service: dict[str, Any]) -> int:
    steps = len(service.get("workflow_steps") or [])
    return _clamp(10 - max(0, steps - 8))


def score_automation(service: dict[str, Any]) -> int:
    return 7 if len(service.get("required_integrations") or []) <= 2 else 6


def score_compliance(service: dict[str, Any]) -> int:
    pol = (service.get("approval_policy") or "").lower()
    if "legal" in pol:
        return 10
    if "approval" in pol or "draft" in pol:
        return 9
    return 6


def score_proof(service: dict[str, Any]) -> int:
    return 8 if service.get("proof_metrics") else 4


def score_upsell(service: dict[str, Any]) -> int:
    return 8 if service.get("upgrade_path") else 5


def calculate_service_excellence_score(service_id: str) -> dict[str, Any]:
    svc = get_service_by_id(service_id) or {}
    dims = {
        "clarity": score_clarity(svc),
        "speed_to_value": score_speed_to_value(svc),
        "automation": score_automation(svc),
        "compliance": score_compliance(svc),
        "proof": score_proof(svc),
        "upsell": score_upsell(svc),
    }
    # Weighted sum → 0..100 scale (6 dims * ~10 max)
    total = sum(dims.values()) * 100 // 60
    status = "launch_ready"
    reasons_ar: list[str] = []
    if total < 80:
        status = "beta_only"
        reasons_ar.append("الدرجة أقل من ٨٠ — إطلاق محدود أو تحسين قبل الإعلان.")
    if (svc.get("risk_level") or "") == "high" and total < 90:
        status = "needs_work"
        reasons_ar.append("مخاطر عالية: عزّز الامتثال والاختبارات.")
    required_fixes: list[str] = []
    if not svc.get("proof_metrics"):
        required_fixes.append("أضف proof_metrics واضحة.")
    return {
        "service_id": service_id,
        "dimensions": dims,
        "total_score": total,
        "status": status,
        "reasons_ar": reasons_ar or ["جاهزية جيدة للعرض الداخلي."],
        "required_fixes": required_fixes,
        "demo": True,
    }
