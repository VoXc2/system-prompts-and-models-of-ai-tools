"""AEO Radar تجريبي — قوائم أسئلة قطاعية بدون استدعاء محركات خارجية."""

from __future__ import annotations

from typing import Any

# أسئلة نموذجية لكل قطاع (تغطية محتوى / سرد)
_SECTOR_QUESTIONS: dict[str, list[str]] = {
    "clinics": [
        "أفضل عيادة [تخصص] في [المدينة]؟",
        "كيف أحجز موعد عيادة أونلاين في السعودية؟",
        "ما الفرق بين العيادات المرخصة من هيئة التخصصات الصحية؟",
        "تكلفة جلسة [إجراء] تقريباً في الرياض؟",
    ],
    "real_estate": [
        "وسطاء عقار موثوقون في [المدينة]؟",
        "كيف أتحقق من صحة صك العقار؟",
        "ما هي الرسوم والضرائب عند شراء شقة جديدة؟",
        "أفضل أحياء للسكن العائلي في [المدينة]؟",
    ],
    "logistics": [
        "شركات لوجستيات للشحن من السعودية إلى الخليج؟",
        "كيف أتتبع شحنة B2B؟",
        "ما المتطلبات الجمركية للتصدير من السعودية؟",
        "تكلفة الشحن للطن الواحد تقريباً؟",
    ],
    "training": [
        "دورات معتمدة في [المجال] للشركات؟",
        "كيف أقيس عائد التدريب للموظفين؟",
        "أفضل مزودي تدريب أونلاين بالعربية؟",
        "سياسة الهيئة للتدريب التقني؟",
    ],
    "default": [
        "ما أفضل حلول [المجال] للشركات الصغيرة في السعودية؟",
        "كيف أقارن بين مزودي [الخدمة]؟",
        "ما متطلبات الامتثال PDPL للتواصل التسويقي؟",
        "كيف أربط المبيعات بواتساب بشكل آمن؟",
    ],
}


def build_aeo_radar_demo(sector: str | None) -> dict[str, Any]:
    """
    يُرجع قائمة تحقق AEO: أسئلة مقترحة، فجوات محتوى، **بدون** استعلام خارجي.
    """
    key = (sector or "default").strip().lower().replace(" ", "_")
    questions = list(_SECTOR_QUESTIONS.get(key, _SECTOR_QUESTIONS["default"]))
    gaps: list[dict[str, Any]] = []
    for i, q in enumerate(questions):
        gaps.append(
            {
                "question_template": q,
                "suggested_content_ar": "صفحة إجابة قصيرة + FAQ + شهادة عميل + CTA لحجز استكشاف.",
                "coverage_estimate": "low" if i >= 2 else "medium",
                "priority": "P1" if i == 0 else "P2",
            }
        )
    return {
        "sector_key": key,
        "demo": True,
        "no_live_search": True,
        "questions": questions,
        "content_gaps": gaps,
        "notes_ar": "هذا عرض تجريبي؛ ربط محركات إجابات لاحقاً يكون اختيارياً وبحدود امتثال.",
    }
