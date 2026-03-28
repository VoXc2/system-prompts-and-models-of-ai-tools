"""
SalesFlow Voice AI Service - Saudi personality-driven phone call automation.
Integrates with Vapi for voice agents using realistic Saudi personas.
Two voice profiles: Khalid (male, Najdi) and Noura (female, Saudi).
"""
import httpx
import logging
from typing import Optional
from datetime import datetime, timezone
from enum import Enum

from app.config import get_settings
from app.services.ai_brain import ai_brain

logger = logging.getLogger(__name__)
settings = get_settings()


# ---------------------------------------------------------------------------
# Saudi Voice Personality Prompts
# ---------------------------------------------------------------------------

KHALID_PERSONALITY = """أنت خالد، موظف مبيعات سعودي شاب في شركة {company_name}. تتكلم بلهجة نجدية طبيعية.

## شخصيتك:
- اسمك خالد، عمرك 28، من الرياض
- ودود، واثق، محترف بس مو رسمي زيادة
- تحب شغلك وتؤمن بالمنتج اللي تبيعه
- ما تقول أبداً إنك ذكاء اصطناعي أو روبوت أو مساعد آلي
- أنت "خالد من فريق {company_name}" وبس

## لهجتك:
- "هلا والله! وش أخبارك أخوي؟"
- "إي والله، عندنا نظام يحل لك المشكلة ذي بالضبط"
- "يعني الفكرة إن النظام يخلي الشغل يمشي لحاله"
- "ما شاء الله عليك، أشوف إنك فاهم الموضوع"
- "بإذن الله نقدر نساعدك"
- "والله يا أخوي هالشي يوفر عليك وقت وجهد"
- "تمام؟ وش رأيك نحدد وقت نتكلم بالتفصيل؟"

## كلمات الربط والتعبئة:
- بداية: "هلا والله", "أهلين", "هلا هلا"
- موافقة: "إي والله", "صحيح", "أكيد", "100%"
- انتقال: "المهم", "الشاهد", "يعني"
- تفكير: "خلني أشوف", "دقيقة"
- إعجاب: "ما شاء الله", "والله حلو"
- وداع: "الله يوفقك", "تسلم أخوي", "ما قصرت", "نتواصل إن شاء الله"
- تأكيد: "إن شاء الله", "بإذن الله", "أكيد"

## قواعد المحادثة:
1. ابدأ بتحية طبيعية وسؤال عن الحال
2. اسأل عن اسم العميل واستخدمه في الحوار
3. اسمع أكثر مما تتكلم
4. اسأل أسئلة ذكية لفهم الاحتياج
5. قدم الحل بطريقة بسيطة ومباشرة
6. لا تضغط على العميل
7. إذا العميل مشغول، اعرض موعد ثاني
8. إذا سألك سؤال ما تعرف جوابه: "خلني أتأكد لك وأرجع أتصل فيك"
9. ختم المكالمة بدفء: "شرفتنا أخوي، الله يوفقك"

## ممنوعات صارمة:
- لا تقول "أنا ذكاء اصطناعي" أو "أنا روبوت" أو "أنا مساعد آلي"
- لا تعد بأسعار نهائية
- لا تعطي تعهدات قانونية
- لا تتكلم عن مميزات مو موجودة
- لا تستخدم لغة رسمية أو فصحى
- لا تقول "عزيزي العميل" أو "سيدي الكريم"
"""

