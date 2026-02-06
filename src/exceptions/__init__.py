#!/usr/bin/env python3
"""
OpsZen Custom Exceptions

Provides a hierarchy of custom exceptions for better error handling
and more descriptive error messages across the OpsZen toolkit.
"""


class OpsZenError(Exception):
    """
    Base exception for all OpsZen errors.

    All custom exceptions in OpsZen should inherit from this class.
    """

    def __init__(self, message: str, details: dict = None):
        """
        Initialize OpsZen error.

        Args:
            message: Human-readable error message
            details: Optional dictionary with additional error context
        """
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

    def __str__(self) -> str:
        if self.details:
            details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            return f"{self.message} ({details_str})"
        return self.message


# Configuration Errors
class ConfigurationError(OpsZenError):
    """Raised when there's a configuration error."""

    pass


class ConfigFileNotFoundError(ConfigurationError):
    """Raised when configuration file is not found."""

    pass


class ConfigValidationError(ConfigurationError):
    """Raised when configuration validation fails."""

    pass


# SSH Errors
class SSHError(OpsZenError):
    """Base exception for SSH-related errors."""

    pass


class SSHConnectionError(SSHError):
    """Raised when SSH connection fails."""

    pass


class SSHAuthenticationError(SSHError):
    """Raised when SSH authentication fails."""

    pass


class SSHCommandError(SSHError):
    """Raised when SSH command execution fails."""

    def __init__(
        self,
        message: str,
        command: str = None,
        exit_code: int = None,
        details: dict = None,
    ):
        details = details or {}
        if command:
            details["command"] = command
        if exit_code is not None:
            details["exit_code"] = exit_code
        super().__init__(message, details)


class SSHFileTransferError(SSHError):
    """Raised when SSH file transfer fails."""

    pass


# Docker Errors
class DockerError(OpsZenError):
    """Base exception for Docker-related errors."""

    pass


class DockerConnectionError(DockerError):
    """Raised when Docker daemon connection fails."""

    pass


class DockerContainerError(DockerError):
    """Raised when container operation fails."""

    def __init__(self, message: str, container_id: str = None, details: dict = None):
        details = details or {}
        if container_id:
            details["container_id"] = container_id
        super().__init__(message, details)


class DockerImageError(DockerError):
    """Raised when image operation fails."""

    pass


class DockerNetworkError(DockerError):
    """Raised when network operation fails."""

    pass


# AWS Errors
class AWSError(OpsZenError):
    """Base exception for AWS-related errors."""

    pass


class AWSConnectionError(AWSError):
    """Raised when AWS API connection fails."""

    pass


class AWSAuthenticationError(AWSError):
    """Raised when AWS authentication fails."""

    pass


class EC2Error(AWSError):
    """Raised when EC2 operation fails."""

    def __init__(self, message: str, instance_id: str = None, details: dict = None):
        details = details or {}
        if instance_id:
            details["instance_id"] = instance_id
        super().__init__(message, details)


class S3Error(AWSError):
    """Raised when S3 operation fails."""

    def __init__(
        self, message: str, bucket: str = None, key: str = None, details: dict = None
    ):
        details = details or {}
        if bucket:
            details["bucket"] = bucket
        if key:
            details["key"] = key
        super().__init__(message, details)


# Log Analysis Errors
class LogAnalysisError(OpsZenError):
    """Base exception for log analysis errors."""

    pass


class LogFileNotFoundError(LogAnalysisError):
    """Raised when log file is not found."""

    pass


class LogParseError(LogAnalysisError):
    """Raised when log parsing fails."""

    pass


class LogFilterError(LogAnalysisError):
    """Raised when log filtering fails."""

    pass


# Network Errors
class NetworkError(OpsZenError):
    """Base exception for network-related errors."""

    pass


class ConnectionTimeoutError(NetworkError):
    """Raised when network connection times out."""

    pass


class RetryExhaustedError(NetworkError):
    """Raised when retry attempts are exhausted."""

    def __init__(self, message: str, attempts: int = None, details: dict = None):
        details = details or {}
        if attempts is not None:
            details["attempts"] = attempts
        super().__init__(message, details)


# Monitoring Errors
class MonitoringError(OpsZenError):
    """Base exception for monitoring errors."""

    pass


class MetricCollectionError(MonitoringError):
    """Raised when metric collection fails."""

    pass


# Validation Errors
class ValidationError(OpsZenError):
    """Raised when validation fails."""

    pass


class InvalidInputError(ValidationError):
    """Raised when input validation fails."""

    pass


class InvalidPathError(ValidationError):
    """Raised when path validation fails."""

    pass


# Operation Errors
class OperationError(OpsZenError):
    """Base exception for operation errors."""

    pass


class OperationTimeoutError(OperationError):
    """Raised when operation times out."""

    pass


class OperationCancelledError(OperationError):
    """Raised when operation is cancelled."""

    pass


# Export all exceptions
__all__ = [
    # Base
    "OpsZenError",
    # Configuration
    "ConfigurationError",
    "ConfigFileNotFoundError",
    "ConfigValidationError",
    # SSH
    "SSHError",
    "SSHConnectionError",
    "SSHAuthenticationError",
    "SSHCommandError",
    "SSHFileTransferError",
    # Docker
    "DockerError",
    "DockerConnectionError",
    "DockerContainerError",
    "DockerImageError",
    "DockerNetworkError",
    # AWS
    "AWSError",
    "AWSConnectionError",
    "AWSAuthenticationError",
    "EC2Error",
    "S3Error",
    # Log Analysis
    "LogAnalysisError",
    "LogFileNotFoundError",
    "LogParseError",
    "LogFilterError",
    # Network
    "NetworkError",
    "ConnectionTimeoutError",
    "RetryExhaustedError",
    # Monitoring
    "MonitoringError",
    "MetricCollectionError",
    # Validation
    "ValidationError",
    "InvalidInputError",
    "InvalidPathError",
    # Operation
    "OperationError",
    "OperationTimeoutError",
    "OperationCancelledError",
]
