"""Agent Observability router — trace events + safety/tone evals."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body

from auto_client_acquisition.agent_observability import (
    build_trace_event,
    run_eval_pack,
    safety_eval,
    saudi_tone_eval,
)

router = APIRouter(prefix="/api/v1/agent-observability", tags=["agent-observability"])


@router.post("/trace/build")
async def trace_build(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    return build_trace_event(
        workflow_name=payload.get("workflow_name", "unknown"),
        agent_name=payload.get("agent_name", "unknown"),
        status=payload.get("status", "started"),
        user_id=payload.get("user_id"),
        company_id=payload.get("company_id"),
        tool=payload.get("tool"),
        policy_result=payload.get("policy_result"),
        risk_level=payload.get("risk_level"),
        approval_status=payload.get("approval_status"),
        latency_ms=float(payload.get("latency_ms", 0)),
        cost_estimate=float(payload.get("cost_estimate", 0)),
        payload=payload.get("payload"),
        output=payload.get("output"),
    )


@router.post("/safety/eval")
async def safety_eval_endpoint(text: str = Body(..., embed=True)) -> dict[str, Any]:
    return safety_eval(text)


@router.post("/tone/eval")
async def tone_eval(text: str = Body(..., embed=True)) -> dict[str, Any]:
    return saudi_tone_eval(text)


@router.get("/evals/run")
async def evals_run() -> dict[str, Any]:
    return run_eval_pack()
