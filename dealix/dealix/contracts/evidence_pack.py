"""
Evidence Pack — the bundled artifact attached to every Tier-A/B decision.

Per the blueprint, every high-stakes decision ships with a pack containing:
- the decision itself (by reference)
- all sources consulted
- all tool calls made (intended vs actual)
- prompt templates used
- model + version used
- data freshness timestamps
- optional reviewer (if HITL)
- bilingual memo (AR + EN)
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


def _utcnow_iso() -> str:
    return datetime.now(UTC).isoformat()


def _new_pack_id() -> str:
    return f"pack_{uuid.uuid4().hex[:16]}"


class EvidenceSource(BaseModel):
    """An external or internal source consulted during the decision."""

    model_config = ConfigDict(extra="forbid")

    source: str
    uri: str | None = None
    excerpt: str
    content_hash: str | None = None
    retrieved_at: str = Field(default_factory=_utcnow_iso)
    freshness_window_hours: int = 24


class ToolCallRecord(BaseModel):
    """Record of a tool invocation during the decision process.

    Critically, we distinguish `intended_action` (what the agent said it would do)
    from `actual_action` (what actually happened) — this drives the tool verification
    ledger in the Trust Plane.
    """

    model_config = ConfigDict(extra="forbid")

    tool_name: str
    intended_action: str
    actual_action: str
    inputs: dict[str, Any] = Field(default_factory=dict)
    outputs: dict[str, Any] = Field(default_factory=dict)
    side_effects: list[str] = Field(default_factory=list)
    verification_status: str = "pending"  # pending | verified | contradicted | blocked
    contradiction_flag: bool = False
    invoked_at: str = Field(default_factory=_utcnow_iso)


class PromptRecord(BaseModel):
    """Record of a prompt template used during the decision."""

    model_config = ConfigDict(extra="forbid")

    template_name: str
    template_version: str = "1.0"
    rendered_length: int = 0
    system_prompt_present: bool = False


class BilingualMemo(BaseModel):
    """The board-grade memo shipped with the pack."""

    model_config = ConfigDict(extra="forbid")

    title_ar: str
    title_en: str
    body_ar: str
    body_en: str
    executive_summary_ar: str
    executive_summary_en: str


class EvidencePack(BaseModel):
    """The full evidence pack."""

    model_config = ConfigDict(extra="forbid")

    schema_version: str = "1.0"
    pack_id: str = Field(default_factory=_new_pack_id)
    decision_id: str
    tenant_id: str = "default"
    entity_id: str

    agent_name: str
    model: str | None = None
    model_version: str | None = None

    sources: list[EvidenceSource] = Field(default_factory=list)
    tool_calls: list[ToolCallRecord] = Field(default_factory=list)
    prompts: list[PromptRecord] = Field(default_factory=list)

    data_freshness_window_hours: int = 24
    reviewer_id: str | None = None
    reviewed_at: str | None = None

    memo: BilingualMemo | None = None
    trace_id: str | None = None
    created_at: str = Field(default_factory=_utcnow_iso)

    @property
    def is_complete(self) -> bool:
        """A pack is 'complete' when it has sources + model info + at least a draft memo."""
        return len(self.sources) > 0 and self.model is not None and self.memo is not None

    def to_json(self) -> str:
        return self.model_dump_json(indent=2)
