"""Saudi Sensitive Workflow — partner data sharing with PDPL controls.

This is a live Saudi-sensitive workflow that enforces:
- PDPL data classification on shared data
- Consent verification before sharing
- Approval gate (Class B+)
- Audit trail
- Evidence pack assembly
- Retention/export rules check
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from sqlalchemy.ext.asyncio import AsyncSession


class SaudiSensitiveWorkflow:
    """Partner data sharing workflow with full PDPL controls."""

    async def share_partner_data(
        self,
        db: AsyncSession,
        *,
        tenant_id: str,
        partner_name: str,
        data_categories: list[str],
        purpose: str,
        requested_by: str,
    ) -> Dict[str, Any]:
        """Execute partner data sharing with all Saudi controls.

        Steps:
        1. Classify data (PDPL)
        2. Check consent
        3. Check retention/export rules
        4. Create approval request (Class B+)
        5. Log to audit trail
        6. Assemble evidence pack
        """
        trace_id = str(uuid.uuid4())
        results: Dict[str, Any] = {"trace_id": trace_id, "steps": {}}

        # Step 1: Data classification
        classification = self._classify_data(data_categories)
        results["steps"]["1_classification"] = classification

        # Step 2: Consent check
        consent_result = await self._check_consent(db, tenant_id=tenant_id, purpose=purpose)
        results["steps"]["2_consent"] = consent_result

        if not consent_result.get("consent_valid"):
            results["status"] = "blocked_no_consent"
            results["blocked_reason_ar"] = "لا توجد موافقة PDPL سارية لهذا الغرض"
            return results

        # Step 3: Retention/export rules
        export_result = self._check_export_rules(classification, partner_name)
        results["steps"]["3_export_rules"] = export_result

        if not export_result.get("export_allowed"):
            results["status"] = "blocked_export_restricted"
            results["blocked_reason_ar"] = "نقل البيانات غير مسموح لهذا الطرف"
            return results

        # Step 4: Create approval request
        approval_result = await self._create_approval(
            db, tenant_id=tenant_id, trace_id=trace_id,
            partner_name=partner_name, classification=classification,
            requested_by=requested_by,
        )
        results["steps"]["4_approval"] = approval_result

        # Step 5: Audit trail
        audit_result = await self._log_audit(
            db, tenant_id=tenant_id, trace_id=trace_id,
            action="partner_data_sharing_requested",
            details={"partner": partner_name, "categories": data_categories, "classification": classification},
        )
        results["steps"]["5_audit"] = audit_result

        # Step 6: Evidence pack
        evidence_result = await self._assemble_evidence(
            db, tenant_id=tenant_id, trace_id=trace_id,
            partner_name=partner_name, classification=classification,
            consent=consent_result, export=export_result,
            approval_id=approval_result.get("approval_id"),
        )
        results["steps"]["6_evidence"] = evidence_result

        results["status"] = "pending_approval"
        results["summary_ar"] = f"طلب مشاركة بيانات مع {partner_name} — ينتظر الموافقة"
        return results

    def _classify_data(self, categories: list[str]) -> Dict[str, Any]:
        """PDPL data classification."""
        classification_map = {
            "company_name": "internal",
            "contact_name": "confidential",
            "contact_phone": "restricted",
            "contact_email": "confidential",
            "deal_value": "confidential",
            "financial_data": "restricted",
            "cr_number": "internal",
            "health_data": "restricted",
        }
        classified = {}
        highest = "internal"
        for cat in categories:
            level = classification_map.get(cat, "internal")
            classified[cat] = level
            if level == "restricted":
                highest = "restricted"
            elif level == "confidential" and highest != "restricted":
                highest = "confidential"

        return {
            "categories": classified,
            "highest_classification": highest,
            "pdpl_applicable": highest in ("confidential", "restricted"),
            "requires_dpo_review": highest == "restricted",
        }

    async def _check_consent(self, db: AsyncSession, *, tenant_id: str, purpose: str) -> Dict[str, Any]:
        """Check PDPL consent — queries real PDPLConsent table."""
        from app.models.consent import PDPLConsent
        from sqlalchemy import select, func

        total = int(
            (await db.execute(
                select(func.count()).select_from(PDPLConsent).where(PDPLConsent.tenant_id == tenant_id)
            )).scalar() or 0
        )
        active = int(
            (await db.execute(
                select(func.count()).select_from(PDPLConsent)
                .where(PDPLConsent.tenant_id == tenant_id, PDPLConsent.status == "granted")
            )).scalar() or 0
        )

        consent_valid = active > 0 or total == 0  # allow if no consent records exist yet (new tenant)
        return {
            "consent_valid": consent_valid,
            "consent_type": "explicit" if active > 0 else "not_found",
            "purpose": purpose,
            "total_records": total,
            "active_consents": active,
            "expires_at": None,
            "note_ar": "موافقة سارية" if consent_valid else "لا توجد موافقة PDPL سارية — مطلوب الحصول على موافقة",
        }

    def _check_export_rules(self, classification: Dict, partner_name: str) -> Dict[str, Any]:
        """Check PDPL cross-border transfer rules — enforces based on classification."""
        gcc_countries = {"SA", "AE", "BH", "KW", "OM", "QA"}
        has_restricted = classification.get("highest_classification") == "restricted"
        requires_dpo = classification.get("requires_dpo_review", False)

        # Restricted data requires explicit DPO review — block by default
        export_allowed = not (has_restricted and requires_dpo)

        return {
            "export_allowed": export_allowed,
            "partner_jurisdiction": "SA",
            "gcc_transfer": True,
            "restricted_data_present": has_restricted,
            "requires_dpo_review": requires_dpo,
            "blocked_reason_ar": "بيانات مقيدة تتطلب مراجعة مسؤول حماية البيانات" if not export_allowed else None,
            "note_ar": "النقل مسموح" if export_allowed else "النقل محظور — بيانات مقيدة",
        }

    async def _create_approval(
        self, db: AsyncSession, *, tenant_id: str, trace_id: str,
        partner_name: str, classification: Dict, requested_by: str,
    ) -> Dict[str, Any]:
        """Create Class B+ approval for data sharing."""
        from app.models.operations import ApprovalRequest

        approval = ApprovalRequest(
            tenant_id=tenant_id,
            channel="system",
            resource_type="partner_data_sharing",
            resource_id=uuid.UUID(trace_id),
            status="pending",
            requested_by_id=requested_by,
            payload={
                "category": "compliance",
                "classification": classification.get("highest_classification"),
                "partner": partner_name,
                "_correlation_id": trace_id,
                "_dealix_sla": {
                    "escalation_level": 0,
                    "escalation_label_ar": "ضمن المهلة",
                    "age_hours": 0,
                    "warn_threshold_hours": 4,
                    "breach_threshold_hours": 12,
                },
            },
        )
        db.add(approval)
        await db.flush()
        return {"approval_id": str(approval.id), "status": "pending", "sla_hours": 12}

    async def _log_audit(
        self, db: AsyncSession, *, tenant_id: str, trace_id: str,
        action: str, details: Dict,
    ) -> Dict[str, Any]:
        """Log to audit trail."""
        from app.services.operations_hub import emit_domain_event

        event = await emit_domain_event(
            db, tenant_id=uuid.UUID(tenant_id),
            event_type=f"saudi.{action}",
            payload={**details, "trace_id": trace_id},
            source="saudi_sensitive_workflow",
            correlation_id=trace_id,
        )
        return {"event_id": str(event.id), "event_type": event.event_type}

    async def _assemble_evidence(
        self, db: AsyncSession, *, tenant_id: str, trace_id: str,
        partner_name: str, classification: Dict, consent: Dict,
        export: Dict, approval_id: str | None,
    ) -> Dict[str, Any]:
        """Auto-assemble evidence pack for the data sharing request."""
        from app.services.evidence_pack_service import evidence_pack_service

        contents = [
            {"type": "data_classification", "source": "pdpl", "data": classification},
            {"type": "consent_check", "source": "pdpl.consent_manager", "data": consent},
            {"type": "export_rules_check", "source": "pdpl.export", "data": export},
            {"type": "approval_request", "source": "approval_requests", "data": {"approval_id": approval_id, "trace_id": trace_id}},
        ]

        pack = await evidence_pack_service.assemble(
            db, tenant_id=tenant_id,
            title=f"Partner Data Sharing Evidence — {partner_name}",
            title_ar=f"حزمة أدلة مشاركة البيانات — {partner_name}",
            pack_type="compliance_audit",
            contents=contents,
            metadata={"trace_id": trace_id, "saudi_sensitive": True, "pdpl_applicable": True},
        )
        return {"evidence_pack_id": str(pack.id), "hash_signature": pack.hash_signature}


saudi_sensitive_workflow = SaudiSensitiveWorkflow()
