"""Launch gate checks for services."""

from __future__ import annotations

from typing import Any

from auto_client_acquisition.service_tower.service_catalog import get_service_by_id


def review_service_before_launch(service_id: str) -> dict[str, Any]:
    svc = get_service_by_id(service_id) or {}
    issues: list[str] = []
    if not svc.get("pricing_range_sar"):
        issues.append("missing_pricing")
    if not svc.get("approval_policy"):
        issues.append("missing_approval_policy")
    if not svc.get("proof_metrics"):
        issues.append("missing_proof_metrics")
    ok = len(issues) == 0
    return {"service_id": service_id, "ok": ok, "issues": issues, "demo": True}


def block_if_missing_proof(service_id: str) -> bool:
    return not (get_service_by_id(service_id) or {}).get("proof_metrics")


def block_if_missing_approval_policy(service_id: str) -> bool:
    return not (get_service_by_id(service_id) or {}).get("approval_policy")


def block_if_unclear_pricing(service_id: str) -> bool:
    if service_id == "free_growth_diagnostic":
        return False
    pr = (get_service_by_id(service_id) or {}).get("pricing_range_sar") or {}
    return pr.get("max") in (None, 0)


def block_if_unsafe_channel(service_id: str) -> bool:
    """Block launch if policy suggests unguarded external send."""
    pol = ((get_service_by_id(service_id) or {}).get("approval_policy") or "").lower()
    return pol in ("", "none", "auto_send")


def review_all_services() -> dict[str, Any]:
    from auto_client_acquisition.service_tower.service_catalog import list_service_ids

    results: list[dict[str, Any]] = []
    for sid in list_service_ids():
        results.append(review_service_before_launch(sid))
    ok_count = sum(1 for r in results if r.get("ok"))
    return {
        "count": len(results),
        "ok_count": ok_count,
        "results": results,
        "demo": True,
    }
