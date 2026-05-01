"""
Event Envelope Contract — CloudEvents 1.0 with Dealix extensions.

Every event in the platform carries this envelope for:
- Correlation across planes (decision → execution → audit)
- Classification (approval / reversibility / sensitivity)
- Traceability (trace_id, span_id)
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from dealix.classifications import ApprovalClass, ReversibilityClass, SensitivityClass

ActorType = Literal["system", "agent", "human", "workflow"]


def _utcnow_iso() -> str:
    return datetime.now(UTC).isoformat()


def _new_event_id() -> str:
    return f"evt_{uuid.uuid4().hex[:16]}"


class EventEnvelope(BaseModel):
    """CloudEvents 1.0-compatible envelope with Dealix extensions.

    CloudEvents required attributes (`id`, `source`, `specversion`, `type`)
    are kept as their CloudEvents names in the serialized JSON.
    """

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    # ── CloudEvents core ────────────────────────────────────────
    specversion: Literal["1.0"] = "1.0"
    id: str = Field(default_factory=_new_event_id, alias="id")
    source: str = Field(..., description="e.g. 'dealix/phase8/intake'")
    type: str = Field(..., description="e.g. 'dealix.lead.intaken'")
    datacontenttype: str = "application/json"
    dataschema: str | None = Field(None, description="URI of the JSON Schema for `data`")
    time: str = Field(default_factory=_utcnow_iso)
    subject: str | None = Field(None, description="Subject within the source (e.g. lead_id)")

    # ── Dealix extensions ───────────────────────────────────────
    schema_version: str = Field(default="1.0")
    tenant_id: str = "default"
    entity_id: str | None = None

    correlation_id: str | None = None
    causation_id: str | None = None

    actor_type: ActorType = "system"
    actor_id: str | None = None

    approval_class: ApprovalClass = ApprovalClass.A0
    reversibility_class: ReversibilityClass = ReversibilityClass.R0
    sensitivity_class: SensitivityClass = SensitivityClass.S1

    trace_id: str | None = None
    span_id: str | None = None

    # ── Payload ─────────────────────────────────────────────────
    data: dict[str, Any] = Field(default_factory=dict)

    def to_cloudevents_json(self) -> str:
        """Emit CloudEvents-compliant JSON (preserves `id`, `source`, etc.)."""
        return self.model_dump_json(by_alias=True)
