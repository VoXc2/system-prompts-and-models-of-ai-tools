"""Onboarding checklist — the 8-step Pilot onboarding flow."""

from __future__ import annotations

from typing import Any

ONBOARDING_STEPS: tuple[dict[str, Any], ...] = (
    {
        "id": "select_goal",
        "label_ar": "اختيار الهدف الأساسي",
        "input_required": "goal",
        "minutes": 2,
        "approval_required": False,
    },
    {
        "id": "select_bundle",
        "label_ar": "اختيار الباقة المناسبة",
        "input_required": "bundle_id",
        "minutes": 3,
        "approval_required": True,
    },
    {
        "id": "company_intake",
        "label_ar": "بيانات الشركة",
        "input_required": "company_profile",
        "minutes": 5,
        "approval_required": False,
    },
    {
        "id": "connect_channels",
        "label_ar": "ربط القنوات (Gmail/Calendar/Sheets — drafts فقط)",
        "input_required": "channels_oauth",
        "minutes": 8,
        "approval_required": True,
    },
    {
        "id": "upload_or_source",
        "label_ar": "رفع قائمة أو ربط مصدر leads",
        "input_required": "list_or_source",
        "minutes": 5,
        "approval_required": True,
    },
    {
        "id": "risk_review",
        "label_ar": "مراجعة المخاطر (PDPL + سمعة القناة)",
        "input_required": None,
        "minutes": 4,
        "approval_required": True,
    },
    {
        "id": "first_service_run",
        "label_ar": "تشغيل أول خدمة (First 10 Opportunities أو List Intelligence)",
        "input_required": None,
        "minutes": 0,  # async — Dealix runs it
        "approval_required": True,
    },
    {
        "id": "first_proof_pack",
        "label_ar": "استلام أول Proof Pack",
        "input_required": None,
        "minutes": 0,  # async
        "approval_required": False,
    },
)


def build_onboarding_checklist(
    *,
    customer_id: str = "",
    company_name: str = "",
    bundle_id: str | None = None,
) -> dict[str, Any]:
    """Build a fresh onboarding checklist for a new customer."""
    return {
        "customer_id": customer_id,
        "company_name": company_name,
        "bundle_id": bundle_id,
        "total_steps": len(ONBOARDING_STEPS),
        "current_step_id": ONBOARDING_STEPS[0]["id"],
        "steps": [
            {**dict(s), "completed": False} for s in ONBOARDING_STEPS
        ],
        "estimated_total_minutes": sum(int(s["minutes"]) for s in ONBOARDING_STEPS),
        "live_send_allowed": False,
    }


def update_onboarding_step(
    checklist: dict[str, Any],
    *,
    step_id: str,
    completed: bool = True,
    notes: str = "",
) -> dict[str, Any]:
    """Mark a step complete + advance current_step_id."""
    steps = list(checklist.get("steps", []))
    found = False
    for i, s in enumerate(steps):
        if s["id"] == step_id:
            s["completed"] = bool(completed)
            if notes:
                s["notes"] = notes[:200]
            steps[i] = s
            found = True
            # advance current_step_id
            if completed and i + 1 < len(steps):
                checklist["current_step_id"] = steps[i + 1]["id"]
            elif completed and i + 1 == len(steps):
                checklist["current_step_id"] = "done"
            break

    if not found:
        return {**checklist, "error": f"unknown step: {step_id}"}

    completed_count = sum(1 for s in steps if s["completed"])
    checklist["steps"] = steps
    checklist["progress_pct"] = round(
        100 * completed_count / max(1, len(steps)), 1,
    )
    return checklist
