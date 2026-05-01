"""Model Router router — task routing + provider registry + cost class."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body

from auto_client_acquisition.model_router import (
    ALL_PROVIDERS,
    ALL_TASK_TYPES,
    build_usage_demo,
    classify_cost,
    route_task,
)

router = APIRouter(prefix="/api/v1/model-router", tags=["model-router"])


@router.get("/providers")
async def providers() -> dict[str, Any]:
    return {
        "total": len(ALL_PROVIDERS),
        "providers": [p.to_dict() for p in ALL_PROVIDERS],
    }


@router.get("/tasks")
async def tasks() -> dict[str, Any]:
    return {"total": len(ALL_TASK_TYPES), "tasks": list(ALL_TASK_TYPES)}


@router.post("/route")
async def route(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    decision = route_task(
        payload.get("task_type", "low_cost_bulk"),
        requires_arabic=bool(payload.get("requires_arabic", False)),
        requires_vision=bool(payload.get("requires_vision", False)),
        sensitivity=payload.get("sensitivity", "low"),
        expected_input_tokens=int(payload.get("expected_input_tokens", 0)),
        expected_output_tokens=int(payload.get("expected_output_tokens", 0)),
        bulk=bool(payload.get("bulk", False)),
        primary_provider=payload.get("primary_provider"),
    )
    return decision.to_dict()


@router.post("/cost-class")
async def cost_class(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    return {
        "cost_class": classify_cost(
            task_type=payload.get("task_type", "low_cost_bulk"),
            expected_input_tokens=int(payload.get("expected_input_tokens", 0)),
            expected_output_tokens=int(payload.get("expected_output_tokens", 0)),
            bulk=bool(payload.get("bulk", False)),
        ),
    }


@router.get("/usage/demo")
async def usage_demo() -> dict[str, Any]:
    return build_usage_demo()
