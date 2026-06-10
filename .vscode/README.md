# VS Code Configuration for Quiet Riot

## Setup

1. **Install Recommended Extensions**

   - Open Command Palette (Cmd+Shift+P / Ctrl+Shift+P)
   - Run "Extensions: Show Recommended Extensions"
   - Install all recommended extensions

2. **Install Pre-commit Hooks**

   ```bash
   pip install pre-commit
   pre-commit install
   ```

3. **Install Development Dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

## Features

### Ruff Integration

- **Linting**: Ruff replaces flake8 for faster, more comprehensive linting
- **Formatting**: Ruff can also format code (alternative to Black)
- **Auto-fix**: Ruff can automatically fix many linting issues

### Tasks

Available tasks (Cmd+Shift+P / Ctrl+Shift+P → "Tasks: Run Task"):

- **Install Dependencies** - Install the package in development mode
- **Run Tests** - Execute pytest
- **Lint Code** - Run ruff check
- **Format Code (Ruff)** - Format code with ruff
- **Fix Linting Issues** - Auto-fix linting issues with ruff
- **Type Check** - Run mypy type checking
- **Start FastAPI Server** - Start the FastAPI server with auto-reload (development)
- **Start FastAPI Server (Production)** - Start the FastAPI server without reload

### Debug Configurations

Available debug configurations (F5 or Run and Debug panel):

#### CLI Debug Configurations

- **Python: Quiet Riot - Main** - Debug main CLI entry point
- **Python: Quiet Riot - AWS Account IDs** - Debug AWS account ID enumeration
- **Python: Quiet Riot - Microsoft 365 Domains** - Debug Microsoft 365 domain check
- **Python: Quiet Riot - AWS Services Footprinting** - Debug AWS services footprinting
- **Python: Quiet Riot - AWS Root User Email** - Debug root user email enumeration
- **Python: Quiet Riot - AWS IAM Principals** - Debug IAM principal enumeration
- **Python: Quiet Riot - Microsoft 365 Users** - Debug Microsoft 365 user enumeration
- **Python: Quiet Riot - Google Workspace Users** - Debug Google Workspace user enumeration
- **Python: Quiet Riot - With ARN** - Debug using IAM role ARN (profile created automatically)

All CLI configurations use the modern CLI entry point (`quiet_riot.cli.main`) and support:

- **Profile-based authentication**: Use `--profile <name>` argument
- **ARN-based authentication**: Use `--arn <full-arn>` argument (profile created automatically)
- **Default profile**: Omit both to use default AWS profile

#### API Server Debug Configurations

- **Python: FastAPI Server (Debug)** - Debug the FastAPI server with auto-reload
- **Python: FastAPI Server (No Reload)** - Debug without auto-reload (faster)

#### Other Debug Configurations

- **Python: Current File** - Debug the currently open file
- **Python: Debug Tests** - Debug pytest tests

#### Example: Using ARN in Debug Configuration

To debug with an IAM role ARN, modify the `args` in the debug configuration:

```json
{
  "name": "Python: Quiet Riot - With ARN",
  "type": "debugpy",
  "request": "launch",
  "module": "quiet_riot.cli.main",
  "args": [
    "--scan", "1",
    "--threads", "10",
    "--arn", "arn:aws:iam::123456789012:role/MyRole"
  ]
}
```

The credentials manager will automatically create a profile from the ARN.

### AWS Credentials in Debug Configurations

All CLI debug configurations support AWS credentials via:

1. **Profile argument**: Add `--profile <name>` to args
2. **ARN argument**: Add `--arn <full-arn>` to args (e.g., `arn:aws:iam::123456789012:role/MyRole`)
3. **Environment variables**: Set `AWS_PROFILE` or other AWS credential environment variables
4. **Default profile**: Omit both `--profile` and `--arn` to use the default profile

**Note**: Profile names take precedence over ARNs if both are provided.

### Pre-commit Hooks

Pre-commit hooks run automatically on `git commit`:

- **Ruff linting** - Checks code quality
- **Ruff formatting** - Formats code
- **File checks** - Trailing whitespace, end of file, etc.
- **Security checks** - Bandit security scanning
- **Type checking** - MyPy (optional)

