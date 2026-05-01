"""Agent observability demo endpoints — evals and trace shapes."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body

from auto_client_acquisition.agent_observability.safety_eval import evaluate_safety
from auto_client_acquisition.agent_observability.saudi_tone_eval import evaluate_saudi_tone
from auto_client_acquisition.agent_observability.trace_events import build_trace_event

router = APIRouter(prefix="/api/v1/agent-observability", tags=["agent_observability"])


@router.get("/demo")
async def demo() -> dict[str, Any]:
    return {"ok": True, "message_ar": "تتبع وتقييم — اربط Langfuse في staging للإنتاج.", "demo": True}


@router.post("/eval/safety")
async def eval_safety(payload: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    return evaluate_safety(str(payload.get("text_ar") or ""))


@router.post("/eval/saudi-tone")
async def eval_saudi_tone(payload: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    return evaluate_saudi_tone(str(payload.get("text_ar") or ""))


@router.post("/trace/build")
async def trace_build(payload: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    return build_trace_event(
        workflow_name=str(payload.get("workflow_name") or "demo"),
        agent_name=str(payload.get("agent_name") or "dealix"),
        action_type=str(payload.get("action_type") or "draft"),
        policy_result=str(payload.get("policy_result") or "approval_required"),
        tool_called=payload.get("tool_called"),
        outcome=payload.get("outcome"),
        metadata=payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {},
    )
