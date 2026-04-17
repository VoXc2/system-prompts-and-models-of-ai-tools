"""Golden Path API — Partner intake → evidence pack end-to-end.

This is the canonical Tier-1 verification path. It proves:
- Structured outputs (PartnerDossier, EconomicsModel, ApprovalPacket)
- Trust enforcement (Class B approval with SLA)
- Evidence assembly (SHA256 tamper-evident)
- Correlation (trace_id links all steps)
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel as PydanticBase
from typing import Any, Dict, Optional

router = APIRouter(prefix="/golden-path", tags=["Golden Path"])


class GoldenPathRequest(PydanticBase):
    partner_name: str
    partner_name_ar: Optional[str] = None
    partner_type: str = "partnership"
    revenue_potential_sar: float = 100000
    cost_sar: float = 20000
    requested_by: str = "00000000-0000-0000-0000-000000000000"


async def _get_db():
    from app.database import get_db
    async for session in get_db():
        yield session


@router.post("/run")
async def run_golden_path(
    body: GoldenPathRequest,
    tenant_id: str = "00000000-0000-0000-0000-000000000000",
    db=Depends(_get_db),
) -> Dict[str, Any]:
    """Run the complete partner golden path end-to-end.

    Creates: PartnerDossier → EconomicsModel → ApprovalPacket → EvidencePack
    All with trace_id correlation and structured Provenance.
    """
    from app.services.golden_path import golden_path_service
    return await golden_path_service.run_full_path(
        db,
        tenant_id=tenant_id,
        partner_name=body.partner_name,
        partner_name_ar=body.partner_name_ar,
        partner_type=body.partner_type,
        revenue_potential_sar=body.revenue_potential_sar,
        cost_sar=body.cost_sar,
        requested_by=body.requested_by,
    )


@router.post("/dossier")
async def create_dossier(
    body: GoldenPathRequest,
    tenant_id: str = "00000000-0000-0000-0000-000000000000",
    db=Depends(_get_db),
) -> Dict[str, Any]:
    """Step 1: Create partner dossier with PartnerDossier schema."""
    from app.services.golden_path import golden_path_service
    return await golden_path_service.create_partner_dossier(
        db, tenant_id=tenant_id, partner_name=body.partner_name,
        partner_name_ar=body.partner_name_ar, partner_type=body.partner_type,
        revenue_potential_sar=body.revenue_potential_sar,
    )
