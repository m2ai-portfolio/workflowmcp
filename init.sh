#!/bin/bash
# WorkflowMCP Development Setup
# Sets up a Python virtual environment and installs project dependencies

cd "$(dirname "$0")"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies quietly
pip install -q click pytest pyyaml

echo "WorkflowMCP dev environment ready."
echo "Run: workflow-mcp --help"
