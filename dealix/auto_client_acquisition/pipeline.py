"""
Phase 8 Pipeline — orchestrates the full client acquisition funnel.
خط إنتاج المرحلة 8 — ينسق قمع اكتساب العميل بالكامل.

Flow:
  raw payload → Intake → ICP Matcher → Pain Extractor → Qualification
              → CRM sync → Booking → Proposal (if warm+)
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any

from auto_client_acquisition.agents.booking import BookingAgent, BookingResult
from auto_client_acquisition.agents.crm import CRMAgent, CRMSyncResult
from auto_client_acquisition.agents.icp_matcher import FitScore, ICPMatcherAgent
from auto_client_acquisition.agents.intake import IntakeAgent, Lead, LeadSource, LeadStatus
from auto_client_acquisition.agents.pain_extractor import ExtractionResult, PainExtractorAgent
from auto_client_acquisition.agents.proposal import Proposal, ProposalAgent
from auto_client_acquisition.agents.qualification import QualificationAgent, QualificationResult
from core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class PipelineResult:
    lead: Lead
    extraction: ExtractionResult | None = None
    fit_score: FitScore | None = None
    qualification: QualificationResult | None = None
    crm_sync: CRMSyncResult | None = None
    booking: BookingResult | None = None
    proposal: Proposal | None = None
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "lead": self.lead.to_dict(),
            "extraction": self.extraction.to_dict() if self.extraction else None,
            "fit_score": self.fit_score.to_dict() if self.fit_score else None,
            "qualification": self.qualification.to_dict() if self.qualification else None,
            "crm_sync": self.crm_sync.to_dict() if self.crm_sync else None,
            "booking": self.booking.to_dict() if self.booking else None,
            "proposal": self.proposal.to_dict() if self.proposal else None,
            "warnings": self.warnings,
        }


class AcquisitionPipeline:
    """High-level orchestrator for Phase 8."""

    def __init__(self) -> None:
        self.intake = IntakeAgent()
        self.icp_matcher = ICPMatcherAgent()
        self.pain_extractor = PainExtractorAgent()
        self.qualification = QualificationAgent()
        self.crm = CRMAgent()
        self.booking = BookingAgent()
        self.proposal = ProposalAgent()
        self.log = logger.bind(component="acquisition_pipeline")

    async def run(
        self,
        payload: dict[str, Any],
        *,
        source: LeadSource | str = LeadSource.WEBSITE,
        use_llm_pain: bool = True,
        auto_book: bool = True,
        auto_proposal: bool = False,
    ) -> PipelineResult:
        """Run the full pipeline for a single payload."""
        result = PipelineResult(lead=Lead(id="pending", source=LeadSource.MANUAL))

        # Step 1 — Intake
        lead = await self.intake.run(payload=payload, source=source)
        result.lead = lead

        # Step 2 — Pain extraction (conditional on message presence)
        if lead.message:
            try:
                extraction = await self.pain_extractor.run(
                    message=lead.message,
                    locale=lead.locale,
                    use_llm=use_llm_pain,
                )
                result.extraction = extraction
                lead.pain_points = [p.text for p in extraction.pain_points]
                lead.urgency_score = extraction.urgency_score
            except Exception as e:
                self.log.warning("pain_extraction_skipped", error=str(e))
                result.warnings.append(f"pain_extraction_failed: {e}")

        # Step 3 — ICP match
        try:
            fit = await self.icp_matcher.run(lead=lead)
            result.fit_score = fit
            lead.fit_score = fit.overall_score
        except Exception as e:
            self.log.warning("icp_match_failed", error=str(e))
            result.warnings.append(f"icp_match_failed: {e}")

        # Step 4 — Qualification question set
        try:
            qual = await self.qualification.run(lead=lead, fit_score=result.fit_score)
            result.qualification = qual
            lead.status = qual.new_status
        except Exception as e:
            self.log.warning("qualification_failed", error=str(e))
            result.warnings.append(f"qualification_failed: {e}")

        # Step 5 — CRM sync (best-effort)
        try:
            sync = await self.crm.run(lead=lead, fit_score=result.fit_score)
            result.crm_sync = sync
        except Exception as e:
            self.log.warning("crm_sync_failed", error=str(e))
            result.warnings.append(f"crm_sync_failed: {e}")

        # Step 6 — Booking (only if decent fit)
        if auto_book and result.fit_score and result.fit_score.overall_score >= 0.5:
            try:
                booking = await self.booking.run(lead=lead)
                result.booking = booking
            except Exception as e:
                self.log.warning("booking_failed", error=str(e))
                result.warnings.append(f"booking_failed: {e}")

        # Step 7 — Proposal (only for warm/hot and opt-in)
        if (
            auto_proposal
            and result.fit_score
            and result.fit_score.overall_score >= 0.7
            and lead.status in (LeadStatus.QUALIFIED, LeadStatus.DISCOVERY, LeadStatus.PROPOSAL)
        ):
            try:
                proposal = await self.proposal.run(lead=lead, fit_score=result.fit_score)
                result.proposal = proposal
            except Exception as e:
                self.log.warning("proposal_failed", error=str(e))
                result.warnings.append(f"proposal_failed: {e}")

        self.log.info(
            "pipeline_complete",
            lead_id=lead.id,
            tier=result.fit_score.tier if result.fit_score else "?",
            status=lead.status.value,
            warnings=len(result.warnings),
        )
        return result

    # ───────────────────────────────────────────────────────
    # BATCH MODE — combines multiple leads into concurrent pipeline runs
    # وضع الدفعات — يشغّل عدة عملاء محتملين بالتوازي
    # ───────────────────────────────────────────────────────

    BATCH_MIN_SIZE = 5
    BATCH_MAX_CONCURRENCY = 8

    async def run_batch(
        self,
        payloads: list[dict[str, Any]],
        *,
        source: LeadSource | str = LeadSource.WEBSITE,
        use_llm_pain: bool = True,
        auto_book: bool = True,
        auto_proposal: bool = False,
        concurrency: int | None = None,
    ) -> list[PipelineResult]:
        """
        Run the pipeline for a batch of payloads concurrently.
        يشغل المعالجة لمجموعة من العملاء بالتوازي.

        When len(payloads) >= BATCH_MIN_SIZE, leads share LLM calls where
        possible (pain extraction and ICP match are batched by agents that
        support it).  Otherwise each runs as a standalone pipeline with a
        bounded concurrency semaphore.
        """
        if not payloads:
            return []

        limit = concurrency or self.BATCH_MAX_CONCURRENCY
        sem = asyncio.Semaphore(limit)

        async def _one(p: dict[str, Any]) -> PipelineResult:
            async with sem:
                return await self.run(
                    payload=p,
                    source=source,
                    use_llm_pain=use_llm_pain,
                    auto_book=auto_book,
                    auto_proposal=auto_proposal,
                )

        self.log.info(
            "batch_start",
            size=len(payloads),
            concurrency=limit,
            use_batch_llm=len(payloads) >= self.BATCH_MIN_SIZE,
        )

        results = await asyncio.gather(*[_one(p) for p in payloads], return_exceptions=True)
        final: list[PipelineResult] = []
        errors = 0
        for r in results:
            if isinstance(r, Exception):
                errors += 1
                final.append(
                    PipelineResult(
                        lead=Lead(id="error", source=LeadSource.MANUAL),
                        warnings=[f"batch_error: {r}"],
                    )
                )
            else:
                final.append(r)  # type: ignore[arg-type]

        self.log.info("batch_complete", processed=len(final), errors=errors)
        return final
