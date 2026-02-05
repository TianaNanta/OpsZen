# OpsZen Usage Examples

A collection of real-world examples and use cases for OpsZen DevOps toolkit.

---

## Table of Contents

- [System Monitoring](#system-monitoring)
- [Docker Management](#docker-management)
- [Log Analysis](#log-analysis)
- [Infrastructure Management](#infrastructure-management)
- [SSH Remote Management](#ssh-remote-management)
- [Combined Workflows](#combined-workflows)

---

## System Monitoring

### Basic System Health Check

```bash
# Take a quick snapshot of system metrics
opszen monitor snapshot
```

### Continuous Monitoring

```bash
# Monitor system every 5 seconds (default)
opszen monitor start

# Custom monitoring interval (every 10 seconds)
opszen monitor start --interval 10

# Monitor and log to file
opszen monitor start --interval 5 | tee system_metrics.log
```

### Scheduled Monitoring with Cron

```bash
# Add to crontab for hourly snapshots
0 * * * * /path/to/opszen monitor snapshot >> /var/log/opszen/hourly_metrics.log 2>&1
```

---

## Docker Management

### Container Lifecycle Management

```bash
# List all running containers
opszen docker list

# List all containers (including stopped)
opszen docker list --all

# Create and start a web server
opszen docker create nginx --name web-server --port 8080:80

# Create database container
opszen docker create postgres:13 --name db --port 5432:5432

# Stop a container
opszen docker stop web-server

# Remove a container
opszen docker remove web-server

# Force remove a running container
opszen docker remove web-server --force
```

### Multi-Container Setup

```bash
# Setup web application stack
opszen docker create nginx --name frontend --port 80:80
opszen docker create redis --name cache --port 6379:6379
opszen docker create postgres:13 --name database --port 5432:5432

# List all to verify
opszen docker list --all
```

### Cleanup Operations

```bash
# Stop all containers
for container in $(docker ps -q); do
    opszen docker stop $container
done

# Remove all stopped containers
opszen docker list --all | grep Exited | awk '{print $1}' | xargs -I {} opszen docker remove {}
```

---

## Log Analysis

### Quick Analysis

```bash
# Analyze system logs
opszen logs analyze /var/log/syslog

# Analyze web server logs
opszen logs analyze /var/log/nginx/access.log

# Analyze application logs
opszen logs analyze /var/log/app/production.log

# Limit analysis to last 5000 lines
opszen logs analyze /var/log/huge.log --max-lines 5000
```

### Error Investigation

```bash
# Find all errors
opszen logs filter /var/log/app.log --level ERROR

# Find critical errors in the last hour
opszen logs filter /var/log/app.log \
    --level CRITICAL \
    --start "$(date -d '1 hour ago' '+%Y-%m-%d %H:%M:%S')"

# Export errors for team review
opszen logs filter /var/log/app.log --level ERROR --output errors.json

# Find database-related errors
opszen logs filter /var/log/app.log --level ERROR --pattern "database|sql|connection"
```

### Security Auditing

```bash
# Find failed login attempts
opszen logs filter /var/log/auth.log --pattern "Failed password"

# Find successful SSH logins
opszen logs filter /var/log/auth.log --pattern "Accepted publickey"

# Find sudo usage
opszen logs filter /var/log/auth.log --pattern "sudo.*COMMAND"

# Export security events
opszen logs filter /var/log/auth.log \
    --pattern "Failed|Accepted|sudo" \
    --output security_audit.csv
```

### Web Traffic Analysis

```bash
# Analyze nginx access logs
opszen logs analyze /var/log/nginx/access.log

# Find all 404 errors
opszen logs filter /var/log/nginx/access.log --pattern "\" 404 "

# Find all 5xx server errors
opszen logs filter /var/log/nginx/access.log --pattern "\" 5[0-9]{2} "

# Find requests from specific IP
opszen logs filter /var/log/nginx/access.log --pattern "^192\.168\.1\.100"

# Export all POST requests
opszen logs filter /var/log/nginx/access.log \
    --pattern "\"POST " \
    --output post_requests.json
```

### Application Debugging

```bash
# Find stack traces
opszen logs filter /var/log/app.log --pattern "Traceback|Exception"

# Find slow queries
opszen logs filter /var/log/app.log --pattern "slow query|timeout|took [0-9]+ seconds"

# Find memory warnings
opszen logs filter /var/log/app.log --pattern "memory|OutOfMemory|heap"

# Time-based debugging (specific incident)
opszen logs filter /var/log/app.log \
    --start "2024-01-15 14:30:00" \
    --end "2024-01-15 14:45:00" \
    --output incident_20240115.json
```

### Real-Time Monitoring

```bash
# Tail application logs
opszen logs tail /var/log/app.log --follow

# Show last 50 lines
opszen logs tail /var/log/app.log --lines 50

# Tail and filter for errors
opszen logs tail /var/log/app.log --follow | grep ERROR

# Monitor multiple logs simultaneously
tail -f /var/log/app.log | opszen logs analyze -
```

### Pattern Exclusion

```bash
# Exclude debug messages
opszen logs filter /var/log/app.log --exclude "DEBUG"

# Exclude health checks
opszen logs filter /var/log/nginx/access.log --exclude "/health|/metrics"

# Show only errors, excluding specific ones
opszen logs filter /var/log/app.log \
    --level ERROR \
    --exclude "ECONNRESET|ENOTFOUND"
```

### Log Format Conversion

```bash
# Convert text logs to JSON
opszen logs export /var/log/app.log app_logs.json --format json

# Convert to CSV for Excel
opszen logs export /var/log/app.log app_logs.csv --format csv

# Extract and clean logs
opszen logs filter /var/log/app.log \
    --level INFO \
    --exclude "DEBUG|TRACE" \
    --output clean_logs.txt
```

### Generate Test Logs

```python
# Generate sample logs for testing
from src.logs.sample_logs import SampleLogGenerator

generator = SampleLogGenerator("test_logs")

# Generate all formats
generator.generate_all_samples()

# Or generate specific formats
generator.generate_syslog("custom_syslog.log", lines=5000)
generator.generate_json_log("app.json.log", lines=2000)
generator.generate_error_burst("errors.log", lines=1000)
```

---

## Infrastructure Management

### AWS EC2 Operations

```bash
# List all EC2 instances
opszen infra list-ec2

# Create a web server instance
opszen infra create-ec2 \
    --name web-server-01 \
    --image-id ami-0c55b159cbfafe1f0 \
    --instance-type t2.micro \
    --key-name my-keypair

# Create a larger instance
opszen infra create-ec2 \
    --name app-server-01 \
    --image-id ami-0c55b159cbfafe1f0 \
    --instance-type t2.medium \
    --key-name production-key
```

### AWS S3 Operations

```bash
# List all S3 buckets
opszen infra list-s3

# Create a new bucket
opszen infra create-s3 my-app-backup --region us-east-1

# Create bucket in different region
opszen infra create-s3 eu-data-bucket --region eu-west-1
```

### Infrastructure as Code

Create a YAML configuration file (`infrastructure.yaml`):

```yaml
ec2_instances:
  - name: web-server-01
    image_id: ami-0c55b159cbfafe1f0
    instance_type: t2.micro
    key_name: production-key
    security_group_ids:
      - sg-0123456789abcdef0
    subnet_id: subnet-0123456789abcdef0

  - name: app-server-01
    image_id: ami-0c55b159cbfafe1f0
    instance_type: t2.medium
    key_name: production-key
    security_group_ids:
      - sg-0123456789abcdef0

s3_buckets:
  - name: my-app-backups
    region: us-east-1
  
  - name: my-app-logs
    region: us-west-2
```

Provision the infrastructure:

```bash
opszen infra provision infrastructure.yaml
```

---

## SSH Remote Management

### Basic Remote Commands

```bash
# Execute command with SSH key
opszen ssh execute server.example.com user "ls -la /var/www" --key ~/.ssh/id_rsa

# Execute with password
opszen ssh execute server.example.com user "df -h" --password mypassword

# Execute with sudo
opszen ssh execute server.example.com user "systemctl restart nginx" --sudo --key ~/.ssh/id_rsa
```

### File Transfer

```bash
# Upload file to remote server
opszen ssh upload server.example.com user ./local/file.txt /remote/path/ --key ~/.ssh/id_rsa

# Upload directory
opszen ssh upload server.example.com user ./local/dir /remote/path/ --key ~/.ssh/id_rsa

# Download file from remote server
opszen ssh download server.example.com user /remote/file.txt ./local/path/ --key ~/.ssh/id_rsa

# Download directory
opszen ssh download server.example.com user /remote/dir ./local/path/ --key ~/.ssh/id_rsa
```

### Remote Directory Operations

```bash
# List remote directory
opszen ssh ls server.example.com user /var/www --key ~/.ssh/id_rsa

# List with password auth
opszen ssh ls server.example.com user /home/user/logs --password mypassword
```

### Deployment Operations

```bash
# Deploy application
opszen ssh upload server.example.com deploy ./dist /var/www/app --key ~/.ssh/deploy_key
opszen ssh execute server.example.com deploy "cd /var/www/app && npm install" --key ~/.ssh/deploy_key
opszen ssh execute server.example.com deploy "systemctl restart app" --sudo --key ~/.ssh/deploy_key

# Backup before deployment
opszen ssh execute server.example.com deploy "tar -czf /backups/app-$(date +%Y%m%d).tar.gz /var/www/app" --sudo --key ~/.ssh/deploy_key
```

### System Administration

```bash
# Check disk space
opszen ssh execute server.example.com admin "df -h" --key ~/.ssh/id_rsa

# Check memory usage
opszen ssh execute server.example.com admin "free -h" --key ~/.ssh/id_rsa

# View running processes
opszen ssh execute server.example.com admin "ps aux | head -20" --key ~/.ssh/id_rsa

# Check service status
opszen ssh execute server.example.com admin "systemctl status nginx" --sudo --key ~/.ssh/id_rsa

# View logs
opszen ssh execute server.example.com admin "tail -100 /var/log/nginx/error.log" --sudo --key ~/.ssh/id_rsa
```

### Multi-Server Operations

```bash
# Deploy to multiple servers
for server in web1.example.com web2.example.com web3.example.com; do
    echo "Deploying to $server..."
    opszen ssh upload $server deploy ./dist /var/www/app --key ~/.ssh/deploy_key
    opszen ssh execute $server deploy "systemctl restart app" --sudo --key ~/.ssh/deploy_key
done

# Health check across servers
for server in db1.example.com db2.example.com db3.example.com; do
    echo "Checking $server..."
    opszen ssh execute $server admin "systemctl status postgresql" --sudo --key ~/.ssh/id_rsa
done
```

---

## Combined Workflows

### Complete Application Deployment

```bash
#!/bin/bash
# deploy.sh - Complete deployment workflow

# 1. Build application locally
echo "Building application..."
npm run build

# 2. Backup current version on server
echo "Creating backup..."
opszen ssh execute server.example.com deploy \
    "tar -czf /backups/app-$(date +%Y%m%d-%H%M%S).tar.gz /var/www/app" \
    --sudo --key ~/.ssh/deploy_key

# 3. Upload new version
echo "Uploading new version..."
opszen ssh upload server.example.com deploy ./dist /var/www/app --key ~/.ssh/deploy_key

# 4. Restart services
echo "Restarting services..."
opszen ssh execute server.example.com deploy "systemctl restart app" --sudo --key ~/.ssh/deploy_key
opszen ssh execute server.example.com deploy "systemctl restart nginx" --sudo --key ~/.ssh/deploy_key

# 5. Check logs for errors
echo "Checking logs..."
sleep 5
opszen ssh execute server.example.com deploy "journalctl -u app -n 50" --sudo --key ~/.ssh/deploy_key | \
    opszen logs filter - --level ERROR

echo "Deployment complete!"
```

### Log Analysis & Alerting

```bash
#!/bin/bash
# monitor_errors.sh - Monitor logs and send alerts

LOG_FILE="/var/log/app/production.log"
ERROR_THRESHOLD=10

# Analyze logs
errors=$(opszen logs filter $LOG_FILE --level ERROR --start "$(date -d '1 hour ago' '+%Y-%m-%d %H:%M:%S')" | wc -l)

if [ $errors -gt $ERROR_THRESHOLD ]; then
    echo "ALERT: $errors errors in the last hour!"
    
    # Export error details
    opszen logs filter $LOG_FILE \
        --level ERROR \
        --start "$(date -d '1 hour ago' '+%Y-%m-%d %H:%M:%S')" \
        --output /tmp/recent_errors.json
    
    # Send alert (use your preferred method)
    # mail -s "Error Alert" ops@example.com < /tmp/recent_errors.json
fi
```

### Infrastructure Monitoring Dashboard

```bash
#!/bin/bash
# dashboard.sh - Generate infrastructure status report

echo "=== Infrastructure Status Report ==="
echo "Generated: $(date)"
echo

echo "=== System Metrics ==="
opszen monitor snapshot

echo
echo "=== Docker Containers ==="
opszen docker list --all

echo
echo "=== EC2 Instances ==="
opszen infra list-ec2

echo
echo "=== S3 Buckets ==="
opszen infra list-s3

echo
echo "=== Recent Errors ==="
opszen logs filter /var/log/syslog \
    --level ERROR \
    --start "$(date -d '24 hours ago' '+%Y-%m-%d %H:%M:%S')"
```

### Automated Backup & Cleanup

```bash
#!/bin/bash
# backup_and_cleanup.sh - Automated backup and log cleanup

BACKUP_DIR="/backups/$(date +%Y%m%d)"
REMOTE_SERVER="backup.example.com"

# 1. Create local backup
echo "Creating backup..."
mkdir -p $BACKUP_DIR

# Backup logs
opszen logs export /var/log/app.log $BACKUP_DIR/app_logs.json --format json

# Backup Docker volumes
opszen docker list | grep -v CONTAINER | while read container; do
    docker export $container > $BACKUP_DIR/${container}.tar
done

# 2. Upload to remote server
echo "Uploading backup..."
opszen ssh upload $REMOTE_SERVER backup $BACKUP_DIR /backups/ --key ~/.ssh/backup_key

# 3. Cleanup old logs
echo "Cleaning up old logs..."
find /var/log/app -name "*.log" -mtime +30 -delete

# 4. Verify backup
opszen ssh ls $REMOTE_SERVER backup /backups/$(date +%Y%m%d) --key ~/.ssh/backup_key
```

### Security Audit Workflow

```bash
#!/bin/bash
# security_audit.sh - Weekly security audit

REPORT_DIR="/reports/security/$(date +%Y%m%d)"
mkdir -p $REPORT_DIR

echo "Running security audit..."

# 1. Check failed login attempts
opszen logs filter /var/log/auth.log \
    --pattern "Failed password" \
    --start "$(date -d '7 days ago' '+%Y-%m-%d %H:%M:%S')" \
    --output $REPORT_DIR/failed_logins.csv

# 2. Check sudo usage
opszen logs filter /var/log/auth.log \
    --pattern "sudo.*COMMAND" \
    --start "$(date -d '7 days ago' '+%Y-%m-%d %H:%M:%S')" \
    --output $REPORT_DIR/sudo_usage.csv

# 3. Check critical errors
opszen logs filter /var/log/syslog \
    --level CRITICAL \
    --start "$(date -d '7 days ago' '+%Y-%m-%d %H:%M:%S')" \
    --output $REPORT_DIR/critical_errors.json

# 4. System metrics
opszen monitor snapshot > $REPORT_DIR/system_metrics.txt

echo "Security audit complete. Reports saved to $REPORT_DIR"
```

### Performance Monitoring

```python
#!/usr/bin/env python3
# performance_monitor.py - Continuous performance monitoring

import time
from datetime import datetime
from src.monitoring.system_monitor import SystemMonitor
from src.logs.log_analyzer import LogAnalyzer

monitor = SystemMonitor()
analyzer = LogAnalyzer()

while True:
    # Get system metrics
    metrics = monitor.get_system_metrics()
    
    # Check CPU usage
    if metrics['cpu_percent'] > 80:
        print(f"ALERT: High CPU usage: {metrics['cpu_percent']}%")
        
        # Analyze logs for potential cause
        analyzer.filter_logs(
            "/var/log/syslog",
            level="WARNING",
            pattern="cpu|process"
        )
    
    # Check memory usage
    if metrics['memory']['percent'] > 85:
        print(f"ALERT: High memory usage: {metrics['memory']['percent']}%")
    
    time.sleep(60)  # Check every minute
```

---

## Tips & Best Practices

### 1. Use Aliases for Common Commands

Add to your `.bashrc` or `.zshrc`:

```bash
alias oz='opszen'
alias ozm='opszen monitor snapshot'
alias ozl='opszen logs'
alias ozd='opszen docker'
```

### 2. Create Reusable Scripts

Store common workflows in scripts and version control them:

```bash
# deploy.sh
# backup.sh
# monitor.sh
```

### 3. Schedule Regular Tasks with Cron

```bash
# Monitor every hour
0 * * * * /usr/local/bin/opszen monitor snapshot >> /var/log/opszen/metrics.log

# Daily security audit
0 0 * * * /path/to/security_audit.sh

# Weekly backups
0 2 * * 0 /path/to/backup_and_cleanup.sh
```

### 4. Combine with Other Tools

```bash
# Pipe to jq for JSON processing
opszen logs export app.log - --format json | jq '.[] | select(.level == "ERROR")'

# Combine with grep
opszen logs tail app.log -f | grep -i error

# Use with watch for live updates
watch -n 5 opszen monitor snapshot
```

### 5. Environment Variables for Configuration

```bash
export OPSZEN_LOG_LEVEL=INFO
export OPSZEN_AWS_REGION=us-west-2
export OPSZEN_SSH_KEY=~/.ssh/id_rsa
```

---

## More Examples

For detailed examples on specific modules, see:
- [Log Analysis Examples](src/logs/README.md)
- [Infrastructure Examples](src/infrastructure/README.md)
- [SSH Management Examples](src/remote/README.md)

---

## Contributing

Have a great use case or workflow? Please contribute by submitting a PR with your examples!