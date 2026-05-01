"""
Sentry error reporting — captures unhandled exceptions + performance traces.
تقارير الأخطاء عبر Sentry.
"""

from __future__ import annotations

import logging
import os

log = logging.getLogger(__name__)


def setup_sentry() -> None:
    dsn = os.getenv("SENTRY_DSN")
    if not dsn:
        log.info("sentry_not_configured")
        return
    try:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
    except ImportError:
        log.warning("sentry_sdk not installed — skipping Sentry setup")
        return

    sentry_sdk.init(
        dsn=dsn,
        environment=os.getenv("APP_ENV", "production"),
        release=os.getenv("APP_VERSION", "3.0.0"),
        traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1")),
        profiles_sample_rate=float(os.getenv("SENTRY_PROFILES_SAMPLE_RATE", "0.05")),
        send_default_pii=False,
        integrations=[FastApiIntegration(), SqlalchemyIntegration()],
    )
    log.info("sentry_enabled", extra={"env": os.getenv("APP_ENV")})
