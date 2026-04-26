"""Content Strategy Agent — generates platform-specific content ideas and drafts."""
from dealix_gtm_os.agents.base_agent import BaseAgent

CONTENT_TEMPLATES = {
    "linkedin": {
        "post_types": ["مشكلة → إحصائية", "حل → بدون بيع", "قصة مؤسس", "ROI", "نصيحة", "وكالات → فرصة"],
        "sample_hooks": [
            "كل حملة تجيب leads ثم تضيع بسبب بطء المتابعة هي ميزانية محترقة.",
            "60% من استفسارات العملاء في السعودية ما تُتابع خلال أول ساعة.",
            "الفرق بين وكالة تجيب leads ووكالة تحوّل leads.",
            "سألت 20 مدير مبيعات سعودي: أكبر مشكلة = ما عندهم وقت يردون.",
        ],
        "cta_options": ["رد بكلمة Demo", "احجز 10 دقائق", "كن شريك Dealix"],
        "frequency": "يومياً",
        "rules": ["70% قيمة / 30% عرض", "لا بيع مباشر في كل بوست", "Arabic first"],
    },
    "x_twitter": {
        "post_types": ["founder insight", "market observation", "data point", "thread"],
        "sample_hooks": [
            "الـlead ما يضيع في الإعلان. يضيع في أول 10 دقائق بعد الإعلان.",
            "مو AI يستبدل البشر. AI يرد الساعة 2 بالليل.",
            "CRM يسجّل بعد المحادثة. بس مين يبدأ المحادثة؟",
        ],
        "frequency": "يومياً",
        "rules": ["قصير ومباشر", "لا automated replies", "ردود يدوية ذات قيمة فقط"],
    },
    "instagram": {
        "post_types": ["carousel", "reel", "story", "story poll"],
        "sample_topics": [
            "رحلة استفسار ضائع (carousel 5 slides)",
            "3 قتلة المبيعات في السعودية (carousel)",
            "45 ثانية — demo حي (reel 30 sec)",
            "كم تاخذ ترد على lead؟ (story poll)",
        ],
        "frequency": "3x/أسبوع",
        "rules": ["visual + Arabic", "لا mass cold DM", "inbound engagement فقط"],
    },
    "whatsapp_status": {
        "sample_updates": [
            "أطلقت Dealix — يرد على عملائك خلال 45 ثانية",
            "أبحث عن 3 شركات للتجربة — 499 ريال فقط",
            "كيف الوكالات تربح 1,980 ريال/شهر إضافي",
        ],
        "frequency": "يومياً",
        "rules": ["للشبكة الحالية فقط", "لا blast"],
    },
}


class ContentStrategyAgent(BaseAgent):
    name = "content_strategy"
    description = "Generates platform-specific content ideas and drafts"

    async def run(self, input_data: dict) -> dict:
        platform = input_data.get("platform", "all")
        day_number = input_data.get("day_number", 1)

        if platform != "all" and platform in CONTENT_TEMPLATES:
            template = CONTENT_TEMPLATES[platform]
            hooks = template.get("sample_hooks", template.get("sample_topics", template.get("sample_updates", [""])))
            hook_idx = (day_number - 1) % len(hooks)
            return {
                "platform": platform,
                "today_hook": hooks[hook_idx],
                "post_type": template["post_types"][(day_number - 1) % len(template["post_types"])],
                "cta": template.get("cta_options", ["احجز demo"])[0] if "cta_options" in template else "احجز demo",
                "rules": template["rules"],
                "frequency": template["frequency"],
            }

        today_pack = {}
        for plat, template in CONTENT_TEMPLATES.items():
            hooks = template.get("sample_hooks", template.get("sample_topics", template.get("sample_updates", [""])))
            hook_idx = (day_number - 1) % len(hooks)
            today_pack[plat] = {
                "hook": hooks[hook_idx],
                "type": template["post_types"][(day_number - 1) % len(template["post_types"])] if "post_types" in template else "update",
                "rules": template["rules"],
            }

        return {"day_number": day_number, "content_pack": today_pack}
