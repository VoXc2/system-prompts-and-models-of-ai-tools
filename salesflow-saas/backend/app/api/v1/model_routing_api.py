"""Model Routing API — Sovereign Routing Fabric dashboard and configuration."""
from __future__ import annotations

from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.sovereign import ModelRoutingConfig
from app.services.sovereign_routing import SovereignRoutingService, LANE_DEFAULTS

router = APIRouter(prefix="/model-routing", tags=["Model Routing — توجيه النماذج"])


class RoutingConfigCreate(BaseModel):
    lane: str
    primary_model: str
    fallback_model: str | None = None
    provider: str
    max_tokens: int | None = None
    temperature: float | None = None
    requires_structured_output: bool = False
    arabic_quality_check: bool = False
    hitl_required: bool = False
    approval_class: str = "A"


class RoutingMetrics(BaseModel):
    lane: str
    avg_latency_ms: int | None = None
    schema_adherence_pct: float | None = None
    contradiction_rate_pct: float | None = None
    arabic_quality_score: float | None = None
    cost_per_task_sar: float | None = None


@router.get("/configs")
async def list_routing_configs(
    tenant_id: str,
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    """لوحة توجيه النماذج — Model routing dashboard."""
    svc = SovereignRoutingService(db)
    return await svc.list_all_configs(tenant_id)


@router.post("/configs", status_code=status.HTTP_201_CREATED)
async def create_routing_config(
    tenant_id: str,
    payload: RoutingConfigCreate,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    config = ModelRoutingConfig(
        tenant_id=tenant_id,
        lane=payload.lane,
        primary_model=payload.primary_model,
        fallback_model=payload.fallback_model,
        provider=payload.provider,
        max_tokens=payload.max_tokens,
        temperature=payload.temperature,
        requires_structured_output=payload.requires_structured_output,
        arabic_quality_check=payload.arabic_quality_check,
        hitl_required=payload.hitl_required,
        approval_class=payload.approval_class,
    )
    db.add(config)
    await db.commit()
    await db.refresh(config)
    return {"id": str(config.id), "lane": config.lane, "primary_model": config.primary_model}


@router.patch("/configs/{config_id}/metrics")
async def update_metrics(
    config_id: str,
    tenant_id: str,
    payload: RoutingMetrics,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """تحديث مقاييس الأداء — Update routing performance metrics."""
    result = await db.execute(
        select(ModelRoutingConfig).where(
            ModelRoutingConfig.id == config_id,
            ModelRoutingConfig.tenant_id == tenant_id,
        )
    )
    config = result.scalar_one_or_none()
    if not config:
        raise HTTPException(status_code=404, detail="Config not found")

    if payload.avg_latency_ms is not None:
        config.avg_latency_ms = payload.avg_latency_ms
    if payload.schema_adherence_pct is not None:
        config.schema_adherence_pct = payload.schema_adherence_pct
    if payload.contradiction_rate_pct is not None:
        config.contradiction_rate_pct = payload.contradiction_rate_pct
    if payload.arabic_quality_score is not None:
        config.arabic_quality_score = payload.arabic_quality_score
    if payload.cost_per_task_sar is not None:
        config.cost_per_task_sar = payload.cost_per_task_sar

    await db.commit()
    return {"id": config_id, "updated": True}


@router.get("/lane-defaults")
async def lane_defaults() -> dict[str, Any]:
    """الإعدادات الافتراضية للمسارات — Default lane configurations."""
    return LANE_DEFAULTS


@router.post("/select-lane")
async def select_lane(
    tenant_id: str,
    decision_type: str,
    arabic_required: bool = False,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """اختيار مسار النموذج — Select model lane for a given decision type."""
    svc = SovereignRoutingService(db)
    lane = await svc.select_lane(decision_type=decision_type, arabic_required=arabic_required)
    config = await svc.get_config_for_lane(tenant_id, lane)
    return {"selected_lane": lane, "config": config}
