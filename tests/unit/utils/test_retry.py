#!/usr/bin/env python3
"""
Unit tests for OpsZen retry utilities.
"""

import time
from unittest.mock import Mock

import pytest

from src.exceptions import RetryExhaustedError
from src.utils import (
    ensure_directory,
    format_bytes,
    retry,
    safe_dict_get,
    truncate_string,
    validate_path,
)


class TestRetryDecorator:
    """Test suite for retry decorator."""

    def test_successful_on_first_attempt(self):
        """Test function that succeeds on first attempt."""
        mock_func = Mock(return_value="success")

        @retry(max_attempts=3)
        def test_function():
            return mock_func()

        result = test_function()
        assert result == "success"
        assert mock_func.call_count == 1

    def test_retry_on_failure(self):
        """Test retry on failure."""
        mock_func = Mock(
            side_effect=[ValueError("fail"), ValueError("fail"), "success"]
        )

        @retry(max_attempts=3, delay=0.01, exceptions=(ValueError,))
        def test_function():
            return mock_func()

        result = test_function()
        assert result == "success"
        assert mock_func.call_count == 3

    def test_retry_exhausted(self):
        """Test that RetryExhaustedError is raised when retries exhausted."""
        mock_func = Mock(side_effect=ValueError("fail"))

        @retry(max_attempts=3, delay=0.01, exceptions=(ValueError,))
        def test_function():
            return mock_func()

        with pytest.raises(RetryExhaustedError) as exc_info:
            test_function()

        assert "Failed after 3 attempts" in str(exc_info.value)
        assert exc_info.value.details["attempts"] == 3
        assert mock_func.call_count == 3

    def test_exponential_backoff(self):
        """Test exponential backoff timing."""
        call_times = []

        @retry(max_attempts=3, delay=0.1, backoff=2.0, exceptions=(ValueError,))
        def test_function():
            call_times.append(time.time())
            if len(call_times) < 3:
                raise ValueError("fail")
            return "success"

        result = test_function()
        assert result == "success"
        assert len(call_times) == 3

        # Check delays are exponential (approximately)
        if len(call_times) >= 3:
            delay1 = call_times[1] - call_times[0]
            delay2 = call_times[2] - call_times[1]
            # Second delay should be roughly 2x first delay
            assert delay2 > delay1

    def test_specific_exception_only(self):
        """Test retry only catches specified exceptions."""
        mock_func = Mock(side_effect=RuntimeError("fail"))

        @retry(max_attempts=3, delay=0.01, exceptions=(ValueError,))
        def test_function():
            return mock_func()

        # RuntimeError should not be caught
        with pytest.raises(RuntimeError):
            test_function()

        assert mock_func.call_count == 1

    def test_multiple_exception_types(self):
        """Test retry catches multiple exception types."""
        mock_func = Mock(
            side_effect=[ValueError("fail1"), TypeError("fail2"), "success"]
        )

        @retry(max_attempts=3, delay=0.01, exceptions=(ValueError, TypeError))
        def test_function():
            return mock_func()

        result = test_function()
        assert result == "success"
        assert mock_func.call_count == 3

    def test_on_retry_callback(self):
        """Test on_retry callback is called."""
        retry_attempts = []

        def on_retry_callback(attempt, exception):
            retry_attempts.append((attempt, str(exception)))

        mock_func = Mock(
            side_effect=[ValueError("fail1"), ValueError("fail2"), "success"]
        )

        @retry(
            max_attempts=3,
            delay=0.01,
            on_retry=on_retry_callback,
            exceptions=(ValueError,),
        )
        def test_function():
            return mock_func()

        result = test_function()
        assert result == "success"
        assert len(retry_attempts) == 2
        assert retry_attempts[0][0] == 1
        assert retry_attempts[1][0] == 2

    def test_no_retry_on_success(self):
        """Test no retry when function succeeds."""
        mock_func = Mock(return_value="success")

        @retry(max_attempts=5, delay=0.01)
        def test_function():
            return mock_func()

        result = test_function()
        assert result == "success"
        assert mock_func.call_count == 1


class TestUtilityFunctions:
    """Test suite for utility functions."""

    def test_validate_path_valid(self, tmp_path):
        """Test validate_path with valid path."""
        assert validate_path(str(tmp_path), must_exist=True) is True

    def test_validate_path_nonexistent(self, tmp_path):
        """Test validate_path with non-existent path."""
        nonexistent = tmp_path / "does_not_exist"
        assert validate_path(str(nonexistent), must_exist=True) is False
        assert validate_path(str(nonexistent), must_exist=False) is True

    def test_validate_path_with_tilde(self):
        """Test validate_path expands tilde."""
        assert validate_path("~/", must_exist=False) is True

    def test_ensure_directory_creates(self, tmp_path):
        """Test ensure_directory creates directory."""
        new_dir = tmp_path / "new" / "nested" / "dir"
        assert ensure_directory(str(new_dir)) is True
        assert new_dir.exists()

    def test_ensure_directory_existing(self, tmp_path):
        """Test ensure_directory with existing directory."""
        assert ensure_directory(str(tmp_path)) is True

    def test_format_bytes(self):
        """Test format_bytes function."""
        assert format_bytes(500) == "500.0 B"
        assert format_bytes(1024) == "1.0 KB"
        assert format_bytes(1024 * 1024) == "1.0 MB"
        assert format_bytes(1024 * 1024 * 1024) == "1.0 GB"
        assert format_bytes(1536) == "1.5 KB"

    def test_truncate_string_short(self):
        """Test truncate_string with short string."""
        text = "Short text"
        assert truncate_string(text, max_length=80) == text

    def test_truncate_string_long(self):
        """Test truncate_string with long string."""
        text = "A" * 100
        result = truncate_string(text, max_length=50)
        assert len(result) == 50
        assert result.endswith("...")

    def test_truncate_string_custom_suffix(self):
        """Test truncate_string with custom suffix."""
        text = "A" * 100
        result = truncate_string(text, max_length=50, suffix="[...]")
        assert result.endswith("[...]")

    def test_safe_dict_get_existing(self):
        """Test safe_dict_get with existing key path."""
        data = {"a": {"b": {"c": 123}}}
        assert safe_dict_get(data, "a.b.c") == 123

    def test_safe_dict_get_missing(self):
        """Test safe_dict_get with missing key path."""
        data = {"a": {"b": {"c": 123}}}
        assert safe_dict_get(data, "a.x.y") is None
        assert safe_dict_get(data, "a.x.y", default=999) == 999

    def test_safe_dict_get_partial_path(self):
        """Test safe_dict_get with partial path."""
        data = {"a": {"b": {"c": 123}}}
        assert safe_dict_get(data, "a.b") == {"c": 123}

    def test_safe_dict_get_single_key(self):
        """Test safe_dict_get with single key."""
        data = {"key": "value"}
        assert safe_dict_get(data, "key") == "value"
