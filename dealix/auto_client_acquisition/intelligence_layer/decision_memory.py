"""Decision Memory — learn the operator's preferences from Accept/Skip/Edit."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Any


VALID_DECISIONS: tuple[str, ...] = ("accept", "skip", "edit", "block")


@dataclass
class DecisionMemory:
    """Per-customer Accept/Skip/Edit history and aggregates."""

    customer_id: str
    raw_decisions: list[dict[str, Any]] = field(default_factory=list)

    def append(
        self,
        *,
        decision: str,
        action_type: str,
        channel: str,
        sector: str | None = None,
        tone: str | None = None,
        objection_id: str | None = None,
    ) -> None:
        if decision not in VALID_DECISIONS:
            raise ValueError(f"unknown decision: {decision}")
        self.raw_decisions.append({
            "decision": decision,
            "action_type": action_type,
            "channel": channel,
            "sector": sector,
            "tone": tone,
            "objection_id": objection_id,
        })

    def preferences(self) -> dict[str, Any]:
        if not self.raw_decisions:
            return {
                "samples": 0,
                "preferred_channels": [],
                "preferred_tones": [],
                "preferred_sectors": [],
                "rejected_action_types": [],
                "accept_rate": 0.0,
            }
        ch_counter: Counter[str] = Counter()
        tone_counter: Counter[str] = Counter()
        sector_counter: Counter[str] = Counter()
        rejected: Counter[str] = Counter()
        accepts = 0
        for d in self.raw_decisions:
            if d["decision"] == "accept":
                accepts += 1
                ch_counter[d.get("channel", "")] += 1
                if d.get("tone"):
                    tone_counter[d["tone"]] += 1
                if d.get("sector"):
                    sector_counter[d["sector"]] += 1
            elif d["decision"] in ("skip", "block"):
                rejected[d.get("action_type", "")] += 1
        return {
            "samples": len(self.raw_decisions),
            "preferred_channels": [c for c, _ in ch_counter.most_common(3)],
            "preferred_tones": [t for t, _ in tone_counter.most_common(2)],
            "preferred_sectors": [s for s, _ in sector_counter.most_common(3)],
            "rejected_action_types": [a for a, _ in rejected.most_common(3) if a],
            "accept_rate": round(accepts / len(self.raw_decisions), 4),
        }


def learn_from_decision(
    *,
    memory: DecisionMemory,
    decision: str,
    action_type: str,
    channel: str,
    sector: str | None = None,
    tone: str | None = None,
    objection_id: str | None = None,
) -> dict[str, Any]:
    """Record a decision + return updated preferences."""
    memory.append(
        decision=decision, action_type=action_type, channel=channel,
        sector=sector, tone=tone, objection_id=objection_id,
    )
    return {
        "customer_id": memory.customer_id,
        "added": True,
        "preferences": memory.preferences(),
    }
