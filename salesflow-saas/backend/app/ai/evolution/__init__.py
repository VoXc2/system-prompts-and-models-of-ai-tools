"""تطور ذاتي مبني على إشارات داخلية (إصدارات، جاهزية AutoGen/Celery)."""

from app.ai.evolution.signals import collect_evolution_signals, evolution_signals_for_flow

__all__ = ["collect_evolution_signals", "evolution_signals_for_flow"]
