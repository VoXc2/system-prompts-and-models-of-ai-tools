from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Dealix"
    APP_NAME_AR: str = "ديليكس"
    DEBUG: bool = False
    DEFAULT_TIMEZONE: str = "Asia/Riyadh"
    DEFAULT_CURRENCY: str = "SAR"
    DEFAULT_LOCALE: str = "ar"
    DEFAULT_TENANT_ID: str = ""

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://salesflow:salesflow_secret_2024@db:5432/salesflow"

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"

    # Security
    SECRET_KEY: str = "change-this-to-a-random-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # URLs
    API_URL: str = "http://localhost:8000"
    FRONTEND_URL: str = "http://localhost:3000"

    # WhatsApp
    WHATSAPP_API_TOKEN: str = ""
    WHATSAPP_PHONE_NUMBER_ID: str = ""
    WHATSAPP_BUSINESS_ACCOUNT_ID: str = ""
    WHATSAPP_VERIFY_TOKEN: str = ""

    # Email
    EMAIL_PROVIDER: str = "smtp"
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SENDGRID_API_KEY: str = ""

    # SMS (Unifonic)
    UNIFONIC_APP_SID: str = ""
    UNIFONIC_SENDER_ID: str = "Dealix"

    # AI Settings
    AI_PROVIDER: str = "openai"  # "openai", "anthropic", or "gemini"
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    ANTHROPIC_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.0-flash"

    # Lead Generation (Legitimate B2B APIs)
    APOLLO_API_KEY: str = ""
    HUNTER_API_KEY: str = ""
    META_CTWA_PIXEL_ID: str = ""

    # Lead Discovery APIs (Optional)
    GOOGLE_MAPS_API_KEY: str = ""
    SERPAPI_KEY: str = ""
    TWITTER_BEARER_TOKEN: str = ""
    INSTAGRAM_ACCESS_TOKEN: str = ""
    INSTAGRAM_USER_ID: str = ""

    # Voice AI
    VAPI_API_KEY: str = ""
    VAPI_ASSISTANT_ID: str = ""
    VOICE_AI_ENABLED: bool = False
    VOICE_PROFILE: str = "khalid"  # khalid (male) or noura (female)
    VOICE_OWNER_NAME: str = ""  # Business owner name for personalization

    # Social Media
    INSTAGRAM_BUSINESS_ACCOUNT_ID: str = ""
    LINKEDIN_ACCESS_TOKEN: str = ""
    TIKTOK_ACCESS_TOKEN: str = ""

    # Data Intelligence
    PROXYCURL_API_KEY: str = ""
    CLEARBIT_API_KEY: str = ""
    BUILTWITH_API_KEY: str = ""

    # Agent Swarm
    MAX_DAILY_WHATSAPP_MESSAGES: int = 200
    MAX_DAILY_INSTAGRAM_DMS: int = 20
    MAX_DAILY_TWITTER_DMS: int = 50
    MAX_WEEKLY_LINKEDIN_CONNECTIONS: int = 100
    AGENT_AUTO_ENGAGE: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()
