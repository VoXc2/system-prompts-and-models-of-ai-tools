"""Dealix Clinics OS — productized vertical for medical clinics."""

from __future__ import annotations

from auto_client_acquisition.vertical_os.base import KPI, MessageTemplate, VerticalOS, _register


CLINICS = VerticalOS(
    vertical_id="clinics",
    sector_ar="عيادات",
    sector_en="Medical Clinics",
    icp_company_size=("micro", "small", "mid"),
    icp_cities=("الرياض", "جدة", "الدمام", "الخبر"),
    icp_keywords=("عيادة", "طب", "تجميل", "جلدية", "أسنان", "نساء وأطفال"),
    pain_points_ar=(
        "no-show rate عالي 30-40%",
        "اعلانات Snapchat/TikTok بدون قياس واضح",
        "الـ private المهتم لا يحجز فوراً",
        "تكلفة patient acquisition عالية",
    ),
    top_objection_ids=("OBJ_TRUST_001", "OBJ_TIMING_001", "OBJ_PRICE_002"),
    priority_signals=(
        "new_branch_opened",
        "new_service_launched",
        "booking_page_added",
        "whatsapp_business_added",
        "ads_volume_increased",
    ),
    dashboard_kpis=(
        KPI("bookings_per_month", "حجوزات شهرياً", "إجمالي الحجوزات المؤكدة", "حجز", True, 80, 200),
        KPI("no_show_rate", "نسبة عدم الحضور", "نسبة المرضى الذين لم يحضروا الموعد", "%", False, 0.30, 0.10),
        KPI("response_time_minutes", "زمن الرد", "متوسط زمن الرد على الاستفسارات", "دقيقة", False, 240, 30),
        KPI("patient_acquisition_cost_sar", "تكلفة استقطاب مريض", "إجمالي إنفاق التسويق ÷ عدد المرضى الجدد", "ريال", False, 350, 120),
        KPI("conversion_inquiry_to_booking", "تحويل الاستفسار للحجز", "نسبة من اتصلوا وحجزوا", "%", True, 0.35, 0.65),
    ),
    message_templates=(
        MessageTemplate(
            template_id="clinic_cold_wa_v1",
            channel="whatsapp",
            purpose="cold",
            subject_ar=None,
            body_ar=(
                "السلام عليكم دكتور {doctor_name}،\n"
                "لاحظنا توسعكم في {city} وإطلاق خدمة {new_service}. "
                "نساعد عيادات مماثلة على تقليل no-show بنسبة 40% + رفع حجوزاتكم 2× "
                "عبر WhatsApp تلقائي بالعربي. هل نقدر نريك demo 10 دقائق؟"
            ),
            variables=("doctor_name", "city", "new_service"),
            expected_reply_rate=0.18,
        ),
        MessageTemplate(
            template_id="clinic_followup_d3_wa",
            channel="whatsapp",
            purpose="followup_3d",
            subject_ar=None,
            body_ar=(
                "متابعة سريعة دكتور {doctor_name}،\n"
                "أعرف أنكم مشغولين. لو 5 دقائق فقط — نرسل لكم مثال حقيقي "
                "من عيادة في {city} خفّضت no-show من 35% إلى 12%. هل تفضلون الـ video أو PDF؟"
            ),
            variables=("doctor_name", "city"),
            expected_reply_rate=0.12,
        ),
        MessageTemplate(
            template_id="clinic_objection_have_receptionist",
            channel="whatsapp",
            purpose="objection_response",
            subject_ar=None,
            body_ar=(
                "تماماً — موظفة الاستقبال جزء أساسي. Dealix لا يستبدلها، بل يخفف عنها العبء: "
                "يرد على الاستفسارات بعد الدوام وبالأوقات الذروة، ويرسل تذكير الموعد تلقائياً. "
                "هل نشوف كيف؟"
            ),
            variables=(),
            expected_reply_rate=0.20,
        ),
    ),
    proposal_template_ar=(
        "## عرض Dealix Clinics لـ {clinic_name}\n\n"
        "**الهدف:** تقليل no-show 40% + زيادة الحجوزات 2× خلال 90 يوم\n\n"
        "### الخدمة\n"
        "- WhatsApp Business مدمج بنظام الحجز\n"
        "- ردود تلقائية بالعربي على الاستفسارات الشائعة (24/7)\n"
        "- تذكير الموعد قبل 24 ساعة + إعادة الحجز للحالات الملغية\n"
        "- Dashboard أسبوعي: bookings / no-show / response time / PAC\n\n"
        "### السعر: {price_sar} ريال/شهر\n"
        "### ضمان: نموذج Pay-per-Booking في أول 30 يوم\n"
        "### المدة: 12 شهر — أول 30 يوم تجريبي مجاني\n"
    ),
    qbr_section_template_ar=(
        "## QBR — {customer_name} — {period}\n\n"
        "- إجمالي الحجوزات: {bookings} (الهدف: {target_bookings})\n"
        "- no-show: {no_show_pct}% (الهدف: <10%)\n"
        "- متوسط زمن الرد: {response_min} دقيقة\n"
        "- تكلفة استقطاب مريض: {pac_sar} ريال (الهدف: <120 ريال)\n\n"
        "**الإيرادات المضافة:** ~{revenue_added_sar} ريال (مرضى جدد × متوسط قيمة الزيارة)\n"
    ),
    avg_deal_value_sar=2_500,           # avg patient lifetime value
    avg_cycle_days=28,
    benchmark_reply_rate=0.138,
    benchmark_meeting_rate=0.40,
    benchmark_win_rate=0.28,
    compliance_notes_ar=(
        "الحجوزات الطبية تخضع لتنظيمات وزارة الصحة + SCFHS — Dealix لا يطلب أي بيانات طبية حساسة في الـ outbound.",
        "كل اتصال بمريض يجب أن يحتوي على lawful basis: legitimate_interest كحد أدنى.",
        "البيانات الطبية الحساسة تبقى في النظام السريري للعيادة — لا تنتقل لـ Dealix.",
    ),
    recommended_channel_mix={"whatsapp": 0.70, "phone": 0.20, "email": 0.10},
)

_register(CLINICS)
