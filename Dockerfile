# Multi-stage Dockerfile for SignUpFlow API

# ============================================================================
# Stage 1: Builder - Install dependencies and build
# ============================================================================
FROM python:3.11-alpine@sha256:0d55920083f1ce1e38ac292e2772f924b4f8bb4188d336c79bf66963039e6146 AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_VERSION=1.7.1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false

RUN apk upgrade --no-cache \
    && apk add --no-cache \
        build-base \
        postgresql-dev

RUN python -m venv /opt/poetry \
    && /opt/poetry/bin/pip install --no-cache-dir \
        "poetry==${POETRY_VERSION}" \
        "poetry-plugin-export==1.6.0"

RUN python -m venv /opt/venv

ENV VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:/opt/poetry/bin:${PATH}"

WORKDIR /app

COPY pyproject.toml poetry.lock* ./

RUN poetry export --only main --format requirements.txt --output requirements.txt \
    && pip install --require-hashes --no-cache-dir -r requirements.txt \
    && rm -rf \
        /opt/venv/bin/pip* \
        /opt/venv/lib/python3.11/site-packages/_distutils_hack \
        /opt/venv/lib/python3.11/site-packages/pip* \
        /opt/venv/lib/python3.11/site-packages/pkg_resources \
        /opt/venv/lib/python3.11/site-packages/setuptools* \
        /opt/venv/lib/python3.11/site-packages/wheel*

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
FROM python:3.11-alpine@sha256:0d55920083f1ce1e38ac292e2772f924b4f8bb4188d336c79bf66963039e6146

ARG VCS_REF=unknown
ARG BUILD_DATE=unknown

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:${PATH}" \
    PORT=8000 \
    HOST=0.0.0.0

RUN apk upgrade --no-cache \
    && apk add --no-cache libpq \
    && rm -rf \
        /usr/local/bin/pip* \
        /usr/local/lib/python3.11/site-packages/_distutils_hack \
        /usr/local/lib/python3.11/site-packages/pip* \
        /usr/local/lib/python3.11/site-packages/pkg_resources \
        /usr/local/lib/python3.11/site-packages/setuptools* \
        /usr/local/lib/python3.11/site-packages/wheel*

RUN addgroup -S signupflow && adduser -S -G signupflow signupflow

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv

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
# Default to one process; operators may scale replicas only after the owned
# Redis/event delivery and artifact acceptance drills pass.
CMD ["python", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
