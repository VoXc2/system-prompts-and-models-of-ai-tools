"""Extract objection-like phrases from transcript text — keyword MVP."""

from __future__ import annotations

import re
from typing import Any

_KEYWORDS = ("ميزانية", "غالي", "لاحقاً", "نراجع", "ليس أولوية", "تكامل", "أمان", "عقد", "منافس")


def extract_objections(transcript_text: str) -> dict[str, Any]:
    text = transcript_text or ""
    found: list[str] = []
    for kw in _KEYWORDS:
        if re.search(re.escape(kw), text, flags=re.IGNORECASE):
            found.append(kw)
    return {"objections_ar": list(dict.fromkeys(found))[:8], "demo": True}
