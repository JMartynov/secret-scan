#!/bin/bash

# Ensure virtual environment is active if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Run the CLI scanner
python3 cli.py "$@"
