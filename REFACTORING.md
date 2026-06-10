# Quiet Riot Refactoring Guide

## Overview

This document describes the major refactoring of Quiet Riot to support both CLI and FastAPI interfaces, with improved code organization and modern Python practices.

## New Structure

```
quiet_riot/
├── __init__.py          # Package initialization
├── config.py            # Configuration singleton
├── settings.py          # Backward compatibility
├── cli/                 # CLI interface
│   ├── __init__.py
│   └── main.py          # CLI entry point
├── api/                 # FastAPI application
│   ├── __init__.py
│   ├── server.py        # FastAPI server
│   ├── templates/       # HTML templates
│   │   └── dashboard.html
│   └── static/          # Static assets (CSS, JS)
├── core/                # Core business logic
│   ├── __init__.py
│   ├── models.py        # Data models
│   ├── scanner.py       # Main scanner class
│   ├── wordlist_handler.py
│   └── result_handler.py
└── enumeration/         # Enumeration modules (existing)
    └── ...
```

## Key Changes

### 1. pyproject.toml (Modern Build System)

- Replaced `setup.py` with `pyproject.toml`
- Supports both `pipx` and `uv` installation
- Modern Python packaging standards
- Includes development dependencies
- Configured tools: Black, Ruff, MyPy, Pytest

### 2. CLI Interface (`quiet_riot/cli/`)

- Separated CLI logic from business logic
- Clean argument parsing
- Better error handling
- Entry point: `quiet-riot` command

### 3. FastAPI Application (`quiet_riot/api/`)

- RESTful API for programmatic access
- Web dashboard at `/`
- Real-time scan status updates
- Entry point: `quiet-riot-server` command

### 4. Core Business Logic (`quiet_riot/core/`)

- `Scanner`: Main scanning orchestration
- `WordlistHandler`: Wordlist operations
- `ResultHandler`: Result file operations
- `models.py`: Data models (ScanConfig, ScanResult, ScanType)

## Installation

### Using pipx

```bash
pipx install quiet-riot
```

### Using uv

```bash
uv pip install quiet-riot
```

### Development Installation

```bash
# Using pip
pip install -e ".[dev]"

# Using uv
uv pip install -e ".[dev]"
```

## Usage

### CLI

```bash
# Basic scan
quiet-riot --scan 1 --threads 100

# With wordlist
quiet-riot --scan 3 --wordlist wordlists/service-linked-roles.txt --account-id 123456789012

# Set log level
quiet-riot --scan 1 --log-level DEBUG
```

### FastAPI Server

```bash
# Start server
quiet-riot-server

# Or with uvicorn directly
uvicorn quiet_riot.api.server:app --host 0.0.0.0 --port 8000
```

Then open http://localhost:8000 in your browser to access the dashboard.

### API Endpoints

- `GET /` - Dashboard UI
- `GET /api/scan-types` - List available scan types
- `POST /api/scans` - Start a new scan
- `GET /api/scans/{scan_id}` - Get scan status
- `GET /api/scans` - List all scans
- `GET /health` - Health check

## Migration Notes

### For Existing Code

The old `main.py` is still present for backward compatibility, but new code should use:

- CLI: `quiet_riot.cli.main.main()`
- Core logic: `quiet_riot.core.scanner.Scanner`
- Config: `quiet_riot.config.get_config()`

### Backward Compatibility

- `settings.py` still works for existing code
- Old entry point `quiet_riot.main:main` still functional
- Gradual migration path available

## Next Steps

1. Complete implementation of `Scanner.run_scan()` with actual enumeration logic
2. Add async support for FastAPI scans
3. Add result storage (database option)
4. Add authentication for API
5. Add more dashboard features (charts, history, etc.)

## Development

### Code Quality Tools

```bash
# Format code
black .

# Lint code
ruff check .

# Type check
mypy quiet_riot

# Run tests
pytest
```

### Project Structure Best Practices

- **CLI**: User-facing command-line interface
- **API**: Web interface and REST API
- **Core**: Business logic (reusable by both CLI and API)
- **Enumeration**: Low-level enumeration modules
- **Config**: Application configuration

This separation allows:

- CLI and API to share the same core logic
- Easy testing of business logic
- Clear separation of concerns
- Better maintainability
