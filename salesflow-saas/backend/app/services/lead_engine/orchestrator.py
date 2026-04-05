"""Orchestrate scoring, routing, signals, stakeholder templates — single entry for lead intel."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import UUID

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import IS_SQLITE
from app.models.lead import Lead
from app.models.lead_engine import (
    LeadEngineLearningEvent,
    LeadEnginePlaybookRun,
    LeadEngineRoutingDecision,
    LeadEngineScoreSnapshot,
    LeadEngineSignal,
    LeadEngineStakeholderRole,
)
from app.services.lead_engine.icp import DEFAULT_ICP_TEMPLATES, match_icp_slug
from app.services.lead_engine.playbooks import pick_playbook_key
from app.services.lead_engine.scoring import compute_lead_dimensions, priority_to_motion
from app.services.lead_engine.stakeholders import build_stakeholder_rows_for_lead
from app.services.operations_hub import emit_domain_event

logger = logging.getLogger("dealix.lead_engine")


async def recompute_lead(
    db: AsyncSession,
    *,
    tenant_id: UUID,
    lead: Lead,
    emit_events: bool = True,
) -> Dict[str, Any]:
    meta = lead.extra_metadata if isinstance(lead.extra_metadata, dict) else {}
    icp_slug = match_icp_slug(lead.source or "", meta)
    template = next((t for t in DEFAULT_ICP_TEMPLATES if t["slug"] == icp_slug), DEFAULT_ICP_TEMPLATES[-1])
    buyer_roles = list(template["config_json"].get("buyer_roles") or [])

    total, band, dims, reasons = compute_lead_dimensions(lead, icp_slug, meta)
    motion = priority_to_motion(band, meta)
    playbook_key = pick_playbook_key(band, motion, {**meta, "enterprise": meta.get("enterprise")})

    # Replace snapshot rows for this lead (latest)
    await db.execute(delete(LeadEngineScoreSnapshot).where(LeadEngineScoreSnapshot.lead_id == lead.id))
    await db.execute(delete(LeadEngineRoutingDecision).where(LeadEngineRoutingDecision.lead_id == lead.id))
    await db.execute(delete(LeadEngineStakeholderRole).where(LeadEngineStakeholderRole.lead_id == lead.id))
    await db.execute(delete(LeadEngineSignal).where(LeadEngineSignal.lead_id == lead.id))

    snap = LeadEngineScoreSnapshot(
        tenant_id=tenant_id,
        lead_id=lead.id,
        total_score=total,
        priority_band=band,
        dimension_scores=dims,
        reason_codes=reasons,
    )
    route = LeadEngineRoutingDecision(
        tenant_id=tenant_id,
        lead_id=lead.id,
        motion=motion,
        playbook_key=playbook_key,
        reason_codes=reasons + [f"icp:{icp_slug}", f"playbook:{playbook_key}"],
    )
    sig = LeadEngineSignal(
        tenant_id=tenant_id,
        lead_id=lead.id,
        category="intent",
        sub_type="pipeline_fit",
        score_contribution=float(dims.get("intent", 50)),
        explanation="Composite intent from status and metadata.",
        evidence_json={"source": lead.source, "status": lead.status},
        directness="indirect" if band in ("P2", "P3") else "direct",
    )
    for row in build_stakeholder_rows_for_lead(tenant_id, lead.id, buyer_roles):
        db.add(row)

    db.add(snap)
    db.add(route)
    db.add(sig)

    lead.score = total
    meta_out = dict(meta)
    meta_out["lead_engine"] = {
        "icp_slug": icp_slug,
        "priority_band": band,
        "motion": motion,
        "playbook_key": playbook_key,
        "recomputed_at": datetime.now(timezone.utc).isoformat(),
    }
    lead.extra_metadata = meta_out

    pb_run = LeadEnginePlaybookRun(
        tenant_id=tenant_id,
        lead_id=lead.id,
        playbook_key=playbook_key,
        status="suggested",
        outcome_json={"band": band, "motion": motion},
    )
    db.add(pb_run)

    await db.flush()

    if emit_events:
        await emit_domain_event(
            db,
            tenant_id=tenant_id,
            event_type="lead.engine.scored",
            payload={
                "lead_id": str(lead.id),
                "score": total,
                "priority_band": band,
                "motion": motion,
                "playbook_key": playbook_key,
            },
            source="lead_engine",
        )

    return {
        "lead_id": str(lead.id),
        "score": total,
        "priority_band": band,
        "motion": motion,
        "playbook_key": playbook_key,
        "icp_slug": icp_slug,
        "reason_codes": reasons,
    }


async def record_outcome(
    db: AsyncSession,
    *,
    tenant_id: UUID,
    lead_id: Optional[UUID],
    event_type: str,
    payload: Optional[Dict[str, Any]] = None,
) -> None:
    lid = str(lead_id) if lead_id and IS_SQLITE else lead_id
    ev = LeadEngineLearningEvent(
        tenant_id=tenant_id,
        lead_id=lid,
        event_type=event_type,
        payload_json=payload or {},
    )
    db.add(ev)
    await db.flush()
