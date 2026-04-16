"""Sovereign OS — readiness, surfaces, compliance, and operational dashboards."""

from __future__ import annotations

import asyncio

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.api.v1.sovereign.tenant import TenantIdQuery
from app.sovereign.compliance_sa.engine import ComplianceMatrix, SaudiComplianceEngine
from app.sovereign.constants import REQUIRED_SURFACES, SOVEREIGNTY_READINESS_CRITERIA
from app.sovereign.contradiction.engine import ContradictionDashboard, ContradictionEngine
from app.sovereign.program_locks.manager import ProgramLockManager, ReadinessReport
from app.sovereign.routing.fabric import RoutingDashboard, SovereignRoutingFabric
from app.sovereign.schemas import ProgramLock

readiness_router = APIRouter(tags=["Sovereign — Readiness"])

_program_lock_manager = ProgramLockManager()
_compliance_engine = SaudiComplianceEngine()
_routing_fabric = SovereignRoutingFabric()
_contradiction_engine = ContradictionEngine()


class SovereignReadinessCriterion(BaseModel):
    """One readiness criterion with bilingual labels and pass/fail."""

    id: int
    passed: bool
    label_en: str
    label_ar: str
    detail_en: str
    detail_ar: str


class SovereignReadinessResponse(BaseModel):
    tenant_id: str
    all_passed: bool
    criteria: list[SovereignReadinessCriterion]


class SovereignSurfaceItem(BaseModel):
    name_en: str
    name_ar: str


class SovereignSurfacesResponse(BaseModel):
    tenant_id: str
    count: int = Field(description="Must be 18 sovereign surfaces")
    surfaces: list[SovereignSurfaceItem]


def _build_readiness_from_constants_and_report(report: ReadinessReport) -> SovereignReadinessResponse:
    criteria_out: list[SovereignReadinessCriterion] = []
    for i, (full_text, rc) in enumerate(zip(SOVEREIGNTY_READINESS_CRITERIA, report.criteria, strict=True)):
        en_part, _, ar_part = full_text.partition("(")
        label_en = en_part.strip()
        label_ar = ar_part.rstrip(")").strip() if ar_part else label_en
        criteria_out.append(
            SovereignReadinessCriterion(
                id=i + 1,
                passed=rc.satisfied,
                label_en=label_en,
                label_ar=label_ar,
                detail_en=rc.detail_en,
                detail_ar=rc.detail_ar,
            ),
        )
    return SovereignReadinessResponse(
        tenant_id="",
        all_passed=report.all_satisfied,
        criteria=criteria_out,
    )


@readiness_router.get(
    "/readiness",
    response_model=SovereignReadinessResponse,
    summary="Full readiness check (8 criteria)",
)
async def sovereign_readiness(tenant_id: TenantIdQuery) -> SovereignReadinessResponse:
    try:
        report = await asyncio.to_thread(_program_lock_manager.check_readiness)
        body = _build_readiness_from_constants_and_report(report)
        body.tenant_id = tenant_id
        return body
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message_en": "Readiness check failed.",
                "message_ar": "فشل فحص الجاهزية.",
                "error": str(exc),
            },
        ) from exc


@readiness_router.get(
    "/surfaces",
    response_model=SovereignSurfacesResponse,
    summary="Required sovereign surfaces (18)",
)
async def sovereign_surfaces(tenant_id: TenantIdQuery) -> SovereignSurfacesResponse:
    surfaces = [SovereignSurfaceItem(name_en=en, name_ar=ar) for en, ar in REQUIRED_SURFACES]
    if len(surfaces) != 18:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message_en": "Surface catalog is misconfigured.",
                "message_ar": "كتالوج الأسطح غير مهيأ بشكل صحيح.",
            },
        )
    return SovereignSurfacesResponse(tenant_id=tenant_id, count=len(surfaces), surfaces=surfaces)


@readiness_router.get(
    "/program-lock",
    response_model=ProgramLock,
    summary="Current program lock",
)
async def sovereign_program_lock(tenant_id: TenantIdQuery) -> ProgramLock:
    try:
        return await asyncio.to_thread(_program_lock_manager.get_current_lock)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message_en": "Program lock lookup failed.",
                "message_ar": "فشل جلب قفل البرنامج.",
                "error": str(exc),
            },
        ) from exc


@readiness_router.get(
    "/compliance-matrix",
    response_model=ComplianceMatrix,
    summary="Saudi compliance matrix",
)
async def sovereign_compliance_matrix(tenant_id: TenantIdQuery) -> ComplianceMatrix:
    try:
        return await asyncio.to_thread(_compliance_engine.get_compliance_matrix, tenant_id)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message_en": "Compliance matrix failed.",
                "message_ar": "فشل جلب مصفوفة الامتثال.",
                "error": str(exc),
            },
        ) from exc


@readiness_router.get(
    "/routing-dashboard",
    response_model=RoutingDashboard,
    summary="Model routing dashboard",
)
async def sovereign_routing_dashboard(tenant_id: TenantIdQuery) -> RoutingDashboard:
    try:
        return await asyncio.to_thread(_routing_fabric.get_routing_dashboard)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message_en": "Routing dashboard failed.",
                "message_ar": "فشل جلب لوحة توجيه النماذج.",
                "error": str(exc),
            },
        ) from exc


@readiness_router.get(
    "/contradiction-dashboard",
    response_model=ContradictionDashboard,
    summary="Contradiction dashboard",
)
async def sovereign_contradiction_dashboard(
    tenant_id: TenantIdQuery,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> ContradictionDashboard:
    try:
        return await asyncio.to_thread(_contradiction_engine.get_dashboard, tenant_id, limit, offset)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message_en": "Contradiction dashboard failed.",
                "message_ar": "فشل جلب لوحة التناقضات.",
                "error": str(exc),
            },
        ) from exc
