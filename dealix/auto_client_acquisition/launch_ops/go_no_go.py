"""Deterministic go/no-go for private beta launch checklist."""

from __future__ import annotations

from typing import Any


def evaluate_go_no_go(flags: dict[str, Any] | None = None) -> dict[str, Any]:
    """flags: optional overrides for tests (e.g. tests_pass=False)."""
    f = flags or {}
    checks = {
        "tests_pass": bool(f.get("tests_pass", True)),
        "routes_ok": bool(f.get("routes_ok", True)),
        "staging_health_ok": bool(f.get("staging_health_ok", False)),
        "no_secrets_in_repo_scan": bool(f.get("no_secrets_in_repo_scan", True)),
        "whatsapp_live_send_disabled": bool(f.get("whatsapp_live_send_disabled", True)),
        "service_catalog_ok": bool(f.get("service_catalog_ok", True)),
        "landing_ready": bool(f.get("landing_ready", True)),
    }
    critical = [
        "tests_pass",
        "routes_ok",
        "no_secrets_in_repo_scan",
        "whatsapp_live_send_disabled",
        "service_catalog_ok",
    ]
    blockers = [k for k in critical if not checks[k]]
    if not checks["landing_ready"]:
        blockers.append("landing_ready")
    go = len(blockers) == 0
    warnings_ar: list[str] = []
    if not checks["staging_health_ok"]:
        warnings_ar.append("Staging غير مؤكد — يُنصح بتشغيل /health على بيئة staging قبل أول عميل.")
    return {
        "go": go,
        "checks": checks,
        "blockers": blockers,
        "warnings_ar": warnings_ar,
        "verdict_ar": "جاهز للبيتا الخاصة (كود وعمليات أساسية)" if go else "موقوف — راجع قائمة الـ blockers.",
        "demo": True,
    }
