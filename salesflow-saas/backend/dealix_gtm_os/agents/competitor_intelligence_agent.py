"""Competitor Intelligence Agent — maps competitor features and Dealix advantages."""
from dealix_gtm_os.agents.base_agent import BaseAgent

COMPETITOR_MAP = {
    "hubspot": {
        "name": "HubSpot",
        "strengths": ["CRM كامل", "workflows", "lead scoring", "WhatsApp CRM"],
        "weakness": "غالي (500$+/شهر)، معقّد، إنجليزي",
        "dealix_advantage": "أبسط، أرخص (990 ريال)، عربي أولاً، done-for-you",
        "positioning": "HubSpot يخزّن. Dealix يحرّك.",
    },
    "gohighlevel": {
        "name": "GoHighLevel",
        "strengths": ["agency OS", "CRM + funnels", "automation", "white-label"],
        "weakness": "إنجليزي، setup معقّد، ما يفهم واتساب السعودي",
        "dealix_advantage": "عربي، واتساب أولاً، done-for-you، pilot 499",
        "positioning": "GHL يحتاج أسابيع setup. Dealix يشتغل خلال يوم.",
    },
    "apollo": {
        "name": "Apollo",
        "strengths": ["275M+ contacts", "enrichment", "buyer intent", "sequences"],
        "weakness": "أداة بحث مو تنفيذ. إنجليزي. ضعيف للسعودية",
        "dealix_advantage": "يبحث + يرسل + يتابع + يحجز",
        "positioning": "Apollo يعطيك أرقام. Dealix يحوّلها لمواعيد.",
    },
    "clay": {
        "name": "Clay",
        "strengths": ["AI research", "enrichment", "personalization", "waterfall data"],
        "weakness": "مكلّف، معقّد، إنجليزي، ما ينفّذ",
        "dealix_advantage": "يبحث بالعربي + يفهم السياق المحلي + ينفّذ",
        "positioning": "Clay يجهّز. Dealix يجهّز وينفّذ.",
    },
    "lemlist": {
        "name": "lemlist",
        "strengths": ["multichannel", "email + LinkedIn + phone", "manual tasks"],
        "weakness": "إنجليزي، يركّز على cold outreach",
        "dealix_advantage": "manual-approved بدل automated spam. عربي",
        "positioning": "lemlist يرسل. Dealix يدير المسار كامل.",
    },
    "manychat": {
        "name": "Manychat",
        "strengths": ["Instagram/WhatsApp flows", "comment-to-DM", "automation"],
        "weakness": "bot replies فقط — ما يؤهل ولا يتابع ولا يحجز",
        "dealix_advantage": "مسار كامل: رد → تصنيف → متابعة → حجز → دفع",
        "positioning": "Manychat يرد. Dealix يبيع.",
    },
}


class CompetitorIntelligenceAgent(BaseAgent):
    name = "competitor_intelligence"
    description = "Maps competitor features and identifies Dealix advantages"

    async def run(self, input_data: dict) -> dict:
        competitor = input_data.get("competitor", "").lower()

        if competitor and competitor in COMPETITOR_MAP:
            return COMPETITOR_MAP[competitor]

        return {
            "competitors": list(COMPETITOR_MAP.keys()),
            "dealix_unique_advantages": [
                "عربي سعودي أولاً — مو ترجمة",
                "واتساب أولاً — القناة #1 في السعودية",
                "Done-for-you — مو DIY software",
                "الوكالات تبيعه كخدمة — مو بس تستخدمه",
                "Pilot 499 ريال — لا مخاطرة",
                "مؤسس يرد على الهاتف — 0597788539",
                "تحويل بنكي محلي (الإنماء)",
                "Service exchange model — فريد",
                "Manual approval gates — لا spam",
                "Learning loop — يتحسن أسبوعياً",
            ],
            "full_map": COMPETITOR_MAP,
        }
