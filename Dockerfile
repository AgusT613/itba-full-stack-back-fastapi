# ==============================================================================
# Stage 1: Builder - Install dependencies into a virtual environment
# ==============================================================================
FROM python:3.13-slim AS builder

WORKDIR /app

# Configure Python and Poetry environment
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_VERSION=2.0.1 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1

# Install Poetry
RUN pip install "poetry==${POETRY_VERSION}"

# Copy packaging and lock files
COPY pyproject.toml poetry.lock README.md ./

# Install project dependencies into /app/.venv
RUN poetry install --no-root --no-interaction --no-ansi


# ==============================================================================
# Stage 2: Runtime - Minimal, secure container image
# ==============================================================================
FROM python:3.13-slim AS runtime

WORKDIR /app

# Ensure Python unbuffered logging and virtualenv in PATH
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

# Create a non-privileged user and group for security
RUN groupadd -g 1000 appgroup && \
    useradd -u 1000 -g appgroup -s /bin/bash -m appuser

# Copy virtualenv from builder stage
COPY --from=builder --chown=appuser:appgroup /app/.venv /app/.venv

# Copy project files
COPY --chown=appuser:appgroup pyproject.toml README.md ./
COPY --chown=appuser:appgroup src/ ./src/

# Switch to non-root user
USER appuser

# Expose default application port
EXPOSE 8000

# Health check using the existing lightweight /server-alive HEAD endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; req = urllib.request.Request('http://localhost:8000/api/itbank/server-alive', method='HEAD'); urllib.request.urlopen(req)" || exit 1

# Launch FastAPI via Uvicorn
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
