import os

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime, timezone
from pydantic import BaseModel as Schema

from app.database import get_db
from app.config import get_settings
from app.services.agent_framework_report import build_agent_framework_report

router = APIRouter()
_settings = get_settings()


class HealthResponse(Schema):
    status: str
    timestamp: str
    version: str = "2.0.0"
    app: str = "Dealix"
    environment: str = "production"
    git_sha: str | None = None


class ReadyResponse(Schema):
    status: str
    database: str
    redis: str | None = None
    timestamp: str


class DeploymentReadinessResponse(Schema):
    """مؤشرات غير حسّاسة — لمعرفة ما إذا كان النظام جاهزاً لخدمة حقيقية."""
    timestamp: str
    environment: str
    demo_mode: bool
    secret_key_configured: bool
    database_url_not_default_credential: bool
    llm_ready: bool
    whatsapp_live: bool
    maps_or_places_ready: bool
    stripe_ready: bool
    lead_intelligence_ready: bool
    score_percent: int
    gaps_ar: list[str]


async def _redis_ping_status() -> str:
    """Best-effort broker/cache check (Celery uses REDIS_URL)."""
    url = _settings.REDIS_URL
    if not url:
        return "skipped"
    client = None
    try:
        import redis.asyncio as aioredis

        client = aioredis.from_url(url, socket_connect_timeout=1.5)
        await client.ping()
        return "connected"
    except Exception:
        return "unavailable"
    finally:
        if client is not None:
            try:
                await client.aclose()
            except Exception:
                pass


def _git_sha() -> str | None:
    s = (os.environ.get("DEALIX_GIT_SHA") or os.environ.get("GIT_COMMIT") or os.environ.get("VERCEL_GIT_COMMIT_SHA") or "").strip()
    return s[:40] if s else None


@router.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(timezone.utc).isoformat(),
        version="2.0.0",
        app=_settings.APP_NAME,
        environment=_settings.ENVIRONMENT,
        git_sha=_git_sha(),
    )


def _deployment_readiness_payload() -> DeploymentReadinessResponse:
    s = get_settings()
    default_secret = "change-this-to-a-random-secret-key"
    secret_ok = bool(s.SECRET_KEY and s.SECRET_KEY.strip() and s.SECRET_KEY != default_secret)
    db_ok = "salesflow_secret_2024" not in (s.DATABASE_URL or "")
    llm = bool((s.GROQ_API_KEY or "").strip() or (s.OPENAI_API_KEY or "").strip())
    wa_live = (not getattr(s, "WHATSAPP_MOCK_MODE", True)) and bool((s.WHATSAPP_API_TOKEN or "").strip())
    maps_ok = bool((s.GOOGLE_MAPS_API_KEY or s.GOOGLE_API_KEY or "").strip())
    stripe_ok = bool((s.STRIPE_SECRET_KEY or "").strip())
    lead_ok = bool((s.SERPAPI_KEY or "").strip()) or maps_ok

    checks = [secret_ok, db_ok, llm, wa_live, maps_ok, stripe_ok, lead_ok]
    score = int(round(100 * sum(1 for c in checks if c) / max(len(checks), 1)))

    gaps: list[str] = []
    if not secret_ok:
        gaps.append("SECRET_KEY ما زال القيمة الافتراضية — خطر أمني في الإنتاج.")
    if not db_ok:
        gaps.append("DATABASE_URL يستخدم كلمة مرور افتراضية معروفة — غيّرها قبل الإنتاج.")
    if not llm:
        gaps.append("فعّل GROQ_API_KEY أو OPENAI_API_KEY لتشغيل الذكاء في المسارات.")
    if not wa_live:
        gaps.append("واتساب في وضع تجريبي — عطّل WHATSAPP_MOCK_MODE واضبط رموز Meta للإرسال الحقيقي.")
    if not maps_ok:
        gaps.append("لا مفتاح Google للخرائط/الأماكن — توليد الليدات الجغرافي ضعيف.")
    if not stripe_ok:
        gaps.append("لا Stripe — الفوترة والدفع الآلي غير مفعّلين.")
    if not lead_ok:
        gaps.append("محرك الليدات محدود — أضف SERPAPI_KEY أو تأكد من مفتاح الأماكن.")

    return DeploymentReadinessResponse(
        timestamp=datetime.now(timezone.utc).isoformat(),
        environment=s.ENVIRONMENT,
        demo_mode=getattr(s, "DEALIX_DEMO_MODE", True),
        secret_key_configured=secret_ok,
        database_url_not_default_credential=db_ok,
        llm_ready=llm,
        whatsapp_live=wa_live,
        maps_or_places_ready=maps_ok,
        stripe_ready=stripe_ok,
        lead_intelligence_ready=lead_ok,
        score_percent=score,
        gaps_ar=gaps,
    )


@router.get("/deployment-readiness", response_model=DeploymentReadinessResponse)
async def deployment_readiness():
    """فحص جاهزية الخدمة الحقيقية — بدون كشف أسرار."""
    return _deployment_readiness_payload()


@router.get("/agent-frameworks")
async def agent_frameworks():
    """إصدارات مكتبات الوكلاء والأتمتة (LangGraph، CrewAI، AutoGen، …) — بدون أسرار."""
    return build_agent_framework_report()


@router.get("/ready", response_model=ReadyResponse)
async def readiness_check(db: AsyncSession = Depends(get_db)):
    db_status = "connected"
    try:
        await db.execute(text("SELECT 1"))
    except Exception:
        db_status = "unavailable"

    redis_status = await _redis_ping_status()
    overall = "ready" if db_status == "connected" else "not_ready"
    return ReadyResponse(
        status=overall,
        database=db_status,
        redis=redis_status,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
