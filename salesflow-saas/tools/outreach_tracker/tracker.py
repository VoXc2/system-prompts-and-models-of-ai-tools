#!/usr/bin/env python3
"""
WhatsApp Outreach Tracker
─────────────────────────
A zero-dependency CLI tool to manage a cold WhatsApp outreach campaign.

Stores everything in a single CSV so it can also be opened in Google Sheets.

Usage:
    python tracker.py add +966512345678 "Riyadh Real Estate Co" --channel whatsapp
    python tracker.py status +966512345678 --to contacted
    python tracker.py note +966512345678 "Asked for callback tomorrow 3pm"
    python tracker.py list --status pending
    python tracker.py stats
    python tracker.py due        # prospects that need a follow-up today
    python tracker.py import contacts.csv

Statuses:
    pending       → not contacted yet
    contacted     → first message sent
    replied       → prospect replied
    qualified     → showed clear interest
    call_booked   → call scheduled
    closed_won    → paying customer
    closed_lost   → not a fit / declined
    dnc           → do not contact (opt-out)

CSV schema:
    phone, company, contact_name, channel, status, first_contact_at,
    last_contact_at, next_followup_at, reply_count, touches, notes, tags
"""
from __future__ import annotations

import argparse
import csv
import os
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

DATA_FILE = Path(os.environ.get("DEALIX_TRACKER_CSV", "outreach.csv"))

FIELDS = [
    "phone",
    "company",
    "contact_name",
    "channel",
    "status",
    "first_contact_at",
    "last_contact_at",
    "next_followup_at",
    "reply_count",
    "touches",
    "notes",
    "tags",
]

VALID_STATUSES = {
    "pending",
    "contacted",
    "replied",
    "qualified",
    "call_booked",
    "closed_won",
    "closed_lost",
    "dnc",
}

# Follow-up cadence (days from last touch) based on current status
CADENCE_DAYS = {
    "pending": 0,
    "contacted": 2,
    "replied": 1,
    "qualified": 1,
    "call_booked": 0,
    "closed_won": 30,
    "closed_lost": 90,
    "dnc": None,  # never
}


# ── Data model ────────────────────────────────────────────────

@dataclass
class Prospect:
    phone: str
    company: str = ""
    contact_name: str = ""
    channel: str = "whatsapp"
    status: str = "pending"
    first_contact_at: str = ""
    last_contact_at: str = ""
    next_followup_at: str = ""
    reply_count: str = "0"
    touches: str = "0"
    notes: str = ""
    tags: str = ""

    def as_row(self) -> dict:
        return {k: getattr(self, k) for k in FIELDS}


# ── IO ────────────────────────────────────────────────────────

def load() -> list[Prospect]:
    if not DATA_FILE.exists():
        return []
    with DATA_FILE.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        return [Prospect(**{k: row.get(k, "") or "" for k in FIELDS}) for row in reader]


def save(rows: list[Prospect]) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with DATA_FILE.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow(row.as_row())


def find(rows: list[Prospect], phone: str) -> Optional[Prospect]:
    phone = phone.strip()
    for r in rows:
        if r.phone == phone:
            return r
    return None


def now_iso() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def today_date() -> datetime:
    return datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)


def compute_next_followup(status: str, last_contact_iso: str) -> str:
    days = CADENCE_DAYS.get(status)
    if days is None or not last_contact_iso:
        return ""
    try:
        last = datetime.strptime(last_contact_iso, "%Y-%m-%d %H:%M")
    except ValueError:
        last = datetime.now()
    return (last + timedelta(days=days)).strftime("%Y-%m-%d")


# ── Commands ──────────────────────────────────────────────────

def cmd_add(args: argparse.Namespace) -> int:
    rows = load()
    if find(rows, args.phone):
        print(f"⚠️  {args.phone} already exists", file=sys.stderr)
        return 1
    p = Prospect(
        phone=args.phone,
        company=args.company,
        contact_name=args.contact or "",
        channel=args.channel,
        status="pending",
        tags=args.tags or "",
    )
    rows.append(p)
    save(rows)
    print(f"✓ added {args.phone} ({args.company})")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    if args.to not in VALID_STATUSES:
        print(f"invalid status. use one of: {', '.join(sorted(VALID_STATUSES))}", file=sys.stderr)
        return 2
    rows = load()
    p = find(rows, args.phone)
    if not p:
        print(f"not found: {args.phone}", file=sys.stderr)
        return 1

    now = now_iso()
    p.status = args.to
    p.last_contact_at = now
    if not p.first_contact_at and args.to != "pending":
        p.first_contact_at = now
    p.touches = str(int(p.touches or "0") + 1)
    if args.to == "replied":
        p.reply_count = str(int(p.reply_count or "0") + 1)
    p.next_followup_at = compute_next_followup(args.to, now)

    save(rows)
    print(f"✓ {args.phone} → {args.to}  (next follow-up: {p.next_followup_at or '—'})")
    return 0


