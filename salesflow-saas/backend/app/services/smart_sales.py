"""
Dealix Smart Sales Agent - Handles intelligent sales conversations.
This is the brain behind WhatsApp auto-replies and outreach.
"""
import json
from typing import Optional
from datetime import datetime, timezone
from app.services.ai_brain import ai_brain

# Industry-specific knowledge bases
HEALTHCARE_KNOWLEDGE = """
## معرفة قطاع العيادات والصحة:
- التحديات: إدارة المواعيد، متابعة المرضى، التسويق الرقمي، المنافسة
- الحلول: نظام حجز أوتوماتيكي، تذكير بالمواعيد، متابعة ما بعد الزيارة
- الأسعار النموذجية: استشارة 200-500 ريال، علاج أسنان 500-5000 ريال
- رؤية 2030: التحول الرقمي في القطاع الصحي، ملف صحي إلكتروني موحد
- نقاط البيع: زيادة الحجوزات 40%، تقليل عدم الحضور 60%، متابعة تلقائية 24/7
- ROI: كل 1 ريال استثمار = 5-10 ريال عائد
"""

REALESTATE_KNOWLEDGE = """
## معرفة قطاع العقارات (الرياض):
- التحديات: منافسة شديدة، عملاء كثير بدون متابعة، عروض كثيرة بدون تنظيم
- الحلول: متابعة تلقائية، مطابقة عميل-عقار ذكية، تقارير أداء الوسطاء
- أحياء الرياض الأكثر طلب: النرجس، الياسمين، حطين، العارض، الملقا، الربيع
- متوسط الأسعار: شقة 500K-1.5M، فيلا 1.5M-5M، أرض 300K-2M
- رؤية 2030: برنامج الإسكان، صندوق التنمية العقاري، نيوم
- نقاط البيع: إغلاق صفقات أسرع 3x، متابعة كل عميل، عرض عقارات بالواتساب
- ROI: كل صفقة عمولة 2.5% = آلاف الريالات
"""

CONSTRUCTION_KNOWLEDGE = """
## معرفة قطاع المقاولات والبناء:
- التحديات: تتبع المشاريع، إدارة المناقصات، متابعة العمالة، تأخر الدفعات، المنافسة على العقود
- الحلول: نظام متابعة مشاريع ذكي، إدارة عروض أسعار، تقارير تقدم العمل، تنبيهات الدفعات
- أنواع المشاريع: سكني، تجاري، حكومي، بنية تحتية، صيانة
- رؤية 2030: مشاريع نيوم، ذا لاين، القدية، مشروع البحر الأحمر، أمالا، جدة داون تاون
- متوسط قيم المشاريع: صيانة 50K-500K، سكني 500K-5M، تجاري 5M-50M
- نقاط البيع: تتبع كل مناقصة، متابعة المقاولين الباطن، تقارير لحظية للمالك
- التراخيص: تصنيف المقاولين من 1-5، رخصة بلدية، شهادة السلامة
- ROI: تقليل تأخر المشاريع 30%، زيادة فوز المناقصات 25%
"""

SALON_KNOWLEDGE = """
## معرفة قطاع الصالونات والتجميل:
- التحديات: إدارة المواعيد، عدم حضور العملاء، المنافسة، الاحتفاظ بالعميلات
- الحلول: نظام حجز أونلاين، تذكير بالمواعيد، برنامج ولاء، عروض موسمية تلقائية
- الخدمات: قص وصبغ 200-1500 ريال، بروتين 500-2000، عناية بشرة 300-1500، مكياج 500-3000
- رؤية 2030: تمكين المرأة السعودية، نمو قطاع التجميل 15% سنوياً
- نقاط البيع: تقليل عدم الحضور 60%، زيادة الحجوزات المتكررة 45%، عروض مستهدفة
- التسويق: إنستقرام أساسي، سناب شات، واتساب للحجز، تيك توك للمحتوى
- الموسمية: رمضان وعيد الفطر وعيد الأضحى واليوم الوطني = ذروة الطلب
- ROI: كل عميلة متكررة = 5000-15000 ريال سنوياً
"""

RESTAURANT_KNOWLEDGE = """
## معرفة قطاع المطاعم والأغذية:
- التحديات: المنافسة الشديدة، إدارة التوصيل، تقييمات العملاء، تكلفة التسويق
- الحلول: نظام طلبات متكامل، برنامج ولاء، إدارة تقييمات، حملات واتساب
- متوسط الإنفاق: وجبة سريعة 25-50 ريال، كافيه 30-80، مطعم عائلي 100-300، فاين داينينق 300+
- رؤية 2030: قطاع الترفيه والسياحة، موسم الرياض، مهرجانات الطعام
- نقاط البيع: زيادة الطلبات المباشرة (بدون عمولة التطبيقات)، عملاء متكررين، عروض ذكية
- المنصات: هنقرستيشن، جاهز، مرسول، طلبات — عمولة 15-30%
- التسويق: إنستقرام + سناب + تيك توك + واتساب
- ROI: تحويل عميل من تطبيق لطلب مباشر = توفير 20-30% من العمولة
"""

