"""Innovation / Autonomous Growth Factory — deterministic demo API + DB-backed paths."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from auto_client_acquisition.innovation import (
    analyze_deal_room,
    build_demo_command_feed,
    build_demo_proof_ledger,
    list_growth_missions,
    recommend_experiments,
)
from auto_client_acquisition.innovation.aeo_radar import build_aeo_radar_demo
from auto_client_acquisition.innovation.command_feed_live import build_command_feed_from_db
from auto_client_acquisition.innovation.proof_ledger_repo import (
    proof_ledger_append,
    proof_ledger_list,
    proof_ledger_weekly_report,
)
from auto_client_acquisition.innovation.ten_in_ten import build_ten_opportunities
from db.session import get_db

router = APIRouter(prefix="/api/v1/innovation", tags=["innovation"])


@router.get("/command-feed/demo")
async def command_feed_demo() -> dict[str, Any]:
    """بطاقات Command Feed توضيحية."""
    return build_demo_command_feed()


@router.get("/command-feed/live")
async def command_feed_live(
    session: AsyncSession = Depends(get_db),
    tenant_id: str = Query("default"),
) -> dict[str, Any]:
    """بطاقات من قاعدة البيانات عند توفر أحداث؛ وإلا fallback للعرض التجريبي."""
    return await build_command_feed_from_db(session, tenant_id=tenant_id)


@router.get("/growth-missions")
async def growth_missions() -> dict[str, Any]:
    """قائمة مهام النمو بما فيها Kill feature «10 فرص في 10 دقائق»."""
    return list_growth_missions()


@router.post("/opportunities/ten-in-ten")
async def opportunities_ten_in_ten(
    payload: dict[str, Any] = Body(default_factory=dict),
) -> dict[str, Any]:
    """10 فرص في 10 دقائق — مسودات بانتظار الموافقة فقط؛ لا إرسال."""
    return build_ten_opportunities(payload or None)


@router.get("/aeo/radar/demo")
async def aeo_radar_demo(sector: str | None = Query(None)) -> dict[str, Any]:
    """قائمة تحقق AEO تجريبية حسب القطاع — بدون بحث حي."""
    return build_aeo_radar_demo(sector)


@router.post("/experiments/recommend")
async def experiments_recommend(
    context: dict[str, Any] = Body(default_factory=dict),
) -> dict[str, Any]:
    """ثلاث تجارب شهرية مقترحة؛ الجسم اختياري ويدعم past_experiments."""
    return recommend_experiments(context or None)


@router.get("/proof-ledger/demo")
async def proof_ledger_demo() -> dict[str, Any]:
    """سجل إثبات تجريبي ثابت."""
    return build_demo_proof_ledger()


@router.post("/proof-ledger/events")
async def proof_ledger_events_create(
    body: dict[str, Any] = Body(default_factory=dict),
    session: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """إلحاق حدث في دفتر الإثبات (تقديرات تشغيلية)."""
    return await proof_ledger_append(
        session,
        tenant_id=str(body.get("tenant_id") or "default"),
        event_type=str(body.get("event_type") or "note"),
        revenue_influenced_sar_estimate=float(body.get("revenue_influenced_sar_estimate") or 0),
        notes_ar=str(body.get("notes_ar") or ""),
        extra=body.get("extra_json") if isinstance(body.get("extra_json"), dict) else {},
    )


@router.get("/proof-ledger/events")
async def proof_ledger_events_list(
    session: AsyncSession = Depends(get_db),
    tenant_id: str = Query("default"),
    limit: int = Query(100, ge=1, le=500),
) -> dict[str, Any]:
    """قائمة أحداث دفتر الإثبات."""
    events = await proof_ledger_list(session, tenant_id=tenant_id, limit=limit)
    return {"events": events, "tenant_id": tenant_id}


@router.get("/proof-ledger/report/week")
async def proof_ledger_report_week(
    session: AsyncSession = Depends(get_db),
    tenant_id: str = Query("default"),
) -> dict[str, Any]:
    """ملخص 7 أيام لتقديرات الإيراد المؤثرة (ليس محاسبة دقيقة)."""
    return await proof_ledger_weekly_report(session, tenant_id=tenant_id)


@router.post("/deal-room/analyze")
async def deal_room_analyze(
    payload: dict[str, Any] = Body(default_factory=dict),
) -> dict[str, Any]:
    """تحليل غرفة صفقة تجريبي من جسم الطلب."""
    return analyze_deal_room(payload or None)
