"""
Phase 9 Orchestrator — coordinates autonomous growth agents.
منسّق المرحلة 9.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from autonomous_growth.agents.competitor import CompetitorMonitorAgent, CompetitorSummary
from autonomous_growth.agents.content import ContentCreatorAgent, ContentPiece
from autonomous_growth.agents.distribution import DistributionAgent, DistributionPlan
from autonomous_growth.agents.market_research import MarketResearchAgent, ResearchFinding
from autonomous_growth.agents.sector_intel import SaudiSector, SectorIntel, SectorIntelAgent
from core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class GrowthRunResult:
    sector_intel: SectorIntel | None = None
    research: ResearchFinding | None = None
    content: ContentPiece | None = None
    distribution: DistributionPlan | None = None
    competitor_summary: CompetitorSummary | None = None
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "sector_intel": self.sector_intel.to_dict() if self.sector_intel else None,
            "research": self.research.to_dict() if self.research else None,
            "content": self.content.to_dict() if self.content else None,
            "distribution": self.distribution.to_dict() if self.distribution else None,
            "competitor_summary": (
                self.competitor_summary.to_dict() if self.competitor_summary else None
            ),
            "warnings": self.warnings,
        }


class GrowthOrchestrator:
    """Runs a growth campaign: research → content → distribution."""

    def __init__(self) -> None:
        self.sector_intel = SectorIntelAgent()
        self.research = MarketResearchAgent()
        self.content = ContentCreatorAgent()
        self.distribution = DistributionAgent()
        self.competitor = CompetitorMonitorAgent()
        self.log = logger.bind(component="growth_orchestrator")

    async def run_sector_campaign(
        self,
        sector: SaudiSector | str,
        *,
        locale: str = "ar",
        content_type: str = "article",
        channels: list[str] | None = None,
    ) -> GrowthRunResult:
        """End-to-end: intel → research → article → distribution plan."""
        result = GrowthRunResult()

        # 1. Sector intel baseline
        try:
            result.sector_intel = await self.sector_intel.run(sector=sector, enrich_with_llm=False)
        except Exception as e:
            self.log.warning("sector_intel_failed", error=str(e))
            result.warnings.append(f"sector_intel_failed: {e}")

        if result.sector_intel is None:
            return result

        # 2. Research question
        si = result.sector_intel
        question = (
            f"What are the top 3 AI use-cases with the fastest payback in the Saudi "
            f"{si.sector.value} sector? Include concrete examples and numbers where possible."
        )
        try:
            result.research = await self.research.run(
                question=question, locale=locale, depth="standard"
            )
        except Exception as e:
            self.log.warning("research_failed", error=str(e))
            result.warnings.append(f"research_failed: {e}")

        # 3. Content piece using research findings
        try:
            topic = (
                f"أفضل 3 استخدامات للذكاء الاصطناعي في قطاع {si.sector.value} السعودي"
                if locale == "ar"
                else f"Top 3 AI use-cases in the Saudi {si.sector.value} sector"
            )
            result.content = await self.content.run(
                topic=topic,
                content_type=content_type,  # type: ignore[arg-type]
                locale=locale,
            )
        except Exception as e:
            self.log.warning("content_failed", error=str(e))
            result.warnings.append(f"content_failed: {e}")

        # 4. Distribution plan
        if result.content:
            try:
                result.distribution = await self.distribution.run(
                    content=result.content,
                    channels=channels or ["blog", "linkedin"],
                )
            except Exception as e:
                self.log.warning("distribution_failed", error=str(e))
                result.warnings.append(f"distribution_failed: {e}")

        self.log.info(
            "growth_run_complete",
            sector=si.sector.value,
            warnings=len(result.warnings),
        )
        return result
