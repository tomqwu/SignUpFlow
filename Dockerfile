# Multi-stage Dockerfile for SignUpFlow API

# ============================================================================
# Stage 1: Builder - Install dependencies and build
# ============================================================================
FROM python:3.11-slim AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_VERSION=1.7.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false

RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org | python3 - \
    && ln -s /opt/poetry/bin/poetry /usr/local/bin/poetry

WORKDIR /app

COPY pyproject.toml poetry.lock* ./

RUN poetry install --only main --no-root --no-directory

# web/ is imported by api.main (`from web.app import mount_web`) — the
# HTML app won't start without it.
COPY api/ ./api/
COPY web/ ./web/
COPY alembic/ ./alembic/
COPY alembic.ini ./
COPY docker-entrypoint.sh ./

# ============================================================================
# Stage 2: Production - Minimal runtime image
# ============================================================================
FROM python:3.11-slim

ARG VCS_REF=unknown
ARG BUILD_DATE=unknown

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000 \
    HOST=0.0.0.0

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd -r signupflow && useradd -r -g signupflow signupflow

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

COPY --from=builder /app ./

RUN find /app -type d -exec chmod 0555 {} + && \
    find /app -type f -exec chmod 0444 {} + && \
    chmod 0555 /app/docker-entrypoint.sh

USER signupflow

LABEL org.opencontainers.image.title="SignUpFlow" \
    org.opencontainers.image.version="1.0.0" \
    org.opencontainers.image.revision="${VCS_REF}" \
    org.opencontainers.image.created="${BUILD_DATE}"

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/ready', timeout=5)" || exit 1

ENTRYPOINT ["/app/docker-entrypoint.sh"]
# Process-local rate limits and SSE require one worker until #261/#266 add
# shared state and cross-worker acceptance.
CMD ["python", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
