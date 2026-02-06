# GitHub Actions Workflow Fixes

## Overview

This document details the fixes applied to GitHub Actions workflows to resolve dependency installation failures that were causing all unit tests to fail in CI.

## Problem Statement

After pushing changes to GitHub, all unit tests were failing in GitHub Actions with the following error:

```
Run source .venv/bin/activate
Running unit tests...
./run_tests.sh unit
========================================
Checking Virtual Environment
========================================
✓ Virtual environment already activated: /home/runner/work/OpsZen/OpsZen/.venv
✗ pytest is not installed
⚠ Install test dependencies with: ./run_tests.sh install
make: *** [Makefile:43: test-unit] Error 1
Error: Process completed with exit code 2.
```

## Root Cause

The workflows were using **incorrect dependency installation commands** for projects using PEP 735 dependency groups:

❌ **Incorrect:**
```yaml
- name: Install dependencies
  run: |
    source .venv/bin/activate
    uv pip install -e ".[dev]"
```

The `uv pip install -e ".[dev]"` command doesn't work correctly with PEP 735 dependency groups defined in `pyproject.toml`.

✅ **Correct:**
```yaml
- name: Install dependencies
  run: |
    uv sync --all-groups
```

## Understanding PEP 735 Dependency Groups

OpsZen uses PEP 735 dependency groups in `pyproject.toml`:

```toml
[dependency-groups]
dev = [
    "pytest>=8.3.5",
    "pytest-cov>=5.0.0",
    "ruff>=0.15.0",
    # ... other dev dependencies
]
```

For PEP 735 projects, you **must** use `uv sync` instead of `uv pip install`:

| Command | Use Case | Works with PEP 735? |
|---------|----------|---------------------|
| `uv pip install -e ".[dev]"` | Legacy extras syntax | ❌ No |
| `uv pip install -e ".[test]"` | Legacy extras syntax | ❌ No |
| `uv sync --group dev` | Install specific group | ✅ Yes |
| `uv sync --all-groups` | Install all groups | ✅ Yes |

## Fixes Applied

### 1. Fixed All Workflow Files

Updated the following workflow files:
- `.github/workflows/tests.yml` - Main test workflow
- `.github/workflows/ci.yml` - CI pipeline
- `.github/workflows/pr-check.yml` - PR quick checks
- `.github/workflows/nightly.yml` - Nightly test runs

### 2. Changes Made

#### Before (Broken):
```yaml
- name: Create virtual environment
  run: |
    uv venv .venv

- name: Install dependencies (Unix)
  if: runner.os != 'Windows'
  run: |
    source .venv/bin/activate
    uv pip install -e ".[dev]"

- name: Install dependencies (Windows)
  if: runner.os == 'Windows'
  run: |
    .venv\Scripts\activate
    uv pip install -e ".[dev]"
```

#### After (Fixed):
```yaml
- name: Install dependencies
  run: |
    uv sync --all-groups
```

### 3. Additional Optimizations

1. **Removed redundant venv creation steps**: `uv sync` automatically creates the virtual environment if it doesn't exist
2. **Unified Unix/Windows steps**: `uv sync` works the same on all platforms
3. **Simplified workflow logic**: Fewer steps, clearer intent

## Impact on Each Workflow

### `tests.yml` - Main Test Workflow
- **Test job**: Fixed dependency installation for all OS/Python version combinations
- **Lint job**: Fixed dependency installation for linting checks
- **Security job**: Fixed dependency installation (kept additional security tools)
- **Quick-check job**: Fixed dependency installation for quick checks

### `ci.yml` - CI Pipeline
- Fixed main CI pipeline dependency installation
- Kept security tool installation as separate step (bandit, safety)

### `pr-check.yml` - PR Quick Check
- Fixed both quick-check and lint-check job dependency installation

### `nightly.yml` - Nightly Tests
- Fixed full test matrix dependency installation
- Fixed security check dependency installation

## How `uv sync` Works

When you run `uv sync --all-groups`:

1. **Creates venv automatically**: No need for explicit `uv venv .venv`
2. **Reads pyproject.toml**: Parses dependency groups
3. **Installs all dependencies**: Includes both main dependencies and all dependency groups
4. **Installs project in editable mode**: Automatically does `-e .`
5. **Creates lockfile**: Generates `uv.lock` for reproducible installs

### Options:

