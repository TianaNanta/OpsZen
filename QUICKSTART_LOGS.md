# Log Analyzer Quick Start Guide

Get started with OpsZen's powerful log analysis capabilities in 5 minutes!

## 🚀 Quick Setup

```bash
# Navigate to OpsZen directory
cd OpsZen

# Activate virtual environment
source .venv/bin/activate

# Verify installation
python -m src.cli logs --help
```

---

## 📋 5-Minute Tutorial

### Step 1: Generate Sample Logs

```bash
# Generate test logs for practice
python -c "
from src.logs.sample_logs import SampleLogGenerator
gen = SampleLogGenerator('my_test_logs')
gen.generate_all_samples()
"
```

This creates 5 sample log files in `my_test_logs/` directory.

### Step 2: Analyze Logs

```bash
# Analyze a log file
python -m src.cli logs analyze my_test_logs/sample_python.log
```

**You'll see:**
- Total log entries
- Log level distribution (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Time range and duration
- Most common messages
- Hourly distribution
- Error analysis

### Step 3: Filter for Errors

```bash
# Find all ERROR level entries
python -m src.cli logs filter my_test_logs/sample_python.log --level ERROR
```

**You'll see:**
- All error messages with timestamps
- Color-coded output (errors in red)
- Total count of filtered entries

### Step 4: Export Results

```bash
# Export errors to JSON for further analysis
python -m src.cli logs filter my_test_logs/sample_python.log \
    --level ERROR \
    --output errors.json
```

**Result:**
- `errors.json` file created with all error entries
- Can also export to CSV (`--output errors.csv`) or text format

### Step 5: Real-Time Monitoring

```bash
# Watch logs in real-time (like tail -f)
python -m src.cli logs tail my_test_logs/sample_python.log --follow

# Press Ctrl+C to stop
```

---

## 🎯 Common Use Cases

### Find Database Errors

```bash
python -m src.cli logs filter app.log --level ERROR --pattern "database|sql|connection"
```

### Security Audit

```bash
# Failed login attempts
python -m src.cli logs filter /var/log/auth.log --pattern "Failed password"

# Successful SSH logins
python -m src.cli logs filter /var/log/auth.log --pattern "Accepted publickey"
```

### Time-Based Analysis

```bash
# Errors in the last hour
python -m src.cli logs filter app.log \
    --level ERROR \
    --start "$(date -d '1 hour ago' '+%Y-%m-%d %H:%M:%S')"
```

### Web Server Analysis

```bash
# Find all 404 errors
python -m src.cli logs filter /var/log/nginx/access.log --pattern "\" 404 "

# Find all 5xx server errors
python -m src.cli logs filter /var/log/nginx/access.log --pattern "\" 5[0-9]{2} "
```

---

## 🔍 Supported Log Formats

OpsZen automatically detects these formats:

| Format | Example |
|--------|---------|
| **Syslog** | `Jan 15 10:30:45 server nginx[1234]: Connection established` |
| **Apache/Nginx** | `192.168.1.1 - - [15/Jan/2024:10:30:45 +0000] "GET /api HTTP/1.1" 200 1234` |
| **JSON** | `{"timestamp": "2024-01-15T10:30:45", "level": "ERROR", "message": "Failed"}` |
| **Python** | `2024-01-15 10:30:45 ERROR app.main: Connection failed` |

Don't know your format? No problem - the analyzer will auto-detect it!

---

## 💡 Pro Tips

### 1. Use Aliases

Add to your `.bashrc` or `.zshrc`:

```bash
alias ozlogs='python -m src.cli logs'
alias ozanalyze='ozlogs analyze'
alias ozfilter='ozlogs filter'
alias oztail='ozlogs tail'
```

Then use:

```bash
ozanalyze app.log
ozfilter app.log --level ERROR
oztail app.log -f
```

### 2. Combine Filters

```bash
# Multiple criteria at once
ozfilter app.log \
    --level WARNING \
    --pattern "timeout|slow" \
    --start "2024-01-15 00:00:00" \
    --output warnings.json
```

### 3. Pipe to Other Tools

```bash
# Combine with jq for JSON processing
ozfilter app.log --level ERROR | jq '.message'

# Combine with grep
oztail app.log -f | grep -i "database"

# Count occurrences
ozfilter app.log --pattern "error" | wc -l
```

### 4. Limit Large Files

```bash
# Analyze only last 10,000 lines
ozanalyze huge.log --max-lines 10000
```

### 5. Exclude Noise

```bash
# Exclude debug and info messages
ozfilter app.log --exclude "DEBUG|INFO"

# Exclude health checks from web logs
ozfilter access.log --exclude "/health|/metrics"
```

---

## 📊 Understanding Output

### Log Level Hierarchy

When you filter by level, you get that level and **higher**:

```
--level ERROR    → Shows: ERROR, CRITICAL
--level WARNING  → Shows: WARNING, ERROR, CRITICAL
--level INFO     → Shows: INFO, WARNING, ERROR, CRITICAL
--level DEBUG    → Shows: Everything
```

### Export Formats

| Format | Use Case | File Extension |
|--------|----------|----------------|
| **JSON** | API integration, further processing | `.json` |
| **CSV** | Excel, spreadsheet analysis | `.csv` |
| **Text** | Human reading, grep/awk processing | `.txt` |

---

## 🛠️ Troubleshooting

### "No matches found"

- Check your regex pattern is valid
- Try a simpler pattern first
- Use `.*` to see all entries

### "File not found"

- Check the file path is correct
- Use absolute paths: `/var/log/app.log`
- Check file permissions

### Slow on large files

- Use `--max-lines` to limit parsing
- Filter early to reduce data
- Consider splitting large files

---

## 📚 Next Steps

### Learn More

- **Full Documentation**: See `src/logs/README.md`
- **Examples**: See `EXAMPLES.md`
- **API Usage**: See Python examples in documentation

### Try These Commands

```bash
# Generate your own test logs
python -c "
from src.logs.sample_logs import SampleLogGenerator
gen = SampleLogGenerator('.')
gen.generate_error_burst('test_errors.log', lines=1000)
"

# Analyze them
ozanalyze test_errors.log

# Find error patterns
ozfilter test_errors.log --level ERROR
```

### Automate with Scripts

Create `monitor_errors.sh`:

```bash
#!/bin/bash
# Check for new errors every 5 minutes

LOGFILE="/var/log/app.log"
SINCE="$(date -d '5 minutes ago' '+%Y-%m-%d %H:%M:%S')"

errors=$(python -m src.cli logs filter $LOGFILE \
    --level ERROR \
    --start "$SINCE" | wc -l)

if [ $errors -gt 0 ]; then
    echo "⚠️  Found $errors new errors!"
    python -m src.cli logs filter $LOGFILE \
        --level ERROR \
        --start "$SINCE" \
        --output recent_errors.json
fi
```

---

## 🎓 Interactive Tutorial

Want hands-on practice? Run the test suite:

```bash
python test_logs.py
```

This will:
1. Generate sample logs in multiple formats
2. Test analysis features
3. Test filtering capabilities
4. Test export functionality
5. Show you real examples of output

---

## 🆘 Getting Help

```bash
# General help
python -m src.cli logs --help

# Command-specific help
python -m src.cli logs analyze --help
python -m src.cli logs filter --help
python -m src.cli logs tail --help
python -m src.cli logs export --help
```

---

## ✨ You're Ready!

Start analyzing your logs:

```bash
# Replace with your actual log file
python -m src.cli logs analyze /var/log/syslog
```

Happy log hunting! 🔍