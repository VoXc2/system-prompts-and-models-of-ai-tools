"""Deal Lifecycle Hooks — auto-assemble evidence pack on deal close."""

from __future__ import annotations

import uuid
from typing import Any, Dict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.deal import Deal
from app.models.lead import Lead
from app.models.operations import ApprovalRequest


async def on_deal_closed(db: AsyncSession, *, tenant_id: str, deal_id: str) -> Dict[str, Any]:
    """Called when a deal transitions to closed_won. Auto-assembles evidence pack."""
    from app.services.evidence_pack_service import evidence_pack_service

    deal = (await db.execute(
        select(Deal).where(Deal.id == deal_id, Deal.tenant_id == tenant_id)
    )).scalar_one_or_none()

    if not deal:
        return {"status": "deal_not_found"}

    lead_data = {}
    if deal.lead_id:
        lead = (await db.execute(select(Lead).where(Lead.id == deal.lead_id))).scalar_one_or_none()
        if lead:
            lead_data = {"id": str(lead.id), "company": lead.company_name, "score": lead.score, "status": lead.status}

    approvals = (await db.execute(
        select(ApprovalRequest).where(
            ApprovalRequest.tenant_id == tenant_id,
            ApprovalRequest.resource_id == deal.id,
        )
    )).scalars().all()

    approval_data = [
        {"id": str(a.id), "status": a.status, "channel": a.channel, "created_at": a.created_at.isoformat() if a.created_at else None}
        for a in approvals
    ]

    contents = [
        {"type": "deal_summary", "source": "deals", "data": {
            "id": str(deal.id), "title": deal.title, "value": float(deal.value or 0),
            "stage": deal.stage, "currency": deal.currency,
        }},
        {"type": "lead_data", "source": "leads", "data": lead_data},
        {"type": "approval_records", "source": "approval_requests", "data": {"approvals": approval_data, "count": len(approval_data)}},
    ]

    pack = await evidence_pack_service.assemble(
        db,
        tenant_id=tenant_id,
        title=f"Deal Closure Evidence — {deal.title}",
        title_ar=f"حزمة أدلة إغلاق الصفقة — {deal.title}",
        pack_type="deal_closure",
        entity_type="deal",
        entity_id=deal_id,
        contents=contents,
        metadata={"trace_id": str(uuid.uuid4()), "auto_generated": True},
    )

    return {
        "status": "evidence_pack_assembled",
        "evidence_pack_id": str(pack.id),
        "hash_signature": pack.hash_signature,
        "deal_id": deal_id,
        "contents_count": len(contents),
    }
