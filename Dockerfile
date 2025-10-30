# Multi-stage Dockerfile for SignUpFlow
# Stage 1: Build stage with Poetry
# Stage 2: Production stage with minimal dependencies

# ============================================================================
# Stage 1: Builder - Install dependencies and build
# ============================================================================
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_VERSION=1.7.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - \
    && ln -s /opt/poetry/bin/poetry /usr/local/bin/poetry

# Set working directory
WORKDIR /app

# Copy dependency files first (for better caching)
COPY pyproject.toml poetry.lock* ./

# Install Python dependencies
RUN poetry install --only main --no-root --no-directory

# Copy application code
COPY api/ ./api/
COPY frontend/ ./frontend/
COPY locales/ ./locales/
COPY alembic/ ./alembic/
COPY alembic.ini ./

# Install the application
RUN poetry install --only main

# ============================================================================
# Stage 2: Production - Minimal runtime image
# ============================================================================
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000 \
    HOST=0.0.0.0

# Install runtime dependencies including Playwright browser dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    # Playwright browser dependencies
    libglib2.0-0t64 \
    libnspr4 \
    libnss3 \
    libdbus-1-3 \
    libatk1.0-0t64 \
    libatspi2.0-0t64 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libxkbcommon0 \
    libasound2t64 \
    libcups2t64 \
    libdrm2 \
    libxcb1 \
    libxext6 \
    libx11-6 \
    libxrender1 \
    libxshmfence1 \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    fonts-liberation \
    libgdk-pixbuf2.0-0 \
    libgtk-3-0 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN groupadd -r signupflow && useradd -r -g signupflow signupflow

# Set working directory
WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Install Playwright browsers (must be done before switching to non-root user)
RUN playwright install chromium

# Copy application code from builder
COPY --from=builder --chown=signupflow:signupflow /app ./

# Create directories for data persistence
RUN mkdir -p /app/data /app/logs && \
    chown -R signupflow:signupflow /app

# Switch to non-root user
USER signupflow

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command - run with uvicorn
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
