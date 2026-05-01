#!/usr/bin/env python3
"""Paid Beta Daily Scorecard — تتبّع التقدّم اليومي نحو أول إيراد.

كل يوم في Paid Beta، شغّل:

    python scripts/paid_beta_daily_scorecard.py \\
        --messages 25 --replies 4 --demos 2 --pilots 1 --payments 0 --proof-packs 0

أو بصيغة JSON للأتمتة:

    python scripts/paid_beta_daily_scorecard.py \\
        --messages 25 --replies 4 --demos 2 --pilots 1 --payments 1 --proof-packs 0 --json

الهدف خلال 7 أيام:
    70 تواصل يدوي / 15 رد / 7 ديمو / 3 pilots / 1–2 paid / 1 Proof Pack على الأقل.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from datetime import date


# ----- Targets -----

WEEKLY_TARGETS = {
    "messages":    {"min": 50, "stretch": 70},
    "replies":     {"min": 5,  "stretch": 15},
    "demos":       {"min": 3,  "stretch": 7},
    "pilots":      {"min": 2,  "stretch": 3},
    "payments":    {"min": 1,  "stretch": 2},
    "proof_packs": {"min": 1,  "stretch": 1},
}

DAILY_TARGETS = {
    # ÷ 7 (مدوّر للأعلى) لأي metric
    "messages":    10,
    "replies":     1,
    "demos":       1,
    "pilots":      0,   # ≥1 خلال الأسبوع
    "payments":    0,   # ≥1 خلال الأسبوع
    "proof_packs": 0,   # ≥1 خلال الأسبوع
}


# ----- Computation -----

@dataclass
class Scorecard:
    as_of: str
    messages: int
    replies: int
    demos: int
    pilots: int
    payments: int
    proof_packs: int
    reply_rate: float
    demo_rate: float
    pilot_rate: float
    payment_rate: float
    daily_verdict: str
    weekly_verdict: str
    next_actions: list[str]


def _safe_div(a: int, b: int) -> float:
    return round(a / b, 3) if b > 0 else 0.0


def _daily_verdict(metrics: dict[str, int]) -> str:
    """Compare today's metrics to daily targets."""
    misses = []
    for key, target in DAILY_TARGETS.items():
        if target == 0:
            continue
        if metrics[key] < target:
            misses.append(f"{key}: {metrics[key]}/{target}")
    if not misses:
        return "ON_TRACK"
    if len(misses) == 1:
        return f"BEHIND on {misses[0]}"
    return f"OFF_TRACK: {', '.join(misses)}"


def _weekly_verdict(metrics: dict[str, int]) -> str:
    """Compare cumulative-week metrics to weekly targets (assumes the input is week-to-date totals)."""
    blockers = []
    misses = []
    for key, t in WEEKLY_TARGETS.items():
        v = metrics[key]
        if v < t["min"]:
            blockers.append(f"{key} {v}/{t['min']}")
        elif v < t["stretch"]:
            misses.append(f"{key} {v}/{t['stretch']}")
    if not blockers and not misses:
        return "WEEKLY_TARGETS_HIT"
    if blockers:
        return "BLOCKERS: " + ", ".join(blockers)
    return "STRETCH_PENDING: " + ", ".join(misses)


def _next_actions(metrics: dict[str, int]) -> list[str]:
    actions: list[str] = []

    if metrics["messages"] < DAILY_TARGETS["messages"]:
        deficit = DAILY_TARGETS["messages"] - metrics["messages"]
        actions.append(
            f"أرسل {deficit} رسالة إضافية اليوم (LinkedIn/Email/WhatsApp opt-in فقط)."
        )

    if metrics["messages"] >= 5 and metrics["replies"] == 0:
        actions.append(
            "0 ردود مع >5 رسائل — راجع نبرة الرسالة وعدّلها (saudi_tone_eval)."
        )

    if metrics["replies"] >= 2 and metrics["demos"] == 0:
        actions.append(
            "ردود إيجابية بدون ديمو — احجز ديمو 12 دقيقة لكل رد إيجابي اليوم."
        )

    if metrics["demos"] >= 2 and metrics["pilots"] == 0:
        actions.append(
            "ديمو ≥2 بدون عرض Pilot — أرسل عرض Pilot 499 + Free Diagnostic لكل ديمو."
        )

    if metrics["pilots"] >= 1 and metrics["payments"] == 0:
        actions.append(
            "Pilot معروض بدون دفع — تابع Moyasar invoice manual + رسالة متابعة دفع."
        )

    if metrics["payments"] >= 1 and metrics["proof_packs"] == 0:
        actions.append(
            "أول دفعة وصلت — ابدأ Pilot delivery + أعد Proof Pack v1 خلال 48 ساعة."
        )

    if not actions:
        actions.append(
            "اليوم ON_TRACK. حافظ على الإيقاع: 10 رسائل + 5 follow-ups + 1 ديمو."
        )

    return actions


