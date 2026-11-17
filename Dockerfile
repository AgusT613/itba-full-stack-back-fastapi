# syntax=docker/dockerfile:1

# ==============================================================================
# Dockerfile based on the official Docker Python Guide (docs/docker-with-python.md)
# Features:
# - BuildKit syntax directive (# syntax=docker/dockerfile:1)
# - BuildKit cache mounts for pip & poetry to speed up repeated builds
# - Bind mounts for dependency files to avoid extra intermediate layers
# - Dual-target multi-stage build:
#     * 'builder' stage: directly runnable for development (target: builder)
#     * 'runtime' stage: minimal, secure non-root image for production
# ==============================================================================

# ==============================================================================
# Stage 1: Builder / Development image
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
    POETRY_NO_INTERACTION=1 \
    PATH="/app/.venv/bin:$PATH"

# Install Poetry using pip cache mount to accelerate builds
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install "poetry==${POETRY_VERSION}"

# Install project dependencies into /app/.venv
# Leverage cache mount to /root/.cache/pypoetry to cache downloaded wheels.
# Leverage bind mounts to pyproject.toml, poetry.lock, and README.md to avoid
# having to copy them into an intermediate image layer.
RUN --mount=type=cache,target=/root/.cache/pypoetry \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=poetry.lock,target=poetry.lock \
    --mount=type=bind,source=README.md,target=README.md \
    poetry install --no-root --no-interaction --no-ansi

# Copy application source code into the builder stage.
# This makes the builder stage directly runnable in development (see compose.yaml target: builder).
COPY . .

# Expose default application port
EXPOSE 8000

# Development command (used when Compose targets 'builder')
CMD ["/app/.venv/bin/python3", "-m", "uvicorn", "src.main:app", "--host=0.0.0.0", "--port=8000", "--reload"]


# ==============================================================================
# Stage 2: Production runtime image
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

# Copy virtualenv and application artifacts from builder stage
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder --chown=appuser:appgroup /app/src /app/src
COPY --from=builder --chown=appuser:appgroup /app/pyproject.toml /app/README.md /app/

# Switch to non-root user
USER appuser

# Expose default application port
EXPOSE 8000

# Health check verifying the FastAPI application is responding
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD /app/.venv/bin/python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/docs')" || exit 1

# Production command
CMD ["/app/.venv/bin/python3", "-m", "uvicorn", "src.main:app", "--host=0.0.0.0", "--port=8000"]
