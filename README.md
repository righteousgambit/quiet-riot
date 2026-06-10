# Quiet Riot
### :notes: *C'mon, Feel The Noise* :notes:

_An enumeration tool for scalable, unauthenticated validation of AWS, Azure, and GCP principals; including AWS Account IDs, root e-mail addresses, users, and roles, Azure Active Directory Users, and Google Workspace Users/E-mails._

__Credit:__ Daniel Grzelak [@dagrz](https://twitter.com/dagrz) for identifying the technique and Will Bengston [@__muscles](https://twitter.com/__muscles) for inspiring me to scale it.

See the introductory blog post [here](https://blog.traingrc.com/en/introducing-quiet-riot).
See a defender's perspective blog post [here](https://blog.traingrc.com/en/quiet-riot-defenders-lens).

## 🚀 Quick Start

### Installation

**Using pipx (recommended):**

```bash
pipx install quiet-riot
```

**Using pip:**

```bash
pip install quiet-riot
```

**Development installation:**

```bash
git clone https://github.com/righteousgambit/quiet-riot.git
cd quiet-riot
pip install -e ".[dev]"
```

### Prerequisites

- Python 3.11+
- AWS credentials configured (for AWS scans - still unauthenticated, but resources need to be provisioned)
- boto3/botocore (installed automatically)

## 📖 Usage

### CLI Usage

Quiet Riot provides a modern CLI interface with support for AWS profile names and IAM role ARNs.

#### Basic Examples

```bash
# AWS Account ID enumeration (using default profile)
quiet-riot --scan 1 --threads 100

# Using a specific AWS profile
quiet-riot --scan 1 --threads 100 --profile my-profile

# Using an IAM role ARN (profile will be created automatically)
quiet-riot --scan 1 --threads 100 --arn arn:aws:iam::123456789012:role/MyRole

# AWS IAM Principals (requires account ID and wordlist)
quiet-riot --scan 5 --account-id 123456789012 --wordlist wordlists/service-linked-roles.txt --threads 50 --profile my-profile

# Microsoft 365 Domain check
quiet-riot --scan 2 --domain example.com --profile my-profile

# With custom log level
quiet-riot --scan 1 --log-level DEBUG --profile my-profile
```

#### AWS Credentials Configuration

Quiet Riot supports multiple ways to configure AWS credentials:

1. **Profile Name (Preferred)**: Use an existing AWS profile from `~/.aws/config` or `~/.aws/credentials`
   ```bash
   quiet-riot --scan 1 --profile my-profile
   ```

2. **IAM Role ARN**: Provide a full IAM role ARN. Quiet Riot will automatically create a profile for role assumption
   ```bash
   quiet-riot --scan 1 --arn arn:aws:iam::123456789012:role/MyRole
   ```

3. **Default Profile**: If neither `--profile` nor `--arn` is provided, Quiet Riot will try the `default` profile
   ```bash
   quiet-riot --scan 1  # Uses default profile
   ```

**Profile Priority**: `--profile` takes precedence over `--arn` if both are provided.

#### CLI Arguments

| Argument | Short | Required | Description |
|----------|-------|----------|-------------|
| `--scan` | `--s` | Yes | Scan type (1-7) |
| `--threads` | `--t` | No | Number of threads (default: 100) |
| `--wordlist` | `--w` | No | Path to wordlist file |
| `--profile` | `--p` | No | AWS profile name (preferred over --arn) |
| `--arn` | - | No | AWS IAM role ARN (full format) |
| `--account-id` | - | No | AWS Account ID (required for some scan types) |
| `--domain` | - | No | Domain name (required for Microsoft 365 scans) |
| `--log-level` | `--l` | No | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| `--no-cleanup` | - | No | Do not clean up AWS resources after scanning |

### Web Dashboard

Start the FastAPI server:

```bash
quiet-riot-server
```

Or use uvicorn directly:

```bash
uvicorn quiet_riot.api.server:app --host 0.0.0.0 --port 8000 --reload
```

Then open http://localhost:8000 in your browser.

#### API Endpoints

- `GET /` - Dashboard UI
- `GET /api/scan-types` - List available scan types
- `POST /api/scans` - Start a new scan
- `GET /api/scans/{scan_id}` - Get scan status
- `GET /api/scans` - List all scans
- `POST /api/credentials` - Set AWS credentials (profile or ARN)
- `GET /api/credentials` - Get current credential status
- `GET /api/infrastructure` - Get AWS infrastructure resources
- `POST /api/infrastructure/cleanup` - Clean up all AWS resources
- `GET /health` - Health check

#### API Credentials Configuration

Configure credentials via API:

```bash
# Set credentials using profile name
curl -X POST http://localhost:8000/api/credentials \
  -H "Content-Type: application/json" \
  -d '{"profile": "my-profile"}'

# Set credentials using ARN
curl -X POST http://localhost:8000/api/credentials \
  -H "Content-Type: application/json" \
  -d '{"arn": "arn:aws:iam::123456789012:role/MyRole"}'

# Check credential status
curl http://localhost:8000/api/credentials
```

## 📊 Scan Types

1. **AWS Account IDs** - Enumerate valid AWS account IDs
2. **Microsoft 365 Domains** - Check if M365 domain exists
3. **AWS Services Footprinting** - Footprint AWS services
4. **AWS Root User Email** - Enumerate AWS root user email addresses
5. **AWS IAM Principals** - Enumerate IAM roles/users
6. **Microsoft 365 Users** - Enumerate M365 user emails
7. **Google Workspace Users** - _Deprecated._ Google disabled the `gxlu` endpoint this relied on (it now returns HTTP 204 for every address), so this scan reports no users. Kept for compatibility; logs a warning when run.

## 📁 Project Structure

```
quiet_riot/
├── cli/                    # CLI interface
│   └── main.py            # CLI entry point
├── api/                    # FastAPI application
│   ├── server.py          # FastAPI server
│   └── templates/         # HTML templates
│       └── dashboard.html # Web dashboard
├── core/                   # Core business logic
│   ├── models.py          # Data models
│   ├── scanner.py         # Main scanner class
│   ├── enumeration_handlers.py  # Enumeration logic
│   ├── wordlist_handler.py
│   └── result_handler.py
├── enumeration/            # Low-level enumeration modules
│   └── ...
└── aws_credentials.py      # AWS credentials management
```

## ✨ Key Features

### 1. Modern Credentials Management

- **Profile Support**: Use existing AWS profiles from `~/.aws/config`
- **ARN Support**: Automatically create profiles from IAM role ARNs
- **Automatic Profile Creation**: Profiles created from ARNs are reusable
- **Credential Validation**: Validates credentials before use and shows authenticated ARN
- **SSO Ready**: Infrastructure in place for future SSO profile support

### 2. Dual Interface

- **CLI**: Clean command-line interface for automation
- **Web Dashboard**: Modern, interactive UI for exploration

### 3. Modern Build System

- `pyproject.toml` replaces `setup.py`
- Supports both `pipx` and `pip`
- Configured code quality tools (Black, Ruff, MyPy)

### 4. Better Code Organization

- Separation of concerns (CLI, API, Core)
- Reusable business logic
- Type hints and data models
- Proper error handling

### 5. Improved Practices

- Logging instead of print statements
- Configuration singleton pattern
- Resource management with cleanup
- Retry logic with exponential backoff

## 🔧 Development

### Code Quality

```bash
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

### Using Makefile

```bash
make lint        # Run linting
make format      # Format code
make lint-fix    # Auto-fix issues
make test        # Run tests
make all         # Run all checks
```

### Pre-commit Hooks

Pre-commit hooks run automatically on `git commit`:

- **Ruff linting** - Checks code quality
- **Ruff formatting** - Formats code
- **File checks** - Trailing whitespace, end of file, etc.
- **Security checks** - Bandit security scanning

Install pre-commit hooks:

```bash
pip install pre-commit
pre-commit install
```

## 📈 Performance & Throttling

After performing extensive analysis of scaling methods using the AWS Python (Boto3) SDK, I was able to determine that the bottleneck for scanning (at least for Python and awscli-based tools) is I/O capacity of a single-threaded Python application. After modifying the program to run with multiple threads, I was able to trigger exceptions in individual threads due to throttling by the various AWS APIs.

With further testing, I settled on a combination of SNS, ECR-Public, and ECR-Private services running in US-East-1 in ~40%/50%/10% configuration split with ~700 threads. The machine I used was a 2020 Macbook Air (M1 and 16 GB RAM). This configuration yielded on average ~1100 calls/sec, though the actual number of calls can fluctuate significantly depending on a variety of factors including network connectivity.

### Computational Difficulty

To attempt every possible Account ID in AWS (1,000,000,000,000) would require an infeasible amount of time given only one account. Even assuming absolute efficiency*, over the course of a day an attacker will only be able to make 95,040,000 validation checks from their local machine. Over 30 days, this is 2,851,200,000 validation checks and we are still over 28 years away from enumerating every valid AWS Account ID.

*~1100 API calls/check per second in perpetuity per account and never repeating a guessed Account ID.

## 🛠️ Configuration

### AWS Credentials

Quiet Riot uses the AWS credentials manager to handle authentication:

1. **Profile-based**: Uses profiles from `~/.aws/config` or `~/.aws/credentials`
2. **ARN-based**: Creates assume-role profiles automatically from IAM role ARNs
3. **Default fallback**: Tries `default` profile if no credentials specified

The credentials manager validates sessions and provides clear error messages if authentication fails.

## 🔄 Migration Notes

### From Legacy `main.py`

The old monolithic `main.py` has been **removed**. Use the package entry points instead:

- **CLI**: `quiet_riot.cli.main.main()` or the `quiet-riot` command
- **Core logic**: `quiet_riot.core.scanner.Scanner`
- **Config**: `quiet_riot.config.get_config()`
- **Credentials**: `quiet_riot.aws_credentials.get_credentials_manager()`

### Command Line Changes

- Old: `quiet_riot --scan_type 1 --profile my-profile`
- New: `quiet-riot --scan 1 --profile my-profile`

The new CLI is non-interactive and requires all parameters upfront.

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📚 Additional Documentation

- [INSTALLATION.md](INSTALLATION.md) - Detailed installation instructions
- [DEVELOPMENT.md](DEVELOPMENT.md) - Development guide
- [CODE_REVIEW.md](CODE_REVIEW.md) - Code review guidelines
- [.vscode/README.md](.vscode/README.md) - VS Code setup and configuration

## 🔗 Links

- **Homepage**: https://github.com/righteousgambit/quiet-riot
- **Issues**: https://github.com/righteousgambit/quiet-riot/issues
- **Documentation**: https://github.com/righteousgambit/quiet-riot#readme
