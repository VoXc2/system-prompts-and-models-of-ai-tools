"""Sales/demo/onboarding outlines per service."""

from __future__ import annotations

from typing import Any

from auto_client_acquisition.service_tower.service_catalog import get_service_by_id


def build_service_launch_package(service_id: str) -> dict[str, Any]:
    svc = get_service_by_id(service_id) or {}
    return {
        "service_id": service_id,
        "name_ar": svc.get("name_ar"),
        "landing_outline_ar": ["الوعد", "لمن؟", "ماذا تحصل؟", "CTA", "تحذير: لا نتائج مضمونة"],
        "demo_script_ar": ["افتح التشخيص", "اعرض الكروت", "أظهر الموافقة", "أغلق بـ Proof"],
        "onboarding_checklist_ar": ["جمع المدخلات", "تشغيل wizard", "تفعيل مسودات فقط"],
        "demo": True,
    }


def build_landing_page_outline(service_id: str) -> dict[str, Any]:
    return {"service_id": service_id, "sections": build_service_launch_package(service_id).get("landing_outline_ar"), "demo": True}


def build_sales_script(service_id: str) -> dict[str, Any]:
    return {
        "service_id": service_id,
        "script_ar": (
            f"نقدّم {service_id}: نعمل مسودات وموافقات، "
            "ولا نرسل أو نخصم دون قرارك. نثبت القيمة عبر Proof Pack."
        ),
        "demo": True,
    }


def build_demo_script(service_id: str) -> dict[str, Any]:
    return build_sales_script(service_id)


def build_onboarding_checklist(service_id: str) -> dict[str, Any]:
    return {
        "service_id": service_id,
        "checklist_ar": build_service_launch_package(service_id).get("onboarding_checklist_ar"),
        "demo": True,
    }
