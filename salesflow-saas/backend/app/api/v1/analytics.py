"""Analytics and reporting API for Dealix CRM."""
from datetime import datetime, date, timedelta
from typing import Optional
from enum import Enum
from io import StringIO

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import select, func, cast, String, case
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_active_user, get_db
from app.models.lead import Lead
from app.models.deal import Deal
from app.models.campaign import Campaign, LeadSource

router = APIRouter()


# ---------------------------------------------------------------------------
# Enums & shared models
# ---------------------------------------------------------------------------

class Period(str, Enum):
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"


class TrendItem(BaseModel):
    """A metric with current value and change vs previous period."""
    label: str
    label_ar: str
    value: float
    previous_value: float
    change_pct: float


class TimeSeriesPoint(BaseModel):
    date: str
    value: float


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _default_dates(
    date_from: Optional[date],
    date_to: Optional[date],
) -> tuple[date, date]:
    today = date.today()
    return (date_from or today - timedelta(days=30), date_to or today)


def _trend(current: float, previous: float) -> float:
    if previous == 0:
        return 100.0 if current > 0 else 0.0
    return round((current - previous) / previous * 100, 1)


def _previous_period(d_from: date, d_to: date) -> tuple[date, date]:
    """Calculate the equivalent previous period for comparison."""
    delta = d_to - d_from
    prev_to = d_from - timedelta(days=1)
    prev_from = prev_to - delta
    return prev_from, prev_to


# ---------------------------------------------------------------------------
# 1. GET /analytics/overview
# ---------------------------------------------------------------------------

