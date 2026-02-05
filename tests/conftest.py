#!/usr/bin/env python3
"""
Shared pytest fixtures and configuration for OpsZen test suite.
"""

import os
import sys
import tempfile
from pathlib import Path
from typing import Dict, Generator
from unittest.mock import MagicMock, Mock, patch

import pytest

# ============================================================================
# Virtual Environment Check (Pytest Plugin Hooks)
# ============================================================================


def is_venv_active():
    """Check if a virtual environment is currently activated."""
    # Check for virtual environment indicators
    return (
        hasattr(sys, "real_prefix")  # virtualenv
        or (
            hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
        )  # venv/pyvenv
        or os.environ.get("VIRTUAL_ENV") is not None  # Environment variable
    )


def get_venv_path():
    """Get the path to the virtual environment if active."""
    return os.environ.get("VIRTUAL_ENV", sys.prefix)


def get_project_venv_path():
    """Get the expected path to the project's virtual environment."""
    # Assume we're in the tests directory or project root
    if Path.cwd().name == "tests":
        return Path.cwd().parent / ".venv"
    return Path.cwd() / ".venv"


def pytest_configure(config):
    """
    Pytest hook that runs during configuration phase.

    This checks if virtual environment is activated and provides warnings/info
    to help users set up their environment correctly.
    """
    print("\n" + "=" * 78)
    print("🔍 OpsZen Test Suite - Virtual Environment Check")
    print("=" * 78)

    if is_venv_active():
        venv_path = get_venv_path()
        project_venv = get_project_venv_path()

        print(f"✓ Virtual environment is active")
        print(f"  Location: {venv_path}")

        # Check if it's the project's venv
        if Path(venv_path) == project_venv:
            print(f"✓ Using project virtual environment")
        else:
            print(f"⚠ Using a different virtual environment")
            print(f"  Project venv: {project_venv}")
            print(f"  Current venv: {venv_path}")

        print("=" * 78 + "\n")

    else:
        # Not in a virtual environment
        project_venv = get_project_venv_path()

        print("⚠️  WARNING: Virtual environment is NOT activated!")
        print("=" * 78)

        if project_venv.exists():
            print("\nℹ️  A virtual environment exists but is not activated.")
            print("\nTo activate it:")
            print("\n  On Linux/macOS:")
            print(f"    source {project_venv}/bin/activate")
            print("\n  On Windows (PowerShell):")
            print(f"    {project_venv}\\Scripts\\Activate.ps1")
            print("\n  On Windows (CMD):")
            print(f"    {project_venv}\\Scripts\\activate.bat")
            print("\n  Or use the activation helper:")
            print("    source activate_venv.sh")

        else:
            print("\nℹ️  No virtual environment found.")
            print("\nTo create and activate one:")
            print("\n  1. Create virtual environment:")
            print("       python3 -m venv .venv")
            print("\n  2. Activate it:")
            print("       source .venv/bin/activate  # Linux/macOS")
            print("       .venv\\Scripts\\activate    # Windows")
            print("\n  3. Install test dependencies:")
            print("       pip install -r tests/requirements-test.txt")
            print("\n  Or use the test runner (handles everything):")
            print("       ./run_tests.sh")
            print("       make install-dev")

        print("\n" + "=" * 78)
        print("⚠️  Tests may fail without proper dependencies!")
        print("=" * 78 + "\n")


def pytest_report_header(config):
    """
    Add custom header to pytest output with environment info.
    """
    lines = []

    if is_venv_active():
        venv_path = get_venv_path()
        lines.append(f"Virtual Environment: {venv_path}")
    else:
        lines.append("Virtual Environment: NOT ACTIVATED")

    lines.append(f"Python: {sys.executable}")
    lines.append(f"Python Version: {sys.version.split()[0]}")
    lines.append(f"Working Directory: {Path.cwd()}")

    return lines


def pytest_sessionstart(session):
    """
    Called after Session object has been created and before performing collection.

    This is a good place to set up test environment checks.
    """
    # Check for critical dependencies
    critical_packages = ["pytest", "pytest_cov"]
    missing_packages = []

    for package in critical_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing_packages.append(package)

    if missing_packages and not is_venv_active():
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("    This is likely because no virtual environment is activated.\n")


