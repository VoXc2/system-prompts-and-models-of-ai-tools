"""Saudi Sensitive Workflow API — partner data sharing with PDPL controls."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel as PydanticBase
from typing import Any, Dict, List

router = APIRouter(prefix="/saudi-workflow", tags=["Saudi Sensitive Workflow"])


class DataSharingRequest(PydanticBase):
    partner_name: str
    data_categories: List[str] = ["company_name", "contact_name", "contact_email"]
    purpose: str = "partnership_evaluation"
    requested_by: str = "00000000-0000-0000-0000-000000000000"


async def _get_db():
    from app.database import get_db
    async for session in get_db():
        yield session


@router.post("/share-partner-data")
async def share_partner_data(
    body: DataSharingRequest,
    tenant_id: str = "00000000-0000-0000-0000-000000000000",
    db=Depends(_get_db),
) -> Dict[str, Any]:
    """Execute Saudi-sensitive partner data sharing workflow.

    Enforces: PDPL classification → consent check → export rules →
    Class B+ approval → audit trail → evidence pack assembly.
    """
    from app.services.saudi_sensitive_workflow import saudi_sensitive_workflow
    return await saudi_sensitive_workflow.share_partner_data(
        db, tenant_id=tenant_id, partner_name=body.partner_name,
        data_categories=body.data_categories, purpose=body.purpose,
        requested_by=body.requested_by,
    )
