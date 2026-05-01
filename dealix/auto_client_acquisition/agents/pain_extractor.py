"""
Pain Extractor — extracts pain points, urgency, and next-step hints.
وكيل استخلاص المشاكل — يستخرج المشاكل ودرجة الاستعجال والخطوة التالية.

Hybrid approach:
1. Fast keyword pass (local, zero-cost)
2. Optional LLM pass for richer extraction (routed to GLM for Arabic)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from core.agents.base import BaseAgent
from core.config.models import Task
from core.llm.base import Message
from core.prompts import get_prompt
from core.utils import detect_locale

PAIN_KEYWORDS: dict[str, str] = {
    # Arabic
    "مشكلة": "general",
    "معقد": "complexity",
    "بطيء": "performance",
    "نحتاج": "need",
    "نفتقر": "missing",
    "صعوبة": "difficulty",
    "نعاني": "struggle",
    "يدوي": "manual",
    "فوضى": "chaos",
    "مكلف": "cost",
    "تأخير": "delay",
    # English
    "problem": "general",
    "issue": "general",
    "need": "need",
    "struggling": "struggle",
    "challenge": "challenge",
    "manual": "manual",
    "slow": "performance",
    "expensive": "cost",
    "inefficient": "efficiency",
    "missing": "missing",
    "broken": "broken",
}

URGENCY_KEYWORDS: dict[str, float] = {
    # Arabic
    "عاجل": 1.0,
    "فوراً": 1.0,
    "الآن": 0.8,
    "بسرعة": 0.7,
    "هذا الأسبوع": 0.6,
    "هذا الشهر": 0.5,
    "قريباً": 0.4,
    # English
    "urgent": 1.0,
    "asap": 1.0,
    "now": 0.8,
    "quickly": 0.7,
    "this week": 0.6,
    "this month": 0.5,
    "soon": 0.4,
    "immediately": 1.0,
}


@dataclass
class PainPoint:
    text: str
    category: str
    severity: float = 0.5

    def to_dict(self) -> dict[str, Any]:
        return {
            "text": self.text,
            "category": self.category,
            "severity": round(self.severity, 2),
        }


@dataclass
class ExtractionResult:
    pain_points: list[PainPoint] = field(default_factory=list)
    urgency_score: float = 0.0
    likely_offer: str = ""
    recommended_next_step: str = ""
    key_phrases: list[str] = field(default_factory=list)
    method: str = "keyword"  # keyword | llm | hybrid

    def to_dict(self) -> dict[str, Any]:
        return {
            "pain_points": [p.to_dict() for p in self.pain_points],
            "urgency_score": round(self.urgency_score, 2),
            "likely_offer": self.likely_offer,
            "recommended_next_step": self.recommended_next_step,
            "key_phrases": self.key_phrases,
            "method": self.method,
        }


class PainExtractorAgent(BaseAgent):
    """Extracts pain signals from lead messages."""

    name = "pain_extractor"

    async def run(
        self,
        *,
        message: str,
        locale: str | None = None,
        use_llm: bool = True,
        **_: Any,
    ) -> ExtractionResult:
        """Run keyword pass, optionally enrich with LLM."""
        if not message or not message.strip():
            return ExtractionResult(method="empty")

        locale = locale or detect_locale(message)
        kw_result = self._keyword_pass(message)

        if not use_llm:
            kw_result.method = "keyword"
            return kw_result

        # LLM enrichment — route to GLM for Arabic, Claude otherwise
        try:
            task = Task.ARABIC_TASKS if locale == "ar" else Task.REASONING
            prompt = get_prompt("pain_extraction", locale=locale, message=message)
            response = await self.router.run(
                task=task,
                messages=[Message(role="user", content=prompt)],
                max_tokens=1024,
                temperature=0.2,
            )
            parsed = self.parse_json_response(response.content)
            llm_result = self._from_llm_json(parsed)
            merged = self._merge(kw_result, llm_result)
            merged.method = "hybrid"
            self.log.info(
                "pain_extracted",
                n_pains=len(merged.pain_points),
                urgency=merged.urgency_score,
                locale=locale,
            )
            return merged
        except Exception as e:
            self.log.warning("llm_extract_failed_falling_back", error=str(e))
            kw_result.method = "keyword"
            return kw_result

    # ── Keyword pass ────────────────────────────────────────────
    def _keyword_pass(self, text: str) -> ExtractionResult:
        lower = text.lower()
        pains: list[PainPoint] = []
        key_phrases: list[str] = []

        for keyword, category in PAIN_KEYWORDS.items():
            if keyword in lower:
                pains.append(PainPoint(text=keyword, category=category, severity=0.5))
                key_phrases.append(keyword)

        urgency = 0.0
        for keyword, score in URGENCY_KEYWORDS.items():
            if keyword in lower:
                urgency = max(urgency, score)
                key_phrases.append(keyword)

        return ExtractionResult(
            pain_points=pains,
            urgency_score=urgency,
            likely_offer=self._suggest_offer(pains),
            recommended_next_step=self._suggest_step(urgency, len(pains)),
            key_phrases=list(set(key_phrases)),
            method="keyword",
        )

    @staticmethod
    def _suggest_offer(pains: list[PainPoint]) -> str:
        categories = {p.category for p in pains}
        if "manual" in categories or "efficiency" in categories:
            return "Process Automation Retainer"
        if "performance" in categories:
            return "AI Performance Optimization Setup"
        if "cost" in categories:
            return "Cost Reduction AI Assessment"
        if categories:
            return "Discovery Workshop + Proposal"
        return "Discovery Call"

    @staticmethod
    def _suggest_step(urgency: float, n_pains: int) -> str:
        if urgency >= 0.8:
            return "Call within 24 hours — high urgency"
        if urgency >= 0.5 or n_pains >= 2:
            return "Book discovery call this week"
        return "Send value-add nurture sequence"

    # ── LLM JSON parsing ────────────────────────────────────────
    def _from_llm_json(self, data: dict[str, Any]) -> ExtractionResult:
        raw_pains = data.get("pain_points") or []
        pains: list[PainPoint] = []
        for p in raw_pains:
            if isinstance(p, dict):
                pains.append(
                    PainPoint(
                        text=str(p.get("text", "")),
                        category=str(p.get("category", "general")),
                        severity=float(p.get("severity", 0.5)),
                    )
                )
            elif isinstance(p, str):
                pains.append(PainPoint(text=p, category="general", severity=0.5))

        return ExtractionResult(
            pain_points=pains,
            urgency_score=float(data.get("urgency_score", 0.0)),
            likely_offer=str(data.get("likely_offer", "")),
            recommended_next_step=str(data.get("recommended_next_step", "")),
            key_phrases=list(data.get("key_phrases") or []),
            method="llm",
        )

    @staticmethod
    def _merge(kw: ExtractionResult, llm: ExtractionResult) -> ExtractionResult:
        """LLM takes priority for rich fields; keyword augments key_phrases."""
        combined_pains = {p.text.lower(): p for p in kw.pain_points}
        for p in llm.pain_points:
            combined_pains[p.text.lower()] = p  # overwrite with LLM version

        return ExtractionResult(
            pain_points=list(combined_pains.values()),
            urgency_score=max(kw.urgency_score, llm.urgency_score),
            likely_offer=llm.likely_offer or kw.likely_offer,
            recommended_next_step=llm.recommended_next_step or kw.recommended_next_step,
            key_phrases=list(set(kw.key_phrases + llm.key_phrases)),
            method="hybrid",
        )
