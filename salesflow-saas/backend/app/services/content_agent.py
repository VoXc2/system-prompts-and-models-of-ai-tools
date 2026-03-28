"""
Dealix Content Agent — Generates viral social media content.
Creates industry-specific content in Saudi dialect.
"""
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional

from app.config import get_settings
from app.services.ai_brain import ai_brain

logger = logging.getLogger(__name__)

settings = get_settings()

# ---------------------------------------------------------------------------
# Saudi Arabic content templates organized by content_type and industry
# ---------------------------------------------------------------------------
CONTENT_TEMPLATES: dict[str, dict[str, str]] = {
    "tip": {
        "real_estate": "💡 نصيحة عقارية: {topic}\n\n{body}\n\n#عقارات_الرياض #عقارات_السعودية #رؤية_2030",
        "clinics": "💡 نصيحة صحية: {topic}\n\n{body}\n\n#صحة #عيادات #عيادات_الرياض",
        "contracting": "💡 نصيحة للمقاولين: {topic}\n\n{body}\n\n#مقاولات #بناء #مقاولات_السعودية",
        "general": "💡 نصيحة: {topic}\n\n{body}\n\n#أعمال #السعودية #رؤية_2030",
    },
    "case_study": {
        "real_estate": "📊 قصة نجاح عقارية\n\n{body}\n\n#عقارات #نجاح #استثمار_عقاري",
        "clinics": "📊 قصة نجاح طبية\n\n{body}\n\n#عيادات #نجاح #رعاية_صحية",
        "contracting": "📊 مشروع ناجح\n\n{body}\n\n#مقاولات #مشاريع #بنية_تحتية",
        "general": "📊 قصة نجاح\n\n{body}\n\n#نجاح #أعمال #السعودية",
    },
    "stat": {
        "real_estate": "📈 رقم مهم: {topic}\n\n{body}\n\n#عقارات #إحصائيات #السوق_السعودي",
        "clinics": "📈 إحصائية صحية: {topic}\n\n{body}\n\n#صحة #إحصائيات #رعاية_صحية",
        "contracting": "📈 رقم في قطاع البناء: {topic}\n\n{body}\n\n#مقاولات #إحصائيات #بناء",
        "general": "📈 رقم مهم: {topic}\n\n{body}\n\n#إحصائيات #أعمال #السعودية",
    },
    "question": {
        "real_estate": "🤔 سؤال للعقاريين:\n\n{body}\n\nشاركونا رأيكم! 👇\n\n#عقارات #نقاش",
        "clinics": "🤔 سؤال لأصحاب العيادات:\n\n{body}\n\nشاركونا رأيكم! 👇\n\n#عيادات #نقاش",
        "contracting": "🤔 سؤال للمقاولين:\n\n{body}\n\nشاركونا رأيكم! 👇\n\n#مقاولات #نقاش",
        "general": "🤔 سؤال لرواد الأعمال:\n\n{body}\n\nشاركونا رأيكم! 👇\n\n#أعمال #نقاش",
    },
    "testimonial": {
        "real_estate": "⭐ عميلنا يقول:\n\n\"{body}\"\n\n#عقارات #رضا_العملاء",
        "clinics": "⭐ مريضنا يقول:\n\n\"{body}\"\n\n#عيادات #رضا_العملاء",
        "contracting": "⭐ عميلنا يقول:\n\n\"{body}\"\n\n#مقاولات #رضا_العملاء",
        "general": "⭐ عميلنا يقول:\n\n\"{body}\"\n\n#رضا_العملاء #تقييم",
    },
    "behind_scenes": {
        "real_estate": "🎬 وراء الكواليس\n\n{body}\n\n#عقارات #يومياتنا",
        "clinics": "🎬 وراء كواليس العيادة\n\n{body}\n\n#عيادات #يومياتنا",
        "contracting": "🎬 من موقع العمل\n\n{body}\n\n#مقاولات #موقع_العمل",
        "general": "🎬 وراء الكواليس\n\n{body}\n\n#يومياتنا #فريق_العمل",
    },
    "offer": {
        "real_estate": "🔥 عرض عقاري حصري!\n\n{body}\n\nتواصل معنا الحين! 📲\n\n#عقارات #عروض",
        "clinics": "🔥 عرض حصري من العيادة!\n\n{body}\n\nاحجز الحين! 📲\n\n#عيادات #عروض",
        "contracting": "🔥 عرض خاص للمشاريع!\n\n{body}\n\nتواصل معنا! 📲\n\n#مقاولات #عروض",
        "general": "🔥 عرض حصري!\n\n{body}\n\nلا تفوّت الفرصة! 📲\n\n#عروض #خصومات",
    },
}

