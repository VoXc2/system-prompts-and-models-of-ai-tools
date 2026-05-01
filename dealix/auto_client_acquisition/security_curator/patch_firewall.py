"""Block risky diffs before they reach git — text inspection only."""

from __future__ import annotations

import re
from typing import Any


def inspect_diff(diff_text: str) -> dict[str, Any]:
    """
    Returns ``allowed`` bool and ``reasons_ar`` list.
    MVP heuristics only — not a full patch parser.
    """
    reasons: list[str] = []
    if not diff_text or not diff_text.strip():
        return {"allowed": True, "reasons_ar": [], "detail": "empty_diff"}

    if re.search(r"^\+.*\.env", diff_text, re.MULTILINE) or re.search(r"^\+.*\.env\.", diff_text, re.MULTILINE):
        reasons.append("يحتوي على إضافة ملف بيئة (.env) — مرفوض في المسار الآلي.")

    if "ghp_" in diff_text or "github_pat_" in diff_text:
        reasons.append("فرق يحتوي على رمز GitHub — مرفوض.")

    if re.search(r"(?i)(supabase_service_role|openai_api_key|anthropic_api_key)\s*=", diff_text):
        reasons.append("فرق يحتوي على تعيين مفتاح حساس — راجع يدوياً.")

    lower = diff_text.lower()
    if ".pem" in lower and "begin" in lower and "private" in lower:
        reasons.append("مفتاح خاص (PEM) في الفرق — مرفوض.")

    return {
        "allowed": len(reasons) == 0,
        "reasons_ar": reasons,
        "detail": "heuristic_scan",
    }