def cmd_note(args: argparse.Namespace) -> int:
    rows = load()
    p = find(rows, args.phone)
    if not p:
        print(f"not found: {args.phone}", file=sys.stderr)
        return 1
    stamped = f"[{now_iso()}] {args.text}"
    p.notes = f"{p.notes}\n{stamped}".strip() if p.notes else stamped
    save(rows)
    print(f"✓ note added to {args.phone}")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    rows = load()
    if args.status:
        rows = [r for r in rows if r.status == args.status]
    if args.tag:
        rows = [r for r in rows if args.tag in (r.tags or "")]
    if not rows:
        print("no results")
        return 0
    _print_table(rows)
    return 0


def cmd_stats(_: argparse.Namespace) -> int:
    rows = load()
    total = len(rows)
    if total == 0:
        print("empty tracker. run `tracker.py add` first.")
        return 0
    by_status: dict[str, int] = {}
    for r in rows:
        by_status[r.status] = by_status.get(r.status, 0) + 1

    contacted = sum(by_status.get(s, 0) for s in ["contacted", "replied", "qualified", "call_booked", "closed_won", "closed_lost"])
    replied = sum(by_status.get(s, 0) for s in ["replied", "qualified", "call_booked", "closed_won"])
    qualified = sum(by_status.get(s, 0) for s in ["qualified", "call_booked", "closed_won"])
    won = by_status.get("closed_won", 0)

    def pct(n: int, d: int) -> str:
        return f"{(n / d * 100):.1f}%" if d else "—"

    print("═══ Outreach Stats ═══")
    print(f"Total prospects:   {total}")
    print(f"Contacted:         {contacted}  ({pct(contacted, total)})")
    print(f"Reply rate:        {pct(replied, contacted)}")
    print(f"Qualification:     {pct(qualified, replied)}")
    print(f"Close rate:        {pct(won, qualified)}")
    print(f"Won:               {won}")
    print()
    print("By status:")
    for status in sorted(by_status):
        print(f"  {status:<14} {by_status[status]}")
    return 0


def cmd_due(_: argparse.Namespace) -> int:
    rows = load()
    today = today_date()
    due = []
    for r in rows:
        if r.status in ("closed_won", "closed_lost", "dnc"):
            continue
        if not r.next_followup_at:
            if r.status == "pending":
                due.append(r)
            continue
        try:
            d = datetime.strptime(r.next_followup_at, "%Y-%m-%d")
        except ValueError:
            continue
        if d <= today:
            due.append(r)
    if not due:
        print("✓ nothing due today. nice.")
        return 0
    print(f"▶ {len(due)} prospects need a touch today:\n")
    _print_table(due)
    return 0


def cmd_import(args: argparse.Namespace) -> int:
    """Import external CSV with at least `phone` and `company` columns."""
    src = Path(args.file)
    if not src.exists():
        print(f"not found: {src}", file=sys.stderr)
        return 1
    rows = load()
    existing = {r.phone for r in rows}
    added = 0
    with src.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            phone = (row.get("phone") or row.get("Phone") or "").strip()
            if not phone or phone in existing:
                continue
            p = Prospect(
                phone=phone,
                company=(row.get("company") or row.get("Company") or "").strip(),
                contact_name=(row.get("contact_name") or row.get("name") or "").strip(),
                channel=(row.get("channel") or "whatsapp").strip(),
                tags=(row.get("tags") or "").strip(),
            )
            rows.append(p)
            existing.add(phone)
            added += 1
    save(rows)
    print(f"✓ imported {added} new prospects from {src}")
    return 0


# ── Rendering ─────────────────────────────────────────────────

def _print_table(rows: list[Prospect]) -> None:
    cols = ["phone", "company", "status", "touches", "last_contact_at", "next_followup_at"]
    widths = {c: max(len(c), *(len((getattr(r, c) or "")) for r in rows)) for c in cols}
    header = "  ".join(c.ljust(widths[c]) for c in cols)
    print(header)
    print("─" * len(header))
    for r in rows:
        print("  ".join((getattr(r, c) or "").ljust(widths[c]) for c in cols))


# ── CLI wiring ────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="WhatsApp outreach tracker")
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("add", help="add a new prospect")
    a.add_argument("phone")
    a.add_argument("company")
    a.add_argument("--contact", default="")
    a.add_argument("--channel", default="whatsapp", choices=["whatsapp", "linkedin", "email", "call"])
    a.add_argument("--tags", default="")
    a.set_defaults(func=cmd_add)

    s = sub.add_parser("status", help="update prospect status")
    s.add_argument("phone")
    s.add_argument("--to", required=True)
    s.set_defaults(func=cmd_status)

    n = sub.add_parser("note", help="append a timestamped note")
    n.add_argument("phone")
    n.add_argument("text")
    n.set_defaults(func=cmd_note)

    l = sub.add_parser("list", help="list prospects")
    l.add_argument("--status")
    l.add_argument("--tag")
    l.set_defaults(func=cmd_list)

    st = sub.add_parser("stats", help="funnel summary")
    st.set_defaults(func=cmd_stats)

    d = sub.add_parser("due", help="prospects due for follow-up today")
    d.set_defaults(func=cmd_due)

    i = sub.add_parser("import", help="bulk import from CSV")
    i.add_argument("file")
    i.set_defaults(func=cmd_import)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
