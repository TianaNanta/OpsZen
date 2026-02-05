# OpsZen Test Suite

Comprehensive test suite for the OpsZen DevOps automation toolkit.

## Table of Contents

- [Overview](#overview)
- [Test Structure](#test-structure)
- [Getting Started](#getting-started)
- [Running Tests](#running-tests)
- [Test Categories](#test-categories)
- [Writing Tests](#writing-tests)
- [Code Coverage](#code-coverage)
- [Continuous Integration](#continuous-integration)
- [Troubleshooting](#troubleshooting)

## Overview

The OpsZen test suite provides comprehensive testing coverage for all modules including:

- **Log Analyzer** - Log parsing, filtering, analysis, and export
- **SSH Manager** - Remote connection management and command execution
- **Docker Manager** - Container lifecycle management
- **Infrastructure Provisioner** - AWS resource provisioning
- **System Monitor** - System metrics collection and display

### Test Statistics

- **Unit Tests**: 100+ test cases
- **Integration Tests**: 20+ workflow tests
- **Code Coverage Target**: >85%
- **Test Execution Time**: ~30 seconds (unit), ~2 minutes (full suite)

## Test Structure

```
tests/
├── README.md                      # This file
├── requirements-test.txt          # Test dependencies
├── conftest.py                    # Shared fixtures and configuration
├── __init__.py                    # Test package initialization
│
├── unit/                          # Unit tests (fast, isolated)
│   ├── test_log_analyzer.py       # Log analyzer tests
│   ├── test_ssh_manager.py        # SSH manager tests
│   ├── test_ssh_config.py         # SSH config tests
│   ├── test_docker_manager.py     # Docker manager tests
│   ├── test_system_monitor.py     # System monitor tests
│   └── test_infrastructure_provisioner.py
│
├── integration/                   # Integration tests (slower, realistic)
│   └── test_log_workflow.py       # End-to-end log analysis workflows
│
└── fixtures/                      # Test data and fixtures
```

## Getting Started

### Prerequisites

- Python 3.8 or higher
- pip or uv package manager
- Virtual environment (recommended)

### Installation

1. **Install test dependencies:**

   ```bash
   # Using pip
   pip install -r tests/requirements-test.txt

   # Or use the test runner script
   ./run_tests.sh install
   ```

2. **Verify installation:**

   ```bash
   pytest --version
   ```

## Running Tests

### Quick Start

```bash
# Run all tests
./run_tests.sh

# Or use pytest directly
pytest tests/
```

### Common Test Commands

```bash
# Run only unit tests (fast)
./run_tests.sh unit

# Run only integration tests
./run_tests.sh integration

# Run tests with coverage report
./run_tests.sh coverage

# Run tests in parallel (faster)
./run_tests.sh fast

# Run with verbose output
./run_tests.sh verbose

# Re-run only failed tests
./run_tests.sh failed
```

### Running Specific Tests

```bash
# Run a specific test file
./run_tests.sh specific tests/unit/test_log_analyzer.py

# Run a specific test function
pytest tests/unit/test_log_analyzer.py::TestLogAnalyzer::test_parse_json_log

# Run tests matching a pattern
pytest tests/ -k "test_ssh"
```

### Category-Specific Tests

```bash
# Run Docker-related tests
./run_tests.sh docker

# Run SSH-related tests
./run_tests.sh ssh

# Run AWS-related tests
./run_tests.sh aws

# Run log analyzer tests
./run_tests.sh logs

# Run monitoring tests
./run_tests.sh monitoring
```

## Test Categories

Tests are organized using pytest markers:

### Unit Tests (`@pytest.mark.unit`)

Fast, isolated tests that don't require external dependencies.

```python
@pytest.mark.unit
def test_parse_log_line():
    analyzer = LogAnalyzer()
    result = analyzer.parse_line("2024-01-15 INFO Test", "generic")
    assert result["level"] == "INFO"
```

### Integration Tests (`@pytest.mark.integration`)

End-to-end tests that verify complete workflows.

```python
@pytest.mark.integration
def test_complete_log_analysis_workflow():
    # Load -> Filter -> Analyze -> Export
    analyzer = LogAnalyzer()
    analyzer.load_logs("test.log")
    errors = analyzer.filter_logs(level="ERROR")
    analyzer.export_filtered_logs(errors, "output.json")
```

### Slow Tests (`@pytest.mark.slow`)

Tests that take longer to execute (>1 second).

```python
@pytest.mark.slow
def test_large_dataset_performance():
    # Test with 10,000+ log entries
    pass
```

### Dependency-Based Markers

- `@pytest.mark.docker` - Requires Docker daemon
- `@pytest.mark.aws` - Requires AWS credentials
- `@pytest.mark.ssh` - Requires SSH connectivity
- `@pytest.mark.network` - Requires network access

### Running by Marker

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"

# Run Docker tests only
pytest -m docker
```

## Writing Tests

### Test Structure

Follow this structure for new tests:

```python
#!/usr/bin/env python3
"""
Unit tests for MyModule.

Description of what this test file covers.
"""

import pytest
from src.my_module import MyClass


class TestMyClass:
    """Test suite for MyClass."""

    @pytest.fixture
    def my_instance(self):
        """Create a MyClass instance for testing."""
        return MyClass()

    def test_initialization(self, my_instance):
        """Test MyClass initialization."""
        assert my_instance is not None
        # Add more assertions

    def test_method_success(self, my_instance):
        """Test method under normal conditions."""
        result = my_instance.method()
        assert result == expected_value

    def test_method_error_handling(self, my_instance):
        """Test method handles errors gracefully."""
        with pytest.raises(ValueError):
            my_instance.method(invalid_input)
```

### Using Fixtures

Shared fixtures are defined in `conftest.py`:

```python
def test_with_temp_file(temp_file):
    """Use the temp_file fixture."""
    assert temp_file.exists()
    content = temp_file.read_text()
    assert content == "test content\n"

def test_with_mock_ssh(mock_ssh_client):
    """Use mocked SSH client."""
    manager = SSHManager()
    manager.connect("test.com", "user")
    assert manager.current_host == "test.com"
```

### Best Practices

1. **Test Naming**: Use descriptive names that explain what is being tested
   ```python
   def test_parse_line_with_invalid_timestamp()  # Good
   def test_parse()                               # Bad
   ```

2. **Arrange-Act-Assert Pattern**:
   ```python
   def test_something():
       # Arrange: Set up test data
       analyzer = LogAnalyzer()
       
       # Act: Execute the code being tested
       result = analyzer.parse_line("test input", "format")
       
       # Assert: Verify the results
       assert result["level"] == "INFO"
   ```

3. **One Assertion Per Test** (when practical):
   ```python
   def test_log_level():
       assert log["level"] == "INFO"
   
   def test_log_message():
       assert log["message"] == "Test"
   ```

4. **Use Fixtures for Setup/Teardown**:
   ```python
   @pytest.fixture
   def database():
       db = Database()
       db.connect()
       yield db
       db.disconnect()
   ```

5. **Mock External Dependencies**:
   ```python
   @patch("boto3.client")
   def test_aws_operation(mock_client):
       # Test without real AWS calls
       pass
   ```

## Code Coverage

### Generating Coverage Reports

```bash
# Run tests with coverage
./run_tests.sh coverage

# Generate HTML report
./run_tests.sh report

# View coverage in terminal
coverage report

# Generate XML report (for CI)
coverage xml
```

### Coverage Targets

- **Overall Coverage**: >85%
- **Critical Modules**: >90%
  - LogAnalyzer
  - SSHManager
  - DockerManager

### Viewing Coverage

After running coverage, open `htmlcov/index.html` in your browser:

```bash
# Linux
xdg-open htmlcov/index.html

# macOS
open htmlcov/index.html

# Windows
start htmlcov/index.html
```

### Coverage Configuration

Coverage settings are in `pytest.ini`:

```ini
[coverage:run]
source = src
omit = */tests/*, */test_*.py

[coverage:report]
precision = 2
show_missing = True
```

## Continuous Integration

### GitHub Actions

Example workflow (`.github/workflows/tests.yml`):

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r tests/requirements-test.txt
    
    - name: Run tests with coverage
      run: |
        pytest tests/ --cov=src --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

### Pre-commit Hooks

Run tests before committing:

```bash
# .git/hooks/pre-commit
#!/bin/bash
./run_tests.sh unit
```

## Troubleshooting

### Common Issues

#### 1. Import Errors

**Problem**: `ModuleNotFoundError: No module named 'src'`

**Solution**: Ensure you're running tests from the project root:
```bash
cd /path/to/OpsZen
pytest tests/
```

#### 2. Missing Dependencies

**Problem**: `ModuleNotFoundError: No module named 'pytest'`

**Solution**: Install test dependencies:
```bash
./run_tests.sh install
```

#### 3. Fixture Not Found

**Problem**: `fixture 'my_fixture' not found`

**Solution**: Check that fixture is defined in `conftest.py` or imported correctly.

#### 4. Docker Tests Fail

**Problem**: Docker tests fail with connection errors

**Solution**: Ensure Docker daemon is running:
```bash
docker info
```

#### 5. AWS Tests Fail

**Problem**: AWS tests fail with authentication errors

**Solution**: Mocks should be in place. If tests require real AWS:
```bash
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
```

### Debugging Tests

```bash
# Run with extra verbosity
pytest tests/ -vv

# Show print statements
pytest tests/ -s

# Stop on first failure
pytest tests/ -x

# Run specific test with debugging
pytest tests/unit/test_log_analyzer.py::test_name -vv -s

# Use pytest debugger
pytest tests/ --pdb
```

### Performance Issues

```bash
# Run in parallel (requires pytest-xdist)
./run_tests.sh fast

# Profile slow tests
pytest tests/ --durations=10

# Show slowest tests
pytest tests/ --durations=0
```

## Test Maintenance

### Adding New Tests

1. Create test file in appropriate directory (`unit/` or `integration/`)
2. Follow naming convention: `test_<module_name>.py`
3. Add appropriate markers
4. Update this README if adding new test categories

### Updating Fixtures

1. Edit `conftest.py` for shared fixtures
2. Document complex fixtures with docstrings
3. Keep fixtures focused and reusable

### Cleaning Up

```bash
# Remove test artifacts
./run_tests.sh clean

# Remove all generated files
find . -type d -name __pycache__ -exec rm -rf {} +
rm -rf .pytest_cache htmlcov .coverage
```

## Additional Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [Python Testing Best Practices](https://docs.python-guide.org/writing/tests/)
- [Mocking with unittest.mock](https://docs.python.org/3/library/unittest.mock.html)

## Contributing

When adding new features to OpsZen:

1. Write tests first (TDD approach recommended)
2. Ensure all tests pass
3. Maintain >85% code coverage
4. Add integration tests for new workflows
5. Update this README if needed

## Support

For test-related issues:

1. Check [Troubleshooting](#troubleshooting) section
2. Review test output and error messages
3. Run with verbose mode for more details
4. Check GitHub issues for similar problems

---

**Last Updated**: 2024-01-15  
**Maintainer**: OpsZen Team