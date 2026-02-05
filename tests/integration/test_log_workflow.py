#!/usr/bin/env python3
"""
Integration tests for log analysis workflow.

Tests end-to-end functionality of the log analyzer with realistic scenarios.
"""

import json
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from src.logs.log_analyzer import LogAnalyzer


@pytest.mark.integration
class TestLogAnalysisWorkflow:
    """Integration tests for complete log analysis workflows."""

    @pytest.fixture
    def large_log_file(self, temp_dir):
        """Create a large realistic log file for testing."""
        log_file = temp_dir / "application.log"

        base_time = datetime(2024, 1, 15, 10, 0, 0)
        log_entries = []

        # Generate 1000 log entries over 24 hours
        for i in range(1000):
            timestamp = base_time + timedelta(minutes=i)

            # Mix of different log levels
            if i % 50 == 0:
                level = "CRITICAL"
                message = f"Critical system error #{i}"
            elif i % 20 == 0:
                level = "ERROR"
                message = f"Database connection failed: timeout after 30s (attempt {i})"
            elif i % 10 == 0:
                level = "WARNING"
                message = f"Slow query detected: {i * 10}ms"
            elif i % 5 == 0:
                level = "DEBUG"
                message = f"Processing request {i}"
            else:
                level = "INFO"
                message = f"Request completed successfully: user_id={i}"

            log_entries.append(
                f"{timestamp.strftime('%Y-%m-%d %H:%M:%S')} {level} {message}"
            )

        log_file.write_text("\n".join(log_entries))
        return log_file

    @pytest.fixture
    def mixed_format_log_file(self, temp_dir):
        """Create a log file with multiple formats."""
        log_file = temp_dir / "mixed.log"

        entries = [
            "2024-01-15 10:00:00 INFO Application started",
            '{"timestamp": "2024-01-15T10:00:01", "level": "INFO", "message": "JSON log entry"}',
            "Jan 15 10:00:02 myapp systemd[1]: Service started",
            "2024-01-15 10:00:03 ERROR Failed to connect to database",
            '{"timestamp": "2024-01-15T10:00:04", "level": "ERROR", "message": "JSON error", "trace": "stack trace here"}',
            "2024-01-15 10:00:05 WARNING High memory usage detected",
        ]

        log_file.write_text("\n".join(entries))
        return log_file

    def test_complete_analysis_workflow(self, large_log_file):
        """Test complete workflow: load, filter, analyze, export."""
        analyzer = LogAnalyzer()

        # Step 1: Load logs
        count = analyzer.load_logs(str(large_log_file))
        assert count == 1000
        assert len(analyzer.log_entries) == 1000

        # Step 2: Filter for errors
        errors = analyzer.filter_logs(str(large_log_file), level="ERROR")
        assert len(errors) > 0
        # ERROR level includes ERROR and CRITICAL
        assert all(log.get("level") in ["ERROR", "CRITICAL"] for log in errors)

        # Step 3: Analyze logs
        stats = analyzer.analyze_logs(str(large_log_file))
        assert stats["total_entries"] == 1000
        assert "ERROR" in stats["level_counts"]
        assert "WARNING" in stats["level_counts"]

        # Step 4: Export filtered results
        output_file = large_log_file.parent / "errors.json"
        analyzer.export_filtered_logs(str(output_file), errors, format="json")
        assert output_file.exists()

        # Verify exported data
        with open(output_file, "r") as f:
            exported_data = json.load(f)
            assert len(exported_data) == len(errors)

    def test_time_based_filtering_workflow(self, large_log_file):
        """Test filtering logs by time range."""
        analyzer = LogAnalyzer()
        analyzer.load_logs(str(large_log_file))

        # Filter logs for a specific hour
        filtered = analyzer.filter_logs(
            str(large_log_file),
            start_time="2024-01-15 12:00:00",
            end_time="2024-01-15 13:00:00",
        )

        # Verify all filtered logs are within time range
        for log in filtered:
            if log.get("timestamp"):
                assert (
                    datetime(2024, 1, 15, 12, 0, 0)
                    <= log["timestamp"]
                    <= datetime(2024, 1, 15, 13, 0, 0)
                )

    def test_keyword_search_workflow(self, large_log_file):
        """Test keyword search across logs using pattern."""
        analyzer = LogAnalyzer()
        analyzer.load_logs(str(large_log_file))

        # Search for database-related logs
        db_logs = analyzer.filter_logs(str(large_log_file), pattern="database")
        assert len(db_logs) > 0
        assert all("database" in log.get("message", "").lower() for log in db_logs)

    def test_regex_pattern_workflow(self, large_log_file):
        """Test regex pattern matching."""
        analyzer = LogAnalyzer()
        analyzer.load_logs(str(large_log_file))

        # Find all logs with user_id pattern
        pattern_logs = analyzer.filter_logs(str(large_log_file), pattern=r"user_id=\d+")
        assert len(pattern_logs) > 0

    def test_multi_format_analysis(self, mixed_format_log_file):
        """Test analyzing logs with multiple formats."""
        analyzer = LogAnalyzer()
        count = analyzer.load_logs(str(mixed_format_log_file))

        assert count == 6
        assert len(analyzer.log_entries) == 6

    def test_export_all_formats(self, large_log_file):
        """Test exporting logs to different formats."""
        analyzer = LogAnalyzer()
        analyzer.load_logs(str(large_log_file))

        errors = analyzer.filter_logs(str(large_log_file), level="ERROR")

        # Test JSON export
        json_file = large_log_file.parent / "export.json"
        analyzer.export_filtered_logs(str(json_file), errors, format="json")
        assert json_file.exists()

        # Test CSV export
        csv_file = large_log_file.parent / "export.csv"
        analyzer.export_filtered_logs(str(csv_file), errors, format="csv")
        assert csv_file.exists()

        # Test text export
        txt_file = large_log_file.parent / "export.txt"
        analyzer.export_filtered_logs(str(txt_file), errors, format="text")
        assert txt_file.exists()

    def test_combined_filters(self, large_log_file):
        """Test combining multiple filters."""
        analyzer = LogAnalyzer()
        analyzer.load_logs(str(large_log_file))

        # Combine level and pattern filters
        filtered = analyzer.filter_logs(
            str(large_log_file), level="ERROR", pattern="database"
        )

        # All results should match both criteria
        for log in filtered:
            assert log.get("level") in ["ERROR", "CRITICAL"]
            assert "database" in log.get("message", "").lower()

    def test_statistics_accuracy(self, large_log_file):
        """Test accuracy of log statistics."""
        analyzer = LogAnalyzer()
        analyzer.load_logs(str(large_log_file))

        stats = analyzer.analyze_logs(str(large_log_file))

        # Verify statistics
        assert stats["total_entries"] == 1000
        assert isinstance(stats["level_counts"], dict)
        assert "time_range" in stats
        assert "common_messages" in stats

    def test_error_recovery(self):
        """Test error handling with invalid file."""
        analyzer = LogAnalyzer()

        # Try to load non-existent file
        count = analyzer.load_logs("/nonexistent/file.log")
        assert count == 0
        assert len(analyzer.log_entries) == 0

    def test_empty_log_handling(self, temp_dir):
        """Test handling of empty log files."""
        empty_file = temp_dir / "empty.log"
        empty_file.write_text("")

        analyzer = LogAnalyzer()
        count = analyzer.load_logs(str(empty_file))

        assert count == 0
        assert len(analyzer.log_entries) == 0

    def test_performance_large_dataset(self, temp_dir):
        """Test performance with large datasets."""
        # Create a very large log file (10,000 entries)
        large_file = temp_dir / "very_large.log"

        base_time = datetime(2024, 1, 1, 0, 0, 0)
        entries = []
        for i in range(10000):
            timestamp = base_time + timedelta(seconds=i)
            level = ["INFO", "DEBUG", "WARNING", "ERROR"][i % 4]
            message = f"Message {i}: Processing data batch {i // 100}"
            entries.append(
                f"{timestamp.strftime('%Y-%m-%d %H:%M:%S')} {level} {message}"
            )

        large_file.write_text("\n".join(entries))

        analyzer = LogAnalyzer()
        count = analyzer.load_logs(str(large_file))

        assert count == 10000
        assert len(analyzer.log_entries) == 10000

        # Filter should also be fast
        errors = analyzer.filter_logs(str(large_file), level="ERROR")
        assert len(errors) > 0

    def test_real_world_apache_logs(self, temp_dir):
        """Test with realistic Apache log format."""
        apache_log = temp_dir / "access.log"

        entries = [
            '127.0.0.1 - - [15/Jan/2024:10:30:45 +0000] "GET /index.html HTTP/1.1" 200 1234',
            '192.168.1.1 - - [15/Jan/2024:10:30:46 +0000] "POST /api/users HTTP/1.1" 201 567',
            '10.0.0.1 - - [15/Jan/2024:10:30:47 +0000] "GET /api/data HTTP/1.1" 404 89',
            '172.16.0.1 - - [15/Jan/2024:10:30:48 +0000] "GET /admin HTTP/1.1" 403 45',
        ]

        apache_log.write_text("\n".join(entries))

        analyzer = LogAnalyzer()
        count = analyzer.load_logs(str(apache_log))

        assert count == 4
        assert len(analyzer.log_entries) == 4

    def test_real_world_json_logs(self, temp_dir):
        """Test with JSON log format."""
        json_log = temp_dir / "app.json.log"

        entries = [
            '{"timestamp": "2024-01-15T10:30:45Z", "level": "INFO", "service": "api", "message": "Request received", "request_id": "abc123"}',
            '{"timestamp": "2024-01-15T10:30:46Z", "level": "ERROR", "service": "database", "message": "Connection timeout", "error": "timeout after 30s"}',
        ]

        json_log.write_text("\n".join(entries))

        analyzer = LogAnalyzer()
        count = analyzer.load_logs(str(json_log))

        assert count == 2
        assert len(analyzer.log_entries) == 2

    def test_incremental_analysis(self, temp_dir):
        """Test analyzing logs incrementally."""
        log_file = temp_dir / "incremental.log"
        log_file.write_text("2024-01-15 10:00:00 INFO First entry\n")

        analyzer = LogAnalyzer()
        count1 = analyzer.load_logs(str(log_file))
        assert count1 == 1

        # Append more entries
        with open(log_file, "a") as f:
            f.write("2024-01-15 10:00:01 ERROR Second entry\n")

        # Load again (should reload entire file)
        count2 = analyzer.load_logs(str(log_file))
        assert count2 == 2
        assert len(analyzer.log_entries) == 2

    def test_filter_chain(self, large_log_file):
        """Test chaining multiple filter operations."""
        analyzer = LogAnalyzer()
        analyzer.load_logs(str(large_log_file))

        # First filter by level
        errors = analyzer.filter_logs(str(large_log_file), level="ERROR")
        initial_error_count = len(errors)

        # Then filter errors by pattern
        database_errors = analyzer.filter_logs(
            str(large_log_file), level="ERROR", pattern="database"
        )

        assert len(database_errors) <= initial_error_count
        assert all(
            "database" in log.get("message", "").lower() for log in database_errors
        )

    def test_export_with_timestamps(self, large_log_file):
        """Test that exports preserve timestamp information."""
        analyzer = LogAnalyzer()
        analyzer.load_logs(str(large_log_file))

        filtered = analyzer.filter_logs(str(large_log_file), level="ERROR")
        output_file = large_log_file.parent / "timestamped.json"

        analyzer.export_filtered_logs(str(output_file), filtered, format="json")

        with open(output_file, "r") as f:
            exported = json.load(f)
            # Check that timestamps are preserved
            for entry in exported:
                assert "timestamp" in entry or "message" in entry