def pytest_collection_finish(session):
    """
    Called after collection has been performed.

    Show summary of what will be tested.
    """
    if session.config.option.collectonly:
        return

    num_items = len(session.items)
    if num_items > 0:
        print(f"\n📊 Collected {num_items} test(s)")

        # Count tests by marker
        markers = {}
        for item in session.items:
            for marker in item.iter_markers():
                markers[marker.name] = markers.get(marker.name, 0) + 1

        if markers:
            print("\n📋 Test Categories:")
            for marker, count in sorted(markers.items()):
                if marker not in ["parametrize", "skip", "skipif", "xfail"]:
                    print(f"   {marker}: {count}")

        print()


# ============================================================================
# Fixture Utilities
# ============================================================================


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def temp_file(temp_dir: Path) -> Generator[Path, None, None]:
    """Create a temporary file for testing."""
    tmp_file = temp_dir / "test_file.txt"
    tmp_file.write_text("test content\n")
    yield tmp_file


@pytest.fixture
def sample_log_file(temp_dir: Path) -> Path:
    """Create a sample log file with various log formats."""
    log_file = temp_dir / "test.log"
    log_content = """2024-01-15 10:30:45 INFO Starting application
2024-01-15 10:30:46 DEBUG Loading configuration
2024-01-15 10:30:47 WARNING Configuration file not found, using defaults
2024-01-15 10:30:48 ERROR Failed to connect to database
2024-01-15 10:30:49 CRITICAL System shutdown initiated
2024-01-15 10:30:50 INFO Application terminated
"""
    log_file.write_text(log_content)
    return log_file


@pytest.fixture
def sample_json_log_file(temp_dir: Path) -> Path:
    """Create a sample JSON log file."""
    log_file = temp_dir / "test.json.log"
    log_content = """{"timestamp": "2024-01-15T10:30:45", "level": "INFO", "message": "Starting application"}
{"timestamp": "2024-01-15T10:30:46", "level": "DEBUG", "message": "Loading configuration"}
{"timestamp": "2024-01-15T10:30:47", "level": "WARNING", "message": "Configuration file not found"}
{"timestamp": "2024-01-15T10:30:48", "level": "ERROR", "message": "Failed to connect to database"}
"""
    log_file.write_text(log_content)
    return log_file


@pytest.fixture
def sample_syslog_file(temp_dir: Path) -> Path:
    """Create a sample syslog format file."""
    log_file = temp_dir / "syslog"
    log_content = """Jan 15 10:30:45 hostname systemd[1]: Started application
Jan 15 10:30:46 hostname kernel: [12345.678901] USB disconnect
Jan 15 10:30:47 hostname app[12345]: WARNING: Configuration missing
Jan 15 10:30:48 hostname app[12345]: ERROR: Connection failed
"""
    log_file.write_text(log_content)
    return log_file


# ============================================================================
# SSH/Remote Fixtures
# ============================================================================


@pytest.fixture
def mock_ssh_client():
    """Mock paramiko SSH client."""
    with patch("paramiko.SSHClient") as mock_client:
        client_instance = MagicMock()
        mock_client.return_value = client_instance

        # Mock transport
        mock_transport = MagicMock()
        mock_transport.is_active.return_value = True
        client_instance.get_transport.return_value = mock_transport

        # Mock exec_command
        mock_stdout = MagicMock()
        mock_stderr = MagicMock()
        mock_stdout.read.return_value = b"command output"
        mock_stderr.read.return_value = b""
        mock_stdout.channel.recv_exit_status.return_value = 0
        client_instance.exec_command.return_value = (
            MagicMock(),
            mock_stdout,
            mock_stderr,
        )

        yield client_instance


@pytest.fixture
def mock_scp_client():
    """Mock SCP client."""
    with patch("scp.SCPClient") as mock_scp:
        scp_instance = MagicMock()
        mock_scp.return_value.__enter__.return_value = scp_instance
        yield scp_instance


@pytest.fixture
def ssh_config_dir(temp_dir: Path) -> Path:
    """Create a temporary SSH config directory."""
    ssh_dir = temp_dir / ".ssh"
    ssh_dir.mkdir()

    # Create a sample SSH config
    config_file = ssh_dir / "config"
    config_content = """Host testhost
    HostName 192.168.1.100
    User testuser
    Port 22
    IdentityFile ~/.ssh/id_rsa

Host production
    HostName prod.example.com
    User admin
    Port 2222
"""
    config_file.write_text(config_content)

    # Create mock key files
    (ssh_dir / "id_rsa").write_text("mock private key")
    (ssh_dir / "id_rsa.pub").write_text("mock public key")
    (ssh_dir / "id_ed25519").write_text("mock ed25519 key")

    return ssh_dir


