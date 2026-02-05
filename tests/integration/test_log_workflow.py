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
        success = analyzer.load_logs(str(large_log_file))
        assert success is True
        assert len(analyzer.logs) == 1000

        # Step 2: Filter for errors
        errors = analyzer.filter_logs(level="ERROR")
        assert len(errors) > 0
        assert all(log["level"] == "ERROR" for log in errors)

        # Step 3: Analyze logs
        stats = analyzer.analyze_logs()
        assert stats["total_lines"] == 1000
        assert "ERROR" in stats["level_counts"]
        assert "WARNING" in stats["level_counts"]

        # Step 4: Export filtered results
        output_file = large_log_file.parent / "errors.json"
        export_success = analyzer.export_filtered_logs(
            errors, str(output_file), format="json"
        )
        assert export_success is True
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
            start_time="2024-01-15 12:00:00", end_time="2024-01-15 13:00:00"
        )

        # Verify all filtered logs are within time range
        for log in filtered:
            if log["timestamp"]:
                assert (
                    datetime(2024, 1, 15, 12, 0, 0)
                    <= log["timestamp"]
                    <= datetime(2024, 1, 15, 13, 0, 0)
                )

    def test_keyword_search_workflow(self, large_log_file):
        """Test keyword search across logs."""
        analyzer = LogAnalyzer()
        analyzer.load_logs(str(large_log_file))

        # Search for database-related logs
        db_logs = analyzer.filter_logs(keyword="database")
        assert len(db_logs) > 0
        assert all("database" in log["message"].lower() for log in db_logs)

    def test_regex_pattern_workflow(self, large_log_file):
        """Test regex pattern matching."""
        analyzer = LogAnalyzer()
        analyzer.load_logs(str(large_log_file))

        # Find all logs with numbers
        pattern_logs = analyzer.filter_logs(regex=r"user_id=\d+")
        assert len(pattern_logs) > 0

    def test_multi_format_analysis(self, mixed_format_log_file):
        """Test analyzing logs with multiple formats."""
        analyzer = LogAnalyzer()
        success = analyzer.load_logs(str(mixed_format_log_file))

        assert success is True
        assert len(analyzer.logs) > 0

        # Should handle mixed formats
        stats = analyzer.analyze_logs()
        assert stats["total_lines"] > 0

    def test_export_all_formats(self, large_log_file):
        """Test exporting to all supported formats."""
        analyzer = LogAnalyzer()
        analyzer.load_logs(str(large_log_file))

        errors = analyzer.filter_logs(level="ERROR")

        # Test JSON export
        json_file = large_log_file.parent / "export.json"
        assert analyzer.export_filtered_logs(errors, str(json_file), format="json")
        assert json_file.exists()

        # Test CSV export
        csv_file = large_log_file.parent / "export.csv"
        assert analyzer.export_filtered_logs(errors, str(csv_file), format="csv")
        assert csv_file.exists()

        # Test text export
        txt_file = large_log_file.parent / "export.txt"
        assert analyzer.export_filtered_logs(errors, str(txt_file), format="text")
        assert txt_file.exists()

    def test_combined_filters(self, large_log_file):
        """Test combining multiple filters."""
        analyzer = LogAnalyzer()
        analyzer.load_logs(str(large_log_file))

        # Combine level, keyword, and time filters
        filtered = analyzer.filter_logs(
            level="ERROR",
            keyword="database",
            start_time="2024-01-15 10:00:00",
            end_time="2024-01-15 23:59:59",
        )

        # Verify all filters are applied
        for log in filtered:
            assert log["level"] == "ERROR"
            assert "database" in log["message"].lower()

    def test_statistics_accuracy(self, large_log_file):
        """Test statistical analysis accuracy."""
        analyzer = LogAnalyzer()
        analyzer.load_logs(str(large_log_file))

        stats = analyzer.analyze_logs()

        # Verify total count
        assert stats["total_lines"] == 1000

        # Verify level counts sum to total
        total_counted = sum(stats["level_counts"].values())
        assert total_counted == 1000

        # Verify specific counts based on generation logic
        # Every 50th entry is CRITICAL (1000 / 50 = 20)
        assert stats["level_counts"].get("CRITICAL", 0) == 20

    def test_error_recovery(self, temp_dir):
        """Test analyzer recovers from errors gracefully."""
        analyzer = LogAnalyzer()

        # Try to load non-existent file
        success = analyzer.load_logs("/nonexistent/file.log")
        assert success is False

        # Analyzer should still be usable
        assert analyzer.logs == []

    def test_empty_log_handling(self, temp_dir):
        """Test handling of empty log files."""
        empty_file = temp_dir / "empty.log"
        empty_file.write_text("")

        analyzer = LogAnalyzer()
        success = analyzer.load_logs(str(empty_file))

        assert success is True
        assert len(analyzer.logs) == 0

        # Analysis should still work
        stats = analyzer.analyze_logs()
        assert stats["total_lines"] == 0

    def test_performance_large_dataset(self, temp_dir):
        """Test performance with large dataset."""
        large_file = temp_dir / "large.log"

        # Generate 10,000 entries
        entries = []
        base_time = datetime(2024, 1, 1, 0, 0, 0)
        for i in range(10000):
            timestamp = base_time + timedelta(seconds=i)
            level = ["INFO", "WARNING", "ERROR", "DEBUG"][i % 4]
            entries.append(
                f"{timestamp.strftime('%Y-%m-%d %H:%M:%S')} {level} Message {i}"
            )

        large_file.write_text("\n".join(entries))

        analyzer = LogAnalyzer()

        # Should handle 10k entries efficiently
        import time

        start = time.time()
        success = analyzer.load_logs(str(large_file))
        load_time = time.time() - start

        assert success is True
        assert len(analyzer.logs) == 10000
        assert load_time < 10  # Should complete in under 10 seconds

    def test_real_world_apache_logs(self, temp_dir):
        """Test with realistic Apache access logs."""
        apache_log = temp_dir / "access.log"

        entries = [
            '127.0.0.1 - - [15/Jan/2024:10:30:45 +0000] "GET /index.html HTTP/1.1" 200 1234',
            '192.168.1.1 - - [15/Jan/2024:10:30:46 +0000] "POST /api/users HTTP/1.1" 201 567',
            '10.0.0.1 - - [15/Jan/2024:10:30:47 +0000] "GET /api/data HTTP/1.1" 404 89',
            '127.0.0.1 - - [15/Jan/2024:10:30:48 +0000] "GET /static/style.css HTTP/1.1" 200 3456',
        ]

        apache_log.write_text("\n".join(entries))

        analyzer = LogAnalyzer()
        success = analyzer.load_logs(str(apache_log))

        assert success is True
        assert len(analyzer.logs) == 4

    def test_real_world_json_logs(self, temp_dir):
        """Test with realistic JSON logs."""
        json_log = temp_dir / "app.json"

        entries = [
            json.dumps(
                {
                    "timestamp": "2024-01-15T10:30:45.123Z",
                    "level": "INFO",
                    "service": "api",
                    "message": "Request received",
                    "request_id": "abc123",
                }
            ),
            json.dumps(
                {
                    "timestamp": "2024-01-15T10:30:46.456Z",
                    "level": "ERROR",
                    "service": "database",
                    "message": "Connection timeout",
                    "error": "TimeoutError",
                    "stack_trace": "...",
                }
            ),
        ]

        json_log.write_text("\n".join(entries))

        analyzer = LogAnalyzer()
        success = analyzer.load_logs(str(json_log))

        assert success is True
        assert len(analyzer.logs) == 2

    def test_incremental_analysis(self, temp_dir):
        """Test analyzing logs incrementally."""
        log_file = temp_dir / "incremental.log"

        # Initial logs
        initial_logs = [
            "2024-01-15 10:00:00 INFO Starting",
            "2024-01-15 10:00:01 ERROR Error 1",
        ]
        log_file.write_text("\n".join(initial_logs))

        analyzer = LogAnalyzer()
        analyzer.load_logs(str(log_file))
        assert len(analyzer.logs) == 2

        # Simulate log rotation/new logs
        additional_logs = initial_logs + [
            "2024-01-15 10:00:02 INFO Processing",
            "2024-01-15 10:00:03 ERROR Error 2",
        ]
        log_file.write_text("\n".join(additional_logs))

        # Reload
        analyzer.load_logs(str(log_file))
        assert len(analyzer.logs) == 4

    def test_filter_chain(self, large_log_file):
        """Test chaining multiple filters."""
        analyzer = LogAnalyzer()
        analyzer.load_logs(str(large_log_file))

        # First filter: get errors
        errors = analyzer.filter_logs(level="ERROR")
        original_error_count = len(errors)

        # Create new analyzer with errors
        analyzer2 = LogAnalyzer()
        analyzer2.logs = errors

        # Second filter: specific time range
        time_filtered = analyzer2.filter_logs(
            start_time="2024-01-15 10:00:00", end_time="2024-01-15 12:00:00"
        )

        assert len(time_filtered) <= original_error_count
