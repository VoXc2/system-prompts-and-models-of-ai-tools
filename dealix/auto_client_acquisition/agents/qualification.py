"""
Qualification Agent — generates BANT questions and updates Fit Score.
وكيل التأهيل — يُولّد أسئلة BANT ويُحدّث درجة الملاءمة.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from auto_client_acquisition.agents.icp_matcher import FitScore
from auto_client_acquisition.agents.intake import Lead, LeadStatus
from core.agents.base import BaseAgent
from core.config.models import Task
from core.llm.base import Message
from core.prompts import get_prompt


@dataclass
class QualificationQuestion:
    q: str
    bant: str  # budget | authority | need | timeline
    why: str
    answered: bool = False
    answer: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "q": self.q,
            "bant": self.bant,
            "why": self.why,
            "answered": self.answered,
            "answer": self.answer,
        }


@dataclass
class QualificationResult:
    questions: list[QualificationQuestion] = field(default_factory=list)
    budget_clarified: bool = False
    authority_confirmed: bool = False
    need_explicit: bool = False
    timeline_known: bool = False
    new_status: LeadStatus = LeadStatus.NEW
    updated_fit: FitScore | None = None

    @property
    def bant_score(self) -> float:
        return (
            int(self.budget_clarified)
            + int(self.authority_confirmed)
            + int(self.need_explicit)
            + int(self.timeline_known)
        ) / 4.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "questions": [q.to_dict() for q in self.questions],
            "budget_clarified": self.budget_clarified,
            "authority_confirmed": self.authority_confirmed,
            "need_explicit": self.need_explicit,
            "timeline_known": self.timeline_known,
            "bant_score": round(self.bant_score, 2),
            "new_status": self.new_status.value,
            "updated_fit": self.updated_fit.to_dict() if self.updated_fit else None,
        }


class QualificationAgent(BaseAgent):
    """Generates discovery questions and advances lead status."""

    name = "qualification"

    async def run(
        self,
        *,
        lead: Lead,
        fit_score: FitScore | None = None,
        answers: dict[str, str] | None = None,
        **_: Any,
    ) -> QualificationResult:
        """Produce 5 BANT-style qualification questions (and ingest answers if provided)."""
        context = self._build_context(lead, fit_score)
        prompt = get_prompt("qualification_questions", locale=lead.locale, context=context)

        try:
            response = await self.router.run(
                task=Task.REASONING,
                messages=[Message(role="user", content=prompt)],
                max_tokens=800,
                temperature=0.3,
            )
            parsed = self.parse_json_response(response.content)
            raw_questions = parsed.get("questions", [])
            questions = [
                QualificationQuestion(
                    q=str(q.get("q", "")),
                    bant=str(q.get("bant", "need")).lower(),
                    why=str(q.get("why", "")),
                )
                for q in raw_questions
                if isinstance(q, dict)
            ]
        except Exception as e:
            self.log.warning("llm_qual_failed_using_fallback", error=str(e))
            questions = self._fallback_questions(lead.locale)

        # Ingest answers if user provided them
        budget_clarified = lead.budget is not None
        need_explicit = bool(lead.pain_points) or bool(lead.message)
        authority_confirmed = False
        timeline_known = False

        if answers:
            for q in questions:
                key = q.bant
                if answers.get(key):
                    q.answered = True
                    q.answer = answers[key]
            authority_confirmed = bool(answers.get("authority"))
            timeline_known = bool(answers.get("timeline"))
            if answers.get("budget"):
                budget_clarified = True
            if answers.get("need"):
                need_explicit = True

        # Determine new status
        bant_total = sum([budget_clarified, authority_confirmed, need_explicit, timeline_known])
        if bant_total >= 3:
            new_status = LeadStatus.QUALIFIED
        elif bant_total >= 2:
            new_status = LeadStatus.DISCOVERY
        else:
            new_status = lead.status

        result = QualificationResult(
            questions=questions,
            budget_clarified=budget_clarified,
            authority_confirmed=authority_confirmed,
            need_explicit=need_explicit,
            timeline_known=timeline_known,
            new_status=new_status,
        )
        self.log.info(
            "qualification_done",
            lead_id=lead.id,
            bant_score=result.bant_score,
            new_status=new_status.value,
        )
        return result

    # ── Helpers ─────────────────────────────────────────────────
    @staticmethod
    def _build_context(lead: Lead, fit: FitScore | None) -> str:
        parts = [
            f"Company: {lead.company_name}",
            f"Sector: {lead.sector or 'unknown'}",
            f"Size: {lead.company_size or 'unknown'}",
            f"Region: {lead.region or 'unknown'}",
            f"Budget: {lead.budget or 'unknown'}",
            f"Message: {lead.message or '(none)'}",
            f"Locale: {lead.locale}",
        ]
        if fit:
            parts.append(f"Fit tier: {fit.tier} (score {fit.overall_score:.2f})")
            parts.append(f"Recommendations: {'; '.join(fit.recommendations)}")
        return "\n".join(parts)

    @staticmethod
    def _fallback_questions(locale: str) -> list[QualificationQuestion]:
        if locale == "ar":
            return [
                QualificationQuestion(
                    q="ما الميزانية التقريبية المخصصة لهذا المشروع هذا الربع؟",
                    bant="budget",
                    why="تحديد النطاق المناسب من الحل",
                ),
                QualificationQuestion(
                    q="من سيشارك في اتخاذ قرار الاعتماد؟",
                    bant="authority",
                    why="التأكد من وجود صانع القرار",
                ),
                QualificationQuestion(
                    q="ما أكبر تحدٍ محدد تحاولون حله الآن؟",
                    bant="need",
                    why="ربط الحل بمشكلة حقيقية",
                ),
                QualificationQuestion(
                    q="ما الإطار الزمني المثالي لبدء العمل؟",
                    bant="timeline",
                    why="قياس مدى الاستعجال",
                ),
                QualificationQuestion(
                    q="هل جربتم حلولاً سابقة لهذه المشكلة؟ وماذا حدث؟",
                    bant="need",
                    why="فهم السياق وتجنب تكرار الأخطاء",
                ),
            ]
        return [
            QualificationQuestion(
                q="What budget is earmarked for this initiative this quarter?",
                bant="budget",
                why="To size the solution appropriately",
            ),
            QualificationQuestion(
                q="Who else is involved in the decision?",
                bant="authority",
                why="Confirm decision-maker is in the loop",
            ),
            QualificationQuestion(
                q="What's the single biggest problem you're trying to solve?",
                bant="need",
                why="Anchor the solution to real pain",
            ),
            QualificationQuestion(
                q="What timeline would you ideally want to start?",
                bant="timeline",
                why="Gauge urgency",
            ),
            QualificationQuestion(
                q="Have you tried anything for this before? What happened?",
                bant="need",
                why="Avoid re-running failed approaches",
            ),
        ]
