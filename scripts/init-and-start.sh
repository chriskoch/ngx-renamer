#!/bin/bash
# Entrypoint wrapper for Paperless NGX with ngx-renamer auto-initialization
# This script ensures the Python virtual environment is ready before starting Paperless

set -e

VENV_PATH="/usr/src/ngx-renamer-venv"
SOURCE_PATH="/usr/src/ngx-renamer"
REQUIREMENTS_FILE="$SOURCE_PATH/requirements.txt"
INIT_MARKER="$VENV_PATH/.initialized"

echo "[ngx-renamer] Checking Python environment..."

# Check if venv needs initialization or update
if [ ! -f "$INIT_MARKER" ] || [ "$REQUIREMENTS_FILE" -nt "$INIT_MARKER" ]; then
    echo "[ngx-renamer] Initializing/updating Python environment..."
    "$SOURCE_PATH/scripts/setup-venv-if-needed.sh"
else
    echo "[ngx-renamer] Python environment ready (venv exists and is up-to-date)"
fi

# Start normal Paperless entrypoint with all original arguments
echo "[ngx-renamer] Starting Paperless NGX..."
exec /sbin/docker-entrypoint.sh "$@"
