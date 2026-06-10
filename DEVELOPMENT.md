# Development Guide

## Quick Start

```bash
# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Or use the helper script
./.pre-commit-install.sh
```

## Code Quality Tools

### Ruff (Linting & Formatting)

Ruff is configured as the primary linting and formatting tool.

```bash
# Check for issues
ruff check .

# Auto-fix issues
ruff check . --fix

# Format code
ruff format .

# Check specific file
ruff check quiet_riot/core/scanner.py
```

### Pre-commit Hooks

Pre-commit hooks run automatically on `git commit`:

- **Ruff linting** - Fast Python linter
- **Ruff formatting** - Code formatter
- **File checks** - Trailing whitespace, end of file, etc.
- **Security checks** - Bandit security scanning
- **Type checking** - MyPy (optional)

```bash
# Install hooks
pre-commit install

# Run on all files
pre-commit run --all-files

# Run on staged files only
pre-commit run
```

### MyPy (Type Checking)

```bash
# Run type checking
mypy quiet_riot

# Or use the VS Code task
# Cmd+Shift+P → "Tasks: Run Task" → "Type Check"
```

## VS Code Integration

### Recommended Extensions

- `ms-python.python` - Python support
- `ms-python.vscode-pylance` - Type checking
- `charliermarsh.ruff` - Ruff integration
- `ms-python.debugpy` - Debugging
- `ms-python.pytest` - Test support

### Tasks

Available tasks (Cmd+Shift+P → "Tasks: Run Task"):

- **Install Dependencies** - `pip install -e .`
- **Run Tests** - `pytest -v`
- **Lint Code** - `ruff check .`
- **Format Code (Ruff)** - `ruff format .`
- **Fix Linting Issues** - `ruff check . --fix`
- **Type Check** - `mypy quiet_riot`

### Settings

- Format on save: Enabled
- Organize imports on save: Enabled
- Auto-fix on save: Enabled
- Ruler at 120 characters

## Makefile Commands

For convenience, a Makefile is provided:

```bash
make help          # Show all commands
make install-dev   # Install with dev dependencies
make lint          # Run ruff check
make format        # Format code
make lint-fix      # Auto-fix linting issues
make type-check    # Run mypy
make test          # Run tests
make test-cov      # Run tests with coverage
make clean         # Clean build artifacts
make all           # Run all checks
```

## Workflow

### Before Committing

1. Run linting: `ruff check .`
2. Fix issues: `ruff check . --fix`
3. Format code: `ruff format .`
4. Run tests: `pytest`

Or use pre-commit (runs automatically):

```bash
git add .
git commit -m "Your message"
# Pre-commit hooks run automatically
```

### Manual Pre-commit Run

```bash
# Test all files
pre-commit run --all-files

# Test specific hook
pre-commit run ruff --all-files
```

## Configuration Files

- **pyproject.toml** - Main configuration (Ruff, MyPy, Pytest, etc.)
- **.pre-commit-config.yaml** - Pre-commit hooks configuration
- **.vscode/settings.json** - VS Code workspace settings
- **.vscode/tasks.json** - VS Code tasks
- **Makefile** - Convenience commands

## Troubleshooting

### Pre-commit Not Running

```bash
# Reinstall hooks
pre-commit uninstall
pre-commit install

# Test manually
pre-commit run --all-files
```

### Ruff Not Found

```bash
# Install ruff
pip install ruff

# Or install all dev dependencies
pip install -e ".[dev]"
```

### Import Errors in VS Code

1. Select correct Python interpreter
2. Reload VS Code window
3. Ensure package is installed: `pip install -e .`

## Code Style

- **Line length**: 120 characters
- **Quotes**: Double quotes (enforced by Ruff)
- **Imports**: Sorted by Ruff (isort)
- **Type hints**: Encouraged but not required
- **Docstrings**: Google style preferred

## Continuous Integration

Pre-commit hooks can be integrated into CI/CD:

```yaml
# Example GitHub Actions
- name: Run pre-commit
  uses: pre-commit/action@v3.0.0
```
