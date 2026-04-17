"""Saudi Compliance API — live compliance matrix with real checks."""

from fastapi import APIRouter, Depends
from typing import Any, Dict

router = APIRouter(prefix="/compliance/matrix", tags=["Saudi Compliance"])


async def _get_db():
    from app.database import get_db
    async for session in get_db():
        yield session


@router.get("/")
async def get_compliance_matrix(tenant_id: str = "00000000-0000-0000-0000-000000000000", db=Depends(_get_db)) -> Dict[str, Any]:
    from app.services.saudi_compliance_matrix import saudi_compliance_matrix
    controls = await saudi_compliance_matrix.get_matrix(db, tenant_id=tenant_id)
    return {"controls": controls, "total": len(controls)}


@router.post("/scan")
async def run_compliance_scan(tenant_id: str = "00000000-0000-0000-0000-000000000000", db=Depends(_get_db)) -> Dict[str, Any]:
    from app.services.saudi_compliance_matrix import saudi_compliance_matrix
    controls = await saudi_compliance_matrix.get_matrix(db, tenant_id=tenant_id)
    posture = await saudi_compliance_matrix.get_posture(db, tenant_id=tenant_id)
    return {"status": "scan_complete", "controls_checked": len(controls), "posture": posture}


@router.get("/posture")
async def get_compliance_posture(tenant_id: str = "00000000-0000-0000-0000-000000000000", db=Depends(_get_db)) -> Dict[str, Any]:
    from app.services.saudi_compliance_matrix import saudi_compliance_matrix
    return await saudi_compliance_matrix.get_posture(db, tenant_id=tenant_id)


@router.get("/risk-heatmap")
async def get_risk_heatmap(tenant_id: str = "00000000-0000-0000-0000-000000000000", db=Depends(_get_db)) -> Dict[str, Any]:
    from app.services.saudi_compliance_matrix import saudi_compliance_matrix
    return await saudi_compliance_matrix.get_risk_heatmap(db, tenant_id=tenant_id)


@router.get("/{control_id}")
async def get_control_detail(control_id: str, tenant_id: str = "00000000-0000-0000-0000-000000000000", db=Depends(_get_db)) -> Dict[str, Any]:
    from app.services.saudi_compliance_matrix import saudi_compliance_matrix
    matrix = await saudi_compliance_matrix.get_matrix(db, tenant_id=tenant_id)
    for ctrl in matrix:
        if ctrl["control_id"] == control_id:
            return ctrl
    return {"control_id": control_id, "status": "not_found"}
