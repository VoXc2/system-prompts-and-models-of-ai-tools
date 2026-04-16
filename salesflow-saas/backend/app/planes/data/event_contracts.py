"""Data Plane — CloudEvents contracts and AsyncAPI schema registry."""
from __future__ import annotations
import uuid
from datetime import datetime, timezone
from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class CloudEvent(BaseModel):
    """CNCF CloudEvents v1.0 compliant event envelope."""
    model_config = ConfigDict(from_attributes=True)
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source: str  # e.g. "dealix/sales-os", "dealix/partnership-os"
    type: str  # e.g. "com.dealix.lead.captured", "com.dealix.deal.closed"
    specversion: str = "1.0"
    time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    datacontenttype: str = "application/json"
    subject: str | None = None
    data: dict[str, Any] = Field(default_factory=dict)
    
    # Dealix extensions
    tenantid: str = ""
    correlationid: str = Field(default_factory=lambda: str(uuid.uuid4()))
    traceid: str = Field(default_factory=lambda: str(uuid.uuid4()))
    approvalclass: str = "R0_AUTO"
    sensitivity: str = "INTERNAL"
    osmodule: str = ""


EVENT_CATALOG: dict[str, dict[str, str]] = {
    # Sales OS
    "com.dealix.lead.captured": {"module": "sales", "description": "New lead captured from any channel", "description_ar": "تم التقاط عميل محتمل جديد"},
    "com.dealix.lead.enriched": {"module": "sales", "description": "Lead data enriched", "description_ar": "تم إثراء بيانات العميل المحتمل"},
    "com.dealix.lead.scored": {"module": "sales", "description": "Lead scored by AI", "description_ar": "تم تقييم العميل المحتمل"},
    "com.dealix.lead.qualified": {"module": "sales", "description": "Lead qualified", "description_ar": "تم تأهيل العميل المحتمل"},
    "com.dealix.lead.routed": {"module": "sales", "description": "Lead routed to rep", "description_ar": "تم توجيه العميل المحتمل"},
    "com.dealix.outreach.sent": {"module": "sales", "description": "Outreach message sent", "description_ar": "تم إرسال رسالة التواصل"},
    "com.dealix.meeting.scheduled": {"module": "sales", "description": "Meeting scheduled", "description_ar": "تم جدولة الاجتماع"},
    "com.dealix.proposal.generated": {"module": "sales", "description": "Proposal generated", "description_ar": "تم إنشاء العرض"},
    "com.dealix.deal.closed_won": {"module": "sales", "description": "Deal closed won", "description_ar": "تم إغلاق الصفقة بنجاح"},
    "com.dealix.deal.closed_lost": {"module": "sales", "description": "Deal closed lost", "description_ar": "تم فقدان الصفقة"},
    "com.dealix.signature.requested": {"module": "sales", "description": "E-signature requested", "description_ar": "تم طلب التوقيع الإلكتروني"},
    "com.dealix.onboarding.started": {"module": "sales", "description": "Customer onboarding started", "description_ar": "بدأ تهيئة العميل"},
    
    # Partnership OS
    "com.dealix.partner.scouted": {"module": "partnership", "description": "Partner scouted", "description_ar": "تم اكتشاف شريك"},
    "com.dealix.partner.scored": {"module": "partnership", "description": "Partner fit scored", "description_ar": "تم تقييم توافق الشريك"},
    "com.dealix.partner.termsheet_drafted": {"module": "partnership", "description": "Term sheet drafted", "description_ar": "تم صياغة ورقة الشروط"},
    "com.dealix.partner.activated": {"module": "partnership", "description": "Partnership activated", "description_ar": "تم تفعيل الشراكة"},
    "com.dealix.partner.health_reviewed": {"module": "partnership", "description": "Partner health reviewed", "description_ar": "تمت مراجعة صحة الشراكة"},
    
    # M&A OS
    "com.dealix.ma.target_sourced": {"module": "ma", "description": "M&A target sourced", "description_ar": "تم اكتشاف هدف استحواذ"},
    "com.dealix.ma.dd_started": {"module": "ma", "description": "Due diligence started", "description_ar": "بدأت العناية الواجبة"},
    "com.dealix.ma.valuation_completed": {"module": "ma", "description": "Valuation completed", "description_ar": "تم التقييم"},
    "com.dealix.ma.offer_sent": {"module": "ma", "description": "Acquisition offer sent", "description_ar": "تم إرسال عرض الاستحواذ"},
    "com.dealix.ma.deal_closed": {"module": "ma", "description": "M&A deal closed", "description_ar": "تم إغلاق صفقة الاستحواذ"},
    
    # Expansion OS
    "com.dealix.expansion.market_scanned": {"module": "expansion", "description": "Market scanned", "description_ar": "تم مسح السوق"},
    "com.dealix.expansion.launch_approved": {"module": "expansion", "description": "Market launch approved", "description_ar": "تم اعتماد إطلاق السوق"},
    "com.dealix.expansion.canary_launched": {"module": "expansion", "description": "Canary launch started", "description_ar": "بدأ الإطلاق التجريبي"},
    
    # PMI OS
    "com.dealix.pmi.day1_ready": {"module": "pmi", "description": "Day-1 readiness confirmed", "description_ar": "تم تأكيد جاهزية اليوم الأول"},
    "com.dealix.pmi.synergy_realized": {"module": "pmi", "description": "Synergy milestone realized", "description_ar": "تم تحقيق إنجاز التآزر"},
    "com.dealix.pmi.escalation_raised": {"module": "pmi", "description": "Escalation raised", "description_ar": "تم رفع تصعيد"},
    
    # Governance
    "com.dealix.approval.requested": {"module": "governance", "description": "Approval requested", "description_ar": "تم طلب الاعتماد"},
    "com.dealix.approval.granted": {"module": "governance", "description": "Approval granted", "description_ar": "تم منح الاعتماد"},
    "com.dealix.approval.denied": {"module": "governance", "description": "Approval denied", "description_ar": "تم رفض الاعتماد"},
    "com.dealix.policy.violated": {"module": "governance", "description": "Policy violation detected", "description_ar": "تم اكتشاف انتهاك سياسة"},
}


def emit_cloud_event(
    event_type: str,
    source: str,
    data: dict[str, Any],
    tenant_id: str = "",
    subject: str | None = None,
    approval_class: str = "R0_AUTO",
    sensitivity: str = "INTERNAL",
    os_module: str = "",
    correlation_id: str | None = None,
) -> CloudEvent:
    return CloudEvent(
        source=source,
        type=event_type,
        subject=subject,
        data=data,
        tenantid=tenant_id,
        correlationid=correlation_id or str(uuid.uuid4()),
        approvalclass=approval_class,
        sensitivity=sensitivity,
        osmodule=os_module,
    )
