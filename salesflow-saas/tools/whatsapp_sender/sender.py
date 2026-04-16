#!/usr/bin/env python3
"""
WhatsApp Cloud API Message Sender
──────────────────────────────────
Sends templated or free-text messages through the Meta WhatsApp Cloud API
and logs every send into the outreach tracker CSV.

Requirements:
    - A Meta WhatsApp Business account
    - A permanent / system-user access token
    - The phone_number_id from Meta Business Manager

Environment variables:
    WA_ACCESS_TOKEN     — Meta permanent token (required)
    WA_PHONE_NUMBER_ID  — your WhatsApp phone number ID (required)
    DEALIX_TRACKER_CSV  — path to outreach tracker CSV (optional, default: ../outreach_tracker/outreach.csv)

Usage:
    # Send a free-text message
    python sender.py send +966500000001 "هلا! لاحظت أغلب شركات العقار..."

    # Send a pre-defined template (WA-01 through WA-05)
    python sender.py template +966500000001 WA-01

    # Bulk send WA-01 to all 'pending' prospects from tracker
    python sender.py blast WA-01 --status pending --limit 30

    # Dry-run (print what would be sent, don't actually send)
    python sender.py blast WA-01 --status pending --dry-run
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Optional
from urllib.request import Request, urlopen
from urllib.error import HTTPError

# ── Config ────────────────────────────────────────────────────

WA_API_URL = "https://graph.facebook.com/v20.0"
ACCESS_TOKEN = os.environ.get("WA_ACCESS_TOKEN", "")
PHONE_NUMBER_ID = os.environ.get("WA_PHONE_NUMBER_ID", "")

TRACKER_CSV = Path(os.environ.get(
    "DEALIX_TRACKER_CSV",
    str(Path(__file__).parent / ".." / "outreach_tracker" / "outreach.csv"),
))

# ── Message templates ─────────────────────────────────────────

TEMPLATES = {
    "WA-01": (
        "هلا 👋\n\n"
        "لاحظت أغلب شركات العقار تضيع ليدات كثيرة بسبب متابعة الواتساب اليدوية.\n\n"
        "أنا شغال على نظام يرفع نسبة إغلاق الصفقات من الواتساب خلال ١٤ يوم فقط — والنتيجة مضمونة.\n\n"
        "لو عندكم ضغط ليدات أو متابعة غير منظمة، أقدر أوريك حل بسيط ممكن يضاعف الإغلاق.\n\n"
        "تبي أشرحه لك بسرعة؟"
    ),
    "WA-02": (
        "مساء الخير 👋\n\n"
        "ما بغيت أثقل عليك — بس شفت أنكم شغالين وكنت متأكد إن الموضوع يهمكم.\n\n"
        "نقطة وحدة بس: لو ترد عليّ بـ \"لا\" أو \"مش الوقت\"، أوقف المتابعة فوراً. احترم وقتك.\n\n"
        "غير كذا، عندي دراسة صغيرة (٤ صفحات) عن كيف شركات العقار تضيع ٤٠٪ من ليداتها. أرسلها لك؟"
    ),
    "WA-03": (
        "ممتاز 🔥\n\n"
        "خل أعطيك فكرة سريعة عن اللي نسويه:\n\n"
        "١. نربط واتساب Business الخاص بكم\n"
        "٢. الذكاء الاصطناعي يرد على الليدات الجديدة خلال ثوانٍ\n"
        "٣. يصنف الليد ويعطيكم الأولوية\n"
        "٤. يتابع تلقائياً للي ما ردّوا\n\n"
        "النتيجة: إغلاق يزيد ٢٠–٤٠٪ خلال أسبوعين.\n\n"
        "أقدر أحجز ١٥ دقيقة معك بكرة أو بعده؟"
    ),
    "WA-04": (
        "تذكير ودّي 🙏\n\n"
        "مكالمتنا بكرة. قبل المكالمة، حاب أعرف فقط:\n"
        "١. كم ليد يجيكم شهرياً تقريباً؟\n"
        "٢. من اللي يتابعهم حالياً؟\n\n"
        "حتى أجي بفكرة جاهزة توفر وقتك."
    ),
    "WA-05": (
        "شكراً جزيلاً على وقتك اليوم 🙏\n\n"
        "كما اتفقنا، هذا ملخص العرض:\n\n"
        "🎯 Pilot ١٤ يوم\n"
        "- Setup: ٥,٠٠٠ ريال (مرة واحدة)\n"
        "- بعد النجاح: ٢,٠٠٠ ريال/شهر\n\n"
        "🛡️ الضمان: لو ما زاد الإغلاق خلال ١٤ يوم — كامل المبلغ يرجع.\n\n"
        "جاهز نبدأ؟ قل \"نبدأ\" وأرسل لك عقد Pilot خلال ٣٠ دقيقة."
    ),
}


# ── API helpers ───────────────────────────────────────────────

def send_whatsapp_message(to: str, body: str) -> dict:
    """Send a free-text WhatsApp message via Cloud API. Returns the API response."""
    if not ACCESS_TOKEN:
        print("[error] WA_ACCESS_TOKEN not set", file=sys.stderr)
        sys.exit(1)
    if not PHONE_NUMBER_ID:
        print("[error] WA_PHONE_NUMBER_ID not set", file=sys.stderr)
        sys.exit(1)

    # Normalize phone number (remove spaces, ensure +)
    to = to.strip().replace(" ", "")
    if not to.startswith("+"):
        to = "+" + to

    url = f"{WA_API_URL}/{PHONE_NUMBER_ID}/messages"
    payload = json.dumps({
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to.lstrip("+"),  # API wants digits only
        "type": "text",
        "text": {"body": body},
    }).encode()

    req = Request(url, data=payload, method="POST")
    req.add_header("Authorization", f"Bearer {ACCESS_TOKEN}")
    req.add_header("Content-Type", "application/json")

    try:
        with urlopen(req) as resp:
            return json.loads(resp.read())
    except HTTPError as e:
        error_body = e.read().decode() if hasattr(e, "read") else str(e)
        print(f"[error] WhatsApp API {e.code}: {error_body}", file=sys.stderr)
        return {"error": error_body, "status_code": e.code}


def log_to_tracker(phone: str, template_name: Optional[str] = None):
    """Update the outreach tracker after sending a message."""
    tracker_script = TRACKER_CSV.parent / "tracker.py"
    if not tracker_script.exists():
        return

    import subprocess
    env = {**os.environ, "DEALIX_TRACKER_CSV": str(TRACKER_CSV)}

    # Try to mark as contacted
    subprocess.run(
        [sys.executable, str(tracker_script), "status", phone, "--to", "contacted"],
        env=env, capture_output=True,
    )

    # Add a note about which template was sent
    if template_name:
        subprocess.run(
            [sys.executable, str(tracker_script), "note", phone, f"Sent {template_name} via WhatsApp sender"],
            env=env, capture_output=True,
        )


# ── Commands ──────────────────────────────────────────────────

def cmd_send(args: argparse.Namespace) -> int:
    body = " ".join(args.message)
    print(f"Sending to {args.phone}...")
    result = send_whatsapp_message(args.phone, body)
    if "error" in result:
        print(f"[fail] {result}")
        return 1
    print(f"✓ Sent. Message ID: {result.get('messages', [{}])[0].get('id', '?')}")
    log_to_tracker(args.phone)
    return 0


def cmd_template(args: argparse.Namespace) -> int:
    template_id = args.template_id.upper()
    if template_id not in TEMPLATES:
        print(f"[error] Unknown template: {template_id}. Available: {', '.join(sorted(TEMPLATES))}", file=sys.stderr)
        return 2
    body = TEMPLATES[template_id]
    print(f"Sending {template_id} to {args.phone}...")
    result = send_whatsapp_message(args.phone, body)
    if "error" in result:
        print(f"[fail] {result}")
        return 1
    print(f"✓ Sent {template_id}. Message ID: {result.get('messages', [{}])[0].get('id', '?')}")
    log_to_tracker(args.phone, template_id)
    return 0


def cmd_blast(args: argparse.Namespace) -> int:
    template_id = args.template_id.upper()
    if template_id not in TEMPLATES:
        print(f"[error] Unknown template: {template_id}", file=sys.stderr)
        return 2

    # Load prospects from tracker
    sys.path.insert(0, str(TRACKER_CSV.parent))
    try:
        import tracker
    except ImportError:
        print("[error] Cannot import tracker — is outreach_tracker/ adjacent?", file=sys.stderr)
        return 1

    os.environ["DEALIX_TRACKER_CSV"] = str(TRACKER_CSV)
    # Reload module to pick up env var
    import importlib
    importlib.reload(tracker)

    prospects = tracker.load()
    if args.status:
        prospects = [p for p in prospects if p.status == args.status]

    prospects = prospects[: args.limit]
    body = TEMPLATES[template_id]

    print(f"{'[DRY RUN] ' if args.dry_run else ''}Blasting {template_id} to {len(prospects)} prospects (status={args.status or 'any'})\n")

    sent = 0
    for p in prospects:
        if args.dry_run:
            print(f"  [dry] {p.phone} ({p.company})")
        else:
            print(f"  → {p.phone} ({p.company})...", end=" ")
            result = send_whatsapp_message(p.phone, body)
            if "error" not in result:
                print("✓")
                log_to_tracker(p.phone, template_id)
                sent += 1
            else:
                print("✗")
            time.sleep(1.5)  # rate-limit: ~40 msg/min

    print(f"\n{'[DRY RUN] ' if args.dry_run else ''}Done: {sent if not args.dry_run else len(prospects)} / {len(prospects)}")
    return 0


# ── CLI ───────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="WhatsApp Cloud API message sender + tracker integration")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("send", help="send a free-text message")
    s.add_argument("phone")
    s.add_argument("message", nargs="+")
    s.set_defaults(func=cmd_send)

    t = sub.add_parser("template", help="send a pre-defined template (WA-01 to WA-05)")
    t.add_argument("phone")
    t.add_argument("template_id", choices=list(TEMPLATES.keys()))
    t.set_defaults(func=cmd_template)

    b = sub.add_parser("blast", help="bulk send a template to tracker prospects")
    b.add_argument("template_id")
    b.add_argument("--status", default="pending", help="filter by prospect status")
    b.add_argument("--limit", type=int, default=30, help="max messages to send (default 30)")
    b.add_argument("--dry-run", action="store_true", help="print what would be sent without sending")
    b.set_defaults(func=cmd_blast)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
