from dealix_gtm_os.agents.base_agent import BaseAgent
from dealix_gtm_os.models.message import OutreachMessage, ChannelType, AutomationLevel

SECTOR_MESSAGES = {
    "agency": {
        "first_line": "شفت أنكم تقدمون خدمات تسويق/دعاية لعملاء.",
        "pain": "عملاؤكم يصرفون على إعلانات والـ leads تضيع بعد الكلك.",
        "offer": "أضف خدمة متابعة leads لعملائك — 20% لك من كل عميل.",
    },
    "real_estate": {
        "first_line": "لاحظت أن نشاطكم في العقار يعتمد على الاستفسارات.",
        "pain": "60% من استفسارات الأسعار والمواقع ما تُتابع خلال ساعة.",
        "offer": "Dealix يرد خلال 45 ثانية ويحجز موعد معاينة.",
    },
    "saas": {
        "first_line": "شفت منتجكم — مشروع قوي.",
        "pain": "الـ leads من الموقع تبرد خلال ساعة.",
        "offer": "Dealix يرد فوراً ويؤهل ويحجز demo تلقائياً.",
    },
}

class MessageGenerationAgent(BaseAgent):
    name = "message_generation"
    description = "Generates personalized Arabic outreach messages"

    async def run(self, input_data: dict) -> dict:
        company = input_data.get("name", "الشركة")
        sector = input_data.get("sector", "").lower().replace(" ", "_")
        channel = input_data.get("channel", "email")
        msgs = SECTOR_MESSAGES.get(sector, SECTOR_MESSAGES.get("saas"))
        body = f"""السلام عليكم فريق {company}،

أنا سامي من Dealix.

{msgs['first_line']}

المشكلة: {msgs['pain']}

الحل: {msgs['offer']}

نسوي pilot 7 أيام بـ 499 ريال مع ضمان استرداد كامل.
يناسبكم ديمو 10 دقائق؟
📅 calendly.com/sami-assiri11/dealix-demo

سامي العسيري | مؤسس Dealix | dealix.me

إذا ما يناسبكم هالنوع من الرسائل، ردوا "إيقاف"."""

        msg = OutreachMessage(
            target_company=company,
            channel=ChannelType(channel) if channel in [c.value for c in ChannelType] else ChannelType.EMAIL,
            automation_level=AutomationLevel.MANUAL_REQUIRED,
            subject=f"فريق {company} — فكرة لتحسين متابعة العملاء",
            first_line=msgs["first_line"],
            body=body,
            cta="يناسبكم ديمو 10 دقائق؟",
            follow_up_24h=f"متابعة سريعة — أقدر أوريكم خلال 10 دقائق كيف Dealix يحول الاستفسارات لمتابعة وحجز.",
            follow_up_72h=f"آخر متابعة مني. مهتم → رد 'مهتم'. إيقاف → رد 'إيقاف'.",
            approval_required=True,
        )
        return msg.model_dump()
