# CI/CD Documentation

## Overview

OpsZen uses GitHub Actions for continuous integration and deployment. The CI/CD pipeline ensures code quality, runs tests across multiple platforms, and maintains security standards.

## Table of Contents

- [Workflows](#workflows)
- [Local Development](#local-development)
- [Workflow Details](#workflow-details)
- [Configuration](#configuration)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## Workflows

### 1. Tests Workflow (`tests.yml`)

**Trigger:** Push to `main`/`develop`, Pull Requests

**Purpose:** Comprehensive testing across multiple platforms and Python versions

**Jobs:**
- **test**: Matrix testing (Ubuntu/macOS/Windows × Python 3.8-3.12)
- **lint**: Code quality checks with ruff
- **security**: Security scanning with bandit and safety
- **quick-check**: Fast feedback with `make quick`
- **test-summary**: Aggregate results

**Key Features:**
- Reduced matrix on macOS/Windows (only latest Python versions)
- Full matrix on Ubuntu
- Coverage reporting to Codecov (Ubuntu + Python 3.11)
- Parallel job execution
- Artifact uploads for test results

**Example:**
```yaml
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]
```

---

### 2. PR Quick Check Workflow (`pr-check.yml`)

**Trigger:** Pull Requests only

**Purpose:** Fast feedback for pull request authors

**Jobs:**
- **quick-check**: Run `make quick` (format + unit tests)
- **lint-check**: Validate formatting and linting

**Why Use This:**
- Faster than full test suite
- Catches common issues early
- Uses same tools as local development

**Local Equivalent:**
```bash
make quick
```

---

### 3. CI Pipeline Workflow (`ci.yml`)

**Trigger:** Push, Pull Requests, Manual

**Purpose:** Full CI pipeline matching local `make ci` command

**Jobs:**
- **ci**: Run complete CI pipeline
  - Format checking
  - Lint checking
  - Full test suite with coverage
  - Security checks (optional)

**Manual Trigger Options:**
- `run_security`: Enable/disable security checks
- `run_coverage`: Enable/disable coverage report generation

**Workflow Dispatch:**
```bash
# Trigger manually via GitHub UI
# Actions → CI Pipeline → Run workflow
```

---

### 4. Nightly Tests Workflow (`nightly.yml`)

**Trigger:** Schedule (2 AM UTC daily), Manual

**Purpose:** Comprehensive testing and security audits

**Jobs:**
- **nightly-full-test**: All platforms × all Python versions
- **nightly-security**: Security scanning
  - bandit (code security)
  - safety (dependency vulnerabilities)
  - pip-audit (package auditing)
- **nightly-summary**: Results aggregation and notification

**Schedule:**
```yaml
schedule:
  - cron: '0 2 * * *'  # Daily at 2 AM UTC
```

---

## Local Development

### Replicating CI Locally

Run the same commands that CI uses:

```bash
# Quick check (PR workflow)
make quick

# Full CI pipeline
make ci

# Individual checks
make format-check        # Check formatting
make lint-check          # Check linting
make test                # Run all tests
make test-coverage       # Generate coverage
make security            # Security checks
```

### Development Workflow

1. **Before committing:**
   ```bash
   make quick              # Format + unit tests
   ```

2. **Before pushing:**
   ```bash
   make ci                 # Full CI locally
   ```

3. **Check pre-commit hooks:**
   ```bash
   make precommit-all      # Run on all files
   ```

---

## Workflow Details

### Dependency Management

All workflows use `uv` for fast, reliable dependency management:

```yaml
- name: Install uv
  uses: astral-sh/setup-uv@v4
  with:
    enable-cache: true

- name: Create virtual environment
  run: uv venv .venv

- name: Install dependencies
  run: |
    source .venv/bin/activate
    uv pip install -e ".[dev]"
```

### Cross-Platform Support

**Unix (Ubuntu/macOS):**
```bash
source .venv/bin/activate
make test-unit
```

**Windows:**
```bash
source .venv/Scripts/activate
./run_tests.sh unit
```

### Caching Strategy

- **uv cache**: Enabled via `astral-sh/setup-uv@v4`
- **Python setup**: Uses `actions/setup-python@v5`
- **Dependency caching**: Automatic with uv

### Test Matrix

#### Full Matrix (Ubuntu)
```yaml
os: ubuntu-latest
python-version: ["3.8", "3.9", "3.10", "3.11", "3.12"]
```

#### Reduced Matrix (macOS/Windows)
```yaml
os: macos-latest / windows-latest
python-version: ["3.11", "3.12"]
```

**Rationale:** Balance between coverage and CI time/cost

---

## Configuration

### Environment Variables

Set in GitHub repository settings (Settings → Secrets and variables → Actions):

```yaml
# Optional: Codecov integration
CODECOV_TOKEN: ${{ secrets.CODECOV_TOKEN }}

# Optional: Custom configurations
OPSZEN_ENV: ci
OPSZEN_LOG_LEVEL: WARNING
```

### Workflow Badges

Add to README.md:

```markdown
[![Tests](https://github.com/TianaNanta/OpsZen/workflows/Tests/badge.svg)](https://github.com/TianaNanta/OpsZen/actions/workflows/tests.yml)
[![CI Pipeline](https://github.com/TianaNanta/OpsZen/workflows/CI%20Pipeline/badge.svg)](https://github.com/TianaNanta/OpsZen/actions/workflows/ci.yml)
[![Nightly Tests](https://github.com/TianaNanta/OpsZen/workflows/Nightly%20Tests/badge.svg)](https://github.com/TianaNanta/OpsZen/actions/workflows/nightly.yml)
```

### Status Checks

Enable required status checks in branch protection:

1. Go to: Settings → Branches → Branch protection rules
2. Select `main` or `develop`
3. Enable: "Require status checks to pass before merging"
4. Select required checks:
   - `test (ubuntu-latest, 3.11)`
   - `lint`
   - `quick-check`

---

## Best Practices

### 1. **Run CI Locally First**

```bash
# Before pushing
make ci
```

**Benefits:**
- Catch issues early
- Faster feedback loop
- Save CI minutes

### 2. **Use Quick Check for Rapid Iteration**

```bash
# During development
make quick
```

### 3. **Keep Tests Fast**

- Unit tests should run in seconds
- Integration tests in minutes
- Use `pytest-xdist` for parallelization

### 4. **Monitor CI Performance**

```bash
# Check workflow run times
# GitHub UI → Actions → Workflow → Runtime
```

**Optimize if needed:**
- Increase parallelization
- Reduce test matrix
- Cache dependencies effectively

### 5. **Security First**

```bash
# Run security checks locally
make security
```

**Tools:**
- `bandit`: Static code analysis
- `safety`: Dependency vulnerability scanning
- `pip-audit`: Package auditing

### 6. **Coverage Tracking**

```bash
# Generate coverage report
make test-coverage

# View HTML report
open htmlcov/index.html
```

**Goals:**
- Overall coverage: >70%
- New code coverage: >80%
- Critical paths: 100%

---

## Troubleshooting

### Common Issues

#### 1. **Tests Pass Locally but Fail in CI**

**Possible causes:**
- Missing dependency in `pyproject.toml`
- Platform-specific behavior
- Timezone/locale differences
- File path issues (Windows vs Unix)

**Solutions:**
```bash
# Test with fresh virtualenv
rm -rf .venv
uv venv .venv
source .venv/bin/activate
uv pip install -e ".[dev]"
make test
```

#### 2. **Cache Issues**

**Clear GitHub Actions cache:**
1. Actions → Caches
2. Delete old caches

**Or disable caching temporarily:**
```yaml
- name: Install uv
  uses: astral-sh/setup-uv@v4
  with:
    enable-cache: false  # Disable for debugging
```

#### 3. **Windows-Specific Failures**

**Common issues:**
- Path separators (`/` vs `\`)
- Line endings (LF vs CRLF)
- Case-sensitive file names

**Solutions:**
```python
# Use pathlib for cross-platform paths
from pathlib import Path
path = Path("data") / "file.txt"

# Handle line endings
with open(file, "r", newline="") as f:
    content = f.read()
```

#### 4. **Timeout Issues**

**Increase timeout:**
```yaml
- name: Run tests
  run: make test
  timeout-minutes: 30  # Default is 360
```

**Or in pytest:**
```bash
pytest --timeout=300  # 5 minutes per test
```

#### 5. **Coverage Upload Failures**

**Check Codecov token:**
```yaml
- name: Upload coverage
  uses: codecov/codecov-action@v4
  with:
    token: ${{ secrets.CODECOV_TOKEN }}
    fail_ci_if_error: false  # Don't fail on upload issues
```

---

## Workflow Maintenance

### Updating Dependencies

**GitHub Actions versions:**
```yaml
# Keep these updated
uses: actions/checkout@v4        # Latest: v4
uses: actions/setup-python@v5    # Latest: v5
uses: astral-sh/setup-uv@v4      # Latest: v4
uses: codecov/codecov-action@v4  # Latest: v4
```

**Python versions:**
```yaml
# Add new Python versions
python-version: ["3.8", "3.9", "3.10", "3.11", "3.12", "3.13"]
```

### Monitoring Workflow Health

**Metrics to track:**
- Success rate (%)
- Average duration
- Failure patterns
- Resource usage

**GitHub provides:**
- Workflow insights
- Job summaries
- Artifact management

---

## Advanced Topics

### Custom Workflows

Create custom workflows for specific needs:

```yaml
# .github/workflows/custom.yml
name: Custom Workflow

on:
  workflow_dispatch:
    inputs:
      environment:
        description: 'Environment to deploy'
        required: true
        default: 'staging'
        type: choice
        options:
          - staging
          - production

jobs:
  custom-job:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      # Your custom steps here
```

### Deployment Workflows

**Example staging deployment:**
```yaml
name: Deploy to Staging

on:
  push:
    branches: [develop]

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - uses: actions/checkout@v4
      - name: Deploy
        run: |
          # Deployment commands
          make deploy-staging
```

### Integration with External Services

**Examples:**
- Slack notifications
- Jira updates
- AWS deployments
- Docker registry pushes

---

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [uv Documentation](https://github.com/astral-sh/uv)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [pytest Documentation](https://docs.pytest.org/)
- [Codecov Documentation](https://docs.codecov.io/)

---

## Summary

**Quick Commands:**
```bash
make quick       # Quick check
make ci          # Full CI pipeline
make test        # All tests
make security    # Security checks
```

**CI Workflows:**
- `tests.yml` - Comprehensive testing
- `pr-check.yml` - Fast PR feedback
- `ci.yml` - Full CI pipeline
- `nightly.yml` - Scheduled comprehensive checks

**Best Practice:**
Always run `make ci` locally before pushing to ensure CI will pass.

---

*Last updated: 2024*
*For issues or questions, please open a GitHub issue.*
