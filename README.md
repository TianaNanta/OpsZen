# OpsZen

A comprehensive collection of Python-based DevOps tools for automation, monitoring, and infrastructure management.

## Features

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
│   └── __init__.py
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

- System Management:
  * psutil
  * rich

- Container Management:
  * docker-py

- Infrastructure:
  * boto3
  * pyyaml

- Remote Management:
  * paramiko
  * scp
  * asyncssh

## Security Notes

- SSH connections use AutoAddPolicy for known hosts
- Supports both key-based and password authentication
- Sudo operations require explicit permission
- AWS credentials should be configured via environment variables or AWS CLI
- Docker operations require appropriate permissions

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
