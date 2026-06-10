#!/bin/bash
# Script to set up virtual environment if it doesn't exist
# This is called automatically by VS Code tasks

set -e

VENV_DIR=".venv"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_PATH="${PROJECT_ROOT}/${VENV_DIR}"

if [ ! -d "$VENV_PATH" ]; then
    echo "📦 Virtual environment not found. Creating .venv..."
    cd "$PROJECT_ROOT"
    python3 -m venv "$VENV_DIR"
    echo "✅ Virtual environment created at $VENV_PATH"

    echo "📥 Activating virtual environment and upgrading pip..."
    source "$VENV_PATH/bin/activate"
    pip install --upgrade pip setuptools wheel

    echo "📦 Installing project dependencies..."
    pip install -e ".[dev]"

    echo "🔧 Installing pre-commit hooks..."
    pre-commit install || echo "⚠️  Pre-commit installation skipped (not critical)"

    echo "✅ Virtual environment setup complete!"
    echo ""
    echo "To activate manually:"
    echo "  source $VENV_PATH/bin/activate"
else
    echo "✅ Virtual environment already exists at $VENV_PATH"
fi
