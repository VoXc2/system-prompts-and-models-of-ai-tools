"""Standard workflow builder for services."""

from __future__ import annotations

from typing import Any

from auto_client_acquisition.service_tower.mission_templates import build_service_workflow


def build_workflow(service_id: str) -> dict[str, Any]:
    return build_service_workflow(service_id)


def validate_workflow(service_id: str) -> dict[str, Any]:
    wf = build_workflow(service_id)
    steps = wf.get("steps") or []
    ok = "approve" in steps or "approval" in steps
    return {"ok": ok, "steps": steps, "has_approval_step": ok, "demo": True}


def build_day_by_day_execution_plan(service_id: str) -> dict[str, Any]:
    wf = build_workflow(service_id)
    steps = list(wf.get("steps") or [])
    plan: list[dict[str, Any]] = []
    for i, s in enumerate(steps[:14], start=1):
        plan.append({"day": i, "step": s, "note_ar": f"اليوم {i}: {s}"})
    return {"service_id": service_id, "plan": plan, "demo": True}


def build_approval_steps(service_id: str) -> dict[str, Any]:
    wf = build_workflow(service_id)
    return {"service_id": service_id, "approval_steps": wf.get("approval_gates") or ["approve"], "demo": True}
