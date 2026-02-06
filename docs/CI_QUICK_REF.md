# CI/CD Quick Reference

## 🚀 Quick Commands

### Local Development
```bash
make quick               # Format + unit tests (fastest)
make ci                  # Full CI pipeline (recommended before push)
make test                # All tests
make test-unit           # Unit tests only
make test-integration    # Integration tests only
make test-coverage       # Tests with coverage report
```

### Code Quality
```bash
make format              # Format code with ruff
make lint                # Lint with auto-fix
make format-check        # Check formatting (no changes)
make lint-check          # Check linting (no changes)
make check               # Run all checks
make fix                 # Auto-fix all issues
```

### Pre-commit
```bash
make precommit           # Run on staged files
make precommit-all       # Run on all files
make precommit-install   # Install hooks
```

### Security & Diagnostics
```bash
make security            # Security checks (bandit, safety)
make diagnose            # Show environment info
make clean               # Clean artifacts
```

---

## 📋 GitHub Actions Workflows

### Tests Workflow (`tests.yml`)
- **Trigger:** Push to main/develop, PRs
- **Matrix:** Ubuntu/macOS/Windows × Python 3.8-3.12
- **Jobs:** test, lint, security, quick-check, test-summary
- **Coverage:** Uploaded to Codecov (Ubuntu + Python 3.11)

### PR Quick Check (`pr-check.yml`)
- **Trigger:** Pull requests only
- **Jobs:** quick-check, lint-check
- **Speed:** ~2-5 minutes
- **Purpose:** Fast feedback

### CI Pipeline (`ci.yml`)
- **Trigger:** Push, PRs, manual
- **Jobs:** Full CI with `make ci`
- **Options:** Security checks, coverage reports
- **Manual:** Workflow dispatch available

### Nightly Tests (`nightly.yml`)
- **Trigger:** Daily at 2 AM UTC, manual
- **Jobs:** Full matrix testing, security audits
- **Tools:** bandit, safety, pip-audit
- **Artifacts:** Test results, coverage reports

---

## 🔄 Development Workflow

### Before Committing
```bash
make quick
# Or manually:
make format
make test-unit
```

### Before Pushing
```bash
make ci
# Equivalent to:
make clean
make install-dev
make format-check
make lint-check
make test-coverage
```

### Quick Iteration
```bash
# Edit code...
make quick              # Fast check
# Edit code...
make quick              # Fast check
# Ready to commit
make ci                 # Full validation
git commit -m "..."
git push
```

---

## 🛠️ Troubleshooting

### Tests Fail in CI but Pass Locally
```bash
# Clean environment
rm -rf .venv
uv venv .venv
source .venv/bin/activate
uv pip install -e ".[dev]"
make test
```

### Linting Errors
```bash
make fix                # Auto-fix everything
make format             # Format code
make lint               # Lint with auto-fix
```

### Coverage Too Low
```bash
make test-coverage      # Generate report
open htmlcov/index.html # View in browser
# Add tests for uncovered code
```

### Security Issues
```bash
make security           # Run security checks
bandit -r src           # Code security
safety check            # Dependency vulnerabilities
```

---

## 📊 CI Status Checks

### Required Checks (Branch Protection)
- `test (ubuntu-latest, 3.11)` - Main test suite
- `lint` - Code quality
- `quick-check` - Fast validation

### Optional Checks
- `security` - Security scanning (continue-on-error)
- Coverage reports
- Nightly tests

---

## 🎯 Best Practices

### ✅ DO
- Run `make quick` frequently during development
- Run `make ci` before pushing
- Keep unit tests fast (<30s total)
- Write meaningful commit messages
- Update tests with code changes

### ❌ DON'T
- Push without running `make ci` locally
- Commit failing tests
- Skip pre-commit hooks
- Ignore linting errors
- Commit formatting issues

---

## 📦 Dependencies

### Tool Versions
- **Python:** 3.8+
- **uv:** Latest (auto-installed in CI)
- **ruff:** >=0.15.0
- **pytest:** >=8.3.5

### Update Dependencies
```bash
# Check for updates
uv pip list --outdated

# Update specific package
uv pip install --upgrade ruff

# Update all dev dependencies
uv pip install --upgrade -e ".[dev]"
```

---

## 🔍 Viewing Results

### Local
```bash
# Coverage report
make test-coverage
open htmlcov/index.html

# Test results
pytest --html=report.html
open report.html

# Linting stats
make stats
```

### GitHub Actions
- **Actions tab** → Select workflow → View logs
- **Pull Request** → Checks tab
- **Codecov** → Coverage dashboard

---

## ⚡ Performance Tips

### Speed Up Tests
```bash
# Parallel execution
make test-fast
# Or manually:
pytest -n auto          # Use all CPUs

# Specific module
make test-docker        # Only Docker tests

# Failed tests only
make test-failed        # Re-run failures
```

### Speed Up CI
- Use `make quick` in PR workflow (faster)
- Run full matrix only on main branch
- Cache dependencies (auto-enabled with uv)
- Run expensive tests in nightly workflow

---

## 🎨 Code Quality Standards

### Ruff Configuration
- **Line length:** 88 (Black compatible)
- **Target:** Python 3.8+
- **Rules:** E, F, I, N, UP, B, SIM, C4
- **Auto-fix:** Enabled

### Coverage Goals
- **Overall:** >70%
- **New code:** >80%
- **Critical paths:** 100%

### Test Organization
```
tests/
├── unit/           # Fast, isolated tests
│   ├── config/
│   ├── logging/
│   └── utils/
└── integration/    # Slower, end-to-end tests
    ├── docker/
    ├── ssh/
    └── aws/
```

---

## 📝 Useful Commands

### Git Workflow
```bash
# Create feature branch
git checkout -b feature/my-feature

# Make changes
make quick              # Validate

# Commit
git add .
git commit -m "feat: add new feature"

# Before push
make ci                 # Full validation

# Push
git push origin feature/my-feature
```

### Debug CI Failures
```bash
# View GitHub Actions logs
gh run view             # GitHub CLI

# Download artifacts
gh run download <run-id>

# Re-run failed jobs
gh run rerun <run-id> --failed
```

---

## 🔗 Quick Links

- [Full CI/CD Docs](./CI_CD.md)
- [GitHub Actions](https://github.com/TianaNanta/OpsZen/actions)
- [Codecov Dashboard](https://codecov.io/gh/TianaNanta/OpsZen)
- [Ruff Docs](https://docs.astral.sh/ruff/)

---

## 💡 Tips

1. **Use `make quick` frequently** - Fast feedback loop
2. **Run `make ci` before pushing** - Catch issues early
3. **Check CI status before merging** - All checks must pass
4. **Monitor coverage trends** - Don't let coverage decrease
5. **Keep tests isolated** - No external dependencies in unit tests
6. **Use fixtures** - Reusable test setup
7. **Mock external services** - AWS, Docker, SSH in unit tests
8. **Test edge cases** - Empty inputs, errors, timeouts

---

*Quick reference for OpsZen CI/CD pipeline*
*Run `make help` for all available commands*
