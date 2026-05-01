"""12-minute demo + discovery + close — Arabic scripts (reference)."""

from __future__ import annotations

from typing import Any


def build_12_min_demo_flow() -> dict[str, Any]:
    return {
        "duration_minutes": 12,
        "steps_ar": [
            "٠–٢: المشكلة — تشتت قنوات وقرارات يومية غير واضحة.",
            "٢–٤: Daily Brief — قرارات ومخاطر.",
            "٤–٦: فرص ومهمات — مثال ١٠ فرص.",
            "٦–٨: Contactability — آمن / يحتاج مراجعة / ممنوع.",
            "٨–١٠: برج الخدمات — عرض ٤٩٩ و Pilot.",
            "١٠–١٢: الخطوة التالية — تشخيص مجاني أو Pilot.",
        ],
        "closing_line_ar": "Dealix لا يرسل عشوائياً — يقرر، يكتب، يطلب موافقة، ثم يثبت النتائج.",
        "demo": True,
    }


def build_discovery_questions() -> dict[str, Any]:
    return {
        "questions_ar": [
            "من عميلكم المثالي اليوم؟",
            "ما القناة التي تثقون بها أكثر (إيميل، واتساب opt-in، نماذج)؟",
            "هل عندكم قائمة أرقام أو CRM؟",
            "ما متوسط قيمة الصفقة؟",
            "من يوافق على الرسائل داخل الشركة؟",
        ],
        "demo": True,
    }


def build_close_script() -> dict[str, Any]:
    return {
        "script_ar": (
            "خلنا نجرب ٧ أيام بـ٤٩٩ ريال: نعطيكم ١٠ فرص، رسائل عربية، فحص مخاطر، خطة متابعة، وProof Pack. "
            "بعدها تقررون Growth OS أو التوقف — بدون التزام تلقائي."
        ),
        "demo": True,
    }


def build_objection_responses() -> dict[str, Any]:
    return {
        "objections_ar": [
            {
                "objection": "نخاف من واتساب",
                "response_ar": "نعم — واتساب فقط مع opt-in أو inbound؛ الباقي إيميل أو مهام يدوية معتمدة.",
            },
            {
                "objection": "هل تضمنون عملاء؟",
                "response_ar": "لا نضمن نتائج — نضمن مسودات وموافقات وتقرير قياس واضح.",
            },
            {
                "objection": "نحتاج وقت للتفكير",
                "response_ar": "تمام — أرسل لك تشخيصاً مجانياً صغيراً خلال ٢٤ ساعة لتشوف الأسلوب.",
            },
        ],
        "demo": True,
    }
