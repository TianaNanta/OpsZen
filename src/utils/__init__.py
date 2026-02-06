#!/usr/bin/env python3
"""
OpsZen Utility Functions

Provides common utilities including retry logic, decorators, and helper functions.
"""

import functools
import time
from typing import Callable, Optional, Tuple, Type

from src.exceptions import RetryExhaustedError


def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Optional[Callable] = None,
):
    """
    Decorator to retry a function with exponential backoff.

    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff: Multiplier for delay (exponential backoff)
        exceptions: Tuple of exceptions to catch and retry
        on_retry: Optional callback function called on each retry

    Returns:
        Decorated function with retry logic

    Example:
        >>> @retry(max_attempts=3, delay=1, backoff=2)
        ... def unstable_network_call():
        ...     # This will retry up to 3 times with exponential backoff
        ...     response = requests.get("https://api.example.com")
        ...     return response.json()

        >>> @retry(max_attempts=5, exceptions=(ConnectionError, TimeoutError))
        ... def connect_to_server():
        ...     return server.connect()
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0
            current_delay = delay

            while attempt < max_attempts:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    attempt += 1

                    if attempt >= max_attempts:
                        # Try to log, but don't fail if logger not set up
                        try:
                            from src.logging import get_logger

                            logger = get_logger(__name__)
                            logger.error(
                                f"Function {func.__name__} failed after {max_attempts} attempts",
                                exc_info=True,
                            )
                        except Exception:
                            pass
                        raise RetryExhaustedError(
                            f"Failed after {max_attempts} attempts: {str(e)}",
                            attempts=max_attempts,
                        ) from e

                    # Try to log, but don't fail if logger not set up
                    try:
                        from src.logging import get_logger

                        logger = get_logger(__name__)
                        logger.warning(
                            f"Attempt {attempt}/{max_attempts} failed for {func.__name__}: {str(e)}. "
                            f"Retrying in {current_delay:.1f}s..."
                        )
                    except Exception:
                        pass

                    if on_retry:
                        on_retry(attempt, e)

                    time.sleep(current_delay)
                    current_delay *= backoff

        return wrapper

    return decorator


def validate_path(path: str, must_exist: bool = False) -> bool:
    """
    Validate a file system path.

    Args:
        path: Path to validate
        must_exist: Whether path must exist

    Returns:
        True if valid, False otherwise
    """
    from pathlib import Path

    try:
        p = Path(path).expanduser()
        if must_exist:
            return p.exists()
        return True
    except (OSError, RuntimeError):
        return False


def ensure_directory(path: str) -> bool:
    """
    Ensure a directory exists, creating it if necessary.

    Args:
        path: Directory path

    Returns:
        True if directory exists or was created, False on error
    """
    from pathlib import Path

    try:
        Path(path).expanduser().mkdir(parents=True, exist_ok=True)
        return True
    except OSError:
        return False


def format_bytes(size: int) -> str:
    """
    Format bytes as human-readable string.

    Args:
        size: Size in bytes

    Returns:
        Formatted string (e.g., "1.5 GB")
    """
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} PB"


def truncate_string(text: str, max_length: int = 80, suffix: str = "...") -> str:
    """
    Truncate a string to maximum length.

    Args:
        text: String to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


def safe_dict_get(data: dict, key_path: str, default=None):
    """
    Safely get nested dictionary value using dot notation.

    Args:
        data: Dictionary to search
        key_path: Dot-separated key path (e.g., "a.b.c")
        default: Default value if key not found

    Returns:
        Value at key path or default

    Example:
        >>> data = {"a": {"b": {"c": 123}}}
        >>> safe_dict_get(data, "a.b.c")
        123
        >>> safe_dict_get(data, "a.x.y", default=0)
        0
    """
    keys = key_path.split(".")
    value = data

    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return default

    return value


__all__ = [
    "retry",
    "validate_path",
    "ensure_directory",
    "format_bytes",
    "truncate_string",
    "safe_dict_get",
]
