#!/usr/bin/env python3
"""
OpsZen Structured Logging System

Provides centralized logging configuration with support for:
- File logging with rotation
- Console logging with colors
- Multiple log levels
- Structured JSON logging
- Per-module loggers
"""

import contextlib
import logging
import logging.handlers
from pathlib import Path

from rich.console import Console
from rich.logging import RichHandler


class LoggerManager:
    """
    Centralized logger management for OpsZen.

    Provides structured logging with file rotation, console output,
    and configurable formatters.
    """

    _instance = None
    _initialized = False

    def __new__(cls):
        """Singleton pattern to ensure one logger manager."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the logger manager (only once)."""
        if not self._initialized:
            self.console = Console()
            self.loggers = {}
            self.log_dir = None
            self.log_level = logging.INFO
            self.console_output = True
            self.file_output = True
            self._initialized = True

    def setup(
        self,
        log_dir: str = "~/.opszen/logs",
        log_level: str = "INFO",
        console_output: bool = True,
        file_output: bool = True,
        log_format: str = "standard",
        max_bytes: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5,
    ):
        """
        Configure the logging system.

        Args:
            log_dir: Directory for log files
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            console_output: Enable console logging
            file_output: Enable file logging
            log_format: Format style (standard, json, detailed)
            max_bytes: Max log file size before rotation
            backup_count: Number of backup log files to keep
        """
        self.log_dir = Path(log_dir).expanduser().absolute()
        self.log_level = getattr(logging, log_level.upper(), logging.INFO)
        self.console_output = console_output
        self.file_output = file_output
        self.log_format = log_format
        self.max_bytes = max_bytes
        self.backup_count = backup_count

        # Create log directory
        if self.file_output:
            self.log_dir.mkdir(parents=True, exist_ok=True)

        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(self.log_level)

        # Remove existing handlers
        root_logger.handlers.clear()

    def get_logger(self, name: str) -> logging.Logger:
        """
        Get or create a logger with the specified name.

        Args:
            name: Logger name (typically __name__ of the module)

        Returns:
            Configured logger instance
        """
        if name in self.loggers:
            return self.loggers[name]

        logger = logging.getLogger(name)
        logger.setLevel(self.log_level)
        logger.propagate = False

        # Add console handler
        if self.console_output:
            console_handler = self._create_console_handler()
            logger.addHandler(console_handler)

        # Add file handler
        if self.file_output and self.log_dir:
            file_handler = self._create_file_handler(name)
            logger.addHandler(file_handler)

        self.loggers[name] = logger
        return logger

    def _create_console_handler(self) -> logging.Handler:
        """Create a Rich console handler with colors."""
        handler = RichHandler(
            console=self.console,
            show_time=True,
            show_path=False,
            markup=True,
            rich_tracebacks=True,
            tracebacks_show_locals=False,
        )
        handler.setLevel(self.log_level)

        # Simple format for console (Rich adds the rest)
        formatter = logging.Formatter(
            "%(message)s",
            datefmt="[%X]",
        )
        handler.setFormatter(formatter)

        return handler

    def _create_file_handler(self, logger_name: str) -> logging.Handler:
        """Create a rotating file handler."""
        # Sanitize logger name for filename
        safe_name = logger_name.replace(".", "_")
        log_file = self.log_dir / f"{safe_name}.log"

        handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=self.max_bytes,
            backupCount=self.backup_count,
            encoding="utf-8",
        )
        handler.setLevel(self.log_level)

        # Detailed format for file
        if self.log_format == "json":
            formatter = self._create_json_formatter()
        elif self.log_format == "detailed":
            formatter = logging.Formatter(
                "%(asctime)s | %(name)s | %(levelname)-8s | %(funcName)s:%(lineno)d | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        else:  # standard
            formatter = logging.Formatter(
                "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )

        handler.setFormatter(formatter)
        return handler

    def _create_json_formatter(self) -> logging.Formatter:
        """Create a JSON formatter for structured logging."""
        import json
        from datetime import datetime

        class JsonFormatter(logging.Formatter):
            def format(self, record):
                log_data = {
                    "timestamp": datetime.fromtimestamp(record.created).isoformat(),
                    "level": record.levelname,
                    "logger": record.name,
                    "module": record.module,
                    "function": record.funcName,
                    "line": record.lineno,
                    "message": record.getMessage(),
                }

                if record.exc_info:
                    log_data["exception"] = self.formatException(record.exc_info)

                if hasattr(record, "extra"):
                    log_data["extra"] = record.extra

                return json.dumps(log_data)

        return JsonFormatter()

    def set_level(self, level: str):
        """
        Change log level for all loggers.

        Args:
            level: New log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.log_level = getattr(logging, level.upper(), logging.INFO)

        # Update all existing loggers
        for logger in self.loggers.values():
            logger.setLevel(self.log_level)
            for handler in logger.handlers:
                handler.setLevel(self.log_level)

    def get_log_files(self) -> list:
        """
        Get list of all log files.

        Returns:
            List of log file paths
        """
        if not self.log_dir or not self.log_dir.exists():
            return []

        return sorted(self.log_dir.glob("*.log*"))

    def clear_logs(self):
        """Delete all log files."""
        if not self.log_dir:
            return
        for log_file in self.get_log_files():
            with contextlib.suppress(OSError):
                log_file.unlink()


# Global logger manager instance
_manager = LoggerManager()


def setup_logging(
    log_dir: str = "~/.opszen/logs",
    log_level: str = "INFO",
    console_output: bool = True,
    file_output: bool = True,
    log_format: str = "standard",
    max_bytes: int = 10 * 1024 * 1024,
    backup_count: int = 5,
):
    """
    Configure the OpsZen logging system.

    This should be called once at application startup.

    Args:
        log_dir: Directory for log files
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        console_output: Enable console logging
        file_output: Enable file logging
        log_format: Format style (standard, json, detailed)
        max_bytes: Max log file size before rotation (default: 10MB)
        backup_count: Number of backup log files to keep

    Example:
        >>> setup_logging(log_level="DEBUG", log_format="json")
    """
    _manager.setup(
        log_dir=log_dir,
        log_level=log_level,
        console_output=console_output,
        file_output=file_output,
        log_format=log_format,
        max_bytes=max_bytes,
        backup_count=backup_count,
    )


def get_logger(name: str = None) -> logging.Logger:
    """
    Get a logger for the specified module.

    Args:
        name: Logger name (use __name__ to get module logger)

    Returns:
        Configured logger instance

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Application started")
        >>> logger.error("An error occurred", exc_info=True)
    """
    if name is None:
        name = "opszen"

    return _manager.get_logger(name)


def set_log_level(level: str):
    """
    Change the log level for all loggers.

    Args:
        level: New log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Example:
        >>> set_log_level("DEBUG")
    """
    _manager.set_level(level)


def get_log_files() -> list:
    """
    Get list of all log files.

    Returns:
        List of Path objects for log files
    """
    return _manager.get_log_files()


def clear_logs():
    """Delete all log files."""
    _manager.clear_logs()


# Export public API
__all__ = [
    "setup_logging",
    "get_logger",
    "set_log_level",
    "get_log_files",
    "clear_logs",
    "LoggerManager",
]
