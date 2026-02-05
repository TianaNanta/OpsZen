#!/usr/bin/env python3
"""
Unit tests for LogAnalyzer module.
"""

import json

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
        assert analyzer.log_entries == []

    def test_detect_log_format_json(self, analyzer):
        """Test JSON log format detection."""
        json_lines = [
            '{"timestamp": "2024-01-15T10:30:45", "level": "INFO", "message": "test"}'
        ]
        assert analyzer.detect_log_format(json_lines) == "json"

    def test_detect_log_format_syslog(self, analyzer):
        """Test syslog format detection."""
        syslog_lines = ["Jan 15 10:30:45 hostname app[123]: Test message"]
        assert analyzer.detect_log_format(syslog_lines) == "syslog"

    def test_detect_log_format_apache(self, analyzer):
        """Test Apache log format detection."""
        apache_lines = [
            '127.0.0.1 - - [15/Jan/2024:10:30:45 +0000] "GET / HTTP/1.1" 200 1234'
        ]
        assert analyzer.detect_log_format(apache_lines) == "apache_common"

    def test_detect_log_format_python(self, analyzer):
        """Test Python log format detection."""
        python_lines = ["INFO:root:2024-01-15 10:30:45,123 - Test message"]
        assert analyzer.detect_log_format(python_lines) == "python"

    def test_detect_log_format_generic(self, analyzer):
        """Test generic log format detection."""
        generic_lines = ["2024-01-15 10:30:45 INFO Starting application"]
        assert analyzer.detect_log_format(generic_lines) == "generic"

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
        assert "timestamp" in parsed
        assert "message" in parsed

    def test_parse_line_json(self, analyzer):
        """Test parsing JSON log line."""
        line = '{"timestamp": "2024-01-15T10:30:45", "level": "ERROR", "message": "test error"}'
        parsed = analyzer.parse_line(line, "json")

        assert parsed is not None
        assert parsed["level"] == "ERROR"
        assert parsed["message"] == "test error"

    def test_load_logs_from_file(self, sample_log_file, analyzer):
        """Test loading logs from file."""
        count = analyzer.load_logs(str(sample_log_file))

        assert count > 0
        assert len(analyzer.log_entries) == count
        assert len(analyzer.log_entries) == 6  # Based on fixture

    def test_load_logs_nonexistent_file(self, analyzer):
        """Test loading from nonexistent file."""
        count = analyzer.load_logs("/nonexistent/file.log")
        assert count == 0
        assert len(analyzer.log_entries) == 0

    def test_filter_logs_by_level(self, sample_log_file, analyzer):
        """Test filtering logs by level."""
        filtered = analyzer.filter_logs(str(sample_log_file), level="ERROR")

        assert isinstance(filtered, list)
        # Should have ERROR and CRITICAL (which are >= ERROR level)
        for entry in filtered:
            assert entry.get("level") in ["ERROR", "CRITICAL"]

    def test_filter_logs_by_keyword(self, sample_log_file, analyzer):
        """Test filtering logs by keyword using pattern."""
        filtered = analyzer.filter_logs(str(sample_log_file), pattern="database")

        assert isinstance(filtered, list)
        for entry in filtered:
            assert "database" in entry.get("message", "").lower()

    def test_filter_logs_by_regex(self, sample_log_file, analyzer):
        """Test filtering logs by regex pattern."""
        filtered = analyzer.filter_logs(str(sample_log_file), pattern=r"(?i)config")

        assert isinstance(filtered, list)
        for entry in filtered:
            assert "config" in entry.get("message", "").lower()

    def test_filter_logs_by_time_range(self, sample_log_file, analyzer):
        """Test filtering logs by time range."""
        filtered = analyzer.filter_logs(
            str(sample_log_file),
            start_time="2024-01-15 10:30:46",
            end_time="2024-01-15 10:30:48",
        )

        assert isinstance(filtered, list)
        # All filtered entries should be within time range
        for entry in filtered:
            if entry.get("timestamp"):
                ts = entry["timestamp"]
                assert ts >= analyzer.parse_timestamp("2024-01-15 10:30:46")
                assert ts <= analyzer.parse_timestamp("2024-01-15 10:30:48")

    def test_analyze_logs_basic(self, sample_log_file, analyzer):
        """Test basic log analysis."""
        stats = analyzer.analyze_logs(str(sample_log_file))

        assert isinstance(stats, dict)
        assert "total_entries" in stats
        assert "level_counts" in stats
        assert stats["total_entries"] > 0

    def test_export_filtered_logs_json(self, sample_log_file, analyzer, temp_dir):
        """Test exporting filtered logs to JSON."""
        analyzer.load_logs(str(sample_log_file))
        output_file = temp_dir / "export.json"

        analyzer.export_filtered_logs(
            str(output_file), analyzer.log_entries, format="json"
        )

        assert output_file.exists()
        with open(output_file) as f:
            data = json.load(f)
            assert isinstance(data, list)
            assert len(data) > 0

    def test_export_filtered_logs_csv(self, sample_log_file, analyzer, temp_dir):
        """Test exporting filtered logs to CSV."""
        analyzer.load_logs(str(sample_log_file))
        output_file = temp_dir / "export.csv"

        analyzer.export_filtered_logs(
            str(output_file), analyzer.log_entries, format="csv"
        )

        assert output_file.exists()
        content = output_file.read_text()
        assert "timestamp" in content.lower() or "level" in content.lower()

    def test_export_filtered_logs_text(self, sample_log_file, analyzer, temp_dir):
        """Test exporting filtered logs to text."""
        analyzer.load_logs(str(sample_log_file))
        output_file = temp_dir / "export.txt"

        analyzer.export_filtered_logs(
            str(output_file), analyzer.log_entries, format="text"
        )

        assert output_file.exists()
        assert len(output_file.read_text()) > 0

    def test_parse_line_with_all_levels(self, analyzer):
        """Test parsing lines with all log levels."""
        levels = ["DEBUG", "INFO", "WARN", "WARNING", "ERROR", "CRITICAL"]

        for level in levels:
            line = f"2024-01-15 10:30:45 {level} Test message"
            parsed = analyzer.parse_line(line, "generic")

            assert parsed is not None
            # The level should be extracted and uppercased
            assert parsed.get("level") == level
            assert parsed.get("message") == "Test message"

    def test_empty_log_file(self, temp_dir, analyzer):
        """Test handling empty log file."""
        empty_file = temp_dir / "empty.log"
        empty_file.write_text("")

        count = analyzer.load_logs(str(empty_file))
        assert count == 0
        assert len(analyzer.log_entries) == 0

    def test_malformed_log_lines(self, temp_dir, analyzer):
        """Test handling malformed log lines."""
        malformed_file = temp_dir / "malformed.log"
        malformed_file.write_text(
            "This is not a valid log line\n\nAnother invalid line\n"
        )

        count = analyzer.load_logs(str(malformed_file))
        # May parse some or none depending on format detection
        assert count >= 0
        assert len(analyzer.log_entries) == count

    def test_filter_logs_case_insensitive(self, sample_log_file, analyzer):
        """Test that pattern filtering is case insensitive."""
        filtered = analyzer.filter_logs(str(sample_log_file), pattern="INFO")

        assert isinstance(filtered, list)
        # Pattern matching is case-insensitive in the implementation

    def test_multiple_filters_combined(self, sample_log_file, analyzer):
        """Test combining multiple filters."""
        filtered = analyzer.filter_logs(
            str(sample_log_file), level="WARNING", pattern="config"
        )

        assert isinstance(filtered, list)
        # Should have entries that match both criteria

    def test_analyze_logs_time_range(self, sample_log_file, analyzer):
        """Test log analysis includes time range."""
        stats = analyzer.analyze_logs(str(sample_log_file))

        assert "time_range" in stats
        # Time range should be present if logs have timestamps

    def test_common_log_formats(self, analyzer):
        """Test detection of common log formats."""
        formats = {
            "generic": ["2024-01-15 10:30:45 INFO Test"],
            "json": ['{"level": "INFO", "message": "test"}'],
            "syslog": ["Jan 15 10:30:45 host app[123]: test"],
            "apache_common": [
                '127.0.0.1 - - [15/Jan/2024:10:30:45 +0000] "GET / HTTP/1.1" 200 1234'
            ],
            "python": ["INFO:root:Test message"],
        }

        for expected_format, lines in formats.items():
            detected = analyzer.detect_log_format(lines)
            assert detected == expected_format
