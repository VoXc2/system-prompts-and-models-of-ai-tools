"""
Public endpoints — no auth, CORS-open. Used by the landing page.

Routes:
  POST /api/v1/public/demo-request   — landing form submission
    Body: {name, company, email, phone, sector?, size?, message?, consent, website(honeypot)}
    Returns: {ok: true, calendly_url: "...", lead_id?: "..."}
"""

from __future__ import annotations

import logging
import os
from typing import Any

from fastapi import APIRouter, HTTPException, Request

from dealix.analytics import FUNNEL_EVENTS, capture_event

log = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/public", tags=["public"])


CALENDLY_URL = os.getenv(
    "CALENDLY_URL",
    "https://calendly.com/sami-assiri11/dealix-demo",
)


@router.post("/demo-request")
async def demo_request(req: Request) -> dict[str, Any]:
    """Public landing form — captures demo request and returns Calendly booking URL."""
    try:
        body = await req.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail="invalid_json") from e

    # Honeypot: if "website" field is filled, silently drop
    if body.get("website"):
        log.info("demo_request_honeypot_triggered")
        return {"ok": True, "calendly_url": CALENDLY_URL}

    name = str(body.get("name") or "").strip()
    company = str(body.get("company") or "").strip()
    email = str(body.get("email") or "").strip()
    phone = str(body.get("phone") or "").strip()
    sector = str(body.get("sector") or "").strip()
    size = str(body.get("size") or "").strip()
    message = str(body.get("message") or "").strip()
    consent = bool(body.get("consent"))

    if not name or not company or "@" not in email or not phone:
        raise HTTPException(status_code=422, detail="missing_required_fields")
    if not consent:
        raise HTTPException(status_code=422, detail="consent_required")

    # Fire PostHog event (fire-and-forget — never blocks response)
    try:
        await capture_event(
            (
                FUNNEL_EVENTS.DEMO_REQUESTED
                if hasattr(FUNNEL_EVENTS, "DEMO_REQUESTED")
                else "demo_requested"
            ),
            distinct_id=email,
            properties={
                "name": name,
                "company": company,
                "email": email,
                "phone": phone,
                "sector": sector,
                "size": size,
                "message_len": len(message),
                "source": "landing.demo_form",
            },
        )
    except Exception:
        log.exception("posthog_capture_failed")

    # TODO: once AcquisitionPipeline is DI-wired here, route through pipeline.run()
    # For now, minimal path: accept + return Calendly URL. Lead is still in PostHog.
    log.info(
        "demo_request_accepted email=%s company=%s sector=%s",
        email,
        company,
        sector,
    )

    return {
        "ok": True,
        "calendly_url": CALENDLY_URL,
        "message": "تم استلام طلبك — سنتواصل خلال 4 ساعات عمل",
    }


@router.get("/health")
async def public_health() -> dict[str, Any]:
    """Unauthenticated health probe for landing page to show live status."""
    return {"ok": True, "service": "dealix-api"}


@router.post("/partner-application")
async def partner_application(req: Request) -> dict[str, Any]:
    """Public partner signup — for agencies/freelancers/consultants."""
    try:
        body = await req.json()
    except Exception:
        # Also accept form-urlencoded submissions from Formspree-style forms
        form = await req.form()
        body = dict(form)

    name = str(body.get("name") or "").strip()
    company = str(body.get("company") or "").strip()
    email = str(body.get("email") or "").strip()
    phone = str(body.get("phone") or "").strip()
    ptype = str(body.get("partnership_type") or body.get("type") or "referral").strip()
    services = str(body.get("services") or "").strip()
    active_clients = str(body.get("active_clients") or body.get("clients") or "0")
    why = str(body.get("why") or "").strip()

    if not name or not company or "@" not in email:
        raise HTTPException(status_code=422, detail="missing_required_fields")

    log.info(
        "partner_application_received company=%s type=%s clients=%s",
        company,
        ptype,
        active_clients,
    )

    try:
        await capture_event(
            "partner_application_submitted",
            distinct_id=email or company or "anonymous",
            properties={
                "company": company,
                "partnership_type": ptype,
                "active_clients": active_clients,
                "has_phone": bool(phone),
                "has_services": bool(services),
                "has_why": bool(why),
                "source": "dealix.partners_page",
            },
        )
    except Exception:
        log.warning("posthog_capture_failed", exc_info=True)

    return {
        "ok": True,
        "message": "وصلنا طلبك. سنتواصل خلال 48 ساعة.",
        "next_step": "email_review",
    }
