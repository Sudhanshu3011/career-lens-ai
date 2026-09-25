# ==============================================================================
# Multi-stage Dockerfile for Resume Analyser Backend using Astral uv
# ==============================================================================

# Stage 1: Build virtual environment with uv
FROM python:3.13-slim-bookworm AS builder

# Install uv from official distroless image
COPY --from=ghcr.io/astral-sh/uv:0.6.14 /uv /uvx /bin/

# Environment configurations for uv
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0

WORKDIR /app

# Copy dependency specifications first to maximize layer caching
COPY pyproject.toml uv.lock README.md ./

# Install locked dependencies into the virtual environment
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Copy application source code
COPY app ./app

# ------------------------------------------------------------------------------
# Stage 2: Minimal, secure production runtime
# ------------------------------------------------------------------------------
FROM python:3.13-slim-bookworm AS runner

# Security hardening: create non-root application user
RUN groupadd -r -g 1001 appgroup && \
    useradd -r -u 1001 -g appgroup -m -d /home/appuser -s /sbin/nologin appuser

WORKDIR /app

# Prepare writable data directory for SQLite database persistence
RUN mkdir -p /app/data && chown -R appuser:appgroup /app/data

# Copy prebuilt virtual environment and source code with proper ownership
COPY --from=builder --chown=appuser:appgroup /app/.venv /app/.venv
COPY --from=builder --chown=appuser:appgroup /app/app /app/app

# Place venv binaries at the front of PATH
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DATABASE_URL="sqlite:////app/data/sessions.db"

# Switch to unprivileged user
USER appuser

# Expose backend port
EXPOSE 8000

# Zero-dependency Python healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health')" || exit 1

# Launch ASGI server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

