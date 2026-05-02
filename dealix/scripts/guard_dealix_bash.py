#!/usr/bin/env python3
"""Claude Code PreToolUse guard for Bash. Reads JSON from stdin.

Exit 0: allow. Exit 2: block. Unknown payload: allow (fail-open).
Run from repository root: python dealix/scripts/guard_dealix_bash.py
"""

from __future__ import annotations

import json
import re
import sys


def _command(data: dict) -> str:
    ti = data.get("tool_input")
    if isinstance(ti, dict):
        for k in ("command", "cmd", "bash_command"):
            v = ti.get(k)
            if isinstance(v, str):
                return v
    return ""


def main() -> int:
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        return 0

    if not isinstance(data, dict):
        return 0

    if data.get("hook_event_name") and data.get("hook_event_name") != "PreToolUse":
        return 0

    if str(data.get("tool_name") or "") != "Bash":
        return 0

    cmd = _command(data).strip()
    if not cmd:
        return 0

    low = cmd.lower()

    if re.search(r"\bgit\s+push\b.*(-f|--force)\b", low):
        print("dealix guard_dealix_bash: blocked: git push --force", file=sys.stderr)
        return 2

    if "whatsapp_allow_live_send=true" in low.replace(" ", ""):
        print("dealix guard_dealix_bash: blocked: WHATSAPP_ALLOW_LIVE_SEND=true", file=sys.stderr)
        return 2

    if "rm" in low and "-rf" in low and "/" in cmd:
        # coarse guard against destructive rm -rf /
        if re.search(r"rm\s+(-[a-z]*f[a-z]*\s+|-\w*f\w*\s+).*/\s*$", low) or " rm -rf /" in low:
            print("dealix guard_dealix_bash: blocked: destructive rm pattern", file=sys.stderr)
            return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
