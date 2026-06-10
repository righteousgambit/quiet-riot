# Quick Start Guide

## Running the FastAPI Server

### Option 1: Debug Mode (Recommended for Development)

1. Press `F5` or go to Run and Debug panel (Cmd+Shift+D / Ctrl+Shift+D)
2. Select **"Python: FastAPI Server (Debug)"**
3. Click the play button or press `F5`
4. Server will start at http://localhost:8000
5. Open http://localhost:8000 in your browser

**Benefits:**

- Full debugging support (breakpoints, variable inspection)
- Auto-reload on code changes
- Integrated terminal output

### Option 2: Task (Quick Start)

1. Press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux)
2. Type "Tasks: Run Task"
3. Select **"Start FastAPI Server"**
4. Server will start at http://localhost:8000

**Benefits:**

- Quick start without debugging
- Runs in background
- Auto-reload enabled

### Option 3: Terminal

```bash
# Development (with reload)
uvicorn quiet_riot.api.server:app --host 0.0.0.0 --port 8000 --reload

# Production (no reload)
uvicorn quiet_riot.api.server:app --host 0.0.0.0 --port 8000
```

## Pre-commit Hooks

Pre-commit hooks are **already installed** and will run automatically on `git commit`.

### Test Pre-commit

```bash
# Test all files
pre-commit run --all-files

# Test on commit (automatic)
git commit -m "Your message"
```

### Manual Run

```bash
# Run on staged files
pre-commit run

# Run specific hook
pre-commit run ruff --all-files
```

## Common Commands

### Code Quality

```bash
# Lint
ruff check .

# Format
ruff format .

# Fix issues
ruff check . --fix

# Type check
mypy quiet_riot
```

### Using Makefile

```bash
make lint        # Run linting
make format      # Format code
make lint-fix    # Auto-fix issues
make test        # Run tests
make all         # Run all checks
```

## Troubleshooting

### Server Won't Start

1. Check if port 8000 is in use: `lsof -i :8000`
2. Install dependencies: `pip install -e ".[dev]"`
3. Check AWS credentials are configured

### Pre-commit Not Running

```bash
# Reinstall hooks
pre-commit uninstall
pre-commit install

# Test manually
pre-commit run --all-files
```

### Import Errors

1. Select correct Python interpreter (Cmd+Shift+P → "Python: Select Interpreter")
2. Install package: `pip install -e .`
3. Reload VS Code window
