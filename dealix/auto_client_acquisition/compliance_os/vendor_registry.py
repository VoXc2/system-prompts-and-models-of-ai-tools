"""
Vendor / Subprocessor registry — PDPL Article on subprocessors.

Every external service that touches data must be registered + assessed.
Required for SDAIA / DPO inspection. Maintains vendor risk tier + DPA status.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


class VendorStatus:
    APPROVED = "approved"
    PENDING_DPA = "pending_dpa"
    PENDING_REVIEW = "pending_review"
    SUSPENDED = "suspended"


@dataclass
class Vendor:
    vendor_id: str
    name: str
    purpose_ar: str
    data_accessed: list[str]                 # types of data
    region: str                              # SA / GCC / US / EU / Global
    has_dpa_signed: bool = False
    iso27001: bool = False
    soc2: bool = False
    risk_tier: str = "medium"                # low / medium / high
    status: str = VendorStatus.PENDING_REVIEW
    contact_email: str | None = None
    onboarded_at: datetime | None = None


# ── Default vendor registry — services Dealix uses ───────────────
DEFAULT_VENDORS: tuple[Vendor, ...] = (
    Vendor(
        vendor_id="anthropic",
        name="Anthropic (Claude)",
        purpose_ar="LLM للتصنيف والتلخيص — لا يستخدم البيانات للتدريب",
        data_accessed=["communication_content_redacted"],
        region="US",
        has_dpa_signed=True,
        iso27001=True,
        soc2=True,
        risk_tier="medium",
        status=VendorStatus.APPROVED,
    ),
    Vendor(
        vendor_id="groq",
        name="Groq",
        purpose_ar="Inference سريع لتصنيف الردود",
        data_accessed=["communication_content_redacted"],
        region="US",
        has_dpa_signed=True,
        iso27001=False,
        soc2=True,
        risk_tier="medium",
        status=VendorStatus.APPROVED,
    ),
    Vendor(
        vendor_id="green_api",
        name="Green API",
        purpose_ar="WhatsApp gateway provider",
        data_accessed=["business_contact_phone"],
        region="Global",
        has_dpa_signed=True,
        iso27001=False,
        soc2=False,
        risk_tier="medium",
        status=VendorStatus.APPROVED,
    ),
    Vendor(
        vendor_id="ultramsg",
        name="Ultramsg",
        purpose_ar="WhatsApp gateway fallback",
        data_accessed=["business_contact_phone"],
        region="Global",
        has_dpa_signed=True,
        iso27001=False,
        soc2=False,
        risk_tier="medium",
        status=VendorStatus.APPROVED,
    ),
    Vendor(
        vendor_id="meta_whatsapp_cloud",
        name="Meta WhatsApp Business Cloud API",
        purpose_ar="Official WhatsApp Business sender",
        data_accessed=["business_contact_phone"],
        region="Global",
        has_dpa_signed=True,
        iso27001=True,
        soc2=True,
        risk_tier="medium",
        status=VendorStatus.APPROVED,
    ),
    Vendor(
        vendor_id="gmail_oauth",
        name="Gmail (Google Workspace OAuth)",
        purpose_ar="إرسال إيميل تجاري via customer's own account",
        data_accessed=["business_contact_email"],
        region="Global",
        has_dpa_signed=True,
        iso27001=True,
        soc2=True,
        risk_tier="low",
        status=VendorStatus.APPROVED,
    ),
    Vendor(
        vendor_id="moyasar",
        name="Moyasar",
        purpose_ar="Saudi payment gateway للـ billing",
        data_accessed=["billing_metadata"],
        region="SA",
        has_dpa_signed=True,
        iso27001=True,
        soc2=False,
        risk_tier="low",
        status=VendorStatus.APPROVED,
    ),
    Vendor(
        vendor_id="apollo",
        name="Apollo.io",
        purpose_ar="Lead enrichment provider",
        data_accessed=["business_contact"],
        region="US",
        has_dpa_signed=True,
        iso27001=True,
        soc2=True,
        risk_tier="medium",
        status=VendorStatus.APPROVED,
    ),
    Vendor(
        vendor_id="zoominfo",
        name="ZoomInfo",
        purpose_ar="Lead enrichment alternative",
        data_accessed=["business_contact"],
        region="US",
        has_dpa_signed=True,
        iso27001=True,
        soc2=True,
        risk_tier="medium",
        status=VendorStatus.APPROVED,
    ),
    Vendor(
        vendor_id="railway",
        name="Railway (hosting)",
        purpose_ar="Application hosting (data hosted in same region as customer)",
        data_accessed=["all"],
        region="Global",
        has_dpa_signed=True,
        iso27001=True,
        soc2=True,
        risk_tier="high",
        status=VendorStatus.APPROVED,
    ),
)


def register_vendor(vendor: Vendor) -> Vendor:
    """Add a custom vendor to the registry — assigns onboarded_at."""
    if not vendor.vendor_id:
        vendor.vendor_id = f"vnd_{uuid.uuid4().hex[:16]}"
    if vendor.onboarded_at is None:
        vendor.onboarded_at = datetime.now(timezone.utc).replace(tzinfo=None)
    return vendor


def vendors_summary(vendors: tuple[Vendor, ...] | None = None) -> dict[str, Any]:
    """Aggregate counts for the Trust Center vendor tile."""
    pool = vendors or DEFAULT_VENDORS
    by_status: dict[str, int] = {}
    by_tier: dict[str, int] = {}
    by_region: dict[str, int] = {}
    n_with_dpa = 0
    for v in pool:
        by_status[v.status] = by_status.get(v.status, 0) + 1
        by_tier[v.risk_tier] = by_tier.get(v.risk_tier, 0) + 1
        by_region[v.region] = by_region.get(v.region, 0) + 1
        if v.has_dpa_signed:
            n_with_dpa += 1
    return {
        "total": len(pool),
        "with_dpa": n_with_dpa,
        "dpa_coverage_pct": round(n_with_dpa / len(pool) * 100, 1) if pool else 0,
        "by_status": by_status,
        "by_risk_tier": by_tier,
        "by_region": by_region,
    }
