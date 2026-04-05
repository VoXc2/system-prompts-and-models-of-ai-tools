"""
تقرير غير حسّاس عن مكتبات الوكلاء والأتمتة المثبّتة — للمراقبة ولوحات التشغيل.
"""

from __future__ import annotations

import importlib.metadata
import sys
from typing import Any


def _safe_version(dist_name: str) -> str | None:
    try:
        return importlib.metadata.version(dist_name)
    except importlib.metadata.PackageNotFoundError:
        return None


def build_agent_framework_report() -> dict[str, Any]:
    """نسخة JSON آمنة للنشر (بدون مفاتيح API)."""
    packages = {
        "langgraph": _safe_version("langgraph"),
        "langchain": _safe_version("langchain"),
        "langchain_community": _safe_version("langchain-community"),
        "crewai": _safe_version("crewai"),
        "groq": _safe_version("groq"),
        "openai": _safe_version("openai"),
        "mem0ai": _safe_version("mem0ai"),
        "instructor": _safe_version("instructor"),
        "autogen_agentchat": _safe_version("autogen-agentchat"),
        "autogen_ext": _safe_version("autogen-ext"),
        "structlog": _safe_version("structlog"),
    }
    report: dict[str, Any] = {
        "python": sys.version.split()[0],
        "packages": packages,
        "autogen_import_ok": False,
        "autogen_llm_ready": False,
        "celery_import_ok": False,
    }
    try:
        from app.ai.autogen.factory import dealix_autogen_openai_client, is_autogen_available

        report["autogen_import_ok"] = is_autogen_available()
        if report["autogen_import_ok"]:
            client = dealix_autogen_openai_client()
            report["autogen_llm_ready"] = client is not None
    except Exception as exc:  # noqa: BLE001
        report["autogen_note"] = str(exc)[:240]

    try:
        from app.workers.celery_app import app as _celery  # noqa: F401

        report["celery_import_ok"] = True
    except Exception:
        report["celery_import_ok"] = False

    return report