EDUCATION_KNOWLEDGE = """
## معرفة قطاع التعليم والتدريب:
- التحديات: جذب الطلاب، متابعة التسجيل، التواصل مع أولياء الأمور، المنافسة
- الحلول: نظام تسجيل إلكتروني، متابعة أولياء الأمور، تقارير أداء، حملات تسويقية
- الأنواع: مدارس خاصة، معاهد تدريب، أكاديميات لغات، مراكز تعليم عن بعد
- رؤية 2030: التحول الرقمي في التعليم، أكاديمية الرقمية، مبادرة تعليم المستقبل
- الأسعار: دورة تدريبية 500-5000 ريال، رسوم مدرسة 15K-80K سنوياً
- نقاط البيع: زيادة التسجيل 35%، تقليل الانسحاب 25%، تواصل فوري مع الأهالي
- المواسم: بداية العام الدراسي (سبتمبر)، الفصل الثاني (يناير)، الصيفي (يونيو)
- ROI: كل طالب جديد = 15K-80K ريال سنوياً
"""

RETAIL_KNOWLEDGE = """
## معرفة قطاع التجزئة:
- التحديات: المنافسة مع التجارة الإلكترونية، إدارة المخزون، ولاء العملاء، التسويق
- الحلول: CRM متكامل، برنامج ولاء، حملات واتساب، تتبع المبيعات
- رؤية 2030: تنويع الاقتصاد، نمو التجارة الإلكترونية، تمكين المرأة في التجزئة
- الأنواع: ملابس، إلكترونيات، أثاث، مستلزمات منزلية، عطور ومستحضرات
- نقاط البيع: زيادة معدل العودة 40%، عروض مستهدفة بناءً على سلوك الشراء
- التسويق: واتساب (الأقوى)، إنستقرام، سناب شات، تيك توك
- المواسم: الجمعة البيضاء، رمضان، الأعياد، اليوم الوطني، موسم الرياض
- ROI: عميل متكرر ينفق 3-5x أكثر من عميل جديد
"""

AUTOMOTIVE_KNOWLEDGE = """
## معرفة قطاع السيارات:
- التحديات: دورة بيع طويلة، متابعة العملاء المهتمين، إدارة المعارض، التمويل
- الحلول: متابعة تلقائية للمهتمين، حجز تجربة قيادة، مقارنة موديلات، تقارير مبيعات
- الأنواع: وكالات رسمية، معارض مستعمل، تأجير، قطع غيار، صيانة
- رؤية 2030: السيارات الكهربائية، لوسيد في السعودية، مدينة السيارات
- متوسط الأسعار: اقتصادية 60K-100K، متوسطة 100K-200K، فاخرة 200K-500K، سوبر 500K+
- نقاط البيع: متابعة كل عميل مهتم، حجز تجربة قيادة أوتوماتيك، عروض تمويل مخصصة
- دورة البيع: 2-8 أسابيع من أول اهتمام للشراء
- ROI: كل صفقة سيارة = عمولة 2-5% = آلاف الريالات
"""

INDUSTRY_KNOWLEDGE = {
    "healthcare": HEALTHCARE_KNOWLEDGE,
    "real_estate": REALESTATE_KNOWLEDGE,
    "construction": CONSTRUCTION_KNOWLEDGE,
    "salon": SALON_KNOWLEDGE,
    "restaurant": RESTAURANT_KNOWLEDGE,
    "education": EDUCATION_KNOWLEDGE,
    "retail": RETAIL_KNOWLEDGE,
    "automotive": AUTOMOTIVE_KNOWLEDGE,
}


