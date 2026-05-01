"""Transcript parser — accepts Google Meet entries OR plain text."""

from __future__ import annotations

import re
from typing import Any


def parse_transcript_entries(entries: list[dict[str, Any]] | str) -> dict[str, Any]:
    """
    Normalize either:
      - a list of Google-Meet-shaped entries [{"participantId", "text", ...}], or
      - a plain string transcript with "Speaker: text" lines.

    Returns:
        {
          "speaker_turns": [{"speaker", "text"}],
          "speakers":      [str],
          "total_chars":   int,
          "total_turns":   int,
        }
    """
    speaker_turns: list[dict[str, str]] = []

    if isinstance(entries, str):
        for raw in entries.splitlines():
            line = raw.strip()
            if not line:
                continue
            m = re.match(r"^([^:]{1,40}):\s*(.+)$", line)
            if m:
                speaker_turns.append({"speaker": m.group(1).strip(),
                                      "text": m.group(2).strip()})
            else:
                speaker_turns.append({"speaker": "?", "text": line})
    else:
        for e in entries or []:
            speaker = (
                e.get("participant")
                or e.get("participantId")
                or e.get("speaker")
                or "?"
            )
            text = e.get("text") or e.get("content") or ""
            text = str(text).strip()
            if not text:
                continue
            speaker_turns.append({"speaker": str(speaker), "text": text})

    speakers = sorted({t["speaker"] for t in speaker_turns})
    total_chars = sum(len(t["text"]) for t in speaker_turns)
    return {
        "speaker_turns": speaker_turns,
        "speakers": speakers,
        "total_chars": total_chars,
        "total_turns": len(speaker_turns),
    }


def summarize_meeting(parsed: dict[str, Any]) -> dict[str, Any]:
    """
    Produce an Arabic summary skeleton from parsed turns.

    Deterministic; LLM-free for Phase D MVP.
    """
    turns = parsed.get("speaker_turns", [])
    speakers = parsed.get("speakers", [])

    # Extract a few candidate "topic" sentences: longest turns.
    sorted_by_len = sorted(turns, key=lambda t: -len(t["text"]))[:5]
    topic_lines = [t["text"][:200] for t in sorted_by_len]

    # Detect questions.
    questions: list[str] = []
    for t in turns:
        text = t["text"]
        if "؟" in text or text.rstrip().endswith("?"):
            questions.append(text[:200])
        if len(questions) >= 5:
            break

    return {
        "summary_ar": [
            f"شارك في الاجتماع {len(speakers)} متحدث.",
            f"إجمالي عدد الأدوار الكلامية: {parsed.get('total_turns', 0)}.",
            "أبرز نقاط النقاش (مرشحة آلياً، تحتاج مراجعة):",
            *[f"• {line}" for line in topic_lines],
        ],
        "speakers": speakers,
        "candidate_questions_ar": questions,
        "approval_required": True,
    }
