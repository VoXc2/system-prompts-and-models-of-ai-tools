"""
Arabic text intelligence API — Mukhtasar when installed; extractive fallback.

Does not persist raw inbound payloads from this endpoint unless `persist_market` is used
for aggregate market rows (themes only).
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import get_current_user
from app.config import get_settings
from app.models.text_intelligence import TextIntelligenceMarketInsight
from app.models.user import User
from app.services.text_intelligence.service import (
    analyze_arabic_text,
    analyze_market_corpus,
    strip_raw_for_persistence,
)

router = APIRouter(prefix="/text-intelligence", tags=["Text Intelligence"])


class AnalyzeBody(BaseModel):
    text: str = Field(..., min_length=1, max_length=24_000)
    context: str = Field("api", max_length=80)
    input_kind: str = Field("manual", max_length=80)


class MarketBody(BaseModel):
    texts: list[str] = Field(..., min_length=1, max_length=120)
    scope: str = Field("generic", max_length=120)
    persist: bool = False


@router.post("/analyze")
async def post_analyze(
    body: AnalyzeBody,
    user: User = Depends(get_current_user),
) -> dict[str, Any]:
    if not get_settings().DEALIX_TEXT_INTELLIGENCE_ENABLED:
        raise HTTPException(503, detail="text_intelligence_disabled")
    intel = analyze_arabic_text(
        body.text,
        context=body.context or "api",
        input_kind=body.input_kind or "manual",
    )
    return strip_raw_for_persistence(intel)


@router.post("/market-insights")
async def post_market_insights(
    body: MarketBody,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict[str, Any]:
    if not get_settings().DEALIX_TEXT_INTELLIGENCE_ENABLED:
        raise HTTPException(503, detail="text_intelligence_disabled")
    chunks = [t[:12_000] for t in body.texts if t][:120]
    agg = analyze_market_corpus(chunks, scope=body.scope)
    if body.persist:
        row = TextIntelligenceMarketInsight(
            tenant_id=user.tenant_id,
            scope=body.scope[:120],
            insights_json=agg,
            source_fingerprint=agg.get("source_fingerprint"),
        )
        db.add(row)
        await db.flush()
        await db.refresh(row)
        return {"id": str(row.id), **agg}
    return agg
