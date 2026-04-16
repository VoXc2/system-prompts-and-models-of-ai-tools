"""Unified Sovereign Enterprise Growth OS API router."""

from fastapi import APIRouter

from app.api.v1.sovereign.planes import (
    data_router,
    decision_router,
    execution_router,
    operating_router,
    trust_router,
)
from app.api.v1.sovereign.readiness import readiness_router
from app.api.v1.sovereign.tracks import (
    executive_router,
    expansion_router,
    ma_router,
    partnership_router,
    pmi_router,
    revenue_router,
)

sovereign_router = APIRouter(prefix="/sovereign", tags=["Sovereign OS"])

sovereign_router.include_router(readiness_router)
sovereign_router.include_router(decision_router)
sovereign_router.include_router(execution_router)
sovereign_router.include_router(trust_router)
sovereign_router.include_router(data_router)
sovereign_router.include_router(operating_router)

sovereign_router.include_router(revenue_router)
sovereign_router.include_router(partnership_router)
sovereign_router.include_router(ma_router)
sovereign_router.include_router(expansion_router)
sovereign_router.include_router(pmi_router)
sovereign_router.include_router(executive_router)
