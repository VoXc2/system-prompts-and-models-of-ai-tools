"""
Content Creator Agent — generates bilingual articles, LinkedIn posts, case studies.
وكيل إنشاء المحتوى — يُنشئ مقالات و منشورات و دراسات حالة ثنائية اللغة.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Literal

from core.agents.base import BaseAgent
from core.config.models import Task
from core.llm.base import Message
from core.prompts import get_prompt
from core.utils import generate_id, utcnow

ContentType = Literal["article", "linkedin_post", "case_study", "newsletter", "tweet_thread"]
Channel = Literal["blog", "linkedin", "twitter", "email", "whatsapp_broadcast"]


@dataclass
class ContentPiece:
    id: str
    content_type: ContentType
    channel: Channel
    locale: str
    topic: str
    title: str
    body_markdown: str
    word_count: int
    tags: list[str] = field(default_factory=list)
    cta: str = ""
    created_at: datetime = field(default_factory=utcnow)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "content_type": self.content_type,
            "channel": self.channel,
            "locale": self.locale,
            "topic": self.topic,
            "title": self.title,
            "body_markdown": self.body_markdown,
            "word_count": self.word_count,
            "tags": self.tags,
            "cta": self.cta,
            "created_at": self.created_at.isoformat(),
        }


DEFAULT_LENGTHS: dict[ContentType, int] = {
    "article": 800,
    "linkedin_post": 200,
    "case_study": 600,
    "newsletter": 400,
    "tweet_thread": 250,
}

DEFAULT_AUDIENCE: dict[str, str] = {
    "ar": "مدراء العمليات والمبيعات في الشركات السعودية المتوسطة والكبيرة",
    "en": "Operations and sales leaders at mid-to-large Saudi companies",
}

DEFAULT_CTA: dict[str, str] = {
    "ar": "احجز استشارة مجانية 30 دقيقة لمعرفة كيف نطبّق هذا على شركتك",
    "en": "Book a free 30-minute consultation to see how this applies to your company",
}


class ContentCreatorAgent(BaseAgent):
    """Generates channel-appropriate content."""

    name = "content_creator"

    async def run(
        self,
        *,
        topic: str,
        content_type: ContentType = "article",
        channel: Channel = "blog",
        locale: str = "ar",
        audience: str | None = None,
        goal: str = "educate prospects and drive consultation bookings",
        length: int | None = None,
        cta: str | None = None,
        **_: Any,
    ) -> ContentPiece:
        """Generate a content piece."""
        length = length or DEFAULT_LENGTHS.get(content_type, 500)
        audience = audience or DEFAULT_AUDIENCE.get(locale, DEFAULT_AUDIENCE["en"])
        cta = cta or DEFAULT_CTA.get(locale, DEFAULT_CTA["en"])

        prompt = get_prompt(
            "content_writer",
            audience=audience,
            goal=goal,
            channel=channel,
            locale=locale,
            topic=topic,
            length=length,
            cta=cta,
        )

        # Arabic content → GLM (stronger for Arabic), else Claude
        task = Task.ARABIC_TASKS if locale == "ar" else Task.PAGE_COPY
        response = await self.router.run(
            task=task,
            messages=[Message(role="user", content=prompt)],
            max_tokens=min(length * 4, 4000),
            temperature=0.65,
        )

        body = response.content.strip()
        title = self._extract_title(body) or topic
        word_count = len(body.split())
        tags = self._extract_tags(topic, content_type)

        piece = ContentPiece(
            id=generate_id("cnt"),
            content_type=content_type,
            channel=channel,
            locale=locale,
            topic=topic,
            title=title,
            body_markdown=body,
            word_count=word_count,
            tags=tags,
            cta=cta,
        )
        self.log.info(
            "content_generated",
            id=piece.id,
            content_type=content_type,
            locale=locale,
            words=word_count,
        )
        return piece

    # ── Helpers ─────────────────────────────────────────────────
    @staticmethod
    def _extract_title(body: str) -> str | None:
        for line in body.splitlines():
            stripped = line.strip()
            if stripped.startswith("# "):
                return stripped.lstrip("# ").strip()
            if stripped and not stripped.startswith("#"):
                # First non-empty line as fallback title
                return stripped[:120]
        return None

    @staticmethod
    def _extract_tags(topic: str, content_type: ContentType) -> list[str]:
        tags = [content_type, "ai", "saudi-arabia"]
        keywords = ["healthcare", "real_estate", "logistics", "retail", "finance", "education"]
        for k in keywords:
            if k in topic.lower().replace(" ", "_"):
                tags.append(k)
        return tags
