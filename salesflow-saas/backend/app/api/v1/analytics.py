"""Analytics & Reporting API endpoints."""
from fastapi import APIRouter, Depends, Query
from typing import Optional
from datetime import datetime, timezone, timedelta
from app.api.v1.deps import get_current_user, get_db

router = APIRouter()


def _date_range(date_from: Optional[str], date_to: Optional[str]):
    """Parse date range or default to last 30 days."""
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=30)
    if date_from:
        try:
            start = datetime.fromisoformat(date_from)
        except ValueError:
            pass
    if date_to:
        try:
            end = datetime.fromisoformat(date_to)
        except ValueError:
            pass
    return start, end


@router.get("/overview")
async def get_overview(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
):
    """Dashboard overview — key metrics at a glance."""
    return {
        "period": {"from": date_from, "to": date_to},
        "metrics": {
            "total_leads": {"value": 0, "change_pct": 0, "label": "إجمالي العملاء المحتملين"},
            "active_deals": {"value": 0, "change_pct": 0, "label": "الصفقات النشطة"},
            "deals_won": {"value": 0, "change_pct": 0, "label": "الصفقات المغلقة"},
            "revenue": {"value": 0, "change_pct": 0, "label": "الإيرادات (ر.س)", "currency": "SAR"},
            "conversion_rate": {"value": 0, "change_pct": 0, "label": "معدل التحويل %"},
            "avg_response_time": {"value": 0, "unit": "minutes", "label": "متوسط وقت الرد"},
            "messages_sent": {"value": 0, "change_pct": 0, "label": "الرسائل المرسلة"},
            "ai_interactions": {"value": 0, "change_pct": 0, "label": "تفاعلات الذكاء الاصطناعي"},
        },
        "tenant_id": current_user.get("tenant_id"),
    }


@router.get("/pipeline")
async def get_pipeline_analytics(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
):
    """Pipeline analytics — deals by stage, conversion rates."""
    stages = [
        {"name": "جديد", "key": "new", "count": 0, "value": 0, "conversion_to_next": 0},
        {"name": "تم التواصل", "key": "contacted", "count": 0, "value": 0, "conversion_to_next": 0},
        {"name": "مؤهل", "key": "qualified", "count": 0, "value": 0, "conversion_to_next": 0},
        {"name": "عرض سعر", "key": "proposal", "count": 0, "value": 0, "conversion_to_next": 0},
        {"name": "تفاوض", "key": "negotiation", "count": 0, "value": 0, "conversion_to_next": 0},
        {"name": "مغلق - ربح", "key": "won", "count": 0, "value": 0, "conversion_to_next": None},
        {"name": "مغلق - خسارة", "key": "lost", "count": 0, "value": 0, "conversion_to_next": None},
    ]
    return {
        "stages": stages,
        "total_pipeline_value": 0,
        "avg_deal_cycle_days": 0,
        "win_rate": 0,
        "currency": "SAR",
    }


@router.get("/revenue")
async def get_revenue_analytics(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    period: str = Query("monthly", regex="^(daily|weekly|monthly)$"),
    current_user: dict = Depends(get_current_user),
):
    """Revenue analytics — MRR, ARR, growth, by plan."""
    return {
        "summary": {
            "mrr": {"value": 0, "change_pct": 0, "label": "الإيراد الشهري المتكرر"},
            "arr": {"value": 0, "change_pct": 0, "label": "الإيراد السنوي المتكرر"},
            "total_revenue": {"value": 0, "label": "إجمالي الإيرادات"},
            "avg_deal_size": {"value": 0, "label": "متوسط حجم الصفقة"},
            "growth_rate": {"value": 0, "label": "معدل النمو %"},
        },
        "by_plan": [
            {"plan": "أساسي", "revenue": 0, "customers": 0},
            {"plan": "احترافي", "revenue": 0, "customers": 0},
            {"plan": "مؤسسي", "revenue": 0, "customers": 0},
        ],
        "trend": [],
        "currency": "SAR",
    }


