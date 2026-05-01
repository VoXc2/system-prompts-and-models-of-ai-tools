"""Leads (Phase 8) endpoints + Local/Web Discovery + Enrichment + Outreach Prepare."""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy import select

from api.dependencies import get_acquisition_pipeline
from api.schemas import LeadCreateRequest, LeadResponse, PipelineResponse
from auto_client_acquisition.agents.intake import LeadSource
from auto_client_acquisition.connectors.google_maps import (
    INDUSTRY_QUERIES as _LOCAL_INDUSTRY_QUERIES,
    SAUDI_CITIES as _LOCAL_SAUDI_CITIES,
)
from auto_client_acquisition.pipeline import AcquisitionPipeline
from auto_client_acquisition.pipelines.enrichment import enrich_account
from auto_client_acquisition.providers.maps import (
    discover_with_chain as _discover_with_chain,
    get_maps_chain as _get_maps_chain,
)
from auto_client_acquisition.providers.search import (
    get_search_chain as _get_search_chain,
    search_with_chain as _search_with_chain,
)
from db.models import (
    AccountRecord,
    ContactRecord,
    LeadScoreRecord,
    OutreachQueueRecord,
    SuppressionRecord,
)
from db.session import async_session_factory

router = APIRouter(prefix="/api/v1/leads", tags=["leads"])
log = logging.getLogger(__name__)


def _new_id(prefix: str = "") -> str:
    suffix = uuid.uuid4().hex[:24]
    return f"{prefix}{suffix}" if prefix else suffix


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


# ── Original lead-create endpoint (unchanged) ────────────────────
@router.post("", response_model=PipelineResponse)
async def create_lead(
    payload: LeadCreateRequest,
    pipeline: AcquisitionPipeline = Depends(get_acquisition_pipeline),
    auto_book: bool = True,
    auto_proposal: bool = False,
) -> PipelineResponse:
    """Submit a new lead — runs through the full acquisition pipeline."""
    try:
        source = LeadSource(payload.source)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=f"Invalid source: {e}") from e

    result = await pipeline.run(
        payload=payload.model_dump(exclude_none=True),
        source=source,
        auto_book=auto_book,
        auto_proposal=auto_proposal,
    )
    return PipelineResponse(
        lead=LeadResponse(
            id=result.lead.id,
            source=result.lead.source.value,
            company_name=result.lead.company_name,
            contact_name=result.lead.contact_name,
            contact_email=result.lead.contact_email,
            contact_phone=result.lead.contact_phone,
            sector=result.lead.sector,
            region=result.lead.region,
            status=result.lead.status.value,
            fit_score=result.lead.fit_score,
            urgency_score=result.lead.urgency_score,
            pain_points=result.lead.pain_points,
            locale=result.lead.locale,
            created_at=result.lead.created_at,
        ),
        fit_score=result.fit_score.to_dict() if result.fit_score else None,
        extraction=result.extraction.to_dict() if result.extraction else None,
        qualification=result.qualification.to_dict() if result.qualification else None,
        crm_sync=result.crm_sync.to_dict() if result.crm_sync else None,
        booking=result.booking.to_dict() if result.booking else None,
        proposal=result.proposal.to_dict() if result.proposal else None,
        warnings=result.warnings,
    )


# ── Local Saudi Lead Engine (Google Places) ────────────────────────
@router.get("/discover/local-industries")
async def list_local_industries() -> dict[str, Any]:
    return {
        "industries": [
            {"key": k, "queries": v} for k, v in _LOCAL_INDUSTRY_QUERIES.items()
        ],
        "cities": [
            {"key": k, "ar": ar, "en": en}
            for k, (ar, en) in _LOCAL_SAUDI_CITIES.items()
        ],
        "notes": (
            "POST /api/v1/leads/discover/local with body "
            "{industry, city, max_results, hydrate_details, custom_query, page_token}. "
            "Set GOOGLE_MAPS_API_KEY in Railway env to enable."
        ),
    }


