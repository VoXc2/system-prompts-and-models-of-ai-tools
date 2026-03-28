"""Public form submission endpoints for lead capture."""
from fastapi import APIRouter, Request
from pydantic import BaseModel
from typing import Optional
from app.services.lead_generation import FormLeadCapture

router = APIRouter()


class DemoFormSubmission(BaseModel):
    name: str
    phone: str
    email: Optional[str] = None
    company: Optional[str] = None
    industry: Optional[str] = None
    team_size: Optional[str] = None
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None


@router.post("/demo")
async def submit_demo_form(req: DemoFormSubmission):
    """Process demo booking form submission (public endpoint)."""
    lead = FormLeadCapture.process_web_form(req.model_dump())
    return {
        "status": "success",
        "message": "شكراً! سنتواصل معك قريباً",
        "lead": lead,
    }


@router.post("/contact")
async def submit_contact_form(req: DemoFormSubmission):
    """Process contact form submission (public endpoint)."""
    lead = FormLeadCapture.process_web_form(req.model_dump())
    lead["source"] = "contact_form"
    return {
        "status": "success",
        "message": "تم استلام رسالتك. سنرد عليك في أقرب وقت",
        "lead": lead,
    }


@router.post("/ctwa")
async def process_ctwa_webhook(request: Request):
    """Process Click-to-WhatsApp ad lead (Meta webhook)."""
    body = await request.json()
    lead = FormLeadCapture.process_ctwa_lead(body)
    return {"status": "success", "lead": lead}
