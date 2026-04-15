#!/usr/bin/env python3
"""
Follow-up Prioritization Engine
────────────────────────────────
Reads the outreach tracker CSV and produces a prioritized daily action list.

Scoring model (0–100):
    recency       (0–30)  : how stale the last touch is
    funnel_stage  (0–30)  : how close the prospect is to closing
    engagement    (0–25)  : reply_count / touches ratio
    tier          (0–15)  : tag-based (e.g. "enterprise" > "smb")

Usage:
    python prioritize.py                     # top 10 for today
    python prioritize.py --top 25 --json     # top 25 as JSON
    python prioritize.py --csv PATH          # custom CSV source
    python prioritize.py --export today.csv  # export actions to CSV
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional


FUNNEL_WEIGHTS = {
    "pending": 10,
    "contacted": 18,
    "replied": 26,
    "qualified": 30,
    "call_booked": 28,
    "closed_won": 0,
    "closed_lost": 0,
    "dnc": 0,
}

TIER_WEIGHTS = {
    "enterprise": 15,
    "mid_market": 10,
    "smb": 6,
    "real_estate": 8,
    "riyadh": 3,
}

ACTION_TEMPLATES = {
    "pending":     "🚀 أرسل WA-01 (الرسالة الأولى)",
    "contacted":   "⏰ أرسل WA-02 (متابعة ٤٨ ساعة)",
    "replied":     "💬 رد يدوي + تأهيل الليد",
    "qualified":   "📞 احجز مكالمة اليوم — جاهز للإغلاق",
    "call_booked": "🎯 تذكير + تحضير العرض",
}


@dataclass
class Prospect:
    phone: str
    company: str
    contact_name: str
    channel: str
    status: str
    first_contact_at: str
    last_contact_at: str
    next_followup_at: str
    reply_count: int
    touches: int
    notes: str
    tags: str


@dataclass
class Action:
    prospect: Prospect
    score: int
    action: str
    reason: str
    days_since_touch: Optional[int]


# ── Loading ───────────────────────────────────────────────────

def load_csv(path: Path) -> list[Prospect]:
    if not path.exists():
        print(f"[fatal] CSV not found: {path}", file=sys.stderr)
        sys.exit(1)
    rows: list[Prospect] = []
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(
                Prospect(
                    phone=row.get("phone", "").strip(),
                    company=row.get("company", "").strip(),
                    contact_name=row.get("contact_name", "").strip(),
                    channel=row.get("channel", "whatsapp").strip(),
                    status=row.get("status", "pending").strip(),
                    first_contact_at=row.get("first_contact_at", "").strip(),
                    last_contact_at=row.get("last_contact_at", "").strip(),
                    next_followup_at=row.get("next_followup_at", "").strip(),
                    reply_count=_safe_int(row.get("reply_count")),
                    touches=_safe_int(row.get("touches")),
                    notes=row.get("notes", "").strip(),
                    tags=row.get("tags", "").strip(),
                )
            )
    return rows


def _safe_int(v: Optional[str]) -> int:
    try:
        return int(v) if v else 0
    except ValueError:
        return 0


# ── Scoring ───────────────────────────────────────────────────

def days_since(iso: str) -> Optional[int]:
    if not iso:
        return None
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(iso, fmt)
            return (datetime.now() - dt).days
        except ValueError:
            continue
    return None


def score_prospect(p: Prospect) -> tuple[int, str]:
    """Return (score, explanation)."""
    reasons: list[str] = []

    # Drop statuses that are terminal
    if p.status in ("closed_won", "closed_lost", "dnc"):
        return 0, "terminal status"

    # 1. Funnel stage (0–30)
    funnel = FUNNEL_WEIGHTS.get(p.status, 0)
    reasons.append(f"funnel({p.status})={funnel}")

    # 2. Recency (0–30) — stale prospects get pushed up
    days = days_since(p.last_contact_at or p.first_contact_at)
    if days is None:
        # Never contacted → high priority if pending
        recency = 25 if p.status == "pending" else 10
    else:
        # Sweet spot: 1–3 days stale = max; older = still high; today = low
        if days == 0:
            recency = 5
        elif 1 <= days <= 3:
            recency = 30
        elif 4 <= days <= 7:
            recency = 22
        elif 8 <= days <= 14:
            recency = 15
        else:
            recency = 8
    reasons.append(f"recency={recency}")

    # 3. Engagement (0–25) — reply_count/touches ratio
    if p.touches > 0:
        ratio = p.reply_count / p.touches
        engagement = int(ratio * 25)
    else:
        engagement = 0
    reasons.append(f"engagement={engagement}")

    # 4. Tier (0–15) — best matching tag
    tier = 0
    tags = [t.strip().lower() for t in p.tags.split(";") if t.strip()]
    for tag in tags:
        tier = max(tier, TIER_WEIGHTS.get(tag, 0))
    reasons.append(f"tier={tier}")

    total = funnel + recency + engagement + tier
    return min(total, 100), " + ".join(reasons)


def pick_action(p: Prospect, days: Optional[int]) -> str:
    action = ACTION_TEMPLATES.get(p.status, "— راجع الحالة")
    if p.status == "contacted" and (days is None or days < 2):
        return "⏳ انتظر (أقل من ٤٨ ساعة من آخر تواصل)"
    return action


def prioritize(prospects: list[Prospect]) -> list[Action]:
    actions: list[Action] = []
    for p in prospects:
        score, reason = score_prospect(p)
        if score == 0:
            continue
        days = days_since(p.last_contact_at or p.first_contact_at)
        actions.append(
            Action(
                prospect=p,
                score=score,
                action=pick_action(p, days),
                reason=reason,
                days_since_touch=days,
            )
        )
    actions.sort(key=lambda a: a.score, reverse=True)
    return actions


# ── Output ────────────────────────────────────────────────────

def render_table(actions: list[Action], limit: int) -> None:
    actions = actions[:limit]
    if not actions:
        print("✓ no actions today. you're caught up.")
        return

    print(f"\n▶ Top {len(actions)} priority actions for today\n")
    print(f"{'#':<4}{'SCORE':<8}{'STATUS':<14}{'STALE':<8}{'COMPANY':<30}{'ACTION'}")
    print("─" * 110)
    for i, a in enumerate(actions, 1):
        stale = f"{a.days_since_touch}d" if a.days_since_touch is not None else "—"
        company = (a.prospect.company or a.prospect.phone)[:28]
        print(f"{i:<4}{a.score:<8}{a.prospect.status:<14}{stale:<8}{company:<30}{a.action}")

    print()
    print(f"Focus: complete the top {min(10, len(actions))} before lunch.")


def render_json(actions: list[Action], limit: int) -> None:
    out = []
    for a in actions[:limit]:
        out.append(
            {
                "score": a.score,
                "phone": a.prospect.phone,
                "company": a.prospect.company,
                "status": a.prospect.status,
                "action": a.action,
                "days_since_touch": a.days_since_touch,
                "reason": a.reason,
                "notes": a.prospect.notes,
            }
        )
    print(json.dumps(out, ensure_ascii=False, indent=2))


def export_csv(actions: list[Action], path: Path, limit: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["rank", "score", "phone", "company", "status", "action", "days_since_touch", "notes"])
        for i, a in enumerate(actions[:limit], 1):
            writer.writerow(
                [
                    i,
                    a.score,
                    a.prospect.phone,
                    a.prospect.company,
                    a.prospect.status,
                    a.action,
                    a.days_since_touch if a.days_since_touch is not None else "",
                    a.prospect.notes.replace("\n", " | "),
                ]
            )
    print(f"✓ exported {min(limit, len(actions))} actions → {path}")


# ── CLI ───────────────────────────────────────────────────────

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Prioritize today's outreach follow-ups")
    parser.add_argument("--csv", default="../outreach_tracker/outreach.csv", help="source CSV from tracker")
    parser.add_argument("--top", type=int, default=10, help="max actions to show")
    parser.add_argument("--json", action="store_true", help="output JSON instead of a table")
    parser.add_argument("--export", metavar="PATH", help="write top actions to a CSV file")
    args = parser.parse_args(argv)

    csv_path = Path(args.csv)
    prospects = load_csv(csv_path)
    actions = prioritize(prospects)

    if args.export:
        export_csv(actions, Path(args.export), args.top)
        return 0

    if args.json:
        render_json(actions, args.top)
    else:
        render_table(actions, args.top)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
