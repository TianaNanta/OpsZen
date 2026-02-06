# OpsZen

A comprehensive collection of Python-based DevOps tools for automation, monitoring, and infrastructure management.

## Features

- **Configuration Management** ⭐ NEW!
  * Centralized YAML configuration (config.yaml)
  * Environment variable support (.env files)
  * Multiple AWS profiles (dev/staging/prod)
  * SSH config integration (~/.ssh/config)
  * Docker daemon configuration
  * Hierarchical settings with validation

- System Monitoring
  * Real-time CPU, memory, disk, and network metrics
  * System health checks
  * Performance monitoring and alerts

- Docker Container Management
  * List, create, stop, and remove containers
  * Container health monitoring
  * Port mapping management

- Log Analysis
  * Parse and analyze log files
  * Extract patterns and metrics
  * Generate log summaries

- Infrastructure Provisioning
  * AWS EC2 instance management
  * S3 bucket operations
  * Infrastructure as Code (IaC)

- SSH Remote Management
  * Secure remote command execution
  * File upload and download
  * Remote directory operations
  * Support for key and password authentication

## Installation

This project uses `uv` as the package manager. To install:

```bash
# Create a new virtual environment and install the package
uv venv
source .venv/bin/activate
uv sync --no-dev

# Or install in development mode with all dependencies
uv sync
```

## Configuration

OpsZen uses a flexible configuration system with support for YAML files and environment variables.

### Quick Setup

```bash
# 1. Copy example configuration
mkdir -p ~/.opszen
cp config.yaml.example ~/.opszen/config.yaml

# 2. (Optional) Set up environment variables
cp env.example .env
```

### Configuration Files

- **config.yaml** - Main configuration file (AWS, SSH, Docker, logging settings)
- **.env** - Environment variables for sensitive data (credentials, API keys)

### Example Configuration

```yaml
# ~/.opszen/config.yaml
aws:
  default_profile: development
  default_region: us-west-2
  profiles:
    development:
      region: us-west-2
      instance_type: t2.micro
    production:
      region: us-east-1
      instance_type: t3.large

ssh:
  default_user: ec2-user
  use_ssh_config: true
  hosts:
    web-server:
      hostname: 10.0.1.100
      user: ubuntu

docker:
  daemon_url: unix:///var/run/docker.sock
  timeout: 60
```

### Environment Variables

```bash
# .env file
AWS_PROFILE=production
AWS_REGION=us-east-1
OPSZEN_SSH_USER=ubuntu
DOCKER_HOST=tcp://192.168.1.100:2375
OPSZEN_LOG_LEVEL=DEBUG
```

### Using Configuration in Python

```python
from src.config import ConfigManager

# Initialize configuration
config = ConfigManager()

# Get values with dot notation
region = config.get("aws.default_region")
ssh_user = config.get("ssh.default_user")

# Use AWS profiles
prod_config = config.get_aws_profile("production")

# Get host-specific SSH config
web_config = config.get_ssh_config("web-server")

# Validate configuration
if config.validate():
    print("Configuration is valid!")

# Display configuration
config.print_config()
```

### Configuration Documentation

- 📖 [Complete Configuration Guide](./docs/CONFIGURATION.md) - Full documentation
- 📋 [Quick Reference](./docs/CONFIG_QUICK_REF.md) - One-page cheat sheet
- 📄 [config.yaml.example](./config.yaml.example) - Template with all options
- 📄 [env.example](./env.example) - Environment variables template

## CLI Usage

The toolkit provides a command-line interface for all features:

### System Monitoring
```bash
# Start continuous monitoring
opszen monitor start --interval 5

# Take a system snapshot
opszen monitor snapshot
```

### Docker Management
```bash
# List containers
opszen docker list
opszen docker list --all  # Include stopped containers

# Create container
opszen docker create nginx --name my-nginx --port 80:80

# Stop container
opszen docker stop my-nginx

# Remove container
opszen docker remove my-nginx --force
```

