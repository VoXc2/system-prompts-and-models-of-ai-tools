# ── Stage 1: Builder ──────────────────────────────────
FROM python:3.12-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt ./
ARG CACHEBUST=2
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt

# ── Stage 2: Runtime ─────────────────────────────────
FROM python:3.12-slim AS runtime

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 curl tini \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd --gid 1000 app \
    && useradd --uid 1000 --gid app --shell /bin/bash --create-home app

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app
COPY --chown=app:app . .
RUN chmod +x start.sh

USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=90s --retries=5 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

ENTRYPOINT ["tini", "--"]
CMD ["./start.sh"]
