"""Model Routing API — real LLM metrics from ai_conversations table."""

from fastapi import APIRouter, Depends
from typing import Any, Dict

router = APIRouter(prefix="/model-routing", tags=["Model Routing"])


async def _get_db():
    from app.database import get_db
    async for session in get_db():
        yield session


@router.get("/dashboard")
async def routing_dashboard(tenant_id: str = "00000000-0000-0000-0000-000000000000", db=Depends(_get_db)) -> Dict[str, Any]:
    from app.services.model_routing_dashboard import model_routing_dashboard
    return await model_routing_dashboard.get_routing_stats(db, tenant_id)


@router.get("/health")
async def provider_health() -> Dict[str, Any]:
    from app.services.model_routing_dashboard import model_routing_dashboard
    return {"providers": model_routing_dashboard.get_provider_health()}


@router.get("/costs")
async def routing_costs(tenant_id: str = "00000000-0000-0000-0000-000000000000", db=Depends(_get_db)) -> Dict[str, Any]:
    from app.services.model_routing_dashboard import model_routing_dashboard
    return await model_routing_dashboard.get_cost_summary(db, tenant_id)


@router.get("/recommendations")
async def routing_recommendations() -> Dict[str, Any]:
    return {"recommendations": []}
