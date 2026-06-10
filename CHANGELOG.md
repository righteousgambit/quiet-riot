# Changelog

## [1.0.7] - 2024-11-26

### Major Refactoring

#### Added

- **Modern Build System**: Replaced `setup.py` with `pyproject.toml`

  - Supports both `pipx` and `uv` installation
  - Configured code quality tools (Black, Ruff, MyPy, Pytest)
  - Modern Python packaging standards

- **FastAPI Web Interface**: New web dashboard and REST API

  - Interactive dashboard at `/`
  - RESTful API endpoints for programmatic access
  - Real-time scan status updates
  - Modern, responsive UI design

- **Improved Code Organization**:

  - Separated CLI interface (`quiet_riot/cli/`)
  - Core business logic (`quiet_riot/core/`)
  - FastAPI application (`quiet_riot/api/`)
  - Clear separation of concerns

- **New Core Modules**:

  - `Scanner`: Main scanning orchestration class
  - `EnumerationHandler`: Handles different enumeration types
  - `WordlistHandler`: Manages wordlist operations
  - `ResultHandler`: Handles result file operations
  - `models.py`: Data models with type safety

- **Configuration Management**:
  - Config singleton pattern (`config.py`)
  - Proper logging configuration
  - Environment variable support
  - Backward compatibility with `settings.py`

#### Changed

- **Logging**: Replaced all `print()` statements with proper logging
- **Error Handling**: Improved error handling with retry logic
- **Threading**: Fixed threading issues using ThreadPoolExecutor
- **Resource Management**: Proper cleanup with try/finally blocks
- **Code Quality**: Improved Pythonic practices throughout

#### Fixed

- Threading bugs in `loadbalancer.py`
- Resource cleanup issues
- Silent exception handling
- Type safety issues

#### Removed

- Hardcoded cleanup logic
- Global state issues
- Print statements

### Installation

```bash
# Using pipx
pipx install quiet-riot

# Using uv
uv pip install quiet-riot

# Development
pip install -e ".[dev]"
```

### Usage

**CLI:**

```bash
quiet-riot --scan 1 --threads 100
```

**Web Dashboard:**

```bash
quiet-riot-server
# Open http://localhost:8000
```

### Migration Notes

- Old `main.py` still works for backward compatibility
- New code should use `quiet_riot.core.scanner.Scanner`
- CLI entry point: `quiet-riot` command
- Server entry point: `quiet-riot-server` command

### Breaking Changes

- None - backward compatible with existing code

### Deprecated

- Direct use of `main.py` (use CLI or API instead)
- `settings.py` global variables (use `config.get_config()`)
