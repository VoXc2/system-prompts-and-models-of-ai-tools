"""Quality review — يمنع الخدمات الضعيفة من الإطلاق."""

from __future__ import annotations

from typing import Any

from auto_client_acquisition.service_tower import get_service

from .service_scoring import calculate_service_excellence_score


def block_if_missing_proof(service_id: str) -> dict[str, Any]:
    s = get_service(service_id)
    if s is None:
        return {"blocked": True, "reason_ar": f"خدمة غير معروفة: {service_id}"}
    if not s.proof_metrics:
        return {"blocked": True, "reason_ar": "لا توجد proof metrics."}
    return {"blocked": False}


def block_if_missing_approval_policy(service_id: str) -> dict[str, Any]:
    s = get_service(service_id)
    if s is None:
        return {"blocked": True, "reason_ar": f"خدمة غير معروفة: {service_id}"}
    if not s.approval_policy:
        return {"blocked": True, "reason_ar": "سياسة الاعتماد غير محددة."}
    return {"blocked": False}


def block_if_unclear_pricing(service_id: str) -> dict[str, Any]:
    s = get_service(service_id)
    if s is None:
        return {"blocked": True, "reason_ar": f"خدمة غير معروفة: {service_id}"}
    if s.pricing_max_sar < 0:
        return {"blocked": True, "reason_ar": "تسعير غير صحيح."}
    if s.pricing_max_sar > 0 and s.pricing_max_sar < s.pricing_min_sar:
        return {"blocked": True, "reason_ar": "نطاق التسعير غير منطقي."}
    return {"blocked": False}


def block_if_unsafe_channel(service_id: str) -> dict[str, Any]:
    """Block if a service depends on an unsafe channel (e.g., scraping)."""
    s = get_service(service_id)
    if s is None:
        return {"blocked": True, "reason_ar": f"خدمة غير معروفة: {service_id}"}
    unsafe = {"scraping", "auto_dm", "auto_connect", "browser_extension"}
    for ch in s.required_integrations:
        if ch.lower() in unsafe:
            return {"blocked": True,
                    "reason_ar": f"تكامل غير آمن: {ch}."}
    return {"blocked": False}


def review_service_before_launch(service_id: str) -> dict[str, Any]:
    """Run all gates + scoring before allowing a service to ship."""
    gates = {
        "proof": block_if_missing_proof(service_id),
        "approval": block_if_missing_approval_policy(service_id),
        "pricing": block_if_unclear_pricing(service_id),
        "channels": block_if_unsafe_channel(service_id),
    }
    blocked = [k for k, v in gates.items() if v.get("blocked")]
    score = calculate_service_excellence_score(service_id)

    if blocked:
        verdict = "blocked_at_gate"
    elif score.get("status") == "launch_ready":
        verdict = "launch_ready"
    elif score.get("status") == "beta_only":
        verdict = "beta_only"
    else:
        verdict = "needs_work"

    return {
        "service_id": service_id,
        "verdict": verdict,
        "score": score,
        "gates": gates,
        "blocked_reasons_ar": [
            gates[k].get("reason_ar", "") for k in blocked
        ],
    }
