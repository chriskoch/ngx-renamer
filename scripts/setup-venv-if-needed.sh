#!/bin/bash
# Conditional virtual environment setup for ngx-renamer
# Creates or updates the Python venv with required dependencies

set -e

VENV_PATH="/usr/src/ngx-renamer-venv"
SOURCE_PATH="/usr/src/ngx-renamer"
REQUIREMENTS_FILE="$SOURCE_PATH/requirements.txt"

echo "[ngx-renamer] Setting up Python virtual environment at $VENV_PATH..."

# Create venv if it doesn't exist (check for activate script, not just directory)
if [ ! -f "$VENV_PATH/bin/activate" ]; then
    echo "[ngx-renamer] Creating new virtual environment..."
    python3 -m venv "$VENV_PATH"
else
    echo "[ngx-renamer] Virtual environment exists, updating..."
fi

# Activate and install/update dependencies
source "$VENV_PATH/bin/activate"

echo "[ngx-renamer] Installing dependencies from $REQUIREMENTS_FILE..."
pip install --no-cache-dir --upgrade pip > /dev/null 2>&1
pip install --no-cache-dir -r "$REQUIREMENTS_FILE"

# Create marker file to track when initialization was done
touch "$VENV_PATH/.initialized"

echo "[ngx-renamer] Python environment setup complete!"