### Log Analysis
```bash
# Analyze logs with comprehensive statistics
opszen logs analyze /path/to/logfile.log
opszen logs analyze /var/log/syslog --max-lines 10000

# Filter logs by level (ERROR and above)
opszen logs filter /path/to/logfile.log --level ERROR

# Filter by time range
opszen logs filter /path/to/logfile.log --start "2024-01-01 00:00:00" --end "2024-01-02 00:00:00"

# Filter by pattern (regex)
opszen logs filter /path/to/logfile.log --pattern "database.*error"

# Exclude specific patterns
opszen logs filter /path/to/logfile.log --exclude "DEBUG"

# Combine filters and export results
opszen logs filter /path/to/logfile.log --level WARNING --pattern "timeout" --output errors.json
opszen logs filter /path/to/logfile.log --level ERROR --output errors.csv

# Tail logs (like tail -f)
opszen logs tail /path/to/logfile.log --lines 20
opszen logs tail /path/to/logfile.log --follow

# Export logs to different formats
opszen logs export /path/to/logfile.log output.json --format json
opszen logs export /path/to/logfile.log output.csv --format csv
opszen logs export /path/to/logfile.log output.txt --format text
```

### Infrastructure Management
```bash
# List EC2 instances
opszen infra list-ec2

# List S3 buckets
opszen infra list-s3

# Create EC2 instance
opszen infra create-ec2 --name web-server --image-id ami-xxxxx

# Create S3 bucket
opszen infra create-s3 my-bucket --region us-west-2

# Provision from config
opszen infra provision config.yaml
```

### SSH Remote Management (New Intuitive Interface!)
```bash
# Save a server profile for quick access
opszen ssh save prod admin@prod.example.com --key ~/.ssh/id_rsa
opszen ssh save dev user@192.168.1.100

# Run commands with SSH KEY
opszen ssh run user@server.com "ls -la"
opszen ssh run prod "systemctl restart nginx" --sudo

# Run commands with PASSWORD (use -p or --password)
opszen ssh run user@server.com "ls -la" --password mypassword
opszen ssh run user@server "apt update" --sudo -p mypass

# Copy files with PASSWORD
opszen ssh copy ./file.txt user@server:/tmp/ --password mypass
opszen ssh copy user@server:/var/log/app.log ./logs/ -p mypass

# Copy files with SSH key
opszen ssh copy ./file.txt user@server:/tmp/
opszen ssh copy prod:~/data.txt ./

# Execute local scripts (with password)
opszen ssh exec user@server deploy.sh --password mypass
opszen ssh exec prod backup.sh --sudo -p prodpass

# Interactive shell with password
opszen ssh shell user@server.com --password mypass
opszen ssh shell prod -p prodpass

# Manage saved profiles
opszen ssh profiles              # List all saved profiles
opszen ssh delete old-server     # Remove a profile

# Password works with ALL commands!
# See SSH_GUIDE.md for complete documentation
# See SSH_PASSWORD_AUTH.md for password authentication guide
```

## Project Structure

```
opszen/
├── src/
│   ├── cli.py                 # Command-line interface
│   ├── config/                # ⭐ Configuration management (NEW!)
│   │   ├── __init__.py
│   │   ├── config_manager.py  # Main configuration manager
│   │   └── config_loader.py   # Config file loader utilities
│   ├── monitoring/
│   │   ├── __init__.py
│   │   └── system_monitor.py
│   ├── container/
│   │   ├── __init__.py
│   │   └── docker_manager.py
│   ├── logs/
│   │   ├── __init__.py
│   │   └── log_analyzer.py
│   ├── infrastructure/
│   │   ├── __init__.py
│   │   └── provisioner.py
│   └── remote/
│       ├── __init__.py
│       └── ssh_manager.py
├── tests/
│   ├── unit/
│   │   ├── config/            # ⭐ Configuration tests (NEW!)
│   │   │   ├── test_config_manager.py
│   │   │   └── test_config_loader.py
│   │   └── ...
│   └── __init__.py
├── docs/                      # ⭐ Documentation (NEW!)
│   ├── CONFIGURATION.md       # Complete configuration guide
│   └── CONFIG_QUICK_REF.md    # Quick reference
├── config.yaml.example        # ⭐ Configuration template (NEW!)
├── env.example                # ⭐ Environment variables template (NEW!)
├── pyproject.toml            # Project configuration and dependencies
└── README.md
```

## Requirements

