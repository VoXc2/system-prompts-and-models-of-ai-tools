"""
واجهة محرك استخبارات الليدات — بحث موحّد، استيراد ملفات، حالة المفاتيح.
"""

from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel, Field

from app.services.lead_intelligence_engine import (
    ALL_SOURCES,
    engine_capabilities,
    parse_leads_csv,
    run_unified_lead_search,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/lead-intelligence", tags=["Lead Intelligence Engine"])


class UnifiedSearchBody(BaseModel):
    query: str = Field(..., min_length=1, max_length=400, description="كلمة البحث أو نوع النشاط")
    city: str = Field(default="الرياض", max_length=120)
    sector: str = Field(default="", max_length=200, description="لإشارات LinkedIn العامة")
    sources: Optional[list[str]] = Field(
        default=None,
        description=f"مصدر واحد أو أكثر من: {', '.join(ALL_SOURCES)}",
    )
    max_per_source: int = Field(default=12, ge=1, le=40)


@router.get("/capabilities")
async def get_capabilities():
    """يعرض أي واجهات API مفعّلة في البيئة."""
    return engine_capabilities()


@router.post("/unified-search")
async def unified_search(body: UnifiedSearchBody):
    """بحث موحّد عبر خرائط Google و/SerpAPI و/CSE وBing وإشارات LinkedIn العامة."""
    if body.sources:
        bad = [s for s in body.sources if s not in ALL_SOURCES]
        if bad:
            raise HTTPException(400, detail=f"مصادر غير معروفة: {bad}. المسموح: {list(ALL_SOURCES)}")
    return await run_unified_lead_search(
        query=body.query,
        city=body.city,
        sector=body.sector,
        sources=body.sources,
        max_per_source=body.max_per_source,
    )


@router.post("/ingest-csv")
async def ingest_csv(file: UploadFile = File(...)):
    """استيراد ليدات من CSV (فاصل ، أو ؛ أو تاب) — أعمدة مرنة: شركة، هاتف، موقع، مدينة، قطاع."""
    if not file.filename or not file.filename.lower().endswith((".csv", ".txt")):
        raise HTTPException(400, detail="الملف يجب أن يكون .csv أو .txt")
    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(413, detail="الحد الأقصى 5 ميجابايت")
    rows, warnings = parse_leads_csv(content)
    return {
        "ok": True,
        "filename": file.filename,
        "count": len(rows),
        "prospects": rows,
        "warnings": warnings,
    }
