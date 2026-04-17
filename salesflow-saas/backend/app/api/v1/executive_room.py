"""Executive Room API — unified executive decision surface with real data."""

from fastapi import APIRouter, Depends
from typing import Any, Dict

router = APIRouter(prefix="/executive-room", tags=["Executive Room"])


async def _get_db():
    from app.database import get_db
    async for session in get_db():
        yield session


@router.get("/snapshot")
async def executive_snapshot(
    tenant_id: str = "00000000-0000-0000-0000-000000000000",
    db=Depends(_get_db),
) -> Dict[str, Any]:
    from app.services.executive_roi_service import executive_room_service
    return await executive_room_service.build_snapshot(db, tenant_id)


@router.get("/risks")
async def executive_risks(
    tenant_id: str = "00000000-0000-0000-0000-000000000000",
    db=Depends(_get_db),
) -> Dict[str, Any]:
    from app.services.executive_roi_service import executive_room_service
    snapshot = await executive_room_service.build_snapshot(db, tenant_id)
    risks = []
    if snapshot["approvals"]["breach"] > 0:
        risks.append({"type": "sla_breach", "severity": "high", "count": snapshot["approvals"]["breach"], "description_ar": "خرق SLA في الموافقات"})
    if snapshot["contradictions"]["critical"] > 0:
        risks.append({"type": "contradiction", "severity": "critical", "count": snapshot["contradictions"]["critical"], "description_ar": "تناقضات حرجة نشطة"})
    if snapshot["compliance"]["non_compliant"] > 0:
        risks.append({"type": "compliance", "severity": "high", "count": snapshot["compliance"]["non_compliant"], "description_ar": "ضوابط غير ممتثلة"})
    if snapshot["connectors"]["error"] > 0:
        risks.append({"type": "connector_error", "severity": "medium", "count": snapshot["connectors"]["error"], "description_ar": "موصلات معطلة"})
    return {"risks": risks, "total": len(risks)}


@router.get("/decisions-pending")
async def pending_decisions(
    tenant_id: str = "00000000-0000-0000-0000-000000000000",
    db=Depends(_get_db),
) -> Dict[str, Any]:
    from app.services.executive_roi_service import executive_room_service
    snapshot = await executive_room_service.build_snapshot(db, tenant_id)
    decisions = []
    if snapshot["approvals"]["pending"] > 0:
        decisions.append({"type": "approval", "count": snapshot["approvals"]["pending"], "description_ar": "موافقات معلقة"})
    if snapshot["contradictions"]["active"] > 0:
        decisions.append({"type": "contradiction", "count": snapshot["contradictions"]["active"], "description_ar": "تناقضات تحتاج مراجعة"})
    return {"decisions": decisions, "total": len(decisions)}


@router.get("/forecast-vs-actual")
async def forecast_vs_actual(
    tenant_id: str = "00000000-0000-0000-0000-000000000000",
    db=Depends(_get_db),
) -> Dict[str, Any]:
    from app.services.executive_roi_service import executive_room_service
    snapshot = await executive_room_service.build_snapshot(db, tenant_id)
    rev = snapshot["revenue"]
    return {
        "tracks": {"revenue": {"actual": rev["actual"], "forecast": rev["forecast"], "variance_percent": rev["variance_percent"]}, "strategic_deals": snapshot["strategic_deals"]},
        "overall_health": "on_track" if rev["variance_percent"] >= -10 else "at_risk",
    }


@router.get("/weekly-pack")
async def weekly_pack(
    tenant_id: str = "00000000-0000-0000-0000-000000000000",
    db=Depends(_get_db),
) -> Dict[str, Any]:
    """ExecWeeklyPack — canonical contract for executive surfaces.
    This is the SINGLE source of truth for Executive Room rendering.
    """
    from app.services.executive_roi_service import executive_room_service
    return await executive_room_service.build_weekly_pack(db, tenant_id)
