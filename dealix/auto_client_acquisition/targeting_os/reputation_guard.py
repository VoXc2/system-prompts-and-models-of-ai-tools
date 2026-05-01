"""Channel reputation — pause suggestions when metrics look bad."""

from __future__ import annotations

from typing import Any


def risk_thresholds() -> dict[str, float]:
    return {
        "bounce_rate_max": 0.08,
        "opt_out_rate_max": 0.02,
        "complaint_rate_max": 0.001,
        "min_reply_rate": 0.05,
    }


def calculate_channel_reputation(metrics: dict[str, Any]) -> dict[str, Any]:
    bounce = float(metrics.get("bounce_rate") or 0)
    opt_out = float(metrics.get("opt_out_rate") or 0)
    complaint = float(metrics.get("complaint_rate") or 0)
    reply = float(metrics.get("reply_rate") or 0)
    th = risk_thresholds()
    score = 100.0
    if bounce > th["bounce_rate_max"]:
        score -= 30
    if opt_out > th["opt_out_rate_max"]:
        score -= 25
    if complaint > th["complaint_rate_max"]:
        score -= 40
    if reply < th["min_reply_rate"]:
        score -= 15
    return {"reputation_score": max(0, min(100, int(score))), "raw": metrics, "demo": True}


def should_pause_channel(metrics: dict[str, Any]) -> bool:
    rep = calculate_channel_reputation(metrics)
    return rep["reputation_score"] < 40


def recommend_recovery_action(metrics: dict[str, Any]) -> dict[str, Any]:
    if should_pause_channel(metrics):
        return {
            "action_ar": "أوقف الإرسال، راجع القوائم والمصادر، قلّل الحجم، أعد تفعيل القناة بعد تحسين المحتوى.",
            "demo": True,
        }
    return {"action_ar": "استمر مع مراقبة يومية للردود وopt-out.", "demo": True}


def summarize_reputation_ar(metrics: dict[str, Any]) -> str:
    rep = calculate_channel_reputation(metrics)
    return f"درجة السمعة للقناة: {rep['reputation_score']}/100."
