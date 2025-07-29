#!/bin/bash
# Start the todo backend service for development

# Set the Python path to include the src directory
export PYTHONPATH="$PYTHONPATH:$(pwd)"

# Run the application
uv run python src/main.py
