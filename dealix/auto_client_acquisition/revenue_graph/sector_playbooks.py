"""
In-Product Saudi Sector Playbooks.

Each playbook is structured data that the Personalization Agent +
Deal Coach Agent + UI all read. NOT just landing-page marketing —
this is the operational knowledge inside the product.

Per sector:
  - Pain points
  - Top objections
  - Best opening lines (Arabic, sector-tuned)
  - Best offer angle
  - Buying committee composition
  - Seasonal timing
  - Average benchmarks
  - Recommended channel mix
  - WhatsApp tone
  - 1-2 mini case studies (templated)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class SectorPlaybook:
    sector_id: str
    sector_ar: str
    sector_en: str
    pain_points_ar: tuple[str, ...]
    top_objections: tuple[str, ...]            # objection_ids from objection_library
    opening_lines_ar: tuple[str, ...]
    best_offer_angle_ar: str
    buying_committee: tuple[str, ...]          # roles
    seasonal_peaks_ar: tuple[str, ...]
    benchmarks: dict[str, float]
    recommended_channel_mix: dict[str, float]  # weights summing to 1
    whatsapp_tone: str                         # formal / warm / direct
    case_study_template_ar: str
    avg_deal_value_sar: int
    avg_cycle_days: int


REAL_ESTATE = SectorPlaybook(
    sector_id="real_estate",
    sector_ar="تطوير عقاري",
    sector_en="Real Estate Development",
    pain_points_ar=(
        "صعوبة جلب مشترين لمشاريع جديدة قبل التسليم",
        "وكالات تسويق غالية وغير مقاسة",
        "بطء الـ qualification — اتصالات كثيرة بدون شراء",
        "غياب CRM يربط الزيارة بالـ booking",
    ),
    top_objections=("OBJ_TRUST_002", "OBJ_PRICE_001", "OBJ_AUTHORITY_002"),
    opening_lines_ar=(
        "لاحظنا مشروعكم الجديد في {city} — كم نسبة الحجوزات حالياً قبل التسليم؟",
        "إذا تبحثون عن طريقة لتعبئة 80% من الوحدات قبل الافتتاح، عندنا سياق مهم.",
    ),
    best_offer_angle_ar=(
        "في 60 يوم نُسلم لكم 50 lead مؤهل من المهتمين بحجم وميزانية مشروعكم — "
        "بدون وكالة + بـ تكلفة أقل 70% من السوق."
    ),
    buying_committee=("CEO", "VP Sales", "Marketing Director", "Project Manager"),
    seasonal_peaks_ar=("Q1 (يناير-مارس)", "Q4 (أكتوبر-ديسمبر) بعد المعارض العقارية"),
    benchmarks={
        "reply_rate_p50": 0.074,
        "meeting_rate_p50": 0.32,
        "win_rate_p50": 0.18,
        "cycle_days_p50": 45,
    },
    recommended_channel_mix={
        "whatsapp": 0.55,
        "email": 0.25,
        "linkedin": 0.10,
        "phone": 0.10,
    },
    whatsapp_tone="warm",
    case_study_template_ar=(
        "شركة تطوير في {city} استخدمت Dealix لمدة {months} شهر، "
        "حصلت على {meetings} اجتماع و{deals} حجز جديد، بقيمة {pipeline} ريال."
    ),
    avg_deal_value_sar=750_000,
    avg_cycle_days=45,
)

CLINICS = SectorPlaybook(
    sector_id="clinics",
    sector_ar="عيادات",
    sector_en="Medical Clinics",
    pain_points_ar=(
        "no-show rate عالي (30-40%)",
        "صعوبة جلب مرضى الـ private للخدمات التجميلية/الطب الوقائي",
        "إعلانات Snapchat/TikTok مكلفة بدون قياس واضح",
        "نقص في CRM للمرضى المهتمين لكن لم يحجزوا",
    ),
    top_objections=("OBJ_TRUST_001", "OBJ_TIMING_001", "OBJ_PRICE_002"),
    opening_lines_ar=(
        "في عيادتكم، كم نسبة من المتصلين يكملون الحجز ويأتون؟",
        "عيادات مشابهة لكم خفّضت no-show بنسبة 40% مع reminder system ذكي.",
    ),
    best_offer_angle_ar=(
        "نخفّض no-show 40% + نزيد الحجوزات 2× — بـ WhatsApp تلقائي بالعربي "
        "+ متابعة المريض المهتم اللي اتصل ولم يحجز."
    ),
    buying_committee=("Owner-Doctor", "Clinic Manager", "Marketing Lead"),
    seasonal_peaks_ar=("Q3 قبل المدارس", "Q1 بعد رمضان", "موسم الصيف للتجميل"),
    benchmarks={
        "reply_rate_p50": 0.138,
        "meeting_rate_p50": 0.40,
        "win_rate_p50": 0.28,
        "cycle_days_p50": 28,
    },
    recommended_channel_mix={
        "whatsapp": 0.70,
        "email": 0.10,
        "phone": 0.20,
    },
    whatsapp_tone="warm",
    case_study_template_ar=(
        "عيادة {city} استخدمت Dealix {months} شهر — no-show نزل من {before}% "
        "إلى {after}%، وحجوزات الـ private زادت {growth}%."
    ),
    avg_deal_value_sar=2_500,
    avg_cycle_days=28,
)

LOGISTICS = SectorPlaybook(
    sector_id="logistics",
    sector_ar="شحن ولوجستيات",
    sector_en="Logistics & Shipping",
    pain_points_ar=(
        "فقدان عملاء B2B لصالح المنافسين بسبب بطء الـ quote",
        "قواعد العملاء قديمة — لا تواصل سنوي للحفاظ عليهم",
        "صعوبة دخول قطاعات جديدة (e-commerce, F&B)",
        "RFQs عبر إيميلات طويلة بدون nurture",
    ),
    top_objections=("OBJ_COMPETITOR_001", "OBJ_PRICE_001", "OBJ_TRUST_002"),
    opening_lines_ar=(
        "في عملياتكم، متوسط زمن الـ quote من الطلب للرد كم يوم؟",
        "شركات لوجستيات سعودية مشابهة قطعت زمن الـ quote من 3 أيام إلى ساعة.",
    ),
    best_offer_angle_ar=(
        "Dealix يجيب لكم 100 RFQ مؤهل شهرياً + يقطع زمن الـ quote إلى أقل من ساعة — "
        "بدون توظيف SDRs جدد."
    ),
    buying_committee=("CEO", "Commercial Director", "Operations Manager"),
    seasonal_peaks_ar=("Q4 (موسم e-commerce)", "Ramadan (FMCG)", "Hajj (موسمي)"),
    benchmarks={
        "reply_rate_p50": 0.068,
        "meeting_rate_p50": 0.30,
        "win_rate_p50": 0.22,
        "cycle_days_p50": 35,
    },
    recommended_channel_mix={
        "email": 0.45,
        "whatsapp": 0.35,
        "linkedin": 0.10,
        "phone": 0.10,
    },
    whatsapp_tone="direct",
    case_study_template_ar=(
        "شركة لوجستيات في {city} استخدمت Dealix {months} شهر — "
        "RFQs المؤهلة زادت {x}× وزمن الـ quote نزل من {before} إلى {after}."
    ),
    avg_deal_value_sar=120_000,
    avg_cycle_days=35,
)

HOSPITALITY = SectorPlaybook(
    sector_id="hospitality",
    sector_ar="فنادق وضيافة",
    sector_en="Hospitality",
    pain_points_ar=(
        "اعتماد كبير على OTAs (Booking, Agoda) بعمولات 18-22%",
        "ضعف الـ corporate / MICE pipeline",
        "موسمية حادة بين Q1 (رمضان/إجازات) والـ off-season",
        "صعوبة الوصول لمدراء التدريب والـ event planners في الشركات",
    ),
    top_objections=("OBJ_COMPETITOR_001", "OBJ_PRICE_002", "OBJ_TRUST_003"),
    opening_lines_ar=(
        "كم نسبة الحجوزات المباشرة لديكم vs OTAs؟ هذا الـ ratio يحدد هامش الربح.",
        "فنادق سعودية تجاوزت 60% direct bookings باستخدام B2B corporate pipeline.",
    ),
    best_offer_angle_ar=(
        "Dealix يبني لكم corporate / MICE pipeline يضيف 30%+ من الإيراد المباشر "
        "(غير OTAs) في 6 شهور."
    ),
    buying_committee=("GM", "Director of Sales", "MICE Coordinator", "Revenue Manager"),
    seasonal_peaks_ar=("Q1 (إجازات)", "Q3 (Hajj)", "Q4 (corporate planning)"),
    benchmarks={
        "reply_rate_p50": 0.124,
        "meeting_rate_p50": 0.38,
        "win_rate_p50": 0.24,
        "cycle_days_p50": 30,
    },
    recommended_channel_mix={
        "email": 0.50,
        "whatsapp": 0.30,
        "linkedin": 0.15,
        "phone": 0.05,
    },
    whatsapp_tone="formal",
    case_study_template_ar=(
        "فندق {brand} في {city} زاد الحجوزات الـ corporate {x}% عبر Dealix في {months} شهر."
    ),
    avg_deal_value_sar=180_000,
    avg_cycle_days=30,
)

RESTAURANTS = SectorPlaybook(
    sector_id="restaurants",
    sector_ar="مطاعم وكاترينج",
    sector_en="Restaurants & Catering",
    pain_points_ar=(
        "اعتماد على المشي (walk-ins) — لا pipeline قابل للتوقع",
        "ضعف خدمة الـ catering للشركات والمكاتب",
        "صعوبة الوصول لـ HR وادارة المكاتب",
        "غياب نظام للحجز المتقدم للمناسبات",
    ),
    top_objections=("OBJ_PRICE_001", "OBJ_FIT_001"),
    opening_lines_ar=(
        "حالياً، كم نسبة إيراد المطعم من corporate catering؟",
        "مطاعم في {city} حققت 25% إيراد إضافي من 3 عقود corporate catering فقط.",
    ),
    best_offer_angle_ar=(
        "Dealix يجيب لكم 5-10 عقود corporate catering شهرياً (مكاتب، HR teams، events) "
        "— يضيف 22% إيراد إضافي بدون توسعة فروع."
    ),
    buying_committee=("Owner", "Operations Manager", "Head Chef"),
    seasonal_peaks_ar=("Q1 (events corporate)", "Ramadan (iftars)", "Q4 (year-end parties)"),
    benchmarks={
        "reply_rate_p50": 0.115,
        "meeting_rate_p50": 0.42,
        "win_rate_p50": 0.30,
        "cycle_days_p50": 21,
    },
    recommended_channel_mix={
        "whatsapp": 0.65,
        "email": 0.20,
        "phone": 0.15,
    },
    whatsapp_tone="warm",
    case_study_template_ar=(
        "مطعم {brand} في {city} حقق {x} عقد catering جديد في {months} شهر — "
        "بقيمة {pipeline} ريال."
    ),
    avg_deal_value_sar=15_000,
    avg_cycle_days=21,
)

TRAINING = SectorPlaybook(
    sector_id="training",
    sector_ar="مراكز تدريب",
    sector_en="Training Centers",
    pain_points_ar=(
        "الاعتماد على individual learners — حجم محدود",
        "صعوبة بيع corporate training packages",
        "غياب نظام نقل المهارات من فرد إلى B2B",
        "منافسة شديدة على دورات Vision 2030",
    ),
    top_objections=("OBJ_TRUST_001", "OBJ_AUTHORITY_001"),
    opening_lines_ar=(
        "كم نسبة الـ enrollments الـ corporate (B2B) من إجمالي مركزكم حالياً؟",
        "مراكز تدريب سعودية حوّلت 30% من focusها إلى corporate وضاعفت الإيراد.",
    ),
    best_offer_angle_ar=(
        "Dealix يبني لكم B2B corporate training pipeline — 5+ شركات شهرياً "
        "تطلب custom programs لفريقها."
    ),
    buying_committee=("Center Director", "Business Development", "Curriculum Lead"),
    seasonal_peaks_ar=("Q1 (بداية السنة المالية)", "Q3 (بعد إجازات)", "Q4 (تخطيط السنة الجديدة)"),
    benchmarks={
        "reply_rate_p50": 0.112,
        "meeting_rate_p50": 0.36,
        "win_rate_p50": 0.25,
        "cycle_days_p50": 35,
    },
    recommended_channel_mix={
        "linkedin": 0.40,
        "email": 0.30,
        "whatsapp": 0.20,
        "phone": 0.10,
    },
    whatsapp_tone="formal",
    case_study_template_ar=(
        "مركز تدريب في {city} رفع corporate enrollments {x}% خلال {months} شهر."
    ),
    avg_deal_value_sar=85_000,
    avg_cycle_days=35,
)

AGENCIES = SectorPlaybook(
    sector_id="agencies",
    sector_ar="وكالات تسويق",
    sector_en="Marketing Agencies",
    pain_points_ar=(
        "تذبذب MRR — الاعتماد على referrals فقط",
        "صعوبة بيع retainer ضد مشاريع one-off",
        "ضعف الـ inbound — لا content marketing منتظم",
        "تغيّر العملاء كل 6 شهور",
    ),
    top_objections=("OBJ_PRICE_003", "OBJ_TRUST_003", "OBJ_FIT_001"),
    opening_lines_ar=(
        "كم نسبة الـ retainers من إجمالي MRR لديكم؟",
        "وكالات في {city} ضاعفت MRR بـ retainer-only model + outbound مستقر.",
    ),
    best_offer_angle_ar=(
        "Dealix لكل وكالة retainer pipeline يضيف 5+ عملاء متعاقدين شهرياً — "
        "MRR مستقر بدلاً من project-by-project."
    ),
    buying_committee=("Founder", "Managing Director", "Sales Lead"),
    seasonal_peaks_ar=("Q1 (تخطيط ميزانيات)", "Q4 (planning النصف القادم)"),
    benchmarks={
        "reply_rate_p50": 0.059,
        "meeting_rate_p50": 0.28,
        "win_rate_p50": 0.20,
        "cycle_days_p50": 45,
    },
    recommended_channel_mix={
        "email": 0.40,
        "linkedin": 0.30,
        "whatsapp": 0.20,
        "phone": 0.10,
    },
    whatsapp_tone="direct",
    case_study_template_ar=(
        "وكالة {brand} رفعت MRR من {before} إلى {after} ريال في {months} شهر."
    ),
    avg_deal_value_sar=18_000,
    avg_cycle_days=45,
)

CONSTRUCTION = SectorPlaybook(
    sector_id="construction",
    sector_ar="مقاولات",
    sector_en="Construction & Contracting",
    pain_points_ar=(
        "RFPs عبر إيميلات بدون متابعة",
        "اعتماد على مناقصات حكومية فقط — تذبذب عالي",
        "ضعف الـ sales process — كله engineers، لا sales reps",
        "صعوبة الوصول لـ developers خاصة قبل المنافسين",
    ),
    top_objections=("OBJ_AUTHORITY_002", "OBJ_TRUST_001", "OBJ_PRICE_001"),
    opening_lines_ar=(
        "متوسط زمن استجابتكم لـ RFP من lead جديد؟ في القطاع 95% يردون بعد 5+ أيام.",
        "شركات مقاولات سعودية رفعت معدل الفوز بمناقصات بنسبة 60% بـ تأهيل أوتوماتيكي.",
    ),
    best_offer_angle_ar=(
        "Dealix يحوّل RFPs الواردة إلى pipeline منظم + يكشف لك 10+ مناقصة جديدة "
        "خاصة شهرياً قبل أن تخرج للسوق."
    ),
    buying_committee=("CEO", "Commercial Director", "Project Director", "Estimation Lead"),
    seasonal_peaks_ar=("Q1 (ميزانيات الجهات)", "Q3 (بدء مشاريع)", "Q4 (تخطيط النصف القادم)"),
    benchmarks={
        "reply_rate_p50": 0.032,
        "meeting_rate_p50": 0.25,
        "win_rate_p50": 0.15,
        "cycle_days_p50": 90,
    },
    recommended_channel_mix={
        "email": 0.55,
        "linkedin": 0.20,
        "phone": 0.15,
        "whatsapp": 0.10,
    },
    whatsapp_tone="formal",
    case_study_template_ar=(
        "شركة مقاولات في {city} رفعت معدل الفوز بالمناقصات بنسبة {x}% في {months} شهر."
    ),
    avg_deal_value_sar=2_500_000,
    avg_cycle_days=90,
)


ALL_PLAYBOOKS: tuple[SectorPlaybook, ...] = (
    REAL_ESTATE,
    CLINICS,
    LOGISTICS,
    HOSPITALITY,
    RESTAURANTS,
    TRAINING,
    AGENCIES,
    CONSTRUCTION,
)


# ── Public API ────────────────────────────────────────────────────
def get_playbook(sector_id: str) -> SectorPlaybook | None:
    for p in ALL_PLAYBOOKS:
        if p.sector_id == sector_id:
            return p
    return None


def list_playbooks_summary() -> list[dict[str, Any]]:
    """Lightweight summary for the Verticals tile in the dashboard."""
    return [
        {
            "sector_id": p.sector_id,
            "sector_ar": p.sector_ar,
            "avg_deal_value_sar": p.avg_deal_value_sar,
            "avg_cycle_days": p.avg_cycle_days,
            "reply_rate_p50": p.benchmarks["reply_rate_p50"],
            "primary_channel": max(p.recommended_channel_mix.items(), key=lambda x: x[1])[0],
            "buying_committee_size": len(p.buying_committee),
            "n_objections_indexed": len(p.top_objections),
        }
        for p in ALL_PLAYBOOKS
    ]
