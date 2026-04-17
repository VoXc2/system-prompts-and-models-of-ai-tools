"""Evidence Pack API — assemble and manage evidence packs with real DB."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel as PydanticBase
from typing import Any, Dict, List, Optional

router = APIRouter(prefix="/evidence-packs", tags=["Evidence Packs"])


class EvidencePackAssemble(PydanticBase):
    title: str
    title_ar: Optional[str] = None
    pack_type: str
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    contents: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None


async def _get_db():
    from app.database import get_db
    async for session in get_db():
        yield session


@router.post("/assemble")
async def assemble_evidence_pack(body: EvidencePackAssemble, tenant_id: str = "00000000-0000-0000-0000-000000000000", db=Depends(_get_db)) -> Dict[str, Any]:
    from app.services.evidence_pack_service import evidence_pack_service
    pack = await evidence_pack_service.assemble(db, tenant_id=tenant_id, title=body.title, title_ar=body.title_ar, pack_type=body.pack_type, entity_type=body.entity_type, entity_id=body.entity_id, contents=body.contents, metadata=body.metadata)
    return {"id": str(pack.id), "status": "assembled", "hash_signature": pack.hash_signature}


@router.get("/")
async def list_evidence_packs(tenant_id: str = "00000000-0000-0000-0000-000000000000", pack_type: Optional[str] = None, db=Depends(_get_db)) -> Dict[str, Any]:
    from app.services.evidence_pack_service import evidence_pack_service
    packs = await evidence_pack_service.list_packs(db, tenant_id=tenant_id, pack_type=pack_type)
    items = [{"id": str(p.id), "title": p.title, "title_ar": p.title_ar, "pack_type": p.pack_type.value if p.pack_type else None, "status": p.status.value if p.status else None, "hash_signature": p.hash_signature, "created_at": p.created_at.isoformat() if p.created_at else None} for p in packs]
    return {"packs": items, "total": len(items)}


@router.get("/{pack_id}")
async def get_evidence_pack(pack_id: str, tenant_id: str = "00000000-0000-0000-0000-000000000000", db=Depends(_get_db)) -> Dict[str, Any]:
    from app.services.evidence_pack_service import evidence_pack_service
    p = await evidence_pack_service.get_by_id(db, tenant_id=tenant_id, pack_id=pack_id)
    if not p:
        return {"id": pack_id, "status": "not_found"}
    return {"id": str(p.id), "title": p.title, "title_ar": p.title_ar, "pack_type": p.pack_type.value if p.pack_type else None, "status": p.status.value if p.status else None, "contents": p.contents, "hash_signature": p.hash_signature}


@router.put("/{pack_id}/review")
async def review_evidence_pack(pack_id: str, tenant_id: str = "00000000-0000-0000-0000-000000000000", reviewer_id: str = "00000000-0000-0000-0000-000000000000", db=Depends(_get_db)) -> Dict[str, Any]:
    from app.services.evidence_pack_service import evidence_pack_service
    p = await evidence_pack_service.review(db, tenant_id=tenant_id, pack_id=pack_id, reviewed_by_id=reviewer_id)
    if not p:
        return {"id": pack_id, "status": "not_found"}
    return {"id": str(p.id), "status": "reviewed"}


@router.get("/{pack_id}/verify")
async def verify_evidence_pack(pack_id: str, tenant_id: str = "00000000-0000-0000-0000-000000000000", db=Depends(_get_db)) -> Dict[str, Any]:
    from app.services.evidence_pack_service import evidence_pack_service
    return await evidence_pack_service.verify_integrity(db, tenant_id=tenant_id, pack_id=pack_id)
