"""
Application settings loaded from environment variables only.
إعدادات التطبيق — تُحمّل من متغيرات البيئة فقط.

Uses pydantic-settings v2 BaseSettings. NO hardcoded secrets anywhere.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

Environment = Literal["development", "staging", "production", "test"]
LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
Locale = Literal["ar", "en"]


class Settings(BaseSettings):
    """Single source of truth for configuration | المصدر الوحيد للإعدادات."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── App ─────────────────────────────────────────────────────
    app_name: str = "Dealix"
    app_version: str = "3.0.0"
    app_env: Environment = "development"
    app_debug: bool = False
    app_host: str = "0.0.0.0"  # noqa: S104 — intentional for containerized deploy
    app_port: int = 8000
    app_timezone: str = "Asia/Riyadh"
    app_default_locale: Locale = "ar"
    app_default_currency: str = "SAR"
    app_log_level: LogLevel = "INFO"
    app_secret_key: SecretStr = Field(default=SecretStr("change-me"))
    cors_origins: str = "http://localhost:3000,http://localhost:8000"

    # ── LLM: Anthropic ──────────────────────────────────────────
    anthropic_api_key: SecretStr | None = None
    anthropic_model: str = "claude-sonnet-4-5-20250929"
    anthropic_max_tokens: int = 4096
    anthropic_timeout: int = 60

    # ── LLM: DeepSeek ───────────────────────────────────────────
    deepseek_api_key: SecretStr | None = None
    deepseek_base_url: str = "https://api.deepseek.com/v1"
    deepseek_model: str = "deepseek-chat"

    # ── LLM: GLM (Z.ai) ─────────────────────────────────────────
    glm_api_key: SecretStr | None = None
    glm_base_url: str = "https://open.bigmodel.cn/api/paas/v4"
    glm_model: str = "glm-4"

    # ── LLM: Google Gemini ──────────────────────────────────────
    google_api_key: SecretStr | None = None
    gemini_model: str = "gemini-1.5-pro"

    # ── LLM: Groq ───────────────────────────────────────────────
    groq_api_key: SecretStr | None = None
    groq_api_key_alt: SecretStr | None = None
    groq_model: str = "llama-3.3-70b-versatile"
    groq_base_url: str = "https://api.groq.com/openai/v1"

    # ── LLM: OpenAI (fallback) ──────────────────────────────────
    openai_api_key: SecretStr | None = None
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o-mini"

    # ── Databases ───────────────────────────────────────────────
    database_url: str = "postgresql+asyncpg://ai_user:ai_password@localhost:5432/ai_company"
    redis_url: str = "redis://localhost:6379/0"
    mongodb_uri: str = "mongodb://localhost:27017/ai_company"

    @field_validator("database_url", mode="before")
    @classmethod
    def _ensure_asyncpg_driver(cls, v: str | None) -> str:
        """Normalize Railway/Heroku postgres://… URLs to postgresql+asyncpg://…

        Managed Postgres providers (Railway, Heroku, Render) export the URL
        as ``postgres://`` or ``postgresql://``; SQLAlchemy async needs the
        explicit ``postgresql+asyncpg://`` driver prefix.
        """
        if not v:
            return "postgresql+asyncpg://ai_user:ai_password@localhost:5432/ai_company"
        if v.startswith("postgres://"):
            v = "postgresql://" + v[len("postgres://") :]
        if v.startswith("postgresql://") and "+asyncpg" not in v:
            v = "postgresql+asyncpg://" + v[len("postgresql://") :]
        return v

    # ── WhatsApp Business ───────────────────────────────────────
    whatsapp_access_token: SecretStr | None = None
    whatsapp_phone_number_id: str | None = None
    whatsapp_business_account_id: str | None = None
    whatsapp_verify_token: SecretStr | None = None
    whatsapp_app_secret: SecretStr | None = None
    # Live WhatsApp Cloud API send — MUST remain False until webhook + opt-in + legal sign-off.
    # Env: WHATSAPP_ALLOW_LIVE_SEND (default false).
    whatsapp_allow_live_send: bool = False

    # ── Email ───────────────────────────────────────────────────
    email_provider: Literal["resend", "sendgrid", "smtp"] = "resend"
    email_from: str = "noreply@ai-company.sa"
    email_from_name: str = "AI Company Saudi"
    resend_api_key: SecretStr | None = None
    sendgrid_api_key: SecretStr | None = None
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_user: str | None = None
    smtp_password: SecretStr | None = None
    smtp_tls: bool = True

    # ── Calendar ────────────────────────────────────────────────
    google_calendar_credentials_file: str | None = None
    google_calendar_id: str = "primary"
    calendly_api_token: SecretStr | None = None
    calendly_user_uri: str | None = None

    # ── HubSpot ─────────────────────────────────────────────────
    hubspot_access_token: SecretStr | None = None
    hubspot_portal_id: str | None = None

    # ── Automation ──────────────────────────────────────────────
    n8n_webhook_url: str | None = None
    n8n_encryption_key: SecretStr | None = None

    # ── Observability ───────────────────────────────────────────
    langfuse_public_key: SecretStr | None = None
    langfuse_secret_key: SecretStr | None = None
    langfuse_host: str = "https://cloud.langfuse.com"
    sentry_dsn: str | None = None

    # ── Other ───────────────────────────────────────────────────
    clickbank_api_key: SecretStr | None = None
    hix_ai_api_key: SecretStr | None = None

    # ── Pricing (SAR) ───────────────────────────────────────────
    pricing_sa_setup_min: int = 12000
    pricing_sa_setup_max: int = 40000
    pricing_sa_retainer_min: int = 3000
    pricing_sa_retainer_max: int = 12000
    pricing_gcc_setup_min: int = 15000
    pricing_gcc_setup_max: int = 50000
    pricing_gcc_retainer_min: int = 4000
    pricing_gcc_retainer_max: int = 15000
    pricing_global_setup_min_usd: int = 3000
    pricing_global_setup_max_usd: int = 10000
    pricing_global_retainer_min_usd: int = 800
    pricing_global_retainer_max_usd: int = 3000

    # ── Validators ──────────────────────────────────────────────
    @field_validator("cors_origins")
    @classmethod
    def _split_cors(cls, v: str) -> str:
        return v.strip()

    @property
    def cors_origin_list(self) -> list[str]:
        """Parsed CORS origins as list."""
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"

    def require_secret(self, name: str) -> str:
        """Get a required secret or raise ValueError | يجلب سراً مطلوباً أو يرفع خطأ."""
        value = getattr(self, name, None)
        if value is None:
            raise ValueError(f"Required secret missing: {name}")
        if isinstance(value, SecretStr):
            secret = value.get_secret_value()
            if not secret or secret in ("", "change-me"):
                raise ValueError(f"Required secret empty: {name}")
            return secret
        return str(value)

    def has_llm_provider(self, provider: str) -> bool:
        """Check if an LLM provider is configured | هل المزود متوفر؟"""
        mapping = {
            "anthropic": self.anthropic_api_key,
            "deepseek": self.deepseek_api_key,
            "glm": self.glm_api_key,
            "gemini": self.google_api_key,
            "groq": self.groq_api_key,
            "openai": self.openai_api_key,
        }
        key = mapping.get(provider.lower())
        if key is None:
            return False
        return bool(key.get_secret_value())


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Cached settings singleton | إعدادات مفردة مخزنة."""
    return Settings()


settings = get_settings()