def build_scorecard(
    messages: int,
    replies: int,
    demos: int,
    pilots: int,
    payments: int,
    proof_packs: int,
    as_of: str | None = None,
) -> Scorecard:
    metrics = {
        "messages": messages,
        "replies": replies,
        "demos": demos,
        "pilots": pilots,
        "payments": payments,
        "proof_packs": proof_packs,
    }
    return Scorecard(
        as_of=as_of or date.today().isoformat(),
        messages=messages,
        replies=replies,
        demos=demos,
        pilots=pilots,
        payments=payments,
        proof_packs=proof_packs,
        reply_rate=_safe_div(replies, messages),
        demo_rate=_safe_div(demos, replies),
        pilot_rate=_safe_div(pilots, demos),
        payment_rate=_safe_div(payments, pilots),
        daily_verdict=_daily_verdict(metrics),
        weekly_verdict=_weekly_verdict(metrics),
        next_actions=_next_actions(metrics),
    )


# ----- Rendering -----

def render_text(card: Scorecard) -> str:
    lines = [
        "════════════════════════════════════════════════",
        f"  Paid Beta Daily Scorecard — {card.as_of}",
        "════════════════════════════════════════════════",
        "",
        "اليوم:",
        f"  📨 رسائل أُرسلت:        {card.messages:>3}  (يومي ≥10)",
        f"  💬 ردود إيجابية:       {card.replies:>3}  (يومي ≥1)",
        f"  📅 ديمو محجوز:         {card.demos:>3}  (يومي ≥1)",
        f"  🚀 Pilots معروضة:      {card.pilots:>3}  (أسبوعي ≥2)",
        f"  💳 دفعات وصلت:         {card.payments:>3}  (أسبوعي ≥1)",
        f"  📦 Proof Packs مرسلة:  {card.proof_packs:>3}  (أسبوعي ≥1)",
        "",
        "Conversion Rates:",
        f"  reply_rate    = {card.reply_rate:.1%}",
        f"  demo_rate     = {card.demo_rate:.1%}  (replies → demos)",
        f"  pilot_rate    = {card.pilot_rate:.1%}  (demos → pilots)",
        f"  payment_rate  = {card.payment_rate:.1%}  (pilots → paid)",
        "",
        f"Daily Verdict:   {card.daily_verdict}",
        f"Weekly Verdict:  {card.weekly_verdict}",
        "",
        "Next Actions:",
    ]
    for i, action in enumerate(card.next_actions, 1):
        lines.append(f"  {i}. {action}")
    lines.extend([
        "",
        "════════════════════════════════════════════════",
        "Targets: 50–70 messages / 5–15 replies / 3–7 demos /",
        "         2–3 pilots / 1–2 paid / 1+ proof pack الأسبوع.",
        "════════════════════════════════════════════════",
    ])
    return "\n".join(lines)


def render_json(card: Scorecard) -> str:
    return json.dumps(asdict(card), ensure_ascii=False, indent=2)


# ----- CLI -----

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Paid Beta daily scorecard — track manual outreach progress.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python scripts/paid_beta_daily_scorecard.py "
            "--messages 25 --replies 4 --demos 2 --pilots 1 --payments 0 --proof-packs 0\n"
            "  python scripts/paid_beta_daily_scorecard.py "
            "--messages 25 --replies 4 --demos 2 --pilots 1 --payments 1 --proof-packs 0 --json"
        ),
    )
    p.add_argument("--messages", type=int, default=0, help="رسائل أُرسلت")
    p.add_argument("--replies", type=int, default=0, help="ردود إيجابية")
    p.add_argument("--demos", type=int, default=0, help="ديمو محجوز")
    p.add_argument("--pilots", type=int, default=0, help="Pilots معروضة")
    p.add_argument("--payments", type=int, default=0, help="دفعات وصلت")
    p.add_argument("--proof-packs", dest="proof_packs", type=int, default=0,
                   help="Proof Packs مُسلَّمة")
    p.add_argument("--as-of", type=str, default=None,
                   help="تاريخ (YYYY-MM-DD أو 'today')")
    p.add_argument("--json", action="store_true", help="إخراج JSON")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    as_of = None if (args.as_of in (None, "today")) else args.as_of
    card = build_scorecard(
        messages=args.messages,
        replies=args.replies,
        demos=args.demos,
        pilots=args.pilots,
        payments=args.payments,
        proof_packs=args.proof_packs,
        as_of=as_of,
    )
    output = render_json(card) if args.json else render_text(card)
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, OSError):
        pass
    print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
