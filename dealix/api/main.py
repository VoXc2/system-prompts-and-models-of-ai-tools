"""
FastAPI application entry point.
نقطة دخول تطبيق FastAPI.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.middleware import RequestIDMiddleware
from api.routers import (
    admin,
    agent_observability,
    agents,
    automation,
    autonomous,
    business,
    command_center,
    connector_catalog,
    customer_success,
    data,
    dominance,
    drafts,
    ecosystem,
    email_send,
    full_os,
    growth_curator,
    growth_operator,
    health,
    innovation,
    intelligence_layer,
    leads,
    meeting_intelligence,
    model_router,
    outreach,
    personal_operator,
    platform_services,
    pricing,
    prospect,
    public,
    revenue,
    revenue_os,
    sales,
    sectors,
    security_curator,
    v3,
    webhooks,
)
from api.security import APIKeyMiddleware, setup_rate_limit
from core.config.settings import get_settings
from core.errors import AICompanyError
from core.logging import configure_logging, get_logger


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """App startup/shutdown hook."""
    configure_logging()
    log = get_logger(__name__)
    settings = get_settings()
    log.info(
        "app_startup",
        app=settings.app_name,
        version=settings.app_version,
        env=settings.app_env,
    )
    # Auto-create tables on boot (additive — safe with SQLAlchemy create_all)
    try:
        from db.session import init_db
        await init_db()
        log.info("db_init_complete")
    except Exception as exc:
        log.warning("db_init_skipped", error=str(exc))
    yield
    log.info("app_shutdown")


def create_app() -> FastAPI:
    """FastAPI factory."""
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "Multi-agent AI platform for the Saudi Arabian market.\n\n"
            "**Phase 8**: Auto Client Acquisition — intake, ICP match, "
            "pain extraction, qualification, CRM sync, booking, proposals.\n\n"
            "**Phase 9**: Autonomous Growth — sector intel, content, distribution, "
            "enrichment, competitor analysis, market research.\n\n"
            "**Phase 10 / v3**: Autonomous Saudi Revenue OS — revenue memory, "
            "safe agent runtime, market radar, compliance OS, revenue science, "
            "and Sami Personal Strategic Operator."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(APIKeyMiddleware)
    setup_rate_limit(app)

    try:
        from dealix.observability import instrument_fastapi, setup_sentry, setup_tracing

        setup_sentry()
        setup_tracing(service_name=settings.app_name, version=settings.app_version)
        instrument_fastapi(app)
    except Exception:  # pragma: no cover
        pass

    @app.exception_handler(AICompanyError)
    async def ai_company_error_handler(_: Request, exc: AICompanyError) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content={"error": exc.__class__.__name__, "detail": str(exc)},
        )

    app.include_router(health.router)
    app.include_router(leads.router)
    app.include_router(sales.router)
    app.include_router(sectors.router)
    app.include_router(agents.router)
    app.include_router(webhooks.router)
    app.include_router(pricing.router)
    app.include_router(prospect.router)
    app.include_router(autonomous.router)
    app.include_router(data.router)
    app.include_router(outreach.router)
    app.include_router(revenue.router)
    app.include_router(automation.router)
    app.include_router(email_send.router)
    app.include_router(drafts.router)
    app.include_router(dominance.router)
    app.include_router(full_os.router)
    app.include_router(customer_success.router)
    app.include_router(ecosystem.router)
    app.include_router(command_center.router)
    app.include_router(revenue_os.router)
    app.include_router(v3.router)
    app.include_router(innovation.router)
    app.include_router(business.router)
    app.include_router(personal_operator.router)
    app.include_router(growth_operator.router)
    app.include_router(platform_services.router)
    app.include_router(intelligence_layer.router)
    app.include_router(security_curator.router)
    app.include_router(growth_curator.router)
    app.include_router(meeting_intelligence.router)
    app.include_router(model_router.router)
    app.include_router(connector_catalog.router)
    app.include_router(agent_observability.router)
    app.include_router(public.router)
    app.include_router(admin.router)

    @app.get("/", tags=["root"])
    async def root() -> dict[str, object]:
        return {
            "name": settings.app_name,
            "version": settings.app_version,
            "status": "operational",
            "env": settings.app_env,
            "docs": "/docs",
            "health": "/health",
            "v3_command_center": "/api/v1/v3/command-center/snapshot",
            "personal_operator_daily_brief": "/api/v1/personal-operator/daily-brief",
            "personal_operator_launch_report": "/api/v1/personal-operator/launch-report",
            "business_pricing": "/api/v1/business/pricing",
            "innovation_command_feed_demo": "/api/v1/innovation/command-feed/demo",
        }

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "api.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.is_development,
    )
