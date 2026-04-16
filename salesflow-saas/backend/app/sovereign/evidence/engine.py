"""Evidence engine: create items, assemble packs, freshness, board export."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID

from pydantic import BaseModel, Field

from app.sovereign.schemas import BusinessTrack, EvidenceItem, EvidencePack, ProvenanceInfo


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class FreshnessReport(BaseModel):
    is_stale: bool
    oldest_evidence_age_seconds: float
    threshold_seconds: float
    stale_item_ids: list[UUID] = Field(default_factory=list)
    summary_en: str
    summary_ar: str


class BoardExportResult(BaseModel):
    pack_id: UUID
    tenant_id: str
    language: str
    title: str
    title_ar: str
    body_markdown: str
    body_markdown_ar: str


class EvidenceEngine:
    STALE_AFTER_SECONDS: float = 86_400.0

    def __init__(self) -> None:
        self._packs: dict[UUID, EvidencePack] = {}
        self._pack_tenant: dict[UUID, str] = {}
        self._decision_packs: dict[tuple[str, str], UUID] = {}
        self._pack_index: dict[tuple[str, BusinessTrack], list[UUID]] = {}

    def create_evidence_item(
        self,
        tenant_id: str,
        source: str,
        content: str,
        provenance: ProvenanceInfo,
        *,
        title: str | None = None,
        title_ar: str | None = None,
    ) -> EvidenceItem:
        snippet = content[:500]
        return EvidenceItem(
            title=title or source,
            title_ar=title_ar or "دليل",
            source=source,
            content_summary=snippet,
            content_summary_ar=snippet,
            provenance=provenance,
        )

    def assemble_pack(
        self,
        tenant_id: str,
        track: BusinessTrack,
        items: list[EvidenceItem],
        assumptions: list[str],
        policy_notes: list[str],
        alternatives: list[str],
        *,
        assumptions_ar: list[str] | None = None,
        financial_model_version: str | None = None,
    ) -> EvidencePack:
        pack = EvidencePack(
            track=track,
            items=items,
            assumptions=assumptions,
            assumptions_ar=assumptions_ar or assumptions,
            financial_model_version=financial_model_version,
            policy_notes=policy_notes,
            alternatives=alternatives,
        )
        self._packs[pack.pack_id] = pack
        self._pack_tenant[pack.pack_id] = tenant_id
        key = (tenant_id, track)
        self._pack_index.setdefault(key, []).insert(0, pack.pack_id)
        return pack

    def attach_to_decision(self, tenant_id: str, decision_id: str, pack_id: UUID) -> None:
        self._decision_packs[(tenant_id, decision_id)] = pack_id

    def get_pack(self, tenant_id: str, pack_id: UUID) -> EvidencePack:
        if pack_id not in self._packs or self._pack_tenant.get(pack_id) != tenant_id:
            msg = "Evidence pack not found for tenant"
            raise KeyError(msg)
        return self._packs[pack_id]

    def list_packs(
        self,
        tenant_id: str,
        track: BusinessTrack,
        limit: int,
        offset: int,
    ) -> list[EvidencePack]:
        ids = self._pack_index.get((tenant_id, track), [])
        slice_ids = ids[offset : offset + limit]
        return [self._packs[i] for i in slice_ids if i in self._packs]

    def validate_freshness(self, pack: EvidencePack, *, threshold_seconds: float | None = None) -> FreshnessReport:
        threshold = threshold_seconds if threshold_seconds is not None else self.STALE_AFTER_SECONDS
        now = _utc_now()
        stale_ids: list[UUID] = []
        oldest = 0.0
        for item in pack.items:
            age = (now - item.created_at).total_seconds()
            oldest = max(oldest, age)
            prov_age = item.provenance.freshness_seconds
            if age > threshold or prov_age > threshold:
                stale_ids.append(item.item_id)
        is_stale = bool(stale_ids)
        return FreshnessReport(
            is_stale=is_stale,
            oldest_evidence_age_seconds=oldest,
            threshold_seconds=threshold,
            stale_item_ids=stale_ids,
            summary_en="Evidence is within freshness budget." if not is_stale else "One or more evidence items exceed freshness.",
            summary_ar="الأدلة ضمن حدود الحداثة." if not is_stale else "تجاوزت عناصر أدلة حد الحداثة.",
        )

    def export_for_board(self, tenant_id: str, pack_id: UUID, language: str = "ar") -> BoardExportResult:
        pack = self.get_pack(tenant_id, pack_id)
        lines_en = [f"## Evidence pack `{pack.pack_id}`", f"Track: {pack.track.value}"]
        lines_ar = [f"## حزمة أدلة `{pack.pack_id}`", f"المسار: {pack.track.value}"]
        for item in pack.items:
            lines_en.append(f"- **{item.title}** ({item.source}): {item.content_summary}")
            lines_ar.append(f"- **{item.title_ar}** ({item.source}): {item.content_summary_ar}")
        if pack.assumptions:
            lines_en.append("### Assumptions")
            lines_ar.append("### الافتراضات")
            for a in pack.assumptions:
                lines_en.append(f"- {a}")
            for a in pack.assumptions_ar:
                lines_ar.append(f"- {a}")
        if pack.policy_notes:
            lines_en.append("### Policy")
            lines_ar.append("### السياسات")
            for p in pack.policy_notes:
                lines_en.append(f"- {p}")
                lines_ar.append(f"- {p}")
        body_en = "\n".join(lines_en)
        body_ar = "\n".join(lines_ar)
        if language == "ar":
            return BoardExportResult(
                pack_id=pack.pack_id,
                tenant_id=tenant_id,
                language=language,
                title="ملخص مجلس الإدارة",
                title_ar="ملخص مجلس الإدارة",
                body_markdown=body_ar,
                body_markdown_ar=body_ar,
            )
        return BoardExportResult(
            pack_id=pack.pack_id,
            tenant_id=tenant_id,
            language=language,
            title="Board evidence summary",
            title_ar="ملخص مجلس الإدارة",
            body_markdown=body_en,
            body_markdown_ar=body_ar,
        )
