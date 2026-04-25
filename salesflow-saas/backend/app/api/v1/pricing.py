"""Pricing & Checkout — plans catalog + Moyasar invoice creation.

P0 for launch: exposes pricing plans and creates payment links
so the first real transaction can happen.
"""

from __future__ import annotations

import hashlib
import hmac
import logging
import time
from typing import Any, Dict, List, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Header, Request
from pydantic import BaseModel

logger = logging.getLogger("dealix.pricing")

router = APIRouter(prefix="/pricing", tags=["Pricing & Checkout"])

PLANS: List[Dict[str, Any]] = [
    {
        "id": "pilot",
        "name_en": "7-Day Pilot",
        "name_ar": "تجربة 7 أيام",
        "price_sar": 499,
        "billing": "one-time",
        "features_en": [
            "7-day full access",
            "AI lead response (45 sec)",
            "Lead qualification",
            "Demo booking automation",
            "Full money-back guarantee",
        ],
        "features_ar": [
            "وصول كامل 7 أيام",
            "رد ذكي على العملاء (45 ثانية)",
            "تأهيل العملاء المحتملين",
            "حجز مواعيد تلقائي",
            "ضمان استرداد كامل",
        ],
    },
    {
        "id": "starter",
        "name_en": "Starter",
        "name_ar": "المبتدئ",
        "price_sar": 990,
        "billing": "monthly",
        "features_en": [
            "Up to 500 leads/month",
            "AI lead scoring",
            "WhatsApp outreach (100 msgs/day)",
            "Basic CRM sync",
            "Email support",
        ],
        "features_ar": [
            "حتى 500 عميل محتمل/شهر",
            "تقييم العملاء بالذكاء الاصطناعي",
            "تواصل واتساب (100 رسالة/يوم)",
            "ربط CRM أساسي",
            "دعم بالبريد الإلكتروني",
        ],
    },
    {
        "id": "growth",
        "name_en": "Growth",
        "name_ar": "النمو",
        "price_sar": 2490,
        "billing": "monthly",
        "features_en": [
            "Up to 2,000 leads/month",
            "AI lead scoring + enrichment",
            "WhatsApp + Email outreach (500 msgs/day)",
            "Full CRM two-way sync",
            "Calendly booking integration",
            "Approval workflows",
            "Priority support",
        ],
        "features_ar": [
            "حتى 2,000 عميل محتمل/شهر",
            "تقييم + إثراء العملاء بالذكاء الاصطناعي",
            "تواصل واتساب + بريد (500 رسالة/يوم)",
            "ربط CRM ثنائي الاتجاه",
            "ربط حجز المواعيد",
            "سير عمل الموافقات",
            "دعم أولوية",
        ],
    },
    {
        "id": "enterprise",
        "name_en": "Enterprise",
        "name_ar": "المؤسسات",
        "price_sar": 0,
        "billing": "custom",
        "features_en": [
            "Unlimited leads",
            "Full AI agent suite",
            "Dedicated success manager",
            "Custom integrations",
            "SLA guarantees",
            "On-premise option",
        ],
        "features_ar": [
            "عملاء محتملون بلا حدود",
            "مجموعة وكلاء ذكاء اصطناعي كاملة",
            "مدير نجاح مخصص",
            "تكاملات مخصصة",
            "ضمانات مستوى الخدمة",
            "خيار التثبيت المحلي",
        ],
    },
]


@router.get("/plans")
async def list_plans() -> Dict[str, Any]:
    return {"plans": PLANS, "currency": "SAR"}


@router.get("/plans/{plan_id}")
async def get_plan(plan_id: str) -> Dict[str, Any]:
    for plan in PLANS:
        if plan["id"] == plan_id:
            return {"plan": plan, "currency": "SAR"}
    raise HTTPException(status_code=404, detail=f"Plan {plan_id} not found")


class CheckoutRequest(BaseModel):
    plan_id: str
    customer_name: str
    customer_email: str
    customer_phone: str = ""
    tenant_id: str = ""
    locale: str = "ar"


@router.post("/checkout")
async def create_checkout(req: CheckoutRequest) -> Dict[str, Any]:
    plan = next((p for p in PLANS if p["id"] == req.plan_id), None)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    if plan["price_sar"] == 0:
        return {
            "status": "contact_sales",
            "message_ar": "تواصل معنا للحصول على عرض مخصص",
            "message_en": "Contact us for a custom quote",
        }

    from app.config import get_settings
    settings = get_settings()
    moyasar_key = getattr(settings, "MOYASAR_SECRET_KEY", "")

    if not moyasar_key:
        return {
            "status": "checkout_unavailable",
            "message": "Payment gateway not configured. Contact support.",
        }

    try:
        import httpx
        invoice_payload = {
            "amount": plan["price_sar"] * 100,
            "currency": "SAR",
            "description": f"Dealix {plan['name_en']} - Monthly",
            "metadata": {
                "plan_id": plan["id"],
                "tenant_id": req.tenant_id,
                "customer_email": req.customer_email,
            },
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                "https://api.moyasar.com/v1/invoices",
                json=invoice_payload,
                auth=(moyasar_key, ""),
            )

        if resp.status_code in (200, 201):
            data = resp.json()
            return {
                "status": "invoice_created",
                "invoice_id": data.get("id"),
                "payment_url": data.get("url"),
                "amount_sar": plan["price_sar"],
                "plan": plan["id"],
            }
        logger.error("Moyasar error: %d %s", resp.status_code, resp.text[:500])
        raise HTTPException(status_code=502, detail="Payment gateway error")
    except httpx.HTTPError as exc:
        logger.error("Moyasar connection error: %s", exc)
        raise HTTPException(status_code=502, detail="Payment gateway unreachable")


@router.post("/webhooks/moyasar")
async def moyasar_payment_webhook(
    request: Request,
    x_moyasar_signature: Optional[str] = Header(None, alias="X-Moyasar-Signature"),
) -> Dict[str, Any]:
    body = await request.body()
    payload = await request.json()

    from app.config import get_settings
    settings = get_settings()
    webhook_secret = getattr(settings, "MOYASAR_WEBHOOK_SECRET", "")

    if webhook_secret and x_moyasar_signature:
        expected = hmac.new(
            webhook_secret.encode(), body, hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(expected, x_moyasar_signature):
            logger.warning("Moyasar webhook signature mismatch")
            raise HTTPException(status_code=401, detail="Invalid signature")

    event_type = payload.get("type", "")
    data = payload.get("data", {})

    from app.services.posthog_client import get_posthog, FunnelEvent
    posthog = get_posthog()

    if event_type == "payment_paid":
        metadata = data.get("metadata", {})
        await posthog.capture(
            distinct_id=metadata.get("customer_email", "unknown"),
            event=FunnelEvent.PAYMENT_SUCCEEDED,
            properties={
                "plan_id": metadata.get("plan_id"),
                "amount_sar": data.get("amount", 0) / 100,
                "invoice_id": data.get("invoice_id"),
            },
        )
        logger.info("Payment succeeded: invoice=%s", data.get("invoice_id"))
        return {"status": "processed", "event": event_type}

    if event_type == "payment_failed":
        metadata = data.get("metadata", {})
        await posthog.capture(
            distinct_id=metadata.get("customer_email", "unknown"),
            event=FunnelEvent.PAYMENT_FAILED,
            properties={"plan_id": metadata.get("plan_id")},
        )
        logger.warning("Payment failed: invoice=%s", data.get("invoice_id"))
        return {"status": "processed", "event": event_type}

    return {"status": "ignored", "event": event_type}
