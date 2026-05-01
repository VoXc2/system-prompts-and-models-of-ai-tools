# syntax=docker/dockerfile:1.7
# ═══════════════════════════════════════════════════════════════
# AI Company Saudi — production Docker image
# Multi-stage, non-root, Python 3.12-slim
# ═══════════════════════════════════════════════════════════════

# ──────────────────────────────────────────────────────────────
# Stage 1 — Builder: install deps into a venv
# ──────────────────────────────────────────────────────────────
FROM python:3.12-slim-bookworm AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

# Create virtualenv
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy dependency files first for better caching
COPY pyproject.toml ./
COPY requirements.txt* ./

# Install deps and aggressively prune caches/metadata to shrink image
RUN pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt \
    && find /opt/venv -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true \
    && find /opt/venv -type d -name tests -exec rm -rf {} + 2>/dev/null || true \
    && find /opt/venv -type f -name "*.pyc" -delete 2>/dev/null || true

# ──────────────────────────────────────────────────────────────
# Stage 2 — Runtime: minimal image
# ──────────────────────────────────────────────────────────────
FROM python:3.12-slim-bookworm AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    APP_ENV=production

# Runtime-only system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl \
        tini \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd --gid 1000 app \
    && useradd --uid 1000 --gid app --shell /bin/bash --create-home app

# Copy venv from builder
COPY --from=builder /opt/venv /opt/venv

WORKDIR /app
COPY --chown=app:app . .

USER app

# Railway injects $PORT dynamically; default to 8000 for local dev
ENV PORT=8000
EXPOSE 8000

# Healthcheck uses $PORT so it matches whatever the platform assigns
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -fsS http://localhost:${PORT:-8000}/health || exit 1

# Wrapper script so any start command (Dockerfile CMD, Procfile, Railway
# startCommand override) works without shell-expansion gotchas.
COPY --chown=app:app <<'EOF' /app/start.sh
#!/bin/sh
set -e
exec uvicorn api.main:app --host 0.0.0.0 --port "${PORT:-8000}" --workers 1
EOF
RUN chmod +x /app/start.sh

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["/app/start.sh"]
