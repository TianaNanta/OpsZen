# OpsZen Configuration Quick Reference

A one-page quick reference for OpsZen configuration management.

---

## Setup (30 seconds)

```bash
# Copy templates
mkdir -p ~/.opszen
cp config.yaml.example ~/.opszen/config.yaml
cp env.example .env

# Edit as needed
vim ~/.opszen/config.yaml
```

---

## Python API

```python
from src.config import ConfigManager

# Initialize
config = ConfigManager()

# Get values (dot notation)
region = config.get("aws.default_region")
user = config.get("ssh.default_user", "ec2-user")

# Set values
config.set("aws.default_region", "us-east-1")

# Get sections
aws_config = config.get_section("aws")
ssh_config = config.get_ssh_config()
docker_config = config.get_docker_config()

# AWS profiles
prod = config.get_aws_profile("production")
profiles = config.list_aws_profiles()

# SSH host-specific
web = config.get_ssh_config("web-server")

# Save/reload
config.save_config()
config.reload()

# Validate
if config.validate():
    print("Config OK!")

# Display
config.print_config()
config.print_config(section="aws")
```

---

## Configuration File (config.yaml)

```yaml
aws:
  default_profile: default
  default_region: us-west-2
  profiles:
    production:
      region: us-east-1
      instance_type: t3.large

ssh:
  default_user: ec2-user
  default_port: 22
  connect_timeout: 10
  hosts:
    web-server:
      hostname: 10.0.1.100
      user: ubuntu
      port: 2222

docker:
  daemon_url: unix:///var/run/docker.sock
  timeout: 60
  tls_verify: false

logging:
  level: INFO
  output_dir: ~/.opszen/logs

application:
  config_dir: ~/.opszen
  verbose: false
  color_output: true
```

---

## Environment Variables (.env)

```bash
# AWS
AWS_PROFILE=production
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=AKIAXXXXXXXXXXXXXXXX
AWS_SECRET_ACCESS_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# SSH
OPSZEN_SSH_USER=ubuntu
OPSZEN_SSH_KEY=~/.ssh/prod_key.pem

# Docker
DOCKER_HOST=tcp://192.168.1.100:2375
DOCKER_TLS_VERIFY=0

# Logging
OPSZEN_LOG_LEVEL=DEBUG
OPSZEN_VERBOSE=1
```

---

## Configuration Hierarchy

```
Priority (High → Low):
1. CLI Arguments        --region us-east-1
2. Environment Vars     AWS_REGION=us-east-1
3. config.yaml          aws.default_region: us-east-1
4. Built-in Defaults    us-west-2
```

---

## Common Tasks

### Multiple AWS Profiles

```python
# Switch between environments
dev = config.get_aws_profile("development")
prod = config.get_aws_profile("production")
```

### SSH Host Configuration

```python
# Get host-specific config
web = config.get_ssh_config("production-web")
db = config.get_ssh_config("production-db")
```

### Remote Docker Daemon

```python
# Via config.yaml
docker:
  daemon_url: tcp://192.168.1.100:2375

# Via environment variable
export DOCKER_HOST=tcp://192.168.1.100:2375
```

### Custom Config Location

```python
# Environment variable
export OPSZEN_CONFIG=~/.opszen/custom.yaml

# Or in code
config = ConfigManager(config_file="~/.opszen/custom.yaml")
```

---

## Environment Variables Reference

| Variable | Purpose | Example |
|----------|---------|---------|
| `AWS_PROFILE` | AWS profile name | `production` |
| `AWS_REGION` | AWS region | `us-east-1` |
| `AWS_ACCESS_KEY_ID` | AWS access key | `AKIAXXXXXXXX` |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | `xxxxxxxx` |
| `OPSZEN_SSH_USER` | Default SSH user | `ubuntu` |
| `OPSZEN_SSH_KEY` | SSH key path | `~/.ssh/key.pem` |
| `DOCKER_HOST` | Docker daemon URL | `tcp://host:2375` |
| `DOCKER_TLS_VERIFY` | Enable TLS | `1` |
| `OPSZEN_CONFIG` | Custom config path | `~/my-config.yaml` |
| `OPSZEN_LOG_LEVEL` | Log level | `DEBUG` |
| `OPSZEN_VERBOSE` | Verbose mode | `1` |

---

## Validation & Debugging

```python
# Validate configuration
valid = config.validate()

# Print entire config
config.print_config()

# Print specific section
config.print_config(section="aws")

# Check what's loaded
print(config.get("aws.default_region"))
print(config.get_section("ssh"))
```

---

## Common Patterns

### Environment-based Config

```python
import os

# Load different env files
env = os.getenv("ENV", "development")
load_dotenv(f".env.{env}")

config = ConfigManager(load_env=True)
```

### Per-Module Config

```python
class MyModule:
    def __init__(self, config=None):
        self.config = config or ConfigManager()
        self.setting = self.config.get("my_module.setting")
```

### Configuration as Dependency

```python
# Initialize once
global_config = ConfigManager()

# Pass to modules
provisioner = InfrastructureProvisioner(config=global_config)
ssh_manager = SSHManager(config=global_config)
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Config not loading | Check `~/.opszen/config.yaml` exists |
| Env vars not working | Verify `.env` in project root |
| Invalid config | Run `config.validate()` |
| Paths not expanding | Use `~` for home directory |
| Profile not found | Check `config.list_aws_profiles()` |

---

## Security Best Practices

✅ **DO:**
- Use `.env` files for secrets (add to `.gitignore`)
- Use AWS IAM roles when possible
- Use SSH keys instead of passwords
- Keep config files at `chmod 600`

❌ **DON'T:**
- Commit `.env` files
- Store passwords in `config.yaml`
- Share credentials in plain text
- Use world-readable permissions

---

## File Locations

```
~/.opszen/
├── config.yaml          # Main configuration
├── .env                 # Environment variables (optional)
├── profiles.yaml        # Connection profiles
├── logs/                # Log files
├── data/                # Data storage
└── cache/               # Temporary cache
```

---

## Next Steps

📖 Full documentation: [docs/CONFIGURATION.md](./CONFIGURATION.md)  
📋 Example config: [config.yaml.example](../config.yaml.example)  
📋 Example env: [env.example](../env.example)

---

**Last Updated:** 2024  
**Quick Reference Version:** 1.0