# Best posting times for Saudi audience (Riyadh timezone)
BEST_POST_TIMES: dict[str, list[str]] = {
    "instagram": ["09:00", "13:00", "18:00", "21:00"],
    "twitter": ["08:00", "12:00", "17:00", "22:00"],
    "linkedin": ["08:00", "10:00", "14:00", "17:00"],
}


class ContentAgent:
    """Generates AI-powered social media content in Saudi dialect."""

    def __init__(self, tenant_id: str, industry: str = "general"):
        self.tenant_id = tenant_id
        self.industry = industry

    async def generate_post(
        self,
        platform: str,
        industry: Optional[str] = None,
        content_type: str = "tip",
        topic: str = "",
    ) -> dict:
        """
        Generate a complete social media post.

        Args:
            platform: instagram | twitter | linkedin
            industry: real_estate | clinics | contracting | general
            content_type: tip | case_study | stat | question | testimonial | behind_scenes | offer
            topic: The subject to write about

        Returns:
            {text, hashtags, suggested_image_prompt, best_time_to_post}
        """
        industry = industry or self.industry

        # Get template if available
        template = CONTENT_TEMPLATES.get(content_type, {}).get(
            industry, CONTENT_TEMPLATES.get(content_type, {}).get("general", "")
        )

        platform_instructions = {
            "instagram": (
                "اكتب بوست انستقرام (caption) بأسلوب سعودي جذاب. "
                "استخدم إيموجي بشكل مناسب. الطول المثالي 150-300 كلمة. "
                "أضف CTA في النهاية."
            ),
            "twitter": (
                "اكتب تغريدة بأسلوب سعودي مختصر (أقل من 280 حرف). "
                "خلها ملفتة وتشجع على التفاعل. "
                "أضف 3-5 هاشتاقات مناسبة."
            ),
            "linkedin": (
                "اكتب بوست لينكدإن بأسلوب سعودي مهني. "
                "الطول المثالي 100-200 كلمة. "
                "ركّز على القيمة والخبرة. أضف سؤال للتفاعل."
            ),
        }

        prompt = (
            f"{platform_instructions.get(platform, platform_instructions['instagram'])}\n\n"
            f"نوع المحتوى: {content_type}\n"
            f"الموضوع: {topic}\n"
            f"القطاع: {industry}\n"
            f"القالب المرجعي: {template}\n\n"
            f"اكتب المحتوى فقط بدون مقدمات أو شرح."
        )

        response = await ai_brain(prompt)
        text = response.get("reply", "")

        # Enforce Twitter limit
        if platform == "twitter" and len(text) > 280:
            text = text[:277] + "..."

        hashtags = await self.generate_hashtags(industry, platform)

        # Generate an image prompt for design teams / AI image tools
        image_prompt = (
            f"Professional {content_type} visual for {industry} business in Saudi Arabia. "
            f"Topic: {topic}. Modern, clean design with Arabic text overlay. "
            f"Colors: brand-aligned, professional. Saudi Vision 2030 aesthetic."
        )

        times = BEST_POST_TIMES.get(platform, BEST_POST_TIMES["instagram"])
        best_time = times[hash(topic) % len(times)]

        return {
            "text": text,
            "hashtags": hashtags,
            "suggested_image_prompt": image_prompt,
            "best_time_to_post": best_time,
            "platform": platform,
            "content_type": content_type,
            "industry": industry,
        }

    async def generate_comment(
        self,
        target_post_content: str,
        industry: Optional[str] = None,
        intent: str = "value_add",
    ) -> str:
        """
        Generate a contextual, value-adding comment (not spam).

        Args:
            target_post_content: The text of the post to comment on
            industry: Target industry
            intent: supportive | expert_insight | question | value_add
        """
        industry = industry or self.industry

        intent_prompts = {
            "supportive": "اكتب تعليق داعم ومشجع — أظهر إعجابك الحقيقي بالمحتوى.",
            "expert_insight": "اكتب تعليق يضيف رأي خبير أو معلومة إضافية قيّمة.",
            "question": "اكتب سؤال ذكي يبين اهتمامك ويفتح نقاش مفيد.",
            "value_add": "اكتب تعليق يضيف قيمة حقيقية — نصيحة أو إحصائية أو تجربة.",
        }

        prompt = (
            f"اكتب تعليق على بوست سوشال ميديا بأسلوب سعودي.\n\n"
            f"محتوى البوست:\n\"{target_post_content[:500]}\"\n\n"
            f"الهدف: {intent_prompts.get(intent, intent_prompts['value_add'])}\n"
            f"القطاع: {industry}\n\n"
            f"القواعد:\n"
            f"- لا تبيع شي بشكل مباشر\n"
            f"- أضف قيمة حقيقية\n"
            f"- خله قصير (جملة أو جملتين)\n"
            f"- استخدم لهجة سعودية طبيعية\n"
            f"- لا تستخدم إيموجي كثير\n\n"
            f"اكتب التعليق فقط:"
        )

        response = await ai_brain(prompt)
        return response.get("reply", "")

    async def generate_dm_sequence(
        self,
        prospect_data: dict,
        platform: str = "instagram",
        num_messages: int = 4,
    ) -> list[dict]:
        """
        Generate a multi-step DM sequence: intro -> value -> ask -> followup.

        Returns:
            List of {step, message, delay_hours, message_type}
        """
        steps = ["intro", "value", "ask", "followup"]
        if num_messages > len(steps):
            steps += [f"followup_{i}" for i in range(2, num_messages - len(steps) + 2)]
        steps = steps[:num_messages]

        step_prompts = {
            "intro": "رسالة تعارف — عرّف نفسك باختصار وأبدِ اهتمامك بشغلهم. لا تبيع شي.",
            "value": "رسالة قيمة — شارك نصيحة أو معلومة مفيدة لمجالهم بدون مقابل.",
            "ask": "رسالة طلب — اسألهم عن تحدياتهم واعرض المساعدة بشكل خفيف.",
            "followup": "رسالة متابعة — تابع معهم بلطف واقترح مكالمة قصيرة أو لقاء.",
        }

        delay_hours_map = {
            "intro": 0,
            "value": 48,
            "ask": 72,
            "followup": 120,
        }

        platform_style = {
            "instagram": "أسلوب انستقرام — ودي، غير رسمي، إيموجي خفيف",
            "twitter": "أسلوب تويتر — مختصر وذكي",
            "linkedin": "أسلوب لينكدإن — مهني لكن ودي",
        }

        sequence: list[dict] = []
        for idx, step in enumerate(steps):
            base_step = step.split("_")[0] if "_" in step else step
            step_instruction = step_prompts.get(base_step, step_prompts["followup"])
            delay = delay_hours_map.get(base_step, 120 + (idx * 48))

            prompt = (
                f"اكتب رسالة خاصة (DM) بأسلوب سعودي.\n\n"
                f"المنصة: {platform_style.get(platform, platform_style['instagram'])}\n"
                f"الخطوة: {step_instruction}\n"
                f"القطاع: {self.industry}\n"
                f"معلومات العميل المحتمل:\n"
                f"- الاسم: {prospect_data.get('name', 'غير معروف')}\n"
                f"- الشركة: {prospect_data.get('company', '')}\n"
                f"- المنصب: {prospect_data.get('title', '')}\n"
                f"- ملاحظات: {prospect_data.get('notes', '')}\n\n"
                f"اكتب الرسالة فقط بدون مقدمات:"
            )

            response = await ai_brain(prompt)
            message_text = response.get("reply", "")

            # Enforce Twitter DM softness
            if platform == "twitter" and len(message_text) > 1000:
                message_text = message_text[:997] + "..."

            sequence.append({
                "step": idx + 1,
                "message_type": step,
                "message": message_text,
                "delay_hours": delay,
            })

        logger.info(
            "Generated %d-step DM sequence for %s on %s — tenant=%s",
            len(sequence), prospect_data.get("name", "?"), platform, self.tenant_id,
        )
        return sequence

    async def generate_content_calendar(
        self,
        industry: Optional[str] = None,
        platforms: Optional[list[str]] = None,
        days: int = 7,
    ) -> list[dict]:
        """
        Generate a daily content calendar.

        Returns:
            List of {day, date, platform, content_type, topic, time, notes}
        """
        industry = industry or self.industry
        platforms = platforms or ["instagram", "twitter", "linkedin"]

        content_types = ["tip", "case_study", "stat", "question", "testimonial", "behind_scenes", "offer"]

        prompt = (
            f"أنت خبير محتوى سوشال ميديا للسوق السعودي.\n\n"
            f"اكتب خطة محتوى لمدة {days} أيام لقطاع {industry}.\n"
            f"المنصات: {', '.join(platforms)}\n"
            f"أنواع المحتوى المتاحة: {', '.join(content_types)}\n\n"
            f"لكل يوم أعطني:\n"
            f"1. المنصة\n2. نوع المحتوى\n3. الموضوع (عنوان قصير)\n4. ملاحظات\n\n"
            f"نوّع بين أنواع المحتوى والمنصات.\n"
            f"ركّز على: رؤية 2030، التحول الرقمي، قصص نجاح سعودية.\n\n"
            f"اكتب الخطة بصيغة JSON array."
        )

        response = await ai_brain(prompt)
        ai_text = response.get("reply", "")

        # Try to parse AI response as JSON, fall back to generating a balanced plan
        calendar: list[dict] = []
        try:
            import json
            # Attempt to extract JSON from AI response
            start = ai_text.find("[")
            end = ai_text.rfind("]") + 1
            if start != -1 and end > start:
                parsed = json.loads(ai_text[start:end])
                for item in parsed:
                    calendar.append(item)
        except (json.JSONDecodeError, ValueError):
            pass

        # Fallback: build a balanced calendar programmatically
        if not calendar:
            from datetime import date as date_type

            today = datetime.now(timezone.utc).date()
            for day_offset in range(days):
                current_date = today + timedelta(days=day_offset)
                platform = platforms[day_offset % len(platforms)]
                ct = content_types[day_offset % len(content_types)]
                times = BEST_POST_TIMES.get(platform, BEST_POST_TIMES["instagram"])
                post_time = times[day_offset % len(times)]

                calendar.append({
                    "day": day_offset + 1,
                    "date": current_date.isoformat(),
                    "platform": platform,
                    "content_type": ct,
                    "topic": f"{industry} — {ct}",
                    "time": post_time,
                    "notes": f"Auto-generated for {industry}",
                })

        logger.info(
            "Generated %d-day content calendar for %s — tenant=%s",
            len(calendar), industry, self.tenant_id,
        )
        return calendar

    async def generate_hashtags(
        self,
        industry: Optional[str] = None,
        platform: str = "instagram",
        location: Optional[str] = None,
    ) -> list[str]:
        """
        Generate industry-specific hashtags optimized per platform.

        Platform limits:
        - Instagram: up to 30 hashtags
        - Twitter: 3-5 hashtags
        - LinkedIn: 3-5 hashtags
        """
        industry = industry or self.industry
        location = location or "السعودية"

        # Base hashtags per industry
        industry_hashtags: dict[str, list[str]] = {
            "real_estate": [
                "#عقارات", "#عقارات_الرياض", "#عقارات_السعودية",
                "#استثمار_عقاري", "#شقق", "#فلل", "#أراضي",
                "#عقار", "#سوق_العقار", "#التطوير_العقاري",
                "#رؤية_2030", "#نيوم", "#مشاريع_السعودية",
            ],
            "clinics": [
                "#عيادات", "#عيادات_الرياض", "#صحة",
                "#رعاية_صحية", "#طب", "#أسنان", "#جلدية",
                "#تجميل", "#صحتك", "#عيادة",
                "#رؤية_2030", "#التحول_الصحي",
            ],
            "contracting": [
                "#مقاولات", "#مقاولات_السعودية", "#بناء",
                "#تشييد", "#مشاريع", "#بنية_تحتية",
                "#هندسة", "#معمار", "#تصميم_معماري",
                "#رؤية_2030", "#مشاريع_نيوم",
            ],
            "general": [
                "#أعمال", "#ريادة_أعمال", "#السعودية",
                "#رؤية_2030", "#تحول_رقمي", "#تقنية",
                "#نجاح", "#تطوير", "#ابتكار",
            ],
        }

        hashtags = industry_hashtags.get(industry, industry_hashtags["general"])[:]

        # Add location-specific tags
        if location and location != "السعودية":
            hashtags.append(f"#{location.replace(' ', '_')}")

        # Platform-specific trimming
        max_tags = {"instagram": 30, "twitter": 5, "linkedin": 5}
        limit = max_tags.get(platform, 10)

        return hashtags[:limit]