@pytest.fixture
def opszen_config_dir(temp_dir: Path) -> Path:
    """Create a temporary OpsZen config directory."""
    config_dir = temp_dir / ".opszen"
    config_dir.mkdir()

    # Create sample profiles
    profiles_file = config_dir / "ssh_profiles.conf"
    profiles_content = """[myserver]
hostname = 192.168.1.50
username = admin
port = 22
key_file = ~/.ssh/id_rsa

[devbox]
hostname = dev.example.com
username = developer
port = 2222
"""
    profiles_file.write_text(profiles_content)

    return config_dir


# ============================================================================
# Docker Fixtures
# ============================================================================


@pytest.fixture
def mock_docker_client():
    """Mock Docker client."""
    with patch("docker.from_env") as mock_from_env:
        client = MagicMock()
        mock_from_env.return_value = client

        # Mock containers
        mock_container1 = MagicMock()
        mock_container1.short_id = "abc123"
        mock_container1.name = "test_container_1"
        mock_container1.status = "running"
        mock_container1.image.tags = ["nginx:latest"]
        mock_container1.ports = {"80/tcp": [{"HostPort": "8080"}]}

        mock_container2 = MagicMock()
        mock_container2.short_id = "def456"
        mock_container2.name = "test_container_2"
        mock_container2.status = "exited"
        mock_container2.image.tags = ["redis:alpine"]
        mock_container2.ports = {}

        client.containers.list.return_value = [mock_container1]
        client.containers.list.side_effect = lambda all=False: (
            [mock_container1, mock_container2] if all else [mock_container1]
        )

        # Mock container operations
        client.containers.get.return_value = mock_container1
        client.containers.run.return_value = mock_container1

        yield client


# ============================================================================
# AWS/Infrastructure Fixtures
# ============================================================================


@pytest.fixture
def mock_boto3_ec2():
    """Mock boto3 EC2 client."""
    with patch("boto3.client") as mock_client:
        ec2_client = MagicMock()

        # Mock EC2 instances
        ec2_client.describe_instances.return_value = {
            "Reservations": [
                {
                    "Instances": [
                        {
                            "InstanceId": "i-1234567890abcdef0",
                            "InstanceType": "t2.micro",
                            "State": {"Name": "running"},
                            "PublicIpAddress": "54.123.45.67",
                            "Tags": [{"Key": "Name", "Value": "TestServer"}],
                        }
                    ]
                }
            ]
        }

        # Mock instance creation
        ec2_client.run_instances.return_value = {
            "Instances": [
                {
                    "InstanceId": "i-newinstance123",
                    "InstanceType": "t2.micro",
                    "State": {"Name": "pending"},
                }
            ]
        }

        mock_client.return_value = ec2_client
        yield ec2_client


@pytest.fixture
def mock_boto3_s3():
    """Mock boto3 S3 client."""
    with patch("boto3.client") as mock_client:
        s3_client = MagicMock()

        # Mock S3 buckets
        s3_client.list_buckets.return_value = {
            "Buckets": [
                {
                    "Name": "test-bucket-1",
                    "CreationDate": "2024-01-01T00:00:00Z",
                },
                {
                    "Name": "test-bucket-2",
                    "CreationDate": "2024-01-02T00:00:00Z",
                },
            ]
        }

        mock_client.return_value = s3_client
        yield s3_client


@pytest.fixture
def sample_infrastructure_config(temp_dir: Path) -> Path:
    """Create a sample infrastructure configuration YAML file."""
    config_file = temp_dir / "infrastructure.yaml"
    config_content = """ec2_instances:
  - name: WebServer
    image_id: ami-0c55b159cbfafe1f0
    instance_type: t2.micro
    key_name: my-key-pair
    security_group_ids:
      - sg-12345678
    subnet_id: subnet-12345678

s3_buckets:
  - name: my-app-bucket
    region: us-west-2
  - name: my-logs-bucket
    region: us-east-1
"""
    config_file.write_text(config_content)
    return config_file


