"""
Trust Plane — Evidence Pack assembly.

Collects and bundles evidence artefacts (documents, data snapshots, approvals)
into an immutable pack that accompanies every governed decision.

حزمة الأدلة — تجميع الوثائق والبيانات لكل قرار محوكم
"""
from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


class EvidenceItem(BaseModel):
    """Single piece of evidence attached to a decision."""
    model_config = ConfigDict(from_attributes=True)

    type: str
    source: str
    content: dict
    collected_at: datetime
    verified: bool = False


class EvidencePack(BaseModel):
    """Immutable bundle of evidence items for a governed decision."""
    model_config = ConfigDict(from_attributes=True)

    pack_id: str
    decision_ref: str
    items: list[EvidenceItem] = Field(default_factory=list)
    assembled_at: datetime
    assembled_by: str
    approval_class: str
    summary_ar: str = ""
    summary_en: str = ""


def assemble_evidence_pack(
    decision_ref: str,
    items: list[dict],
    assembled_by: str,
    approval_class: str,
) -> EvidencePack:
    """Create an :class:`EvidencePack` from raw item dicts.

    Each dict in *items* must match the :class:`EvidenceItem` schema.
    A unique ``pack_id`` is generated automatically.
    """
    evidence_items = [EvidenceItem(**item) for item in items]
    return EvidencePack(
        pack_id=str(uuid4()),
        decision_ref=decision_ref,
        items=evidence_items,
        assembled_at=datetime.now(timezone.utc),
        assembled_by=assembled_by,
        approval_class=approval_class,
    )
