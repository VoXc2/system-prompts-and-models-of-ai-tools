"""Mock LLM client — returns structured responses. Replace with real LLM later."""
import json

SECTOR_INTELLIGENCE = {
    "agency": {
        "business_summary": "وكالة تسويق تقدم خدمات إعلانية ورقمية للشركات",
        "products_services": ["إعلانات رقمية", "إدارة سوشال ميديا", "تصميم", "محتوى"],
        "target_customers": ["شركات صغيرة ومتوسطة", "عقارات", "عيادات", "متاجر"],
        "revenue_model": "رسوم خدمات شهرية + نسبة من ميزانية الإعلان",
        "lead_channels": ["موقع إلكتروني", "سوشال ميديا", "إحالات"],
        "pain_points": ["عملاء يلومونهم على ضعف التحويل", "لا recurring revenue", "leads العميل تضيع بعد الإعلان"],
        "partnership_potential": "عالي — يقدرون يبيعون Dealix كخدمة لعملائهم",
        "opportunity_types": ["agency_partner", "co_selling_partner"],
    },
    "real_estate": {
        "business_summary": "شركة تسويق أو تطوير عقاري",
        "products_services": ["بيع وتأجير عقارات", "تسويق مشاريع عقارية"],
        "target_customers": ["مشترين أفراد", "مستثمرين", "مستأجرين"],
        "revenue_model": "عمولات بيع/تأجير + رسوم تسويق",
        "lead_channels": ["واتساب", "اتصالات", "نماذج موقع", "إعلانات"],
        "pain_points": ["60% من الاستفسارات ما تُتابع", "المنافسة عالية", "فريق مبيعات صغير"],
        "partnership_potential": "متوسط — عميل مباشر",
        "opportunity_types": ["direct_customer"],
    },
    "saas": {
        "business_summary": "شركة تقنية تقدم حلول برمجية",
        "products_services": ["برمجيات سحابية", "تطبيقات", "حلول تقنية"],
        "target_customers": ["شركات", "مؤسسات"],
        "revenue_model": "اشتراكات شهرية/سنوية",
        "lead_channels": ["موقع إلكتروني", "إعلانات Google", "LinkedIn"],
        "pain_points": ["leads من الموقع تبرد", "SDR مكلّف", "فريق صغير"],
        "partnership_potential": "متوسط — عميل أو integration partner",
        "opportunity_types": ["direct_customer", "integration_partner"],
    },
}

DEFAULT_INTEL = {
    "business_summary": "شركة تقدم خدمات في السوق السعودي",
    "products_services": ["خدمات متنوعة"],
    "target_customers": ["شركات ومؤسسات"],
    "revenue_model": "رسوم خدمات",
    "lead_channels": ["واتساب", "إيميل", "موقع"],
    "pain_points": ["استفسارات ما تُتابع", "بطء الرد"],
    "partnership_potential": "متوسط",
    "opportunity_types": ["direct_customer"],
}


async def call_llm(prompt: str, context: dict | None = None) -> str:
    """Mock LLM — returns sector-based intelligence. Replace with real API later."""
    sector = (context or {}).get("sector", "")
    intel = SECTOR_INTELLIGENCE.get(sector, DEFAULT_INTEL)
    return json.dumps(intel, ensure_ascii=False)
