"""Model routing API — configuration hints only."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body

from auto_client_acquisition.model_router.provider_registry import list_providers
from auto_client_acquisition.model_router.task_router import list_tasks, route_task

router = APIRouter(prefix="/api/v1/model-router", tags=["model_router"])


@router.get("/tasks")
async def tasks() -> dict[str, Any]:
    return list_tasks()


@router.post("/route")
async def route(payload: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    return route_task(str(payload.get("task_type") or ""))


@router.get("/providers")
async def providers() -> dict[str, Any]:
    return list_providers()
