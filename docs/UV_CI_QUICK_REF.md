# UV CI Quick Reference Guide

## TL;DR - GitHub Actions with UV

**The only command you need for installing dependencies in CI:**

```yaml
- name: Install dependencies
  run: |
    uv sync --all-groups
```

That's it! No venv creation, no pip install, no platform-specific steps needed.

---

## Essential Commands

### For GitHub Actions Workflows

```yaml
# Install UV
- name: Install uv
  uses: astral-sh/setup-uv@v4
  with:
    enable-cache: true

# Install all dependencies (creates venv automatically)
- name: Install dependencies
  run: |
    uv sync --all-groups

# Run commands (activate venv first)
- name: Run tests
  run: |
    source .venv/bin/activate
    make test-unit
```

### For Local Development

```bash
# Install all dependencies
uv sync --all-groups

# Install specific group
uv sync --group dev

# Run without activating venv
uv run pytest tests/

# Or activate and run normally
source .venv/bin/activate
pytest tests/
```

---

## Common Patterns

### Basic Test Workflow

```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - uses: astral-sh/setup-uv@v4
        with:
          enable-cache: true

      - run: uv sync --all-groups

      - run: |
          source .venv/bin/activate
          make test
```

### Matrix Testing (Multiple Python Versions)

```yaml
strategy:
  matrix:
    python-version: ["3.8", "3.9", "3.10", "3.11", "3.12"]

steps:
  - uses: actions/checkout@v4

  - uses: actions/setup-python@v5
    with:
      python-version: ${{ matrix.python-version }}

  - uses: astral-sh/setup-uv@v4
    with:
      enable-cache: true

  - run: uv sync --all-groups

  - run: |
      source .venv/bin/activate
      pytest tests/
```

### Cross-Platform (Unix + Windows)

```yaml
strategy:
  matrix:
    os: [ubuntu-latest, macos-latest, windows-latest]

steps:
  - uses: actions/checkout@v4

  - uses: actions/setup-python@v5
    with:
      python-version: "3.11"

  - uses: astral-sh/setup-uv@v4
    with:
      enable-cache: true

  - run: uv sync --all-groups

  # UV sync works the same on all platforms!

  - name: Run tests (Unix)
    if: runner.os != 'Windows'
    run: |
      source .venv/bin/activate
      make test

  - name: Run tests (Windows)
    if: runner.os == 'Windows'
    shell: bash
    run: |
      source .venv/Scripts/activate
      pytest tests/
```

---

## Command Reference

### Installation Commands

| Command | What It Does | When To Use |
|---------|--------------|-------------|
| `uv sync` | Install main dependencies only | Production builds |
| `uv sync --all-groups` | Install all dependency groups | CI, local dev |
| `uv sync --group dev` | Install specific group | Targeted testing |
| `uv sync --frozen` | Use exact lockfile versions | Reproducible builds |
| `uv sync --no-dev` | Skip dev dependencies | Production |

### Running Commands

| Command | What It Does | When To Use |
|---------|--------------|-------------|
| `uv run <cmd>` | Run command in project env | Quick one-offs |
| `uv run pytest` | Run pytest without activating | CI scripts |
| `source .venv/bin/activate` | Activate environment | Interactive use |
| `uv tool run ruff check .` | Run tool without installing | External tools |

### Build & Publish

| Command | What It Does | When To Use |
|---------|--------------|-------------|
| `uv build` | Build source dist + wheel | Package creation |
| `uv publish` | Publish to PyPI | Releases |
| `uv publish --publish-url https://test.pypi.org/legacy/` | Publish to Test PyPI | Testing releases |

---

## Common Mistakes (Don't Do This!)

### ❌ Wrong: Old pip-style installation
```yaml
- run: uv venv .venv
- run: source .venv/bin/activate
- run: uv pip install -e ".[dev]"
```

### ✅ Right: Use uv sync
```yaml
- run: uv sync --all-groups
```

---

### ❌ Wrong: Platform-specific duplication
```yaml
- name: Install (Unix)
  if: runner.os != 'Windows'
  run: |
    source .venv/bin/activate
    uv sync --all-groups

- name: Install (Windows)
  if: runner.os == 'Windows'
  run: |
    .venv\Scripts\activate
    uv sync --all-groups
```

