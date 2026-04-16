"""Saudi Compliance Matrix API — PDPL, NCA ECC 2024, NIST AI RMF, OWASP LLM mapping."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models.sovereign import SaudiComplianceControl

router = APIRouter(prefix="/saudi-compliance", tags=["Saudi Compliance Matrix — مصفوفة الامتثال السعودي"])


# ─── Pre-seeded compliance controls ──────────────────────────────

COMPLIANCE_SEED: list[dict] = [
    # PDPL
    {
        "framework": "PDPL",
        "control_ref": "PDPL.Art.5",
        "title_ar": "مبادئ معالجة البيانات الشخصية",
        "title_en": "Personal Data Processing Principles",
        "description_ar": "يجب أن تكون المعالجة مشروعة وعادلة وشفافة ومحدودة بالغرض",
        "risk_category": "data_processing",
        "risk_level": "critical",
        "penalty_notes_ar": "غرامة تصل إلى 5 مليون ريال سعودي لكل انتهاك",
    },
    {
        "framework": "PDPL",
        "control_ref": "PDPL.Art.12",
        "title_ar": "الموافقة على معالجة البيانات",
        "title_en": "Consent for Data Processing",
        "description_ar": "يجب الحصول على موافقة صريحة قبل أي معالجة",
        "risk_category": "consent",
        "risk_level": "critical",
        "penalty_notes_ar": "غرامة تصل إلى 5 مليون ريال",
    },
    {
        "framework": "PDPL",
        "control_ref": "PDPL.Art.16",
        "title_ar": "نقل البيانات خارج المملكة",
        "title_en": "Cross-border Data Transfer",
        "description_ar": "يتطلب ضمانات مناسبة لنقل البيانات إلى دول أخرى",
        "risk_category": "data_transfer",
        "risk_level": "high",
    },
    # NCA ECC 2024
    {
        "framework": "NCA_ECC_2024",
        "control_ref": "ECC.2-2024.Ctrl.1",
        "title_ar": "إدارة هوية المستخدمين والصلاحيات",
        "title_en": "Identity and Access Management",
        "description_ar": "يجب تطبيق مبدأ أقل الامتيازات في جميع الأنظمة",
        "risk_category": "access_control",
        "risk_level": "high",
    },
    {
        "framework": "NCA_ECC_2024",
        "control_ref": "ECC.2-2024.Ctrl.5",
        "title_ar": "أمن الذكاء الاصطناعي",
        "title_en": "AI Systems Security",
        "description_ar": "تطبيق ضوابط أمنية على أنظمة الذكاء الاصطناعي والنماذج اللغوية",
        "risk_category": "ai_security",
        "risk_level": "critical",
    },
    # NIST AI RMF
    {
        "framework": "NIST_AI_RMF",
        "control_ref": "NIST.GOVERN.1.1",
        "title_ar": "سياسات وإجراءات حوكمة الذكاء الاصطناعي",
        "title_en": "AI Governance Policies and Procedures",
        "description_ar": "يجب توثيق سياسات المخاطر وآليات الاعتماد البشري",
        "risk_category": "ai_governance",
        "risk_level": "high",
    },
    {
        "framework": "NIST_AI_RMF",
        "control_ref": "NIST.MAP.1.5",
        "title_ar": "تحديد سياق استخدام الذكاء الاصطناعي",
        "title_en": "AI Use Context Identification",
        "description_ar": "تحديد السياق التشغيلي ومتطلبات القرارات الحرجة",
        "risk_category": "risk_mapping",
        "risk_level": "medium",
    },
    # OWASP LLM Top 10
    {
        "framework": "OWASP_LLM_TOP10",
        "control_ref": "OWASP.LLM01",
        "title_ar": "حقن التعليمات (Prompt Injection)",
        "title_en": "Prompt Injection Prevention",
        "description_ar": "تطبيق ضوابط للحد من هجمات حقن التعليمات في النماذج اللغوية",
        "risk_category": "prompt_security",
        "risk_level": "critical",
    },
    {
        "framework": "OWASP_LLM_TOP10",
        "control_ref": "OWASP.LLM06",
        "title_ar": "الإفصاح عن المعلومات الحساسة",
        "title_en": "Sensitive Information Disclosure",
        "description_ar": "منع النماذج من الإفصاح عن بيانات حساسة أو سرية",
        "risk_category": "data_security",
        "risk_level": "high",
    },
]


class ControlUpdate(BaseModel):
    implementation_status: str
    platform_control_mapping: list[dict] | None = None
    evidence_ref: list[dict] | None = None


@router.get("/controls")
async def list_controls(
    tenant_id: str,
    framework: str | None = None,
    implementation_status: str | None = None,
    risk_level: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    """مصفوفة الامتثال السعودي — Saudi compliance matrix."""
    q = select(SaudiComplianceControl).where(SaudiComplianceControl.tenant_id == tenant_id)
    if framework:
        q = q.where(SaudiComplianceControl.framework == framework)
    if implementation_status:
        q = q.where(SaudiComplianceControl.implementation_status == implementation_status)
    if risk_level:
        q = q.where(SaudiComplianceControl.risk_level == risk_level)
    q = q.order_by(SaudiComplianceControl.framework, SaudiComplianceControl.control_ref)
    result = await db.execute(q)
    rows = result.scalars().all()
    return [_control_to_dict(r) for r in rows]


@router.post("/controls/seed", status_code=status.HTTP_201_CREATED)
async def seed_controls(
    tenant_id: str,
    created_by_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """بذر ضوابط الامتثال — Seed compliance controls from built-in catalog."""
    created = 0
    for item in COMPLIANCE_SEED:
        existing = await db.execute(
            select(SaudiComplianceControl).where(
                SaudiComplianceControl.tenant_id == tenant_id,
                SaudiComplianceControl.framework == item["framework"],
                SaudiComplianceControl.control_ref == item["control_ref"],
            )
        )
        if not existing.scalar_one_or_none():
            ctrl = SaudiComplianceControl(
                tenant_id=tenant_id,
                verified_by_id=created_by_id,
                **item,
            )
            db.add(ctrl)
            created += 1
    await db.commit()
    return {"controls_seeded": created, "total_in_catalog": len(COMPLIANCE_SEED)}


@router.patch("/controls/{control_id}")
async def update_control(
    control_id: str,
    tenant_id: str,
    reviewer_id: str,
    payload: ControlUpdate,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    result = await db.execute(
        select(SaudiComplianceControl).where(
            SaudiComplianceControl.id == control_id,
            SaudiComplianceControl.tenant_id == tenant_id,
        )
    )
    ctrl = result.scalar_one_or_none()
    if not ctrl:
        raise HTTPException(status_code=404, detail="Control not found")
    ctrl.implementation_status = payload.implementation_status
    if payload.platform_control_mapping:
        ctrl.platform_control_mapping = payload.platform_control_mapping
    if payload.evidence_ref:
        ctrl.evidence_ref = payload.evidence_ref
    ctrl.last_verified_at = datetime.now()
    ctrl.verified_by_id = reviewer_id
    await db.commit()
    return {"id": control_id, "implementation_status": ctrl.implementation_status}


@router.get("/summary")
async def compliance_summary(
    tenant_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """ملخص الامتثال — Overall compliance posture summary."""
    total_result = await db.execute(
        select(func.count(SaudiComplianceControl.id)).where(
            SaudiComplianceControl.tenant_id == tenant_id
        )
    )
    total = total_result.scalar() or 0

    implemented_result = await db.execute(
        select(func.count(SaudiComplianceControl.id)).where(
            SaudiComplianceControl.tenant_id == tenant_id,
            SaudiComplianceControl.implementation_status == "implemented",
        )
    )
    implemented = implemented_result.scalar() or 0

    critical_not_done = await db.execute(
        select(func.count(SaudiComplianceControl.id)).where(
            SaudiComplianceControl.tenant_id == tenant_id,
            SaudiComplianceControl.risk_level == "critical",
            SaudiComplianceControl.implementation_status != "implemented",
            SaudiComplianceControl.implementation_status != "not_applicable",
        )
    )
    critical_gap = critical_not_done.scalar() or 0

    return {
        "label_ar": "مصفوفة الامتثال السعودي",
        "total_controls": total,
        "implemented": implemented,
        "compliance_pct": round((implemented / total * 100) if total > 0 else 0, 1),
        "critical_gaps": critical_gap,
        "frameworks": ["PDPL", "NCA_ECC_2024", "NIST_AI_RMF", "OWASP_LLM_TOP10"],
    }


def _control_to_dict(r: SaudiComplianceControl) -> dict[str, Any]:
    return {
        "id": str(r.id),
        "framework": r.framework,
        "control_ref": r.control_ref,
        "title_ar": r.title_ar,
        "title_en": r.title_en,
        "description_ar": r.description_ar,
        "risk_category": r.risk_category,
        "implementation_status": r.implementation_status,
        "risk_level": r.risk_level,
        "platform_control_mapping": r.platform_control_mapping,
        "evidence_ref": r.evidence_ref,
        "last_verified_at": r.last_verified_at.isoformat() if r.last_verified_at else None,
        "penalty_notes_ar": r.penalty_notes_ar,
    }
