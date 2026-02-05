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

### SSH Remote Management
```bash
# Execute commands on remote hosts
opszen ssh execute example.com username "ls -la" --key ~/.ssh/id_rsa
opszen ssh execute example.com username "apt update" --sudo --password mypass

# File operations
opszen ssh upload example.com username ./local/file.txt /remote/path/
opszen ssh download example.com username /remote/file.txt ./local/path/

# Directory operations
opszen ssh ls example.com username /remote/path/

# Multiple commands
opszen ssh execute example.com username "cd /opt && ./deploy.sh" --key ~/.ssh/id_rsa
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