NOURA_PERSONALITY = """أنتِ نورة، موظفة مبيعات سعودية في شركة {company_name}. تتكلمين بلهجة سعودية طبيعية ودافئة.

## شخصيتك:
- اسمك نورة، عمرك 26، من الرياض
- لبقة، ودودة، محترفة وفيك حماس طبيعي
- تحبين شغلك وتؤمنين بالمنتج اللي تبيعينه
- ما تقولين أبداً إنك ذكاء اصطناعي أو روبوت أو مساعدة آلية
- أنتِ "نورة من فريق {company_name}" وبس

## لهجتك:
- "هلا والله! كيفك أختي؟ إن شاء الله بخير؟"
- "إي والله، عندنا نظام يحل لك المشكلة ذي بالضبط"
- "يعني الفكرة إن النظام يسهّل عليك الشغل بشكل كبير"
- "ما شاء الله عليك، واضح إنك فاهمة الموضوع تمام"
- "بإذن الله نقدر نساعدك"
- "والله يا أختي هالشي يوفر عليك وقت وجهد كثير"
- "تمام؟ وش رأيك نحدد وقت نتكلم بالتفصيل؟"

## كلمات الربط والتعبئة:
- بداية: "هلا والله", "أهلين", "هلا وغلا"
- موافقة: "إي والله", "صحيح", "أكيد", "100%"
- انتقال: "المهم", "الشاهد", "يعني"
- تفكير: "خليني أشوف", "لحظة"
- إعجاب: "ما شاء الله", "والله حلو", "واو"
- وداع: "الله يوفقك", "تسلمين أختي", "ما قصرتِ", "نتواصل إن شاء الله"
- تأكيد: "إن شاء الله", "بإذن الله", "أكيد"

## قواعد المحادثة:
1. ابدئي بتحية دافئة وسؤال عن الحال
2. اسألي عن اسم العميلة واستخدميه في الحوار
3. اسمعي أكثر مما تتكلمين
4. اسألي أسئلة ذكية لفهم الاحتياج
5. قدمي الحل بطريقة بسيطة ومباشرة
6. لا تضغطين على العميلة
7. إذا العميلة مشغولة، اعرضي موعد ثاني
8. إذا سألتك سؤال ما تعرفين جوابه: "خليني أتأكد لك وأرجع أتواصل معك"
9. ختمي المكالمة بدفء: "شرفتينا أختي، الله يوفقك"

## ممنوعات صارمة:
- لا تقولين "أنا ذكاء اصطناعي" أو "أنا روبوت" أو "أنا مساعدة آلية"
- لا تعدين بأسعار نهائية
- لا تعطين تعهدات قانونية
- لا تتكلمين عن مميزات مو موجودة
- لا تستخدمين لغة رسمية أو فصحى
- لا تقولين "عزيزتي العميلة" أو "سيدتي الكريمة"
"""


# ---------------------------------------------------------------------------
# Voice Profiles Registry
# ---------------------------------------------------------------------------

class VoiceProfile(str, Enum):
    KHALID = "khalid"
    NOURA = "noura"


VOICE_PROFILES = {
    VoiceProfile.KHALID: {
        "id": "khalid",
        "name": "خالد",
        "name_en": "Khalid",
        "gender": "male",
        "dialect": "Najdi",
        "personality_prompt": KHALID_PERSONALITY,
        "elevenlabs_voice_id": "pMsXgVXv3BLzUgSXRplE",
        "first_message": "هلا والله! أنا خالد من فريق {company_name}. كيف حالك؟",
        "end_call_message": "شرفتنا والله، الله يوفقك. نتواصل إن شاء الله!",
        "description": "صوت شاب سعودي بلهجة نجدية، ودود وواثق",
    },
    VoiceProfile.NOURA: {
        "id": "noura",
        "name": "نورة",
        "name_en": "Noura",
        "gender": "female",
        "dialect": "Saudi",
        "personality_prompt": NOURA_PERSONALITY,
        "elevenlabs_voice_id": "pMsXgVXv3BLzUgSXRplE",  # Replace with female Arabic voice ID
        "first_message": "هلا والله! أنا نورة من فريق {company_name}. كيفك إن شاء الله بخير؟",
        "end_call_message": "شرفتينا والله، الله يوفقك. نتواصل إن شاء الله!",
        "description": "صوت سعودي نسائي دافئ ومحترف",
    },
}


# ---------------------------------------------------------------------------
# Call Flow Templates
# ---------------------------------------------------------------------------

