"""
Competitor Monitor — summarizes competitor positioning from provided data.
وكيل مراقبة المنافسين — يلخّص وضع المنافسين من البيانات المُقدّمة.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from core.agents.base import BaseAgent
from core.config.models import Task
from core.llm.base import Message
from core.prompts import get_prompt
from core.utils import generate_id, utcnow


@dataclass
class CompetitorSummary:
    id: str
    competitor_name: str
    locale: str
    positioning: str = ""
    pricing_hints: str = ""
    strengths: list[str] = field(default_factory=list)
    weaknesses: list[str] = field(default_factory=list)
    counter_moves: list[str] = field(default_factory=list)
    summary_markdown: str = ""
    created_at: datetime = field(default_factory=utcnow)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "competitor_name": self.competitor_name,
            "locale": self.locale,
            "positioning": self.positioning,
            "pricing_hints": self.pricing_hints,
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "counter_moves": self.counter_moves,
            "summary_markdown": self.summary_markdown,
            "created_at": self.created_at.isoformat(),
        }


class CompetitorMonitorAgent(BaseAgent):
    """Analyzes competitor info and suggests counter-moves."""

    name = "competitor_monitor"

    async def run(
        self,
        *,
        competitor_name: str,
        competitor_data: str,
        locale: str = "ar",
        **_: Any,
    ) -> CompetitorSummary:
        """Summarize competitor, extract counter-moves."""
        prompt = get_prompt(
            "competitor_summary",
            locale=locale,
            data=f"Competitor: {competitor_name}\n\n{competitor_data}",
        )

        response = await self.router.run(
            task=Task.REASONING,
            messages=[Message(role="user", content=prompt)],
            max_tokens=800,
            temperature=0.3,
        )
        markdown = response.content.strip()

        summary = CompetitorSummary(
            id=generate_id("comp"),
            competitor_name=competitor_name,
            locale=locale,
            summary_markdown=markdown,
        )
        # Best-effort section extraction
        self._populate_sections(summary, markdown)

        self.log.info(
            "competitor_analyzed",
            id=summary.id,
            name=competitor_name,
            n_weaknesses=len(summary.weaknesses),
        )
        return summary

    @staticmethod
    def _populate_sections(summary: CompetitorSummary, markdown: str) -> None:
        """Parse bullet sections loosely."""
        lines = markdown.splitlines()
        current: list[str] | None = None
        for line in lines:
            s = line.strip()
            lower = s.lower()
            if any(t in lower for t in ("strength", "نقاط القوة", "القوة")):
                current = summary.strengths
                continue
            if any(t in lower for t in ("weakness", "نقاط الضعف", "الضعف")):
                current = summary.weaknesses
                continue
            if any(t in lower for t in ("counter", "مضاد", "الحركات المضادة")):
                current = summary.counter_moves
                continue
            if any(t in lower for t in ("pricing", "السعر", "الأسعار")):
                summary.pricing_hints = s
                current = None
                continue
            if any(t in lower for t in ("position", "التموضع", "الوضع")):
                summary.positioning = s
                current = None
                continue

            if current is not None and (s.startswith("-") or s.startswith("*")):
                current.append(s.lstrip("-* ").strip())
