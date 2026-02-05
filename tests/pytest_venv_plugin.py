#!/usr/bin/env python3
"""
Pytest plugin to ensure virtual environment is activated before running tests.

This plugin automatically checks if a virtual environment is active and provides
helpful warnings if not. It runs before test collection begins.
"""

import os
import sys
from pathlib import Path


def is_venv_active():
    """Check if a virtual environment is currently activated."""
    # Check for virtual environment indicators
    return (
        hasattr(sys, "real_prefix")  # virtualenv
        or (
            hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
        )  # venv/pyvenv
        or os.environ.get("VIRTUAL_ENV") is not None  # Environment variable
    )


def get_venv_path():
    """Get the path to the virtual environment if active."""
    return os.environ.get("VIRTUAL_ENV", sys.prefix)


def get_project_venv_path():
    """Get the expected path to the project's virtual environment."""
    # Assume we're in the tests directory or project root
    if Path.cwd().name == "tests":
        return Path.cwd().parent / ".venv"
    return Path.cwd() / ".venv"


def pytest_configure(config):
    """
    Pytest hook that runs during configuration phase.

    This checks if virtual environment is activated and provides warnings/info
    to help users set up their environment correctly.
    """
    print("\n" + "=" * 78)
    print("🔍 OpsZen Test Suite - Virtual Environment Check")
    print("=" * 78)

    if is_venv_active():
        venv_path = get_venv_path()
        project_venv = get_project_venv_path()

        print("✓ Virtual environment is active")
        print(f"  Location: {venv_path}")

        # Check if it's the project's venv
        if Path(venv_path) == project_venv:
            print("✓ Using project virtual environment")
        else:
            print("⚠ Using a different virtual environment")
            print(f"  Project venv: {project_venv}")
            print(f"  Current venv: {venv_path}")

        print("=" * 78 + "\n")

    else:
        # Not in a virtual environment
        project_venv = get_project_venv_path()

        print("⚠️  WARNING: Virtual environment is NOT activated!")
        print("=" * 78)

        if project_venv.exists():
            print("\nℹ️  A virtual environment exists but is not activated.")
            print("\nTo activate it:")
            print("\n  On Linux/macOS:")
            print(f"    source {project_venv}/bin/activate")
            print("\n  On Windows (PowerShell):")
            print(f"    {project_venv}\\Scripts\\Activate.ps1")
            print("\n  On Windows (CMD):")
            print(f"    {project_venv}\\Scripts\\activate.bat")
            print("\n  Or use the activation helper:")
            print("    source activate_venv.sh")

        else:
            print("\nℹ️  No virtual environment found.")
            print("\nTo create and activate one:")
            print("\n  1. Create virtual environment:")
            print("       python3 -m venv .venv")
            print("\n  2. Activate it:")
            print("       source .venv/bin/activate  # Linux/macOS")
            print("       .venv\\Scripts\\activate    # Windows")
            print("\n  3. Install test dependencies:")
            print("       pip install -r tests/requirements-test.txt")
            print("\n  Or use the test runner (handles everything):")
            print("       ./run_tests.sh")
            print("       make install-dev")

        print("\n" + "=" * 78)
        print("⚠️  Tests may fail without proper dependencies!")
        print("=" * 78 + "\n")


def pytest_report_header(config):
    """
    Add custom header to pytest output with environment info.
    """
    lines = []

    if is_venv_active():
        venv_path = get_venv_path()
        lines.append(f"Virtual Environment: {venv_path}")
    else:
        lines.append("Virtual Environment: NOT ACTIVATED")

    lines.append(f"Python: {sys.executable}")
    lines.append(f"Python Version: {sys.version.split()[0]}")
    lines.append(f"Working Directory: {Path.cwd()}")

    return lines


def pytest_sessionstart(session):
    """
    Called after Session object has been created and before performing collection.

    This is a good place to set up test environment checks.
    """
    # Check for critical dependencies
    critical_packages = ["pytest", "pytest_cov"]
    missing_packages = []

    for package in critical_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing_packages.append(package)

    if missing_packages and not is_venv_active():
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("    This is likely because no virtual environment is activated.\n")


def pytest_collection_finish(session):
    """
    Called after collection has been performed.

    Show summary of what will be tested.
    """
    if session.config.option.collectonly:
        return

    num_items = len(session.items)
    if num_items > 0:
        print(f"\n📊 Collected {num_items} test(s)")

        # Count tests by marker
        markers = {}
        for item in session.items:
            for marker in item.iter_markers():
                markers[marker.name] = markers.get(marker.name, 0) + 1

        if markers:
            print("\n📋 Test Categories:")
            for marker, count in sorted(markers.items()):
                if marker not in ["parametrize", "skip", "skipif", "xfail"]:
                    print(f"   {marker}: {count}")

        print()


# Register the plugin
pytest_plugins = []