CALL_FLOWS = {
    "cold_call": (
        "أهلين {name}، أنا {agent_name} من {company}. "
        "بدون ما أطوّل عليك، عندنا شي أتوقع يفيدك في شغلك. "
        "عندك دقيقتين أشرح لك بسرعة؟"
    ),
    "followup": (
        "هلا {name}! كيف حالك؟ أنا {agent_name} تكلمنا قبل كم يوم عن "
        "{topic}. حبيت أتابع معك وأشوف وش صار عندك."
    ),
    "appointment_reminder": (
        "أهلين {name}، أنا {agent_name} من {company}. "
        "حبيت أذكرك بموعدنا {appointment_time}. "
        "إن شاء الله لسا ماشي الموضوع معك؟"
    ),
    "after_hours": (
        "أهلين، شكراً لاتصالك بـ{company}. للأسف الفريق مو متواجد الحين، "
        "بس أنا {agent_name} أقدر أساعدك. وش أقدر أسوي لك؟"
    ),
    "missed_callback": (
        "هلا {name}، شفت إنك اتصلت علينا وما قدرنا نرد عليك. "
        "أنا {agent_name} من {company}، كيف أقدر أساعدك؟"
    ),
    "demo_invite": (
        "هلا {name}، أنا {agent_name} من {company}. "
        "حابب أدعوك لعرض سريع لنظامنا، ما يأخذ أكثر من ربع ساعة. "
        "وش رأيك نحدد وقت يناسبك؟"
    ),
    "reactivation": (
        "هلا {name}! كيف حالك؟ أنا {agent_name} من {company}. "
        "ما شفناك من زمان وحبينا نطمّن عليك ونشوف إذا تحتاج أي شي."
    ),
}

# Voice and transcription defaults
DEFAULT_ELEVENLABS_VOICE_ID = "pMsXgVXv3BLzUgSXRplE"
DEFAULT_DEEPGRAM_MODEL = "nova-2"
DEFAULT_DEEPGRAM_LANGUAGE = "ar"
DEFAULT_TEMPERATURE = 0.8
MAX_CALL_DURATION_SECONDS = 600  # 10 minutes


# ---------------------------------------------------------------------------
# Voice AI Service
# ---------------------------------------------------------------------------

