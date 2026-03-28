"""PDPL consent management API."""
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user, get_db
from app.models.consent import Consent

router = APIRouter()


# --------------- Schemas ---------------

class ConsentCreate(BaseModel):
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    lead_id: Optional[str] = None
    customer_id: Optional[str] = None
    consent_type: str  # marketing_whatsapp, marketing_email, data_processing, call_recording
    source: str = "manual"  # web_form, whatsapp_optin, manual, api, ctwa_ad
    legal_basis: str = "consent"
    ip_address: Optional[str] = None
    privacy_notice_version: Optional[str] = None


class ConsentResponse(BaseModel):
    id: str
    tenant_id: str
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    consent_type: str
    status: str
    source: Optional[str] = None
    legal_basis: Optional[str] = None
    granted_at: Optional[str] = None
    revoked_at: Optional[str] = None
    created_at: str

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm_model(cls, obj: Consent) -> "ConsentResponse":
        return cls(
            id=str(obj.id),
            tenant_id=str(obj.tenant_id),
            contact_phone=obj.contact_phone,
            contact_email=obj.contact_email,
            consent_type=obj.consent_type or "",
            status=obj.status or "granted",
            source=obj.source,
            legal_basis=obj.legal_basis,
            granted_at=obj.granted_at.isoformat() if obj.granted_at else None,
            revoked_at=obj.revoked_at.isoformat() if obj.revoked_at else None,
            created_at=obj.created_at.isoformat() if obj.created_at else "",
        )


# --------------- Endpoints ---------------

@router.post("/", status_code=201)
async def record_consent(
    req: ConsentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Record a new consent."""
    tenant_id = current_user["tenant_id"]
    now = datetime.now(timezone.utc)

    consent = Consent(
        tenant_id=tenant_id,
        contact_phone=req.contact_phone,
        contact_email=req.contact_email,
        lead_id=req.lead_id if req.lead_id else None,
        customer_id=req.customer_id if req.customer_id else None,
        consent_type=req.consent_type,
        status="granted",
        granted_at=now,
        source=req.source,
        legal_basis=req.legal_basis,
        ip_address=req.ip_address,
        privacy_notice_version=req.privacy_notice_version,
    )
    db.add(consent)
    await db.commit()
    await db.refresh(consent)

    return {
        "status": "recorded",
        "consent": ConsentResponse.from_orm_model(consent),
    }


@router.get("/{contact_id}")
async def get_consent_history(
    contact_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get consent history for a contact (by lead_id, customer_id, phone, or email)."""
    tenant_id = current_user["tenant_id"]

    # Search by multiple identifiers: try UUID first (lead/customer), then phone/email
    stmt = select(Consent).where(Consent.tenant_id == tenant_id)

    try:
        uid = UUID(contact_id)
        stmt = stmt.where(
            (Consent.lead_id == uid) | (Consent.customer_id == uid)
        )
    except ValueError:
        # Not a UUID -- treat as phone or email
        stmt = stmt.where(
            (Consent.contact_phone == contact_id) | (Consent.contact_email == contact_id)
        )

    result = await db.execute(stmt)
    consents = result.scalars().all()

    return {
        "contact_id": contact_id,
        "consents": [ConsentResponse.from_orm_model(c) for c in consents],
    }


@router.post("/{consent_id}/revoke")
async def revoke_consent(
    consent_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Revoke a previously granted consent."""
    tenant_id = current_user["tenant_id"]

    result = await db.execute(
        select(Consent).where(
            Consent.id == UUID(consent_id),
            Consent.tenant_id == tenant_id,
        )
    )
    consent = result.scalar_one_or_none()
    if not consent:
        raise HTTPException(status_code=404, detail="الموافقة غير موجودة")

    consent.status = "revoked"
    consent.revoked_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(consent)

    return {
        "status": "revoked",
        "consent_id": consent_id,
        "consent": ConsentResponse.from_orm_model(consent),
    }
