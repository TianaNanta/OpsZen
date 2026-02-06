#!/usr/bin/env python3
"""
Unit tests for OpsZen custom exceptions.
"""

from src.exceptions import (
    AWSAuthenticationError,
    AWSConnectionError,
    AWSError,
    ConfigFileNotFoundError,
    ConfigurationError,
    ConfigValidationError,
    ConnectionTimeoutError,
    DockerConnectionError,
    DockerContainerError,
    DockerError,
    DockerImageError,
    DockerNetworkError,
    EC2Error,
    InvalidInputError,
    InvalidPathError,
    LogAnalysisError,
    LogFileNotFoundError,
    LogFilterError,
    LogParseError,
    MetricCollectionError,
    MonitoringError,
    NetworkError,
    OperationCancelledError,
    OperationError,
    OperationTimeoutError,
    OpsZenError,
    RetryExhaustedError,
    S3Error,
    SSHAuthenticationError,
    SSHCommandError,
    SSHConnectionError,
    SSHError,
    SSHFileTransferError,
    ValidationError,
)


class TestOpsZenError:
    """Test suite for base OpsZenError class."""

    def test_basic_error(self):
        """Test basic error creation."""
        error = OpsZenError("Something went wrong")
        assert str(error) == "Something went wrong"
        assert error.message == "Something went wrong"
        assert error.details == {}

    def test_error_with_details(self):
        """Test error with additional details."""
        error = OpsZenError(
            "Operation failed", details={"operation": "test", "reason": "timeout"}
        )
        assert "Operation failed" in str(error)
        assert "operation=test" in str(error)
        assert "reason=timeout" in str(error)
        assert error.details["operation"] == "test"

    def test_error_inheritance(self):
        """Test that it's an Exception."""
        error = OpsZenError("Test")
        assert isinstance(error, Exception)


class TestConfigurationErrors:
    """Test suite for configuration-related errors."""

    def test_configuration_error(self):
        """Test ConfigurationError."""
        error = ConfigurationError("Config is invalid")
        assert isinstance(error, OpsZenError)
        assert str(error) == "Config is invalid"

    def test_config_file_not_found_error(self):
        """Test ConfigFileNotFoundError."""
        error = ConfigFileNotFoundError("config.yaml not found")
        assert isinstance(error, ConfigurationError)
        assert isinstance(error, OpsZenError)

    def test_config_validation_error(self):
        """Test ConfigValidationError."""
        error = ConfigValidationError("Invalid AWS region")
        assert isinstance(error, ConfigurationError)


class TestSSHErrors:
    """Test suite for SSH-related errors."""

    def test_ssh_error(self):
        """Test base SSHError."""
        error = SSHError("SSH operation failed")
        assert isinstance(error, OpsZenError)

    def test_ssh_connection_error(self):
        """Test SSHConnectionError."""
        error = SSHConnectionError("Could not connect to server")
        assert isinstance(error, SSHError)

    def test_ssh_authentication_error(self):
        """Test SSHAuthenticationError."""
        error = SSHAuthenticationError("Authentication failed")
        assert isinstance(error, SSHError)

    def test_ssh_command_error(self):
        """Test SSHCommandError with command and exit code."""
        error = SSHCommandError("Command failed", command="ls -la", exit_code=127)
        assert isinstance(error, SSHError)
        assert error.details["command"] == "ls -la"
        assert error.details["exit_code"] == 127
        assert "command=ls -la" in str(error)

    def test_ssh_file_transfer_error(self):
        """Test SSHFileTransferError."""
        error = SSHFileTransferError("Failed to upload file")
        assert isinstance(error, SSHError)


class TestDockerErrors:
    """Test suite for Docker-related errors."""

    def test_docker_error(self):
        """Test base DockerError."""
        error = DockerError("Docker operation failed")
        assert isinstance(error, OpsZenError)

    def test_docker_connection_error(self):
        """Test DockerConnectionError."""
        error = DockerConnectionError("Cannot connect to Docker daemon")
        assert isinstance(error, DockerError)

    def test_docker_container_error(self):
        """Test DockerContainerError with container ID."""
        error = DockerContainerError(
            "Container operation failed", container_id="abc123"
        )
        assert isinstance(error, DockerError)
        assert error.details["container_id"] == "abc123"
        assert "container_id=abc123" in str(error)

    def test_docker_image_error(self):
        """Test DockerImageError."""
        error = DockerImageError("Failed to pull image")
        assert isinstance(error, DockerError)

    def test_docker_network_error(self):
        """Test DockerNetworkError."""
        error = DockerNetworkError("Network creation failed")
        assert isinstance(error, DockerError)


