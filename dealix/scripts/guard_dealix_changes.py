#!/usr/bin/env python3
"""Claude Code PreToolUse guard for file-writing tools. Reads JSON from stdin.

Exit 0: allow. Exit 2: block (stderr message). Unknown payload: allow (fail-open).
Run from repository root: python dealix/scripts/guard_dealix_changes.py
"""

from __future__ import annotations

import json
import sys


def _norm_path(s: str) -> str:
    s = (s or "").replace("\\", "/").strip()
    if not s:
        return ""
    # Normalize to forward slashes for substring checks
    return s.lower()


def _iter_paths(tool_input: object) -> list[str]:
    out: list[str] = []
    if not isinstance(tool_input, dict):
        return out
    for key in ("file_path", "path", "target_file", "file"):
        v = tool_input.get(key)
        if isinstance(v, str) and v.strip():
            out.append(v.strip())
    for key in ("file_paths", "paths", "files"):
        v = tool_input.get(key)
        if isinstance(v, list):
            for item in v:
                if isinstance(item, str) and item.strip():
                    out.append(item.strip())
                elif isinstance(item, dict):
                    out.extend(_iter_paths(item))
    # MultiEdit-style nested edits
    edits = tool_input.get("edits")
    if isinstance(edits, list):
        for e in edits:
            if isinstance(e, dict):
                out.extend(_iter_paths(e))
    return out


def _forbidden_path_reason(norm: str) -> str | None:
    if ".cursor/plans" in norm or norm.endswith("/.cursor/plans") or "/.cursor/plans/" in norm:
        return "blocked path: .cursor/plans"
    if not (norm.endswith(".env.example") or norm.endswith(".env.sample")):
        if norm.endswith(".env") or "/.env." in norm:
            return "blocked path: sensitive env file (.env*)"
    low = norm
    if "linkedin" in low and ("scrap" in low or "scrape" in low):
        return "blocked: LinkedIn scraping path/name signal"
    return None


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

    tool = str(data.get("tool_name") or "")
    if tool and tool not in {
        "Edit",
        "Write",
        "MultiEdit",
        "NotebookEdit",
        "StrReplace",
    }:
        # Only guard known file mutation tools; allow others
        if "edit" not in tool.lower() and "write" not in tool.lower():
            return 0

    paths = _iter_paths(data.get("tool_input"))
    if not paths:
        return 0

    for p in paths:
        n = _norm_path(p)
        reason = _forbidden_path_reason(n)
        if reason:
            print(f"dealix guard_dealix_changes: {reason}: {p}", file=sys.stderr)
            return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
