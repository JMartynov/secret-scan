#!/bin/bash

# Ensure virtual environment is active if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Set default API key if not set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "Warning: OPENAI_API_KEY is not set. Looking for .env file..."
    if [ ! -f ".env" ]; then
        if [ -f "env.example" ]; then
            echo "Creating .env from env.example. Please update it with your API key."
            cp env.example .env
        else
            echo "Error: No .env file found and no OPENAI_API_KEY environment variable set."
            exit 1
        fi
    fi
fi

# Run the chat application
python3 infinite_memory_chat.py
