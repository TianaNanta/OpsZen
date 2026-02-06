# Build System Migration to UV

## Overview

The OpsZen project build system has been migrated from the traditional `python -m build` + `twine` workflow to use `uv` for both building and publishing packages. This modernization aligns with the project's broader migration to `uv` tooling.

## Changes Made

### Build Process

**Before:**
```makefile
build:
    python -m build
```

**After:**
```makefile
build:
    uv build
```

### Publishing Process

**Before:**
```makefile
publish-test: build
    twine upload --repository testpypi dist/*

publish: build
    twine upload dist/*
```

**After:**
```makefile
publish-test: build
    uv publish --publish-url https://test.pypi.org/legacy/

publish: build
    uv publish
```

## Benefits

1. **Simplified Dependencies**: No need to install separate `build` and `twine` packages
2. **Consistency**: All build/test/publish operations now use `uv` tooling
3. **Speed**: `uv` is significantly faster than traditional Python packaging tools
4. **Modern Best Practices**: Aligns with current Python packaging ecosystem trends

## Build Backend

The project continues to use `hatchling` as the build backend (defined in `pyproject.toml`):

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

The `uv build` command automatically uses this configuration, eliminating the need for the separate `build` package.

## Package Structure

The built packages maintain the correct structure:
- Source distribution: `dist/opszen-{version}.tar.gz`
- Wheel: `dist/opszen-{version}-py3-none-any.whl`

All source files are correctly included under the `src/` directory structure.

## Usage

### Building Locally

```bash
make build
```

This will create distribution packages in the `dist/` directory.

### Publishing to Test PyPI

```bash
make publish-test
```

Requires PyPI credentials configured for `uv`.

### Publishing to Production PyPI

```bash
make publish
```

Includes a confirmation prompt before publishing to production.

## Configuration

### PyPI Credentials

For publishing, configure your PyPI credentials using one of these methods:

1. **Environment Variables:**
   ```bash
   export UV_PUBLISH_TOKEN="your-pypi-token"
   ```

2. **UV Configuration:**
   ```bash
   uv publish --token "your-pypi-token"
   ```

3. **Keyring (Recommended):**
   ```bash
   # UV automatically uses system keyring if available
   keyring set https://upload.pypi.org/legacy/ __token__
   ```

### Test PyPI

For Test PyPI, use a separate token:

```bash
export UV_PUBLISH_TOKEN="your-test-pypi-token"
make publish-test
```

## Troubleshooting

### Issue: "No module named build"

**Cause:** Attempting to use old `python -m build` command

**Solution:** This is resolved by using `uv build` instead. Update your Makefile or run directly:
```bash
uv build
```

### Issue: Build fails with hatchling errors

**Cause:** Missing or incorrect `pyproject.toml` configuration

**Solution:** Ensure your `pyproject.toml` has the correct build-system configuration:
```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

### Issue: Publish fails with authentication error

**Cause:** PyPI credentials not configured

**Solution:** Set the `UV_PUBLISH_TOKEN` environment variable or use keyring. See Configuration section above.

## Clean Build

To ensure a clean build, remove old build artifacts first:

```bash
make clean
make build
```

The `clean` target removes:
- `dist/` directory
- `build/` directory
- `*.egg-info` directories
- Python cache files

## Verification

After building, verify the package contents:

```bash
# List wheel contents
unzip -l dist/opszen-*.whl

# List source distribution contents
tar -tzf dist/opszen-*.tar.gz
```

## Related Documentation

- [UV Migration Guide](./UV_MIGRATION.md) - Complete migration to uv tooling
- [CI/CD Documentation](./CI_CD.md) - GitHub Actions workflows using uv
- [Development Workflow](./DEVELOPMENT.md) - Local development setup

## References

- [UV Documentation](https://github.com/astral-sh/uv)
- [Hatchling Documentation](https://hatch.pypa.io/latest/)
- [PEP 517 - Build System Interface](https://peps.python.org/pep-0517/)
- [PyPI Publishing Guide](https://packaging.python.org/tutorials/packaging-projects/)
