"""Suppression list API — manage do-not-contact list."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user, get_db
from app.models.suppression import SuppressionEntry
from app.services.consent_service import ConsentService

router = APIRouter()


class SuppressRequest(BaseModel):
    phone: Optional[str] = None
    email: Optional[str] = None
    channel: str = "all"
    reason: str = "manual"
    notes: Optional[str] = None


class CheckContactRequest(BaseModel):
    phone: Optional[str] = None
    email: Optional[str] = None
    channel: str = "whatsapp"


class ConsentRequest(BaseModel):
    phone: Optional[str] = None
    email: Optional[str] = None
    consent_type: str  # marketing_whatsapp, marketing_email, marketing_sms
    source: str = "api"
    legal_basis: str = "consent"


@router.get("/")
async def list_suppressed(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    limit: int = 100,
    offset: int = 0,
):
    """List all suppressed contacts."""
    result = await db.execute(
        select(SuppressionEntry)
        .where(SuppressionEntry.tenant_id == current_user["tenant_id"])
        .order_by(SuppressionEntry.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    entries = result.scalars().all()
    return {
        "suppressed": [
            {
                "id": str(e.id),
                "phone": e.contact_phone,
                "email": e.contact_email,
                "channel": e.channel,
                "reason": e.reason,
                "notes": e.notes,
                "suppressed_at": e.suppressed_at.isoformat() if e.suppressed_at else None,
            }
            for e in entries
        ],
        "total": len(entries),
    }


@router.post("/")
async def suppress_contact(
    req: SuppressRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Add a contact to the suppression list."""
    if not req.phone and not req.email:
        raise HTTPException(status_code=400, detail="يجب تحديد رقم الهاتف أو البريد الإلكتروني")

    svc = ConsentService(db, current_user["tenant_id"])
    entry = await svc.suppress_contact(
        channel=req.channel,
        reason=req.reason,
        phone=req.phone,
        email=req.email,
        suppressed_by=current_user["user_id"],
        notes=req.notes,
    )
    return {"status": "suppressed", "id": str(entry.id)}


@router.post("/check")
async def check_contact_eligibility(
    req: CheckContactRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Check if a contact can be reached on a given channel."""
    svc = ConsentService(db, current_user["tenant_id"])
    result = await svc.can_contact(channel=req.channel, phone=req.phone, email=req.email)
    return result


@router.post("/consent")
async def record_consent(
    req: ConsentRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Record consent from a contact."""
    svc = ConsentService(db, current_user["tenant_id"])
    consent = await svc.record_consent(
        consent_type=req.consent_type,
        phone=req.phone,
        email=req.email,
        source=req.source,
        legal_basis=req.legal_basis,
    )
    return {"status": "recorded", "id": str(consent.id)}


@router.post("/revoke")
async def revoke_consent(
    req: ConsentRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Revoke consent and auto-suppress contact."""
    svc = ConsentService(db, current_user["tenant_id"])
    count = await svc.revoke_consent(
        consent_type=req.consent_type,
        phone=req.phone,
        email=req.email,
    )
    return {"status": "revoked", "consents_revoked": count}