class VoiceAIService:
    """Saudi-personality voice AI agent integration via Vapi."""

    def __init__(self, tenant_id: str, company_name: str = "SalesFlow"):
        self.tenant_id = tenant_id
        self.company_name = company_name
        self.provider = "vapi"
        self._base_url = "https://api.vapi.ai"

    # -- helpers -------------------------------------------------------------

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {settings.VAPI_API_KEY}",
            "Content-Type": "application/json",
        }

    def _resolve_profile(self, voice_profile: str | VoiceProfile) -> dict:
        """Return the full profile dict for a given profile key."""
        if isinstance(voice_profile, str):
            voice_profile = VoiceProfile(voice_profile)
        profile = VOICE_PROFILES[voice_profile]
        return profile

    def _render_prompt(self, template: str, **kwargs) -> str:
        """Fill placeholders in a prompt template."""
        kwargs.setdefault("company_name", self.company_name)
        return template.format(**kwargs)

    # -- public API ----------------------------------------------------------

    def get_voice_profiles(self) -> list[dict]:
        """Return all available voice profiles with metadata."""
        profiles = []
        for key, profile in VOICE_PROFILES.items():
            profiles.append({
                "id": profile["id"],
                "name": profile["name"],
                "name_en": profile["name_en"],
                "gender": profile["gender"],
                "dialect": profile["dialect"],
                "description": profile["description"],
            })
        return profiles

    def create_call_flow(
        self,
        flow_type: str,
        lead_data: dict,
        voice_profile: str | VoiceProfile = VoiceProfile.KHALID,
    ) -> str:
        """Generate a personalized call flow opening from a template.

        Args:
            flow_type: One of the keys in CALL_FLOWS (e.g. "cold_call").
            lead_data: Dict with keys like name, company, topic, appointment_time.
            voice_profile: Which persona to use for agent_name.

        Returns:
            Rendered opening string ready to use as first message.
        """
        template = CALL_FLOWS.get(flow_type)
        if template is None:
            raise ValueError(
                f"Unknown flow type '{flow_type}'. "
                f"Available: {', '.join(CALL_FLOWS.keys())}"
            )

        profile = self._resolve_profile(voice_profile)
        params = {
            "agent_name": profile["name"],
            "company": self.company_name,
            **lead_data,
        }
        # Fill only the placeholders that exist in the template; leave others
        # untouched so partial data does not crash.
        import re
        placeholders = re.findall(r"\{(\w+)\}", template)
        safe_params = {k: params.get(k, "") for k in placeholders}
        return template.format(**safe_params)

    async def create_assistant(
        self,
        name: str = "SalesFlow Voice Agent",
        industry: str = "general",
        voice_profile: str | VoiceProfile = VoiceProfile.KHALID,
    ) -> dict:
        """Create a voice AI assistant on Vapi with the chosen Saudi persona.

        Args:
            name: Display name for the assistant.
            industry: Industry context added to the system prompt.
            voice_profile: 'khalid' or 'noura'.
        """
        if not settings.VAPI_API_KEY:
            return {
                "error": "Voice AI not configured",
                "setup": "Set VAPI_API_KEY in .env",
            }

        profile = self._resolve_profile(voice_profile)
        system_prompt = self._render_prompt(
            profile["personality_prompt"],
        )
        # Append industry context if provided
        if industry and industry != "general":
            system_prompt += (
                f"\n\n## سياق القطاع:\n"
                f"- أنت متخصص في قطاع: {industry}\n"
                f"- استخدم مصطلحات هذا القطاع بشكل طبيعي\n"
                f"- اربط فوائد المنتج باحتياجات هذا القطاع\n"
            )

        first_message = self._render_prompt(profile["first_message"])
        end_message = self._render_prompt(profile["end_call_message"])

        payload = {
            "name": name,
            "model": {
                "provider": "openai",
                "model": "gpt-4o-mini",
                "systemPrompt": system_prompt,
                "temperature": DEFAULT_TEMPERATURE,
            },
            "voice": {
                "provider": "11labs",
                "voiceId": profile["elevenlabs_voice_id"],
            },
            "firstMessage": first_message,
            "endCallMessage": end_message,
            "transcriber": {
                "provider": "deepgram",
                "model": DEFAULT_DEEPGRAM_MODEL,
                "language": DEFAULT_DEEPGRAM_LANGUAGE,
            },
            "serverUrl": f"{settings.API_URL}/api/v1/voice/webhook",
            "endCallFunctionEnabled": True,
            "recordingEnabled": True,
            "maxDurationSeconds": MAX_CALL_DURATION_SECONDS,
            "metadata": {
                "tenant_id": self.tenant_id,
                "voice_profile": profile["id"],
                "industry": industry,
                "created_at": datetime.now(timezone.utc).isoformat(),
            },
        }

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{self._base_url}/assistant",
                headers=self._headers(),
                json=payload,
            )
            result = response.json()
            logger.info(
                "Created Vapi assistant '%s' with profile '%s' for tenant %s",
                name,
                profile["id"],
                self.tenant_id,
            )
            return result

    async def make_outbound_call(
        self,
        phone_number: str,
        assistant_id: Optional[str] = None,
        call_flow: Optional[str] = None,
        lead_data: Optional[dict] = None,
        voice_profile: str | VoiceProfile = VoiceProfile.KHALID,
    ) -> dict:
        """Initiate an outbound call via Vapi with optional call flow context.

        Args:
            phone_number: E.164 formatted phone number.
            assistant_id: Vapi assistant ID (falls back to env default).
            call_flow: Flow type from CALL_FLOWS (e.g. 'cold_call').
            lead_data: Context about the lead (name, company, topic, etc.).
            voice_profile: Which persona to use if generating a flow.
        """
        if not settings.VAPI_API_KEY:
            return {"error": "Voice AI not configured"}

        aid = assistant_id or settings.VAPI_ASSISTANT_ID
        if not aid:
            return {"error": "No assistant configured"}

        lead_data = lead_data or {}

        call_payload: dict = {
            "assistantId": aid,
            "phoneNumberId": settings.WHATSAPP_PHONE_NUMBER_ID,
            "customer": {
                "number": phone_number,
                "name": lead_data.get("name", ""),
            },
            "metadata": {
                "tenant_id": self.tenant_id,
                "call_flow": call_flow or "default",
                "lead_data": lead_data,
                "initiated_at": datetime.now(timezone.utc).isoformat(),
            },
        }

        # If a call flow is specified, override the first message
        if call_flow and call_flow in CALL_FLOWS:
            first_message = self.create_call_flow(
                flow_type=call_flow,
                lead_data=lead_data,
                voice_profile=voice_profile,
            )
            call_payload["assistantOverrides"] = {
                "firstMessage": first_message,
            }

            # Inject lead context into the system prompt so the agent knows
            # who it is talking to.
            if lead_data:
                context_lines = ["\n\n## معلومات العميل:"]
                if lead_data.get("name"):
                    context_lines.append(f"- الاسم: {lead_data['name']}")
                if lead_data.get("company"):
                    context_lines.append(f"- الشركة: {lead_data['company']}")
                if lead_data.get("industry"):
                    context_lines.append(f"- القطاع: {lead_data['industry']}")
                if lead_data.get("topic"):
                    context_lines.append(f"- الموضوع السابق: {lead_data['topic']}")
                if lead_data.get("notes"):
                    context_lines.append(f"- ملاحظات: {lead_data['notes']}")

                call_payload["assistantOverrides"]["model"] = {
                    "systemPromptAppend": "\n".join(context_lines),
                }

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{self._base_url}/call/phone",
                headers=self._headers(),
                json=call_payload,
            )
            result = response.json()
            logger.info(
                "Outbound call initiated to %s (flow=%s) for tenant %s",
                phone_number,
                call_flow or "default",
                self.tenant_id,
            )
            return result

    async def process_call_webhook(self, event: dict) -> dict:
        """Process incoming call webhook from Vapi with full DB persistence.

        Handles transcript chunks, end-of-call reports, function calls,
        status updates, and hang events.
        """
        message = event.get("message", {})
        event_type = message.get("type", "")
        call_id = message.get("call", {}).get("id", "unknown")
        timestamp = datetime.now(timezone.utc).isoformat()

        logger.info(
            "Voice webhook: type=%s call_id=%s tenant=%s",
            event_type,
            call_id,
            self.tenant_id,
        )

        # --- Live transcript fragment ---
        if event_type == "transcript":
            transcript = message.get("transcript", "")
            role = message.get("role", "")
            return {
                "action": "log_transcript",
                "call_id": call_id,
                "role": role,
                "text": transcript,
                "timestamp": timestamp,
                "persist": True,
            }

        # --- End of call report ---
        if event_type == "end-of-call-report":
            summary = message.get("summary", "")
            duration = message.get("duration", 0)
            transcript_text = message.get("transcript", "")
            recording_url = message.get("recordingUrl", "")
            ended_reason = message.get("endedReason", "")
            cost = message.get("cost", 0.0)
            metadata = message.get("call", {}).get("metadata", {})

            # AI-driven structured analysis
            analysis = await ai_brain.think_json(
                system_prompt=(
                    "حلل نص المكالمة التالي واستخرج بصيغة JSON:\n"
                    "- customer_name: اسم العميل\n"
                    "- company: اسم الشركة\n"
                    "- needs: قائمة احتياجات العميل\n"
                    "- budget_mentioned: هل ذكر ميزانية (true/false)\n"
                    "- budget_range: نطاق الميزانية إن ذُكر\n"
                    "- interest_level: مستوى الاهتمام 1-10\n"
                    "- objections: اعتراضات إن وجدت\n"
                    "- sentiment: إيجابي/محايد/سلبي\n"
                    "- next_action: الإجراء التالي المطلوب\n"
                    "- should_follow_up: true/false\n"
                    "- follow_up_urgency: low/medium/high\n"
                    "- summary: ملخص المكالمة بالعربي (3-5 جمل)\n"
                    "- key_quotes: أهم العبارات من العميل (قائمة)\n"
                    "رد بـ JSON فقط."
                ),
                user_message=transcript_text,
            )

            call_record = {
                "action": "call_completed",
                "call_id": call_id,
                "duration": duration,
                "ended_reason": ended_reason,
                "recording_url": recording_url,
                "cost": cost,
                "summary": summary,
                "analysis": analysis,
                "transcript": transcript_text,
                "metadata": metadata,
                "timestamp": timestamp,
                "persist": True,
            }

            logger.info(
                "Call completed: call_id=%s duration=%ds interest=%s",
                call_id,
                duration,
                analysis.get("interest_level", "?") if isinstance(analysis, dict) else "?",
            )

            return call_record

        # --- Function calls from the voice agent ---
        if event_type == "function-call":
            func_call = message.get("functionCall", {})
            function_name = func_call.get("name", "")
            params = func_call.get("parameters", {})

            if function_name == "book_demo":
                logger.info("Book demo requested via voice for call %s", call_id)
                return {
                    "action": "book_demo",
                    "call_id": call_id,
                    "customer_name": params.get("name", ""),
                    "phone": params.get("phone", ""),
                    "preferred_time": params.get("time", ""),
                    "notes": params.get("notes", ""),
                    "timestamp": timestamp,
                    "persist": True,
                }

            if function_name == "transfer_to_human":
                logger.info("Transfer requested for call %s: %s", call_id, params.get("reason"))
                return {
                    "action": "transfer",
                    "call_id": call_id,
                    "reason": params.get("reason", ""),
                    "department": params.get("department", "sales"),
                    "timestamp": timestamp,
                    "persist": True,
                }

            if function_name == "schedule_callback":
                return {
                    "action": "schedule_callback",
                    "call_id": call_id,
                    "customer_name": params.get("name", ""),
                    "phone": params.get("phone", ""),
                    "callback_time": params.get("time", ""),
                    "reason": params.get("reason", ""),
                    "timestamp": timestamp,
                    "persist": True,
                }

            if function_name == "send_info":
                return {
                    "action": "send_info",
                    "call_id": call_id,
                    "channel": params.get("channel", "whatsapp"),
                    "phone": params.get("phone", ""),
                    "info_type": params.get("type", "brochure"),
                    "timestamp": timestamp,
                    "persist": True,
                }

            # Unknown function
            logger.warning("Unknown function call '%s' in call %s", function_name, call_id)
            return {
                "action": "unknown_function",
                "call_id": call_id,
                "function_name": function_name,
                "params": params,
                "timestamp": timestamp,
            }

        # --- Status updates ---
        if event_type == "status-update":
            status = message.get("status", "")
            logger.info("Call %s status: %s", call_id, status)
            return {
                "action": "status_update",
                "call_id": call_id,
                "status": status,
                "timestamp": timestamp,
                "persist": True,
            }

        # --- Hang / speech events ---
        if event_type == "hang":
            return {
                "action": "call_hang",
                "call_id": call_id,
                "timestamp": timestamp,
                "persist": True,
            }

        # --- Catch-all ---
        logger.debug("Unhandled voice event type: %s", event_type)
        return {
            "action": "ignored",
            "call_id": call_id,
            "event_type": event_type,
            "timestamp": timestamp,
        }

    async def get_call_history(self, limit: int = 50) -> list:
        """Get recent call history from Vapi."""
        if not settings.VAPI_API_KEY:
            return []

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                f"{self._base_url}/call",
                headers=self._headers(),
                params={"limit": limit},
            )
            if response.status_code != 200:
                logger.warning(
                    "Failed to fetch call history: %s %s",
                    response.status_code,
                    response.text[:200],
                )
                return []
            return response.json()

    async def generate_call_summary(self, transcript: str) -> dict:
        """AI-generated call summary and action items."""
        return await ai_brain.think_json(
            system_prompt=(
                "أنت محلل مكالمات مبيعات محترف. حلل هذا النص واستخرج:\n"
                "- summary: ملخص المكالمة بالعربي (3-5 جمل)\n"
                "- customer_name: اسم العميل\n"
                "- company: اسم الشركة\n"
                "- needs: احتياجات العميل (قائمة)\n"
                "- interest_level: مستوى الاهتمام 1-10\n"
                "- objections: اعتراضات إن وجدت (قائمة)\n"
                "- sentiment: إيجابي/محايد/سلبي\n"
                "- key_quotes: أهم عبارات العميل (قائمة)\n"
                "- next_action: الإجراء التالي\n"
                "- should_follow_up: true/false\n"
                "- follow_up_urgency: low/medium/high\n"
                "- follow_up_date_suggestion: اقتراح تاريخ المتابعة\n"
                "- deal_probability: احتمالية إغلاق الصفقة (نسبة مئوية)\n"
                "رد بـ JSON فقط."
            ),
            user_message=transcript,
        )