class TestAWSErrors:
    """Test suite for AWS-related errors."""

    def test_aws_error(self):
        """Test base AWSError."""
        error = AWSError("AWS operation failed")
        assert isinstance(error, OpsZenError)

    def test_aws_connection_error(self):
        """Test AWSConnectionError."""
        error = AWSConnectionError("Cannot connect to AWS")
        assert isinstance(error, AWSError)

    def test_aws_authentication_error(self):
        """Test AWSAuthenticationError."""
        error = AWSAuthenticationError("Invalid credentials")
        assert isinstance(error, AWSError)

    def test_ec2_error(self):
        """Test EC2Error with instance ID."""
        error = EC2Error("Instance operation failed", instance_id="i-123456")
        assert isinstance(error, AWSError)
        assert error.details["instance_id"] == "i-123456"
        assert "instance_id=i-123456" in str(error)

    def test_s3_error(self):
        """Test S3Error with bucket and key."""
        error = S3Error("S3 operation failed", bucket="my-bucket", key="file.txt")
        assert isinstance(error, AWSError)
        assert error.details["bucket"] == "my-bucket"
        assert error.details["key"] == "file.txt"
        assert "bucket=my-bucket" in str(error)
        assert "key=file.txt" in str(error)


class TestLogAnalysisErrors:
    """Test suite for log analysis errors."""

    def test_log_analysis_error(self):
        """Test base LogAnalysisError."""
        error = LogAnalysisError("Log analysis failed")
        assert isinstance(error, OpsZenError)

    def test_log_file_not_found_error(self):
        """Test LogFileNotFoundError."""
        error = LogFileNotFoundError("Log file not found")
        assert isinstance(error, LogAnalysisError)

    def test_log_parse_error(self):
        """Test LogParseError."""
        error = LogParseError("Failed to parse log line")
        assert isinstance(error, LogAnalysisError)

    def test_log_filter_error(self):
        """Test LogFilterError."""
        error = LogFilterError("Invalid filter expression")
        assert isinstance(error, LogAnalysisError)


class TestNetworkErrors:
    """Test suite for network-related errors."""

    def test_network_error(self):
        """Test base NetworkError."""
        error = NetworkError("Network operation failed")
        assert isinstance(error, OpsZenError)

    def test_connection_timeout_error(self):
        """Test ConnectionTimeoutError."""
        error = ConnectionTimeoutError("Connection timed out")
        assert isinstance(error, NetworkError)

    def test_retry_exhausted_error(self):
        """Test RetryExhaustedError with attempts."""
        error = RetryExhaustedError("All retry attempts failed", attempts=5)
        assert isinstance(error, NetworkError)
        assert error.details["attempts"] == 5
        assert "attempts=5" in str(error)


class TestMonitoringErrors:
    """Test suite for monitoring errors."""

    def test_monitoring_error(self):
        """Test base MonitoringError."""
        error = MonitoringError("Monitoring failed")
        assert isinstance(error, OpsZenError)

    def test_metric_collection_error(self):
        """Test MetricCollectionError."""
        error = MetricCollectionError("Failed to collect CPU metrics")
        assert isinstance(error, MonitoringError)


class TestValidationErrors:
    """Test suite for validation errors."""

    def test_validation_error(self):
        """Test base ValidationError."""
        error = ValidationError("Validation failed")
        assert isinstance(error, OpsZenError)

    def test_invalid_input_error(self):
        """Test InvalidInputError."""
        error = InvalidInputError("Invalid input provided")
        assert isinstance(error, ValidationError)

    def test_invalid_path_error(self):
        """Test InvalidPathError."""
        error = InvalidPathError("Path does not exist")
        assert isinstance(error, ValidationError)


class TestOperationErrors:
    """Test suite for operation errors."""

    def test_operation_error(self):
        """Test base OperationError."""
        error = OperationError("Operation failed")
        assert isinstance(error, OpsZenError)

    def test_operation_timeout_error(self):
        """Test OperationTimeoutError."""
        error = OperationTimeoutError("Operation timed out")
        assert isinstance(error, OperationError)

    def test_operation_cancelled_error(self):
        """Test OperationCancelledError."""
        error = OperationCancelledError("Operation was cancelled")
        assert isinstance(error, OperationError)


class TestErrorDetails:
    """Test error details functionality."""

    def test_empty_details(self):
        """Test error with no details."""
        error = OpsZenError("Error")
        assert error.details == {}
        assert str(error) == "Error"

    def test_single_detail(self):
        """Test error with single detail."""
        error = OpsZenError("Error", details={"code": 500})
        assert error.details["code"] == 500
        assert "code=500" in str(error)

    def test_multiple_details(self):
        """Test error with multiple details."""
        error = OpsZenError(
            "Error", details={"code": 500, "service": "API", "retry": True}
        )
        assert len(error.details) == 3
        assert "code=500" in str(error)
        assert "service=API" in str(error)
        assert "retry=True" in str(error)

    def test_details_in_subclass(self):
        """Test that subclass properly handles details."""
        error = SSHCommandError(
            "Command failed",
            command="test",
            exit_code=1,
            details={"host": "server.com"},
        )
        assert error.details["command"] == "test"
        assert error.details["exit_code"] == 1
        assert error.details["host"] == "server.com"
