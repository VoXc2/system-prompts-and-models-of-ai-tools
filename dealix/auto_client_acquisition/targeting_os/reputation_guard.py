"""Reputation guard — يحمي القنوات من الحظر."""

from __future__ import annotations

from typing import Any


def risk_thresholds() -> dict[str, dict[str, float]]:
    """The thresholds where a channel needs throttling/pause."""
    return {
        "email": {
            "bounce_rate_warn": 0.02, "bounce_rate_pause": 0.05,
            "complaint_rate_warn": 0.001, "complaint_rate_pause": 0.003,
            "opt_out_rate_warn": 0.05, "opt_out_rate_pause": 0.10,
            "min_reply_rate": 0.02,
        },
        "whatsapp": {
            "block_rate_warn": 0.01, "block_rate_pause": 0.03,
            "report_rate_warn": 0.005, "report_rate_pause": 0.02,
            "opt_out_rate_warn": 0.05, "opt_out_rate_pause": 0.10,
            "min_reply_rate": 0.10,
        },
        "linkedin": {
            "connection_decline_warn": 0.3, "connection_decline_pause": 0.5,
        },
    }


def calculate_channel_reputation(
    metrics: dict[str, float],
    *,
    channel: str = "email",
) -> dict[str, Any]:
    """Compute a 0..100 reputation score for a channel based on metrics."""
    th = risk_thresholds().get(channel, {})
    score = 100
    reasons_ar: list[str] = []

    if channel == "email":
        bounce = float(metrics.get("bounce_rate", 0))
        complaint = float(metrics.get("complaint_rate", 0))
        opt_out = float(metrics.get("opt_out_rate", 0))
        reply = float(metrics.get("reply_rate", 0.05))

        if bounce >= th["bounce_rate_pause"]:
            score -= 40; reasons_ar.append("معدل الـ bounce تجاوز الحد الحرج.")
        elif bounce >= th["bounce_rate_warn"]:
            score -= 15; reasons_ar.append("ارتفاع في الـ bounce — راقب.")

        if complaint >= th["complaint_rate_pause"]:
            score -= 50; reasons_ar.append("شكاوى spam مرتفعة جداً.")
        elif complaint >= th["complaint_rate_warn"]:
            score -= 20; reasons_ar.append("بداية شكاوى spam.")

        if opt_out >= th["opt_out_rate_pause"]:
            score -= 25; reasons_ar.append("نسبة opt-out مرتفعة جداً.")

        if reply < th["min_reply_rate"]:
            score -= 10; reasons_ar.append("معدل الرد منخفض — راجع الجودة.")

    elif channel == "whatsapp":
        block = float(metrics.get("block_rate", 0))
        report = float(metrics.get("report_rate", 0))
        opt_out = float(metrics.get("opt_out_rate", 0))

        if block >= th["block_rate_pause"]:
            score -= 60; reasons_ar.append("نسبة الحظر مرتفعة جداً — أوقف.")
        elif block >= th["block_rate_warn"]:
            score -= 25; reasons_ar.append("بداية حظر — راجع المحتوى.")

        if report >= th["report_rate_pause"]:
            score -= 50; reasons_ar.append("بلاغات spam على واتساب.")

        if opt_out >= th["opt_out_rate_pause"]:
            score -= 30; reasons_ar.append("opt-out واتساب مرتفع.")

    score = max(0, min(100, score))
    return {
        "channel": channel,
        "score": score,
        "reasons_ar": reasons_ar,
        "verdict": ("healthy" if score >= 70
                    else "watch" if score >= 40
                    else "pause"),
    }


def should_pause_channel(
    metrics: dict[str, float], *, channel: str = "email",
) -> dict[str, Any]:
    """Boolean wrapper: should we pause this channel right now?"""
    rep = calculate_channel_reputation(metrics, channel=channel)
    return {
        "should_pause": rep["verdict"] == "pause",
        "reputation_score": rep["score"],
        "reasons_ar": rep["reasons_ar"],
    }


def recommend_recovery_action(
    metrics: dict[str, float], *, channel: str = "email",
) -> dict[str, Any]:
    """Recommend recovery actions based on reputation problems."""
    rep = calculate_channel_reputation(metrics, channel=channel)
    actions: list[str] = []
    if rep["verdict"] == "pause":
        actions = [
            "أوقف إرسال جميع الحملات الجديدة على هذه القناة.",
            "ابدأ فترة تبريد لمدة 14 يوماً على الأقل.",
            "افحص قائمة الـ contacts وحدّث opt-in.",
            "نظّف عناوين الـ bounce وأعد التحقق.",
        ]
    elif rep["verdict"] == "watch":
        actions = [
            "خفّض الحجم اليومي بنسبة 50%.",
            "ركّز على المصادر الآمنة فقط (CRM/inbound).",
            "راجع الرسائل لتقليل العبارات المخاطرة.",
        ]
    else:
        actions = ["استمر — راقب أسبوعياً."]
    return {
        "channel": channel,
        "verdict": rep["verdict"],
        "actions_ar": actions,
        "score": rep["score"],
    }


def summarize_reputation_ar(metrics: dict[str, float], *, channel: str = "email") -> str:
    """One-line Arabic summary of channel health."""
    rep = calculate_channel_reputation(metrics, channel=channel)
    return (
        f"قناة {channel}: score {rep['score']} ({rep['verdict']}). "
        + (rep["reasons_ar"][0] if rep["reasons_ar"] else "حالة صحية.")
    )
