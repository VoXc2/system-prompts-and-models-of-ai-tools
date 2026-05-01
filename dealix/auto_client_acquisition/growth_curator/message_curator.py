"""Message Curator — grade Arabic outreach messages, dedupe, suggest fixes."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from difflib import SequenceMatcher

# Risky/forbidden Arabic phrases — heavy promises, urgency manipulation.
RISKY_PHRASES_AR: tuple[str, ...] = (
    "ضمان 100%",
    "نتائج مضمونة",
    "آخر فرصة",
    "العرض ينتهي اليوم",
    "خصم محدود جداً",
    "لن تجد مثله",
    "صفقة العمر",
    "اضغط الآن",
)

# Required signals for a "Saudi natural tone" message.
REQUIRED_SIGNALS_AR: tuple[str, ...] = (
    # Greeting
    "هلا|أهلاً|السلام عليكم|مرحبا|مساء الخير|صباح الخير",
    # Reason for contacting
    "لاحظت|شفت|رأيت|متابع|قرأت|تابعت|اطلعت",
    # Soft CTA
    "يناسبك|تحب|ممكن|إذا فيه وقت|تفتح|تجربة|تواصل|نتقابل",
)


@dataclass(frozen=True)
class MessageGrade:
    """Result of grading a single Arabic message."""
    score: int            # 0..100
    verdict: str          # "publish" | "needs_edit" | "reject"
    reasons_ar: list[str] = field(default_factory=list)
    suggestions_ar: list[str] = field(default_factory=list)
    risky_phrases: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {
            "score": self.score,
            "verdict": self.verdict,
            "reasons_ar": self.reasons_ar,
            "suggestions_ar": self.suggestions_ar,
            "risky_phrases": self.risky_phrases,
        }


def _has_arabic(text: str) -> bool:
    return any("؀" <= ch <= "ۿ" for ch in text)


def _word_count(text: str) -> int:
    return len([w for w in re.split(r"\s+", text.strip()) if w])


def _matches_signal(text: str, alternatives: str) -> bool:
    pat = "|".join(re.escape(a) for a in alternatives.split("|"))
    return re.search(pat, text) is not None


def grade_message(
    message: str,
    *,
    sector: str | None = None,
    channel: str = "whatsapp",
) -> MessageGrade:
    """
    Grade a single Arabic message.

    Returns MessageGrade with score 0..100 and a verdict.
    """
    reasons: list[str] = []
    suggestions: list[str] = []
    risky: list[str] = [p for p in RISKY_PHRASES_AR if p in message]

    score = 100

    # 1. Must contain Arabic.
    if not _has_arabic(message):
        score -= 60
        reasons.append("الرسالة لا تحتوي محتوى عربي.")
        suggestions.append("أعد صياغة الرسالة بالعربي بأسلوب طبيعي سعودي.")

    # 2. Length sanity.
    wc = _word_count(message)
    if wc < 12:
        score -= 15
        reasons.append("الرسالة قصيرة جداً ولا توضح السبب أو القيمة.")
        suggestions.append("أضف سبب التواصل + سؤال مفتوح قصير.")
    elif wc > 80:
        score -= 15
        reasons.append("الرسالة طويلة جداً للعرض الأول.")
        suggestions.append("اختصر إلى 4-6 أسطر.")

    # 3. Risky phrases.
    if risky:
        score -= 25 * min(len(risky), 2)
        reasons.append(f"عبارات عالية المخاطرة: {', '.join(risky)}")
        suggestions.append("استبدل العبارات المضللة بأمثلة محددة وأرقام واقعية.")

    # 4. Saudi tone signals (greeting + reason + soft CTA).
    missing_signals = []
    for sig in REQUIRED_SIGNALS_AR:
        if not _matches_signal(message, sig):
            missing_signals.append(sig.split("|")[0])
    if missing_signals:
        score -= 8 * len(missing_signals)
        reasons.append(
            f"تنقصها إشارات أسلوب طبيعي: {', '.join(missing_signals)}"
        )
        suggestions.append("ابدأ بتحية + لاحظت/شفت + سؤال يناسبك.")

    # 5. WhatsApp-specific: avoid bulk markers.
    if channel == "whatsapp" and re.search(r"\bعميل عزيز\b|\bلجميع العملاء\b", message):
        score -= 10
        reasons.append("الرسالة بنبرة جماعية لا تناسب واتساب الشخصي.")
        suggestions.append("استخدم اسم الشخص أو شركته بدل النداء العام.")

    # 6. Sector hook — soft bonus if sector is mentioned.
    if sector and sector.lower() in message.lower():
        score = min(100, score + 5)

    score = max(0, min(100, score))
    if score >= 75 and not risky:
        verdict = "publish"
    elif score >= 50:
        verdict = "needs_edit"
    else:
        verdict = "reject"

    return MessageGrade(
        score=score, verdict=verdict,
        reasons_ar=reasons, suggestions_ar=suggestions,
        risky_phrases=risky,
    )


def detect_duplicates(messages: list[str], *, threshold: float = 0.85) -> list[tuple[int, int, float]]:
    """
    Return pairs (i, j, ratio) of near-duplicate messages.

    Uses SequenceMatcher; deterministic, no external deps.
    """
    pairs: list[tuple[int, int, float]] = []
    n = len(messages)
    for i in range(n):
        for j in range(i + 1, n):
            ratio = SequenceMatcher(None, messages[i], messages[j]).ratio()
            if ratio >= threshold:
                pairs.append((i, j, round(ratio, 3)))
    return pairs


def suggest_improvement(message: str, *, sector: str | None = None) -> dict[str, object]:
    """Return a structured improvement suggestion (deterministic, no LLM)."""
    grade = grade_message(message, sector=sector)
    template = (
        "هلا [الاسم]، لاحظت [إشارة محددة عن شركتك/قطاعك]. "
        "أعمل على [وصف العرض في جملة واحدة]. "
        "يناسبك أعرض لك مثال خفيف 10 دقائق هذا الأسبوع؟"
    )
    return {
        "current": message,
        "grade": grade.to_dict(),
        "suggested_skeleton_ar": template,
    }


def archive_low_quality(
    messages: list[dict[str, object]],
    *,
    score_field: str = "score",
    threshold: int = 50,
) -> dict[str, list[dict[str, object]]]:
    """
    Split a list of {message, score} into (active, archived) by threshold.
    """
    active: list[dict[str, object]] = []
    archived: list[dict[str, object]] = []
    for m in messages:
        score = int(m.get(score_field, 0) or 0)
        if score < threshold:
            archived.append(m)
        else:
            active.append(m)
    return {"active": active, "archived": archived}
