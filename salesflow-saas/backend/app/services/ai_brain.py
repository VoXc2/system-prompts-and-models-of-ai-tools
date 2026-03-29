"""
Dealix AI Brain - The core intelligence engine.
Uses LLM APIs (OpenAI/Claude) to power all AI sales agents.
"""
import asyncio
import json
import logging
import time
import httpx
from typing import Optional
from app.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()


async def _log_ai_trace(
    provider: str,
    model: str,
    system_prompt: str,
    user_message: str,
    response: str,
    temperature: float,
    max_tokens: int,
    latency_ms: float,
    input_tokens: int = 0,
    output_tokens: int = 0,
    error_message: str = "",
    status: str = "success",
):
    """Log an AI call to the AITrace table for governance."""
    try:
        from app.database import async_session
        from app.models.ai_trace import AITrace

        total_tokens = input_tokens + output_tokens
        # Rough cost estimate (varies by provider/model)
        cost_usd = total_tokens * 0.000003 if total_tokens else 0.0

        async with async_session() as db:
            trace = AITrace(
                agent_type="ai_brain",
                action="think",
                status=status,
                provider=provider,
                model=model,
                temperature=temperature,
                system_prompt=system_prompt[:2000],
                user_message=user_message[:2000],
                response=response[:2000] if response else "",
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=total_tokens,
                cost_usd=cost_usd,
                latency_ms=int(latency_ms),
                error_message=error_message[:500] if error_message else "",
            )
            db.add(trace)
            await db.commit()
    except Exception as e:
        logger.warning("Failed to log AI trace: %s", e)

# ─── Retry Configuration ─────────────────────────────────────────────────────

MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = [2, 4, 8]  # exponential backoff: 2s, 4s, 8s

# ─── System Prompts ──────────────────────────────────────────────────────────

SALES_AGENT_PROMPT_AR = """أنت تتكلم بصفة صاحب الشركة نفسه، مو كمساعد ذكي أو بوت.

## شخصيتك:
- أنت صاحب الشركة شخصياً، تتكلم من قلبك مع العميل
- تستخدم اللهجة السعودية الدارجة مو الفصحى
- ودود وطبيعي، مثل واحد يكلم صاحبه عن شغله
- تعرف السوق السعودي ورؤية 2030 بالتفصيل
- خبير في القطاع اللي تبيع فيه (عيادات/عقارات/مقاولات)

## أسلوبك في الكلام:
- ابدأ بالاسم الأول مباشرة، لا تقول عزيزي أو سيدي
- رسائلك قصيرة مثل محادثة واتساب حقيقية
- لا تبدأ بتحية رسمية طويلة
- استخدم كلمات مثل: وش رأيك، إن شاء الله، ما قصرت، تمام، أكيد
- تكلم بصيغة المتكلم: "أنا سويت"، "عندي"، "أقولك"
- لا تستخدم: عزيزي، سيدي، يسرنا، نود إبلاغكم

## طريقة البيع:
1. **الترحيب**: هلا باسمه الأول وعرّف نفسك ببساطة
2. **الاستكشاف**: اسأل أسئلة طبيعية لفهم وش يحتاج
3. **التأهيل**: حدد إذا العميل جاد ويقدر يشتري
4. **العرض**: قدّم الحل بطريقة بسيطة وواضحة
5. **معالجة الاعتراضات**: رد بثقة مثل صاحب خبرة
6. **الإغلاق**: اطلب البيع بشكل طبيعي بدون ضغط

## قواعد مهمة:
- لا تكذب أبداً، كن صادق بخصوص المنتج/الخدمة
- إذا ما تعرف الجواب، قل "خلني أتأكد لك وأرد عليك"
- استخدم أرقام وأمثلة حقيقية لتقوية كلامك
- اربط كل شي برؤية 2030 والتحول الرقمي لما يناسب
- إذا العميل مهتم جداً، حوّله لفريق المبيعات البشري
- لا تطوّل في الرسائل أبداً — واتساب مو إيميل

## معلومات الشركة:
{company_info}

## معلومات القطاع:
{industry_info}

## سجل المحادثة السابقة:
{conversation_history}
"""

