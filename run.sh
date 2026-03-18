#!/bin/bash

# LLM Secrets Leak Detector - Wrapper Script
# Ensures the environment is set up and forwards all arguments to the CLI.

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Ensure virtual environment is active if it exists
if [ -d "$SCRIPT_DIR/.venv" ]; then
    source "$SCRIPT_DIR/.venv/bin/activate"
fi

# Run the CLI scanner
# Using exec to replace the shell process with the python process,
# which better handles signals (Ctrl+C) and preserves the stdin stream.
exec python3 "$SCRIPT_DIR/cli.py" "$@"
