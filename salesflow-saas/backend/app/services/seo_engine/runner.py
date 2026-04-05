"""Orchestrates SEO engine runs — persists rows, optional domain events."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.seo_intelligence import (
    SeoCompetitor,
    SeoContentDraft,
    SeoContentGap,
    SeoEngineRun,
    SeoKeywordOpportunity,
    SeoSchemaFinding,
)
from app.models.tenant import Tenant
from app.services.operations_hub import emit_domain_event
from app.services.seo_engine.http_fetch import check_url_reachability, fetch_page_summary
from app.services.seo_engine.schema_builder import build_organization_jsonld, build_website_jsonld

logger = logging.getLogger("dealix.seo_engine")


async def _public_urls_from_settings() -> List[str]:
    s = get_settings()
    raw = (getattr(s, "DEALIX_SEO_PUBLIC_BASE_URLS", None) or "").strip()
    if not raw:
        fe = (s.FRONTEND_URL or "").strip()
        return [fe] if fe else []
    return [u.strip() for u in raw.split(",") if u.strip()]


async def run_technical_audit(
    db: AsyncSession,
    *,
    tenant_id: UUID,
    tenant: Optional[Tenant] = None,
) -> Dict[str, Any]:
    """Check reachability of configured public URLs; record schema suggestions for homepage."""
    urls = await _public_urls_from_settings()
    checks = []
    for u in urls:
        checks.append(await check_url_reachability(u))

    issues = [c for c in checks if not c.get("ok")]
    out = {
        "urls_checked": checks,
        "issue_count": len(issues),
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }

    if tenant and urls:
        org = build_organization_jsonld(
            name=tenant.name_ar or tenant.name,
            url=urls[0],
        )
        web = build_website_jsonld(url=urls[0], name=tenant.name_ar or tenant.name)
        sf = SeoSchemaFinding(
            tenant_id=tenant_id,
            page_url=urls[0],
            page_kind="home",
            finding_type="suggested" if issues else "info",
            detail="Organization + WebSite JSON-LD recommended on homepage.",
            proposed_jsonld={"organization": org, "website": web},
            status="open",
        )
        db.add(sf)

    return out


async def run_competitor_refresh(
    db: AsyncSession,
    *,
    tenant_id: UUID,
) -> Dict[str, Any]:
    q = await db.execute(
        select(SeoCompetitor).where(SeoCompetitor.tenant_id == tenant_id, SeoCompetitor.is_active.is_(True))
    )
    comps = q.scalars().all()
    snapshots = []
    for c in comps:
        url = c.domain if c.domain.startswith("http") else f"https://{c.domain}"
        snap = await fetch_page_summary(url)
        c.snapshot_json = snap
        c.last_snapshot_at = datetime.now(timezone.utc)
        snapshots.append({"domain": c.domain, "snapshot": snap})
    await db.flush()
    return {"competitors_refreshed": len(snapshots), "snapshots": snapshots}


def _derive_gaps_from_competitors(snapshots: List[Dict[str, Any]], our_keywords: List[str]) -> List[Dict[str, Any]]:
    """Heuristic: competitor titles vs our seed keywords."""
    gaps = []
    for s in snapshots:
        title = (s.get("snapshot") or {}).get("title") or ""
        for kw in our_keywords:
            if kw and kw.lower() not in title.lower():
                gaps.append(
                    {
                        "topic": f"Coverage: {kw} vs competitor tone",
                        "gap_type": "keyword_presence",
                        "priority": "medium",
                        "evidence": {"competitor": s.get("domain"), "their_title": title[:200]},
                    }
                )
    return gaps[:50]


async def run_keyword_and_gap_scan(
    db: AsyncSession,
    *,
    tenant_id: UUID,
    seed_keywords: List[str],
    source_run_id: Optional[UUID],
) -> Dict[str, Any]:
    q = await db.execute(
        select(SeoCompetitor).where(SeoCompetitor.tenant_id == tenant_id, SeoCompetitor.is_active.is_(True))
    )
    comps = q.scalars().all()
    snaps = [{"domain": c.domain, "snapshot": c.snapshot_json or {}} for c in comps]
    gaps_data = _derive_gaps_from_competitors(snaps, seed_keywords or ["B2B", "مبيعات", "CRM"])
    for g in gaps_data:
        db.add(
            SeoContentGap(
                tenant_id=tenant_id,
                topic=g["topic"],
                gap_type=g["gap_type"],
                priority=g["priority"],
                evidence_json=g.get("evidence") or {},
                source_run_id=source_run_id,
            )
        )
    for i, kw in enumerate(seed_keywords[:30]):
        score = max(30, 90 - i * 2)
        db.add(
            SeoKeywordOpportunity(
                tenant_id=tenant_id,
                keyword=kw[:500],
                intent="commercial",
                score=score,
                priority="high" if score > 70 else "medium",
                source_run_id=source_run_id,
                status="suggested",
                evidence_json={"source": "seed_list"},
            )
        )
    await db.flush()
    return {"gaps_created": len(gaps_data), "keywords_seeded": min(len(seed_keywords), 30)}


async def create_content_brief_draft(
    db: AsyncSession,
    *,
    tenant_id: UUID,
    target_keyword: str,
    city: Optional[str] = None,
) -> SeoContentDraft:
    title = f"مسودة SEO: {target_keyword}" + (f" — {city}" if city else "")
    body = (
        f"# {title}\n\n"
        "## المقصد\n"
        "- شرح قيمة المنتج للمشتري B2B في السعودية.\n\n"
        "## العناوين المقترحة\n"
        "- التحديات\n- الحل\n- لماذا Dealix\n- دعوة لاتخاذ إجراء\n"
    )
    row = SeoContentDraft(
        tenant_id=tenant_id,
        kind="brief",
        title=title[:500],
        body_md=body,
        target_keyword=target_keyword[:500],
        intent="commercial",
        city=city,
        locale="ar",
        status="draft",
        meta_json={"generator": "seo_engine", "mode": "draft_only"},
    )
    db.add(row)
    await db.flush()
    return row


async def execute_run(
    db: AsyncSession,
    *,
    tenant_id: UUID,
    tenant: Tenant,
    run_kind: str,
    options: Dict[str, Any],
) -> SeoEngineRun:
    run = SeoEngineRun(
        tenant_id=tenant_id,
        run_kind=run_kind,
        status="running",
        input_json=options,
        started_at=datetime.now(timezone.utc),
    )
    db.add(run)
    await db.flush()
    out: Dict[str, Any] = {}
    try:
        if run_kind in ("technical_audit", "full_pipeline"):
            out["technical"] = await run_technical_audit(db, tenant_id=tenant_id, tenant=tenant)
        if run_kind in ("competitor_refresh", "full_pipeline"):
            out["competitors"] = await run_competitor_refresh(db, tenant_id=tenant_id)
        if run_kind in ("keyword_gap", "full_pipeline"):
            seeds = list(options.get("seed_keywords") or [])
            out["keywords"] = await run_keyword_and_gap_scan(
                db, tenant_id=tenant_id, seed_keywords=seeds, source_run_id=run.id
            )
        if run_kind == "content_brief" and options.get("target_keyword"):
            d = await create_content_brief_draft(
                db,
                tenant_id=tenant_id,
                target_keyword=str(options["target_keyword"]),
                city=options.get("city"),
            )
            out["draft_id"] = str(d.id)
        run.status = "completed"
        run.output_json = out
        run.completed_at = datetime.now(timezone.utc)
        await emit_domain_event(
            db,
            tenant_id=tenant_id,
            event_type="seo.engine.run_completed",
            payload={"run_id": str(run.id), "kind": run_kind, "summary_keys": list(out.keys())},
            source="seo_engine",
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception("seo run failed")
        run.status = "failed"
        run.error_text = str(exc)[:4000]
        run.completed_at = datetime.now(timezone.utc)
    await db.flush()
    return run
