"""Parse plain-text transcript lines into a short Arabic summary."""

from __future__ import annotations

import re
from typing import Any


def summarize_transcript_text(text: str) -> dict[str, Any]:
    lines = [ln.strip() for ln in (text or "").splitlines() if ln.strip()]
    bullets = lines[:5] if lines else ["لا يوجد نص كافٍ."]
    word_count = len(re.findall(r"\w+", text or "", flags=re.UNICODE))
    return {
        "bullets_ar": bullets,
        "word_count": word_count,
        "demo": True,
        "note_ar": "ملخص من نص خام — ربط Google Meet API لاحقاً مع OAuth.",
    }
