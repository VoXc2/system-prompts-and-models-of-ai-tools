#!/usr/bin/env python3
"""Print Dealix Private/Paid Beta daily scorecard metrics (stdin for ops, no network).

Reads counts from CLI flags, environment variable DEALIX_DAILY_SCORECARD_JSON,
or a JSON file (--file). Missing keys default to 0.

Example:
  python scripts/paid_beta_daily_scorecard.py --messages 10 --replies 2 --demos 1
  python scripts/paid_beta_daily_scorecard.py --file .dealix/daily_scorecard.json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))


def _configure_stdio_utf8() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError):
            pass


def _load_json_file(path: Path) -> dict[str, object]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("JSON root must be an object")
    return {str(k): v for k, v in raw.items()}


def _coerce_int(val: object) -> int:
    if val is None:
        return 0
    if isinstance(val, bool):
        return int(val)
    if isinstance(val, int):
        return val
    if isinstance(val, float):
        return int(val)
    s = str(val).strip()
    if not s:
        return 0
    try:
        return int(float(s))
    except ValueError:
        return 0


def build_metrics(
    *,
    messages_sent: int = 0,
    replies: int = 0,
    demos: int = 0,
    pilots: int = 0,
    payments: int = 0,
    proof_packs: int = 0,
) -> dict[str, int]:
    return {
        "messages_sent": max(0, messages_sent),
        "replies": max(0, replies),
        "demos": max(0, demos),
        "pilots": max(0, pilots),
        "payments": max(0, payments),
        "proof_packs": max(0, proof_packs),
    }


def merge_from_mapping(base: dict[str, int], data: dict[str, object]) -> dict[str, int]:
    aliases = {
        "messages_sent": ("messages_sent", "messages", "msgs"),
        "replies": ("replies", "positive_replies", "reply"),
        "demos": ("demos", "demos_booked", "demo"),
        "pilots": ("pilots", "pilots_offered", "pilot"),
        "payments": ("payments", "payments_received", "paid"),
        "proof_packs": ("proof_packs", "proof_pack", "proofs"),
    }
    out = dict(base)
    for canonical, keys in aliases.items():
        for k in keys:
            if k in data:
                out[canonical] = max(out.get(canonical, 0), _coerce_int(data[k]))
                break
    return out


def print_scorecard(m: dict[str, int], *, as_json: bool) -> None:
    if as_json:
        print(json.dumps(m, ensure_ascii=False, indent=2))
        return
    lines = [
        "Dealix — Daily scorecard",
        "------------------------",
        f"messages_sent   {m['messages_sent']}",
        f"replies         {m['replies']}",
        f"demos           {m['demos']}",
        f"pilots          {m['pilots']}",
        f"payments        {m['payments']}",
        f"proof_packs     {m['proof_packs']}",
    ]
    print("\n".join(lines))


def main() -> int:
    _configure_stdio_utf8()
    p = argparse.ArgumentParser(description="Print daily beta scorecard metrics")
    p.add_argument("--file", type=Path, help="JSON file with metric keys (see docs/PRIVATE_BETA_OPERATING_BOARD.md)")
    p.add_argument("--json", action="store_true", help="Print JSON only")
    p.add_argument("--messages", type=int, default=None)
    p.add_argument("--replies", type=int, default=None)
    p.add_argument("--demos", type=int, default=None)
    p.add_argument("--pilots", type=int, default=None)
    p.add_argument("--payments", type=int, default=None)
    p.add_argument("--proof-packs", type=int, default=None)
    args = p.parse_args()

    m = build_metrics()

    env_blob = os.environ.get("DEALIX_DAILY_SCORECARD_JSON", "").strip()
    if env_blob:
        try:
            parsed = json.loads(env_blob)
            if isinstance(parsed, dict):
                m = merge_from_mapping(m, parsed)
        except json.JSONDecodeError as exc:
            print(f"Invalid DEALIX_DAILY_SCORECARD_JSON: {exc}", file=sys.stderr)
            return 1

    if args.file:
        try:
            file_data = _load_json_file(args.file)
            # file uses string keys; merge
            m = merge_from_mapping(m, {str(k): v for k, v in file_data.items()})
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            print(f"--file error: {exc}", file=sys.stderr)
            return 1

    cli_overrides = {
        "messages_sent": args.messages,
        "replies": args.replies,
        "demos": args.demos,
        "pilots": args.pilots,
        "payments": args.payments,
        "proof_packs": args.proof_packs,
    }
    for key, val in cli_overrides.items():
        if val is not None:
            m[key] = max(0, int(val))

    print_scorecard(m, as_json=args.json)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
