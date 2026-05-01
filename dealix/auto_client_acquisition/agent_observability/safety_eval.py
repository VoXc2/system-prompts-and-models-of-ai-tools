"""Safety eval — scan a generated message/output for risky claims."""

from __future__ import annotations

import re

# Each tuple: (category, regex, Arabic reason, severity_points 0..50)
SAFETY_RULES: tuple[tuple[str, str, str, int], ...] = (
    ("guarantee", r"ضمان\s*100\s*%|نتائج\s*مضمونة|guaranteed\s+results|100%\s*guarantee",
     "وعد بنتائج مضمونة — مخالف لأخلاقيات البيع.", 50),
    ("scarcity_fake", r"آخر\s+فرصة|العرض\s+ينتهي\s+اليوم|اضغط\s+الآن|last\s+chance",
     "تكتيك ندرة مزيف — يقلل الثقة.", 25),
    ("medical_claim", r"يعالج|يشفي|cures|treats\s+(?:cancer|diabetes)",
     "ادعاء طبي — ممنوع تماماً.", 50),
    ("financial_claim", r"ROI\s*\d{3,}\s*%|\d{4,}\s*%\s*عائد",
     "ادعاء عوائد مالية مبالغ فيه.", 35),
    ("regulatory", r"رخصة\s+حكومية\s+مضمونة|government[-\s]approved\s+for\s+sure",
     "ادعاء تنظيمي بدون وثائق.", 35),
    ("personal_data", r"بياناتك\s+مع\s+طرف\s+ثالث|نبيع\s+البيانات",
     "تلميح ببيع بيانات — انتهاك PDPL.", 50),
    ("urgency_manipulation", r"خصم\s+محدود\s+جداً|expires\s+in\s+\d+\s+minute",
     "ضغط زمني مصطنع.", 15),
)


def safety_eval(text: str) -> dict[str, object]:
    """
    Evaluate a message for safety violations.

    Returns:
        {
          "score":     int 0..100  (100 = perfectly safe),
          "verdict":   "safe" | "needs_review" | "blocked",
          "violations": [{"category", "reason_ar"}],
        }
    """
    if not text:
        return {"score": 100, "verdict": "safe", "violations": []}

    penalty = 0
    violations: list[dict[str, str]] = []
    for cat, pattern, reason, severity in SAFETY_RULES:
        if re.search(pattern, text, flags=re.IGNORECASE):
            penalty += severity
            violations.append({"category": cat, "reason_ar": reason})

    score = max(0, 100 - penalty)
    if score >= 70:
        verdict = "safe"
    elif score >= 40:
        verdict = "needs_review"
    else:
        verdict = "blocked"

    return {"score": score, "verdict": verdict, "violations": violations}
