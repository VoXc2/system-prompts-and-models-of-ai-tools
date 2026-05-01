"""Per-service success scorecard — deterministic from metrics dict."""

from __future__ import annotations

from typing import Any

from auto_client_acquisition.service_tower.service_catalog import get_service_by_id


def build_service_scorecard(service_id: str, metrics: dict[str, Any]) -> dict[str, Any]:
    svc = get_service_by_id(service_id)
    m = metrics or {}
    drafts = int(m.get("drafts_created", 0))
    approved = int(m.get("approvals", 0))
    meetings = int(m.get("meetings_booked", 0))
    blocked = int(m.get("risks_blocked", 0))
    score = min(100, 20 + drafts * 3 + approved * 5 + meetings * 10 + blocked * 2)
    status = "strong" if score >= 70 else "needs_attention"
    return {
        "service_id": service_id,
        "score": score,
        "status": status,
        "summary_ar": f"درجة الخدمة {score}/١٠٠ — الحالة: {status}.",
        "inputs_used": list(m.keys()),
        "name_ar": (svc or {}).get("name_ar"),
        "demo": True,
    }


def calculate_service_success_score(metrics: dict[str, Any]) -> int:
    sc = build_service_scorecard("growth_os", metrics)
    return int(sc.get("score", 0))


def recommend_next_step(metrics: dict[str, Any]) -> dict[str, Any]:
    if int(metrics.get("risks_blocked", 0)) > int(metrics.get("meetings_booked", 0)):
        return {"next_step_ar": "ركّز على تحويل المسودات المعتمدة إلى اجتماعات.", "demo": True}
    return {"next_step_ar": "وسّع القنوات بعد تثبيت الاجتماعات.", "demo": True}


def summarize_scorecard_ar(scorecard: dict[str, Any]) -> str:
    return str(scorecard.get("summary_ar") or "")