- Python 3.8+
- uv package manager
- Docker (for container management features)
- AWS credentials (for infrastructure management)
- SSH key or password authentication (for remote management)

## Core Dependencies

- Configuration Management:
  * pyyaml - YAML configuration files
  * python-dotenv - Environment variable loading

- System Management:
  * psutil - System metrics
  * rich - Beautiful console output

- Container Management:
  * docker-py - Docker API client

- Infrastructure:
  * boto3 - AWS SDK
  * pyyaml - YAML parsing

- Remote Management:
  * paramiko - SSH client
  * scp - Secure copy
  * asyncssh - Async SSH operations

## Security Notes

- **Configuration Files**: Keep `config.yaml` at `chmod 600` for sensitive data
- **.env Files**: Never commit `.env` files to version control (add to `.gitignore`)
- **AWS Credentials**: Store in `.env` or use AWS IAM roles (preferred)
- **SSH Authentication**: Supports both key-based (recommended) and password authentication
- **SSH Connections**: Use AutoAddPolicy for known hosts
- **Sudo Operations**: Require explicit permission flag
- **Docker Operations**: Require appropriate user permissions or group membership

## Development

To set up the development environment:

```bash
# Clone the repository
git clone https://github.com/TianaNanta/OpsZen.git
cd OpsZen

# Create a virtual environment and install dependencies
uv venv
source .venv/bin/activate
uv sync

## Development Setup

This project uses modern Python development tools for code quality and consistency.

### Code Quality Tools

- **[Ruff](https://github.com/astral-sh/ruff)** - Fast Python linter and formatter (replaces Black, isort, Flake8)
- **[Pre-commit](https://pre-commit.com/)** - Git hooks for automated code checks
- **[Prek](https://github.com/j178/prek)** - Enhanced pre-commit CLI

### Quick Start for Contributors

```bash
# 1. Install development dependencies
make install-dev

# 2. Install pre-commit hooks
make precommit-install

# 3. Format and lint code
make format

# 4. Run tests
make test
```

### Common Development Commands

```bash
# Code formatting and linting
make format              # Format code with ruff
make lint                # Lint with auto-fix
make check               # Check without changes

# Pre-commit hooks
make precommit           # Run on staged files
make precommit-all       # Run on all files

# Testing
make test                # Run all tests
make test-unit           # Run unit tests only
make test-coverage       # Run with coverage report

# Quick development cycle
make quick               # Format + fast tests
make fix                 # Auto-fix all issues
make ci                  # Run full CI pipeline locally
```

### Helper Scripts

```bash
./format.sh              # Ruff formatting/linting
./precommit.sh           # Pre-commit hook runner
./run_tests.sh           # Test runner with venv support
```

### Documentation

**Configuration:**
- [docs/CONFIGURATION.md](./docs/CONFIGURATION.md) - Complete configuration guide
- [docs/CONFIG_QUICK_REF.md](./docs/CONFIG_QUICK_REF.md) - Configuration quick reference
- [CONFIG_IMPLEMENTATION_SUMMARY.md](./CONFIG_IMPLEMENTATION_SUMMARY.md) - Implementation details

**Development:**
- [PRECOMMIT_SETUP.md](./PRECOMMIT_SETUP.md) - Complete pre-commit and ruff setup guide
- [QUICK_REFERENCE_PRECOMMIT.md](./QUICK_REFERENCE_PRECOMMIT.md) - Quick command reference
- [TESTING.md](./TESTING.md) - Testing documentation
- [TEST_FIX_SUMMARY.md](./TEST_FIX_SUMMARY.md) - Test suite fixes and improvements

### Running Tests

```bash
# All tests
make test

# Specific test categories
make test-unit           # Unit tests only
make test-integration    # Integration tests
make test-fast           # Parallel execution

# Coverage
make test-coverage       # With coverage report
make test-report         # Generate HTML report

# Module-specific
make test-docker         # Docker tests
make test-ssh            # SSH tests
make test-logs           # Log analyzer tests
```

### Code Quality Standards

- Line length: 88 characters (Black compatible)
- Import sorting: Automatic with ruff
- Type hints: Recommended for new code
- Docstrings: Required for public APIs
- Test coverage: Aim for >70%

---
