#!/bin/bash

set -e

echo "WorkflowMCP Setup Script"
echo "======================="
echo ""

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $PYTHON_VERSION"

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv .venv
else
    echo "Virtual environment already exists, skipping creation"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip, setuptools, and wheel
echo "Upgrading pip, setuptools, and wheel..."
pip install --upgrade pip setuptools wheel

# Install project dependencies
echo "Installing project dependencies..."
if [ -f "pyproject.toml" ]; then
    pip install -e .
else
    echo "Warning: pyproject.toml not found"
fi

# Verify installation
echo ""
echo "Verifying installation..."
echo "CLI Help Output:"
echo "---------------"
python -m workflow_mcp --help 2>/dev/null || echo "Note: CLI module will be available after project structure is created"

echo ""
echo "Setup complete!"
echo "To activate the virtual environment, run:"
echo "  source .venv/bin/activate"
