"""Public form submission endpoints for lead capture."""
import uuid
from fastapi import APIRouter, Request, Depends
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_db
from app.models.lead import Lead
from app.config import get_settings

router = APIRouter()
settings = get_settings()


class DemoFormSubmission(BaseModel):
    name: str
    phone: str
    email: Optional[str] = None
    company: Optional[str] = None
    industry: Optional[str] = None
    team_size: Optional[str] = None
    tenant_id: Optional[str] = None
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None


class ContactFormSubmission(BaseModel):
    name: str
    phone: str
    email: Optional[str] = None
    company: Optional[str] = None
    message: Optional[str] = None
    tenant_id: Optional[str] = None


def _resolve_tenant_id(form_tenant_id: Optional[str]) -> Optional[str]:
    """Resolve tenant_id from form data or fall back to config default."""
    if form_tenant_id:
        return form_tenant_id
    default = settings.DEFAULT_TENANT_ID
    return default if default else None


@router.post("/demo")
async def submit_demo_form(
    req: DemoFormSubmission,
    db: AsyncSession = Depends(get_db),
):
    """Process demo booking form submission (public endpoint)."""
    tenant_id = _resolve_tenant_id(req.tenant_id)

    lead = Lead(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        name=req.name,
        phone=req.phone,
        email=req.email,
        source="demo_form",
        status="new",
        score=0,
        extra_data={
            "company": req.company,
            "industry": req.industry,
            "team_size": req.team_size,
            "utm_source": req.utm_source,
            "utm_medium": req.utm_medium,
            "utm_campaign": req.utm_campaign,
        },
    )
    db.add(lead)
    await db.commit()
    await db.refresh(lead)

    return {
        "status": "success",
        "message": "شكراً! سنتواصل معك قريباً",
        "lead_id": str(lead.id),
    }


@router.post("/contact")
async def submit_contact_form(
    req: ContactFormSubmission,
    db: AsyncSession = Depends(get_db),
):
    """Process contact form submission (public endpoint)."""
    tenant_id = _resolve_tenant_id(req.tenant_id)

    lead = Lead(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        name=req.name,
        phone=req.phone,
        email=req.email,
        source="contact_form",
        status="new",
        score=0,
        notes=req.message,
        extra_data={
            "company": req.company,
        },
    )
    db.add(lead)
    await db.commit()
    await db.refresh(lead)

    return {
        "status": "success",
        "message": "تم استلام رسالتك. سنرد عليك في أقرب وقت",
        "lead_id": str(lead.id),
    }


@router.post("/ctwa")
async def process_ctwa_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Process Click-to-WhatsApp ad lead (Meta webhook)."""
    body = await request.json()

    # Extract lead data from Meta CTWA webhook payload
    entry = body.get("entry", [{}])[0]
    changes = entry.get("changes", [{}])[0]
    value = changes.get("value", {})
    contacts = value.get("contacts", [{}])
    contact = contacts[0] if contacts else {}
    messages = value.get("messages", [{}])
    message = messages[0] if messages else {}

    name = contact.get("profile", {}).get("name", "Unknown")
    phone = contact.get("wa_id", message.get("from", ""))
    tenant_id = _resolve_tenant_id(body.get("tenant_id"))

    lead = Lead(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        name=name,
        phone=phone,
        source="ctwa",
        status="new",
        score=0,
        extra_data={
            "ctwa_payload": body,
            "wa_id": phone,
        },
    )
    db.add(lead)
    await db.commit()
    await db.refresh(lead)

    return {
        "status": "success",
        "lead_id": str(lead.id),
    }
