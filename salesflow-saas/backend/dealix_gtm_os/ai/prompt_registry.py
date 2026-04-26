"""Prompt registry — versioned prompts with stable prefix for caching."""

SYSTEM_PREFIX = """أنت Dealix AI — نظام ذكاء أعمال سعودي.
مهمتك: تحليل الشركات، تحديد الفرص، اختيار القنوات، وتوليد رسائل مخصصة بالعربي السعودي.

القواعد:
- لا تخترع معلومات. قل "غير متأكد" إذا ما تعرف.
- لا تبالغ. لا تقول "مضمون" أو "100%".
- أجب بـ JSON فقط حسب الـ schema المطلوب.
- اللغة: عربي سعودي (مو فصحى).
"""

PROMPTS = {
    "company_research": {
        "version": "1.0",
        "system": SYSTEM_PREFIX,
        "user_template": """حلل هذه الشركة:
اسم: {name}
القطاع: {sector}
المدينة: {city}
الوصف: {description}

أرجع JSON بالضبط:
{{"business_summary": "...", "products_services": [...], "target_customers": [...], "revenue_model": "...", "lead_channels": [...], "pain_points": [...], "partnership_potential": "...", "opportunity_types": [...], "confidence": 0.0-1.0}}""",
    },
    "message_generation": {
        "version": "1.0",
        "system": SYSTEM_PREFIX,
        "user_template": """اكتب رسالة outreach لهذه الشركة:
اسم: {name}
القطاع: {sector}
الألم: {pain}
القناة: {channel}
العرض: {offer}

الرسالة لازم:
- تبدأ بالسلام
- تذكر اسم الشركة
- تذكر ألم واضح
- تقدم حل بسيط
- CTA صغير (ديمو 10 دقائق)
- opt-out في النهاية
- أقل من 150 كلمة

أرجع JSON:
{{"subject": "...", "body": "...", "cta": "...", "follow_up_24h": "...", "follow_up_72h": "..."}}""",
    },
    "negotiation": {
        "version": "1.0",
        "system": SYSTEM_PREFIX,
        "user_template": """العميل اعترض بـ: "{objection}"
سياق: {context}

أرجع JSON:
{{"response": "...", "next_action": "...", "fallback": "...", "confidence": 0.0-1.0}}""",
    },
}

def get_prompt(name: str, **kwargs) -> tuple[str, str]:
    """Returns (system_prompt, user_prompt) with variables filled."""
    p = PROMPTS.get(name)
    if not p:
        raise ValueError(f"Unknown prompt: {name}")
    system = p["system"]
    user = p["user_template"].format(**{k: v or "" for k, v in kwargs.items()})
    return system, user
