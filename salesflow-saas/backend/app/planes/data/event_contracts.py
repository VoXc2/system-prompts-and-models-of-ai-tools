"""
Event Contracts — CloudEvents + JSON Schema + AsyncAPI compliant event system.

Every domain event is typed, versioned, and machine-readable.
Producers and consumers share a contract that enables interoperability.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field


class CloudEvent(BaseModel):
    """CNCF CloudEvents v1.0 compliant envelope."""
    specversion: str = "1.0"
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source: str
    type: str
    subject: Optional[str] = None
    time: datetime = Field(default_factory=datetime.utcnow)
    datacontenttype: str = "application/json"
    dataschema: Optional[str] = None
    data: dict[str, Any] = Field(default_factory=dict)

    # Dealix extensions
    tenantid: Optional[str] = None
    correlationid: Optional[str] = None
    traceid: Optional[str] = None
    sensitivity: str = "internal"


EVENT_CATALOG: dict[str, dict[str, str]] = {
    # Sales OS
    "dealix.sales.lead.captured": {
        "description": "New lead captured from any channel",
        "description_ar": "تم التقاط عميل محتمل جديد من أي قناة",
        "schema": "schemas/sales/lead_captured.json",
    },
    "dealix.sales.lead.qualified": {
        "description": "Lead qualified by AI scoring",
        "description_ar": "تم تأهيل العميل المحتمل بالتقييم الذكي",
        "schema": "schemas/sales/lead_qualified.json",
    },
    "dealix.sales.deal.created": {
        "description": "New deal created in pipeline",
        "description_ar": "تم إنشاء صفقة جديدة في المسار",
        "schema": "schemas/sales/deal_created.json",
    },
    "dealix.sales.deal.stage_changed": {
        "description": "Deal moved to a new stage",
        "description_ar": "انتقلت الصفقة إلى مرحلة جديدة",
        "schema": "schemas/sales/deal_stage_changed.json",
    },
    "dealix.sales.deal.closed_won": {
        "description": "Deal closed successfully",
        "description_ar": "تم إغلاق الصفقة بنجاح",
        "schema": "schemas/sales/deal_closed_won.json",
    },
    "dealix.sales.proposal.sent": {
        "description": "Proposal sent to prospect",
        "description_ar": "تم إرسال المقترح للعميل المحتمل",
        "schema": "schemas/sales/proposal_sent.json",
    },
    # Partnership OS
    "dealix.partnership.discovered": {
        "description": "New potential partner identified",
        "description_ar": "تم اكتشاف شريك محتمل جديد",
        "schema": "schemas/partnership/discovered.json",
    },
    "dealix.partnership.activated": {
        "description": "Partnership officially activated",
        "description_ar": "تم تفعيل الشراكة رسمياً",
        "schema": "schemas/partnership/activated.json",
    },
    "dealix.partnership.scorecard_updated": {
        "description": "Partner scorecard metrics refreshed",
        "description_ar": "تم تحديث مقاييس بطاقة أداء الشريك",
        "schema": "schemas/partnership/scorecard_updated.json",
    },
    # M&A OS
    "dealix.ma.target.sourced": {
        "description": "New acquisition target identified",
        "description_ar": "تم تحديد هدف استحواذ جديد",
        "schema": "schemas/ma/target_sourced.json",
    },
    "dealix.ma.dd.started": {
        "description": "Due diligence process initiated",
        "description_ar": "بدأت عملية الفحص النافي للجهالة",
        "schema": "schemas/ma/dd_started.json",
    },
    "dealix.ma.offer.sent": {
        "description": "Acquisition offer submitted",
        "description_ar": "تم تقديم عرض الاستحواذ",
        "schema": "schemas/ma/offer_sent.json",
    },
    "dealix.ma.closed": {
        "description": "Acquisition closed and completed",
        "description_ar": "تم إغلاق وإتمام الاستحواذ",
        "schema": "schemas/ma/closed.json",
    },
    # Expansion OS
    "dealix.expansion.market.scanned": {
        "description": "New market scanning completed",
        "description_ar": "اكتمل مسح السوق الجديد",
        "schema": "schemas/expansion/market_scanned.json",
    },
    "dealix.expansion.launched": {
        "description": "Market entry launched",
        "description_ar": "تم إطلاق دخول السوق",
        "schema": "schemas/expansion/launched.json",
    },
    # PMI OS
    "dealix.pmi.day1.ready": {
        "description": "Day-1 readiness confirmed",
        "description_ar": "تم تأكيد جاهزية اليوم الأول",
        "schema": "schemas/pmi/day1_ready.json",
    },
    "dealix.pmi.milestone.completed": {
        "description": "PMI milestone reached",
        "description_ar": "تم الوصول لمحطة مهمة في تكامل ما بعد الاستحواذ",
        "schema": "schemas/pmi/milestone_completed.json",
    },
    # Executive OS
    "dealix.executive.approval.requested": {
        "description": "Executive approval requested",
        "description_ar": "تم طلب موافقة تنفيذية",
        "schema": "schemas/executive/approval_requested.json",
    },
    "dealix.executive.approval.granted": {
        "description": "Executive approval granted",
        "description_ar": "تم منح الموافقة التنفيذية",
        "schema": "schemas/executive/approval_granted.json",
    },
    "dealix.executive.escalation.triggered": {
        "description": "Issue escalated to executive level",
        "description_ar": "تم تصعيد المشكلة للمستوى التنفيذي",
        "schema": "schemas/executive/escalation_triggered.json",
    },
    # Trust/Compliance
    "dealix.compliance.violation.detected": {
        "description": "Policy violation detected",
        "description_ar": "تم اكتشاف مخالفة للسياسة",
        "schema": "schemas/compliance/violation_detected.json",
    },
    "dealix.compliance.check.passed": {
        "description": "Compliance check passed successfully",
        "description_ar": "تم اجتياز فحص الامتثال بنجاح",
        "schema": "schemas/compliance/check_passed.json",
    },
}


def create_event(
    event_type: str,
    source: str,
    data: dict[str, Any],
    tenant_id: Optional[str] = None,
    correlation_id: Optional[str] = None,
    trace_id: Optional[str] = None,
    subject: Optional[str] = None,
) -> CloudEvent:
    """Create a typed CloudEvent with Dealix extensions."""
    catalog_entry = EVENT_CATALOG.get(event_type)
    schema_uri = catalog_entry["schema"] if catalog_entry else None
    return CloudEvent(
        source=source,
        type=event_type,
        subject=subject,
        data=data,
        dataschema=schema_uri,
        tenantid=tenant_id,
        correlationid=correlation_id or str(uuid.uuid4()),
        traceid=trace_id or str(uuid.uuid4()),
    )
