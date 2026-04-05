"""
SEO Intelligence Engine — internal API (draft-only content; no auto-publish).

Requires authenticated user with role owner | admin | manager.
"""

from __future__ import annotations

from typing import Any, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_tenant, require_role
from app.config import get_settings
from app.database import get_db
from app.models.seo_intelligence import (
    SeoCompetitor,
    SeoContentDraft,
    SeoContentGap,
    SeoEngineRun,
    SeoKeywordOpportunity,
    SeoSchemaFinding,
)
from app.models.tenant import Tenant
from app.models.user import User
from app.services.seo_engine.runner import create_content_brief_draft, execute_run

router = APIRouter(prefix="/seo-engine", tags=["SEO Intelligence"])

_role = require_role("owner", "admin", "manager")


class StartRunBody(BaseModel):
    run_kind: str = Field(
        ...,
        pattern="^(technical_audit|competitor_refresh|keyword_gap|content_brief|full_pipeline)$",
    )
    options: dict[str, Any] = Field(default_factory=dict)


class CompetitorIn(BaseModel):
    domain: str = Field(..., min_length=3, max_length=255)
    display_name: Optional[str] = None
    notes: Optional[str] = None


class BriefBody(BaseModel):
    target_keyword: str = Field(..., min_length=1, max_length=500)
    city: Optional[str] = None


def _gate() -> None:
    if not get_settings().DEALIX_SEO_ENGINE_ENABLED:
        raise HTTPException(503, detail="SEO engine disabled")


@router.post("/runs")
async def start_run(
    body: StartRunBody,
    db: AsyncSession = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
    _auth: User = Depends(_role),
) -> dict[str, Any]:
    _gate()
    run = await execute_run(
        db,
        tenant_id=tenant.id,
        tenant=tenant,
        run_kind=body.run_kind,
        options=body.options,
    )
    await db.commit()
    return {
        "run_id": str(run.id),
        "status": run.status,
        "output": run.output_json,
        "error": run.error_text,
    }


@router.get("/runs")
async def list_runs(
    db: AsyncSession = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
    _: User = Depends(_role),
    limit: int = 30,
) -> dict[str, Any]:
    _gate()
    q = await db.execute(
        select(SeoEngineRun)
        .where(SeoEngineRun.tenant_id == tenant.id)
        .order_by(desc(SeoEngineRun.created_at))
        .limit(min(limit, 100))
    )
    rows = q.scalars().all()
    return {
        "runs": [
            {
                "id": str(r.id),
                "run_kind": r.run_kind,
                "status": r.status,
                "created_at": r.created_at.isoformat() if r.created_at else None,
                "completed_at": r.completed_at.isoformat() if r.completed_at else None,
            }
            for r in rows
        ]
    }


@router.get("/runs/{run_id}")
async def get_run(
    run_id: UUID,
    db: AsyncSession = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
    _: User = Depends(_role),
) -> dict[str, Any]:
    _gate()
    q = await db.execute(
        select(SeoEngineRun).where(SeoEngineRun.id == run_id, SeoEngineRun.tenant_id == tenant.id)
    )
    r = q.scalar_one_or_none()
    if not r:
        raise HTTPException(404, detail="not_found")
    return {
        "id": str(r.id),
        "run_kind": r.run_kind,
        "status": r.status,
        "input": r.input_json,
        "output": r.output_json,
        "error": r.error_text,
        "started_at": r.started_at.isoformat() if r.started_at else None,
        "completed_at": r.completed_at.isoformat() if r.completed_at else None,
    }


@router.post("/competitors")
async def add_competitor(
    body: CompetitorIn,
    db: AsyncSession = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
    _: User = Depends(_role),
) -> dict[str, Any]:
    _gate()
    row = SeoCompetitor(
        tenant_id=tenant.id,
        domain=body.domain.strip().lower().replace("https://", "").replace("http://", "").split("/")[0],
        display_name=body.display_name,
        notes=body.notes,
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return {"id": str(row.id), "domain": row.domain}


@router.get("/competitors")
async def list_competitors(
    db: AsyncSession = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
    _: User = Depends(_role),
) -> dict[str, Any]:
    _gate()
    q = await db.execute(
        select(SeoCompetitor).where(SeoCompetitor.tenant_id == tenant.id).order_by(SeoCompetitor.domain)
    )
    rows = q.scalars().all()
    return {
        "competitors": [
            {
                "id": str(c.id),
                "domain": c.domain,
                "display_name": c.display_name,
                "last_snapshot_at": c.last_snapshot_at.isoformat() if c.last_snapshot_at else None,
            }
            for c in rows
        ]
    }


@router.get("/keywords")
async def list_keywords(
    db: AsyncSession = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
    _: User = Depends(_role),
    limit: int = 50,
) -> dict[str, Any]:
    _gate()
    q = await db.execute(
        select(SeoKeywordOpportunity)
        .where(SeoKeywordOpportunity.tenant_id == tenant.id)
        .order_by(desc(SeoKeywordOpportunity.score))
        .limit(min(limit, 200))
    )
    rows = q.scalars().all()
    return {
        "keywords": [
            {
                "id": str(k.id),
                "keyword": k.keyword,
                "score": k.score,
                "status": k.status,
                "intent": k.intent,
            }
            for k in rows
        ]
    }


@router.get("/gaps")
async def list_gaps(
    db: AsyncSession = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
    _: User = Depends(_role),
    limit: int = 50,
) -> dict[str, Any]:
    _gate()
    q = await db.execute(
        select(SeoContentGap)
        .where(SeoContentGap.tenant_id == tenant.id)
        .order_by(desc(SeoContentGap.created_at))
        .limit(min(limit, 200))
    )
    rows = q.scalars().all()
    return {"gaps": [{"id": str(g.id), "topic": g.topic, "gap_type": g.gap_type, "priority": g.priority} for g in rows]}


@router.get("/schema-findings")
async def list_schema(
    db: AsyncSession = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
    _: User = Depends(_role),
    limit: int = 50,
) -> dict[str, Any]:
    _gate()
    q = await db.execute(
        select(SeoSchemaFinding)
        .where(SeoSchemaFinding.tenant_id == tenant.id)
        .order_by(desc(SeoSchemaFinding.created_at))
        .limit(min(limit, 200))
    )
    rows = q.scalars().all()
    return {
        "findings": [
            {
                "id": str(s.id),
                "page_url": s.page_url[:200],
                "finding_type": s.finding_type,
                "status": s.status,
                "has_proposal": s.proposed_jsonld is not None,
            }
            for s in rows
        ]
    }


@router.get("/drafts")
async def list_drafts(
    db: AsyncSession = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
    _: User = Depends(_role),
    limit: int = 50,
) -> dict[str, Any]:
    _gate()
    q = await db.execute(
        select(SeoContentDraft)
        .where(SeoContentDraft.tenant_id == tenant.id)
        .order_by(desc(SeoContentDraft.created_at))
        .limit(min(limit, 200))
    )
    rows = q.scalars().all()
    return {
        "drafts": [
            {
                "id": str(d.id),
                "kind": d.kind,
                "title": d.title,
                "status": d.status,
                "target_keyword": d.target_keyword,
            }
            for d in rows
        ]
    }


@router.post("/drafts/brief")
async def post_brief(
    body: BriefBody,
    db: AsyncSession = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
    _: User = Depends(_role),
) -> dict[str, Any]:
    _gate()
    d = await create_content_brief_draft(
        db, tenant_id=tenant.id, target_keyword=body.target_keyword, city=body.city
    )
    await db.commit()
    return {"draft_id": str(d.id), "status": d.status}
