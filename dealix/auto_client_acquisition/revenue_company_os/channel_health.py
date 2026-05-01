"""Channel health — cross-channel reputation snapshot for the customer."""

from __future__ import annotations

from typing import Any

from auto_client_acquisition.targeting_os.reputation_guard import (
    calculate_channel_reputation,
)


def build_channel_health_snapshot(
    *,
    metrics_per_channel: dict[str, dict[str, float]] | None = None,
) -> dict[str, Any]:
    """
    Build a single snapshot of channel health across channels.

    Input:
        metrics_per_channel = {
            "email": {"bounce_rate": 0.005, "complaint_rate": 0.0001, ...},
            "whatsapp": {"block_rate": 0.01, "report_rate": 0.001, ...},
            ...
        }
    """
    metrics_per_channel = metrics_per_channel or {
        "email": {"bounce_rate": 0.005, "complaint_rate": 0.0001,
                  "opt_out_rate": 0.01, "reply_rate": 0.04},
        "whatsapp": {"block_rate": 0.005, "report_rate": 0.001,
                     "opt_out_rate": 0.02, "reply_rate": 0.10},
        "linkedin": {"connection_decline": 0.25},
    }

    snapshot: dict[str, Any] = {}
    for channel, metrics in metrics_per_channel.items():
        snapshot[channel] = calculate_channel_reputation(
            metrics, channel=channel,
        )

    overall_score = (
        sum(int(s.get("score", 0) or 0) for s in snapshot.values())
        / max(1, len(snapshot))
    )
    risky = [c for c, s in snapshot.items() if s.get("verdict") == "pause"]

    return {
        "channels": snapshot,
        "overall_score": round(overall_score, 1),
        "channels_at_risk": risky,
        "summary_ar": [
            f"الدرجة الكلية: {round(overall_score, 1)} / 100",
            (
                f"قنوات في حالة pause: {', '.join(risky)}."
                if risky else
                "جميع القنوات صحية الآن."
            ),
        ],
    }
