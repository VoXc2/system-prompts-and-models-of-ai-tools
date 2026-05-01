"""Go/No-Go launch readiness — 10 deterministic gates."""

from __future__ import annotations

from typing import Any

# All 10 gates Dealix Launch Control Room checks before approving sale.
LAUNCH_GATES: tuple[dict[str, str], ...] = (
    {"id": "tests_passed", "label_ar": "اختبارات pytest خضراء"},
    {"id": "routes_check", "label_ar": "scripts/print_routes.py لا يكشف تكرار"},
    {"id": "no_secrets", "label_ar": "scan الأسرار نظيف"},
    {"id": "staging_health", "label_ar": "/health على staging يرجع 200"},
    {"id": "supabase_staging", "label_ar": "Supabase staging مهيأ"},
    {"id": "service_catalog", "label_ar": "/services/catalog يعمل ويعرض ≥4 خدمات"},
    {"id": "private_beta_page", "label_ar": "landing/private-beta.html جاهزة"},
    {"id": "first_20_ready", "label_ar": "أول 20 prospect معرّفون"},
    {"id": "live_sends_disabled", "label_ar": "WHATSAPP/GMAIL/CALENDAR/MOYASAR live=false"},
    {"id": "payment_manual_ready", "label_ar": "Moyasar invoice/payment link جاهز يدوياً"},
)


def build_launch_readiness(
    *, statuses: dict[str, bool] | None = None,
) -> dict[str, Any]:
    """
    Build the launch-readiness checklist with current statuses.

    Pass `statuses` as a dict of gate_id → bool. Unknown gates default to False.
    """
    statuses = statuses or {}
    items: list[dict[str, Any]] = []
    passed = 0
    blockers: list[str] = []

    for gate in LAUNCH_GATES:
        ok = bool(statuses.get(gate["id"], False))
        items.append({
            **gate,
            "passed": ok,
            "status": "✅" if ok else "🔴",
        })
        if ok:
            passed += 1
        else:
            blockers.append(gate["label_ar"])

    total = len(LAUNCH_GATES)
    pct = round(100.0 * passed / total, 1) if total else 0.0

    return {
        "total_gates": total,
        "passed_gates": passed,
        "passed_pct": pct,
        "items": items,
        "blockers_ar": blockers,
        "ready_threshold_min_pct": 70.0,
    }


def decide_go_no_go(
    *, statuses: dict[str, bool] | None = None,
) -> dict[str, Any]:
    """
    Decide whether Dealix can sell today.

    Rules:
      - All "critical" gates must pass: no_secrets, live_sends_disabled, staging_health.
      - At least 7 of 10 gates must pass overall.
    """
    readiness = build_launch_readiness(statuses=statuses)
    passed_pct = readiness["passed_pct"]
    items = {it["id"]: it for it in readiness["items"]}

    critical = ("no_secrets", "live_sends_disabled", "staging_health")
    critical_failed = [c for c in critical if not items.get(c, {}).get("passed")]

    if critical_failed:
        verdict = "no_go"
        reason_ar = (
            f"بوابات حرجة فشلت: {', '.join(critical_failed)}. "
            "لا تبيع اليوم."
        )
    elif passed_pct >= 70:
        verdict = "go"
        reason_ar = (
            f"الجاهزية {passed_pct}%. "
            "ابدأ Private Beta — لا Public Launch."
        )
    else:
        verdict = "fix_then_go"
        reason_ar = (
            f"الجاهزية {passed_pct}% — أقل من 70%. "
            "ابدأ بإصلاح: " + ", ".join(readiness["blockers_ar"][:3])
        )

    return {
        "verdict": verdict,
        "reason_ar": reason_ar,
        "readiness": readiness,
        "next_actions_ar": _next_actions(readiness),
    }


def _next_actions(readiness: dict[str, Any]) -> list[str]:
    """Build concrete next-actions for any failing gates."""
    by_id = {it["id"]: it for it in readiness["items"]}
    actions: list[str] = []
    if not by_id["tests_passed"]["passed"]:
        actions.append("شغّل: pytest -q")
    if not by_id["routes_check"]["passed"]:
        actions.append("شغّل: python scripts/print_routes.py")
    if not by_id["no_secrets"]["passed"]:
        actions.append("شغّل grep scan + ألغِ أي مفتاح ظهر.")
    if not by_id["staging_health"]["passed"]:
        actions.append("انشر على Railway: railway up + curl /health.")
    if not by_id["supabase_staging"]["passed"]:
        actions.append("شغّل: supabase db push --dry-run ثم db push.")
    if not by_id["service_catalog"]["passed"]:
        actions.append("افحص: curl /api/v1/services/catalog.")
    if not by_id["private_beta_page"]["passed"]:
        actions.append("افتح landing/private-beta.html وتحقق من CTA.")
    if not by_id["first_20_ready"]["passed"]:
        actions.append("جهز Sheet 'Dealix First 20 Pipeline' بالعمدة.")
    if not by_id["live_sends_disabled"]["passed"]:
        actions.append(
            "تأكد: WHATSAPP_ALLOW_LIVE_SEND=false (وما يماثلها)."
        )
    if not by_id["payment_manual_ready"]["passed"]:
        actions.append("افتح Moyasar dashboard وجهّز invoice template.")
    return actions
