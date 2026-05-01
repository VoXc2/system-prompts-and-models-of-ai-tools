"""Readiness scorecard for launch — simple weighted score."""

from __future__ import annotations

from typing import Any

from auto_client_acquisition.launch_ops.go_no_go import evaluate_go_no_go


def build_launch_scorecard(extra: dict[str, Any] | None = None) -> dict[str, Any]:
    ex = extra or {}
    g = evaluate_go_no_go(ex)
    score = 100
    if not g["checks"].get("tests_pass"):
        score -= 30
    if not g["checks"].get("routes_ok"):
        score -= 15
    if not g["checks"].get("staging_health_ok"):
        score -= 10
    if not g["checks"].get("no_secrets_in_repo_scan"):
        score -= 40
    if not g["checks"].get("whatsapp_live_send_disabled"):
        score -= 25
    if not g["checks"].get("service_catalog_ok"):
        score -= 10
    if not g["checks"].get("landing_ready"):
        score -= 5
    score = max(0, min(100, score))
    status = "ready" if score >= 75 and g["go"] else "needs_work"
    return {
        "readiness_score": score,
        "status": status,
        "go_no_go": g,
        "summary_ar": f"درجة الجاهزية {score}/١٠٠ — {status}.",
        "demo": True,
    }
