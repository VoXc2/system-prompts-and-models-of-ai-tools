"""Analytics and reporting API for Dealix CRM."""
from datetime import datetime, date, timedelta
from typing import Optional
from enum import Enum
from io import StringIO

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.api.v1.deps import get_current_active_user

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


# ---------------------------------------------------------------------------
# 1. GET /analytics/overview
# ---------------------------------------------------------------------------

@router.get("/overview")
async def analytics_overview(
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    period: Period = Query(Period.monthly),
    current_user: dict = Depends(get_current_active_user),
):
    """لوحة المؤشرات الرئيسية — Dashboard overview KPIs."""
    d_from, d_to = _default_dates(date_from, date_to)
    return {
        "period": period.value,
        "date_from": str(d_from),
        "date_to": str(d_to),
        "tenant_id": current_user.get("tenant_id"),
        "kpis": [
            TrendItem(
                label="Total Leads",
                label_ar="إجمالي العملاء المحتملين",
                value=1_247,
                previous_value=1_103,
                change_pct=_trend(1_247, 1_103),
            ),
            TrendItem(
                label="Total Deals",
                label_ar="إجمالي الصفقات",
                value=342,
                previous_value=298,
                change_pct=_trend(342, 298),
            ),
            TrendItem(
                label="Revenue (SAR)",
                label_ar="الإيرادات (ر.س)",
                value=487_500.0,
                previous_value=412_300.0,
                change_pct=_trend(487_500, 412_300),
            ),
            TrendItem(
                label="Conversion Rate %",
                label_ar="معدل التحويل %",
                value=27.4,
                previous_value=24.1,
                change_pct=_trend(27.4, 24.1),
            ),
            TrendItem(
                label="Avg Response Time (min)",
                label_ar="متوسط وقت الاستجابة (دقيقة)",
                value=4.2,
                previous_value=6.8,
                change_pct=_trend(4.2, 6.8),
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
    current_user: dict = Depends(get_current_active_user),
):
    """تحليلات خط الأنابيب — Pipeline analytics."""
    d_from, d_to = _default_dates(date_from, date_to)

    stages = [
        {"stage": "جديد", "stage_en": "new", "deals": 185, "value": 740_000, "avg_days": 2.1, "conversion_pct": 72.0},
        {"stage": "مؤهل", "stage_en": "qualified", "deals": 133, "value": 532_000, "avg_days": 5.4, "conversion_pct": 61.0},
        {"stage": "عرض سعر", "stage_en": "proposal", "deals": 81, "value": 405_000, "avg_days": 7.2, "conversion_pct": 54.0},
        {"stage": "تفاوض", "stage_en": "negotiation", "deals": 44, "value": 308_000, "avg_days": 9.8, "conversion_pct": 68.0},
        {"stage": "مغلق - ربح", "stage_en": "closed_won", "deals": 30, "value": 487_500, "avg_days": 0, "conversion_pct": 100.0},
        {"stage": "مغلق - خسارة", "stage_en": "closed_lost", "deals": 14, "value": 0, "avg_days": 0, "conversion_pct": 0.0},
    ]

    return {
        "period": period.value,
        "date_from": str(d_from),
        "date_to": str(d_to),
        "stages": stages,
        "total_pipeline_value": 2_472_500,
        "avg_deal_cycle_days": 24.5,
        "win_rate": 68.2,
        "currency": "SAR",
        "trend": TrendItem(
            label="Pipeline Value",
            label_ar="قيمة خط الأنابيب",
            value=2_472_500,
            previous_value=2_180_000,
            change_pct=_trend(2_472_500, 2_180_000),
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
    current_user: dict = Depends(get_current_active_user),
):
    """تحليلات الإيرادات — Revenue analytics."""
    d_from, d_to = _default_dates(date_from, date_to)

    monthly_revenue = [
        TimeSeriesPoint(date="2025-10", value=312_400),
        TimeSeriesPoint(date="2025-11", value=345_800),
        TimeSeriesPoint(date="2025-12", value=412_300),
        TimeSeriesPoint(date="2026-01", value=438_100),
        TimeSeriesPoint(date="2026-02", value=462_700),
        TimeSeriesPoint(date="2026-03", value=487_500),
    ]

    return {
        "period": period.value,
        "date_from": str(d_from),
        "date_to": str(d_to),
        "monthly_revenue": monthly_revenue,
        "mrr": 487_500,
        "arr": 5_850_000,
        "growth_rate_pct": 5.4,
        "avg_deal_size": 16_250,
        "currency": "SAR",
        "revenue_by_plan": [
            {"plan": "أساسي", "plan_en": "basic", "revenue": 97_500, "customers": 65},
            {"plan": "احترافي", "plan_en": "professional", "revenue": 195_000, "customers": 39},
            {"plan": "مؤسسي", "plan_en": "enterprise", "revenue": 195_000, "customers": 13},
        ],
        "trends": {
            "mrr": TrendItem(
                label="MRR",
                label_ar="الإيراد الشهري المتكرر",
                value=487_500,
                previous_value=462_700,
                change_pct=_trend(487_500, 462_700),
            ),
            "arr": TrendItem(
                label="ARR",
                label_ar="الإيراد السنوي المتكرر",
                value=5_850_000,
                previous_value=5_552_400,
                change_pct=_trend(5_850_000, 5_552_400),
            ),
            "growth_rate": TrendItem(
                label="Growth Rate",
                label_ar="معدل النمو",
                value=5.4,
                previous_value=4.8,
                change_pct=_trend(5.4, 4.8),
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
    current_user: dict = Depends(get_current_active_user),
):
    """تحليلات العملاء المحتملين — Lead analytics."""
    d_from, d_to = _default_dates(date_from, date_to)

    return {
        "period": period.value,
        "date_from": str(d_from),
        "date_to": str(d_to),
        "total_leads": 1_247,
        "new_leads_today": 18,
        "by_source": [
            {"source": "واتساب", "source_en": "whatsapp", "count": 412, "pct": 33.0, "conversion_rate": 31.2},
            {"source": "موقع إلكتروني", "source_en": "website", "count": 324, "pct": 26.0, "conversion_rate": 24.8},
            {"source": "إحالة", "source_en": "referral", "count": 198, "pct": 15.9, "conversion_rate": 38.4},
            {"source": "إعلانات قوقل", "source_en": "google_ads", "count": 162, "pct": 13.0, "conversion_rate": 19.6},
            {"source": "وسائل التواصل", "source_en": "social_media", "count": 151, "pct": 12.1, "conversion_rate": 15.3},
        ],
        "by_status": [
            {"status": "جديد", "status_en": "new", "count": 287},
            {"status": "تم التواصل", "status_en": "contacted", "count": 394},
            {"status": "مؤهل", "status_en": "qualified", "count": 312},
            {"status": "غير مؤهل", "status_en": "unqualified", "count": 154},
            {"status": "محول", "status_en": "converted", "count": 100},
        ],
        "by_industry": [
            {"industry": "تجارة إلكترونية", "industry_en": "ecommerce", "count": 298},
            {"industry": "عقارات", "industry_en": "real_estate", "count": 215},
            {"industry": "خدمات مهنية", "industry_en": "professional_services", "count": 187},
            {"industry": "تقنية معلومات", "industry_en": "it", "count": 164},
            {"industry": "مطاعم وضيافة", "industry_en": "hospitality", "count": 143},
            {"industry": "أخرى", "industry_en": "other", "count": 240},
        ],
        "conversion_funnel": [
            {"stage": "زائر", "stage_en": "visitor", "count": 8_540},
            {"stage": "عميل محتمل", "stage_en": "lead", "count": 1_247},
            {"stage": "مؤهل", "stage_en": "qualified", "count": 312},
            {"stage": "فرصة", "stage_en": "opportunity", "count": 133},
            {"stage": "عميل", "stage_en": "customer", "count": 30},
        ],
        "trend": TrendItem(
            label="New Leads",
            label_ar="عملاء محتملون جدد",
            value=1_247,
            previous_value=1_103,
            change_pct=_trend(1_247, 1_103),
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
    current_user: dict = Depends(get_current_active_user),
):
    """أداء الفريق — Team performance analytics."""
    d_from, d_to = _default_dates(date_from, date_to)

    members = [
        {
            "user_id": "usr_001",
            "name": "أحمد الغامدي",
            "role": "مدير مبيعات",
            "deals_closed": 12,
            "revenue": 186_000,
            "avg_response_min": 3.1,
            "lead_conversion_pct": 34.2,
            "active_deals": 8,
        },
        {
            "user_id": "usr_002",
            "name": "سارة القحطاني",
            "role": "مندوبة مبيعات",
            "deals_closed": 9,
            "revenue": 142_500,
            "avg_response_min": 4.7,
            "lead_conversion_pct": 28.6,
            "active_deals": 11,
        },
        {
            "user_id": "usr_003",
            "name": "محمد العتيبي",
            "role": "مندوب مبيعات",
            "deals_closed": 6,
            "revenue": 97_000,
            "avg_response_min": 5.3,
            "lead_conversion_pct": 22.1,
            "active_deals": 14,
        },
        {
            "user_id": "usr_004",
            "name": "نورة الشمري",
            "role": "مندوبة مبيعات",
            "deals_closed": 3,
            "revenue": 62_000,
            "avg_response_min": 6.1,
            "lead_conversion_pct": 18.5,
            "active_deals": 7,
        },
    ]

    return {
        "period": period.value,
        "date_from": str(d_from),
        "date_to": str(d_to),
        "team": members,
        "totals": {
            "deals_closed": 30,
            "revenue": 487_500,
            "avg_response_min": 4.8,
            "avg_conversion_pct": 25.9,
        },
        "leaderboard": {
            "by_revenue": ["usr_001", "usr_002", "usr_003", "usr_004"],
            "by_deals_closed": ["usr_001", "usr_002", "usr_003", "usr_004"],
            "by_response_time": ["usr_001", "usr_002", "usr_003", "usr_004"],
        },
        "currency": "SAR",
        "trend": TrendItem(
            label="Team Revenue",
            label_ar="إيرادات الفريق",
            value=487_500,
            previous_value=412_300,
            change_pct=_trend(487_500, 412_300),
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
    current_user: dict = Depends(get_current_active_user),
):
    """عائد الحملات — Campaign ROI analytics."""
    d_from, d_to = _default_dates(date_from, date_to)

    campaigns = [
        {
            "campaign_id": "cmp_001",
            "name": "حملة رمضان ٢٠٢٦",
            "channel": "واتساب",
            "spend": 15_000,
            "leads": 312,
            "conversions": 47,
            "revenue": 188_000,
            "cpl": 48.1,
            "conversion_pct": 15.1,
            "roi_pct": 1153.3,
        },
        {
            "campaign_id": "cmp_002",
            "name": "إعلانات قوقل - عقارات",
            "channel": "إعلانات قوقل",
            "spend": 22_000,
            "leads": 162,
            "conversions": 21,
            "revenue": 147_000,
            "cpl": 135.8,
            "conversion_pct": 13.0,
            "roi_pct": 568.2,
        },
        {
            "campaign_id": "cmp_003",
            "name": "حملة انستقرام - تجارة إلكترونية",
            "channel": "وسائل التواصل",
            "spend": 8_500,
            "leads": 151,
            "conversions": 14,
            "revenue": 56_000,
            "cpl": 56.3,
            "conversion_pct": 9.3,
            "roi_pct": 558.8,
        },
    ]

    return {
        "period": period.value,
        "date_from": str(d_from),
        "date_to": str(d_to),
        "campaigns": campaigns,
        "by_channel": [
            {"channel": "واتساب", "leads": 312, "spend": 15_000, "revenue": 188_000},
            {"channel": "إعلانات قوقل", "leads": 162, "spend": 22_000, "revenue": 147_000},
            {"channel": "وسائل التواصل", "leads": 151, "spend": 8_500, "revenue": 56_000},
        ],
        "totals": {
            "total_spend": 45_500,
            "total_leads": 625,
            "total_conversions": 82,
            "total_revenue": 391_000,
            "avg_cpl": 72.8,
            "overall_roi_pct": 759.3,
        },
        "currency": "SAR",
        "trend": TrendItem(
            label="Campaign ROI",
            label_ar="عائد الحملات",
            value=759.3,
            previous_value=612.5,
            change_pct=_trend(759.3, 612.5),
        ),
    }


# ---------------------------------------------------------------------------
# 7. GET /analytics/ai
# ---------------------------------------------------------------------------

@router.get("/ai")
async def analytics_ai(
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    period: Period = Query(Period.monthly),
    current_user: dict = Depends(get_current_active_user),
):
    """أداء الوكيل الذكي — AI agent performance analytics."""
    d_from, d_to = _default_dates(date_from, date_to)

    return {
        "period": period.value,
        "date_from": str(d_from),
        "date_to": str(d_to),
        "messages": {
            "total_sent": 8_430,
            "auto_replies": 6_218,
            "auto_reply_pct": 73.8,
            "avg_response_sec": 2.4,
        },
        "qualification": {
            "leads_scored": 1_247,
            "accuracy_pct": 89.3,
            "false_positive_pct": 4.2,
            "false_negative_pct": 6.5,
        },
        "sentiment": {
            "positive_pct": 62.4,
            "neutral_pct": 28.1,
            "negative_pct": 9.5,
            "avg_satisfaction_score": 4.3,
        },
        "handoffs": {
            "total_handoffs": 1_847,
            "avg_handoff_time_sec": 18.6,
            "successful_pct": 94.2,
        },
        "by_type": [
            {"type": "رد تلقائي", "type_en": "auto_reply", "count": 6_218},
            {"type": "تأهيل عميل", "type_en": "qualification", "count": 1_247},
            {"type": "معالجة اعتراض", "type_en": "objection_handling", "count": 483},
            {"type": "رسالة متابعة", "type_en": "follow_up", "count": 312},
            {"type": "تحليل مشاعر", "type_en": "sentiment_analysis", "count": 170},
        ],
        "tokens_used": 2_340_000,
        "cost_estimate_sar": 842,
        "trends": {
            "auto_reply_rate": TrendItem(
                label="Auto-reply Rate",
                label_ar="معدل الرد التلقائي",
                value=73.8,
                previous_value=68.2,
                change_pct=_trend(73.8, 68.2),
            ),
            "qualification_accuracy": TrendItem(
                label="Qualification Accuracy",
                label_ar="دقة التأهيل",
                value=89.3,
                previous_value=85.7,
                change_pct=_trend(89.3, 85.7),
            ),
            "satisfaction": TrendItem(
                label="Satisfaction Score",
                label_ar="درجة الرضا",
                value=4.3,
                previous_value=4.1,
                change_pct=_trend(4.3, 4.1),
            ),
        },
    }


# ---------------------------------------------------------------------------
# 8. GET /analytics/voice
# ---------------------------------------------------------------------------

@router.get("/voice")
async def analytics_voice(
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    period: Period = Query(Period.monthly),
    current_user: dict = Depends(get_current_active_user),
):
    """تحليلات المكالمات الذكية — Voice AI analytics."""
    d_from, d_to = _default_dates(date_from, date_to)

    return {
        "period": period.value,
        "date_from": str(d_from),
        "date_to": str(d_to),
        "calls": {
            "total": 2_156,
            "outbound": 1_489,
            "inbound": 667,
            "answered_pct": 78.4,
        },
        "duration": {
            "avg_seconds": 187,
            "total_minutes": 6_720,
            "median_seconds": 142,
        },
        "qualification": {
            "qualified_pct": 41.3,
            "meeting_booked_pct": 18.7,
            "callback_requested_pct": 12.4,
        },
        "by_disposition": [
            {"disposition": "مؤهل", "disposition_en": "qualified", "count": 891},
            {"disposition": "غير مهتم", "disposition_en": "not_interested", "count": 518},
            {"disposition": "طلب معاودة الاتصال", "disposition_en": "callback", "count": 267},
            {"disposition": "لم يرد", "disposition_en": "no_answer", "count": 324},
            {"disposition": "تم التحويل لموظف", "disposition_en": "handoff", "count": 156},
        ],
        "cost": {
            "total_sar": 8_624,
            "per_call_sar": 4.0,
            "per_minute_sar": 1.28,
        },
        "daily_volume": [
            TimeSeriesPoint(date="2026-03-22", value=74),
            TimeSeriesPoint(date="2026-03-23", value=82),
            TimeSeriesPoint(date="2026-03-24", value=91),
            TimeSeriesPoint(date="2026-03-25", value=68),
            TimeSeriesPoint(date="2026-03-26", value=88),
            TimeSeriesPoint(date="2026-03-27", value=79),
            TimeSeriesPoint(date="2026-03-28", value=63),
        ],
        "currency": "SAR",
        "trends": {
            "calls": TrendItem(
                label="Total Calls",
                label_ar="إجمالي المكالمات",
                value=2_156,
                previous_value=1_834,
                change_pct=_trend(2_156, 1_834),
            ),
            "qualification_rate": TrendItem(
                label="Qualification Rate",
                label_ar="معدل التأهيل",
                value=41.3,
                previous_value=37.8,
                change_pct=_trend(41.3, 37.8),
            ),
            "cost_per_call": TrendItem(
                label="Cost per Call",
                label_ar="تكلفة المكالمة",
                value=4.0,
                previous_value=4.7,
                change_pct=_trend(4.0, 4.7),
            ),
        },
    }


# ---------------------------------------------------------------------------
# 9. GET /analytics/export
# ---------------------------------------------------------------------------

@router.get("/export")
async def analytics_export(
    report_type: str = Query(
        "overview",
        description="نوع التقرير: overview, pipeline, revenue, leads, team, campaigns, ai, voice",
    ),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    current_user: dict = Depends(get_current_active_user),
):
    """تصدير التقارير — Export analytics report as CSV."""
    d_from, d_to = _default_dates(date_from, date_to)

    csv_generators = {
        "overview": _csv_overview,
        "pipeline": _csv_pipeline,
        "revenue": _csv_revenue,
        "leads": _csv_leads,
        "team": _csv_team,
        "campaigns": _csv_campaigns,
        "ai": _csv_ai,
        "voice": _csv_voice,
    }

    generator = csv_generators.get(report_type, _csv_overview)
    content = generator(d_from, d_to)

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
# CSV generators (realistic mock data with Arabic headers)
# ---------------------------------------------------------------------------

def _csv_overview(d_from: date, d_to: date) -> str:
    buf = StringIO()
    buf.write("المؤشر,القيمة الحالية,القيمة السابقة,التغيير %\n")
    buf.write("إجمالي العملاء المحتملين,1247,1103,13.1\n")
    buf.write("إجمالي الصفقات,342,298,14.8\n")
    buf.write("الإيرادات (ر.س),487500,412300,18.2\n")
    buf.write("معدل التحويل %,27.4,24.1,13.7\n")
    buf.write("متوسط وقت الاستجابة (دقيقة),4.2,6.8,-38.2\n")
    return buf.getvalue()


def _csv_pipeline(d_from: date, d_to: date) -> str:
    buf = StringIO()
    buf.write("المرحلة,عدد الصفقات,القيمة (ر.س),متوسط الأيام,معدل التحويل %\n")
    buf.write("جديد,185,740000,2.1,72.0\n")
    buf.write("مؤهل,133,532000,5.4,61.0\n")
    buf.write("عرض سعر,81,405000,7.2,54.0\n")
    buf.write("تفاوض,44,308000,9.8,68.0\n")
    buf.write("مغلق - ربح,30,487500,0,100.0\n")
    buf.write("مغلق - خسارة,14,0,0,0.0\n")
    return buf.getvalue()


def _csv_revenue(d_from: date, d_to: date) -> str:
    buf = StringIO()
    buf.write("الشهر,الإيرادات (ر.س)\n")
    buf.write("2025-10,312400\n")
    buf.write("2025-11,345800\n")
    buf.write("2025-12,412300\n")
    buf.write("2026-01,438100\n")
    buf.write("2026-02,462700\n")
    buf.write("2026-03,487500\n")
    return buf.getvalue()


def _csv_leads(d_from: date, d_to: date) -> str:
    buf = StringIO()
    buf.write("المصدر,العدد,النسبة %,معدل التحويل %\n")
    buf.write("واتساب,412,33.0,31.2\n")
    buf.write("موقع إلكتروني,324,26.0,24.8\n")
    buf.write("إحالة,198,15.9,38.4\n")
    buf.write("إعلانات قوقل,162,13.0,19.6\n")
    buf.write("وسائل التواصل,151,12.1,15.3\n")
    return buf.getvalue()


def _csv_team(d_from: date, d_to: date) -> str:
    buf = StringIO()
    buf.write("الاسم,الدور,الصفقات المغلقة,الإيرادات (ر.س),متوسط الاستجابة (دقيقة),معدل التحويل %\n")
    buf.write("أحمد الغامدي,مدير مبيعات,12,186000,3.1,34.2\n")
    buf.write("سارة القحطاني,مندوبة مبيعات,9,142500,4.7,28.6\n")
    buf.write("محمد العتيبي,مندوب مبيعات,6,97000,5.3,22.1\n")
    buf.write("نورة الشمري,مندوبة مبيعات,3,62000,6.1,18.5\n")
    return buf.getvalue()


def _csv_campaigns(d_from: date, d_to: date) -> str:
    buf = StringIO()
    buf.write("الحملة,القناة,الإنفاق (ر.س),العملاء المحتملين,التحويلات,الإيرادات (ر.س),CPL,ROI %\n")
    buf.write("حملة رمضان ٢٠٢٦,واتساب,15000,312,47,188000,48.1,1153.3\n")
    buf.write("إعلانات قوقل - عقارات,إعلانات قوقل,22000,162,21,147000,135.8,568.2\n")
    buf.write("حملة انستقرام - تجارة إلكترونية,وسائل التواصل,8500,151,14,56000,56.3,558.8\n")
    return buf.getvalue()


def _csv_ai(d_from: date, d_to: date) -> str:
    buf = StringIO()
    buf.write("المؤشر,القيمة\n")
    buf.write("إجمالي الرسائل,8430\n")
    buf.write("الردود التلقائية,6218\n")
    buf.write("نسبة الرد التلقائي %,73.8\n")
    buf.write("دقة التأهيل %,89.3\n")
    buf.write("المشاعر الإيجابية %,62.4\n")
    buf.write("المشاعر المحايدة %,28.1\n")
    buf.write("المشاعر السلبية %,9.5\n")
    buf.write("التكلفة التقديرية (ر.س),842\n")
    return buf.getvalue()


def _csv_voice(d_from: date, d_to: date) -> str:
    buf = StringIO()
    buf.write("المؤشر,القيمة\n")
    buf.write("إجمالي المكالمات,2156\n")
    buf.write("المكالمات الصادرة,1489\n")
    buf.write("المكالمات الواردة,667\n")
    buf.write("نسبة الرد %,78.4\n")
    buf.write("متوسط المدة (ثانية),187\n")
    buf.write("معدل التأهيل %,41.3\n")
    buf.write("التكلفة الإجمالية (ر.س),8624\n")
    buf.write("تكلفة المكالمة (ر.س),4.0\n")
    return buf.getvalue()