LEAD_QUALIFIER_PROMPT = """You are a lead qualification AI agent for Dealix CRM.

Analyze the following lead information and conversation to determine:
1. **Score (0-100)**: How likely this lead is to convert
2. **Status**: new, contacted, qualified, proposal, hot
3. **Budget**: Estimated budget if mentioned
4. **Timeline**: When they want to buy/start
5. **Pain Points**: What problems they have
6. **Next Action**: What should be done next
7. **Priority**: low, medium, high, urgent

Lead Data:
{lead_data}

Conversation History:
{conversation}

Respond in JSON format only.
"""

LEAD_DISCOVERY_PROMPT = """You are a lead discovery AI agent for the Saudi market.

Given the following industry and target criteria, generate a search strategy:
1. What keywords to search for (Arabic + English)
2. What platforms to search (Google Maps, Instagram, Twitter/X, LinkedIn)
3. What business directories to check
4. What qualifying criteria to use
5. Suggested outreach message (Arabic)

Industry: {industry}
Target Location: {location}
Target Criteria: {criteria}

Respond in JSON format.
"""

OBJECTION_HANDLER_PROMPT_AR = """أنت خبير في معالجة اعتراضات المبيعات في السوق السعودي.

الاعتراض: {objection}
القطاع: {industry}
المنتج/الخدمة: {product}

اعطني:
1. نوع الاعتراض (سعر، وقت، ثقة، حاجة، منافس)
2. رد قوي ومقنع بالعامية السعودية
3. سؤال متابعة ذكي يفتح الحوار

رد بصيغة JSON.
"""

PERSONALIZED_MESSAGE_PROMPT_AR = """أنت صاحب الشركة نفسه تكتب رسالة واتساب لعميل محتمل.

أنت {owner_name} من {company}.

اكتب رسالة واتساب شخصية لهذا الشخص:

معلومات العميل:
- الاسم: {name}
- الشركة/النشاط: {business}
- القطاع: {industry}
- المدينة: {city}
- المصدر: {source}

نوع الرسالة: {message_type}

القواعد:
- تكلم بصيغة المتكلم: "أنا {owner_name} من {company}"
- جمل قصيرة مثل لو تسوي فويس نوت وتحوله نص
- استخدم لهجة سعودية دارجة بشكل طبيعي
- اذكر شي محدد عن نشاط العميل يبيّن إنك فعلاً شفت شغله
- ناده باسمه الأول مباشرة بدون ألقاب
- قصيرة (أقل من 100 كلمة)
- إيموجي 1-2 بس
- فيها CTA واضحة ومباشرة (وش رأيك نتكلم؟ تبي أرسلك؟)

اكتب الرسالة فقط بدون مقدمات.
"""


