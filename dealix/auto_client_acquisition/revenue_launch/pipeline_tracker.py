"""Deterministic pipeline tracker — schema, add, update, summarize."""

from __future__ import annotations

from typing import Any

PIPELINE_STAGES: tuple[str, ...] = (
    "identified",
    "contacted",
    "replied",
    "demo_booked",
    "diagnostic_sent",
    "pilot_offered",
    "paid",
    "lost",
)

# Default Sheet/CSV columns the pipeline tracker emits.
PIPELINE_COLUMNS: tuple[str, ...] = (
    "company", "person", "segment", "source", "channel",
    "message_sent_at", "reply_status", "stage",
    "demo_booked", "service_offered", "price_sar",
    "paid", "next_step", "notes",
)


def build_pipeline_schema() -> dict[str, Any]:
    """Return the canonical pipeline schema (deterministic)."""
    return {
        "stages": list(PIPELINE_STAGES),
        "columns": list(PIPELINE_COLUMNS),
        "stage_progression": [
            {"from": "identified", "to": "contacted", "trigger": "outreach_sent"},
            {"from": "contacted", "to": "replied", "trigger": "reply_received"},
            {"from": "replied", "to": "demo_booked", "trigger": "demo_scheduled"},
            {"from": "demo_booked", "to": "diagnostic_sent", "trigger": "diagnostic_delivered"},
            {"from": "diagnostic_sent", "to": "pilot_offered", "trigger": "offer_sent"},
            {"from": "pilot_offered", "to": "paid", "trigger": "moyasar_invoice_paid"},
        ],
        "loss_reasons_ar": [
            "السعر",
            "التوقيت",
            "بديل قائم",
            "صانع القرار غير متاح",
            "PDPL/أمان",
            "لا حاجة الآن",
        ],
        "notes_ar": (
            "هذا المخطط deterministic. كل صفقة تتقدم بـ trigger صريح فقط، "
            "ولا يحدث تغيير stage بدون event موثّق."
        ),
    }


def add_prospect(
    *,
    pipeline: list[dict[str, Any]] | None = None,
    company: str,
    person: str = "",
    segment: str = "",
    source: str = "manual",
    channel: str = "email",
    notes: str = "",
) -> dict[str, Any]:
    """Add a new prospect to the in-memory pipeline. Stage starts at identified."""
    entry: dict[str, Any] = {
        "company": company,
        "person": person,
        "segment": segment,
        "source": source,
        "channel": channel,
        "message_sent_at": None,
        "reply_status": "none",
        "stage": "identified",
        "demo_booked": False,
        "service_offered": "",
        "price_sar": 0,
        "paid": False,
        "next_step": "send_first_outreach",
        "notes": notes[:300],
    }
    if pipeline is not None:
        pipeline.append(entry)
    return entry


def update_stage(
    *,
    prospect: dict[str, Any],
    new_stage: str,
    notes: str = "",
) -> dict[str, Any]:
    """Move a prospect to a new stage. Validates the new stage is known."""
    if new_stage not in PIPELINE_STAGES:
        raise ValueError(
            f"Unknown stage: {new_stage}. "
            f"Valid: {', '.join(PIPELINE_STAGES)}"
        )
    prospect["stage"] = new_stage
    if notes:
        existing = str(prospect.get("notes", ""))
        sep = " | " if existing else ""
        prospect["notes"] = (existing + sep + notes)[:300]
    if new_stage == "paid":
        prospect["paid"] = True
        prospect["next_step"] = "deliver_24h"
    elif new_stage == "lost":
        prospect["next_step"] = "archive"
    return prospect


def summarize_pipeline(
    pipeline: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    """Aggregate pipeline counts + revenue."""
    pipeline = pipeline or []
    by_stage: dict[str, int] = {s: 0 for s in PIPELINE_STAGES}
    by_segment: dict[str, int] = {}
    revenue_paid_sar = 0.0
    revenue_offered_sar = 0.0

    for p in pipeline:
        stage = str(p.get("stage", "identified"))
        if stage in by_stage:
            by_stage[stage] += 1
        seg = str(p.get("segment", "unknown"))
        by_segment[seg] = by_segment.get(seg, 0) + 1
        price = float(p.get("price_sar", 0) or 0)
        if p.get("paid"):
            revenue_paid_sar += price
        if stage in ("pilot_offered", "paid"):
            revenue_offered_sar += price

    total = len(pipeline)
    won = by_stage["paid"]
    lost = by_stage["lost"]
    closed = won + lost
    win_rate = round(won / closed, 3) if closed else 0.0

    return {
        "total_prospects": total,
        "by_stage": by_stage,
        "by_segment": by_segment,
        "revenue_paid_sar": round(revenue_paid_sar, 2),
        "revenue_offered_sar": round(revenue_offered_sar, 2),
        "win_rate": win_rate,
        "summary_ar": [
            f"إجمالي الـ prospects: {total}",
            f"اتصالات: {by_stage['contacted']} | ردود: {by_stage['replied']}",
            f"ديموهات: {by_stage['demo_booked']} | عروض: {by_stage['pilot_offered']}",
            f"مدفوعة: {by_stage['paid']} | خسرت: {by_stage['lost']}",
            f"إيراد محصّل: {revenue_paid_sar:.0f} ريال",
            f"win rate: {win_rate * 100:.1f}%",
        ],
    }
