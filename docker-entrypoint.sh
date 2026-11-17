#!/bin/sh
set -e

# ==============================================================================
# Container Entrypoint Script
# Bootstraps database tables, branch offices, and administrative/seed users
# before launching the application server (e.g. uvicorn).
# ==============================================================================

# Select python binary (prefers /app/.venv/bin/python3 if present in container)
if [ -x "/app/.venv/bin/python3" ]; then
    PYTHON_BIN="/app/.venv/bin/python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_BIN="python"
else
    PYTHON_BIN="python3"
fi

if [ "$ENVIRONMENT" = "development" ] || [ "$ENVIRONMENT" = "dev" ]; then
    echo "[Entrypoint] Initializing development database with seed accounts..."
    "$PYTHON_BIN" -m src.db.seed
else
    echo "[Entrypoint] Initializing production database (branch offices & initial admin)..."
    "$PYTHON_BIN" -m src.db.init_db
fi

# Execute container command (e.g. uvicorn)
exec "$@"
