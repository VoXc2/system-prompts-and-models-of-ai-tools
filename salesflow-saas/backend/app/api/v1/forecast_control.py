"""Forecast Control API — real actual vs forecast from deals + strategic deals."""

from fastapi import APIRouter, Depends
from typing import Any, Dict

router = APIRouter(prefix="/forecast-control", tags=["Forecast Control"])


async def _get_db():
    from app.database import get_db
    async for session in get_db():
        yield session


@router.get("/unified")
async def unified_view(tenant_id: str = "00000000-0000-0000-0000-000000000000", db=Depends(_get_db)) -> Dict[str, Any]:
    from app.services.forecast_control_center import forecast_control_center
    return await forecast_control_center.get_unified_view(db, tenant_id)


@router.get("/variance")
async def variance_analysis(tenant_id: str = "00000000-0000-0000-0000-000000000000", db=Depends(_get_db)) -> Dict[str, Any]:
    from app.services.forecast_control_center import forecast_control_center
    return await forecast_control_center.get_variance_analysis(db, tenant_id)


@router.post("/recalibrate")
async def recalibrate_forecast() -> Dict[str, Any]:
    return {"status": "recalibration_triggered"}


@router.get("/accuracy")
async def forecast_accuracy(tenant_id: str = "00000000-0000-0000-0000-000000000000", db=Depends(_get_db)) -> Dict[str, Any]:
    from app.services.forecast_control_center import forecast_control_center
    return await forecast_control_center.get_accuracy_trend(db, tenant_id)


@router.get("/trends")
async def accuracy_trends(tenant_id: str = "00000000-0000-0000-0000-000000000000", periods: int = 6, db=Depends(_get_db)) -> Dict[str, Any]:
    from app.services.forecast_control_center import forecast_control_center
    return await forecast_control_center.get_accuracy_trend(db, tenant_id, periods)
