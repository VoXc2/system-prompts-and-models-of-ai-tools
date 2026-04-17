"""Contradiction Engine API — detect and manage contradictions with real DB."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel as PydanticBase
from typing import Any, Dict, Optional

router = APIRouter(prefix="/contradictions", tags=["Contradictions"])


class ContradictionCreate(PydanticBase):
    source_a: str
    source_b: str
    claim_a: str
    claim_b: str
    contradiction_type: str = "factual"
    severity: str = "medium"
    detected_by: str = "manual"
    evidence: Optional[Dict[str, Any]] = None


class ContradictionResolve(PydanticBase):
    resolution: str
    resolved_by_id: str = "00000000-0000-0000-0000-000000000000"
    status: str = "resolved"


async def _get_db():
    from app.database import get_db
    async for session in get_db():
        yield session


@router.post("/")
async def register_contradiction(body: ContradictionCreate, tenant_id: str = "00000000-0000-0000-0000-000000000000", db=Depends(_get_db)) -> Dict[str, Any]:
    from app.services.contradiction_engine import contradiction_engine
    c = await contradiction_engine.register(db, tenant_id=tenant_id, source_a=body.source_a, source_b=body.source_b, claim_a=body.claim_a, claim_b=body.claim_b, contradiction_type=body.contradiction_type, severity=body.severity, detected_by=body.detected_by, evidence=body.evidence)
    return {"id": str(c.id), "status": "registered", "severity": body.severity}


@router.get("/")
async def list_contradictions(tenant_id: str = "00000000-0000-0000-0000-000000000000", db=Depends(_get_db)) -> Dict[str, Any]:
    from app.services.contradiction_engine import contradiction_engine
    active = await contradiction_engine.get_active(db, tenant_id=tenant_id)
    items = [{"id": str(c.id), "source_a": c.source_a, "source_b": c.source_b, "claim_a": c.claim_a, "claim_b": c.claim_b, "contradiction_type": c.contradiction_type.value if c.contradiction_type else None, "severity": c.severity.value if c.severity else None, "status": c.status.value if c.status else None, "detected_by": c.detected_by, "created_at": c.created_at.isoformat() if c.created_at else None} for c in active]
    return {"contradictions": items, "total": len(items)}


@router.get("/stats")
async def contradiction_stats(tenant_id: str = "00000000-0000-0000-0000-000000000000", db=Depends(_get_db)) -> Dict[str, Any]:
    from app.services.contradiction_engine import contradiction_engine
    return await contradiction_engine.get_stats(db, tenant_id=tenant_id)


@router.get("/{contradiction_id}")
async def get_contradiction(contradiction_id: str, tenant_id: str = "00000000-0000-0000-0000-000000000000", db=Depends(_get_db)) -> Dict[str, Any]:
    from app.services.contradiction_engine import contradiction_engine
    c = await contradiction_engine.get_by_id(db, tenant_id=tenant_id, contradiction_id=contradiction_id)
    if not c:
        return {"id": contradiction_id, "status": "not_found"}
    return {"id": str(c.id), "source_a": c.source_a, "source_b": c.source_b, "status": c.status.value if c.status else None, "resolution": c.resolution}


@router.put("/{contradiction_id}/resolve")
async def resolve_contradiction(contradiction_id: str, body: ContradictionResolve, tenant_id: str = "00000000-0000-0000-0000-000000000000", db=Depends(_get_db)) -> Dict[str, Any]:
    from app.services.contradiction_engine import contradiction_engine
    c = await contradiction_engine.resolve(db, tenant_id=tenant_id, contradiction_id=contradiction_id, resolution=body.resolution, resolved_by_id=body.resolved_by_id, status=body.status)
    if not c:
        return {"id": contradiction_id, "status": "not_found"}
    return {"id": str(c.id), "status": c.status.value, "resolution": c.resolution}
