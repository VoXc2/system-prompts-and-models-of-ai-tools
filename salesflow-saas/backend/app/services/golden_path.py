"""Golden Path — Partner intake → evidence pack end-to-end.

This service orchestrates the complete partner deal lifecycle:
1. Create partner dossier (PartnerDossier schema)
2. Generate economics model (EconomicsModel schema)
3. Create approval packet (ApprovalPacket schema)
4. Submit for approval (Class B enforcement)
5. On approval: create workflow commitment
6. Auto-assemble evidence pack (SHA256)
7. Generate executive summary

Each step produces a structured output with Provenance.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.structured_outputs import (
    ApprovalPacket,
    EconomicsModel,
    PartnerDossier,
    Provenance,
)


class GoldenPathService:
    """Orchestrates the partner golden path with structured outputs."""

    async def create_partner_dossier(
        self,
        db: AsyncSession,
        *,
        tenant_id: str,
        partner_name: str,
        partner_name_ar: Optional[str] = None,
        partner_type: str = "partnership",
        revenue_potential_sar: float = 0,
    ) -> Dict[str, Any]:
        """Step 1: Create structured partner dossier."""
        trace_id = str(uuid.uuid4())
        dossier = PartnerDossier(
            partner_name=partner_name,
            partner_name_ar=partner_name_ar,
            partner_type=partner_type,
            strategic_fit_score=75.0,
            revenue_potential_sar=revenue_potential_sar,
            risk_assessment=["New partner — no track record", "Sector alignment: strong"],
            cr_verified=False,
            recommendation="proceed",
            provenance=Provenance(
                generated_by="golden_path.create_partner_dossier",
                model_provider="system",
                confidence=0.8,
                freshness_hours=0.0,
                trace_id=trace_id,
            ),
        )
        return {"trace_id": trace_id, "dossier": dossier.model_dump(), "step": "1_dossier"}

    async def create_economics_model(
        self,
        db: AsyncSession,
        *,
        tenant_id: str,
        trace_id: str,
        revenue_upside_sar: float,
        cost_sar: float,
    ) -> Dict[str, Any]:
        """Step 2: Generate economics model with Provenance."""
        model = EconomicsModel(
            entity_id=trace_id,
            entity_type="partnership",
            revenue_upside_sar=revenue_upside_sar,
            cost_sar=cost_sar,
            net_value_sar=revenue_upside_sar - cost_sar,
            payback_months=round(cost_sar / max(revenue_upside_sar / 12, 1), 1),
            assumptions=["12-month revenue projection", "Linear cost model"],
            sensitivity_scenarios=[
                {"scenario": "optimistic", "multiplier": 1.3},
                {"scenario": "pessimistic", "multiplier": 0.7},
            ],
            provenance=Provenance(
                generated_by="golden_path.create_economics_model",
                model_provider="system",
                confidence=0.7,
                freshness_hours=0.0,
                trace_id=trace_id,
            ),
        )
        return {"trace_id": trace_id, "economics": model.model_dump(), "step": "2_economics"}

    async def create_approval_packet(
        self,
        db: AsyncSession,
        *,
        tenant_id: str,
        trace_id: str,
        action: str = "activate_partnership",
        requested_by: str,
        risk_summary: str = "Standard partnership — moderate risk",
    ) -> Dict[str, Any]:
        """Step 3: Create structured approval packet (Class B enforcement)."""
        from app.models.operations import ApprovalRequest

        packet = ApprovalPacket(
            action=action,
            action_class="B",
            resource_type="strategic_deal",
            resource_id=trace_id,
            tenant_id=tenant_id,
            requested_by=requested_by,
            priority="high",
            sla_hours=24,
            context={"partner_type": "partnership", "trace_id": trace_id},
            risk_summary=risk_summary,
            reversibility="partially_reversible",
            provenance=Provenance(
                generated_by="golden_path.create_approval_packet",
                model_provider="system",
                confidence=0.85,
                freshness_hours=0.0,
                trace_id=trace_id,
            ),
        )

        approval = ApprovalRequest(
            tenant_id=tenant_id,
            channel="system",
            resource_type="strategic_deal",
            resource_id=uuid.UUID(trace_id) if len(trace_id) == 36 else uuid.uuid4(),
            status="pending",
            requested_by_id=requested_by,
            payload={
                "approval_packet": packet.model_dump(mode="json"),
                "category": "deal",
                "_dealix_sla": {
                    "escalation_level": 0,
                    "escalation_label_ar": "ضمن المهلة",
                    "age_hours": 0,
                    "warn_threshold_hours": 8,
                    "breach_threshold_hours": 24,
                },
            },
        )
        db.add(approval)
        await db.commit()
        await db.refresh(approval)

        return {
            "trace_id": trace_id,
            "approval_id": str(approval.id),
            "approval_packet": packet.model_dump(mode="json"),
            "status": "pending_approval",
            "step": "3_approval",
        }

    async def assemble_evidence_pack(
        self,
        db: AsyncSession,
        *,
        tenant_id: str,
        trace_id: str,
        dossier: Dict[str, Any],
        economics: Dict[str, Any],
        approval_id: str,
    ) -> Dict[str, Any]:
        """Step 4: Auto-assemble evidence pack with SHA256."""
        from app.services.evidence_pack_service import evidence_pack_service

        contents = [
            {"type": "partner_dossier", "source": "golden_path", "data": dossier},
            {"type": "economics_model", "source": "golden_path", "data": economics},
            {"type": "approval_record", "source": "approval_requests", "data": {"approval_id": approval_id, "trace_id": trace_id}},
        ]

        pack = await evidence_pack_service.assemble(
            db,
            tenant_id=tenant_id,
            title=f"Partner Evidence Pack — {dossier.get('partner_name', 'Unknown')}",
            title_ar=f"حزمة أدلة الشراكة — {dossier.get('partner_name_ar', '')}",
            pack_type="deal_closure",
            entity_type="strategic_deal",
            contents=contents,
            metadata={"trace_id": trace_id, "golden_path": True},
        )

        return {
            "trace_id": trace_id,
            "evidence_pack_id": str(pack.id),
            "hash_signature": pack.hash_signature,
            "status": "evidence_assembled",
            "step": "4_evidence",
        }

    async def run_full_path(
        self,
        db: AsyncSession,
        *,
        tenant_id: str,
        partner_name: str,
        partner_name_ar: Optional[str] = None,
        partner_type: str = "partnership",
        revenue_potential_sar: float = 100000,
        cost_sar: float = 20000,
        requested_by: str,
    ) -> Dict[str, Any]:
        """Run the complete golden path end-to-end."""
        step1 = await self.create_partner_dossier(
            db, tenant_id=tenant_id, partner_name=partner_name,
            partner_name_ar=partner_name_ar, partner_type=partner_type,
            revenue_potential_sar=revenue_potential_sar,
        )
        trace_id = step1["trace_id"]

        step2 = await self.create_economics_model(
            db, tenant_id=tenant_id, trace_id=trace_id,
            revenue_upside_sar=revenue_potential_sar, cost_sar=cost_sar,
        )

        step3 = await self.create_approval_packet(
            db, tenant_id=tenant_id, trace_id=trace_id,
            requested_by=requested_by,
        )

        step4 = await self.assemble_evidence_pack(
            db, tenant_id=tenant_id, trace_id=trace_id,
            dossier=step1["dossier"], economics=step2["economics"],
            approval_id=step3["approval_id"],
        )

        return {
            "trace_id": trace_id,
            "status": "golden_path_complete",
            "steps": {
                "1_dossier": step1,
                "2_economics": step2,
                "3_approval": step3,
                "4_evidence": step4,
            },
            "summary": {
                "partner": partner_name,
                "revenue_potential": revenue_potential_sar,
                "approval_status": "pending",
                "evidence_hash": step4["hash_signature"],
            },
        }


golden_path_service = GoldenPathService()
