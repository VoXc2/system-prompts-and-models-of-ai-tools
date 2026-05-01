"""
Lead scoring — heuristic now, sklearn-ready when >=200 labeled examples exist.
تسجيل العملاء المحتملين.
"""

from __future__ import annotations

import os
import pickle
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

MODEL_PATH = Path(os.getenv("LEAD_SCORER_MODEL", "/opt/dealix/models/lead_scorer.pkl"))


@dataclass
class LeadFeatures:
    company_size: int = 0  # employees
    budget_usd: float = 0.0
    urgency_score: float = 0.0  # 0-1 (from pain extractor)
    message_length: int = 0
    is_arabic: bool = False
    has_company_email: bool = False
    has_phone: bool = False
    pain_points_count: int = 0
    sector_fit: float = 0.0  # 0-1 ICP sector match

    def to_vector(self) -> list[float]:
        return [
            float(self.company_size),
            self.budget_usd,
            self.urgency_score,
            float(self.message_length),
            1.0 if self.is_arabic else 0.0,
            1.0 if self.has_company_email else 0.0,
            1.0 if self.has_phone else 0.0,
            float(self.pain_points_count),
            self.sector_fit,
        ]


@dataclass
class ScoreResult:
    score: float  # 0-1
    tier: str  # cold / warm / hot
    reasons: list[str] = field(default_factory=list)
    model: str = "heuristic"


def _heuristic_score(f: LeadFeatures) -> ScoreResult:
    score = 0.0
    reasons: list[str] = []

    if f.company_size >= 50:
        score += 0.20
        reasons.append("شركة بحجم مناسب")
    elif f.company_size >= 10:
        score += 0.10

    if f.budget_usd >= 10000:
        score += 0.25
        reasons.append("ميزانية جاهزة")
    elif f.budget_usd >= 2000:
        score += 0.12

    if f.urgency_score >= 0.7:
        score += 0.20
        reasons.append("احتياج عاجل")
    elif f.urgency_score >= 0.4:
        score += 0.10

    if f.has_company_email:
        score += 0.08
        reasons.append("إيميل شركة")
    if f.has_phone:
        score += 0.04
    if f.pain_points_count >= 2:
        score += 0.08
        reasons.append("نقاط ألم محددة")

    score += 0.15 * f.sector_fit
    if f.sector_fit >= 0.7:
        reasons.append("قطاع مستهدف")

    score = min(max(score, 0.0), 1.0)
    tier = "hot" if score >= 0.7 else "warm" if score >= 0.45 else "cold"
    return ScoreResult(score=round(score, 3), tier=tier, reasons=reasons, model="heuristic")


class LeadScorer:
    """
    Scores leads. Uses sklearn model when available at MODEL_PATH,
    otherwise falls back to a weighted-heuristic scorer.
    """

    def __init__(self) -> None:
        self._model: Any = None
        if MODEL_PATH.exists():
            try:
                with MODEL_PATH.open("rb") as f:
                    self._model = pickle.load(f)
            except Exception:
                self._model = None

    @property
    def mode(self) -> str:
        return "ml" if self._model is not None else "heuristic"

    def score(self, features: LeadFeatures) -> ScoreResult:
        if self._model is None:
            return _heuristic_score(features)
        try:
            proba = self._model.predict_proba([features.to_vector()])[0][1]
            score = float(proba)
            tier = "hot" if score >= 0.7 else "warm" if score >= 0.45 else "cold"
            return ScoreResult(
                score=round(score, 3), tier=tier, reasons=["ml_model"], model="sklearn"
            )
        except Exception:
            return _heuristic_score(features)
