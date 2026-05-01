"""Growth memory — long-term cross-customer learning store (anonymized aggregates)."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class GrowthMemory:
    """Cross-customer aggregates Dealix learns from (anonymized + bucketed)."""
    sector_message_winrate: dict[str, dict[str, float]] = field(default_factory=dict)
    sector_channel_winrate: dict[str, dict[str, float]] = field(default_factory=dict)
    common_objections: dict[str, int] = field(default_factory=dict)
    blocked_action_reasons: dict[str, int] = field(default_factory=dict)
    successful_playbooks: list[dict[str, Any]] = field(default_factory=list)

    def record_message_outcome(
        self, *, sector: str, message_id: str, won: bool,
    ) -> None:
        bucket = self.sector_message_winrate.setdefault(sector, {})
        # rolling success/fail count stored as floats in [0..1]
        prev = bucket.get(message_id, 0.5)
        bucket[message_id] = round((prev + (1.0 if won else 0.0)) / 2.0, 3)

    def record_channel_outcome(
        self, *, sector: str, channel: str, won: bool,
    ) -> None:
        bucket = self.sector_channel_winrate.setdefault(sector, {})
        prev = bucket.get(channel, 0.5)
        bucket[channel] = round((prev + (1.0 if won else 0.0)) / 2.0, 3)

    def record_objection(self, label: str) -> None:
        self.common_objections[label] = self.common_objections.get(label, 0) + 1

    def record_blocked_reason(self, reason: str) -> None:
        self.blocked_action_reasons[reason] = (
            self.blocked_action_reasons.get(reason, 0) + 1
        )

    def append_successful_playbook(
        self, *, sector: str, name: str, win_rate: float,
    ) -> None:
        self.successful_playbooks.append({
            "ts": time.time(),
            "sector": sector,
            "name": name,
            "win_rate": float(win_rate),
        })

    def best_message_for_sector(self, sector: str) -> dict[str, Any]:
        bucket = self.sector_message_winrate.get(sector, {})
        if not bucket:
            return {"sector": sector, "best_message_id": None, "win_rate": 0.0}
        best = max(bucket.items(), key=lambda x: x[1])
        return {"sector": sector, "best_message_id": best[0], "win_rate": best[1]}

    def best_channel_for_sector(self, sector: str) -> dict[str, Any]:
        bucket = self.sector_channel_winrate.get(sector, {})
        if not bucket:
            return {"sector": sector, "best_channel": None, "win_rate": 0.0}
        best = max(bucket.items(), key=lambda x: x[1])
        return {"sector": sector, "best_channel": best[0], "win_rate": best[1]}

    def summary(self) -> dict[str, Any]:
        return {
            "sector_message_winrate": {
                k: dict(v) for k, v in self.sector_message_winrate.items()
            },
            "sector_channel_winrate": {
                k: dict(v) for k, v in self.sector_channel_winrate.items()
            },
            "top_objections": sorted(
                self.common_objections.items(),
                key=lambda x: -x[1],
            )[:5],
            "top_blocked_reasons": sorted(
                self.blocked_action_reasons.items(),
                key=lambda x: -x[1],
            )[:5],
            "successful_playbooks": self.successful_playbooks[-5:],
        }


def build_growth_memory_demo() -> dict[str, Any]:
    """Build a demo memory with sample aggregates."""
    g = GrowthMemory()
    g.record_message_outcome(sector="training", message_id="msg_warm_intro", won=True)
    g.record_message_outcome(sector="training", message_id="msg_warm_intro", won=True)
    g.record_message_outcome(sector="training", message_id="msg_cold_pitch", won=False)
    g.record_channel_outcome(sector="training", channel="email", won=True)
    g.record_channel_outcome(sector="training", channel="email", won=True)
    g.record_channel_outcome(sector="training", channel="linkedin_lead_form", won=True)
    g.record_objection("price")
    g.record_objection("timing")
    g.record_objection("price")
    g.record_blocked_reason("cold_whatsapp")
    g.record_blocked_reason("cold_whatsapp")
    g.record_blocked_reason("payload_contains_secret")
    g.append_successful_playbook(
        sector="training", name="warm_intro_with_proof", win_rate=0.42,
    )
    return {
        "summary": g.summary(),
        "best_message_training": g.best_message_for_sector("training"),
        "best_channel_training": g.best_channel_for_sector("training"),
    }
