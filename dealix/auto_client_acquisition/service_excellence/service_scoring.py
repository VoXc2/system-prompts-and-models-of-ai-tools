"""Service Excellence scoring — every service must score ≥80 to ship."""

from __future__ import annotations

from typing import Any

from auto_client_acquisition.service_tower import Service, get_service


def score_clarity(service: Service | dict[str, Any]) -> int:
    """0..10. هل العميل يفهم ما الذي سيحصل عليه؟"""
    if isinstance(service, dict):
        outcome = service.get("outcome_ar", "")
        deliverables = service.get("deliverables_ar", [])
    else:
        outcome = service.outcome_ar
        deliverables = list(service.deliverables_ar)
    score = 5
    if len(outcome or "") >= 30:
        score += 3
    if len(deliverables) >= 3:
        score += 2
    return min(10, score)


def score_speed_to_value(service: Service | dict[str, Any]) -> int:
    """0..10. هل النتيجة خلال 7 أيام؟"""
    if isinstance(service, dict):
        model = service.get("pricing_model", "")
    else:
        model = service.pricing_model
    if model == "sprint":
        return 10
    if model == "monthly":
        return 6
    return 8  # one_time


def score_automation(service: Service | dict[str, Any]) -> int:
    """0..10. هل قابلة للأتمتة؟"""
    if isinstance(service, dict):
        steps = service.get("workflow_steps", [])
    else:
        steps = list(service.workflow_steps)
    auto_steps = sum(1 for s in steps
                     if s in {"intake", "data_check", "targeting",
                              "contactability", "strategy", "drafting",
                              "tracking", "proof", "upsell"})
    return min(10, auto_steps)


def score_compliance(service: Service | dict[str, Any]) -> int:
    """0..10. هل فيها opt-in/approval/audit؟"""
    if isinstance(service, dict):
        policy = service.get("approval_policy", "")
    else:
        policy = service.approval_policy
    if "approval_required" in policy:
        return 10
    if "draft_only" in policy:
        return 9
    if policy:
        return 6
    return 3


def score_proof(service: Service | dict[str, Any]) -> int:
    """0..10. هل لها proof metrics؟"""
    if isinstance(service, dict):
        metrics = service.get("proof_metrics", [])
    else:
        metrics = list(service.proof_metrics)
    return min(10, len(metrics) * 3)


def score_upsell(service: Service | dict[str, Any]) -> int:
    """0..10. هل لها upgrade path؟"""
    if isinstance(service, dict):
        upgrade = service.get("upgrade_path", [])
    else:
        upgrade = list(service.upgrade_path)
    return 10 if upgrade else 5


def calculate_service_excellence_score(
    service: Service | dict[str, Any] | str,
) -> dict[str, Any]:
    """Compute the full excellence score (0..100) + verdict."""
    if isinstance(service, str):
        s = get_service(service)
        if s is None:
            return {"error": f"unknown service: {service}"}
        service_obj: Service | dict[str, Any] = s
    else:
        service_obj = service

    clarity = score_clarity(service_obj)
    speed = score_speed_to_value(service_obj)
    automation = score_automation(service_obj)
    compliance = score_compliance(service_obj)
    proof = score_proof(service_obj)
    upsell = score_upsell(service_obj)

    # Each dimension max=10; we have 6 dimensions → max=60.
    # Add 4 baseline dimensions (uniqueness, scalability, ops, proof_data)
    # at fixed values for now (can become real signals later).
    uniqueness = 8        # deterministic — Dealix is Saudi-first
    scalability = 8       # multi-sector ready
    ops_daily = 7         # daily autopilot integration
    proof_data = min(10, proof + 2)

    total = (clarity + speed + automation + compliance
             + proof + upsell + uniqueness + scalability
             + ops_daily + proof_data)
    total = max(0, min(100, total))

    if total >= 80:
        status = "launch_ready"
    elif total >= 60:
        status = "beta_only"
    else:
        status = "needs_work"

    reasons: list[str] = []
    fixes: list[str] = []
    if compliance < 8:
        reasons.append("سياسة الاعتماد غير واضحة.")
        fixes.append("اضبط approval_policy على 'approval_required' أو 'draft_only'.")
    if proof < 6:
        reasons.append("Proof metrics قليلة.")
        fixes.append("أضف ≥3 proof metrics محددة.")
    if not upsell:
        reasons.append("لا يوجد upgrade path.")
        fixes.append("اربط الخدمة بخدمة أعلى عبر upgrade_path.")

    return {
        "service_id": (
            service_obj.get("id") if isinstance(service_obj, dict) else service_obj.id
        ),
        "total_score": total,
        "dimensions": {
            "clarity": clarity, "speed_to_value": speed,
            "automation": automation, "compliance": compliance,
            "proof": proof, "upsell": upsell,
            "uniqueness": uniqueness, "scalability": scalability,
            "ops_daily": ops_daily, "proof_data": proof_data,
        },
        "status": status,
        "reasons_ar": reasons,
        "required_fixes_ar": fixes,
    }
