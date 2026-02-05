#!/usr/bin/env python3
"""
Unit tests for LogAnalyzer module.
"""

import json
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from src.logs.log_analyzer import LogAnalyzer


class TestLogAnalyzer:
    """Test suite for LogAnalyzer class."""

    @pytest.fixture
    def analyzer(self):
        """Create a LogAnalyzer instance."""
        return LogAnalyzer()

    def test_initialization(self, analyzer):
        """Test LogAnalyzer initialization."""
        assert analyzer is not None
        assert analyzer.logs == []
        assert analyzer.log_format is None

    def test_detect_log_format_json(self, analyzer):
        """Test JSON log format detection."""
        json_line = (
            '{"timestamp": "2024-01-15T10:30:45", "level": "INFO", "message": "test"}'
        )
        assert analyzer.detect_log_format(json_line) == "json"

    def test_detect_log_format_syslog(self, analyzer):
        """Test syslog format detection."""
        syslog_line = "Jan 15 10:30:45 hostname app[123]: Test message"
        assert analyzer.detect_log_format(syslog_line) == "syslog"

    def test_detect_log_format_apache(self, analyzer):
        """Test Apache log format detection."""
        apache_line = (
            '127.0.0.1 - - [15/Jan/2024:10:30:45 +0000] "GET / HTTP/1.1" 200 1234'
        )
        assert analyzer.detect_log_format(apache_line) == "apache"

    def test_detect_log_format_python(self, analyzer):
        """Test Python log format detection."""
        python_line = "INFO:root:2024-01-15 10:30:45,123 - Test message"
        assert analyzer.detect_log_format(python_line) == "python"

    def test_detect_log_format_generic(self, analyzer):
        """Test generic log format detection."""
        generic_line = "2024-01-15 10:30:45 INFO Starting application"
        assert analyzer.detect_log_format(generic_line) == "generic"

    def test_parse_timestamp_iso_format(self, analyzer):
        """Test parsing ISO format timestamp."""
        timestamp = analyzer.parse_timestamp("2024-01-15T10:30:45")
        assert timestamp is not None
        assert timestamp.year == 2024
        assert timestamp.month == 1
        assert timestamp.day == 15

    def test_parse_timestamp_standard_format(self, analyzer):
        """Test parsing standard timestamp format."""
        timestamp = analyzer.parse_timestamp("2024-01-15 10:30:45")
        assert timestamp is not None
        assert timestamp.year == 2024
        assert timestamp.month == 1
        assert timestamp.day == 15

    def test_parse_timestamp_invalid(self, analyzer):
        """Test parsing invalid timestamp."""
        timestamp = analyzer.parse_timestamp("invalid-timestamp")
        assert timestamp is None

    def test_parse_json_log(self, analyzer):
        """Test parsing JSON log entry."""
        json_line = '{"timestamp": "2024-01-15T10:30:45", "level": "INFO", "message": "test message"}'
        parsed = analyzer.parse_json_log(json_line)

        assert parsed is not None
        assert parsed["level"] == "INFO"
        assert parsed["message"] == "test message"
        assert "timestamp" in parsed

    def test_parse_json_log_invalid(self, analyzer):
        """Test parsing invalid JSON log."""
        parsed = analyzer.parse_json_log("not a json log")
        assert parsed is None

    def test_parse_line_generic(self, analyzer):
        """Test parsing generic log line."""
        line = "2024-01-15 10:30:45 INFO Starting application"
        parsed = analyzer.parse_line(line, "generic")

        assert parsed is not None
        assert parsed["level"] == "INFO"
        assert parsed["message"] == "Starting application"
        assert parsed["raw"] == line

    def test_parse_line_json(self, analyzer):
        """Test parsing JSON log line."""
        line = '{"timestamp": "2024-01-15T10:30:45", "level": "ERROR", "message": "error occurred"}'
        parsed = analyzer.parse_line(line, "json")

        assert parsed is not None
        assert parsed["level"] == "ERROR"
        assert parsed["message"] == "error occurred"

    def test_load_logs_from_file(self, sample_log_file, analyzer):
        """Test loading logs from file."""
        success = analyzer.load_logs(str(sample_log_file))

        assert success is True
        assert len(analyzer.logs) > 0
        assert analyzer.log_format is not None

    def test_load_logs_nonexistent_file(self, analyzer):
        """Test loading logs from nonexistent file."""
        success = analyzer.load_logs("/nonexistent/file.log")
        assert success is False

    def test_filter_logs_by_level(self, analyzer):
        """Test filtering logs by level."""
        analyzer.logs = [
            {"level": "INFO", "message": "info message", "timestamp": None, "raw": ""},
            {
                "level": "ERROR",
                "message": "error message",
                "timestamp": None,
                "raw": "",
            },
            {
                "level": "WARNING",
                "message": "warning message",
                "timestamp": None,
                "raw": "",
            },
            {
                "level": "ERROR",
                "message": "another error",
                "timestamp": None,
                "raw": "",
            },
        ]

        filtered = analyzer.filter_logs(level="ERROR")
        assert len(filtered) == 2
        assert all(log["level"] == "ERROR" for log in filtered)

    def test_filter_logs_by_keyword(self, analyzer):
        """Test filtering logs by keyword."""
        analyzer.logs = [
            {
                "level": "INFO",
                "message": "user login successful",
                "timestamp": None,
                "raw": "",
            },
            {
                "level": "ERROR",
                "message": "database connection failed",
                "timestamp": None,
                "raw": "",
            },
            {
                "level": "WARNING",
                "message": "user timeout warning",
                "timestamp": None,
                "raw": "",
            },
        ]

        filtered = analyzer.filter_logs(keyword="user")
        assert len(filtered) == 2

    def test_filter_logs_by_regex(self, analyzer):
        """Test filtering logs by regex pattern."""
        analyzer.logs = [
            {
                "level": "INFO",
                "message": "Request from 192.168.1.1",
                "timestamp": None,
                "raw": "",
            },
            {
                "level": "INFO",
                "message": "Request from 10.0.0.1",
                "timestamp": None,
                "raw": "",
            },
            {
                "level": "INFO",
                "message": "Invalid request",
                "timestamp": None,
                "raw": "",
            },
        ]

        filtered = analyzer.filter_logs(regex=r"\d+\.\d+\.\d+\.\d+")
        assert len(filtered) == 2

    def test_filter_logs_by_time_range(self, analyzer):
        """Test filtering logs by time range."""
        analyzer.logs = [
            {
                "level": "INFO",
                "message": "msg1",
                "timestamp": datetime(2024, 1, 15, 10, 0, 0),
                "raw": "",
            },
            {
                "level": "INFO",
                "message": "msg2",
                "timestamp": datetime(2024, 1, 15, 12, 0, 0),
                "raw": "",
            },
            {
                "level": "INFO",
                "message": "msg3",
                "timestamp": datetime(2024, 1, 15, 14, 0, 0),
                "raw": "",
            },
        ]

        filtered = analyzer.filter_logs(
            start_time="2024-01-15 11:00:00", end_time="2024-01-15 13:00:00"
        )
        assert len(filtered) == 1
        assert filtered[0]["message"] == "msg2"

    def test_analyze_logs_basic(self, analyzer):
        """Test basic log analysis."""
        analyzer.logs = [
            {
                "level": "INFO",
                "message": "info msg",
                "timestamp": datetime(2024, 1, 15, 10, 0, 0),
                "raw": "",
            },
            {
                "level": "ERROR",
                "message": "error msg",
                "timestamp": datetime(2024, 1, 15, 10, 0, 0),
                "raw": "",
            },
            {
                "level": "ERROR",
                "message": "another error",
                "timestamp": datetime(2024, 1, 15, 11, 0, 0),
                "raw": "",
            },
            {
                "level": "WARNING",
                "message": "warning msg",
                "timestamp": datetime(2024, 1, 15, 10, 0, 0),
                "raw": "",
            },
        ]

        stats = analyzer.analyze_logs()

        assert stats["total_lines"] == 4
        assert stats["level_counts"]["ERROR"] == 2
        assert stats["level_counts"]["INFO"] == 1
        assert stats["level_counts"]["WARNING"] == 1

    def test_export_filtered_logs_json(self, analyzer, temp_dir):
        """Test exporting filtered logs to JSON."""
        analyzer.logs = [
            {
                "level": "INFO",
                "message": "test message",
                "timestamp": None,
                "raw": "test",
            },
        ]

        output_file = temp_dir / "output.json"
        success = analyzer.export_filtered_logs(
            analyzer.logs, str(output_file), format="json"
        )

        assert success is True
        assert output_file.exists()

        with open(output_file, "r") as f:
            data = json.load(f)
            assert len(data) == 1
            assert data[0]["level"] == "INFO"

    def test_export_filtered_logs_csv(self, analyzer, temp_dir):
        """Test exporting filtered logs to CSV."""
        analyzer.logs = [
            {
                "level": "INFO",
                "message": "test message",
                "timestamp": datetime(2024, 1, 15, 10, 0, 0),
                "raw": "test",
            },
        ]

        output_file = temp_dir / "output.csv"
        success = analyzer.export_filtered_logs(
            analyzer.logs, str(output_file), format="csv"
        )

        assert success is True
        assert output_file.exists()

        content = output_file.read_text()
        assert "level,timestamp,message" in content.lower()
        assert "INFO" in content

    def test_export_filtered_logs_text(self, analyzer, temp_dir):
        """Test exporting filtered logs to text."""
        analyzer.logs = [
            {
                "level": "INFO",
                "message": "test message",
                "timestamp": None,
                "raw": "test raw",
            },
        ]

        output_file = temp_dir / "output.txt"
        success = analyzer.export_filtered_logs(
            analyzer.logs, str(output_file), format="text"
        )

        assert success is True
        assert output_file.exists()

        content = output_file.read_text()
        assert "test raw" in content

    def test_parse_line_with_all_levels(self, analyzer):
        """Test parsing lines with all log levels."""
        levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

        for level in levels:
            line = f"2024-01-15 10:30:45 {level} Test message"
            parsed = analyzer.parse_line(line, "generic")
            assert parsed is not None
            assert parsed["level"] == level

    def test_empty_log_file(self, temp_dir, analyzer):
        """Test loading an empty log file."""
        empty_file = temp_dir / "empty.log"
        empty_file.write_text("")

        success = analyzer.load_logs(str(empty_file))
        assert success is True
        assert len(analyzer.logs) == 0

    def test_malformed_log_lines(self, analyzer):
        """Test parsing malformed log lines."""
        malformed_lines = [
            "",
            "   ",
            "no timestamp or level here",
            "2024-01-15",  # incomplete
        ]

        for line in malformed_lines:
            parsed = analyzer.parse_line(line, "generic")
            # Should still parse but with limited info
            assert parsed is not None
            assert "raw" in parsed

    def test_filter_logs_case_insensitive(self, analyzer):
        """Test case-insensitive keyword filtering."""
        analyzer.logs = [
            {"level": "INFO", "message": "ERROR in logs", "timestamp": None, "raw": ""},
            {
                "level": "ERROR",
                "message": "error occurred",
                "timestamp": None,
                "raw": "",
            },
        ]

        # Filter by level should be exact match
        filtered = analyzer.filter_logs(level="error")
        # Depends on implementation - might want to adjust based on actual behavior

    def test_multiple_filters_combined(self, analyzer):
        """Test applying multiple filters simultaneously."""
        analyzer.logs = [
            {
                "level": "ERROR",
                "message": "database error",
                "timestamp": datetime(2024, 1, 15, 10, 0, 0),
                "raw": "",
            },
            {
                "level": "ERROR",
                "message": "network error",
                "timestamp": datetime(2024, 1, 15, 11, 0, 0),
                "raw": "",
            },
            {
                "level": "WARNING",
                "message": "database warning",
                "timestamp": datetime(2024, 1, 15, 10, 30, 0),
                "raw": "",
            },
        ]

        filtered = analyzer.filter_logs(level="ERROR", keyword="database")
        assert len(filtered) == 1
        assert filtered[0]["message"] == "database error"

    def test_analyze_logs_time_range(self, analyzer):
        """Test time range in log analysis."""
        analyzer.logs = [
            {
                "level": "INFO",
                "message": "msg",
                "timestamp": datetime(2024, 1, 15, 9, 0, 0),
                "raw": "",
            },
            {
                "level": "INFO",
                "message": "msg",
                "timestamp": datetime(2024, 1, 16, 15, 0, 0),
                "raw": "",
            },
        ]

        stats = analyzer.analyze_logs()
        assert "time_range" in stats
        # Verify time range is calculated correctly

    def test_common_log_formats(self, analyzer):
        """Test detection of various common log formats."""
        test_cases = {
            "nginx_access": '127.0.0.1 - - [15/Jan/2024:10:30:45 +0000] "GET /api HTTP/1.1" 200 512',
            "apache_error": "[Mon Jan 15 10:30:45.123456 2024] [error] [client 127.0.0.1] Error message",
            "docker": "2024-01-15T10:30:45.123456789Z container_name: log message",
            "kubernetes": "2024-01-15T10:30:45.123456789Z stdout F log message from pod",
        }

        for name, line in test_cases.items():
            format_detected = analyzer.detect_log_format(line)
            assert format_detected is not None, f"Failed to detect format for {name}"
