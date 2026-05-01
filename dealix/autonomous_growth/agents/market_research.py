"""
Market Research Agent — uses Gemini for source-dense research.
وكيل بحث السوق — يستخدم Gemini للبحث المعتمد على المصادر.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from core.agents.base import BaseAgent
from core.config.models import Task
from core.llm.base import Message
from core.utils import generate_id, utcnow


@dataclass
class ResearchFinding:
    id: str
    question: str
    summary: str
    bullet_points: list[str] = field(default_factory=list)
    locale: str = "en"
    created_at: datetime = field(default_factory=utcnow)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "question": self.question,
            "summary": self.summary,
            "bullet_points": self.bullet_points,
            "locale": self.locale,
            "created_at": self.created_at.isoformat(),
        }


class MarketResearchAgent(BaseAgent):
    """Runs open-ended research questions through Gemini."""

    name = "market_research"

    async def run(
        self,
        *,
        question: str,
        locale: str = "en",
        depth: str = "standard",  # quick | standard | deep
        **_: Any,
    ) -> ResearchFinding:
        """Answer a research question with bullet-pointed summary."""
        depth_tokens = {"quick": 800, "standard": 1500, "deep": 3000}.get(depth, 1500)

        system = (
            "You are a market research analyst specializing in the Saudi and GCC markets. "
            "Prefer concrete facts, numbers, and named entities. "
            "If uncertain, say so explicitly. Output structured markdown."
        )
        user_prompt = (
            f"Research question (answer in {'Arabic' if locale == 'ar' else 'English'}):\n"
            f"{question}\n\n"
            "Structure the answer as:\n"
            "## Summary (3-4 sentences)\n"
            "## Key Points (5-8 bullets)\n"
            "## Caveats / Unknowns\n"
        )

        response = await self.router.run(
            task=Task.RESEARCH,
            messages=[Message(role="user", content=user_prompt)],
            system=system,
            max_tokens=depth_tokens,
            temperature=0.3,
        )

        summary, bullets = self._parse_markdown(response.content)

        finding = ResearchFinding(
            id=generate_id("rsrch"),
            question=question,
            summary=summary,
            bullet_points=bullets,
            locale=locale,
        )

        self.log.info(
            "research_done",
            id=finding.id,
            depth=depth,
            n_bullets=len(bullets),
        )
        return finding

    @staticmethod
    def _parse_markdown(md: str) -> tuple[str, list[str]]:
        """Extract summary + bullets sections loosely."""
        lines = md.splitlines()
        section: str | None = None
        summary_parts: list[str] = []
        bullets: list[str] = []

        for line in lines:
            stripped = line.strip()
            lower = stripped.lower()
            if lower.startswith("## ") and ("summary" in lower or "ملخص" in lower):
                section = "summary"
                continue
            if lower.startswith("## ") and (
                "key points" in lower or "النقاط" in lower or "bullet" in lower
            ):
                section = "bullets"
                continue
            if lower.startswith("## "):
                section = "other"
                continue

            if section == "summary" and stripped and not stripped.startswith("#"):
                summary_parts.append(stripped)
            elif section == "bullets" and (stripped.startswith("-") or stripped.startswith("*")):
                bullets.append(stripped.lstrip("-* ").strip())

        summary = " ".join(summary_parts)
        return summary or md[:300], bullets
