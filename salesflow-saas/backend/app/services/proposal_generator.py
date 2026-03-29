"""
Proposal content generator — توليد محتوى العروض التقديمية بالذكاء الاصطناعي.

Uses AIBrain to produce structured Arabic proposal content (JSONB)
and provides pre-built industry templates for the Saudi market.
"""
import json
import logging
from typing import Optional

from app.services.ai_brain import ai_brain as _ai_brain_singleton
from app.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

# ---------------------------------------------------------------------------
# AI system prompt for proposal generation
# ---------------------------------------------------------------------------

PROPOSAL_SYSTEM_PROMPT = """أنت خبير في كتابة العروض التقديمية والتجارية للسوق السعودي.

## مهمتك:
اكتب عرض تقديمي احترافي باللغة العربية بناءً على بيانات العميل والصفقة.

## القواعد:
- المحتوى يكون باللغة العربية الفصحى الاحترافية
- اذكر الأرقام والأسعار بالريال السعودي (SAR)
- اربط المحتوى بالقطاع المحدد وبرؤية 2030 عند المناسبة
- كن واقعي في الأسعار والمدد الزمنية
- استخدم تنسيق مهني ومرتب
- أضف شروط وأحكام واضحة

## تنسيق الرد:
أجب بصيغة JSON فقط بالتنسيق التالي:
{
  "sections": [
    {"title": "عنوان القسم", "content": "محتوى القسم بالتفصيل"},
    ...
  ],
  "services": [
    {"name": "اسم الخدمة", "description": "وصف مختصر", "price": "السعر أو يحدد لاحقاً"},
    ...
  ],
  "terms": "الشروط والأحكام",
  "validity_days": 30
}

لا تضف أي نص خارج JSON.
"""


# ---------------------------------------------------------------------------
# Industry templates (Arabic, Saudi market)
# ---------------------------------------------------------------------------

