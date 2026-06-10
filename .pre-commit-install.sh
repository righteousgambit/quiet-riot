#!/bin/bash
# Quick setup script for pre-commit hooks

echo "Installing pre-commit hooks..."
pip install pre-commit
pre-commit install

echo ""
echo "Pre-commit hooks installed!"
echo "Run 'pre-commit run --all-files' to test, or just commit normally."
