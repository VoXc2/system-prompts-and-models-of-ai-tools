"""
إشارات تطور ذاتي — تُستَمد من حالة المشروع الفعلية (إصدارات، AutoGen، Celery)، وليس من مصادر خارجية غير موثوقة.
تُحقَن في `self_improvement_flow` كمصدر `signals` لربط الحلقة بما يعمل فعلياً في الخادم.
"""

from __future__ import annotations

from typing import Any

from app.services.agent_framework_report import build_agent_framework_report


def collect_evolution_signals() -> dict[str, Any]:
    """لقطة خفيفة لطبقة الوكلاء — آمنة للسجلات (لا مفاتيح)."""
    r = build_agent_framework_report()
    return {
        "agent_framework_versions": r.get("packages"),
        "autogen_import_ok": r.get("autogen_import_ok"),
        "autogen_llm_ready": r.get("autogen_llm_ready"),
        "celery_import_ok": r.get("celery_import_ok"),
    }


def evolution_signals_for_flow() -> list[dict[str, Any]]:
    """صيغة مناسبة لحقل `signals` في SelfImprovementFlow."""
    return [
        {
            "source": "dealix_agent_framework_snapshot",
            "payload": collect_evolution_signals(),
        }
    ]
