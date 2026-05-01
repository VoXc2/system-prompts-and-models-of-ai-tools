"""Objection extractor — find common Arabic + English buying objections in transcript."""

from __future__ import annotations

import re

# Each entry: (category, regex pattern (case-insensitive), Arabic gloss).
OBJECTION_PATTERNS: tuple[tuple[str, str, str], ...] = (
    ("price", r"غالي|مرتفع|الميزانية|expensive|too\s+pricey|cost", "السعر/الميزانية"),
    ("timing", r"ليس\s+الآن|بعد\s+شهر|الربع\s+القادم|not\s+now|next\s+quarter", "التوقيت"),
    ("authority", r"المدير|صاحب\s+القرار|need\s+approval|decision\s+maker", "صاحب القرار"),
    ("trust", r"بيانات|خصوصية|أمان|PDPL|trust|security|privacy", "الأمان والخصوصية"),
    ("integration", r"CRM|نظامنا|الربط|integration|migration", "التكامل/الترحيل"),
    ("competitor", r"نستخدم|بديل|أداة\s+ثانية|competitor|alternative", "وجود بديل/منافس"),
    ("results", r"نتائج|مضمون|guarantee|ROI|دليل", "إثبات النتائج"),
    ("complexity", r"معقد|صعب|تدريب|onboarding|complex|hard", "التعقيد/التبني"),
)


def extract_objections(transcript_text: str) -> dict[str, object]:
    """
    Extract objection categories from a free-text transcript.

    Returns:
        {
          "objections": [{"category", "label_ar", "snippet"}],
          "categories_found": [str],
          "count": int,
        }
    """
    if not transcript_text:
        return {"objections": [], "categories_found": [], "count": 0}

    found: list[dict[str, str]] = []
    seen_categories: set[str] = set()
    for cat, pattern, gloss in OBJECTION_PATTERNS:
        for m in re.finditer(pattern, transcript_text, flags=re.IGNORECASE):
            seen_categories.add(cat)
            start = max(0, m.start() - 40)
            end = min(len(transcript_text), m.end() + 40)
            snippet = transcript_text[start:end].replace("\n", " ").strip()
            found.append({
                "category": cat,
                "label_ar": gloss,
                "snippet": snippet[:200],
            })

    return {
        "objections": found,
        "categories_found": sorted(seen_categories),
        "count": len(found),
    }