```bash
# Install all dependency groups (recommended for CI)
uv sync --all-groups

# Install specific group only
uv sync --group dev

# Install main dependencies only (no groups)
uv sync

# Install with frozen lockfile (fail if lockfile is outdated)
uv sync --frozen

# Install without dev dependencies (production)
uv sync --no-dev
```

## Testing the Fix

### Local Testing

Before pushing, verify the workflow commands work locally:

```bash
# Clean environment
rm -rf .venv

# Test the exact command used in workflows
uv sync --all-groups

# Verify pytest is installed
source .venv/bin/activate
pytest --version

# Run tests
make test-unit
```

### GitHub Actions Testing

After pushing:

1. Check the "Actions" tab in GitHub
2. Verify the "Install dependencies" step succeeds
3. Verify all test jobs pass
4. Check that pytest and other tools are found

## Common Issues and Solutions

### Issue: "No module named pytest"

**Cause**: Dependencies not installed correctly

**Solution**: Use `uv sync --all-groups` instead of `uv pip install`

### Issue: "Virtual environment not found"

**Cause**: Trying to activate venv before `uv sync` creates it

**Solution**: Remove explicit venv creation, let `uv sync` handle it

### Issue: "No such file or directory: ruff"

**Cause**: Calling tool directly without activating venv

**Solution**: Either:
- Activate venv: `source .venv/bin/activate && ruff check .`
- Use uv run: `uv run ruff check .`
- Use make targets: `make lint-check`

### Issue: Windows path errors

**Cause**: Using Unix-style paths on Windows

**Solution**: Use `uv sync` which handles paths cross-platform

## Best Practices for GitHub Actions with UV

### 1. Use uv sync for Installation

```yaml
- name: Install dependencies
  run: |
    uv sync --all-groups
```

### 2. Enable UV Cache

```yaml
- name: Install uv
  uses: astral-sh/setup-uv@v4
  with:
    enable-cache: true
```

### 3. Pin Python Version

```yaml
- name: Set up Python
  uses: actions/setup-python@v5
  with:
    python-version: "3.11"
```

### 4. Use Make Targets

```yaml
- name: Run tests
  run: |
    source .venv/bin/activate
    make test-unit
```

### 5. Avoid Redundant Steps

❌ **Don't:**
```yaml
- run: uv venv .venv
- run: source .venv/bin/activate
- run: uv pip install -e ".[dev]"
```

✅ **Do:**
```yaml
- run: uv sync --all-groups
```

## Verification Checklist

After applying these fixes, verify:

- [ ] All workflow files updated to use `uv sync --all-groups`
- [ ] Redundant venv creation steps removed
- [ ] Platform-specific install steps unified where possible
- [ ] Tests pass locally with `make ci`
- [ ] GitHub Actions workflows pass
- [ ] Coverage reports generate correctly
- [ ] Lint checks work
- [ ] Security scans complete

## Migration Guide for Other Projects

If you have a similar project using PEP 735 dependency groups:

### Step 1: Update pyproject.toml

Ensure you're using dependency groups:

```toml
[dependency-groups]
dev = [
    "pytest>=8.0.0",
    "ruff>=0.15.0",
]
```

### Step 2: Update GitHub Actions

Replace all instances of:
```yaml
uv pip install -e ".[dev]"
```

With:
```yaml
uv sync --all-groups
```

### Step 3: Remove Redundant Steps

Delete explicit venv creation:
```yaml
# DELETE THIS:
- name: Create virtual environment
  run: uv venv .venv
```

### Step 4: Update Local Scripts

Update any scripts that use `pip install`:
```bash
# Before
pip install -e ".[dev]"

# After
uv sync --all-groups
```

### Step 5: Update Documentation

Update README, CONTRIBUTING, and CI docs with new commands.

## References

- [UV Documentation](https://github.com/astral-sh/uv)
- [PEP 735 - Dependency Groups](https://peps.python.org/pep-0735/)
- [UV Migration Guide](./UV_MIGRATION.md)
- [Build Migration Guide](./BUILD_MIGRATION.md)
- [CI/CD Documentation](./CI_CD.md)

## Summary

The GitHub Actions test failures were caused by using the wrong dependency installation method for PEP 735 dependency groups. The fix was straightforward:

**Replace `uv pip install -e ".[dev]"` with `uv sync --all-groups`**

This change was applied across all four workflow files, simplifying the CI configuration and ensuring all dependencies are correctly installed in GitHub Actions.
