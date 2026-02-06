# GitHub Actions CI/CD

This directory contains the GitHub Actions workflows for the OpsZen project.

## 📋 Workflows

### 🧪 `tests.yml` - Main Test Workflow
**Triggers:** Push to main/develop, Pull Requests

Comprehensive testing across multiple platforms and Python versions.

**Matrix:**
- **Ubuntu:** Python 3.8, 3.9, 3.10, 3.11, 3.12 (full coverage)
- **macOS:** Python 3.11, 3.12 (reduced matrix)
- **Windows:** Python 3.11, 3.12 (reduced matrix)

**Jobs:**
- `test` - Unit and integration tests
- `lint` - Code quality with ruff
- `security` - Security scanning (bandit, safety)
- `quick-check` - Fast validation with `make quick`
- `test-summary` - Results aggregation

**Coverage:** Uploaded to Codecov (Ubuntu + Python 3.11 only)

---

### ⚡ `pr-check.yml` - PR Quick Check
**Triggers:** Pull Requests only

Fast feedback workflow for pull request authors (~2-5 minutes).

**Jobs:**
- `quick-check` - Run `make quick` (format + unit tests)
- `lint-check` - Validate code quality

**Purpose:** Provide rapid feedback before full test suite runs.

---

### 🔄 `ci.yml` - Full CI Pipeline
**Triggers:** Push, Pull Requests, Manual (workflow_dispatch)

Complete CI pipeline using `make ci`.

**Features:**
- Full test suite with coverage
- Optional security checks
- Optional coverage report generation
- Manual workflow dispatch with configuration options

**Manual Inputs:**
- `run_security`: Enable/disable security checks
- `run_coverage`: Enable/disable coverage reports

---

### 🌙 `nightly.yml` - Nightly Tests
**Triggers:** Daily at 2 AM UTC, Manual (workflow_dispatch)

Comprehensive testing and security audits.

**Jobs:**
- `nightly-full-test` - All platforms × all Python versions
- `nightly-security` - Security audits (bandit, safety, pip-audit)
- `nightly-summary` - Results and notifications

**Purpose:** Catch issues early with comprehensive daily testing.

---

## 🚀 Quick Start

### For Developers

**Before committing:**
```bash
make quick              # Fast check (~30s)
```

**Before pushing:**
```bash
make ci                 # Full CI pipeline (~2-3 min)
```

### For Maintainers

**Enable workflows:**
1. Settings → Actions → Enable workflows
2. Settings → Branches → Configure branch protection
3. Add required status checks:
   - `test (ubuntu-latest, 3.11)`
   - `lint`
   - `quick-check`

**Add status badges to README:**
```markdown
[![Tests](https://github.com/TianaNanta/OpsZen/workflows/Tests/badge.svg)](https://github.com/TianaNanta/OpsZen/actions/workflows/tests.yml)
[![CI Pipeline](https://github.com/TianaNanta/OpsZen/workflows/CI%20Pipeline/badge.svg)](https://github.com/TianaNanta/OpsZen/actions/workflows/ci.yml)
```

---

## 🔧 Tools & Technology

- **uv** - Fast Python package installer (10-100x faster than pip)
- **ruff** - Fast linter/formatter (replaces black, flake8, isort, pylint)
- **pytest** - Test framework with coverage, xdist, timeout plugins
- **make** - Consistent commands across local and CI environments

---

## 📚 Documentation

- [**CI/CD Documentation**](../docs/CI_CD.md) - Comprehensive guide (533 lines)
- [**Quick Reference**](../docs/CI_QUICK_REF.md) - One-page cheat sheet
- [**Update Summary**](../GITHUB_ACTIONS_UPDATE.md) - What changed and why
- [**Deployment Checklist**](./DEPLOYMENT_CHECKLIST.md) - Step-by-step guide
- [**Delivery Summary**](../DELIVERY_GITHUB_ACTIONS.md) - Complete deliverables

---

## 🎯 Key Features

✅ **Fast** - 20-40% faster CI runs with uv and ruff  
✅ **Consistent** - Same commands locally and in CI  
✅ **Modern** - Latest tooling and best practices  
✅ **Cross-platform** - Ubuntu, macOS, Windows support  
✅ **Secure** - Automated security scanning  
✅ **Reliable** - Caching and parallel execution  

---

## 📊 Workflow Matrix

| Workflow | Trigger | Duration | Coverage |
|----------|---------|----------|----------|
| tests.yml | Push/PR | ~10-15 min | Full matrix |
| pr-check.yml | PR only | ~2-5 min | Ubuntu only |
| ci.yml | Manual | ~5-10 min | Ubuntu only |
| nightly.yml | Daily 2 AM UTC | ~30-45 min | Full matrix |

---

## 🛠️ Common Tasks

### Run CI Locally
```bash
make ci                 # Full CI pipeline
```

### Test Specific Components
```bash
make test-unit          # Unit tests only
make test-integration   # Integration tests only
make test-coverage      # With coverage report
```

### Code Quality
```bash
make format             # Format code
make lint               # Lint with auto-fix
make format-check       # Check formatting
make lint-check         # Check linting
```

### Security
```bash
make security           # Run security checks
```

---

## 🔍 Troubleshooting

### Tests Fail in CI but Pass Locally

**Solution:**
```bash
# Clean environment and retry
rm -rf .venv
uv venv .venv
source .venv/bin/activate
uv pip install -e ".[dev]"
make test
```

### Workflow Doesn't Start

**Check:**
1. Workflow trigger conditions match (branch name, etc.)
2. Repository settings (Actions enabled)
3. Workflow file syntax (YAML validation)

### Slow Workflows

**Optimize:**
1. Check cache hit rates
2. Review parallel job configuration
3. Consider splitting large test suites
4. Use `make quick` for rapid feedback

---

## 📈 Performance Metrics

Expected improvements over previous setup:

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Dependency install | 2-3 min | 15-30s | 4-6x faster |
| Linting | 1-2 min | 5-10s | 10-20x faster |
| Overall CI time | 15-20 min | 10-15 min | 25-33% faster |
| Cache hit rate | ~50% | ~80% | 60% increase |

---

## 🎓 Learning Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [uv Documentation](https://github.com/astral-sh/uv)
- [ruff Documentation](https://docs.astral.sh/ruff/)
- [pytest Documentation](https://docs.pytest.org/)

---

## 📞 Support

**Questions or Issues?**
- Check [CI/CD Documentation](../docs/CI_CD.md)
- Review [GitHub Actions logs](https://github.com/TianaNanta/OpsZen/actions)
- Open an [issue](https://github.com/TianaNanta/OpsZen/issues)

---

## ✅ Validation

Verify the setup:
```bash
# Validate workflows and setup
./.github/validate.sh

# Test locally
make quick              # Quick check
make ci                 # Full CI pipeline
```

---

**Last Updated:** 2024  
**Version:** 1.0  
**Status:** Production Ready
