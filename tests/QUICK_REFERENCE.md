# OpsZen Test Suite - Quick Reference Card

## 🚀 Run Tests (Choose One)

```bash
# Using test runner script
./run_tests.sh

# Using Make
make test

# Using pytest directly
pytest tests/
```

## 📋 Common Commands

### Test Execution

| Command | Description |
|---------|-------------|
| `make test` | Run all tests |
| `make test-unit` | Unit tests only (fast) |
| `make test-integration` | Integration tests only |
| `make test-coverage` | Run with coverage report |
| `make test-fast` | Parallel execution |
| `make test-verbose` | Verbose output |
| `make test-failed` | Re-run only failures |

### Module-Specific

| Command | Description |
|---------|-------------|
| `make test-logs` | Log analyzer tests |
| `make test-ssh` | SSH manager tests |
| `make test-docker` | Docker manager tests |
| `make test-aws` | AWS provisioner tests |
| `make test-monitoring` | System monitor tests |

### Using run_tests.sh

```bash
./run_tests.sh all              # All tests
./run_tests.sh unit             # Unit tests
./run_tests.sh integration      # Integration tests
./run_tests.sh coverage         # With coverage
./run_tests.sh fast             # Parallel
./run_tests.sh specific <file>  # Specific test
./run_tests.sh clean            # Clean artifacts
./run_tests.sh install          # Install dependencies
```

### Using pytest

```bash
pytest tests/                   # All tests
pytest tests/unit/              # Unit tests only
pytest -m unit                  # By marker
pytest -k "ssh"                 # By keyword
pytest -x                       # Stop on first failure
pytest -vv                      # Verbose
pytest --lf                     # Last failed
pytest --pdb                    # Debug mode
```

## 🎯 Test Markers

```bash
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m "not slow"    # Skip slow tests
pytest -m docker        # Docker tests only
pytest -m ssh           # SSH tests only
pytest -m aws           # AWS tests only
```

## 📊 Coverage

```bash
# Generate coverage report
make test-coverage

# View HTML report
make test-report

# Terminal summary
coverage report

# XML for CI
coverage xml
```

## 🛠️ Setup

```bash
# Install test dependencies
./run_tests.sh install
# or
make install-dev
# or
pip install -r tests/requirements-test.txt

# Clean artifacts
make clean
```

## 📝 Test Structure

```
tests/
├── unit/                      # Fast, isolated tests
│   ├── test_log_analyzer.py
│   ├── test_ssh_manager.py
│   ├── test_docker_manager.py
│   └── ...
├── integration/               # End-to-end workflows
│   └── test_log_workflow.py
└── conftest.py               # Shared fixtures
```

## 🔍 Debugging

```bash
# Verbose output
pytest tests/ -vv

# Show print statements
pytest tests/ -s

# Stop on first failure
pytest tests/ -x

# Interactive debugger
pytest tests/ --pdb

# Show slow tests
pytest tests/ --durations=10
```

## 📦 Available Fixtures

From `conftest.py`:

- `temp_dir` - Temporary directory
- `temp_file` - Temporary file
- `sample_log_file` - Sample logs
- `sample_json_log_file` - JSON logs
- `mock_ssh_client` - Mocked SSH
- `mock_docker_client` - Mocked Docker
- `mock_boto3_ec2` - Mocked AWS EC2
- `mock_boto3_s3` - Mocked AWS S3
- `mock_psutil` - Mocked system metrics

## ✍️ Writing Tests

### Basic Template

```python
import pytest
from src.module import MyClass

class TestMyClass:
    @pytest.fixture
    def instance(self):
        return MyClass()

    def test_method(self, instance):
        result = instance.method()
        assert result == expected
```

### Using Fixtures

```python
def test_with_fixture(temp_file):
    content = temp_file.read_text()
    assert content == "test content\n"
```

### Markers

```python
@pytest.mark.unit
def test_something():
    pass

@pytest.mark.integration
def test_workflow():
    pass

@pytest.mark.slow
def test_performance():
    pass
```

## 🔧 Maintenance

```bash
# Clean test artifacts
make clean

# Format code
make format

# Run linters
make lint

# Run all checks
make check

# Full CI pipeline locally
make ci
```

## 📈 Stats

- **Total Tests**: 243+
- **Unit Tests**: 100+
- **Integration Tests**: 20+
- **Coverage Target**: >85%
- **Runtime**: ~30s (unit), ~2min (full)

## 🎓 Best Practices

1. ✅ Write tests first (TDD)
2. ✅ One assertion per test
3. ✅ Use descriptive names
4. ✅ Mock external dependencies
5. ✅ Keep tests fast
6. ✅ Test edge cases
7. ✅ Document complex tests

## 📚 Documentation

- `tests/README.md` - Full testing guide
- `TESTING.md` - Overview & architecture
- `TEST_SUITE_SUMMARY.md` - Implementation details
- This file - Quick reference

## 🆘 Troubleshooting

### Import errors
```bash
cd /path/to/OpsZen
pytest tests/
```

### Missing dependencies
```bash
make install-dev
```

### Slow tests
```bash
make test-fast  # Parallel execution
pytest -m "not slow"  # Skip slow tests
```

### Docker tests fail
```bash
docker info  # Check Docker is running
```

## 💡 Tips

- Use `make help` to see all available commands
- Use `./run_tests.sh help` for script options
- Use `pytest --markers` to list all markers
- Run `make diagnose` for system info
- Tests run automatically in CI/CD on push

## 🔗 Quick Links

- GitHub Actions: `.github/workflows/tests.yml`
- Test Config: `pytest.ini`
- Fixtures: `tests/conftest.py`
- Dependencies: `tests/requirements-test.txt`

---

**For detailed information, see `tests/README.md` or `TESTING.md`**