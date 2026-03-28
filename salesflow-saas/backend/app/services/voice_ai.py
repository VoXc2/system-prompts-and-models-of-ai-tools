"""
Dealix Voice AI Service - Phone call automation.
Integrates with Vapi/Retell for voice agents.
Role: qualifier, not full closer. Handles after-hours, booking, follow-ups.
"""
import httpx
from typing import Optional
from datetime import datetime, timezone
from app.config import get_settings
from app.services.ai_brain import ai_brain

settings = get_settings()

VOICE_PERSONALITY_AR = """أنت مساعد Dealix الصوتي.

## شخصيتك:
- اسمك: مساعد Dealix
- لهجة: سعودية واضحة، لطيفة، مباشرة
- مهنية عالية لكن ودودة
- لا تتظاهر أنك إنسان - وضّح أنك مساعد ذكي

## مهامك:
1. استقبال المكالمات خارج الدوام
2. تأهيل العميل (اسم، شركة، احتياج، ميزانية تقريبية)
3. حجز مواعيد للعروض التوضيحية
4. الرد على الأسئلة الأساسية عن Dealix
5. تحويل للفريق البشري إذا لزم

## قواعد صارمة:
- لا تعد بأسعار نهائية
- لا تعطي تعهدات قانونية أو تعاقدية
- لا تتكلم عن مميزات غير موجودة
- إذا سألك سؤال ما تعرف جوابه قل: "خلني أوصل الفريق يتواصلون معك"
- كل مكالمة يتم تسجيل ملخصها

## معلومات عن Dealix:
- نظام ذكاء تشغيلي للمبيعات والإيرادات
- مصمم للشركات السعودية الصغيرة والمتوسطة
- يدعم: واتساب بزنس، أتمتة المتابعة، تقارير، عروض أسعار
- القطاعات: عيادات، عقارات، مقاولات، صالونات
- تجربة مجانية 14 يوم
- ساعات العمل: الأحد - الخميس، 9 ص - 6 م
"""


class VoiceAIService:
    """Voice AI agent integration."""

    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.provider = "vapi"  # or "retell"

    async def create_assistant(self, name: str = "Dealix Voice Agent", industry: str = "general") -> dict:
        """Create a voice AI assistant on Vapi."""
        if not settings.VAPI_API_KEY:
            return {"error": "Voice AI not configured", "setup": "Set VAPI_API_KEY in .env"}

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://api.vapi.ai/assistant",
                headers={
                    "Authorization": f"Bearer {settings.VAPI_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "name": name,
                    "model": {
                        "provider": "openai",
                        "model": "gpt-4o-mini",
                        "systemPrompt": VOICE_PERSONALITY_AR,
                        "temperature": 0.7,
                    },
                    "voice": {
                        "provider": "11labs",
                        "voiceId": "arabic-male-1",
                    },
                    "firstMessage": "السلام عليكم، أنا مساعد Dealix الذكي. كيف أقدر أساعدك؟",
                    "endCallMessage": "شكراً لتواصلك مع Dealix. فريقنا يتواصل معك قريباً. مع السلامة!",
                    "transcriber": {
                        "provider": "deepgram",
                        "language": "ar",
                    },
                    "serverUrl": f"{settings.API_URL}/api/v1/voice/webhook",
                    "endCallFunctionEnabled": True,
                    "recordingEnabled": True,
                },
            )
            return response.json()

    async def make_outbound_call(self, phone_number: str, assistant_id: str = None) -> dict:
        """Initiate an outbound call via Voice AI."""
        if not settings.VAPI_API_KEY:
            return {"error": "Voice AI not configured"}

        aid = assistant_id or settings.VAPI_ASSISTANT_ID
        if not aid:
            return {"error": "No assistant configured"}

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://api.vapi.ai/call/phone",
                headers={
                    "Authorization": f"Bearer {settings.VAPI_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "assistantId": aid,
                    "phoneNumberId": settings.WHATSAPP_PHONE_NUMBER_ID,
                    "customer": {"number": phone_number},
                },
            )
            return response.json()

    async def process_call_webhook(self, event: dict) -> dict:
        """Process incoming call webhook from Vapi."""
        event_type = event.get("message", {}).get("type", "")

        if event_type == "transcript":
            transcript = event.get("message", {}).get("transcript", "")
            role = event.get("message", {}).get("role", "")
            return {"action": "log_transcript", "role": role, "text": transcript}

        elif event_type == "end-of-call-report":
            report = event.get("message", {})
            summary = report.get("summary", "")
            duration = report.get("duration", 0)
            transcript_text = report.get("transcript", "")

            # AI generates structured summary
            analysis = await ai_brain.think_json(
                system_prompt="Analyze this call transcript and extract: customer_name, company, needs, budget_mentioned, interest_level (1-10), next_action, and summary in Arabic.",
                user_message=transcript_text,
            )

            return {
                "action": "call_completed",
                "duration": duration,
                "summary": summary,
                "analysis": analysis,
                "transcript": transcript_text,
            }

        elif event_type == "function-call":
            function_name = event.get("message", {}).get("functionCall", {}).get("name", "")
            params = event.get("message", {}).get("functionCall", {}).get("parameters", {})

            if function_name == "book_demo":
                return {
                    "action": "book_demo",
                    "customer_name": params.get("name", ""),
                    "phone": params.get("phone", ""),
                    "preferred_time": params.get("time", ""),
                }
            elif function_name == "transfer_to_human":
                return {
                    "action": "transfer",
                    "reason": params.get("reason", ""),
                }

        return {"action": "ignored", "event_type": event_type}

    async def get_call_history(self, limit: int = 50) -> list:
        """Get recent call history from Vapi."""
        if not settings.VAPI_API_KEY:
            return []

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                "https://api.vapi.ai/call",
                headers={"Authorization": f"Bearer {settings.VAPI_API_KEY}"},
                params={"limit": limit},
            )
            if response.status_code != 200:
                return []
            return response.json()

    async def generate_call_summary(self, transcript: str) -> dict:
        """AI-generated call summary and action items."""
        return await ai_brain.think_json(
            system_prompt="""أنت محلل مكالمات مبيعات. حلل هذا النص واستخرج:
- summary: ملخص المكالمة بالعربي
- customer_name: اسم العميل
- company: اسم الشركة
- needs: احتياجات العميل (قائمة)
- interest_level: مستوى الاهتمام 1-10
- objections: اعتراضات إن وجدت
- next_action: الإجراء التالي
- should_follow_up: true/false
- follow_up_urgency: low/medium/high
رد بـ JSON فقط.""",
            user_message=transcript,
        )
