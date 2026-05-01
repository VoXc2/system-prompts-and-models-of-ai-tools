"""Dealix Real Estate OS — productized vertical for property developers."""

from __future__ import annotations

from auto_client_acquisition.vertical_os.base import KPI, MessageTemplate, VerticalOS, _register


REAL_ESTATE = VerticalOS(
    vertical_id="real_estate",
    sector_ar="تطوير عقاري",
    sector_en="Real Estate Development",
    icp_company_size=("mid", "large"),
    icp_cities=("الرياض", "جدة", "الدمام", "الخبر", "مكة"),
    icp_keywords=("تطوير", "مشروع", "وحدات سكنية", "شقق", "فلل", "عقار"),
    pain_points_ar=(
        "صعوبة جلب مشترين قبل التسليم",
        "وكالات تسويق غالية بدون قياس",
        "بطء الـ qualification — اتصالات كثيرة بدون شراء",
        "غياب CRM يربط الزيارة بالـ booking",
    ),
    top_objection_ids=("OBJ_TRUST_002", "OBJ_PRICE_001", "OBJ_AUTHORITY_002"),
    priority_signals=(
        "new_branch_opened",
        "new_service_launched",
        "ads_volume_increased",
        "exhibition_participation",
        "tender_published",
        "leadership_change",
    ),
    dashboard_kpis=(
        KPI("qualified_leads_per_month", "Leads مؤهلة شهرياً", "leads مرّت ICP + budget", "lead", True, 30, 80),
        KPI("site_visit_rate", "نسبة زيارة الموقع", "نسبة من حصلوا على tour الفعلي", "%", True, 0.20, 0.45),
        KPI("conversion_visit_to_reservation", "تحويل الزيارة لحجز", "نسبة الذين يحجزون بعد الزيارة", "%", True, 0.15, 0.32),
        KPI("avg_time_to_close_days", "متوسط مدة الإغلاق", "من lead إلى حجز", "يوم", False, 60, 30),
        KPI("cost_per_qualified_lead", "تكلفة كل lead مؤهل", "إنفاق التسويق ÷ leads المؤهلة", "ريال", False, 600, 200),
    ),
    message_templates=(
        MessageTemplate(
            template_id="re_cold_wa_branch_opened",
            channel="whatsapp",
            purpose="cold",
            subject_ar=None,
            body_ar=(
                "السلام عليكم {first_name}،\n"
                "تابعنا افتتاح مشروعكم الجديد في {city} — تهانينا. "
                "في 60 يوم نسلمكم 50 lead مؤهل من المهتمين بحجم وميزانية مشروعكم تحديداً، "
                "بدون وكالة + بـ تكلفة أقل 70% من السوق. "
                "مهتم تشوف 3 أمثلة من مشاريع مشابهة؟"
            ),
            variables=("first_name", "city"),
            expected_reply_rate=0.10,
        ),
        MessageTemplate(
            template_id="re_email_hiring_signal",
            channel="email",
            purpose="cold",
            subject_ar="ملاحظة على توسعكم في {city}",
            body_ar=(
                "السلام عليكم {first_name}،\n\n"
                "لاحظنا أنكم تبحثون عن sales reps إضافيين في {city}. "
                "في {months} شهر، Dealix يخفّض ramp-up SDR من 90 يوم إلى 21 يوم "
                "عبر playbook عقاري سعودي مدروس + AI drafts.\n\n"
                "نسعد بـ 15 دقيقة لعرض الأمثلة من شركات تطوير سعودية مماثلة. "
                "هل الأربعاء أم الخميس يناسبك؟"
            ),
            variables=("first_name", "city", "months"),
            expected_reply_rate=0.07,
        ),
    ),
    proposal_template_ar=(
        "## عرض Dealix Real Estate لـ {company_name}\n\n"
        "**الهدف:** 50 lead مؤهل + اجتماع أسبوعياً خلال 90 يوم\n\n"
        "### الخدمة\n"
        "- اكتشاف يومي للمهتمين عبر Saudi Maps + LinkedIn + Google Search\n"
        "- enrichment + ICP scoring تلقائي\n"
        "- Personalization عربية لكل lead بناءً على وضعه (مستثمر / مستخدم نهائي / شركة)\n"
        "- WhatsApp + Email chain + booking page integration\n"
        "- Dashboard للمدير: leads / visits / reservations / revenue\n\n"
        "### السعر: {price_sar} ريال/شهر · أول 30 يوم Pay-per-Qualified-Lead (150 ريال/lead)\n"
    ),
    qbr_section_template_ar=(
        "## QBR — {customer_name} — {period}\n\n"
        "- Leads المؤهلة: {qualified}\n"
        "- زيارات الموقع: {visits}\n"
        "- الحجوزات: {reservations}\n"
        "- إيراد محسوم: {revenue_sar:,.0f} ريال\n"
        "- Cost per qualified lead: {cpql} ريال (target: <200)\n"
    ),
    avg_deal_value_sar=750_000,
    avg_cycle_days=45,
    benchmark_reply_rate=0.074,
    benchmark_meeting_rate=0.32,
    benchmark_win_rate=0.18,
    compliance_notes_ar=(
        "بيع الوحدات السكنية يتطلب احترام أنظمة الترخيص العقاري السعودي.",
        "لا تطلب بيانات هوية أو IBAN في الرسالة الأولى.",
        "احترم quiet hours — الجمعة + المساء بعد 9م مزعج للعملاء.",
    ),
    recommended_channel_mix={"whatsapp": 0.55, "email": 0.25, "linkedin": 0.10, "phone": 0.10},
)

_register(REAL_ESTATE)