INDUSTRY_TEMPLATES: dict[str, dict] = {
    "salon": {
        "sections": [
            {
                "title": "نبذة عن خدماتنا",
                "content": "نقدم لكم باقة متكاملة من حلول إدارة صالونات التجميل والعناية الشخصية، مصممة خصيصاً لتلبية احتياجات السوق السعودي وتماشياً مع رؤية 2030 في دعم قطاع الخدمات.",
            },
            {
                "title": "الحلول المقترحة",
                "content": "نظام حجز المواعيد الذكي، إدارة العملاء وبرنامج الولاء، نظام نقاط البيع المتكامل، التسويق الرقمي عبر وسائل التواصل الاجتماعي، وتطبيق جوال مخصص للعملاء.",
            },
            {
                "title": "المزايا التنافسية",
                "content": "واجهة عربية بالكامل، دعم فني على مدار الساعة، تكامل مع أنظمة الدفع السعودية (مدى، Apple Pay)، وتقارير تحليلية متقدمة.",
            },
        ],
        "services": [
            {"name": "نظام إدارة الصالون", "description": "نظام شامل لإدارة المواعيد والموظفين والمخزون", "price": "يحدد لاحقاً"},
            {"name": "تطبيق حجز العملاء", "description": "تطبيق جوال للعملاء لحجز المواعيد ومتابعة الخدمات", "price": "يحدد لاحقاً"},
            {"name": "برنامج الولاء", "description": "نظام نقاط ومكافآت لزيادة ولاء العملاء", "price": "يحدد لاحقاً"},
            {"name": "التسويق الرقمي", "description": "إدارة حسابات التواصل الاجتماعي والحملات الإعلانية", "price": "يحدد لاحقاً"},
        ],
        "terms": "صلاحية العرض 30 يوماً من تاريخ الإصدار. الأسعار لا تشمل ضريبة القيمة المضافة (15%). يتم الدفع على ثلاث دفعات: 40% عند التوقيع، 30% عند التسليم الأولي، 30% عند التسليم النهائي. تشمل الصيانة والدعم الفني لمدة سنة من تاريخ التسليم.",
        "validity_days": 30,
    },
    "clinic": {
        "sections": [
            {
                "title": "نبذة عن خدماتنا",
                "content": "نقدم حلولاً تقنية متكاملة للعيادات والمراكز الطبية، متوافقة مع معايير وزارة الصحة السعودية ومنصة صحة، لتحسين كفاءة العمليات وتجربة المريض.",
            },
            {
                "title": "الحلول المقترحة",
                "content": "نظام السجلات الطبية الإلكترونية (EMR)، نظام حجز المواعيد والتذكيرات الآلية، بوابة المرضى الإلكترونية، نظام الفوترة والتأمين، والتكامل مع منصة صحة.",
            },
            {
                "title": "الامتثال والأمان",
                "content": "جميع حلولنا متوافقة مع معايير حماية البيانات الصحية، مع تشفير كامل للبيانات واستضافة محلية داخل المملكة العربية السعودية.",
            },
        ],
        "services": [
            {"name": "نظام السجلات الطبية الإلكترونية", "description": "إدارة شاملة لملفات المرضى والتاريخ الطبي", "price": "يحدد لاحقاً"},
            {"name": "نظام حجز المواعيد", "description": "حجز إلكتروني مع تذكيرات SMS وواتساب", "price": "يحدد لاحقاً"},
            {"name": "بوابة المرضى", "description": "تطبيق للمرضى للوصول لنتائجهم ومواعيدهم", "price": "يحدد لاحقاً"},
            {"name": "نظام الفوترة والتأمين", "description": "ربط مع شركات التأمين وإصدار الفواتير إلكترونياً", "price": "يحدد لاحقاً"},
        ],
        "terms": "صلاحية العرض 30 يوماً من تاريخ الإصدار. الأسعار لا تشمل ضريبة القيمة المضافة (15%). يتطلب التنفيذ 8-12 أسبوعاً. يشمل التدريب لفريق العمل. الدعم الفني والصيانة لمدة سنة. التحديثات الأمنية مشمولة طوال فترة الاشتراك.",
        "validity_days": 30,
    },
    "real_estate": {
        "sections": [
            {
                "title": "نبذة عن خدماتنا",
                "content": "حلول تقنية متقدمة لقطاع العقارات والتطوير العقاري في المملكة، تواكب النمو الكبير في القطاع ضمن رؤية 2030 ومشاريع نيوم والبحر الأحمر والقدية.",
            },
            {
                "title": "الحلول المقترحة",
                "content": "نظام إدارة العقارات (Property Management)، منصة التسويق العقاري الرقمي، جولات افتراضية 360°، نظام إدارة العملاء المحتملين (CRM عقاري)، وتحليلات السوق العقاري.",
            },
            {
                "title": "القيمة المضافة",
                "content": "تكامل مع منصات العقار السعودية، دعم التسجيل العيني، وتقارير تحليلية للسوق العقاري المحلي.",
            },
        ],
        "services": [
            {"name": "نظام إدارة العقارات", "description": "إدارة الوحدات والعقود والإيجارات", "price": "يحدد لاحقاً"},
            {"name": "منصة التسويق العقاري", "description": "موقع ومنصة لعرض العقارات مع SEO متقدم", "price": "يحدد لاحقاً"},
            {"name": "CRM عقاري", "description": "إدارة العملاء المحتملين وتتبع الصفقات", "price": "يحدد لاحقاً"},
            {"name": "جولات افتراضية", "description": "تصوير 360° وجولات تفاعلية للعقارات", "price": "يحدد لاحقاً"},
        ],
        "terms": "صلاحية العرض 30 يوماً. الأسعار لا تشمل ضريبة القيمة المضافة (15%). التنفيذ خلال 6-10 أسابيع. يشمل تدريب الفريق. دعم فني وصيانة لمدة سنة.",
        "validity_days": 30,
    },
    "construction": {
        "sections": [
            {
                "title": "نبذة عن خدماتنا",
                "content": "نوفر حلولاً تقنية متخصصة لقطاع المقاولات والبناء، مصممة لتحسين إدارة المشاريع وخفض التكاليف وزيادة الكفاءة في ظل الطفرة الإنشائية بالمملكة.",
            },
            {
                "title": "الحلول المقترحة",
                "content": "نظام إدارة المشاريع الإنشائية، تتبع التقدم والجداول الزمنية، إدارة المقاولين من الباطن، نظام المشتريات والمخزون، وتقارير التكلفة والميزانية.",
            },
            {
                "title": "المزايا",
                "content": "تتبع لحظي لتقدم المشاريع، إشعارات ذكية للتأخيرات، لوحات تحكم تنفيذية، ودعم للمعايير السعودية في البناء.",
            },
        ],
        "services": [
            {"name": "نظام إدارة المشاريع", "description": "تخطيط وتتبع ومراقبة المشاريع الإنشائية", "price": "يحدد لاحقاً"},
            {"name": "إدارة المقاولين", "description": "نظام لإدارة مقاولي الباطن والعقود", "price": "يحدد لاحقاً"},
            {"name": "نظام المشتريات", "description": "إدارة طلبات الشراء والموردين والمخزون", "price": "يحدد لاحقاً"},
            {"name": "تقارير التكلفة", "description": "تحليل التكاليف والميزانيات في الوقت الفعلي", "price": "يحدد لاحقاً"},
        ],
        "terms": "صلاحية العرض 30 يوماً. الأسعار لا تشمل ضريبة القيمة المضافة (15%). التنفيذ خلال 10-16 أسبوعاً. يشمل تدريب شامل لفريق العمل. دعم فني على مدار الساعة لمدة سنة.",
        "validity_days": 30,
    },
    "restaurant": {
        "sections": [
            {
                "title": "نبذة عن خدماتنا",
                "content": "حلول رقمية متكاملة لقطاع المطاعم والمقاهي في المملكة العربية السعودية، تساعد في تحسين العمليات وزيادة المبيعات وتعزيز تجربة العملاء.",
            },
            {
                "title": "الحلول المقترحة",
                "content": "نظام نقاط البيع (POS)، تطبيق طلبات العملاء، نظام إدارة المطبخ (KDS)، برنامج الولاء والعروض، ونظام إدارة المخزون والتكاليف.",
            },
            {
                "title": "التكاملات",
                "content": "ربط مع منصات التوصيل (هنقرستيشن، مرسول، جاهز)، أنظمة الدفع الإلكتروني، ومنصة الفوترة الإلكترونية (فاتورة).",
            },
        ],
        "services": [
            {"name": "نظام نقاط البيع", "description": "POS متكامل مع إدارة الطاولات والطلبات", "price": "يحدد لاحقاً"},
            {"name": "تطبيق الطلبات", "description": "تطبيق جوال للطلب المسبق والتوصيل", "price": "يحدد لاحقاً"},
            {"name": "إدارة المخزون", "description": "تتبع المخزون والتكاليف والهدر", "price": "يحدد لاحقاً"},
            {"name": "برنامج الولاء", "description": "نظام نقاط وعروض لزيادة تكرار الزيارات", "price": "يحدد لاحقاً"},
        ],
        "terms": "صلاحية العرض 30 يوماً. الأسعار لا تشمل ضريبة القيمة المضافة (15%). التنفيذ خلال 4-6 أسابيع. يشمل تدريب الموظفين. دعم فني لمدة سنة.",
        "validity_days": 30,
    },
    "education": {
        "sections": [
            {
                "title": "نبذة عن خدماتنا",
                "content": "حلول تعليمية رقمية متطورة تدعم التحول الرقمي في قطاع التعليم بالمملكة، متوافقة مع معايير وزارة التعليم ومنصة مدرستي.",
            },
            {
                "title": "الحلول المقترحة",
                "content": "منصة التعلم الإلكتروني (LMS)، نظام إدارة المدرسة/المعهد، بوابة أولياء الأمور، نظام الاختبارات الإلكترونية، والتقارير التحليلية لأداء الطلاب.",
            },
            {
                "title": "المزايا",
                "content": "محتوى تعليمي تفاعلي، دعم اللغة العربية بالكامل، تكامل مع نظام نور، وتقارير مفصلة للأداء الأكاديمي.",
            },
        ],
        "services": [
            {"name": "منصة التعلم الإلكتروني", "description": "LMS متكامل مع محتوى تفاعلي", "price": "يحدد لاحقاً"},
            {"name": "نظام إدارة المدرسة", "description": "إدارة الطلاب والمعلمين والجداول", "price": "يحدد لاحقاً"},
            {"name": "بوابة أولياء الأمور", "description": "تطبيق لمتابعة أداء الأبناء والتواصل مع المدرسة", "price": "يحدد لاحقاً"},
            {"name": "نظام الاختبارات", "description": "اختبارات إلكترونية مع تصحيح آلي وتحليل نتائج", "price": "يحدد لاحقاً"},
        ],
        "terms": "صلاحية العرض 30 يوماً. الأسعار لا تشمل ضريبة القيمة المضافة (15%). التنفيذ خلال 8-12 أسبوعاً. يشمل تدريب المعلمين والإداريين. دعم فني طوال العام الدراسي.",
        "validity_days": 30,
    },
    "retail": {
        "sections": [
            {
                "title": "نبذة عن خدماتنا",
                "content": "حلول تجارة إلكترونية وإدارة متاجر متكاملة لقطاع التجزئة في المملكة، تدعم التحول الرقمي وتعزز تجربة التسوق للعملاء.",
            },
            {
                "title": "الحلول المقترحة",
                "content": "متجر إلكتروني متكامل، نظام إدارة المخزون متعدد الفروع، نظام نقاط البيع، برنامج الولاء والعروض الترويجية، والتحليلات التجارية المتقدمة.",
            },
            {
                "title": "التكاملات",
                "content": "ربط مع شركات الشحن السعودية (سمسا، أرامكس، ناقل)، بوابات الدفع (STC Pay، مدى، تابي)، ومنصة زاتكا للفوترة الإلكترونية.",
            },
        ],
        "services": [
            {"name": "متجر إلكتروني", "description": "منصة تجارة إلكترونية متكاملة مع تصميم احترافي", "price": "يحدد لاحقاً"},
            {"name": "نظام إدارة المخزون", "description": "إدارة مخزون متعدد الفروع والمستودعات", "price": "يحدد لاحقاً"},
            {"name": "نظام نقاط البيع", "description": "POS لنقاط البيع مع تكامل المخزون", "price": "يحدد لاحقاً"},
            {"name": "التحليلات التجارية", "description": "لوحة تحكم تحليلية للمبيعات وسلوك العملاء", "price": "يحدد لاحقاً"},
        ],
        "terms": "صلاحية العرض 30 يوماً. الأسعار لا تشمل ضريبة القيمة المضافة (15%). التنفيذ خلال 6-8 أسابيع. يشمل تدريب فريق العمل. دعم فني وصيانة لمدة سنة.",
        "validity_days": 30,
    },
    "automotive": {
        "sections": [
            {
                "title": "نبذة عن خدماتنا",
                "content": "حلول رقمية متخصصة لقطاع السيارات في المملكة، من معارض البيع إلى مراكز الصيانة ووكالات التأجير، مصممة لتحسين الكفاءة وزيادة رضا العملاء.",
            },
            {
                "title": "الحلول المقترحة",
                "content": "نظام إدارة المعرض (DMS)، نظام مواعيد الصيانة، تقييم وتسعير المركبات المستعملة، نظام إدارة العملاء المحتملين، وتطبيق العملاء.",
            },
            {
                "title": "المزايا",
                "content": "تكامل مع نظام أبشر لنقل الملكية، ربط مع شركات التأمين، وتقارير تحليلية لأداء المبيعات.",
            },
        ],
        "services": [
            {"name": "نظام إدارة المعرض", "description": "إدارة المخزون والمبيعات والعملاء", "price": "يحدد لاحقاً"},
            {"name": "نظام الصيانة", "description": "إدارة مواعيد وأوامر الصيانة وقطع الغيار", "price": "يحدد لاحقاً"},
            {"name": "تقييم المركبات", "description": "نظام ذكي لتقييم وتسعير السيارات المستعملة", "price": "يحدد لاحقاً"},
            {"name": "تطبيق العملاء", "description": "تطبيق جوال لتصفح المعروض وحجز مواعيد الصيانة", "price": "يحدد لاحقاً"},
        ],
        "terms": "صلاحية العرض 30 يوماً. الأسعار لا تشمل ضريبة القيمة المضافة (15%). التنفيذ خلال 8-12 أسبوعاً. يشمل تدريب شامل. دعم فني لمدة سنة.",
        "validity_days": 30,
    },
    "general": {
        "sections": [
            {
                "title": "نبذة عن خدماتنا",
                "content": "نقدم حلولاً رقمية متكاملة تساعد الشركات في المملكة العربية السعودية على التحول الرقمي وتحسين العمليات وزيادة الإيرادات.",
            },
            {
                "title": "الحلول المقترحة",
                "content": "نظام إدارة علاقات العملاء (CRM)، أتمتة العمليات التجارية، منصة التسويق الرقمي، نظام التقارير والتحليلات، والتكامل مع الأنظمة الحالية.",
            },
            {
                "title": "لماذا نحن",
                "content": "فريق سعودي متخصص، خبرة واسعة في السوق المحلي، دعم فني باللغة العربية على مدار الساعة، وحلول قابلة للتخصيص حسب احتياجاتكم.",
            },
        ],
        "services": [
            {"name": "نظام CRM", "description": "إدارة شاملة لعلاقات العملاء والمبيعات", "price": "يحدد لاحقاً"},
            {"name": "أتمتة العمليات", "description": "أتمتة سير العمل والعمليات المتكررة", "price": "يحدد لاحقاً"},
            {"name": "التسويق الرقمي", "description": "حملات تسويقية متكاملة عبر القنوات الرقمية", "price": "يحدد لاحقاً"},
            {"name": "التحليلات والتقارير", "description": "لوحات تحكم تحليلية لدعم اتخاذ القرار", "price": "يحدد لاحقاً"},
        ],
        "terms": "صلاحية العرض 30 يوماً من تاريخ الإصدار. الأسعار لا تشمل ضريبة القيمة المضافة (15%). الدفع على دفعات حسب مراحل التنفيذ. يشمل التدريب والدعم الفني لمدة سنة.",
        "validity_days": 30,
    },
}