@router.post("/discover/local")
async def discover_local_endpoint(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """Saudi local lead engine — chains Google Places → SerpApi → Apify → static."""
    industry = str(body.get("industry") or "").strip()
    city = str(body.get("city") or "").strip()
    max_results = int(body.get("max_results") or 20)
    hydrate_details = bool(body.get("hydrate_details", True))
    custom_query = body.get("custom_query")
    page_token = body.get("page_token")

    if not industry and not custom_query:
        raise HTTPException(400, "industry_required")
    if not city:
        raise HTTPException(400, "city_required")
    if max_results < 1 or max_results > 40:
        raise HTTPException(400, "max_results_out_of_range: 1..40")

    chain_result = await _discover_with_chain(
        industry=industry or "custom",
        city=city,
        max_results=max_results,
        page_token=str(page_token) if page_token else None,
        hydrate_details=hydrate_details,
        custom_query=str(custom_query) if custom_query else None,
    )
    payload = chain_result.to_dict()
    payload["chain"] = [
        {"name": p.name, "available": p.is_available()} for p in _get_maps_chain()
    ]
    return payload


# ── Web Lead Discovery ────────────────────────────────────────────
@router.post("/discover/web")
async def discover_web_endpoint(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """Web lead discovery via SearchProvider chain (Google CSE → Tavily → static)."""
    query = str(body.get("query") or "").strip()
    num = int(body.get("num") or 10)
    site = body.get("site")
    lang = body.get("lang")

    if len(query) < 5:
        raise HTTPException(400, "query_too_short: min 5 chars")
    if num < 1 or num > 10:
        raise HTTPException(400, "num_out_of_range: 1..10")

    chain_result = await _search_with_chain(
        query, num=num,
        site=str(site) if site else None,
        lang=str(lang) if lang else None,
    )
    payload = chain_result.to_dict()
    payload["chain"] = [
        {"name": p.name, "available": p.is_available()} for p in _get_search_chain()
    ]
    return payload


# ── Full enrichment (single account) ──────────────────────────────
@router.post("/enrich/full")
async def enrich_full_endpoint(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """
    Full enrichment for a single account.
    Body: {company_name?, domain?, website?, city?, sector?, place_id?, level?}
    Level: basic | standard (default) | deep.
    """
    if not (body.get("company_name") or body.get("domain") or body.get("website")):
        raise HTTPException(400, "must_provide_company_name_or_domain_or_website")
    level = str(body.get("level") or "standard")
    if level not in {"basic", "standard", "deep"}:
        raise HTTPException(400, "level_must_be: basic | standard | deep")

    account = {
        "company_name": body.get("company_name") or "",
        "domain": body.get("domain"),
        "website": body.get("website"),
        "city": body.get("city"),
        "country": body.get("country") or "SA",
        "sector": body.get("sector"),
        "google_place_id": body.get("place_id"),
        "best_source": body.get("source") or "manual",
        "allowed_use": body.get("allowed_use") or "business_contact_research_only",
        "risk_level": body.get("risk_level") or "medium",
    }
    return await enrich_account(account, enrichment_level=level)


# ── Batch enrichment over existing accounts ───────────────────────
@router.post("/enrich/batch")
async def enrich_batch_endpoint(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """
    Enrich a batch of accounts already in the graph.
    Body: {account_ids: [...], level: basic|standard|deep}
    """
    ids = body.get("account_ids")
    level = str(body.get("level") or "standard")
    if not isinstance(ids, list) or not ids:
        raise HTTPException(400, "account_ids_required")
    if len(ids) > 100:
        raise HTTPException(400, "too_many: max 100 per batch")

    async with async_session_factory() as session:
        try:
            accs = (await session.execute(
                select(AccountRecord).where(AccountRecord.id.in_(ids))
            )).scalars().all()
        except Exception as exc:  # noqa: BLE001
            return {"status": "skipped_db_unreachable", "error": str(exc), "items": []}

        results: list[dict[str, Any]] = []
        for acc in accs:
            account_dict = {
                "id": acc.id, "company_name": acc.company_name,
                "domain": acc.domain, "website": acc.website,
                "city": acc.city, "country": acc.country, "sector": acc.sector,
                "google_place_id": acc.google_place_id, "best_source": acc.best_source,
                "risk_level": acc.risk_level,
                "allowed_use": (acc.extra or {}).get("allowed_use"),
            }
            try:
                result = await enrich_account(account_dict, enrichment_level=level)
            except Exception as exc:  # noqa: BLE001
                results.append({"id": acc.id, "status": "error", "error": str(exc)})
                continue
            score = result.get("score", {})
            session.add(LeadScoreRecord(
                id=_new_id("ls_"), account_id=acc.id,
                fit_score=float(score.get("fit") or 0),
                intent_score=float(score.get("intent") or 0),
                urgency_score=float(score.get("urgency") or 0),
                risk_score=float(score.get("risk") or 0),
                total_score=float(score.get("total") or 0),
                priority=str(score.get("priority") or "P3")[:8],
                recommended_channel=score.get("recommended_channel"),
                reason=score.get("reason"),
            ))
            acc.data_quality_score = float(result.get("data_quality", {}).get("score", 0))
            acc.status = "enriched"
            acc.updated_at = _utcnow()
            results.append({
                "id": acc.id, "status": "ok",
                "score": score, "dq": result.get("data_quality"),
                "providers_used": result.get("providers_used"),
            })

        try:
            await session.commit()
        except Exception as exc:  # noqa: BLE001
            await session.rollback()
            return {"status": "commit_failed", "error": str(exc), "items": results}

    return {"count": len(results), "items": results}
