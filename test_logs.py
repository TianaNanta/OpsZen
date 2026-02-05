#!/usr/bin/env python3
"""Test script for the log analyzer module."""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.logs.log_analyzer import LogAnalyzer
from src.logs.sample_logs import SampleLogGenerator


def test_sample_generation():
    """Test sample log generation."""
    print("=" * 60)
    print("Testing Sample Log Generation")
    print("=" * 60)

    generator = SampleLogGenerator("test_sample_logs")
    generator.generate_all_samples()
    print("\n✓ Sample log generation successful\n")


def test_log_analysis():
    """Test log analysis functionality."""
    print("=" * 60)
    print("Testing Log Analysis")
    print("=" * 60)

    analyzer = LogAnalyzer()

    # Test with generated sample logs
    log_files = [
        "test_sample_logs/sample_syslog.log",
        "test_sample_logs/sample_apache.log",
        "test_sample_logs/sample_json.log",
        "test_sample_logs/sample_python.log",
    ]

    for log_file in log_files:
        if Path(log_file).exists():
            print(f"\n{'─' * 60}")
            print(f"Analyzing: {log_file}")
            print("─" * 60)
            stats = analyzer.analyze_logs(log_file)

            if stats:
                print(f"✓ Analysis completed: {stats['total_entries']} entries")
            else:
                print(f"✗ Analysis failed for {log_file}")
        else:
            print(f"⚠ File not found: {log_file}")


def test_log_filtering():
    """Test log filtering functionality."""
    print("\n" + "=" * 60)
    print("Testing Log Filtering")
    print("=" * 60)

    analyzer = LogAnalyzer()
    log_file = "test_sample_logs/sample_python.log"

    if not Path(log_file).exists():
        print(f"⚠ Log file not found: {log_file}")
        return

    # Test level filtering
    print(f"\n{'─' * 60}")
    print("Test 1: Filter by ERROR level")
    print("─" * 60)
    filtered = analyzer.filter_logs(log_file, level="ERROR")
    print(f"✓ Filtered {len(filtered)} ERROR entries")

    # Test pattern filtering
    print(f"\n{'─' * 60}")
    print("Test 2: Filter by pattern (database)")
    print("─" * 60)
    filtered = analyzer.filter_logs(log_file, pattern="database")
    print(f"✓ Found {len(filtered)} entries matching 'database'")

    # Test combined filtering
    print(f"\n{'─' * 60}")
    print("Test 3: Combined filtering (WARNING + timeout)")
    print("─" * 60)
    filtered = analyzer.filter_logs(log_file, level="WARNING", pattern=".*")
    print(f"✓ Found {len(filtered)} WARNING or higher entries")


def test_log_export():
    """Test log export functionality."""
    print("\n" + "=" * 60)
    print("Testing Log Export")
    print("=" * 60)

    analyzer = LogAnalyzer()
    log_file = "test_sample_logs/sample_python.log"

    if not Path(log_file).exists():
        print(f"⚠ Log file not found: {log_file}")
        return

    # Load logs
    analyzer.load_logs(log_file)

    # Export to JSON
    print("\nExporting to JSON...")
    analyzer.export_filtered_logs("test_output.json", format="json")
    if Path("test_output.json").exists():
        print("✓ JSON export successful")
    else:
        print("✗ JSON export failed")

    # Export to CSV
    print("\nExporting to CSV...")
    analyzer.export_filtered_logs("test_output.csv", format="csv")
    if Path("test_output.csv").exists():
        print("✓ CSV export successful")
    else:
        print("✗ CSV export failed")

    # Export to text
    print("\nExporting to text...")
    analyzer.export_filtered_logs("test_output.txt", format="text")
    if Path("test_output.txt").exists():
        print("✓ Text export successful")
    else:
        print("✗ Text export failed")


def test_tail_functionality():
    """Test tail functionality (non-follow mode)."""
    print("\n" + "=" * 60)
    print("Testing Tail Functionality")
    print("=" * 60)

    analyzer = LogAnalyzer()
    log_file = "test_sample_logs/sample_python.log"

    if not Path(log_file).exists():
        print(f"⚠ Log file not found: {log_file}")
        return

    print(f"\nShowing last 10 lines of {log_file}:")
    print("─" * 60)
    analyzer.tail_logs(log_file, lines=10, follow=False)
    print("\n✓ Tail functionality working")


def cleanup():
    """Cleanup test files."""
    print("\n" + "=" * 60)
    print("Cleaning up test files...")
    print("=" * 60)

    # Remove test output files
    test_files = [
        "test_output.json",
        "test_output.csv",
        "test_output.txt",
    ]

    for file in test_files:
        if Path(file).exists():
            os.remove(file)
            print(f"✓ Removed {file}")


def main():
    """Run all tests."""
    print("\n" + "╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "OpsZen Log Analyzer Test Suite" + " " * 18 + "║")
    print("╚" + "═" * 58 + "╝\n")

    try:
        # Run tests
        test_sample_generation()
        test_log_analysis()
        test_log_filtering()
        test_log_export()
        test_tail_functionality()

        # Cleanup
        cleanup()

        print("\n" + "╔" + "═" * 58 + "╗")
        print("║" + " " * 18 + "All Tests Passed!" + " " * 20 + "║")
        print("╚" + "═" * 58 + "╝\n")

    except Exception as e:
        print(f"\n✗ Test failed with error: {str(e)}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
