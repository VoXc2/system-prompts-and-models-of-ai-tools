"""
Proposal Agent — generates tailored proposals using Claude.
وكيل العروض — يُعدّ عروضاً مخصصة باستخدام Claude.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

from auto_client_acquisition.agents.icp_matcher import FitScore
from auto_client_acquisition.agents.intake import Lead
from core.agents.base import BaseAgent
from core.config.models import Task
from core.config.settings import get_settings
from core.llm.base import Message
from core.prompts import get_prompt
from core.utils import generate_id, utcnow


@dataclass
class Proposal:
    id: str
    lead_id: str
    company_name: str
    sector: str | None
    locale: str
    body_markdown: str
    budget_min: float
    budget_max: float
    currency: str
    valid_until: datetime
    created_at: datetime = field(default_factory=utcnow)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "lead_id": self.lead_id,
            "company_name": self.company_name,
            "sector": self.sector,
            "locale": self.locale,
            "body_markdown": self.body_markdown,
            "budget_min": self.budget_min,
            "budget_max": self.budget_max,
            "currency": self.currency,
            "valid_until": self.valid_until.isoformat(),
            "created_at": self.created_at.isoformat(),
        }


class ProposalAgent(BaseAgent):
    """Generates an LLM-authored proposal tailored to the lead."""

    name = "proposal"

    def __init__(self) -> None:
        super().__init__()
        self.settings = get_settings()

    async def run(
        self,
        *,
        lead: Lead,
        fit_score: FitScore | None = None,
        outcomes: list[str] | None = None,
        start_date: datetime | None = None,
        **_: Any,
    ) -> Proposal:
        """Generate a proposal tailored to the lead context."""
        outcomes = outcomes or [
            "Reduce manual work by 50%+",
            "Increase qualified pipeline by 2–3x",
            "Cut response time from hours to minutes",
        ]
        start_date = start_date or (utcnow() + timedelta(days=14))

        # Determine pricing tier based on region
        budget_min, budget_max, currency = self._pricing_for_region(lead.region)

        prompt = get_prompt(
            "proposal_generation",
            locale=lead.locale,
            company_name=lead.company_name or "Your Company",
            sector=lead.sector or "General",
            pain_points="; ".join(lead.pain_points) or lead.message or "To be confirmed",
            outcomes="; ".join(outcomes),
            budget_min=f"{budget_min:,.0f}",
            budget_max=f"{budget_max:,.0f}",
            start_date=start_date.strftime("%Y-%m-%d"),
        )

        response = await self.router.run(
            task=Task.PROPOSAL,
            messages=[Message(role="user", content=prompt)],
            max_tokens=3000,
            temperature=0.5,
        )

        proposal = Proposal(
            id=generate_id("prop"),
            lead_id=lead.id,
            company_name=lead.company_name,
            sector=lead.sector,
            locale=lead.locale,
            body_markdown=response.content,
            budget_min=budget_min,
            budget_max=budget_max,
            currency=currency,
            valid_until=utcnow() + timedelta(days=30),
        )

        self.log.info(
            "proposal_generated",
            lead_id=lead.id,
            proposal_id=proposal.id,
            locale=lead.locale,
            budget_range=f"{budget_min:,.0f}-{budget_max:,.0f} {currency}",
        )
        return proposal

    # ── Pricing logic ───────────────────────────────────────────
    def _pricing_for_region(self, region: str | None) -> tuple[float, float, str]:
        """Return (setup_min, setup_max, currency) for the lead's region."""
        s = self.settings
        if not region:
            return float(s.pricing_sa_setup_min), float(s.pricing_sa_setup_max), "SAR"

        region_lower = region.lower()
        gcc_tokens = {"uae", "kuwait", "bahrain", "qatar", "oman", "الإمارات", "الكويت"}
        if any(t in region_lower for t in gcc_tokens):
            return (
                float(s.pricing_gcc_setup_min),
                float(s.pricing_gcc_setup_max),
                "SAR-equivalent",
            )
        sa_tokens = {"saudi", "ksa", "sa", "riyadh", "jeddah", "السعودية"}
        if any(t in region_lower for t in sa_tokens):
            return (float(s.pricing_sa_setup_min), float(s.pricing_sa_setup_max), "SAR")
        # Global
        return (
            float(s.pricing_global_setup_min_usd),
            float(s.pricing_global_setup_max_usd),
            "USD",
        )