✅ **Pre-commit hooks are installed and active!**

### Manual Pre-commit Run

```bash
# Run on all files
pre-commit run --all-files

# Run on staged files only (default)
pre-commit run
```

## Configuration

### Ruff Settings

Ruff is configured in `pyproject.toml`:

- Line length: 120
- Target Python: 3.8+
- Enabled rules: E, W, F, I, B, C4, UP, N, S, SIM

### Editor Settings

- Format on save: Enabled
- Organize imports on save: Enabled
- Auto-fix on save: Enabled
- Ruler at 120 characters

### Python Interpreter

The workspace is configured to use a virtual environment at `.venv`. The Python interpreter is automatically detected, but you can manually select it:

1. Press Cmd+Shift+P / Ctrl+Shift+P
2. Type "Python: Select Interpreter"
3. Choose the interpreter at `.venv/bin/python`

## Troubleshooting

### Ruff Not Working

1. Install ruff: `pip install ruff`
2. Reload VS Code window
3. Check that Ruff extension is installed
4. Verify `ruff` is in your `.venv/bin/` directory

### Pre-commit Not Running

1. Install pre-commit: `pip install pre-commit`
2. Install hooks: `pre-commit install`
3. Test: `pre-commit run --all-files`

### Import Errors

If you see import errors in VS Code:

1. Select the correct Python interpreter (Cmd+Shift+P → "Python: Select Interpreter")
2. Ensure virtual environment is activated
3. Install package: `pip install -e .`
4. Reload VS Code window

### AWS Credentials Not Working in Debug

1. **Check profile exists**: Verify the profile name exists in `~/.aws/config` or `~/.aws/credentials`
2. **Test credentials**: Run `aws sts get-caller-identity --profile <profile-name>` in terminal
3. **ARN format**: Ensure ARN is in full format: `arn:aws:iam::123456789012:role/RoleName`
4. **Check logs**: Look at the debug console output for credential validation errors

### Debug Configuration Not Starting

1. **Check preLaunchTask**: Ensure "Setup Virtual Environment" task completes successfully
2. **Verify module path**: For CLI configs, ensure `module` is set to `quiet_riot.cli.main` (not `program`)
3. **Check Python path**: Verify `python` points to `${workspaceFolder}/.venv/bin/python`
4. **Review args**: Ensure all required arguments are provided (e.g., `--scan`, `--account-id` for some scan types)

### FastAPI Server Won't Start

1. **Check port**: Verify port 8000 is available: `lsof -i :8000`
2. **Check credentials**: The server will start but may require credentials for scans
3. **Install dependencies**: Run `pip install -e ".[dev]"`
4. **Check logs**: Review terminal output for errors

## Quick Reference

### Common Commands

```bash
# Start FastAPI server (development)
uvicorn quiet_riot.api.server:app --host 0.0.0.0 --port 8000 --reload

# Start FastAPI server (production)
uvicorn quiet_riot.api.server:app --host 0.0.0.0 --port 8000

# Run CLI with profile
quiet-riot --scan 1 --threads 100 --profile my-profile

# Run CLI with ARN
quiet-riot --scan 1 --threads 100 --arn arn:aws:iam::123456789012:role/MyRole

# Format code
ruff format .

# Lint code
ruff check .

# Fix linting issues
ruff check . --fix

# Type check
mypy quiet_riot

# Run tests
pytest
```

### Debug Shortcuts

- **F5**: Start debugging (uses last selected configuration)
- **Cmd+Shift+D / Ctrl+Shift+D**: Open Run and Debug panel
- **Cmd+Shift+P / Ctrl+Shift+P**: Open Command Palette

## Additional Resources

- [QUICK_START.md](QUICK_START.md) - Quick start guide for running the server
- [SERVER_GUIDE.md](SERVER_GUIDE.md) - Detailed server running guide
- [VENV_SETUP.md](VENV_SETUP.md) - Virtual environment setup guide
- Main [README.md](../README.md) - Complete project documentation