@router.get("/leads")
async def get_lead_analytics(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
):
    """Lead analytics — by source, status, industry, conversion funnel."""
    return {
        "by_source": [
            {"source": "واتساب", "count": 0, "conversion_rate": 0},
            {"source": "نموذج الموقع", "count": 0, "conversion_rate": 0},
            {"source": "إعلانات Meta", "count": 0, "conversion_rate": 0},
            {"source": "إحالة", "count": 0, "conversion_rate": 0},
            {"source": "LinkedIn", "count": 0, "conversion_rate": 0},
            {"source": "يدوي", "count": 0, "conversion_rate": 0},
        ],
        "by_status": [
            {"status": "جديد", "count": 0},
            {"status": "تم التواصل", "count": 0},
            {"status": "مؤهل", "count": 0},
            {"status": "غير مؤهل", "count": 0},
        ],
        "by_industry": [
            {"industry": "رعاية صحية", "count": 0},
            {"industry": "عقارات", "count": 0},
            {"industry": "مقاولات", "count": 0},
            {"industry": "تجزئة", "count": 0},
            {"industry": "أغذية ومشروبات", "count": 0},
            {"industry": "تعليم", "count": 0},
        ],
        "funnel": {
            "total_leads": 0,
            "contacted": 0,
            "qualified": 0,
            "proposal_sent": 0,
            "won": 0,
        },
        "total_leads": 0,
        "new_leads_today": 0,
    }


@router.get("/team")
async def get_team_analytics(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
):
    """Team performance — per-user metrics."""
    return {
        "team_members": [],
        "summary": {
            "total_members": 0,
            "avg_deals_per_member": 0,
            "avg_revenue_per_member": 0,
            "avg_response_time_minutes": 0,
            "top_performer": None,
        },
        "leaderboard": {
            "by_revenue": [],
            "by_deals_closed": [],
            "by_response_time": [],
        },
    }


@router.get("/campaigns")
async def get_campaign_analytics(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
):
    """Campaign ROI analytics."""
    return {
        "campaigns": [],
        "summary": {
            "total_campaigns": 0,
            "total_spend": 0,
            "total_leads": 0,
            "total_revenue": 0,
            "avg_cpl": 0,
            "avg_roi": 0,
            "label_spend": "إجمالي الإنفاق",
            "label_roi": "العائد على الاستثمار",
        },
        "by_channel": [
            {"channel": "واتساب", "leads": 0, "spend": 0, "revenue": 0},
            {"channel": "إيميل", "leads": 0, "spend": 0, "revenue": 0},
            {"channel": "Meta Ads", "leads": 0, "spend": 0, "revenue": 0},
            {"channel": "Google Ads", "leads": 0, "spend": 0, "revenue": 0},
        ],
        "currency": "SAR",
    }


@router.get("/ai")
async def get_ai_analytics(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
):
    """AI agent performance analytics."""
    return {
        "summary": {
            "total_interactions": {"value": 0, "label": "إجمالي التفاعلات"},
            "auto_replies_sent": {"value": 0, "label": "ردود تلقائية"},
            "leads_qualified": {"value": 0, "label": "عملاء تم تأهيلهم"},
            "objections_handled": {"value": 0, "label": "اعتراضات تم التعامل معها"},
            "avg_sentiment": {"value": 0, "label": "متوسط المشاعر"},
            "qualification_accuracy": {"value": 0, "label": "دقة التأهيل %"},
        },
        "by_type": [
            {"type": "رد تلقائي", "count": 0},
            {"type": "تأهيل عميل", "count": 0},
            {"type": "معالجة اعتراض", "count": 0},
            {"type": "رسالة متابعة", "count": 0},
            {"type": "تحليل مشاعر", "count": 0},
        ],
        "tokens_used": 0,
        "cost_estimate_sar": 0,
    }


@router.get("/voice")
async def get_voice_analytics(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
):
    """Voice AI analytics."""
    return {
        "summary": {
            "total_calls": {"value": 0, "label": "إجمالي المكالمات"},
            "inbound_calls": {"value": 0, "label": "مكالمات واردة"},
            "outbound_calls": {"value": 0, "label": "مكالمات صادرة"},
            "avg_duration_seconds": {"value": 0, "label": "متوسط المدة"},
            "qualification_rate": {"value": 0, "label": "معدل التأهيل %"},
            "handoff_rate": {"value": 0, "label": "معدل التحويل لموظف %"},
            "total_cost_sar": {"value": 0, "label": "التكلفة الإجمالية"},
        },
        "by_disposition": [
            {"disposition": "مؤهل", "count": 0},
            {"disposition": "غير مهتم", "count": 0},
            {"disposition": "طلب معاودة الاتصال", "count": 0},
            {"disposition": "لم يرد", "count": 0},
            {"disposition": "تم التحويل لموظف", "count": 0},
        ],
        "by_hour": [],
    }


@router.get("/export")
async def export_analytics(
    report_type: str = Query(..., regex="^(overview|leads|deals|revenue|team|campaigns)$"),
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
):
    """Export analytics report as CSV (returns download URL)."""
    return {
        "status": "generating",
        "report_type": report_type,
        "format": "csv",
        "message": "جاري إعداد التقرير، سيتم إرسال رابط التحميل",
        "estimated_seconds": 10,
        "download_url": None,
    }
