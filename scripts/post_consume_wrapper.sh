#!/bin/bash
# Post-consume script wrapper for ngx-renamer
# Activates the virtual environment and runs the title generation script

set -e

VENV_PATH="/usr/src/ngx-renamer-venv"
SOURCE_PATH="/usr/src/ngx-renamer"

# Activate virtual environment
source "$VENV_PATH/bin/activate"

# Set RUN_DIR for change_title.py to find settings.yaml
export RUN_DIR="$SOURCE_PATH"

# Run the main Python script
python3 "$SOURCE_PATH/change_title.py"
