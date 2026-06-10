# Installation Guide

## Prerequisites

- Python 3.8 or higher
- AWS credentials configured (for AWS scans)
- pip, pipx, or uv package manager

## Installation Methods

### Method 1: Using pipx (Recommended)

pipx installs applications in isolated environments, preventing dependency conflicts.

```bash
# Install pipx if you don't have it
python3 -m pip install --user pipx
python3 -m pipx ensurepath

# Install Quiet Riot
pipx install quiet-riot

# Verify installation
quiet-riot --help
```

### Method 2: Using uv

uv is a fast Python package manager written in Rust.

```bash
# Install uv (macOS/Linux)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install Quiet Riot
uv pip install quiet-riot

# Or install in a virtual environment
uv venv
source .venv/bin/activate  # or `.venv\Scripts\activate` on Windows
uv pip install quiet-riot
```

### Method 3: Using pip

```bash
# Install from PyPI (when published)
pip install quiet-riot

# Or install from source
git clone https://github.com/righteousgambit/quiet-riot.git
cd quiet-riot
pip install -e .
```

### Method 4: Development Installation

For development with all dependencies:

```bash
# Clone the repository
git clone https://github.com/righteousgambit/quiet-riot.git
cd quiet-riot

# Install with development dependencies
pip install -e ".[dev]"

# Or with uv
uv pip install -e ".[dev]"
```

## Verify Installation

```bash
# Check CLI
quiet-riot --help

# Check server
quiet-riot-server --help

# Or with Python
python -m quiet_riot.cli.main --help
```

## AWS Configuration

Before running scans, ensure AWS credentials are configured:

```bash
# Using AWS CLI
aws configure

# Or set environment variables
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1

# Or use a profile
export AWS_PROFILE=your_profile_name
```

## Troubleshooting

### Import Errors

If you get import errors, ensure you're using the correct Python version:

```bash
python3 --version  # Should be 3.8+
```

### Permission Errors

On Linux/macOS, you may need to use `sudo` or install to user directory:

```bash
pip install --user quiet-riot
```

### Module Not Found

If modules aren't found, ensure the package is installed:

```bash
pip show quiet-riot
```

If not installed, reinstall:

```bash
pip uninstall quiet-riot
pip install -e .
```

## Next Steps

- Read the [README_REFACTORED.md](README_REFACTORED.md) for usage examples
- Check [REFACTORING.md](REFACTORING.md) for architecture details
- See [CODE_REVIEW.md](CODE_REVIEW.md) for code quality improvements