# ---------------------------------------------------------------------------
# ProposalGenerator service
# ---------------------------------------------------------------------------

class ProposalGenerator:
    """Generates structured Arabic proposal content using AI and industry templates."""

    def __init__(self):
        self.ai = _ai_brain_singleton

    async def generate_proposal_content(
        self,
        lead_data: dict,
        deal_data: dict,
        industry: str = "general",
        services_list: Optional[list[str]] = None,
        custom_instructions: Optional[str] = None,
    ) -> dict:
        """
        Generate structured proposal content using AIBrain.

        Returns a JSONB-compatible dict with:
            sections, services, terms, validity_days
        """
        # Start with the industry template as a baseline
        template = self.get_industry_template(industry)

        # Build the user message with all available context
        context_parts = []

        if lead_data:
            context_parts.append(f"بيانات العميل المحتمل:\n{json.dumps(lead_data, ensure_ascii=False, indent=2)}")
        if deal_data:
            context_parts.append(f"بيانات الصفقة:\n{json.dumps(deal_data, ensure_ascii=False, indent=2)}")

        context_parts.append(f"القطاع: {industry}")

        if services_list:
            context_parts.append(f"الخدمات المطلوبة: {', '.join(services_list)}")

        if custom_instructions:
            context_parts.append(f"تعليمات إضافية: {custom_instructions}")

        context_parts.append(
            f"القالب الأساسي للقطاع (استخدمه كمرجع وطوّره بناءً على بيانات العميل):\n"
            f"{json.dumps(template, ensure_ascii=False, indent=2)}"
        )

        user_message = "\n\n".join(context_parts)
        user_message += "\n\nأنشئ عرض تقديمي احترافي مخصص لهذا العميل. أجب بصيغة JSON فقط."

        try:
            result = await self.ai.think_json(
                system_prompt=PROPOSAL_SYSTEM_PROMPT,
                user_message=user_message,
                temperature=0.4,
            )

            # Validate the structure; if AI returned a parse error, fall back to template
            if result.get("parse_error"):
                logger.warning(
                    "AI returned unparseable response for proposal generation, "
                    "falling back to industry template. Raw: %s",
                    result.get("raw_response", "")[:500],
                )
                return template

            # Ensure required keys exist
            return self._normalize_content(result, template)

        except Exception:
            logger.exception("AI proposal generation failed, falling back to industry template")
            return template

    def get_industry_template(self, industry: str) -> dict:
        """
        Return a pre-built proposal template for the given industry.

        Supported industries:
            salon, clinic, real_estate, construction, restaurant,
            education, retail, automotive, general

        Falls back to 'general' for unknown industries.
        """
        return INDUSTRY_TEMPLATES.get(industry, INDUSTRY_TEMPLATES["general"]).copy()

    @staticmethod
    def _normalize_content(content: dict, fallback: dict) -> dict:
        """Ensure the AI-generated content has all required keys with valid types."""
        normalized = {}

        # sections: must be a list of dicts with title + content
        sections = content.get("sections")
        if isinstance(sections, list) and len(sections) > 0:
            normalized["sections"] = [
                {
                    "title": s.get("title", ""),
                    "content": s.get("content", ""),
                }
                for s in sections
                if isinstance(s, dict)
            ]
        else:
            normalized["sections"] = fallback.get("sections", [])

        # services: must be a list of dicts
        services = content.get("services")
        if isinstance(services, list) and len(services) > 0:
            normalized["services"] = [
                {
                    "name": s.get("name", ""),
                    "description": s.get("description", ""),
                    "price": s.get("price", "يحدد لاحقاً"),
                }
                for s in services
                if isinstance(s, dict)
            ]
        else:
            normalized["services"] = fallback.get("services", [])

        # terms: must be a non-empty string
        terms = content.get("terms")
        if isinstance(terms, str) and terms.strip():
            normalized["terms"] = terms.strip()
        else:
            normalized["terms"] = fallback.get("terms", "")

        # validity_days: must be a positive int
        validity = content.get("validity_days")
        if isinstance(validity, int) and validity > 0:
            normalized["validity_days"] = validity
        else:
            normalized["validity_days"] = fallback.get("validity_days", 30)

        return normalized