# ============================================================================
# Monitoring Fixtures
# ============================================================================


@pytest.fixture
def mock_psutil():
    """Mock psutil for system monitoring tests."""
    with patch("psutil.cpu_percent") as mock_cpu, patch(
        "psutil.virtual_memory"
    ) as mock_mem, patch("psutil.disk_usage") as mock_disk, patch(
        "psutil.disk_partitions"
    ) as mock_partitions, patch("psutil.net_io_counters") as mock_net:
        mock_cpu.return_value = 45.5

        mock_mem.return_value = MagicMock(
            total=16 * 1024**3,  # 16 GB
            available=8 * 1024**3,  # 8 GB
            used=8 * 1024**3,  # 8 GB
            percent=50.0,
        )
        mock_mem.return_value._asdict.return_value = {
            "total": 16 * 1024**3,
            "available": 8 * 1024**3,
            "used": 8 * 1024**3,
            "percent": 50.0,
        }

        mock_partition = MagicMock()
        mock_partition.mountpoint = "/"
        mock_partition.fstype = "ext4"
        mock_partitions.return_value = [mock_partition]

        mock_disk.return_value = MagicMock(
            total=500 * 1024**3,  # 500 GB
            used=250 * 1024**3,  # 250 GB
            free=250 * 1024**3,  # 250 GB
            percent=50.0,
        )
        mock_disk.return_value._asdict.return_value = {
            "total": 500 * 1024**3,
            "used": 250 * 1024**3,
            "free": 250 * 1024**3,
            "percent": 50.0,
        }

        mock_net.return_value = MagicMock(
            bytes_sent=1024 * 1024 * 100,  # 100 MB
            bytes_recv=1024 * 1024 * 200,  # 200 MB
        )
        mock_net.return_value._asdict.return_value = {
            "bytes_sent": 1024 * 1024 * 100,
            "bytes_recv": 1024 * 1024 * 200,
        }

        yield {
            "cpu": mock_cpu,
            "memory": mock_mem,
            "disk": mock_disk,
            "partitions": mock_partitions,
            "network": mock_net,
        }


# ============================================================================
# Log Analyzer Fixtures
# ============================================================================


@pytest.fixture
def sample_logs() -> Dict[str, str]:
    """Sample log entries for testing."""
    return {
        "simple": "2024-01-15 10:30:45 INFO Starting application",
        "json": '{"timestamp": "2024-01-15T10:30:45", "level": "INFO", "message": "Test"}',
        "syslog": "Jan 15 10:30:45 hostname app[123]: Test message",
        "apache": '127.0.0.1 - - [15/Jan/2024:10:30:45 +0000] "GET / HTTP/1.1" 200 1234',
        "python": "INFO:root:2024-01-15 10:30:45,123 - Test message",
    }


@pytest.fixture
def multi_format_log_file(temp_dir: Path) -> Path:
    """Create a log file with multiple formats."""
    log_file = temp_dir / "multi_format.log"
    log_content = """2024-01-15 10:30:45 INFO Starting application
{"timestamp": "2024-01-15T10:30:46", "level": "DEBUG", "message": "Debug message"}
Jan 15 10:30:47 hostname app[123]: Warning message
2024-01-15 10:30:48 ERROR Connection failed
{"timestamp": "2024-01-15T10:30:49", "level": "CRITICAL", "message": "Critical error"}
"""
    log_file.write_text(log_content)
    return log_file


# ============================================================================
# Environment Fixtures
# ============================================================================


@pytest.fixture
def mock_env_vars():
    """Mock environment variables."""
    with patch.dict(
        os.environ,
        {
            "AWS_REGION": "us-west-2",
            "USER": "testuser",
            "HOME": "/home/testuser",
        },
    ):
        yield os.environ


@pytest.fixture(autouse=True)
def reset_rich_console():
    """Reset Rich console state between tests."""
    # This ensures consistent output in tests
    yield
    # Cleanup happens automatically


# ============================================================================
# Helper Functions
# ============================================================================


def create_mock_file(path: Path, content: str) -> Path:
    """Helper to create a mock file with content."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    return path


def assert_log_contains(caplog, level: str, message: str):
    """Helper to assert log contains a message at a specific level."""
    for record in caplog.records:
        if record.levelname == level and message in record.message:
            return True
    raise AssertionError(f"Log message not found: {level} - {message}")
