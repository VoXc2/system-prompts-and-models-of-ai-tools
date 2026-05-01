"""Multi-day outreach plan — limits and approvals, no execution."""

from __future__ import annotations

from typing import Any

_DEFAULT_LIMITS = {
    "max_daily_email_drafts": 8,
    "max_daily_whatsapp_approved_sends": 0,
    "max_followups": 3,
    "cooldown_days": 2,
    "max_same_domain_contacts": 5,
}


def build_outreach_plan(targets: list[dict[str, Any]], channels: list[str], goal: str) -> dict[str, Any]:
    steps = []
    for i, t in enumerate(targets[:15]):
        steps.append(
            {
                "day_offset": (i % 3) * 2,
                "target_id": t.get("id") or f"t{i}",
                "channel": channels[0] if channels else "email",
                "action": "draft_only",
                "approval_required": True,
            }
        )
    return {
        "goal": goal,
        "steps": steps,
        "limits": _DEFAULT_LIMITS,
        "summary_ar": "خطة MVP — كل خطوة مسودة أو موافقة؛ لا إرسال تلقائي.",
        "demo": True,
    }


def schedule_followups(plan: dict[str, Any]) -> list[dict[str, Any]]:
    return [{"followup_after_days": 3, "approval_required": True} for _ in plan.get("steps", [])[:5]]


def enforce_daily_limits(plan: dict[str, Any], limits: dict[str, Any] | None = None) -> dict[str, Any]:
    lim = {**_DEFAULT_LIMITS, **(limits or {})}
    steps = plan.get("steps") or []
    capped = steps[: lim["max_daily_email_drafts"]]
    return {"capped_steps": len(capped), "limits_applied": lim, "truncated": len(steps) > len(capped), "demo": True}


def stop_on_opt_out(plan: dict[str, Any]) -> dict[str, Any]:
    return {"stopped": True, "reason": "opt_out_global", "note_ar": "أي opt-out يوقف الخطة فوراً.", "demo": True}


def summarize_plan_ar(plan: dict[str, Any]) -> str:
    n = len(plan.get("steps") or [])
    return f"خطة بـ {n} خطوة — كلها تتطلب موافقة قبل التنفيذ الخارجي."
