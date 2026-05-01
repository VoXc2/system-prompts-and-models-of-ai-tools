"""Pilot Tracker — track 5–10 active pilots toward Public Launch gate.

Tracks each Pilot's lifecycle:
    intake → diagnostic_24h → pilot_48h → proof_pack_7d → upgrade_decision

Used by the Public Launch Gate to count `pilots_completed` and
`paid_customers`. Deterministic — no I/O, no LLM.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from typing import Any, Mapping, Sequence


PILOT_STAGES = (
    "intake",                 # T+0
    "diagnostic_sent",        # T+24h
    "pilot_delivered",        # T+48h
    "proof_pack_sent",        # T+7d
    "upgrade_decided",        # T+14d
    "completed",              # marked done
    "stalled",                # SLA breach
    "lost",                   # no upgrade, no case study
)

UPGRADE_OUTCOMES = (
    "growth_os_monthly",      # 2,999/mo subscription
    "partnership_growth",     # 3,000–7,500 SAR
    "case_study",             # free in exchange for case study
    "second_pilot",           # paid 499 again, different angle
    "no_upgrade",              # explicit decline
    "ghost",                   # no response
)


@dataclass
class PilotRecord:
    """A single Pilot's data."""
    pilot_id: str
    company: str
    sector: str
    city: str
    started_at: str           # ISO date
    stage: str
    paid: bool                # True if 499 SAR received OR signed Growth OS
    pilot_price_sar: int
    proof_pack_sent: bool
    proof_pack_sent_at: str | None
    upgrade_outcome: str | None
    upgrade_value_sar: int = 0
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class PilotSummary:
    """Aggregate view across all pilots."""
    total_pilots: int
    completed_pilots: int            # reached upgrade_decided or completed
    proof_packs_delivered: int
    paid_pilots: int
    paid_revenue_sar: int            # sum of pilot prices that were paid
    upgrade_revenue_sar: int         # sum of upgrade_value_sar
    case_studies: int                # upgrade_outcome == "case_study"
    growth_os_subscribers: int       # upgrade_outcome == "growth_os_monthly"
    stalled_pilots: int
    lost_pilots: int
    completion_rate: float           # completed / total
    paid_conversion_rate: float      # paid / total
    upgrade_conversion_rate: float   # any upgrade / completed
    by_sector: dict[str, int]
    by_city: dict[str, int]
    average_proof_pack_days: float
    summary_ar: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _parse_iso(s: str) -> datetime | None:
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None


def pilot_tracker_summary(pilots: Sequence[PilotRecord | Mapping[str, Any]]) -> PilotSummary:
    """Compute aggregate summary across all pilots.

    Accepts either PilotRecord instances or plain dicts (for API ingestion).
    """
    records: list[PilotRecord] = []
    for p in pilots:
        if isinstance(p, PilotRecord):
            records.append(p)
        else:
            records.append(PilotRecord(
                pilot_id=str(p.get("pilot_id", "")),
                company=str(p.get("company", "")),
                sector=str(p.get("sector", "unknown")),
                city=str(p.get("city", "unknown")),
                started_at=str(p.get("started_at", "")),
                stage=str(p.get("stage", "intake")),
                paid=bool(p.get("paid", False)),
                pilot_price_sar=int(p.get("pilot_price_sar", 499)),
                proof_pack_sent=bool(p.get("proof_pack_sent", False)),
                proof_pack_sent_at=p.get("proof_pack_sent_at"),
                upgrade_outcome=p.get("upgrade_outcome"),
                upgrade_value_sar=int(p.get("upgrade_value_sar", 0)),
                notes=str(p.get("notes", "")),
            ))

    total = len(records)
    completed_stages = {"upgrade_decided", "completed"}
    completed = sum(1 for r in records if r.stage in completed_stages)
    proof_count = sum(1 for r in records if r.proof_pack_sent)
    paid_count = sum(1 for r in records if r.paid)
    paid_revenue = sum(r.pilot_price_sar for r in records if r.paid)
    upgrade_revenue = sum(r.upgrade_value_sar for r in records)
    case_studies = sum(1 for r in records if r.upgrade_outcome == "case_study")
    gros_subs = sum(1 for r in records if r.upgrade_outcome == "growth_os_monthly")
    stalled = sum(1 for r in records if r.stage == "stalled")
    lost = sum(1 for r in records if r.stage == "lost")

    by_sector: dict[str, int] = {}
    by_city: dict[str, int] = {}
    for r in records:
        by_sector[r.sector] = by_sector.get(r.sector, 0) + 1
        by_city[r.city] = by_city.get(r.city, 0) + 1

    proof_durations: list[float] = []
    for r in records:
        if r.proof_pack_sent and r.proof_pack_sent_at and r.started_at:
            start = _parse_iso(r.started_at)
            done = _parse_iso(r.proof_pack_sent_at)
            if start and done:
                proof_durations.append((done - start).total_seconds() / 86400)
    avg_proof_days = (
        round(sum(proof_durations) / len(proof_durations), 2)
        if proof_durations else 0.0
    )

    summary_ar = (
        f"{total} Pilots إجمالاً، {completed} مكتمل، "
        f"{paid_count} مدفوع، {proof_count} Proof Packs، "
        f"{gros_subs} Growth OS، {case_studies} case studies."
    )

    return PilotSummary(
        total_pilots=total,
        completed_pilots=completed,
        proof_packs_delivered=proof_count,
        paid_pilots=paid_count,
        paid_revenue_sar=paid_revenue,
        upgrade_revenue_sar=upgrade_revenue,
        case_studies=case_studies,
        growth_os_subscribers=gros_subs,
        stalled_pilots=stalled,
        lost_pilots=lost,
        completion_rate=round(completed / total, 3) if total else 0.0,
        paid_conversion_rate=round(paid_count / total, 3) if total else 0.0,
        upgrade_conversion_rate=(
            round((gros_subs + case_studies) / completed, 3)
            if completed else 0.0
        ),
        by_sector=by_sector,
        by_city=by_city,
        average_proof_pack_days=avg_proof_days,
        summary_ar=summary_ar,
    )
