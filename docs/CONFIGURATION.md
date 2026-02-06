# OpsZen Configuration Management

Comprehensive guide to configuring OpsZen for AWS, SSH, Docker, and application settings.

---

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Configuration Hierarchy](#configuration-hierarchy)
4. [Configuration File](#configuration-file)
5. [Environment Variables](#environment-variables)
6. [AWS Configuration](#aws-configuration)
7. [SSH Configuration](#ssh-configuration)
8. [Docker Configuration](#docker-configuration)
9. [Logging Configuration](#logging-configuration)
10. [Application Settings](#application-settings)
11. [Python API](#python-api)
12. [Examples](#examples)
13. [Troubleshooting](#troubleshooting)

---

## Overview

OpsZen provides a flexible, hierarchical configuration system that supports:

- **YAML configuration files** (`config.yaml`)
- **Environment variables** (`.env` files and system env vars)
- **Multiple AWS profiles** for different accounts/regions
- **SSH config integration** (`~/.ssh/config`)
- **Docker daemon configuration** (local and remote)
- **Runtime overrides** via command-line arguments

### Key Features

✅ **Hierarchical configuration** - Defaults → config.yaml → .env → CLI args  
✅ **Multiple profiles** - Switch between AWS accounts, SSH hosts, etc.  
✅ **Environment variable overrides** - Sensitive data stays out of config files  
✅ **Path expansion** - `~` and environment variables automatically expanded  
✅ **Validation** - Built-in config validation with helpful error messages  
✅ **Hot reload** - Reload configuration without restarting  

---

## Quick Start

### 1. Create Your Configuration

```bash
# Copy example config to ~/.opszen/
mkdir -p ~/.opszen
cp config.yaml.example ~/.opszen/config.yaml

# Copy environment template (optional)
cp env.example .env
```

### 2. Edit Configuration

```bash
# Edit with your preferred editor
vim ~/.opszen/config.yaml
```

### 3. Set Environment Variables (Optional)

```bash
# For sensitive data like AWS credentials
echo "AWS_PROFILE=my-profile" >> .env
echo "AWS_REGION=us-east-1" >> .env
```

### 4. Use in Your Code

```python
from src.config import ConfigManager

# Initialize configuration
config = ConfigManager()

# Get values
region = config.get("aws.default_region")
ssh_user = config.get("ssh.default_user")

# Use profiles
prod_profile = config.get_aws_profile("production")
```

---

## Configuration Hierarchy

OpsZen uses a layered configuration system where **higher priority overrides lower priority**:

```
┌─────────────────────────────────────┐
│  1. CLI Arguments (Highest)         │  --region us-east-1
├─────────────────────────────────────┤
│  2. Environment Variables           │  AWS_REGION=us-east-1
├─────────────────────────────────────┤
│  3. config.yaml File                │  aws.default_region: us-east-1
├─────────────────────────────────────┤
│  4. Built-in Defaults (Lowest)      │  us-west-2
└─────────────────────────────────────┘
```

### Configuration Locations

OpsZen searches for `config.yaml` in these locations (in order):

1. Path specified by `OPSZEN_CONFIG` environment variable
2. `~/.opszen/config.yaml` (recommended)
3. `./config.yaml` (current directory)
4. `/etc/opszen/config.yaml` (system-wide)

---

## Configuration File

The `config.yaml` file is the primary configuration source. See `config.yaml.example` for a complete template.

### Basic Structure

```yaml
# AWS Configuration
aws:
  default_profile: default
  default_region: us-west-2
  default_instance_type: t2.micro

# SSH Configuration
ssh:
  default_user: ec2-user
  default_port: 22
  connect_timeout: 10

# Docker Configuration
docker:
  daemon_url: unix:///var/run/docker.sock
  timeout: 60

# Logging Configuration
logging:
  level: INFO
  output_dir: ~/.opszen/logs

# Application Settings
application:
  config_dir: ~/.opszen
  verbose: false
  color_output: true
```

### Dot Notation Access

Access nested configuration using dot notation:

```python
config.get("aws.default_region")           # "us-west-2"
config.get("ssh.default_user")             # "ec2-user"
config.get("logging.level")                # "INFO"
config.get("monitoring.alert_thresholds.cpu")  # 80
```

---

## Environment Variables

Environment variables provide a secure way to configure sensitive data and override settings.

### Loading .env Files

Create a `.env` file in your project root or `~/.opszen/.env`:

```bash
# AWS Credentials
AWS_PROFILE=production
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=AKIAXXXXXXXXXXXXXXXX
AWS_SECRET_ACCESS_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# SSH Configuration
OPSZEN_SSH_USER=ubuntu
OPSZEN_SSH_KEY=~/.ssh/prod_key.pem

# Docker Configuration
DOCKER_HOST=tcp://192.168.1.100:2375

# Application Settings
OPSZEN_LOG_LEVEL=DEBUG
OPSZEN_VERBOSE=1
```

### Supported Environment Variables

#### AWS
- `AWS_PROFILE` - AWS profile name
- `AWS_REGION` / `AWS_DEFAULT_REGION` - AWS region
- `AWS_ACCESS_KEY_ID` - AWS access key
- `AWS_SECRET_ACCESS_KEY` - AWS secret key
- `AWS_SESSION_TOKEN` - Temporary session token

#### SSH
- `OPSZEN_SSH_USER` - Default SSH username
- `OPSZEN_SSH_KEY` - Path to SSH private key
- `OPSZEN_SSH_PASSWORD` - SSH password (not recommended)
- `OPSZEN_SSH_PASSPHRASE` - Passphrase for encrypted keys

#### Docker
- `DOCKER_HOST` - Docker daemon URL
- `DOCKER_TLS_VERIFY` - Enable TLS (1 or 0)
- `DOCKER_CERT_PATH` - Path to TLS certificates

#### Application
- `OPSZEN_CONFIG` - Path to custom config file
- `OPSZEN_LOG_LEVEL` - Logging level (DEBUG, INFO, WARNING, ERROR)
- `OPSZEN_VERBOSE` - Enable verbose mode (1 or 0)
- `OPSZEN_NO_COLOR` - Disable colored output (1 or 0)

---

## AWS Configuration

### Multiple AWS Profiles

Configure multiple AWS profiles for different accounts or environments:

```yaml
aws:
  default_profile: development

  profiles:
    development:
      region: us-west-2
      instance_type: t2.micro
      timeout: 300

    staging:
      region: us-west-2
      instance_type: t2.small
      timeout: 300

    production:
      region: us-east-1
      instance_type: t3.medium
      timeout: 600
```

### Using AWS Profiles

```python
# Get specific profile
prod_config = config.get_aws_profile("production")
print(prod_config["region"])  # us-east-1

# List all profiles
profiles = config.list_aws_profiles()
print(profiles)  # ['development', 'staging', 'production']

# Use AWS CLI profile
os.environ["AWS_PROFILE"] = "production"
```

### Default AWS Settings

```yaml
aws:
  default_profile: default
  default_region: us-west-2
  default_instance_type: t2.micro
  default_ami: ami-0c55b159cbfafe1f0  # Amazon Linux 2
  timeout: 300
  max_retries: 3
```

---

## SSH Configuration

### SSH Config Integration

OpsZen integrates with `~/.ssh/config` and also supports its own host configurations.

```yaml
ssh:
  # Global defaults
  default_user: ec2-user
  default_port: 22
  connect_timeout: 10
  banner_timeout: 30
  auth_timeout: 30

  # SSH config file integration
  config_file: ~/.ssh/config
  use_ssh_config: true

  # Key management
  key_directory: ~/.ssh
  auto_add_host: false

  # Host-specific configurations
  hosts:
    production-web:
      hostname: 10.0.1.100
      user: ubuntu
      port: 2222
      identity_file: ~/.ssh/prod_key.pem

    staging-db:
      hostname: 192.168.1.50
      user: postgres
      port: 22
      identity_file: ~/.ssh/staging_key.pem
```

### Using SSH Configuration

```python
# Get default SSH config
ssh_config = config.get_ssh_config()

# Get host-specific config
web_config = config.get_ssh_config("production-web")
print(web_config["user"])      # ubuntu
print(web_config["port"])      # 2222
```

### SSH Config File (~/.ssh/config)

OpsZen reads and respects `~/.ssh/config`:

```
Host production-web
    HostName 10.0.1.100
    User ubuntu
    Port 2222
    IdentityFile ~/.ssh/prod_key.pem

Host *.example.com
    User ec2-user
    ForwardAgent yes
```

---

## Docker Configuration

### Local Docker Daemon

```yaml
docker:
  daemon_url: unix:///var/run/docker.sock
  timeout: 60
  tls_verify: false
  default_network: bridge
  auto_remove: false
  pull_policy: missing  # always, missing, never
```

### Remote Docker Daemon

```yaml
docker:
  daemon_url: tcp://192.168.1.100:2375
  timeout: 60
  tls_verify: false
```

### Docker with TLS

```yaml
docker:
  daemon_url: tcp://192.168.1.100:2376
  timeout: 60
  tls_verify: true
  cert_path: ~/.docker/certs
```

### Using Docker Configuration

```python
# Get Docker config
docker_config = config.get_docker_config()
print(docker_config["daemon_url"])

# Set via environment variable
os.environ["DOCKER_HOST"] = "tcp://192.168.1.100:2375"
```

---

## Logging Configuration

### Log Settings

```yaml
logging:
  level: INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
  format: generic  # generic, json, syslog, apache, python
  output_dir: ~/.opszen/logs
  max_file_size: 10MB
  backup_count: 5
  console_output: true
  filename_pattern: "opszen_{date}.log"
```

### Log Levels via Environment

```bash
export OPSZEN_LOG_LEVEL=DEBUG
```

---

## Application Settings

### General Settings

```yaml
application:
  # Directories
  config_dir: ~/.opszen
  data_dir: ~/.opszen/data
  cache_dir: ~/.opszen/cache

  # Files
  profiles_file: ~/.opszen/profiles.yaml
  history_file: ~/.opszen/history.log

  # UI Settings
  theme: auto  # auto, light, dark
  color_output: true
  verbose: false
  debug: false

  # Features
  check_updates: true
  history_size: 1000
```

### Monitoring Settings

```yaml
monitoring:
  refresh_interval: 5
  history_size: 100

  alert_thresholds:
    cpu: 80
    memory: 85
    disk: 90
```

---

## Python API

### Basic Usage

```python
from src.config import ConfigManager

# Initialize with default config file
config = ConfigManager()

# Or specify a custom config file
config = ConfigManager(
    config_file="~/.opszen/custom.yaml",
    load_env=True,
    create_dirs=True
)
```

### Getting Values

```python
# Get with dot notation
region = config.get("aws.default_region")

# Get with default value
timeout = config.get("aws.timeout", 300)

# Get entire section
aws_config = config.get_section("aws")
```

### Setting Values

```python
# Set a value
config.set("aws.default_region", "us-east-1")

# Set nested value
config.set("custom.nested.key", "value")
```

### Saving Configuration

```python
# Save to file (creates backup)
config.save_config()

# Save without backup
config.save_config(backup=False)
```

### Reloading Configuration

```python
# Reload from file
config.reload()
```

### Validation

```python
# Validate current configuration
is_valid = config.validate()

if not is_valid:
    print("Configuration has errors!")
```

### Printing Configuration

```python
# Print all configuration
config.print_config()

# Print specific section
config.print_config(section="aws")
```

---

## Examples

### Example 1: AWS Multi-Profile Setup

```yaml
# ~/.opszen/config.yaml
aws:
  default_profile: development

  profiles:
    development:
      region: us-west-2
      instance_type: t2.micro

    production:
      region: us-east-1
      instance_type: m5.large
```

```python
from src.config import ConfigManager

config = ConfigManager()

# Switch between profiles
dev_config = config.get_aws_profile("development")
prod_config = config.get_aws_profile("production")

print(f"Dev: {dev_config['region']}")   # us-west-2
print(f"Prod: {prod_config['region']}")  # us-east-1
```

### Example 2: Environment-Based Configuration

```bash
# .env
AWS_PROFILE=production
AWS_REGION=eu-west-1
OPSZEN_LOG_LEVEL=DEBUG
OPSZEN_VERBOSE=1
```

```python
config = ConfigManager(load_env=True)

# Environment variables override config file
print(config.get("aws.default_region"))  # eu-west-1 (from .env)
print(config.get("logging.level"))       # DEBUG (from .env)
```

### Example 3: SSH Host Configuration

```yaml
ssh:
  default_user: ec2-user

  hosts:
    web-server:
      hostname: 10.0.1.10
      user: ubuntu
      port: 2222

    db-server:
      hostname: 10.0.2.20
      user: postgres
```

```python
# Get host-specific config
web_config = config.get_ssh_config("web-server")
db_config = config.get_ssh_config("db-server")

print(web_config["user"])  # ubuntu
print(db_config["user"])   # postgres
```

---

## Troubleshooting

### Configuration Not Loading

**Problem:** Configuration file not being loaded

**Solutions:**
1. Check file location: `~/.opszen/config.yaml`
2. Verify file permissions: `chmod 644 ~/.opszen/config.yaml`
3. Check YAML syntax: Use a YAML validator
4. Set `OPSZEN_CONFIG` to specify custom path

### Environment Variables Not Working

**Problem:** Environment variables not overriding config

**Solutions:**
1. Ensure `.env` file is in project root or `~/.opszen/`
2. Check variable names (case-sensitive)
3. Verify `load_env=True` in ConfigManager
4. Export variables: `export AWS_REGION=us-east-1`

### Invalid Configuration

**Problem:** Validation errors

**Solutions:**
1. Run `config.validate()` to see specific errors
2. Check required fields are not empty
3. Verify numeric values are positive
4. Use `config.print_config()` to inspect current values

### Path Issues

**Problem:** Paths not expanding correctly

**Solutions:**
1. Use `~` for home directory (automatically expanded)
2. Use absolute paths when possible
3. Check directory permissions
4. Verify paths exist: `ls -la ~/.opszen/`

### AWS Profile Issues

**Problem:** AWS profile not found

**Solutions:**
1. List available profiles: `config.list_aws_profiles()`
2. Check profile name spelling
3. Verify profile exists in config.yaml
4. Use AWS CLI profile: `aws configure --profile myprofile`

---

## Best Practices

### Security

✅ **DO:**
- Store credentials in `.env` files (add to `.gitignore`)
- Use AWS IAM roles when possible
- Use SSH keys instead of passwords
- Encrypt sensitive configuration files

❌ **DON'T:**
- Commit `.env` files to version control
- Store passwords in `config.yaml`
- Share AWS credentials in plain text
- Use overly permissive file permissions

### Organization

✅ **DO:**
- Use separate profiles for dev/staging/prod
- Group related settings in sections
- Use meaningful profile names
- Document custom settings

❌ **DON'T:**
- Mix development and production settings
- Use hardcoded values in code
- Create overly complex configurations
- Ignore configuration validation errors

### Performance

✅ **DO:**
- Initialize ConfigManager once and reuse
- Use config.get() for frequently accessed values
- Set reasonable timeouts
- Cache configuration values if needed

❌ **DON'T:**
- Create new ConfigManager instances unnecessarily
- Read config files repeatedly
- Use very long timeouts
- Ignore performance warnings

---

## Additional Resources

- [config.yaml.example](../config.yaml.example) - Full configuration template
- [env.example](../env.example) - Environment variables template
- [AWS Configuration](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html)
- [SSH Config File](https://www.ssh.com/academy/ssh/config)
- [Docker Environment Variables](https://docs.docker.com/engine/reference/commandline/cli/#environment-variables)

---

**Last Updated:** 2024  
**Version:** 1.0  
**Maintained by:** OpsZen Team