class SmartSalesAgent:
    """Intelligent sales conversation handler."""

    def __init__(self, tenant_id: str, industry: str = "general"):
        self.tenant_id = tenant_id
        self.industry = industry
        self.knowledge = INDUSTRY_KNOWLEDGE.get(industry, "")

    async def handle_incoming_message(
        self, message: str, lead_data: dict,
        conversation_history: list = None
    ) -> dict:
        """
        Process incoming message and generate intelligent response.
        Returns: {response, action, sentiment, should_escalate}
        """
        # Step 1: Analyze sentiment and intent
        analysis = await ai_brain.analyze_sentiment(message)
        sentiment = analysis.get("sentiment", "neutral")
        intent = analysis.get("intent", "inquiry")
        urgency = analysis.get("urgency", "medium")

        # Step 2: Check if should escalate to human
        should_escalate = self._should_escalate(intent, urgency, analysis)

        # Step 3: Generate AI response
        history_text = self._format_history(conversation_history or [])
        company_info = self._get_company_info(lead_data)

        response = await ai_brain.generate_sales_response(
            message=message,
            company_info=company_info,
            industry_info=self.knowledge,
            conversation_history=history_text,
        )

        # Step 4: Determine next action
        action = self._determine_action(intent, sentiment, lead_data)

        # Step 5: Update lead score based on conversation
        score_change = self._calculate_score_change(intent, sentiment)

        return {
            "response": response,
            "sentiment": sentiment,
            "intent": intent,
            "urgency": urgency,
            "action": action,
            "should_escalate": should_escalate,
            "score_change": score_change,
            "escalation_reason": analysis.get("suggested_action", "") if should_escalate else None,
        }

    async def generate_outreach_message(
        self, lead_data: dict, message_type: str = "أول تواصل"
    ) -> str:
        """Generate a personalized outreach message for a lead."""
        return await ai_brain.write_personalized_message(
            name=lead_data.get("name", ""),
            business=lead_data.get("company_name", lead_data.get("business", "")),
            industry=self.industry,
            city=lead_data.get("city", "الرياض"),
            source=lead_data.get("source", "واتساب"),
            message_type=message_type,
        )

    async def generate_followup_message(self, lead_data: dict, days_since_last: int) -> str:
        """Generate smart follow-up based on time elapsed."""
        if days_since_last <= 1:
            msg_type = "متابعة سريعة"
        elif days_since_last <= 3:
            msg_type = "متابعة"
        elif days_since_last <= 7:
            msg_type = "تذكير ودي"
        else:
            msg_type = "عرض خاص"

        return await ai_brain.write_personalized_message(
            name=lead_data.get("name", ""),
            business=lead_data.get("company_name", ""),
            industry=self.industry,
            message_type=msg_type,
        )

    async def handle_objection(self, objection: str, product: str = "") -> dict:
        """Handle a sales objection intelligently."""
        if not product:
            product = f"نظام Dealix لإدارة المبيعات - قطاع {self.industry}"
        return await ai_brain.handle_objection(objection, self.industry, product)

    async def create_sales_sequence(self, lead_data: dict, num_messages: int = 5) -> list:
        """Create a complete automated sales sequence for a lead."""
        sequence = []
        message_types = [
            ("أول تواصل", 0),
            ("متابعة", 2),
            ("عرض قيمة", 5),
            ("عرض خاص", 10),
            ("فرصة أخيرة", 15),
        ]

        for msg_type, delay_days in message_types[:num_messages]:
            message = await ai_brain.write_personalized_message(
                name=lead_data.get("name", ""),
                business=lead_data.get("company_name", ""),
                industry=self.industry,
                message_type=msg_type,
            )
            sequence.append({
                "day": delay_days,
                "type": msg_type,
                "message": message,
                "channel": "whatsapp",
            })

        return sequence

    def _should_escalate(self, intent: str, urgency: str, analysis: dict) -> bool:
        """Determine if conversation should be escalated to human."""
        escalate_intents = {"complaint", "ready_to_buy", "pricing_question"}
        if intent in escalate_intents:
            return True
        if urgency == "high":
            return True
        if analysis.get("sentiment") == "negative" and analysis.get("urgency") == "high":
            return True
        return False

    def _determine_action(self, intent: str, sentiment: str, lead_data: dict) -> str:
        """Determine the next CRM action to take."""
        action_map = {
            "ready_to_buy": "create_deal",
            "interested": "schedule_call",
            "inquiry": "send_info",
            "objection": "handle_objection",
            "complaint": "escalate_support",
            "not_interested": "add_to_nurture",
        }
        return action_map.get(intent, "follow_up")

    def _calculate_score_change(self, intent: str, sentiment: str) -> int:
        """Calculate lead score change based on interaction."""
        score_map = {
            "ready_to_buy": 30,
            "interested": 20,
            "inquiry": 10,
            "objection": 5,
            "neutral": 0,
            "not_interested": -10,
            "complaint": -5,
        }
        base = score_map.get(intent, 0)
        if sentiment == "positive":
            base += 5
        elif sentiment == "negative":
            base -= 5
        return base

    def _format_history(self, messages: list) -> str:
        """Format conversation history for AI context."""
        if not messages:
            return "لا يوجد محادثات سابقة"
        lines = []
        for msg in messages[-10:]:  # Last 10 messages
            direction = "العميل" if msg.get("direction") == "inbound" else "ديليكس"
            lines.append(f"{direction}: {msg.get('content', '')}")
        return "\n".join(lines)

    def _get_company_info(self, lead_data: dict) -> str:
        """Get company context info."""
        return f"""
اسم العميل: {lead_data.get('name', 'غير معروف')}
الشركة: {lead_data.get('company_name', 'غير معروف')}
المصدر: {lead_data.get('source', 'غير معروف')}
الحالة: {lead_data.get('status', 'جديد')}
النقاط: {lead_data.get('score', 0)}
"""
