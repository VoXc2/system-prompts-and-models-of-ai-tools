"""Dealix Logistics OS — productized vertical for shipping & 3PL."""

from __future__ import annotations

from auto_client_acquisition.vertical_os.base import KPI, MessageTemplate, VerticalOS, _register


LOGISTICS = VerticalOS(
    vertical_id="logistics",
    sector_ar="شحن ولوجستيات",
    sector_en="Logistics & Shipping",
    icp_company_size=("mid", "large"),
    icp_cities=("الرياض", "جدة", "الدمام", "الخبر"),
    icp_keywords=("شحن", "نقل", "لوجستيات", "logistics", "3PL", "fulfillment"),
    pain_points_ar=(
        "RFQs عبر إيميلات طويلة بدون متابعة سريعة",
        "زمن الـ quote 3+ أيام — يخسرون لصالح المنافسين",
        "اعتماد على القطاع الحكومي فقط — تذبذب",
        "صعوبة دخول قطاعات جديدة (e-commerce, F&B)",
    ),
    top_objection_ids=("OBJ_COMPETITOR_001", "OBJ_PRICE_001", "OBJ_TRUST_002"),
    priority_signals=(
        "tender_published",
        "hiring_sales_rep",
        "new_service_launched",
        "ads_volume_increased",
    ),
    dashboard_kpis=(
        KPI("rfqs_per_month", "RFQs شهرياً", "إجمالي طلبات العروض المؤهلة", "rfq", True, 30, 100),
        KPI("avg_quote_time_hours", "متوسط زمن الـ quote", "من استلام الطلب إلى إرسال العرض", "ساعة", False, 48, 1),
        KPI("rfq_to_won_rate", "نسبة فوز RFQ", "نسبة الـ RFQs التي تتحول لعقود", "%", True, 0.18, 0.40),
        KPI("avg_contract_value_sar", "متوسط قيمة العقد", "السنوية", "ريال", True, 80_000, 200_000),
        KPI("client_concentration_top3_pct", "تركّز العملاء (top 3)", "نسبة الإيراد من أكبر 3 عملاء", "%", False, 0.60, 0.30),
    ),
    message_templates=(
        MessageTemplate(
            template_id="logistics_email_tender",
            channel="email",
            purpose="cold",
            subject_ar="بخصوص مناقصة {tender_title}",
            body_ar=(
                "السلام عليكم {first_name}،\n\n"
                "لاحظنا منشور مناقصة {tender_title} في {city} بـ deadline {deadline}. "
                "Dealix يساعد شركات لوجستيات سعودية على pre-qualification + جمع 5 موردين بدائل + "
                "Bid response في {response_hours} ساعة بدلاً من أيام.\n\n"
                "هل تفضلون عرض 15 دقيقة قبل الإثنين؟"
            ),
            variables=("first_name", "tender_title", "city", "deadline", "response_hours"),
            expected_reply_rate=0.08,
        ),
        MessageTemplate(
            template_id="logistics_wa_hiring",
            channel="whatsapp",
            purpose="cold",
            subject_ar=None,
            body_ar=(
                "السلام عليكم {first_name}،\n"
                "رأيت إعلانكم لتوظيف commercial reps. السؤال السريع: "
                "متوسط زمن الـ quote عندكم اليوم كم يوم؟ شركات لوجستيات في {city} "
                "قطعت زمن الـ quote من 3 أيام إلى ساعة عبر Dealix — "
                "RFQs المؤهلة زادت 3×. مهتم نشوف؟"
            ),
            variables=("first_name", "city"),
            expected_reply_rate=0.09,
        ),
    ),
    proposal_template_ar=(
        "## عرض Dealix Logistics لـ {company_name}\n\n"
        "**الهدف:** 100 RFQ مؤهل شهرياً + زمن الـ quote <1 ساعة\n\n"
        "### الخدمة\n"
        "- اكتشاف يومي للمناقصات الحكومية + خاصة (saudi tender feed + corporate RFPs)\n"
        "- ICP match + budget verification قبل الـ quote\n"
        "- Quote auto-draft من template مدمج بـ pricing engine\n"
        "- Multi-channel reach (email + WhatsApp) للمشترين\n"
        "- Dashboard للـ commercial director: rfqs / response_time / win_rate / pipeline\n\n"
        "### السعر: {price_sar} ريال/شهر · success fee 5% على عقود +500K ريال\n"
    ),
    qbr_section_template_ar=(
        "## QBR — {customer_name} — {period}\n\n"
        "- RFQs مؤهلة: {rfqs}\n"
        "- متوسط زمن الـ quote: {quote_hours} ساعة\n"
        "- العقود الموقّعة: {contracts}\n"
        "- إيراد محسوم: {revenue_sar:,.0f} ريال\n"
        "- Pipeline: {pipeline_sar:,.0f} ريال\n"
    ),
    avg_deal_value_sar=120_000,
    avg_cycle_days=35,
    benchmark_reply_rate=0.068,
    benchmark_meeting_rate=0.30,
    benchmark_win_rate=0.22,
    compliance_notes_ar=(
        "بيانات الشحنات قد تحتوي على معلومات تجارية حساسة — لا تشاركها مع subprocessors بدون DPA.",
        "تواصلات المناقصات الحكومية تخضع لسياسة منصة اعتماد.",
    ),
    recommended_channel_mix={"email": 0.45, "whatsapp": 0.35, "linkedin": 0.10, "phone": 0.10},
)

_register(LOGISTICS)
