from dealix_gtm_os.agents.base_agent import BaseAgent

OBJECTION_RESPONSES = {
    "غالي": "499 ريال لـ 7 أيام مع ضمان استرداد. لو حفظنا lead واحد = أكثر من 499.",
    "عندنا CRM": "CRM يخزّن. Dealix يحرّك العميل للخطوة التالية. الطبقة اللي قبل.",
    "نفكّر": "طبعاً. أرسل لكم مثال عملي تشوفونه بهدوء. وش يخليكم تترددون؟",
    "أرسل تفاصيل": "10 دقائق ديمو أوضح من أي PDF. يناسبكم بكرا؟",
    "مو الحين": "فاهم. أرسل لكم ملخص ترجعون لي وقت ما يناسبكم.",
    "عندنا وكالة": "ممتاز — Dealix يكمّل شغل الوكالة بعد الإعلان.",
    "ما نعرفكم": "عادي — نحن جدد. Pilot 499 ريال + ضمان. ما فيه مخاطرة.",
    "كم السعر": "Pilot 499 ريال + ضمان. Starter 990/شهر. وكالات 20% لهم.",
    "white-label": "ممكن لاحقاً بعد 3 عملاء. الحين نثبت الخدمة باسم Dealix.",
    "مين يملك العميل": "العميل عميلك. أنت العلاقة، أنا التشغيل.",
}

class NegotiationAgent(BaseAgent):
    name = "negotiation"
    description = "Handles objections and negotiation"

    async def run(self, input_data: dict) -> dict:
        objection = input_data.get("objection", "")
        for key, response in OBJECTION_RESPONSES.items():
            if key in objection:
                return {"objection": objection, "response": response, "next_action": "follow_up", "confidence": 0.9}
        return {"objection": objection, "response": "أفهمك. خلني أشرح لك بالضبط كيف Dealix يخدم نشاطكم.", "next_action": "demo", "confidence": 0.6}
