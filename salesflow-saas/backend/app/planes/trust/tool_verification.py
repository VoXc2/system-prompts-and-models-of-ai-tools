"""
Trust Plane — Tool Verification Ledger.

Maintains a registry of verified tools and their capabilities so the
orchestrator only invokes tools that have passed integrity checks.

سجل التحقق من الأدوات — التأكد من سلامة وصلاحية كل أداة قبل استخدامها
"""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ToolVerificationEntry(BaseModel):
    """Record representing a verified tool in the ledger."""
    model_config = ConfigDict(from_attributes=True)

    tool_id: str
    tool_name: str
    version: str
    verified_at: datetime
    verified_by: str
    checksum: str
    status: str = "verified"
    capabilities: list[str] = Field(default_factory=list)
    restrictions: list[str] = Field(default_factory=list)


class ToolVerificationLedger:
    """In-memory ledger that tracks tool verification state."""

    def __init__(self) -> None:
        self._entries: dict[str, ToolVerificationEntry] = {}

    def register(self, entry: ToolVerificationEntry) -> None:
        """Add or update a tool entry in the ledger."""
        self._entries[entry.tool_id] = entry

    def verify(self, tool_id: str) -> ToolVerificationEntry | None:
        """Return the entry for *tool_id* if it exists and is verified."""
        entry = self._entries.get(tool_id)
        if entry and entry.status == "verified":
            return entry
        return None

    def is_allowed(self, tool_id: str, capability: str) -> bool:
        """Check whether *tool_id* is verified and has *capability*."""
        entry = self.verify(tool_id)
        if entry is None:
            return False
        if capability in entry.restrictions:
            return False
        return capability in entry.capabilities

    def list_all(self) -> list[ToolVerificationEntry]:
        """Return all registered entries."""
        return list(self._entries.values())
