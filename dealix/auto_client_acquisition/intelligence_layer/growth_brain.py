"""Growth Brain — per-customer context + preferences + priorities."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class GrowthBrain:
    """The customer's growth context as a single object."""

    customer_id: str
    company_context: dict[str, Any]
    channels_connected: tuple[str, ...]
    target_segments: tuple[str, ...]
    approved_actions: tuple[str, ...]
    blocked_actions: tuple[str, ...]
    growth_priorities: tuple[str, ...]
    risk_tolerance: str = "medium"           # low / medium / high
    preferred_tone: str = "warm"             # formal / warm / direct
    accept_rate_30d: float = 0.0
    avg_response_minutes: int = 0
    learning_signal_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "customer_id": self.customer_id,
            "company_context": self.company_context,
            "channels_connected": list(self.channels_connected),
            "target_segments": list(self.target_segments),
            "approved_actions": list(self.approved_actions),
            "blocked_actions": list(self.blocked_actions),
            "growth_priorities": list(self.growth_priorities),
            "risk_tolerance": self.risk_tolerance,
            "preferred_tone": self.preferred_tone,
            "accept_rate_30d": self.accept_rate_30d,
            "avg_response_minutes": self.avg_response_minutes,
            "learning_signal_count": self.learning_signal_count,
        }

    def is_ready_for_autopilot(self) -> bool:
        """≥30 learned signals + ≥40% accept rate + non-empty channels."""
        return (
            self.learning_signal_count >= 30
            and self.accept_rate_30d >= 0.40
            and len(self.channels_connected) > 0
        )


def build_growth_brain(payload: dict[str, Any] | None = None) -> GrowthBrain:
    """Build a brain from a customer payload — sane Saudi-B2B defaults."""
    p = payload or {}
    return GrowthBrain(
        customer_id=str(p.get("customer_id") or "demo"),
        company_context={
            "company_name": p.get("company_name", "Demo Saudi B2B Co."),
            "sector": p.get("sector", "real_estate"),
            "city": p.get("city", "الرياض"),
            "offer_one_liner": p.get("offer_one_liner", "تشغيل نمو B2B سعودي"),
            "ideal_customer": p.get("ideal_customer", "شركات SMB سعودية"),
            "average_deal_size_sar": float(p.get("average_deal_size_sar", 25_000)),
        },
        channels_connected=tuple(p.get("channels_connected", ("whatsapp",))),
        target_segments=tuple(p.get("target_segments", ("inbound_lead", "existing_customer"))),
        approved_actions=tuple(p.get("approved_actions", (
            "create_draft", "send_with_approval", "ingest_lead",
        ))),
        blocked_actions=tuple(p.get("blocked_actions", (
            "cold_send_without_consent", "charge_card_without_user_action",
        ))),
        growth_priorities=tuple(p.get("growth_priorities", (
            "fill_pipeline", "improve_response_time", "build_partner_channel",
        ))),
        risk_tolerance=p.get("risk_tolerance", "medium"),
        preferred_tone=p.get("preferred_tone", "warm"),
        accept_rate_30d=float(p.get("accept_rate_30d", 0.0)),
        avg_response_minutes=int(p.get("avg_response_minutes", 0)),
        learning_signal_count=int(p.get("learning_signal_count", 0)),
    )