@router.get("/overview")
async def analytics_overview(
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    period: Period = Query(Period.monthly),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """لوحة المؤشرات الرئيسية — Dashboard overview KPIs."""
    d_from, d_to = _default_dates(date_from, date_to)
    prev_from, prev_to = _previous_period(d_from, d_to)
    tenant_id = current_user["tenant_id"]

    d_from_dt = datetime.combine(d_from, datetime.min.time())
    d_to_dt = datetime.combine(d_to, datetime.max.time())
    prev_from_dt = datetime.combine(prev_from, datetime.min.time())
    prev_to_dt = datetime.combine(prev_to, datetime.max.time())

    # Current period leads
    cur_leads_result = await db.execute(
        select(func.count(Lead.id)).where(
            Lead.tenant_id == tenant_id,
            Lead.created_at >= d_from_dt,
            Lead.created_at <= d_to_dt,
        )
    )
    cur_leads = cur_leads_result.scalar() or 0

    # Previous period leads
    prev_leads_result = await db.execute(
        select(func.count(Lead.id)).where(
            Lead.tenant_id == tenant_id,
            Lead.created_at >= prev_from_dt,
            Lead.created_at <= prev_to_dt,
        )
    )
    prev_leads = prev_leads_result.scalar() or 0

    # Current period deals
    cur_deals_result = await db.execute(
        select(func.count(Deal.id)).where(
            Deal.tenant_id == tenant_id,
            Deal.created_at >= d_from_dt,
            Deal.created_at <= d_to_dt,
        )
    )
    cur_deals = cur_deals_result.scalar() or 0

    # Previous period deals
    prev_deals_result = await db.execute(
        select(func.count(Deal.id)).where(
            Deal.tenant_id == tenant_id,
            Deal.created_at >= prev_from_dt,
            Deal.created_at <= prev_to_dt,
        )
    )
    prev_deals = prev_deals_result.scalar() or 0

    # Current period revenue (closed_won deals)
    cur_rev_result = await db.execute(
        select(func.coalesce(func.sum(Deal.value), 0)).where(
            Deal.tenant_id == tenant_id,
            Deal.stage == "closed_won",
            Deal.created_at >= d_from_dt,
            Deal.created_at <= d_to_dt,
        )
    )
    cur_revenue = float(cur_rev_result.scalar() or 0)

    # Previous period revenue
    prev_rev_result = await db.execute(
        select(func.coalesce(func.sum(Deal.value), 0)).where(
            Deal.tenant_id == tenant_id,
            Deal.stage == "closed_won",
            Deal.created_at >= prev_from_dt,
            Deal.created_at <= prev_to_dt,
        )
    )
    prev_revenue = float(prev_rev_result.scalar() or 0)

    # Conversion rate: deals / leads
    cur_conversion = round((cur_deals / cur_leads * 100), 1) if cur_leads > 0 else 0.0
    prev_conversion = round((prev_deals / prev_leads * 100), 1) if prev_leads > 0 else 0.0

    return {
        "period": period.value,
        "date_from": str(d_from),
        "date_to": str(d_to),
        "tenant_id": tenant_id,
        "kpis": [
            TrendItem(
                label="Total Leads",
                label_ar="إجمالي العملاء المحتملين",
                value=cur_leads,
                previous_value=prev_leads,
                change_pct=_trend(cur_leads, prev_leads),
            ),
            TrendItem(
                label="Total Deals",
                label_ar="إجمالي الصفقات",
                value=cur_deals,
                previous_value=prev_deals,
                change_pct=_trend(cur_deals, prev_deals),
            ),
            TrendItem(
                label="Revenue (SAR)",
                label_ar="الإيرادات (ر.س)",
                value=cur_revenue,
                previous_value=prev_revenue,
                change_pct=_trend(cur_revenue, prev_revenue),
            ),
            TrendItem(
                label="Conversion Rate %",
                label_ar="معدل التحويل %",
                value=cur_conversion,
                previous_value=prev_conversion,
                change_pct=_trend(cur_conversion, prev_conversion),
            ),
        ],
    }


# ---------------------------------------------------------------------------
# 2. GET /analytics/pipeline
# ---------------------------------------------------------------------------

@router.get("/pipeline")
async def analytics_pipeline(
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    period: Period = Query(Period.monthly),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """تحليلات خط الأنابيب — Pipeline analytics."""
    d_from, d_to = _default_dates(date_from, date_to)
    prev_from, prev_to = _previous_period(d_from, d_to)
    tenant_id = current_user["tenant_id"]

    d_from_dt = datetime.combine(d_from, datetime.min.time())
    d_to_dt = datetime.combine(d_to, datetime.max.time())

    # Stage labels (English -> Arabic)
    stage_labels = {
        "new": "جديد",
        "qualified": "مؤهل",
        "proposal": "عرض سعر",
        "negotiation": "تفاوض",
        "closed_won": "مغلق - ربح",
        "closed_lost": "مغلق - خسارة",
    }

    # Group by stage: count + sum value
    stage_result = await db.execute(
        select(
            Deal.stage,
            func.count(Deal.id).label("deal_count"),
            func.coalesce(func.sum(Deal.value), 0).label("total_value"),
        )
        .where(
            Deal.tenant_id == tenant_id,
            Deal.created_at >= d_from_dt,
            Deal.created_at <= d_to_dt,
        )
        .group_by(Deal.stage)
    )
    stage_rows = stage_result.all()

    stages = []
    total_pipeline_value = 0
    total_deals = 0
    won_deals = 0
    lost_deals = 0

    for row in stage_rows:
        stage_en = row.stage or "unknown"
        stage_ar = stage_labels.get(stage_en, stage_en)
        deal_count = row.deal_count
        total_value = float(row.total_value)

        stages.append({
            "stage": stage_ar,
            "stage_en": stage_en,
            "deals": deal_count,
            "value": total_value,
        })

        total_pipeline_value += total_value
        total_deals += deal_count
        if stage_en == "closed_won":
            won_deals = deal_count
        elif stage_en == "closed_lost":
            lost_deals = deal_count

    decided = won_deals + lost_deals
    win_rate = round((won_deals / decided * 100), 1) if decided > 0 else 0.0

    # Previous period pipeline value for trend
    prev_pipeline_result = await db.execute(
        select(func.coalesce(func.sum(Deal.value), 0)).where(
            Deal.tenant_id == tenant_id,
            Deal.created_at >= datetime.combine(prev_from, datetime.min.time()),
            Deal.created_at <= datetime.combine(prev_to, datetime.max.time()),
        )
    )
    prev_pipeline_value = float(prev_pipeline_result.scalar() or 0)

    return {
        "period": period.value,
        "date_from": str(d_from),
        "date_to": str(d_to),
        "stages": stages,
        "total_pipeline_value": total_pipeline_value,
        "win_rate": win_rate,
        "currency": "SAR",
        "trend": TrendItem(
            label="Pipeline Value",
            label_ar="قيمة خط الأنابيب",
            value=total_pipeline_value,
            previous_value=prev_pipeline_value,
            change_pct=_trend(total_pipeline_value, prev_pipeline_value),
        ),
    }


# ---------------------------------------------------------------------------
# 3. GET /analytics/revenue
# ---------------------------------------------------------------------------

@router.get("/revenue")
async def analytics_revenue(
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    period: Period = Query(Period.monthly),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """تحليلات الإيرادات — Revenue analytics."""
    d_from, d_to = _default_dates(date_from, date_to)
    tenant_id = current_user["tenant_id"]

    d_from_dt = datetime.combine(d_from, datetime.min.time())
    d_to_dt = datetime.combine(d_to, datetime.max.time())

    # Monthly revenue from closed_won deals grouped by month
    monthly_result = await db.execute(
        select(
            func.to_char(Deal.closed_at, 'YYYY-MM').label("month"),
            func.coalesce(func.sum(Deal.value), 0).label("revenue"),
        )
        .where(
            Deal.tenant_id == tenant_id,
            Deal.stage == "closed_won",
            Deal.closed_at >= d_from_dt,
            Deal.closed_at <= d_to_dt,
            Deal.closed_at.isnot(None),
        )
        .group_by(func.to_char(Deal.closed_at, 'YYYY-MM'))
        .order_by(func.to_char(Deal.closed_at, 'YYYY-MM'))
    )
    monthly_rows = monthly_result.all()

    monthly_revenue = [
        TimeSeriesPoint(date=row.month, value=float(row.revenue))
        for row in monthly_rows
    ]

    # Total revenue in period
    total_rev_result = await db.execute(
        select(
            func.coalesce(func.sum(Deal.value), 0).label("total"),
            func.count(Deal.id).label("deal_count"),
        ).where(
            Deal.tenant_id == tenant_id,
            Deal.stage == "closed_won",
            Deal.closed_at >= d_from_dt,
            Deal.closed_at <= d_to_dt,
        )
    )
    total_row = total_rev_result.one()
    total_revenue = float(total_row.total)
    deal_count = total_row.deal_count
    avg_deal_size = round(total_revenue / deal_count, 2) if deal_count > 0 else 0

    # Previous period revenue for trend
    prev_from, prev_to = _previous_period(d_from, d_to)
    prev_rev_result = await db.execute(
        select(func.coalesce(func.sum(Deal.value), 0)).where(
            Deal.tenant_id == tenant_id,
            Deal.stage == "closed_won",
            Deal.closed_at >= datetime.combine(prev_from, datetime.min.time()),
            Deal.closed_at <= datetime.combine(prev_to, datetime.max.time()),
        )
    )
    prev_revenue = float(prev_rev_result.scalar() or 0)

    return {
        "period": period.value,
        "date_from": str(d_from),
        "date_to": str(d_to),
        "monthly_revenue": monthly_revenue,
        "total_revenue": total_revenue,
        "avg_deal_size": avg_deal_size,
        "deals_closed": deal_count,
        "currency": "SAR",
        "trends": {
            "revenue": TrendItem(
                label="Revenue",
                label_ar="الإيرادات",
                value=total_revenue,
                previous_value=prev_revenue,
                change_pct=_trend(total_revenue, prev_revenue),
            ),
        },
    }


# ---------------------------------------------------------------------------
# 4. GET /analytics/leads
# ---------------------------------------------------------------------------

@router.get("/leads")
async def analytics_leads(
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    period: Period = Query(Period.monthly),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """تحليلات العملاء المحتملين — Lead analytics."""
    d_from, d_to = _default_dates(date_from, date_to)
    prev_from, prev_to = _previous_period(d_from, d_to)
    tenant_id = current_user["tenant_id"]

    d_from_dt = datetime.combine(d_from, datetime.min.time())
    d_to_dt = datetime.combine(d_to, datetime.max.time())

    # Total leads in period
    total_leads_result = await db.execute(
        select(func.count(Lead.id)).where(
            Lead.tenant_id == tenant_id,
            Lead.created_at >= d_from_dt,
            Lead.created_at <= d_to_dt,
        )
    )
    total_leads = total_leads_result.scalar() or 0

    # New leads today
    today_start = datetime.combine(date.today(), datetime.min.time())
    today_end = datetime.combine(date.today(), datetime.max.time())
    new_today_result = await db.execute(
        select(func.count(Lead.id)).where(
            Lead.tenant_id == tenant_id,
            Lead.created_at >= today_start,
            Lead.created_at <= today_end,
        )
    )
    new_leads_today = new_today_result.scalar() or 0

    # Previous period leads for trend
    prev_leads_result = await db.execute(
        select(func.count(Lead.id)).where(
            Lead.tenant_id == tenant_id,
            Lead.created_at >= datetime.combine(prev_from, datetime.min.time()),
            Lead.created_at <= datetime.combine(prev_to, datetime.max.time()),
        )
    )
    prev_leads = prev_leads_result.scalar() or 0

    # By source
    source_result = await db.execute(
        select(
            Lead.source,
            func.count(Lead.id).label("count"),
        )
        .where(
            Lead.tenant_id == tenant_id,
            Lead.created_at >= d_from_dt,
            Lead.created_at <= d_to_dt,
        )
        .group_by(Lead.source)
        .order_by(func.count(Lead.id).desc())
    )
    source_rows = source_result.all()

    by_source = []
    for row in source_rows:
        pct = round((row.count / total_leads * 100), 1) if total_leads > 0 else 0.0
        by_source.append({
            "source": row.source or "unknown",
            "count": row.count,
            "pct": pct,
        })

    # By status
    status_result = await db.execute(
        select(
            Lead.status,
            func.count(Lead.id).label("count"),
        )
        .where(
            Lead.tenant_id == tenant_id,
            Lead.created_at >= d_from_dt,
            Lead.created_at <= d_to_dt,
        )
        .group_by(Lead.status)
        .order_by(func.count(Lead.id).desc())
    )
    status_rows = status_result.all()

    status_labels = {
        "new": "جديد",
        "contacted": "تم التواصل",
        "qualified": "مؤهل",
        "unqualified": "غير مؤهل",
        "converted": "محول",
        "proposal": "عرض سعر",
        "won": "ربح",
        "lost": "خسارة",
    }

    by_status = [
        {
            "status": status_labels.get(row.status, row.status or "unknown"),
            "status_en": row.status or "unknown",
            "count": row.count,
        }
        for row in status_rows
    ]

    # By industry (from extra_data JSONB -> 'industry')
    industry_result = await db.execute(
        select(
            Lead.extra_data["industry"].astext.label("industry"),
            func.count(Lead.id).label("count"),
        )
        .where(
            Lead.tenant_id == tenant_id,
            Lead.created_at >= d_from_dt,
            Lead.created_at <= d_to_dt,
            Lead.extra_data["industry"].astext.isnot(None),
            Lead.extra_data["industry"].astext != "null",
        )
        .group_by(Lead.extra_data["industry"].astext)
        .order_by(func.count(Lead.id).desc())
    )
    industry_rows = industry_result.all()

    by_industry = [
        {"industry": row.industry, "count": row.count}
        for row in industry_rows
    ]

    return {
        "period": period.value,
        "date_from": str(d_from),
        "date_to": str(d_to),
        "total_leads": total_leads,
        "new_leads_today": new_leads_today,
        "by_source": by_source,
        "by_status": by_status,
        "by_industry": by_industry,
        "trend": TrendItem(
            label="New Leads",
            label_ar="عملاء محتملون جدد",
            value=total_leads,
            previous_value=prev_leads,
            change_pct=_trend(total_leads, prev_leads),
        ),
    }


# ---------------------------------------------------------------------------
# 5. GET /analytics/team
# ---------------------------------------------------------------------------

@router.get("/team")
async def analytics_team(
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    period: Period = Query(Period.monthly),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """أداء الفريق — Team performance analytics."""
    d_from, d_to = _default_dates(date_from, date_to)
    tenant_id = current_user["tenant_id"]

    d_from_dt = datetime.combine(d_from, datetime.min.time())
    d_to_dt = datetime.combine(d_to, datetime.max.time())

    # Deals per assigned user
    team_result = await db.execute(
        select(
            Deal.assigned_to,
            func.count(Deal.id).label("total_deals"),
            func.count(case((Deal.stage == "closed_won", Deal.id))).label("deals_closed"),
            func.coalesce(
                func.sum(case((Deal.stage == "closed_won", Deal.value), else_=0)),
                0,
            ).label("revenue"),
        )
        .where(
            Deal.tenant_id == tenant_id,
            Deal.created_at >= d_from_dt,
            Deal.created_at <= d_to_dt,
            Deal.assigned_to.isnot(None),
        )
        .group_by(Deal.assigned_to)
        .order_by(func.coalesce(
            func.sum(case((Deal.stage == "closed_won", Deal.value), else_=0)),
            0,
        ).desc())
    )
    team_rows = team_result.all()

    total_closed = 0
    total_revenue = 0.0
    members = []

    for row in team_rows:
        revenue = float(row.revenue)
        members.append({
            "user_id": str(row.assigned_to),
            "deals_total": row.total_deals,
            "deals_closed": row.deals_closed,
            "revenue": revenue,
        })
        total_closed += row.deals_closed
        total_revenue += revenue

    # Previous period for trend
    prev_from, prev_to = _previous_period(d_from, d_to)
    prev_rev_result = await db.execute(
        select(func.coalesce(func.sum(Deal.value), 0)).where(
            Deal.tenant_id == tenant_id,
            Deal.stage == "closed_won",
            Deal.created_at >= datetime.combine(prev_from, datetime.min.time()),
            Deal.created_at <= datetime.combine(prev_to, datetime.max.time()),
        )
    )
    prev_revenue = float(prev_rev_result.scalar() or 0)

    return {
        "period": period.value,
        "date_from": str(d_from),
        "date_to": str(d_to),
        "team": members,
        "totals": {
            "deals_closed": total_closed,
            "revenue": total_revenue,
        },
        "currency": "SAR",
        "trend": TrendItem(
            label="Team Revenue",
            label_ar="إيرادات الفريق",
            value=total_revenue,
            previous_value=prev_revenue,
            change_pct=_trend(total_revenue, prev_revenue),
        ),
    }


# ---------------------------------------------------------------------------
# 6. GET /analytics/campaigns
# ---------------------------------------------------------------------------

@router.get("/campaigns")
async def analytics_campaigns(
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    period: Period = Query(Period.monthly),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """عائد الحملات — Campaign ROI analytics."""
    d_from, d_to = _default_dates(date_from, date_to)
    tenant_id = current_user["tenant_id"]

    d_from_dt = datetime.combine(d_from, datetime.min.time())
    d_to_dt = datetime.combine(d_to, datetime.max.time())

    # Get campaigns with their metrics
    campaigns_result = await db.execute(
        select(Campaign)
        .where(
            Campaign.tenant_id == tenant_id,
            Campaign.created_at >= d_from_dt,
            Campaign.created_at <= d_to_dt,
        )
        .order_by(Campaign.created_at.desc())
    )
    campaigns = campaigns_result.scalars().all()

    campaign_list = []
    total_spend = 0.0
    total_leads = 0
    total_revenue = 0.0

    for c in campaigns:
        budget = float(c.budget) if c.budget else 0
        revenue = float(c.revenue_generated) if c.revenue_generated else 0
        leads = c.leads_generated or 0
        cpl = float(c.cost_per_lead) if c.cost_per_lead else (
            round(budget / leads, 2) if leads > 0 else 0
        )
        roi = round((revenue - budget) / budget * 100, 1) if budget > 0 else 0.0

        campaign_list.append({
            "campaign_id": str(c.id),
            "name": c.name,
            "channel": c.channel,
            "spend": budget,
            "leads": leads,
            "deals_closed": c.deals_closed or 0,
            "revenue": revenue,
            "cpl": cpl,
            "roi_pct": roi,
        })

        total_spend += budget
        total_leads += leads
        total_revenue += revenue

    # By channel aggregation
    channel_result = await db.execute(
        select(
            Campaign.channel,
            func.coalesce(func.sum(Campaign.leads_generated), 0).label("leads"),
            func.coalesce(func.sum(Campaign.budget), 0).label("spend"),
            func.coalesce(func.sum(Campaign.revenue_generated), 0).label("revenue"),
        )
        .where(
            Campaign.tenant_id == tenant_id,
            Campaign.created_at >= d_from_dt,
            Campaign.created_at <= d_to_dt,
        )
        .group_by(Campaign.channel)
        .order_by(func.coalesce(func.sum(Campaign.revenue_generated), 0).desc())
    )
    channel_rows = channel_result.all()

    by_channel = [
        {
            "channel": row.channel or "unknown",
            "leads": int(row.leads),
            "spend": float(row.spend),
            "revenue": float(row.revenue),
        }
        for row in channel_rows
    ]

    avg_cpl = round(total_spend / total_leads, 2) if total_leads > 0 else 0
    overall_roi = round((total_revenue - total_spend) / total_spend * 100, 1) if total_spend > 0 else 0.0

    return {
        "period": period.value,
        "date_from": str(d_from),
        "date_to": str(d_to),
        "campaigns": campaign_list,
        "by_channel": by_channel,
        "totals": {
            "total_spend": total_spend,
            "total_leads": total_leads,
            "total_revenue": total_revenue,
            "avg_cpl": avg_cpl,
            "overall_roi_pct": overall_roi,
        },
        "currency": "SAR",
    }


# ---------------------------------------------------------------------------
# 7. GET /analytics/export
# ---------------------------------------------------------------------------

@router.get("/export")
async def analytics_export(
    report_type: str = Query(
        "overview",
        description="نوع التقرير: overview, pipeline, leads, campaigns",
    ),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """تصدير التقارير — Export analytics report as CSV."""
    d_from, d_to = _default_dates(date_from, date_to)
    tenant_id = current_user["tenant_id"]

    d_from_dt = datetime.combine(d_from, datetime.min.time())
    d_to_dt = datetime.combine(d_to, datetime.max.time())

    generators = {
        "overview": _csv_overview,
        "pipeline": _csv_pipeline,
        "leads": _csv_leads,
        "campaigns": _csv_campaigns,
    }

    generator = generators.get(report_type, _csv_overview)
    content = await generator(db, tenant_id, d_from_dt, d_to_dt)

    return StreamingResponse(
        iter([content]),
        media_type="text/csv; charset=utf-8-sig",
        headers={
            "Content-Disposition": (
                f'attachment; filename="dealix_{report_type}_{d_from}_{d_to}.csv"'
            ),
        },
    )


# ---------------------------------------------------------------------------
# CSV generators (real DB queries)
# ---------------------------------------------------------------------------

async def _csv_overview(
    db: AsyncSession, tenant_id: str, d_from: datetime, d_to: datetime
) -> str:
    leads_result = await db.execute(
        select(func.count(Lead.id)).where(
            Lead.tenant_id == tenant_id,
            Lead.created_at >= d_from,
            Lead.created_at <= d_to,
        )
    )
    total_leads = leads_result.scalar() or 0

    deals_result = await db.execute(
        select(func.count(Deal.id)).where(
            Deal.tenant_id == tenant_id,
            Deal.created_at >= d_from,
            Deal.created_at <= d_to,
        )
    )
    total_deals = deals_result.scalar() or 0

    rev_result = await db.execute(
        select(func.coalesce(func.sum(Deal.value), 0)).where(
            Deal.tenant_id == tenant_id,
            Deal.stage == "closed_won",
            Deal.created_at >= d_from,
            Deal.created_at <= d_to,
        )
    )
    total_revenue = float(rev_result.scalar() or 0)

    conversion = round((total_deals / total_leads * 100), 1) if total_leads > 0 else 0

    buf = StringIO()
    buf.write("المؤشر,القيمة\n")
    buf.write(f"إجمالي العملاء المحتملين,{total_leads}\n")
    buf.write(f"إجمالي الصفقات,{total_deals}\n")
    buf.write(f"الإيرادات (ر.س),{total_revenue}\n")
    buf.write(f"معدل التحويل %,{conversion}\n")
    return buf.getvalue()


async def _csv_pipeline(
    db: AsyncSession, tenant_id: str, d_from: datetime, d_to: datetime
) -> str:
    stage_result = await db.execute(
        select(
            Deal.stage,
            func.count(Deal.id).label("deal_count"),
            func.coalesce(func.sum(Deal.value), 0).label("total_value"),
        )
        .where(
            Deal.tenant_id == tenant_id,
            Deal.created_at >= d_from,
            Deal.created_at <= d_to,
        )
        .group_by(Deal.stage)
    )
    rows = stage_result.all()

    buf = StringIO()
    buf.write("المرحلة,عدد الصفقات,القيمة (ر.س)\n")
    for row in rows:
        buf.write(f"{row.stage},{row.deal_count},{float(row.total_value)}\n")
    return buf.getvalue()


async def _csv_leads(
    db: AsyncSession, tenant_id: str, d_from: datetime, d_to: datetime
) -> str:
    total_result = await db.execute(
        select(func.count(Lead.id)).where(
            Lead.tenant_id == tenant_id,
            Lead.created_at >= d_from,
            Lead.created_at <= d_to,
        )
    )
    total = total_result.scalar() or 0

    source_result = await db.execute(
        select(
            Lead.source,
            func.count(Lead.id).label("count"),
        )
        .where(
            Lead.tenant_id == tenant_id,
            Lead.created_at >= d_from,
            Lead.created_at <= d_to,
        )
        .group_by(Lead.source)
        .order_by(func.count(Lead.id).desc())
    )
    rows = source_result.all()

    buf = StringIO()
    buf.write("المصدر,العدد,النسبة %\n")
    for row in rows:
        pct = round((row.count / total * 100), 1) if total > 0 else 0
        buf.write(f"{row.source},{row.count},{pct}\n")
    return buf.getvalue()


async def _csv_campaigns(
    db: AsyncSession, tenant_id: str, d_from: datetime, d_to: datetime
) -> str:
    campaigns_result = await db.execute(
        select(Campaign)
        .where(
            Campaign.tenant_id == tenant_id,
            Campaign.created_at >= d_from,
            Campaign.created_at <= d_to,
        )
        .order_by(Campaign.created_at.desc())
    )
    campaigns = campaigns_result.scalars().all()

    buf = StringIO()
    buf.write("الحملة,القناة,الميزانية (ر.س),العملاء المحتملين,الإيرادات (ر.س)\n")
    for c in campaigns:
        budget = float(c.budget) if c.budget else 0
        revenue = float(c.revenue_generated) if c.revenue_generated else 0
        leads = c.leads_generated or 0
        buf.write(f"{c.name},{c.channel},{budget},{leads},{revenue}\n")
    return buf.getvalue()
