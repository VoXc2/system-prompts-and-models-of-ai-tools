"""PDPL consent management API."""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class ConsentRecord(BaseModel):
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    consent_type: str  # marketing_whatsapp, marketing_email, data_processing, call_recording
    source: str = "manual"  # web_form, whatsapp_optin, manual, api, ctwa_ad
    legal_basis: str = "consent"


@router.post("/")
async def record_consent(req: ConsentRecord):
    """Record a new consent."""
    return {
        "status": "recorded",
        "consent": {
            "type": req.consent_type,
            "source": req.source,
            "status": "granted",
        },
    }


@router.get("/{contact_id}")
async def get_consent_history(contact_id: str):
    """Get consent history for a contact."""
    return {"contact_id": contact_id, "consents": []}


@router.post("/{consent_id}/revoke")
async def revoke_consent(consent_id: str):
    """Revoke a previously granted consent."""
    return {"status": "revoked", "consent_id": consent_id}
