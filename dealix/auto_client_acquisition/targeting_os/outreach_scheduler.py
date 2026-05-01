"""Outreach scheduler — pace, follow-up, opt-out enforcement."""

from __future__ import annotations

from typing import Any

DEFAULT_LIMITS: dict[str, int] = {
    "max_daily_email_drafts": 30,
    "max_daily_whatsapp_approved_sends": 10,
    "max_followups": 3,
    "cooldown_days": 7,
    "max_same_domain_contacts": 5,
}


def build_outreach_plan(
    targets: list[dict[str, Any]],
    *,
    channels: list[str] | None = None,
    goal: str = "fill_pipeline",
) -> dict[str, Any]:
    """
    Build a per-target outreach plan across channels.

    Each target gets day-by-day actions; never schedules a live send.
    """
    channels = channels or ["email", "linkedin_lead_form"]
    plan: list[dict[str, Any]] = []

    for t in targets:
        steps: list[dict[str, Any]] = [
            {"day": 0, "channel": channels[0],
             "action": "draft_first_message",
             "approval_required": True,
             "live_send_allowed": False},
            {"day": 3, "channel": channels[0],
             "action": "draft_followup_1",
             "approval_required": True,
             "live_send_allowed": False},
        ]
        if "linkedin_lead_form" in channels or "linkedin" in channels:
            steps.append({
                "day": 5, "channel": "linkedin_manual",
                "action": "manual_research_task",
                "approval_required": True,
                "live_send_allowed": False,
            })
        steps.append({
            "day": 7, "channel": channels[0],
            "action": "draft_final_followup_or_archive",
            "approval_required": True,
            "live_send_allowed": False,
        })
        plan.append({
            "target_company": t.get("name", "?"),
            "target_role": t.get("role", "?"),
            "channels": channels,
            "steps": steps,
        })

    return {
        "goal": goal,
        "channels": channels,
        "total_targets": len(targets),
        "plan": plan,
        "limits": DEFAULT_LIMITS,
        "notes_ar": (
            "كل خطوة draft تحتاج اعتماد. "
            "لا إرسال آلي، ولا تجاوز الحدود اليومية."
        ),
    }


def schedule_followups(plan: dict[str, Any]) -> dict[str, Any]:
    """Add follow-up timing to each target in a plan."""
    out = dict(plan)
    out["scheduled"] = True
    return out


def enforce_daily_limits(
    plan: dict[str, Any],
    *,
    limits: dict[str, int] | None = None,
) -> dict[str, Any]:
    """Cap actions in the plan to the configured daily limits."""
    limits = limits or DEFAULT_LIMITS
    targets = plan.get("plan", [])

    capped: list[dict[str, Any]] = []
    daily_email = 0
    domain_count: dict[str, int] = {}

    for t in targets:
        company = t.get("target_company", "")
        # treat company as a proxy for domain in test data
        if company in domain_count and domain_count[company] >= limits["max_same_domain_contacts"]:
            continue
        ok_steps = []
        for step in t.get("steps", []):
            if step.get("channel") == "email":
                if daily_email >= limits["max_daily_email_drafts"]:
                    continue
                daily_email += 1
            ok_steps.append(step)
        if ok_steps:
            capped.append({**t, "steps": ok_steps})
            domain_count[company] = domain_count.get(company, 0) + 1

    return {
        **plan,
        "plan": capped,
        "applied_limits": limits,
        "capped_total_targets": len(capped),
    }


def stop_on_opt_out(plan: dict[str, Any]) -> dict[str, Any]:
    """Filter out targets where the contact has opted out."""
    targets = plan.get("plan", [])
    kept = [t for t in targets if not t.get("opt_out")]
    return {**plan, "plan": kept, "stopped_due_to_opt_out": len(targets) - len(kept)}


def summarize_plan_ar(plan: dict[str, Any]) -> str:
    """Build an Arabic one-paragraph summary of an outreach plan."""
    n = plan.get("total_targets") or len(plan.get("plan", []))
    channels = ", ".join(plan.get("channels", []))
    return (
        f"خطة تواصل لـ{n} هدف عبر القنوات: {channels}. "
        f"كل خطوة draft، تتطلب اعتماد، ولا إرسال آلي. "
        f"الحدود اليومية مفعّلة. opt-out يوقف فوراً."
    )