class AIBrain:
    """Core AI engine that powers all Dealix agents."""

    def __init__(self):
        self.openai_key = settings.OPENAI_API_KEY
        self.openai_model = settings.OPENAI_MODEL
        self.anthropic_key = settings.ANTHROPIC_API_KEY
        self.gemini_key = settings.GEMINI_API_KEY
        self.gemini_model = settings.GEMINI_MODEL
        self.ai_provider = settings.AI_PROVIDER  # "openai", "anthropic", or "gemini"

    async def think(self, system_prompt: str, user_message: str, temperature: float = 0.7, max_tokens: int = 1000) -> str:
        """Send a prompt to the AI and get a response. Logs every call to AITrace."""
        start_ms = time.time() * 1000

        # Determine provider and model
        if self.ai_provider == "gemini" and self.gemini_key:
            provider, model = "gemini", self.gemini_model
            call_fn = self._call_gemini
        elif self.ai_provider == "anthropic" and self.anthropic_key:
            provider, model = "anthropic", "claude-sonnet-4-20250514"
            call_fn = self._call_anthropic
        else:
            provider, model = "openai", self.openai_model
            call_fn = self._call_openai

        try:
            response = await call_fn(system_prompt, user_message, temperature, max_tokens)
            latency = time.time() * 1000 - start_ms
            # Fire-and-forget trace logging
            asyncio.create_task(_log_ai_trace(
                provider=provider, model=model,
                system_prompt=system_prompt, user_message=user_message,
                response=response, temperature=temperature, max_tokens=max_tokens,
                latency_ms=latency, status="success",
            ))
            return response
        except Exception as exc:
            latency = time.time() * 1000 - start_ms
            asyncio.create_task(_log_ai_trace(
                provider=provider, model=model,
                system_prompt=system_prompt, user_message=user_message,
                response="", temperature=temperature, max_tokens=max_tokens,
                latency_ms=latency, status="error", error_message=str(exc),
            ))
            raise

    async def think_json(self, system_prompt: str, user_message: str, temperature: float = 0.3) -> dict:
        """Get a JSON response from the AI."""
        response = await self.think(system_prompt, user_message, temperature)
        try:
            # Try to extract JSON from response
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                response = response.split("```")[1].split("```")[0]
            return json.loads(response.strip())
        except (json.JSONDecodeError, IndexError):
            return {"raw_response": response, "parse_error": True}

    async def _call_openai(self, system_prompt: str, user_message: str, temperature: float, max_tokens: int) -> str:
        """Call OpenAI API with retry logic (3 retries, exponential backoff)."""
        last_error: Optional[Exception] = None

        for attempt in range(MAX_RETRIES):
            try:
                async with httpx.AsyncClient(timeout=60) as client:
                    response = await client.post(
                        "https://api.openai.com/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {self.openai_key}",
                            "Content-Type": "application/json",
                        },
                        json={
                            "model": self.openai_model,
                            "messages": [
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": user_message},
                            ],
                            "temperature": temperature,
                            "max_tokens": max_tokens,
                        },
                    )
                    response.raise_for_status()
                    data = response.json()
                    return data["choices"][0]["message"]["content"]

            except (httpx.HTTPStatusError, httpx.RequestError, KeyError) as exc:
                last_error = exc
                backoff = RETRY_BACKOFF_SECONDS[attempt]
                logger.warning(
                    "OpenAI API call failed (attempt %d/%d): %s. "
                    "Retrying in %ds...",
                    attempt + 1,
                    MAX_RETRIES,
                    str(exc),
                    backoff,
                )
                if attempt < MAX_RETRIES - 1:
                    await asyncio.sleep(backoff)

        logger.error(
            "OpenAI API call failed after %d retries. Last error: %s",
            MAX_RETRIES,
            str(last_error),
        )
        raise last_error  # type: ignore[misc]

    async def _call_anthropic(self, system_prompt: str, user_message: str, temperature: float, max_tokens: int) -> str:
        """Call Anthropic Claude API with retry logic (3 retries, exponential backoff)."""
        last_error: Optional[Exception] = None

        for attempt in range(MAX_RETRIES):
            try:
                async with httpx.AsyncClient(timeout=60) as client:
                    response = await client.post(
                        "https://api.anthropic.com/v1/messages",
                        headers={
                            "x-api-key": self.anthropic_key,
                            "anthropic-version": "2023-06-01",
                            "Content-Type": "application/json",
                        },
                        json={
                            "model": "claude-sonnet-4-20250514",
                            "max_tokens": max_tokens,
                            "system": system_prompt,
                            "messages": [
                                {"role": "user", "content": user_message},
                            ],
                            "temperature": temperature,
                        },
                    )
                    response.raise_for_status()
                    data = response.json()
                    return data["content"][0]["text"]

            except (httpx.HTTPStatusError, httpx.RequestError, KeyError) as exc:
                last_error = exc
                backoff = RETRY_BACKOFF_SECONDS[attempt]
                logger.warning(
                    "Anthropic API call failed (attempt %d/%d): %s. "
                    "Retrying in %ds...",
                    attempt + 1,
                    MAX_RETRIES,
                    str(exc),
                    backoff,
                )
                if attempt < MAX_RETRIES - 1:
                    await asyncio.sleep(backoff)

        logger.error(
            "Anthropic API call failed after %d retries. Last error: %s",
            MAX_RETRIES,
            str(last_error),
        )
        raise last_error  # type: ignore[misc]

    async def _call_gemini(self, system_prompt: str, user_message: str, temperature: float, max_tokens: int) -> str:
        """Call Google Gemini API with retry logic (3 retries, exponential backoff)."""
        last_error: Optional[Exception] = None
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.gemini_model}:generateContent"

        for attempt in range(MAX_RETRIES):
            try:
                async with httpx.AsyncClient(timeout=60) as client:
                    response = await client.post(
                        url,
                        params={"key": self.gemini_key},
                        headers={"Content-Type": "application/json"},
                        json={
                            "contents": [
                                {
                                    "parts": [
                                        {"text": system_prompt + "\n\n" + user_message}
                                    ]
                                }
                            ],
                            "generationConfig": {
                                "temperature": temperature,
                                "maxOutputTokens": max_tokens,
                            },
                        },
                    )
                    response.raise_for_status()
                    data = response.json()
                    return data["candidates"][0]["content"]["parts"][0]["text"]

            except (httpx.HTTPStatusError, httpx.RequestError, KeyError) as exc:
                last_error = exc
                backoff = RETRY_BACKOFF_SECONDS[attempt]
                logger.warning(
                    "Gemini API call failed (attempt %d/%d): %s. "
                    "Retrying in %ds...",
                    attempt + 1,
                    MAX_RETRIES,
                    str(exc),
                    backoff,
                )
                if attempt < MAX_RETRIES - 1:
                    await asyncio.sleep(backoff)

        logger.error(
            "Gemini API call failed after %d retries. Last error: %s",
            MAX_RETRIES,
            str(last_error),
        )
        raise last_error  # type: ignore[misc]

    # ─── High-Level Agent Functions ───

    async def generate_sales_response(
        self, message: str, company_info: str, industry_info: str,
        conversation_history: str = ""
    ) -> str:
        """Generate an intelligent sales response in Arabic."""
        system = SALES_AGENT_PROMPT_AR.format(
            company_info=company_info,
            industry_info=industry_info,
            conversation_history=conversation_history,
        )
        return await self.think(system, message, temperature=0.7, max_tokens=500)

    async def qualify_lead(self, lead_data: dict, conversation: str = "") -> dict:
        """AI-powered lead qualification and scoring."""
        system = LEAD_QUALIFIER_PROMPT.format(
            lead_data=json.dumps(lead_data, ensure_ascii=False),
            conversation=conversation,
        )
        return await self.think_json(system, "Analyze and qualify this lead. Respond in JSON.")

    async def generate_discovery_strategy(self, industry: str, location: str, criteria: str = "") -> dict:
        """Generate a lead discovery strategy for an industry."""
        system = LEAD_DISCOVERY_PROMPT.format(
            industry=industry, location=location, criteria=criteria,
        )
        return await self.think_json(system, "Generate the search strategy. Respond in JSON.")

    async def handle_objection(self, objection: str, industry: str, product: str) -> dict:
        """AI-powered objection handling."""
        system = OBJECTION_HANDLER_PROMPT_AR.format(
            objection=objection, industry=industry, product=product,
        )
        return await self.think_json(system, "Handle this objection. Respond in JSON.")

    async def write_personalized_message(
        self, name: str, business: str, industry: str,
        city: str = "الرياض", source: str = "واتساب",
        message_type: str = "أول تواصل",
        owner_name: str = "", company: str = "",
    ) -> str:
        """Write a personalized outreach message as the business owner."""
        system = PERSONALIZED_MESSAGE_PROMPT_AR.format(
            name=name, business=business, industry=industry,
            city=city, source=source, message_type=message_type,
            owner_name=owner_name or "صاحب الشركة",
            company=company or "الشركة",
        )
        return await self.think(system, "اكتب الرسالة", temperature=0.8, max_tokens=300)

    async def analyze_sentiment(self, message: str) -> dict:
        """Analyze customer message sentiment and intent."""
        system = """Analyze this Arabic customer message. Return JSON with:
- sentiment: positive, negative, neutral
- intent: inquiry, complaint, interested, objection, ready_to_buy, not_interested
- urgency: low, medium, high
- suggested_action: what to do next
- key_topics: list of topics mentioned"""
        return await self.think_json(system, message)

    async def summarize_conversation(self, messages: list) -> dict:
        """Summarize a sales conversation."""
        conversation = "\n".join([f"{'العميل' if m.get('direction') == 'inbound' else 'ديليكس'}: {m.get('content', '')}" for m in messages])
        system = """Summarize this sales conversation in Arabic. Return JSON with:
- summary: brief summary
- customer_needs: list of identified needs
- objections: list of objections raised
- commitment_level: low, medium, high
- next_steps: recommended next steps
- deal_probability: 0-100"""
        return await self.think_json(system, conversation)


# Singleton
ai_brain = AIBrain()
