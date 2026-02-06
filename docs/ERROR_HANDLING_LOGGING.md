# OpsZen Error Handling & Logging Guide

Complete guide to error handling, custom exceptions, and structured logging in OpsZen.

---

## Table of Contents

1. [Overview](#overview)
2. [Custom Exceptions](#custom-exceptions)
3. [Structured Logging](#structured-logging)
4. [Retry Logic](#retry-logic)
5. [Best Practices](#best-practices)
6. [Examples](#examples)
7. [Troubleshooting](#troubleshooting)

---

## Overview

OpsZen implements comprehensive error handling and logging with:

- **Custom exception hierarchy** for descriptive error messages
- **Structured logging** with file rotation and multiple formats
- **Retry logic** with exponential backoff for network operations
- **Log files** in `~/.opszen/logs/` with automatic rotation
- **Multiple log levels** (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- **Rich console output** with colors and formatting

### Key Features

✅ Hierarchical exception types for different error categories  
✅ Automatic log file rotation based on size  
✅ JSON, standard, and detailed log formats  
✅ Retry decorator with exponential backoff  
✅ Colored console logging with Rich  
✅ Structured error details for debugging  

---

## Custom Exceptions

### Exception Hierarchy

```
OpsZenError (base)
├── ConfigurationError
│   ├── ConfigFileNotFoundError
│   └── ConfigValidationError
├── SSHError
│   ├── SSHConnectionError
│   ├── SSHAuthenticationError
│   ├── SSHCommandError
│   └── SSHFileTransferError
├── DockerError
│   ├── DockerConnectionError
│   ├── DockerContainerError
│   ├── DockerImageError
│   └── DockerNetworkError
├── AWSError
│   ├── AWSConnectionError
│   ├── AWSAuthenticationError
│   ├── EC2Error
│   └── S3Error
├── LogAnalysisError
│   ├── LogFileNotFoundError
│   ├── LogParseError
│   └── LogFilterError
├── NetworkError
│   ├── ConnectionTimeoutError
│   └── RetryExhaustedError
├── MonitoringError
│   └── MetricCollectionError
├── ValidationError
│   ├── InvalidInputError
│   └── InvalidPathError
└── OperationError
    ├── OperationTimeoutError
    └── OperationCancelledError
```

### Using Exceptions

```python
from src.exceptions import (
    SSHConnectionError,
    DockerContainerError,
    EC2Error,
    RetryExhaustedError,
)

# Raise exception with message only
raise SSHConnectionError("Failed to connect to server")

# Raise with additional details
raise SSHCommandError(
    "Command execution failed",
    command="ls -la",
    exit_code=127
)

# Raise with context dictionary
raise DockerContainerError(
    "Container failed to start",
    container_id="abc123",
    details={"image": "nginx:latest", "ports": [80, 443]}
)
```

### Exception Details

All OpsZen exceptions support a `details` dictionary for additional context:

```python
from src.exceptions import EC2Error

try:
    # Some AWS operation
    pass
except Exception as e:
    raise EC2Error(
        "Failed to launch instance",
        instance_id="i-123456",
        details={
            "region": "us-west-2",
            "instance_type": "t2.micro",
            "ami": "ami-abc123"
        }
    )

# Exception string includes details:
# "Failed to launch instance (instance_id=i-123456, region=us-west-2, ...)"
```

### Catching Exceptions

```python
from src.exceptions import SSHError, DockerError, OpsZenError

# Catch specific exception
try:
    ssh_manager.connect(host)
except SSHConnectionError as e:
    print(f"SSH connection failed: {e}")
    print(f"Details: {e.details}")

# Catch category of exceptions
try:
    docker_manager.create_container(...)
except DockerError as e:
    print(f"Docker operation failed: {e}")

# Catch all OpsZen exceptions
try:
    perform_operation()
except OpsZenError as e:
    print(f"OpsZen error: {e}")
    if e.details:
        for key, value in e.details.items():
            print(f"  {key}: {value}")
```

---

## Structured Logging

### Setup

```python
from src.logging import setup_logging, get_logger

# Configure logging (call once at startup)
setup_logging(
    log_dir="~/.opszen/logs",      # Log directory
    log_level="INFO",                # Log level
    console_output=True,             # Enable console logging
    file_output=True,                # Enable file logging
    log_format="standard",           # Format: standard, json, detailed
    max_bytes=10*1024*1024,         # Max file size (10MB)
    backup_count=5                   # Number of backup files
)

# Get logger for your module
logger = get_logger(__name__)
```

### Using Loggers

```python
from src.logging import get_logger

logger = get_logger(__name__)

# Log at different levels
logger.debug("Detailed debug information")
logger.info("General information message")
logger.warning("Warning about potential issue")
logger.error("Error occurred")
logger.critical("Critical error!")

# Log with exception info
try:
    risky_operation()
except Exception as e:
    logger.error("Operation failed", exc_info=True)

# Log with extra context
logger.info("User logged in", extra={"user_id": 123, "ip": "192.168.1.1"})
```

### Log Levels

| Level | Description | Use Case |
|-------|-------------|----------|
| `DEBUG` | Detailed diagnostic info | Development, troubleshooting |
| `INFO` | General informational messages | Normal operations, confirmations |
| `WARNING` | Warning about potential issues | Deprecations, recoverable errors |
| `ERROR` | Error events | Operation failures, exceptions |
| `CRITICAL` | Critical errors | System failures, data loss |

### Log Formats

#### Standard Format
```
2024-01-15 10:30:45 | INFO     | my_module | User logged in successfully
2024-01-15 10:30:46 | ERROR    | my_module | Database connection failed
```

#### Detailed Format
```
2024-01-15 10:30:45 | my_module | INFO     | connect_user:45 | User logged in
2024-01-15 10:30:46 | my_module | ERROR    | query_db:123   | Query failed
```

#### JSON Format
```json
{"timestamp": "2024-01-15T10:30:45", "level": "INFO", "logger": "my_module", "message": "User logged in"}
{"timestamp": "2024-01-15T10:30:46", "level": "ERROR", "logger": "my_module", "message": "Query failed", "exception": "..."}
```

### Log File Management

```python
from src.logging import get_log_files, clear_logs, set_log_level

# List all log files
log_files = get_log_files()
for log_file in log_files:
    print(log_file)

# Change log level at runtime
set_log_level("DEBUG")

# Clear all log files
clear_logs()
```

### Log Rotation

Logs are automatically rotated when they reach the maximum size:

- **Default max size**: 10MB
- **Backup count**: 5 files
- **Naming**: `module_name.log`, `module_name.log.1`, `module_name.log.2`, etc.

---

## Retry Logic

### Retry Decorator

Use the `@retry` decorator for operations that may fail temporarily:

```python
from src.utils import retry
from src.exceptions import NetworkError

@retry(max_attempts=3, delay=1.0, backoff=2.0)
def connect_to_api():
    response = requests.get("https://api.example.com/data")
    return response.json()

# Will retry up to 3 times with exponential backoff
# Delays: 1s, 2s, 4s
data = connect_to_api()
```

### Retry Configuration

```python
from src.utils import retry

@retry(
    max_attempts=5,              # Maximum retry attempts
    delay=2.0,                   # Initial delay in seconds
    backoff=2.0,                 # Backoff multiplier (exponential)
    exceptions=(ConnectionError, TimeoutError),  # Exceptions to catch
    on_retry=lambda attempt, e: print(f"Retry {attempt}")  # Callback
)
def unreliable_operation():
    # Your code here
    pass
```

### Retry Examples

#### SSH Connection with Retry

```python
from src.utils import retry
from src.exceptions import SSHConnectionError

@retry(max_attempts=3, delay=2, exceptions=(SSHConnectionError,))
def connect_to_server(host, user):
    ssh_manager = SSHManager()
    return ssh_manager.connect(host, user)
```

#### AWS API with Retry

```python
from src.utils import retry
from src.exceptions import AWSConnectionError

@retry(
    max_attempts=5,
    delay=1.0,
    backoff=2.0,
    exceptions=(AWSConnectionError, ConnectionTimeoutError)
)
def create_ec2_instance(config):
    provisioner = InfrastructureProvisioner()
    return provisioner.create_ec2_instance(config)
```

#### Custom Retry Callback

```python
from src.utils import retry
from src.logging import get_logger

logger = get_logger(__name__)

def on_retry_callback(attempt, exception):
    logger.warning(f"Retry attempt {attempt} after error: {exception}")

@retry(
    max_attempts=3,
    delay=1.0,
    on_retry=on_retry_callback,
    exceptions=(NetworkError,)
)
def fetch_data():
    # Fetch data from remote source
    pass
```

### Retry Exhausted

When all retries are exhausted, a `RetryExhaustedError` is raised:

```python
from src.utils import retry
from src.exceptions import RetryExhaustedError

@retry(max_attempts=3, delay=1)
def failing_operation():
    raise ValueError("Always fails")

try:
    failing_operation()
except RetryExhaustedError as e:
    print(f"Operation failed after {e.details['attempts']} attempts")
```

---

## Best Practices

### Error Handling

✅ **DO:**
- Use specific exception types for different error categories
- Include helpful details in exception messages
- Log exceptions with `exc_info=True` for stack traces
- Catch specific exceptions rather than bare `except:`
- Re-raise with context using `raise ... from e`

❌ **DON'T:**
- Use generic `Exception` for all errors
- Swallow exceptions silently
- Log and re-raise (choose one)
- Use exceptions for control flow
- Include sensitive data in error messages

### Logging

✅ **DO:**
- Get module-specific loggers: `logger = get_logger(__name__)`
- Use appropriate log levels
- Include context in log messages
- Log exceptions with stack traces
- Set up logging early in application startup

❌ **DON'T:**
- Use `print()` statements in production code
- Log sensitive information (passwords, keys)
- Over-log (DEBUG level in production)
- Forget to rotate large log files
- Log the same event multiple times

### Retry Logic

✅ **DO:**
- Use retry for network/remote operations
- Set reasonable max_attempts (3-5 typically)
- Use exponential backoff for retries
- Log retry attempts
- Specify which exceptions to retry

❌ **DON'T:**
- Retry operations that can't succeed (bad auth)
- Use infinite retries
- Retry without backoff
- Retry on all exceptions
- Hide retry logic from callers

---

## Examples

### Complete Module with Error Handling and Logging

```python
from src.logging import get_logger
from src.utils import retry
from src.exceptions import (
    SSHConnectionError,
    SSHCommandError,
    RetryExhaustedError
)

logger = get_logger(__name__)

class DeploymentManager:
    """Manages application deployments with proper error handling."""

    def __init__(self):
        self.ssh_manager = SSHManager()
        logger.info("DeploymentManager initialized")

    @retry(max_attempts=3, delay=2, exceptions=(SSHConnectionError,))
    def connect(self, host, user):
        """Connect to remote server with retry logic."""
        logger.info(f"Connecting to {host} as {user}")
        try:
            self.ssh_manager.connect(host, user)
            logger.info(f"Successfully connected to {host}")
        except SSHConnectionError as e:
            logger.error(f"Connection failed: {e}", exc_info=True)
            raise

    def deploy(self, app_name, version):
        """Deploy application with comprehensive error handling."""
        logger.info(f"Starting deployment: {app_name} v{version}")

        try:
            # Execute deployment commands
            result = self._run_deployment_commands(app_name, version)
            logger.info(f"Deployment successful: {app_name} v{version}")
            return result

        except SSHCommandError as e:
            logger.error(
                f"Deployment command failed: {e.details.get('command')}",
                exc_info=True
            )
            raise

        except RetryExhaustedError as e:
            logger.critical(
                f"Deployment failed after {e.details['attempts']} attempts"
            )
            raise

        except Exception as e:
            logger.critical(
                f"Unexpected error during deployment: {e}",
                exc_info=True
            )
            raise

    def _run_deployment_commands(self, app_name, version):
        """Execute deployment commands."""
        commands = [
            f"cd /opt/{app_name}",
            f"git pull origin v{version}",
            "pip install -r requirements.txt",
            "systemctl restart app"
        ]

        for cmd in commands:
            logger.debug(f"Executing: {cmd}")
            try:
                result = self.ssh_manager.execute_command(cmd)
                logger.debug(f"Command output: {result}")
            except SSHCommandError as e:
                logger.error(f"Command failed: {cmd}")
                raise

        return {"status": "success", "version": version}
```

### Application Startup with Logging Configuration

```python
from src.logging import setup_logging, get_logger
from src.config import ConfigManager

def main():
    # Load configuration
    config = ConfigManager()

    # Setup logging from config
    setup_logging(
        log_dir=config.get("logging.output_dir", "~/.opszen/logs"),
        log_level=config.get("logging.level", "INFO"),
        log_format=config.get("logging.format", "standard"),
        max_bytes=10*1024*1024,
        backup_count=5
    )

    # Get logger
    logger = get_logger(__name__)

    logger.info("=" * 50)
    logger.info("OpsZen Application Starting")
    logger.info("=" * 50)

    try:
        # Run application
        run_app()
        logger.info("Application completed successfully")

    except Exception as e:
        logger.critical("Application failed", exc_info=True)
        raise

    finally:
        logger.info("=" * 50)
        logger.info("OpsZen Application Shutdown")
        logger.info("=" * 50)

if __name__ == "__main__":
    main()
```

---

## Troubleshooting

### Log Files Not Created

**Problem:** No log files appear in `~/.opszen/logs/`

**Solutions:**
1. Check `setup_logging()` was called with `file_output=True`
2. Verify directory permissions: `ls -la ~/.opszen/`
3. Check log directory path is correct
4. Ensure logger is actually being used: `logger.info("test")`

### Logs Not Appearing in Console

**Problem:** Console output is missing

**Solutions:**
1. Verify `console_output=True` in `setup_logging()`
2. Check log level isn't filtering messages: `set_log_level("DEBUG")`
3. Ensure Rich library is installed: `pip install rich`

### Retry Not Working

**Problem:** Operations don't retry

**Solutions:**
1. Check exception type matches `exceptions` parameter
2. Verify `max_attempts > 1`
3. Check if exception is being caught elsewhere
4. Add logging to `on_retry` callback to verify retries

### Log Files Too Large

**Problem:** Log files growing too large

**Solutions:**
1. Reduce `max_bytes` in `setup_logging()`
2. Increase `backup_count` for more rotation
3. Use log level filtering: set to INFO or WARNING
4. Implement log cleanup script
5. Use `clear_logs()` periodically

### Exception Details Missing

**Problem:** Exception details not showing

**Solutions:**
1. Ensure using OpsZen exceptions, not base `Exception`
2. Pass `details` parameter when raising
3. Use `exc_info=True` when logging
4. Check exception string representation

---

## Configuration Integration

### Loading Logging Config from config.yaml

```python
from src.config import ConfigManager
from src.logging import setup_logging

config = ConfigManager()

setup_logging(
    log_dir=config.get("logging.output_dir"),
    log_level=config.get("logging.level"),
    log_format=config.get("logging.format"),
    max_bytes=config.get("logging.max_file_size_bytes", 10*1024*1024),
    backup_count=config.get("logging.backup_count", 5)
)
```

### config.yaml Example

```yaml
logging:
  level: INFO
  format: standard  # standard, json, detailed
  output_dir: ~/.opszen/logs
  max_file_size_bytes: 10485760  # 10MB
  backup_count: 5
  console_output: true
  file_output: true
```

---

## API Reference

### Exceptions

- `OpsZenError(message, details=None)` - Base exception
- `ConfigurationError`, `SSHError`, `DockerError`, `AWSError`, etc. - Category exceptions
- All exceptions support `details` dict for additional context

### Logging Functions

- `setup_logging(...)` - Configure logging system
- `get_logger(name)` - Get module logger
- `set_log_level(level)` - Change log level
- `get_log_files()` - List log files
- `clear_logs()` - Delete all log files

### Retry Decorator

- `@retry(max_attempts, delay, backoff, exceptions, on_retry)` - Retry with exponential backoff

---

**Last Updated:** 2024  
**Version:** 1.0  
**See Also:** [Configuration Guide](./CONFIGURATION.md), [Development Guide](../README.md)
