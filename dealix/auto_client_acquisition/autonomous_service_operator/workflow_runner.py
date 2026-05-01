"""Workflow runner — advances service pipelines + checks completion."""

from __future__ import annotations

from typing import Any

from .service_orchestrator import (
    SERVICE_PIPELINE_STEPS,
    build_service_pipeline,
    run_service_step,
)


def build_workflow_state(service_id: str, *, customer_id: str = "") -> dict[str, Any]:
    """Initialize a new workflow state for a service."""
    pipeline = build_service_pipeline(service_id, customer_id=customer_id)
    return {
        "service_id": service_id,
        "customer_id": customer_id,
        "pipeline": pipeline,
        "human_approvals_received": 0,
        "human_approvals_pending": 0,
        "blocked_actions": 0,
    }


def advance_workflow(
    workflow_state: dict[str, Any], *, step_id: str | None = None,
) -> dict[str, Any]:
    """Advance the underlying pipeline by one step."""
    pipeline = workflow_state.get("pipeline") or build_service_pipeline(
        str(workflow_state.get("service_id", "")),
    )
    pipeline = run_service_step(pipeline, step_id=step_id)
    workflow_state["pipeline"] = pipeline
    return workflow_state


def is_workflow_complete(workflow_state: dict[str, Any]) -> bool:
    """True iff all canonical steps have run."""
    pipeline = workflow_state.get("pipeline", {})
    completed = pipeline.get("completed_steps", [])
    return len(completed) >= len(SERVICE_PIPELINE_STEPS)