### ✅ Right: Single unified step
```yaml
- name: Install dependencies
  run: uv sync --all-groups
```

---

### ❌ Wrong: Calling tools without venv
```yaml
- run: ruff check .
- run: pytest tests/
```

### ✅ Right: Activate venv or use uv run
```yaml
- run: |
    source .venv/bin/activate
    ruff check .
    pytest tests/

# OR

- run: uv run ruff check .
- run: uv run pytest tests/
```

---

## Troubleshooting

### "pytest: command not found"
**Cause:** Virtual environment not activated  
**Fix:** Run `source .venv/bin/activate` before the command

### "No module named pytest"
**Cause:** Dependencies not installed correctly  
**Fix:** Use `uv sync --all-groups` instead of `uv pip install`

### "uv: command not found"
**Cause:** UV not installed in CI  
**Fix:** Add `uses: astral-sh/setup-uv@v4` step

### Slow CI builds
**Cause:** Not using UV cache  
**Fix:** Add `enable-cache: true` to setup-uv step

---

## Environment Variables

### For Publishing

```bash
# PyPI token
export UV_PUBLISH_TOKEN="pypi-token-here"

# Or use workflow secrets
env:
  UV_PUBLISH_TOKEN: ${{ secrets.PYPI_TOKEN }}
```

### For Caching

```yaml
- uses: astral-sh/setup-uv@v4
  with:
    enable-cache: true
    cache-dependency-glob: "**/pyproject.toml"
```

---

## Performance Tips

### 1. Enable Caching
```yaml
uses: astral-sh/setup-uv@v4
with:
  enable-cache: true
```
**Speeds up installs by 5-10x**

### 2. Use `--frozen` in CI
```yaml
run: uv sync --frozen --all-groups
```
**Fails fast if lockfile is outdated**

### 3. Parallel Jobs
```yaml
strategy:
  matrix:
    python-version: ["3.11", "3.12"]
  max-parallel: 4
```
**Run multiple jobs simultaneously**

### 4. Cache Python Packages
```yaml
- uses: actions/cache@v4
  with:
    path: ~/.cache/uv
    key: ${{ runner.os }}-uv-${{ hashFiles('**/pyproject.toml') }}
```
**Cache UV's package cache**

---

## Real-World Examples

### Example 1: Fast PR Checks
```yaml
name: PR Check
on: pull_request

jobs:
  quick:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - uses: astral-sh/setup-uv@v4
        with:
          enable-cache: true
      - run: uv sync --all-groups
      - run: |
          source .venv/bin/activate
          make quick  # format-check + unit tests
```

### Example 2: Full CI Pipeline
```yaml
name: CI
on: [push]

jobs:
  ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - uses: astral-sh/setup-uv@v4
        with:
          enable-cache: true
      - run: uv sync --all-groups
      - run: |
          source .venv/bin/activate
          make ci  # format, lint, test, coverage
```

### Example 3: Release Build
```yaml
name: Release
on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - uses: astral-sh/setup-uv@v4
      - run: uv build
      - run: uv publish
        env:
          UV_PUBLISH_TOKEN: ${{ secrets.PYPI_TOKEN }}
```

---

## Migration Checklist

Migrating from pip to UV in CI:

- [ ] Add `uses: astral-sh/setup-uv@v4` step
- [ ] Replace `pip install` with `uv sync --all-groups`
- [ ] Remove explicit `python -m venv .venv` steps
- [ ] Enable UV caching
- [ ] Update documentation
- [ ] Test locally: `uv sync --all-groups && make test`
- [ ] Push and verify CI passes

---

## Links

- [UV GitHub](https://github.com/astral-sh/uv)
- [UV Docs](https://docs.astral.sh/uv/)
- [PEP 735 - Dependency Groups](https://peps.python.org/pep-0735/)
- [setup-uv Action](https://github.com/astral-sh/setup-uv)

---

**Last Updated:** 2024-02-06  
**OpsZen Version:** 0.8.0
